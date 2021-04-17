#!/usr/bin/env python
# coding: utf-8
""" 
Transform extracted data
"""

#################################### Dependencies ##############################

import pandas as pd
import os
import glob
import ast
import matplotlib.pyplot as plt
from tqdm.auto import tqdm
import numpy as np
from collections import Counter
import re


##################################### Functions ##############################

def remove_non_ascii(text:str): 
    """ Removes non ASCII characters"""
    
    return ''.join(i for i in str(text) if ord(i)<128)


def to_list(x:str):
    """ Convert string to list of strings """
    x_list=str(x).split(',')
    x_list_cleaned=[" ".join(item.split()) for item in x_list]

    return x_list_cleaned


def remove_doublequotes(x:list):
    """ removes double quotes from list """
    x_cleaned=[el.replace("'",'') for el in x]

    return x_cleaned


def clean_cuisines_list(x:str) -> list:
    """ Converts cuisine list from string format to list """
    x_cleaned=str(x).replace('[','').replace(']','')
    x_cleaned=to_list(x_cleaned)
    x_cleaned=remove_doublequotes(x_cleaned)
    
    return x_cleaned


def get_reviewers_ids(reviews_list):
    """ Extracts reviewer names from all reviews """
    reviewers_ids=[review['reviewer'] for review in reviews_list if review['reviewer'] is not None]

    return reviewers_ids



def group_reviews_by_reviewers(df_restaurants, all_reviews, all_reviewers) -> object:
    """ Extracts information about reviewers from the reviews:
    Input:
        - df_restaurants: data frame restaurants
        - all_reviews: list of all the reviews
        - all_reviewers: list of reviewers names (that have posted 10 reviews or more)
    Output:
        - dataframe containing all the information regarding the reviewers
    """ 
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
                    reviewer_info_item['review_quote']=all_reviews[i][j]['review_quote']
                    reviewer_info_item['review_date']=all_reviews[i][j]['review_date']
                    reviewer_info_item['helpful_vote']=all_reviews[i][j]['helpful_vote']
                    reviewer_info_item['restaurant_name']=df_restaurants.iloc[i]['name']
                    reviewer_info_item['restaurant_cuisines']=df_restaurants.iloc[i]['cuisines']
                    reviewer_info_item['restaurant_special_diets']=df_restaurants.iloc[i]['special_diets']
                    reviewer_info['reviews'].append(reviewer_info_item)
        reviewer_info['number_Zurich_reviews']=len(reviewer_info['reviews'])
        reviewers_info.append(reviewer_info)
    reviewers_info_df=pd.DataFrame(reviewers_info)
    
    return reviewers_info_df



def price_range_int(price_range:str) -> int:
    """
    Computes the mean of price range.
    Example:
        - input: [20, 30]
        - output: 25 CHF
    """
    if price_range=='[]':
        return None
    else:
        price_range=price_range.split(',')
        price_range_int=[re.sub("[^0-9]", "", e) for e in price_range]
        price_range_int=[int(e) for e in price_range_int]
        
        return price_range_int


def price_min(price_range_str:str) -> int:
    """Returns price min from price range"""
    price_range=price_range_int(price_range_str)
    print('price_range: ', price_range)
    if price_range==None:
        return None
    else:    
        return price_range[0]


def price_max(price_range_str:str) -> int:
    """Returns price max from price range"""
    price_range=price_range_int(price_range_str)
    if price_range==None:
        return None
    else:    
        return price_range[1]


##################################### EXECUTION ##############################

def transform_data(df_restaurants):

    df_restaurants=pd.read_csv(f'./scraped_data/scraped_data.csv')
    df_restaurants.drop_duplicates(subset=['url'],inplace=True)
    df_restaurants.dropna(subset=['cuisines','special_diets'], how='all', inplace=True)
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
    df_restaurants['reviews'] = df_restaurants['reviews'].apply(lambda x: remove_non_ascii(x))
    cleaned_reviews= [ast.literal_eval(reviews[i]) for i in range(len(reviews))]
    df_restaurants['reviews']=cleaned_reviews

    # transform dataset: put list of cuisines in a usable format + get price min and price max
    df_restaurants['cuisines']=df_restaurants['cuisines'].apply(lambda x: clean_cuisines_list(x))
    df_restaurants['price_min']=df_restaurants['price_range'].apply(lambda x: price_min(x))
    df_restaurants['price_max']=df_restaurants['price_range'].apply(lambda x: price_max(x))

    # save transformed dataset
    df_restaurants.rename(columns={'num reviews': 'number_reviews'}, inplace=True)
    df_restaurants=df_restaurants[['url', 'name', 'location', 'number_reviews', 'price_min', 'price_max', 'cuisines', 'special_diets']]
    df_restaurants.to_csv(f'./transformed_data/restaurants_info_clean.csv', index=False)

    # extract reviewers ids
    print('Extracting reviewers ids...')
    reviewers=[get_reviewers_ids(item) for item in cleaned_reviews]
    reviewers_flat_list=[item for sublist in reviewers for item in sublist]
    reviewers=Counter(reviewers_flat_list).most_common()
    print(len(reviewers), '...reviewers found.')

    df_reviewers=pd.DataFrame(reviewers)
    df_reviewers.rename(columns={0: 'reviewer_name', 1: 'reviewer_posted_reviews'}, inplace=True)
    df_reviewers=df_reviewers[df_reviewers['reviewer_name']!=' ']
    
    # save transformed dataframe
    if not os.path.exists(f"./transformed_data"):
        os.makedirs(f"./transformed_data")
    urls_df.to_csv('./transformed_data/urls.csv', index=False)  
    df_reviewers.to_csv(f'./transformed_data/reviewers.csv', index=False)

    # group restaurants info by reviewers (reviewers with a minimum of 10 reviews)
    reviewers_relevant=df_reviewers[df_reviewers['reviewer_posted_reviews']>=10]['reviewer_name'].values.tolist()
    reviewers_info_df=group_reviews_by_reviewers(df_restaurants,cleaned_reviews,reviewers_relevant)
    reviewers_info_df.to_csv(f'./transformed_data/reviewers_info_clean.csv',index=False)