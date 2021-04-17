# -*- coding: utf-8 -*-
"""
Preprocessing & feature engineering

"""

##################################### Dependencies ##############################

import pandas as pd
from sklearn import preprocessing
import ast
from tqdm.auto import tqdm
import matplotlib.pyplot as plt
import ast
import sys
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from nltk.corpus import stopwords
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
import warnings
warnings.filterwarnings("ignore")
tqdm.pandas()

####################################### Functions ################################


def get_price_ranges(reviews) -> str:
    reviews_l=ast.literal_eval(reviews)
    price_ranges=[]
    if len(reviews_l)>0:
        for i in range(len(reviews_l)):
            if (reviews_l[i]['restaurant_price_range']!='') and (reviews_l[i]['restaurant_price_range']!='[]'):
                price_ranges.append(reviews_l[i]['restaurant_price_range'])
    else:
        price_ranges=reviews_l[0]['restaurant_price_range']  
    return price_ranges


def get_cuisines(reviews) -> list:
    reviews_l=ast.literal_eval(reviews)
    cuisines=[]
    if len(reviews_l)>0:
        for i in range(len(reviews_l)):
            if (reviews_l[i]['restaurant_cuisines']!='') and (reviews_l[i]['restaurant_cuisines']!='[]'):
                cuisines.append(reviews_l[i]['restaurant_cuisines'])
    else:
        cuisines=reviews_l[0]['restaurant_cuisines']
    splited_cuisines=[]
    for item in cuisines:
        splited_cuisines.append(" ".join(item.split()))
    return splited_cuisines


def get_locations(reviews) -> str:
    reviews_l=ast.literal_eval(reviews)
    locations=[]
    if len(reviews_l)>0:
        for i in range(len(reviews_l)):
            if (reviews_l[i]['restaurant_location']!='') and (reviews_l[i]['restaurant_location']!='[]'):
                locations.append(reviews_l[i]['restaurant_location'])
    else:
        locations=reviews_l[0]['restaurant_location']  
    return locations


def get_special_diets(reviews) -> list:
    reviews_l=ast.literal_eval(reviews)
    special_diets=[]
    if len(reviews_l)>0:
        for i in range(len(reviews_l)):
            if (reviews_l[i]['restaurant_special_diets']!='') and (reviews_l[i]['restaurant_special_diets']!='[]'):
                special_diets.append(reviews_l[i]['restaurant_special_diets'])
    else:
        special_diets=reviews_l[0]['restaurant_special_diets'] 
    splited_special_diets=[]
    for item in special_diets:
        splited_special_diets.append(" ".join(item.split()))
    return splited_special_diets


def get_nb_reviews(reviews) -> int:
    reviews_l=ast.literal_eval(reviews)
    restaurant_nb_reviews=[]
    if len(reviews_l)>0:
        for i in range(len(reviews_l)):
            if (reviews_l[i]['restaurant_nb_reviews']!='') and (reviews_l[i]['restaurant_nb_reviews']!='[]'):
                restaurant_nb_reviews.append(reviews_l[i]['restaurant_nb_reviews'])
    else:
        restaurant_nb_reviews=reviews_l[0]['restaurant_nb_reviews']  
    return int(restaurant_nb_reviews)


def get_urls(reviews):
    reviews_l=ast.literal_eval(reviews)
    urls=[]
    if len(reviews_l)>0:
        for i in range(len(reviews_l)):
            if (reviews_l[i]['restaurant_url']!='') and (reviews_l[i]['restaurant_url']!='[]'):
                urls.append(reviews_l[i]['restaurant_url'])
    else:
        urls=reviews_l[0]['restaurant_url']  
    return urls


def mean_price_ranges(x) -> float:
    ranges=[item.replace('[', '').replace(']', '').split(',') for item in x]
    int_ranges=[[int(y) for y in element] for element in ranges]
    if len(int_ranges)>1:
        for item in int_ranges:
            mean_price_range=np.mean(np.mean(item))
    else:
        mean_price_range=np.mean(int_ranges)
    return mean_price_range


def count_elements(z) -> list:
    z_list=[]
    for item in z:
        z_list.append(item.split(','))
    flat_list = [item for sublist in z_list for item in sublist]
    x_list=[]
    for item in flat_list:
        x_list.append(" ".join(item.split(',')))
    if (x_list!=[]) and (x_list!='') and (type(x_list)==list):
        count=Counter(x_list).most_common()
    else:
        count=''
        median_cuisines=''
    return count


