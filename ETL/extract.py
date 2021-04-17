#!/usr/bin/env python
# coding: utf-8
""" 
Extract data from TripAdvisor
"""

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
import os
# setting Selenium driver
options = webdriver.ChromeOptions()
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
chrome_driver_binary = "/usr/local/chromedriver"
driver = webdriver.Chrome(chrome_driver_binary, chrome_options=options)

####################################### Functions ################################

def check_url_database(url:str, urls_db:list) -> bool:
    """Chek if url has been already scraped or not
    """
    if url in urls_list:
        return True
    else:
        return False


def scrape_restaurants_urls(search_url: str) -> list:
    """ Scrapes restaurants' urls and returns it as a list of urls
    Input:
        - search_url: string
    Output:
        - restaurants' URLs: list of strings
    """
    # page request with provided url
    session = requests.Session()
    response = session.get(search_url) 
    
    # check status
    print(response.status_code)
    soup_ = BeautifulSoup(response.content, 'html.parser').find_all()
    
    # extract restaurant links
    restaurants_list=soup_[0].find_all('div', class_="_1llCuDZj")
    links: list=[]
    links=[el.find('a', class_='_2uEVo25r').get('href') for el in restaurants_list]


    for i in range(30, 150, 30):
        time.sleep(2)
        url_page="https://www.tripadvisor.com/RestaurantSearch-g188113-oa"+str(i)+"-Zurich.html#EATERY_LIST_CONTENTS"
        response = session.get(url_page) 
        soup_ = BeautifulSoup(response.content, 'html.parser').find_all()
        # extract restaurant links
        restaurants_list=soup_[0].find_all('div', class_="_1llCuDZj")
        for el in restaurants_list:
            links.append(el.find('a', class_='_2uEVo25r').get('href'))
        print('scraped urls: ', len(links))

    return links


def get_more(session, reviews_ids):
    """ Expands each review (automate the click on "see more")
    
    Input:
        - search_url: string
    Output:
        - restaurants' URLs: list of strings
    """

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


def post_soup(session, url, params, show=False) -> object:
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


def get_reviews_ids(soup) -> list:

    items = soup.find_all('div', attrs={'data-reviewid': True})

    if items:
        reviews_ids = [x.attrs['data-reviewid'] for x in items][::2]
        return reviews_ids


def parse_reviews(soup_more) -> list:
    """Extracts all reviews from one page
        Input:
            - soup (scraped data)
        Output:
            - list of dictionaries (1 item = 1 review)
    """
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


def numbers(s) -> list:
    """Keep numerical characters from list"""
    return [int(match) for match in re.findall(r"\d+", s)]


def scrape_restaurant_details(restaurant_id, session) -> dict:
    """Extracts restaurants details 
        Input:
            - restaurant id
            - request session
        Output:
            -  dictionary with keys: 
                *'url'
                *'price_range'
                *'price_category'
                *'cuisines'
                *'special_diets'
                *'location'
                *'num reviews'
    """
    ## build complete url
    restaurant_url="https://www.tripadvisor.com"+restaurant_id
    #  page request for 1 restaurant
    # select all languages for reviews (click radio button "all languages")
    #WebDriver driver = new ChromeDriver();
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
            cuisines=[el.get_text() for el in el_cuisines]
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


#################################################### EXECUTION #################################################

def extract_data(search_url:str): 
    """ Extract restaurants data from Trip Advisor 
            Input: 
                - search_url (example: restaurants in a specific city)
            Saves extracted data into 2 csv files:
                - urls.csv (list of restaurants' urls)
                - restaurants_details.csv 
                (url,name,price_range,price_category,cuisines,special_diets,location,num reviews,reviews)
    """
    
    # 1 - Extract Restaurants URLs - convert to dataframe and save in csv file
    print('Start scraping restaurants urls...')
    scraped_urls=scrape_restaurants_urls(search_url)
    print(len(scraped_urls), ' restaurants found')

    # check if url is listed in the database
    if os.path.isfile(f"./scraped_data/urls.csv"):
        urls_db=pd.read_csv('./scraped_data/urls.csv')
        urls_listed=urls_db['0'].values.tolist()
        urls_new=[url for url in scraped_urls if url not in urls_listed]
        # add new urls to listed urls
        restaurants_urls=urls_listed
        for url in urls_new:
            restaurants_urls.append(url)
    else:
        restaurants_urls=scraped_urls      
    
    urls_df=pd.DataFrame(restaurants_urls)
    print('...end')

    # save dataframe
    if not os.path.exists(f"./scraped_data"):
        os.makedirs(f"./scraped_data/")
    urls_df.to_csv('./scraped_data/urls.csv', index=False)  
    print('urls saved')

    # 2 - Extract Restaurants' details- convert to dataframe and save in csv file

    print('Start scraping info about restaurants...')
    session = requests.Session()
    urls_df=pd.read_csv('./scraped_data/urls.csv')
    restaurants_urls=urls_df['0'].values.tolist()

    # check if url is listed in the database
    if os.path.isfile(f"./scraped_data/restaurants_details.csv"):
        urls_db=pd.read_csv('./scraped_data/restaurants_details.csv')
        urls_listed=urls_db['url'].values.tolist()
        restaurants_urls=[url for url in restaurants_urls if url not in urls_listed]

    restaurants_scraped=[]
    for i in tqdm(range(len(restaurants_urls))):
        restaurants_scraped.append(scrape_restaurant_details(restaurants_urls[i], session))
        restaurants_scraped=pd.DataFrame(restaurants_scraped)
        if os.path.isfile(f"./scraped_data/restaurants_details.csv"):
            restaurants_db=pd.read_csv(f"./scraped_data/restaurants_details.csv")
            restaurants_db.append(restaurants_scraped)
            restaurants_db.to_csv('./scraped_data/restaurants_details.csv', index=False)
        else:
            restaurants_scraped.to_csv('./scraped_data/restaurants_details.csv', index=False)
    print('...end')

    return restaurants_scraped