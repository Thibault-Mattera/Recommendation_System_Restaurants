import pandas as pd
import numpy as np
import pickle
import joblib
from sklearn.metrics import pairwise_distances_argmin_min
import ast
import os
import re


###################################### FUNCTIONS #######################################


def load_metadata() -> object:
    if os.path.isfile(f"models/metadata.csv"):
        return pd.read_csv('models/metadata.csv')
    else:
        raise Exception("Metadata is missing")    


def load_matrix_cuisines() -> object:
    if os.path.isfile(f"models/X_cat_1.npy"):
        return np.load('models/X_cat_1.npy')
    else:
        raise Exception("Matrix for cuisines clusters is missing")
    

def load_clustering_model() -> object:
    if os.path.isfile(f"models/cuisine_countries_km.pkl"):
        with open('models/cuisine_countries_km.pkl', 'rb') as pickle_file:
            km_model_X_cat_1 = pickle.load(pickle_file)
            return km_model_X_cat_1
    else:
        raise Exception("Clustering model (pickle file) is missing")


def get_user_cluster(cuisine_regions_input:list, cuisine_regions_list:list, model_clustering: object) -> int:
    """
    Returns the user's cluster based on his profile (cuisine preference)
        *Input: 
            - user input (list of prefered cuisine(s))
            - cuisine regions list
            - pre-trained clustering model (k-means)
        *Output:
            - user cluster (integer)
    """

    cuisine_regions_dict = {}
    for i in range(len(cuisine_regions_list)):
        cuisine_regions_dict[cuisine_regions_list[i]]=cuisine_regions_input[i]
    # normalize
    cuisine_regions_normalized=cuisine_regions_input/np.array(cuisine_regions_input).sum()
    cuisine_regions_normalized=np.array([cuisine_regions_normalized])
    user_cluster=model_clustering.predict(cuisine_regions_normalized)[0]
    
    return user_cluster


def get_restaurants_from_user_cluster(metadata:object, user_cluster:int) -> list:

    """
    Extracts list of restaurants urls corresponding to user cluster
        Inputs:
            - Metadata
            - user cluster
        Output: 
            - list of restaurants
    """

    restaurants_same_cluster=metadata[metadata['cuisine_countries_cluster']==user_cluster]['restaurants_urls'].values.tolist()
    restaurants_same_cluster=[ast.literal_eval(item) for item in restaurants_same_cluster]
    restaurants_same_cluster_flatten = [item for sublist in restaurants_same_cluster for item in sublist]
    restaurants_same_cluster=list(set(restaurants_same_cluster_flatten))  
    restaurants_same_cluster=get_restaurants_info(restaurants_same_cluster)

    return restaurants_same_cluster


def get_restaurants_info(matching_restaurants_urls:list) -> list:
    """
    Get restaurant info from database 
        - Input: list of restaurants urls 
        - output: list of dictionnaries containing restaurant's info: 
                url, name, price_range, cuisines, location, number of reviews
    """

    # load restaurant database
    fields=['url','name','price_range','cuisines','location','num reviews']
    dataset=pd.read_csv('data/restaurants_database.csv', usecols=fields)
    # match with restaurants
    matching_restaurants=dataset[dataset['url'].isin(matching_restaurants_urls)].to_dict('records')
    
    return matching_restaurants


def mean_price_ranges_int(price_range:str) -> int:
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
        
        return np.mean(price_range_int)


def filter_restaurants_by_price(matching_restaurants:list, price_input:int) -> list:
    """
    Filter list of restaurants by price: select restaurants with price equal or lower than user input
    """
    
    matching_restaurants=pd.DataFrame(matching_restaurants)
    price_ranges_list=matching_restaurants['price_range'].values.tolist()
    restaurants_prices=[mean_price_ranges_int(price_range) for price_range in price_ranges_list]
    matching_restaurants['price_mean']=restaurants_prices
    restaurants_filtered_price=matching_restaurants[matching_restaurants['price_mean']<=price_input].to_dict('records')

    return restaurants_filtered_price


def filter_restaurants_by_reviews(matching_restaurants:list, number_reviews_input:int) -> list:
    """
    Filter list of restaurants by price: select restaurants with number of reviews equal or higher than user input
    """
    
    matching_restaurants=pd.DataFrame(matching_restaurants)
    number_reviews_list=matching_restaurants['num reviews'].values.tolist()
    number_reviews_list=[int(number_reviews) for number_reviews in number_reviews_list]
    matching_restaurants['num reviews']=number_reviews_list
    restaurants_filtered_reviews=matching_restaurants[matching_restaurants['num reviews']>=number_reviews_input].to_dict('records')
    
    return restaurants_filtered_reviews


def get_user_favorite_cuisines(cuisine_regions_input:list, cuisine_regions_list:list) -> list:
    """
    Extract favorite cuisines from user input
        - input: user input (cuisine_regions_input), cuisine_regions_list
        - output: user's favorite cuisines (list of string)
    """
    sorted_cuisines = [[x,y] for x,y in sorted(zip(cuisine_regions_input,cuisine_regions_list), reverse=True)]
    user_favorite_cuisines=[item[1] for item in sorted_cuisines if item[0]>0]
    
    return user_favorite_cuisines


