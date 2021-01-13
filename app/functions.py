
import pandas as pd
import numpy as np
import pickle
import joblib
from sklearn.metrics import pairwise_distances_argmin_min
import ast



###################################### FUNCTIONS #######################################

def to_list(x):

    x_list=str(x).split(',')

    return x_list


def get_cleaned_list(uncleaned_list):
    
    c_clean=[]
    for el in uncleaned_list:
        el_clean=[]
        for item in el:
            el_clean.append(" ".join(item.split()))
        c_clean.append(el_clean)
    
    return c_clean


def mean_price_ranges_int(int_ranges):
    
    if len(int_ranges)>1:
        for item in int_ranges:
            mean_price_range=np.mean(np.mean(item))
    else:
        mean_price_range=np.mean(int_ranges)
    
    return mean_price_range


def get_user_popularity_vector(popularity_input,nb_reviews_scaler):
    
    popularity_values=[1000,500,100]

    
    # set default value if user didn't enter anything
    if popularity_input==[0,0,0]:
        popularity_new_flat=popularity_values

    else: 
        popularity_new=[]  
        for i in range(len(popularity_values)):
            popularity_new_i=[]
            if popularity_input[i]>0:
                popularity_new_i=[]
                for j in range(0,popularity_input[i]):
                    popularity_new_i.append(popularity_input[i])
            elif popularity_input[i]==1:
                popularity_new_i=[popularity_values[i]]
            popularity_new.append(popularity_new_i)
            popularity_new_flat = [item for sublist in popularity_new for item in sublist]
    print('popularity_new_flat', popularity_new_flat)
    nb_reviews_new_mean=np.mean(popularity_new_flat)
    nb_reviews_new_mean=nb_reviews_scaler.transform(np.array(nb_reviews_new_mean).reshape(-1, 1))

    return nb_reviews_new_mean


def get_user_price_range_vector(price_range_input,price_scaler):
    
    price_range_values=[[10,30],[30,50],[50,100]]
    
    price_range_new=[]
    for i in range(len(price_range_values)):
        price_range_new_i=[]
        if price_range_input[i]>1:
            for j in range(0,price_range_input[i]):
                price_range_new_i.append(price_range_values[i])
        elif price_range_input[i]==1:
            price_range_new_i=[price_range_values[i]]  
        price_range_new.append(price_range_new_i)
    price_range_new_flat = [item for sublist in price_range_new for item in sublist]

    # set default value if user didn't enter anything
    if price_range_input==[0,0,0]:
        price_range_new_flat=price_range_values

    price_range_new_mean=mean_price_ranges_int(price_range_new_flat)
    price_range_new_mean=price_scaler.transform(np.mean(price_range_new_mean).reshape(-1, 1))

    return price_range_new_mean


def get_user_price_review_cluster(price_range_input, popularity_input, km_model_X_num ,price_scaler ,nb_reviews_scaler):
    
    price_range_new_mean=get_user_price_range_vector(price_range_input,price_scaler)
    nb_reviews_new_mean=get_user_popularity_vector(popularity_input,nb_reviews_scaler)

    print('price_range_new_mean ',price_range_new_mean)
    print('nb_reviews_new_mean ',nb_reviews_new_mean)
    X_num_new=np.array([[price_range_new_mean[0][0],nb_reviews_new_mean[0][0]]])

    price_review_cluster_new=km_model_X_num.predict(X_num_new)[0]

    return price_review_cluster_new


def get_cuisine_countries_cluster(cuisine_countries_input,km_model_X_cat_1, cuisine_countries):

    
    cuisine_countries_new=[]
    for i in range(len(cuisine_countries)):
        cuisine_countries_new.append([cuisine_countries[i],cuisine_countries_input[i]])
    
    # set default value if user didn't enter anything
    if cuisine_countries_input==[0 for i in range(len(cuisine_countries))]:
        cuisine_countries_new=[]
        for i in range(len(cuisine_countries)):
            cuisine_countries_new.append([cuisine_countries[i],1])

    total_cuisine_countries_new=[]
    for i in range(len(cuisine_countries_new)):
        total_cuisine_countries_new.append(cuisine_countries_new[i][1])
    total_cuisine_countries_new=total_cuisine_countries_new/np.array(total_cuisine_countries_new).sum()
    X_cat_1_new=np.array([total_cuisine_countries_new])

    print(X_cat_1_new)
    cuisine_countries_cluster_new=km_model_X_cat_1.predict(X_cat_1_new)[0]

    return cuisine_countries_cluster_new


