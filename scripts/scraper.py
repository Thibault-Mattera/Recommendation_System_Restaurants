###################### SCRIPT TO SCRAPE TRIP ADVISOR #######################

##################################### Dependencies ##############################
import requests 
from bs4 import BeautifulSoup
import csv                  
import webbrowser
import io
import re
import time
import pandas as pd 
from tqdm.auto import tqdm
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
options = Options()

####################################### Functions ################################

def scrape_restaurants_links(search_url,session):
    
    # page request with provided url
    response = session.get(search_url) 
    
    # check status
    print(response.status_code)
    soup_ = BeautifulSoup(response.content, 'html.parser').find_all()
    
    # total number of restaurants in specified location
    results=soup_[0].find('div', class_='_3X__xCrG')
    number_of_restaurants=results.find('span', class_='_1D_QUaKi').get_text()
    print('number_of_restaurants: ', number_of_restaurants)
    
    # extract restaurant links
    restaurants_list=soup_[0].find_all('div', class_="_1llCuDZj")
    links=[]
    for el in restaurants_list:
        links.append(el.find('a', class_='_2uEVo25r').get('href'))


    for i in range(30, 1831, 30):
        time.sleep(3)
        url_page="https://www.tripadvisor.com/RestaurantSearch-g188113-oa"+str(i)+"-Zurich.html#EATERY_LIST_CONTENTS"
        response = session.get(url_page) 
        soup_ = BeautifulSoup(response.content, 'html.parser').find_all()
        # extract restaurant links
        restaurants_list=soup_[0].find_all('div', class_="_1llCuDZj")
        for el in restaurants_list:
            links.append(el.find('a', class_='_2uEVo25r').get('href'))
        print('scraped links: ', len(links))

    return links


def get_more(session, reviews_ids):
    # Function to expand each review -> automate "see more" click

    url = 'https://www.tripadvisor.com/OverlayWidgetAjax?Mode=EXPANDED_HOTEL_REVIEWS_RESP&metaReferer=Hotel_Review'

    payload = {
        'reviews': ','.join(reviews_ids), # ie. "577882734,577547902,577300887",
        #'contextChoice': 'DETAIL_HR', # ???
        'widgetChoice': 'EXPANDED_HOTEL_REVIEW_HSX', # ???
        'haveJses': 'earlyRequireDefine,amdearly,global_error,long_lived_global,apg-Hotel_Review,apg-Hotel_Review-in,bootstrap,desktop-rooms-guests-dust-en_US,responsive-calendar-templates-dust-en_US,taevents',
        'haveCsses': 'apg-Hotel_Review-in',
        'Action': 'install',
    }

    soup = post_soup(session, url, payload)

    return soup


def post_soup(session, url, params, show=False):
    '''Read HTML from server and convert to Soup'''

    r = session.post(url, data=params)
    
    if show:
        display(r.content, 'temp.html')

    if r.status_code != 200: # not OK
        print('[post_soup] status code:', r.status_code)
    else:
        content_soup = BeautifulSoup(r.content, 'html.parser')
        return content_soup

def display(content, filename='output.html'):
    with open(filename, 'wb') as f:
        f.write(content)
        webbrowser.open(filename)


def get_reviews_ids(soup):

    items = soup.find_all('div', attrs={'data-reviewid': True})

    if items:
        reviews_ids = [x.attrs['data-reviewid'] for x in items][::2]
        return reviews_ids


def parse_reviews(soup_more):
    '''Get all reviews from one page'''
    items = []

    for idx, review in enumerate(soup_more.find_all('div', class_='reviewSelector')):

            badgets = review.find_all('span', class_='badgetext')
            if len(badgets) > 0:
                contributions = badgets[0].get_text()
            else:
                contributions = '0'

            if len(badgets) > 1:
                helpful_vote = badgets[1].get_text()
            else:
                helpful_vote = '0'
            user_loc = review.select_one('div.userLoc strong')
            if user_loc:
                user_loc = user_loc.get_text()
            else:
                user_loc = ''
                
            bubble_rating = review.select_one('span.ui_bubble_rating')['class']
            bubble_rating = bubble_rating[1].split('_')[-1]

            try:
                reviewer=review.find('div', class_='prw_rup prw_reviews_member_info_resp').find('div', class_='info_text pointer_cursor').find('div').get_text()
            except:
                reviewer=None

            try:
                reviewer_contribution=int(review.find('div', class_='prw_rup prw_reviews_member_info_resp').find('span', class_='badgetext').get_text())
            except:
                reviewer_contribution=None

            try:
                review_body=review.find('p', class_='partial_entry').get_text()
            except:
                review_body=None

            try:
                review_date=review.find('span', class_='ratingDate')['title']
            except:
                review_date=None

            try:
                review_quote=review.find('span', class_='noQuotes').get_text()
            except:
                review_quote=None
            

            item = {
                'reviewer':reviewer,
                'reviewer_contribution':reviewer_contribution,
                'review_quote':review_quote,
                'review_body': review_body,
                'review_date': review_date, # 'ratingDate' instead of 'relativeDate'
                'helpful_vote': helpful_vote
            }

            items.append(item)
                
    return items

