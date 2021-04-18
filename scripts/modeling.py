#!/usr/bin/env python
# coding: utf-8
""" 
Modelling: build reviewers clusters with K-means method
"""

#################################### Dependencies ##############################

import pandas as pd
import ast
import numpy as np
from sklearn.cluster import KMeans
from matplotlib.pyplot import cm
# import Elbow method visualizer
from yellowbrick.cluster import KElbowVisualizer
#from kmodes.kmodes import KModes
from sklearn.metrics import pairwise_distances_argmin_min
import warnings
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt
from collections import Counter
import pickle
import seaborn as sns


##################################### Functions ##############################


def get_unique_elements(column_name:str) -> list:
    """ Extract unique elements from a column as a list
    """
    c=data_to_cluster[column_name].values.tolist()
    cuisines_list=[]
    for i in range(len(c)):
        item=ast.literal_eval(c[i])
        for j in range(len(item)):
            cuisines_list.append(item[j][0])
    c_s=set(cuisines_list)
    cuisines=list(c_s)
    return cuisines

def map_count_list(x,element) -> int:
    """ Counts the number of occurence of a specific element within the list of cuisines"""
    x_list=ast.literal_eval(str(x))
    value_count=0
    for item in x_list:
        if item[0]==element:
            value_count=item[1]
    return value_count


def total_tags(x) -> int:
    """Sum the total number of tags within a list of cuisines"""
    x_list=ast.literal_eval(str(x))
    total_tags=0
    for el in x_list:
        total_tags=total_tags+el[1]
    return total_tags


def kmeans(points,n_clusters):
    """
    Cluster observations with K-means method
    returns labels and fitted model
    """
    # create kmeans object
    kmeans = KMeans(n_clusters=n_clusters)
    # fit kmeans object to data
    kmeans.fit(points)
    # print location of clusters learned by kmeans object
    print(kmeans.cluster_centers_)
    # save new clusters for chart
    y_km = kmeans.fit_predict(points)

    print('Clusters partition: ', Counter(y_km))
    
    return y_km, kmeans

    
def plot_clusters_cuisines(i,cuisine_countries_clusters):
    """ Visual analysis of the clusters with types of cuisine
    """
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


def elbow_visualizer(matrix):
    """Elbow method to optimize the number of clusters with the K-means algorithm
    """
    model = KMeans()
    visualizer = KElbowVisualizer(model, k=(1,20))
    visualizer.fit(matrix)      
    visualizer.poof()


##################################### Execution ##############################


data_to_cluster=pd.read_csv('./reviewers_preprocessed.csv',usecols=['reviewer_name','restaurants_urls','cuisine_countries','cuisine_styles'])
data_to_cluster.dropna(subset=['cuisine_countries'],inplace=True)

# remove outlier
data_to_cluster.reset_index(level=0, inplace=True)
del data_to_cluster['index']

cuisine_countries=get_unique_elements('cuisine_countries')
cuisine_styles=get_unique_elements('cuisine_styles')
print('cuisine_countries: ', cuisine_countries)
print('cuisine_styles: ', cuisine_styles)

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


"""## Cuisines Clustering"""

index_cuisine_countries=data_to_cluster.columns.get_loc(cuisine_countries[0])
X_cat_1=data_to_cluster.iloc[:,index_cuisine_countries:index_cuisine_countries+len(cuisine_countries)].values
np.save('./X_cat_1.npy', X_cat_1) # save natrix for remmendation engine

elbow_visualizer(X_cat_1)

# cluster reviewers by cuisines
cuisine_countries_clusters, km_model_X_cat_1=kmeans(X_cat_1,4)

data_cuisines=data_to_cluster.iloc[:, 8:8+len(cuisine_countries)-1]
data_cuisines['cuisine_countries_cluster']=cuisine_countries_clusters

# Analyze cuisines clusters
group_by_cluster=data_cuisines.groupby(by=["cuisine_countries_cluster"]).mean()
for i in range(len(group_by_cluster)):
    plot_clusters_cuisines(i,cuisine_countries_clusters)

# Save to file in the current working directory
with open("./cuisine_countries_km.pkl", 'wb') as file:
    pickle.dump(km_model_X_cat_1, file)

# merge 2 metadata sets
data_summarized=data_to_cluster[['reviewer_name','restaurants_urls']]
data_summarized['cuisine_countries_cluster']=data_cuisines['cuisine_countries_cluster']
data_summarized.reset_index(level=0, inplace=True)
del data_summarized['index']

# save final labeled data for webapp
data_summarized.to_csv('./metadata.csv',index=False)