def find_matching_cluster(metadata,X_num,X_cat_1,price_review_cluster_new,cuisine_countries_cluster_new,km_model_X_num,km_model_X_cat_1):

    # get matching cluser
    matching_cluster=metadata[(metadata['price_review_cluster']==price_review_cluster_new) & (metadata['cuisine_countries_cluster']==cuisine_countries_cluster_new)]
    matching_cluster.reset_index(level=0, inplace=True)

    # get matching index
    matching_index=matching_cluster['index'].values.tolist()

    X_num_matching=X_num[matching_index]
    X_cat_1_matching=X_cat_1[matching_index]
    
    # Find reviewers that are closest to cluster center
    closest_price_review, _ = pairwise_distances_argmin_min(km_model_X_num.cluster_centers_, X_num_matching)
    closest_price_review_record=closest_price_review[price_review_cluster_new]
    
    #closest_price_review_record
    closest_cuisine, _ = pairwise_distances_argmin_min(km_model_X_cat_1.cluster_centers_, X_cat_1_matching)
    closest_cuisine_record=closest_cuisine[cuisine_countries_cluster_new]

    matching_restaurants=matching_cluster.loc[[closest_price_review_record,closest_cuisine_record],'restaurants_urls'].values.tolist()
    matching_restaurants_list=[ast.literal_eval(item) for item in matching_restaurants]
    flat_list = [item for sublist in matching_restaurants_list for item in sublist]
    r_s=set(flat_list)
    matching_restaurants_links=list(r_s)

    ### get restaurants info (name and cuisine)
    # load info database
    dataset=pd.read_csv('./app/data/restaurants_database.csv')
    dataset.drop_duplicates(subset=['url'],inplace=True)
    dataset.dropna(inplace=True)
    # match with restaurants
    matching_restaurants_info=dataset[dataset['url'].isin(matching_restaurants_links)]
    
    matching_restaurants_urls=matching_restaurants_info['url'].values.tolist()

    matching_restaurants_names=matching_restaurants_info['name'].values.tolist()

    print('matching_restaurants_names', matching_restaurants_names)

    #matching_restaurants_info['cuisines_list']=matching_restaurants_info['cuisines'].apply(lambda x: to_list(x))
    
    #matching_restaurants_cuisines=get_cleaned_list(matching_restaurants_info['cuisines_list'].values.tolist())
    matching_restaurants_cuisines=matching_restaurants_info['cuisines'].values.tolist()

    matching_restaurants=[]
    if len(matching_restaurants_urls)>1:
        for i in range(len(matching_restaurants_urls)):
            matching_restaurants.append({'link': matching_restaurants_urls[i],
                                         'name': matching_restaurants_names[i],
                                         'cuisines': matching_restaurants_cuisines[i]})
    else:
        matching_restaurants=[{'link':matching_restaurants_urls[0],
                               'name': matching_restaurants_names[0],
                               'cuisines': matching_restaurants_cuisines[0]}]

    return matching_restaurants


def sort_matching_restaurants(matching_restaurants, cuisine_countries_input, cuisine_countries):
    
    df_matching_restaurants=pd.DataFrame(matching_restaurants)
    
    sorted_cuisines = [[x,y] for x,y in sorted(zip(cuisine_countries_input,cuisine_countries), reverse=True)]

    favorite_cuisines=[]
    for i in range(len(sorted_cuisines)):
        if sorted_cuisines[i][0]>0:
            favorite_cuisines.append(sorted_cuisines[i][1])
            
    final_list=[]
    if len(favorite_cuisines)>0:
        if len(favorite_cuisines)>1:
            string_favorite_cuisines='|'.join(favorite_cuisines)
        else:
            string_favorite_cuisines=favorite_cuisines[0]
        print('string_favorite_cuisines: ',string_favorite_cuisines)

        df_final_list=df_matching_restaurants[df_matching_restaurants['cuisines'].str.contains(string_favorite_cuisines)]
        final_list_links=df_final_list['link'].values.tolist()
        final_list_names=df_final_list['name'].values.tolist()
        final_list_cuisines=df_final_list['cuisines'].values.tolist()

        if len(final_list_links)>1:
            for i in range(len(final_list_links)):
                final_list.append({'link': final_list_links[i],
                                'name': final_list_names[i],
                                'cuisines': final_list_cuisines[i]})
        elif len(final_list_links)>0:
            final_list=[{'link':final_list_links[0],
                        'name': final_list_names[0],
                        'cuisines': final_list_cuisines[0]}]
    
    if len(final_list)>0:
        display_restaurants_1=final_list
        if len(final_list)>10:
            display_restaurants_1=final_list[:10]
    else:
        if len(matching_restaurants)>10:
            display_restaurants_1=matching_restaurants[:10]
        else:
            display_restaurants_1=matching_restaurants
    return display_restaurants_1, favorite_cuisines

    
################################## EXECUTION #######################################


def get_list(price_range_input,popularity_input,cuisine_countries_input):
        
    #parameters
    cuisine_countries=['Mexican',
                        'Indian',
                        'French',
                        'American',
                        'Middle Eastern',
                        'Swiss',
                        'Japanese',
                        'Thai',
                        'Chinese/Korean',
                        'Pacific Islands',
                        'South American',
                        'British',
                        'Vietnamese',
                        'Spanish',
                        'German',
                        'Italian',
                        'Mediterranean']
    cuisine_countries.sort()

    #load metadata
    metadata=pd.read_csv('./app/data/metadata.csv')

    #df_num=pd.read_csv('./app/data/matrix_data.csv')
    #X_num=df_num.iloc[:,:].values
    X_num=np.load('./app/models/X_num.npy') # load
    X_cat_1=np.load('./app/models/X_cat_1.npy')


    # load models
    price_scaler = joblib.load('./app/models/price_scaler.gz')
    nb_reviews_scaler = joblib.load('./app/models/nb_reviews_scaler.gz')

    with open('./app/models/price_review_km.pkl', 'rb') as pickle_file:
        km_model_X_num = pickle.load(pickle_file)

    with open('./app/models/cuisine_countries_km.pkl', 'rb') as pickle_file:
        km_model_X_cat_1 = pickle.load(pickle_file)

    price_review_cluster_new=get_user_price_review_cluster(price_range_input, popularity_input,km_model_X_num,price_scaler,nb_reviews_scaler)
    cuisine_countries_cluster_new=get_cuisine_countries_cluster(cuisine_countries_input,km_model_X_cat_1, cuisine_countries)

    matching_restaurants=find_matching_cluster(metadata,X_num,X_cat_1,price_review_cluster_new,cuisine_countries_cluster_new,km_model_X_num,km_model_X_cat_1)

    short_list, favorite_cuisines=sort_matching_restaurants(matching_restaurants,cuisine_countries_input,cuisine_countries)

    others_list=[]
    for item in matching_restaurants:
        if item not in short_list:
            others_list.append(item)
    if len(others_list)>10:
         others_list= others_list[:10]

    return short_list, others_list, favorite_cuisines