def numbers(s):
    return [int(match) for match in re.findall(r"\d+", s)]


def scrape_restaurant_details(restaurant_id, session):
    ## build complete url
    restaurant_url="https://www.tripadvisor.com"+restaurant_id
    #  page request for 1 restaurant
    
    # select all languages for reviews (click radio button "all languages")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(restaurant_url) 
    time.sleep(5)
    try: 
        languages=driver.find_element_by_xpath("//*[@id='taplc_detail_filters_rr_resp_0']")
        languages.find_element_by_css_selector("input[id='filters_detail_language_filterLang_ALL'][value='ALL']").click()
        time.sleep(5)
        driver.refresh()
        time.sleep(3)
    except:
        languages=None
    
    #Seleium hands the page source to Beautiful Soup
    soup_= BeautifulSoup(driver.page_source, 'lxml').find_all()

    # get restaurant details: price range, cuisines, special diets and location
    try:
        details=soup_[0].find('div', class_="_3UjHBXYa").find_all('div', class_="_1XLfiSsv")
        details_content=details.find_all('div', class_="_1XLfiSsv")
    except: 
        details = None

    name=''
    try:
        name=soup_[0].find('h1', class_="_3a1XQ88S").get_text()
    except:
        name=None
    
    location=''
    try:
        location=soup_[0].find('div', class_="xAOpeG9l").find('span', class_='_2saB_OSe').get_text()
    except:
        location=None

    price_range=''
    try:
        price_range=numbers(soup_[0].find('div', class_="_3UjHBXYa").find_all('div', class_="_1XLfiSsv")[0].get_text())
    except:
        price_range=None
    
    try:
        price_category=soup_[0].find('div', class_="bk7Uv0cc").find('div', class_="_1ud-0ITN").find('span', class_="_13OzAOXO _34GKdBMV").find('a', class_="_2mn01bsa").get_text()
    except:
        price_category=None

    cuisines=''
    try:
        cuisines_1=soup_[0].find('div', class_="_3UjHBXYa").find_all('div', class_="_1XLfiSsv")[1].get_text()
        if (cuisines_1 != None) or (cuisines_1 != ''):
            cuisines=cuisines_1
        else:
            el_cuisines=soup_[0].find('div', class_="bk7Uv0cc").find('div', class_="_1ud-0ITN").find('span', class_="_13OzAOXO _34GKdBMV").find_all('a', class_="_2mn01bsa")
            cuisines=[]
            for el in el_cuisines:
                cuisines.append(el.get_text())
            cuisines.pop(0)
    except:
        cuisines=None
    
    special_diets=''
    try:
        special_diets=soup_[0].find('div', class_="_3UjHBXYa").find_all('div', class_="_1XLfiSsv")[2].get_text()
    except:
        special_diets=None

    try:
        num_reviews = soup_[0].find('span', class_='reviews_header_count').get_text()
        num_reviews=int(num_reviews.replace(',', '').replace(')', '').replace('(', ''))
    except:
        num_reviews=None

    restaurant_info = {
    'url':restaurant_url,
    'name': name,
    'price_range': price_range,
    'price_category': price_category,
    'cuisines': cuisines,
    'special_diets': special_diets,
    'location': location,
    'num reviews': num_reviews
    }

    # get reviews from first page
    if num_reviews > 0:
        reviews_ids = get_reviews_ids(soup_[0])
        soup_more = get_more(session, reviews_ids)
        reviews = parse_reviews(soup_more)
    else:
        reviews=''

    # get reviews from other pages if more than 10 reviews
    if num_reviews > 10:

        page_numbers=soup_[0].find('div', class_='pageNumbers').find_all('a')
        last_offset=int(page_numbers[-1].get('data-page-number'))
        pages=[str(i) for i in range(2,last_offset+1)]

        for page in pages:
            driver.find_element_by_link_text(page).click()
            time.sleep(3)
            soup_= BeautifulSoup(driver.page_source, 'lxml').find_all()
            reviews_ids = get_reviews_ids(soup_[0])
            soup_more = get_more(session, reviews_ids)
            other_reviews = parse_reviews(soup_more)
            for element in other_reviews:
                reviews.append(element)

    restaurant_info['reviews']=reviews

    return restaurant_info