def sort_matching_restaurants(matching_restaurants:list, favorite_cuisines:list) -> list:
    """
    Sort list of matching restaurants by order of preference (cuisines)
    """
    matching_restaurants_dataframe=pd.DataFrame(matching_restaurants)
    # filter restaurant list to display relevant ones
    if len(favorite_cuisines)>0:
        if len(favorite_cuisines)>1:
            string_favorite_cuisines='|'.join(favorite_cuisines)
        else:
            string_favorite_cuisines=favorite_cuisines[0]
        restaurants_filtered_dataframe=matching_restaurants_dataframe[matching_restaurants_dataframe['cuisines'].str.contains(string_favorite_cuisines)]
        restaurants_filtered_list=restaurants_filtered_dataframe.to_dict('records')
        # limit list to 5 restaurants 
        if len(restaurants_filtered_list)>5:
            return restaurants_filtered_list[:5]
        else: 
            return restaurants_filtered_list
    # else keep original list
    else:
        return None

def get_more_restaurants(user_cluster:int, metadata:object, restaurants_first_list:list, price_input:int, number_reviews_input:int) -> list:
    
    """
    Provide a complementary list of restaurant from user's cluster (same price and budget but different cuisines)
        - input: user's cluster, metadata (dataframe), first list of restaurants
        - output: complementary list of restaurants
    """
    
    restaurants_same_cluster=metadata[metadata['cuisine_countries_cluster']==user_cluster]['restaurants_urls'].values.tolist()
    restaurants_same_cluster=[ast.literal_eval(item) for item in restaurants_same_cluster]
    restaurants_same_cluster_flatten = [item for sublist in restaurants_same_cluster for item in sublist]
    # remove duplicates
    restaurants_same_cluster=list(set(restaurants_same_cluster_flatten))  
    restaurants_first_list_urls=[item['url'] for item in restaurants_first_list]
    restaurants_second_list=[item for item in restaurants_same_cluster if item not in restaurants_first_list_urls]

    restaurants_second_list=get_restaurants_info(restaurants_second_list)

    # filter by prefered price
    matching_restaurants_price=filter_restaurants_by_price(restaurants_second_list,price_input)
    if len(matching_restaurants_price)>0:
        restaurants_second_list=matching_restaurants_price
    
    # fitler by minimum number of reviews
    matching_restaurants_reviews=filter_restaurants_by_reviews(restaurants_second_list,number_reviews_input)
    if len(matching_restaurants_reviews)>0:
        restaurants_second_list=matching_restaurants_reviews
    
    # limit to 10 restaurants
    if len(restaurants_second_list)>5:
        restaurants_second_list=restaurants_second_list[:5]

    return restaurants_second_list


############################## EXECUTION #######################################


def load_models() -> object:
    """
    Load objects to make recommendationsw:
        - metadata: labeled reviewers (csv file)
        - matrix_cuisines: normalized vectors of reviewers's favorite cuisines)
        - model_clustering: pre-trained clustering model (k-means)

    """

    metadata=load_metadata()
    matrix_cuisines=load_matrix_cuisines()
    model_clustering=load_clustering_model()

    return metadata, matrix_cuisines, model_clustering


def find_restaurants(price_input:int, number_reviews_input:int, cuisine_regions_input:list) -> list:
    """Get list of recommended restaurants based on user profile.
    Inputs:
        - price_input: user's maximum budget
        - number_reviews_input: minimum number of reviewers for the restaurants
        - cuisine_regions_input: user's prefered cuisines
    Returns:
        - list of recommended restaurants (best match)
    """   
    # parameters
    cuisine_regions_list=['American',
                    'Chinese',
                    'French',
                    'German',
                    'Indian',
                    'Italian',
                    'Japanese',
                    'Mexican',
                    'Middle Eastern',
                    'South American',
                    'Spanish',
                    'Swiss',
                    'Thai',
                    'Vietnamese']

    # load metadata & clustering model
    metadata, matrix_cuisines, model_clustering = load_models()

    # get user cluster
    user_cluster=get_user_cluster(cuisine_regions_input,cuisine_regions_list,model_clustering)
    
    # get list of restaurants from user cluster
    restaurants_first_list=get_restaurants_from_user_cluster(metadata,user_cluster)
    
    # get user's favorite cuisine
    user_favorite_cuisines=get_user_favorite_cuisines(cuisine_regions_input,cuisine_regions_list)

    # get first sorted list of restaurants (best match) - based on user's favorite cuisine
    best_matching_restaurants=sort_matching_restaurants(restaurants_first_list,user_favorite_cuisines)
    if best_matching_restaurants is not None:
        restaurants_first_list=best_matching_restaurants

    # filter by prefered price
    matching_restaurants_price=filter_restaurants_by_price(restaurants_first_list,price_input)
    if len(matching_restaurants_price)>0:
        restaurants_first_list=matching_restaurants_price
    
    # fitler by minimum number of reviews
    matching_restaurants_reviews=filter_restaurants_by_reviews(restaurants_first_list,number_reviews_input)
    if len(matching_restaurants_reviews)>0:
        restaurants_first_list=matching_restaurants_reviews

    # get second list of restaurants (might also like)
    restaurants_second_list=get_more_restaurants(user_cluster,metadata,restaurants_first_list,price_input,number_reviews_input)
    
    return restaurants_first_list, restaurants_second_list, user_favorite_cuisines