def mean_number_reviews(x) -> float:
    mean_nb_rev=float(np.mean(x))
    return mean_nb_rev


def extract_unique_element(dataset,name_column) -> list:
    c=dataset[name_column].values.tolist()
    z_list=[]
    for item in c:
        for el in item:
            z_list.append(el.split(','))
    flat_list = [item for sublist in z_list for item in sublist]
    cuisines=[]
    for el in flat_list:
        cuisines.append(" ".join(el.split()))
    print(len(Counter(cuisines).most_common()), ' ',name_column)
    return Counter(cuisines).most_common()


def clean_values(x) -> list:
    x_list=ast.literal_eval(str(x))
    x_list_cleaned=[]
    for el in x_list:
        cleaned_el=el.replace('[','').replace(']','').replace("'",'')
        x_list_cleaned.append(cleaned_el)
    final_list=[]
    for item in x_list_cleaned:
        a=item.split(',')
        final_list.append(a)
    final_list_flat = [item for sublist in final_list for item in sublist]
    return final_list_flat

def replace_cuisines(x:list) -> list:
    to_Italian=['Southern-Italian','Central-Italian','Northern-Italian', 'Neapolitan', 'Campania', 'Tuscan']
    to_Mexican=['Central American']
    to_Japanese=['Japanese Fusion','Sushi']
    to_American=['Native American','South western']
    to_SouthAmerican=['Argentinean','Chilean', 'Peruvian']
    to_Indian=['Pakistani', 'Tibetan', 'SriLankan']
    to_MiddleEastern=['Israeli', 'Lebanese', 'Turkish','Persian','Arabic']
    to_Pacific_Islands=['Hawaiian','Polynesian']
    to_British=['Irish']
    to_Swiss=['Austrian']
    to_Chinese_Korean=['Korean','Chinese']
    to_Mediterranean=['Moroccan','Greek']
    
    new_list=[]
    for i in range(len(x)):
        if x[i][0] in to_Italian:
            cuisine='Italian'
        elif x[i][0] in to_Mexican:
            cuisine='Mexican'
        elif x[i][0] in to_Japanese:
            cuisine='Japanese'
        elif x[i][0] in to_American:
            cuisine='American'
        elif x[i][0] in to_SouthAmerican:
            cuisine='South American'
        elif x[i][0] in to_Indian:
            cuisine='Indian'
        elif x[i][0] in to_MiddleEastern:
            cuisine='Middle Eastern'
        elif x[i][0] in to_Pacific_Islands:
            cuisine='Pacific Islands'
        elif x[i][0] in to_British:
            cuisine='British'
        elif x[i][0] in to_Swiss:
            cuisine='Swiss'
        elif x[i][0] in to_Chinese_Korean:
            cuisine='Chinese/Korean'  
        elif x[i][0] in to_Mediterranean:
            cuisine='Mediterranean'  
        else:
            cuisine=x[i][0]
        count=x[i][1]
        new_list.append((cuisine,count))
    
    return new_list

def move_to_new_category(x:list,list_of_items:list) -> list:
    new_list=[]
    for i in range(len(x)):
        if x[i][0] in list_of_items:
            new_list.append((x[i][0],x[i][1]))
    return new_list


####################################### Execution ################################

"""
4 features: 
- price range
- cuisine country
- cuisine style
- number of reviews
"""
## Load dataset and collect features

df_reviewers=pd.read_csv('transformed_data/reviewers_info_clean.csv')
df_reviewers=df_reviewers[['reviewer_name','reviews','number_Zurich_reviews']]
df_reviewers.drop_duplicates(subset=['reviewer_name'],inplace=True)

# select only reviewer with 10 or more reviews
df_reviewers=df_reviewers[df_reviewers['number_Zurich_reviews']>9]

