# -*- coding: utf-8 -*-
"""
Clustering

"""

#################################### Dependencies ##############################

import pandas as pd
import ast
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
# import KMeans
from sklearn.cluster import KMeans, AgglomerativeClustering
# import colors from matplotlib
from matplotlib.pyplot import cm
# import Elbow method visualizer
from yellowbrick.cluster import KElbowVisualizer
#from kmodes.kmodes import KModes
from tkinter import *
from sklearn.metrics import pairwise_distances_argmin_min
import warnings
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
from collections import Counter
import tkinter as tk
import time
import ast
import joblib
import pickle

##################################### Functions ##############################


def get_unique_elements(column_name):
    c=data_to_cluster[column_name].values.tolist()
    cuisines_list=[]
    for i in range(len(c)):
        item=ast.literal_eval(c[i])
        for j in range(len(item)):
            cuisines_list.append(item[j][0])
    c_s=set(cuisines_list)
    cuisines=list(c_s)
    return cuisines

def map_count_list(x,element):
    x_list=ast.literal_eval(str(x))
    value_count=0
    for item in x_list:
        if item[0]==element:
            value_count=item[1]
    return value_count


def total_tags(x):
    x_list=ast.literal_eval(str(x))
    total_tags=0
    for el in x_list:
        total_tags=total_tags+el[1]
    return total_tags


def kmeans(points,n_clusters):
    """
    cluster observations with K-means method
    """
    # create kmeans object
    kmeans = KMeans(n_clusters=n_clusters)
    # fit kmeans object to data
    kmeans.fit(points)
    # print location of clusters learned by kmeans object
    print(kmeans.cluster_centers_)
    # save new clusters for chart
    y_km = kmeans.fit_predict(points)
    # Visualize clustering
    # set colors 
    colors=iter(cm.rainbow(np.linspace(0,1,n_clusters)))
    for i in range(n_clusters):
        plt.scatter(points[y_km ==i,0], points[y_km == i,1], s=100, color=next(colors), alpha = 0.5)
    # check clusters
    print('price and nb of reviews clusters: ', Counter(y_km))
    
    return y_km, kmeans

def standardize(X,scaler_type):
    X=np.reshape(X, (-1, 1))
    scaler = scaler_type
    X_normalized=scaler.fit_transform(X)
    return X_normalized, scaler


def clusters_analysis(data, feature_column, clusters_column):
    labels=data[clusters_column].unique().tolist()
    x_array=[]
    for label in labels:
        x_array.append(data[data[clusters_column]==label][feature_column].values)
    for i in range(len(x_array)):
        plt.hist(x_array[i], bins='auto', rwidth=0.85, label=str(i))
    plt.xlabel(feature_column)
    plt.ylabel('Count')
    plt.legend(loc='upper right')
    plt.show()

    
def plot_clusters_cuisines(i,cuisine_countries_clusters):
    import seaborn as sns
    df=pd.DataFrame(group_by_cluster.iloc[i,:])
    df.reset_index(level=0, inplace=True)
    df.columns=['cuisine','count']
    df=df.sort_values(by='count',ascending=False)
    sns.set(rc={'figure.figsize':(11.7,5.27)})
    sns.barplot(x="cuisine", y='count', data=df)
    plt.xticks(rotation=90)
    plt.title('cluster '+str(i)+ ' count: '+str(Counter(cuisine_countries_clusters)[i]))
    plt.tight_layout()
    plt.show()


def to_list(x):
    x_list=str(x).split(',')
    return x_list


def elbow_visualizer(x):
    model = KMeans()
    visualizer = KElbowVisualizer(model, k=(1,20))
    visualizer.fit(x)      
    visualizer.poof()


def normalize_category(x):
    total_tags=0
    for el in x:
        total_tags=total_tags+el[1]
    return round(x/total_tags,2)


##################################### Execution ##############################


data=pd.read_csv('data/reviewers_ready_for_clustering.csv')
data.dropna(inplace=True)

# remove outlier
data=data[data['mean_restaurants_reviews']<5000]
data_to_cluster=data[['reviewer_name','restaurants_urls','mean_price_range','mean_restaurants_reviews','cuisine_countries','cuisine_styles']]
data_to_cluster.reset_index(level=0, inplace=True)
del data_to_cluster['index']


