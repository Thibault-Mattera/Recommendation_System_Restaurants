""" 
Data Cleaning

"""


# -*- coding: utf-8 -*-

#################################### Dependencies ##############################

import pandas as pd
import os
import glob
import ast
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm.auto import tqdm
import numpy as np


##################################### Functions ##############################

def remove_non_ascii(text): 
    return ''.join(i for i in str(text) if ord(i)<128)


def clean_cuisines_list(x):
    x_cleaned=str(x).replace('[','').replace(']','')
    x_cleaned=to_list(x_cleaned)
    x_cleaned=remove_doublequotes(x_cleaned)
    return x_cleaned


def to_list(x):
    x_list=str(x).split(',')
    x_list_cleaned=[]
    for item in x_list:
        cleaned_item=" ".join(item.split())
        x_list_cleaned.append(cleaned_item)
    return x_list_cleaned


def remove_doublequotes(x):
    x_cleaned=[]
    for el in x:
        x_cleaned.append(el.replace("'",''))
    return x_cleaned


def get_reviewers_ids(x):

    for i in range(len(x)):
        for j in range(len(x[i])):
            if (type(x[i][j]['reviewer_contribution'])==int):
                reviewers.append(x[i][j]['reviewer'])
                if (x[i][j]['reviewer_contribution']>19):
                    influent_reviewers.append(x[i][j]['reviewer'])
    reviewers_unique=set(all_reviewers)
    reviewers=list(all_reviewers_unique)
    influent_reviewers_unique=set(influent_reviewers)
    influent_reviewers=list(influent_reviewers_unique)
    
    print('There are ', len(reviewers), ' reviewers.')
    print('There are ', len(influent_reviewers), ' influent reviewers (that posted 20 reviews or more).')
    
    return reviewers


def group_reviews_by_reviewers(df_restaurants, all_reviews, all_reviewers):
    # for each reviewer, get the list of visited restaurants in Zurich and corresponding reviews 
    reviewers_info=[]
    
    for n in tqdm(range(len(all_reviewers))):
        reviewer_info={}
        reviewer_info['reviewer_name']=all_reviewers[n]
        reviewer_info['reviews']=[]
        # for each reviewer - 1 item = 1 restaurant
        for i in range(len(all_reviews)):
            for j in range(len(all_reviews[i])):
                if all_reviews[i][j]['reviewer']==all_reviewers[n]:
                    reviewer_info_item={}
                    reviewer_info_item['restaurant_url']=df_restaurants.iloc[i]['url']
                    reviewer_info_item['restaurant_name']=df_restaurants.iloc[i]['name']
                    reviewer_info_item['restaurant_location']=df_restaurants.iloc[i]['location']
                    reviewer_info_item['restaurant_nb_reviews']=df_restaurants.iloc[i]['num reviews']
                    reviewer_info_item['restaurant_price_range']=df_restaurants.iloc[i]['price_range']
                    reviewer_info_item['restaurant_cuisines']=df_restaurants.iloc[i]['cuisines']
                    reviewer_info_item['restaurant_special_diets']=df_restaurants.iloc[i]['special_diets']
                    reviewer_info_item['review_quote']=all_reviews[i][j]['review_quote']
                    reviewer_info_item['review_body']=all_reviews[i][j]['review_body']
                    reviewer_info_item['review_date']=all_reviews[i][j]['review_date']
                    reviewer_info_item['helpful_vote']=all_reviews[i][j]['helpful_vote']
                    reviewer_info['reviews'].append(reviewer_info_item)
        reviewer_info['number_Zurich_reviews']=len(reviewer_info['reviews'])
        reviewers_info.append(reviewer_info)
    
    return reviewers_info


##################################### EXECUTION ##############################

os.chdir("./data")

# if scraped data correspond to several csv files to combine
extension = 'csv'
all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
if len(all_filenames)>1:
    combined_csv=pd.concat([pd.read_csv(f) for f in all_filenames ])
    combined_csv.to_csv( "combined.csv", index=False, encoding='utf-8-sig')
    df_restaurants=pd.read_csv('combined.csv')
else:
    df_restaurants=pd.read_csv('scraped_restaurants_data.csv')

df_restaurants.fillna('', inplace=True)

"""Replace missing price by default range depending on number of $ symbol
- $ 10 30 CHF
- $$ $$$ 30 50 CHF
- $$$$ 50 100 CHF
"""

df_restaurants.loc[df_restaurants['price_category']=='$', 'price_range'] = '[10,30]'
df_restaurants.loc[df_restaurants['price_category']=='$$ - $$$', 'price_range'] = '[30,50]'
df_restaurants.loc[df_restaurants['price_category']=='$$$$', 'price_range'] = '[50,100]'

# clean list of list of reviews
reviews=df_restaurants['reviews'].values
cleaned_reviews= [ast.literal_eval(reviews[i]) for i in range(len(reviews))]
df_restaurants['reviews']=cleaned_reviews
df_restaurants['reviews'] = df_restaurants['reviews'].apply(lambda x: remove_non_ascii(x))
df_restaurants.drop_duplicates(subset=['url'],inplace=True)
df_restaurants.dropna(subset=['cuisines'],inplace=True)

# put list of cuisines in a usable format
df_restaurants['cuisines']=df_restaurants['cuisines'].apply(lambda x: clean_cuisines_list(x))

# save cleaned dataset
df_restaurants.to_csv('restaurants_info_cleaned.csv', index=False)

# extract reviewers ids
df_restaurants=pd.read_csv('restaurants_info_cleaned.csv')
reviews=df_restaurants['reviews'].values.tolist()
reviewers=get_reviewers_ids(reviews)
df_reviewers=pd.DataFrame(reviewers)
df_reviewers.to_csv('reviewers.csv', index=False)

# group restaurants info by reviewers
reviewers_info=group_reviews_by_reviewers(df_restaurants,reviews,reviewers)
reviewers_info_df=pd.DataFrame(reviewers_info)
reviewers_info.to_csv('reviewers_info.csv')