# extract features from scraped reviews
df_reviewers['restaurants_price_ranges']=df_reviewers['reviews'].apply(lambda x: get_price_ranges(x))
df_reviewers['restaurants_cuisines']=df_reviewers['reviews'].apply(lambda x: get_cuisines(x))
df_reviewers['restaurants_location']=df_reviewers['reviews'].apply(lambda x: get_locations(x))
df_reviewers['restaurants_special_diets']=df_reviewers['reviews'].apply(lambda x: get_special_diets(x))
df_reviewers['restaurants_nb_reviews']=df_reviewers['reviews'].apply(lambda x: get_nb_reviews(x))
df_reviewers['restaurants_urls']=df_reviewers['reviews'].apply(lambda x: get_urls(x))
df_reviewers['mean_price_range']=df_reviewers['restaurants_price_ranges'].apply(lambda x: mean_price_ranges(x))
df_reviewers['count_cuisines']=df_reviewers['restaurants_cuisines'].apply(lambda x: count_elements(x))
df_reviewers['count_diets']=df_reviewers['restaurants_special_diets'].apply(lambda x: count_elements(x))
df_reviewers['mean_restaurants_reviews']=df_reviewers['restaurants_nb_reviews'].apply(lambda x: mean_number_reviews(x))
df_reviewers['restaurants_cuisines']=df_reviewers['restaurants_cuisines'].apply(lambda x: clean_values(x))

# Label cuisine and special diets tags in 4 meaningful categories (countries, styles, special diets and other criteria)

# define cuisine categories refering to countries/regions
cuisine_countries=['Tibetan',
 'Japanese Fusion',
 'Campania',
 'SriLankan',
 'Swiss',
 'Central American',
 'Polynesian',
 'Middle Eastern',
 'Argentinean',
 'Korean',
 'South American',
 'British',
 'South western',
 'Sushi',
 'Taiwanese',
 'Australian',
 'American',
 'Hawaiian',
 'Chilean',
 'Moroccan',
 'Greek',
 'Southern-Italian',
 'Indian',
 'Scandinavian',
 'Turkish',
 'Arabic',
 'Latin',
 'Neapolitan',
 'Spanish',
 'Pakistani',
 'Italian',
 'French',
 'Austrian',
 'Mediterranean',
 'Malaysian',
 'Nepali',
 'Chinese',
 'Thai',
 'Vietnamese',
 'Central-Italian',
 'Japanese',
 'Mexican',
 'Portuguese',
 'Tuscan',
 'German',
 'Peruvian',
 'Native American',
 'Bangladeshi',
 'Irish',
 'Lebanese',
 'Northern-Italian',
 'Israeli',
 'Persian']

# define cuisine categories refering to a style (no country)
cuisine_styles=['Contemporary',
'Steakhouse',
'Pizza',
'Soups',
'Healthy',
'Fast Food',
'Street Food',
'Barbecue',
'Grill',
'Fusion',
'Deli',
'Seafood']

# define special specif criteria
other_criteria=['Reservations', 
'Wheelchair Accessible',
'Cafe',
'Wine and Beer',
'Serves Alcohol',
'Accepts Credit Cards',
'Breakfast',
'Live Music',
'Diner',
'Table Service',
'Brunch',
'Pub', 
'Dinner', 
'Lunch', 
'Drinks',
'Late Night',
'Seating',
'Bar',
'Diningbars',
'Free Wifi',
'Wine Bar',
'Digital Payments',
'Gastropub',
'Full Bar',
'Pub', 
'Late Night',
'Take out',
'Brew Pub',
'Outdoor Seating']

special_diets=['Vegetarian Friendly',
'Gluten Free Options',
'Vegan Options',
'Halal',
'Kosher']

# reorganize cuisines tags (column "count_cuisines ")
df_reviewers['countries']=df_reviewers['count_cuisines'].apply(lambda x: move_to_new_category(x,cuisine_countries))
df_reviewers['cuisine_styles']=df_reviewers['count_cuisines'].apply(lambda x: move_to_new_category(x,cuisine_styles))
df_reviewers['special_diets']=df_reviewers['count_cuisines'].apply(lambda x: move_to_new_category(x,special_diets))
df_reviewers['other_criteria']=df_reviewers['count_cuisines'].apply(lambda x: move_to_new_category(x,other_criteria))

# reduce the number of classes by asssigning similar cuisine to a unique region
df_reviewers['cuisine_countries']=df_reviewers['countries'].apply(lambda x: replace_cuisines(x))

# select only relevant column for recommendation system
df_reviewers=df_reviewers[['reviewer_name','number_Zurich_reviews','restaurants_urls',
                             'restaurants_price_ranges','restaurants_nb_reviews','restaurants_cuisines',
                             'mean_price_range','mean_restaurants_reviews','cuisine_countries','cuisine_styles']]

df_reviewers.to_csv('data/reviewers_ready_for_clustering.csv', index=False)