cuisine_countries=get_unique_elements('cuisine_countries')
cuisine_styles=get_unique_elements('cuisine_styles')

## normalize tags count

data_to_cluster['total_countries_tags']=data_to_cluster['cuisine_countries'].apply(lambda x: total_tags(x))
data_to_cluster['total_styles_tags']=data_to_cluster['cuisine_styles'].apply(lambda x: total_tags(x))
for cuisine in cuisine_countries:
    data_to_cluster[cuisine]=data_to_cluster['cuisine_countries'].apply(lambda x: map_count_list(x, cuisine))
    data_to_cluster[cuisine]=round(data_to_cluster[cuisine]/data_to_cluster['total_countries_tags'],2)
for diet in cuisine_styles:
    data_to_cluster[diet]=data_to_cluster['cuisine_styles'].apply(lambda y: map_count_list(y, diet))
    data_to_cluster[diet]=round(data_to_cluster[diet]/data_to_cluster['total_styles_tags'],2)
data_to_cluster.dropna(inplace=True)


"""
Succsessive clustering approach

"""

"""Price and Review Clustering"""

# preprocess normalize prices and numbers of reviews
standardized_prices, price_scaler=standardize(data_to_cluster['mean_price_range'].values,RobustScaler())
standardized_nb_reviews, nb_reviews_scaler=standardize(data_to_cluster['mean_restaurants_reviews'].values,RobustScaler())
df_num=pd.DataFrame(standardized_prices)
df_num['standardized_nb_reviews']=standardized_nb_reviews
X_num=df_num.iloc[:,:].values
np.save('X_num.npy', X_num) #save matrix for recommendation engine

#  Determine the appropriate number of clusters using Elbow Analysis
elbow_visualizer(X_num)

# cluster price ranges and nb of reviews
price_review_clusters, km_model_X_num = kmeans(X_num,4)

# Analyse Price/review clusters
data_clustered_1=data_to_cluster.ix[:, 2:4]
data_clustered_1['price_review_cluster']=price_review_clusters
clusters_analysis(data_clustered_1, 'mean_price_range', 'price_review_cluster')
clusters_analysis(data_clustered_1, 'mean_restaurants_reviews', 'price_review_cluster')

# save models
joblib.dump(price_scaler, 'models/price_scaler.gz')
joblib.dump(nb_reviews_scaler, 'models/nb_reviews_scaler.gz')

# Save to file in the current working directory
with open("models/price_review_km.pkl", 'wb') as file:
    pickle.dump(km_model_X_num, file)

"""## Cuisines Clustering"""

index_cuisine_countries=data_to_cluster.columns.get_loc(cuisine_countries[0])
X_cat_1=data_to_cluster.iloc[:,index_cuisine_countries:index_cuisine_countries+len(cuisine_countries)].values
np.save('X_cat_1.npy', X_cat_1) # save natrix for remmendation engine

elbow_visualizer(X_cat_1)

# cluster reviewers by cuisines
cuisine_countries_clusters, km_model_X_cat_1=kmeans(X_cat_1,4)

data_clustered_2=data_to_cluster.ix[:, 8:8+len(cuisine_countries)-1]
data_clustered_2['cuisine_countries_cluster']=cuisine_countries_clusters

# Analyze cuisines clusters
group_by_cluster=data_clustered_2.groupby(by=["cuisine_countries_cluster"]).mean()
for i in range(len(group_by_cluster)):
    plot_clusters_cuisines(i,cuisine_countries_clusters)

# Save to file in the current working directory
with open("app/models/cuisine_countries_km.pkl", 'wb') as file:
    pickle.dump(km_model_X_cat_1, file)

# merge 2 metadata sets
data_summarized=data_to_cluster[['reviewer_name','restaurants_urls']]
data_summarized['price_review_cluster']=data_clustered_1['price_review_cluster']
data_summarized['cuisine_countries_cluster']=data_clustered_2['cuisine_countries_cluster']
data_summarized.reset_index(level=0, inplace=True)
del data_summarized['index']

# save final labeled data for webapp
data_summarized.to_csv('data/app/metadata.csv',index=False)