def find_influent_reviewer(all_reviews):
    influent_reviewers=[]
    for review in all_reviews:
        if review['reviewer_contribution'] >= 10:
            influent_reviewers.append(review['reviewer'])
    
    return influent_reviewers



def scrape_reviewer(reviewer):
    
    profile_url='https://www.tripadvisor.ca/Profile/'+reviewer

    response = requests.get(profile_url)
    print(response.status_code)
    soup_ = BeautifulSoup(response.content, 'html.parser').find_all()
    
    reviewer_location=''
    try:
        reviewer_location=soup_[0].find('span', class_='_2VknwlEe _3J15flPT default').get_text()
    except:
        reviewer_location=None
    
    reviewer_joining_date=''
    try:
        joining_date=soup_[0].find('span', class_='_1CdMKu4t').get_text()
        reviewer_joining_date=joining_date.split("Joined in",1)[1]
    except:
        reviewer_joining_date=None
    
    nb_reviews_TA=''
    try:
        nb_reviews_TA= int(soup_[0].find('span', class_='iX3IT_XP').get_text())
    except:
        nb_reviews_TA=None
    
    reviewer_info = {
        'reviewer_name': reviewer,
        'reviewer_location': reviewer_location,
        'reviewer_joining_date': reviewer_joining_date,
        'nb_reviews_TA': nb_reviews_TA,

    }
    
    return reviewer_info

#################################################### EXECUTION #################################################


# 0 - create session and define Trip Advisor search URL
session = requests.Session()
search_url = 'https://www.tripadvisor.com/Restaurants-g188113-Zurich.html'


# 1 - Extract Restaurants URLs - convert to dataframe and save in csv file
print('Start scraping restaurants urls...')
restaurants_urls=scrape_restaurants_links(search_url,session)
print(len(restaurants_urls), ' restaurants found')
urls_df=pd.DataFrame(restaurants_urls)
urls_df.to_csv('../data/urls.csv', index=False)
print('...end')


# 2 - Extract Restaurants info - convert to dataframe and save in csv file
print('Start scraping restaurants infos...')
df=pd.read_csv('../data/urls.csv')
restaurants_urls=df['0'].values.tolist()
restaurants_info=[]
for i in tqdm(range(len(restaurants_urls))):
    restaurants_info.append(scrape_restaurant_details(restaurants_urls[i], session))
    restaurants_df=pd.DataFrame(restaurants_info)
    restaurants_df.to_csv('../data/restaurants_info.csv', index=False)
print('...end')


# 3 - Find influent reviewers - convert to dataframe and save in csv file
print('Find relevant reviewers...')
t=[restaurant['influent_reviewers'] for restaurant in restaurants_info]
flat_t = [item for sublist in t for item in sublist]
influent_reviewers = set(flat_t)
influent_reviewers=list(influent_reviewers)
influent_reviewers.to_csv('../data/reviewers_ids.csv', index=False)
print('...Done')
print(len(influent_reviewers), ' influent reviewers found')


# 4 - extract reviews from influent reviewers - convert to dataframe and save in csv file
print('Extract reviewers profiles...')
reviewers_info=[]
df=pd.read_csv('../data/reviewers_ids.csv')
influent_reviewers=df['reviewer_name'].values.tolist()

for j in tqdm(range(len(influent_reviewers))):
    reviewers_info.append(scrape_reviewer(influent_reviewers[j]))
    reviewers_df=pd.DataFrame(reviewers_info)
    reviewers_df.to_csv('../data/reviewers_info.csv', index=False)
print('...Done')
