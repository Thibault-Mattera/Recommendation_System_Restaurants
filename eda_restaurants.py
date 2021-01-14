# -*- coding: utf-8 -*-
"""
Exploratory Data Analysis - Restaurants

"""

##################################### Dependencies ##############################

import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from collections import Counter
import re
import ast
import warnings
warnings.filterwarnings("ignore")

##################################### Functions #################################


def mean_price_ranges(x):
    range_price=x.replace('[', '').replace(']', '').split(',')
    int_ranges=[int(y) for y in range_price]
    mean_price_range=np.mean(int_ranges)
    return mean_price_range

def normalize(X):
    X=np.reshape(X, (-1, 1))
    scaler = MinMaxScaler()
    X_normalized=scaler.fit_transform(X)
    return X_normalized

def map_count_list(x_list,element):
    value_count=0
    for item in x_list:
        if item==element:
            value_count=1
    return value_count

def mean_price_ranges(x):
    range_price=x.replace('[', '').replace(']', '').split(',')
    int_ranges=[int(y) for y in range_price]
    mean_price_range=np.mean(int_ranges)
    return mean_price_range

def get_total_number_of_reviews(reviews)
    n_reviews=[]
    n_reviews_tot=0
    for item in reviews:
        n_reviews.append(len(item))
        n_reviews_tot+=len(item)
    print('There is ', n_reviews_tot, 'reviews in total')

def correlation(dataset,feature_1,feature_2):
    x=normalize(dataset[feature_1].values)
    y=normalize(dataset[feature_2].values)
    print(pd.DataFrame(x,y).corr())
    plt.scatter(x,y)
    plt.xlabel('feature_1')
    plt.ylabel('feature_2')
    plt.show()

def plot_distribution(n_reviews)
# Plot distribution - number of reviews per restaurant
    plt.hist(n_reviews, bins='auto', rwidth=0.85)
    plt.xlim(0, 1000)
    plt.xlabel('Number of reviews')
    plt.ylabel('Count')
    plt.show()

def get_top_list_cuisines(x):
    flat_list = [item for sublist in c for item in sublist]
    c_s=set(flat_list)
    cuisines=list(c_s)
    print(Counter(flat_list).most_common())
    return cuisines

def plot_cuisines_vs_prices(dataset):
    mean_price_cuisine=[]
    count_cuisine=[]
    for cuisine in cuisines:
        df_filtered=df_cuisines_price[df_cuisines_price[cuisine]==1]
        mean_price_cuisine.append(np.mean(df_filtered['mean_price'].values))
        count_cuisine.append(df3[cuisine].sum())
    dataset_group_by_cuisines=pd.DataFrame(cuisines,mean_price_cuisine)
    dataset_group_by_cuisines['count_cuisine']=count_cuisine
    dataset_group_by_cuisines.reset_index(inplace=True)
    dataset_group_by_cuisines.columns=['mean_price','cuisine','count_cuisine']
    dataset_group_by_cuisines=dataset_group_by_cuisines[dataset_group_by_cuisines['count_cuisine']>5]
    dataset_group_by_cuisines=dataset_group_by_cuisines.sort_values(by='mean_price',ascending=False)
    sns.set(rc={'figure.figsize':(11.7,5.27)})
    sns.barplot(x="cuisine", y='mean price', data=dataset_group_by_cuisines)
    plt.xticks(rotation=90)
    plt.title('Mean price of most common cuisines')
    plt.tight_layout()
    plt.show()


##################################### EXECUTION ##############################

# load dataset
dataset=pd.read_csv('data/restaurants_info_cleaned.csv')

# Price & Nb of Review correlation

df_price_reviews=dataset[['price_range','num reviews']]
df_price_reviews.dropna(subset=['price_range'],inplace=True)
df_price_reviews=df_price_reviews[df_price_reviews['price_range']!='[]']
# compute mean of price ranges
df_price_reviews['mean_price_range']=df_price_reviews['price_range'].apply(lambda x: mean_price_ranges(x))
# plot correlation
correlation(df_price_reviews,'mean_price_range', 'num reviews')

# Correlations between cuisine types

df_cuisines=dataset[['url','cuisines']]
df_cuisines.dropna(inplace=True)

# get cuisines top list
list_cuisines=get_top_list_cuisines(df2['cuisines'].values.tolist())

# count cuisine type for each restaurants
for cuisine in list_cuisines:
    df_cuisines[cuisine]=df_cuisines['cuisines'].apply(lambda x: map_count_list(x, cuisine))

# correlations between European cuisines
df_cuisines_corr=df_cuisines.ix[:,['Swiss','European','Central European','Mediterranean',
                            'Italian','International','French','German','Latin','Austrian', 'Spanish']].corr()
sns.heatmap(df_cuisines_corr)

"""Strong correlations between:
- Swiss and European cuisines
- Swiss and Central European
- Italian and Mediteraranean
"""

# correlations between Middle Eastern/Arabic cuisines
df_cuisines_corr=df_cuisines.ix[:,['Arabic','Turkish','Moroccan','Lebanese','Israeli','Middle Eastern']].corr()
sns.heatmap(df_cuisines_corr)

# correlations between Asian cuisines
df_cuisines_corr=df_cuisines.ix[:,['Asian','Thai','Japanese','Vietnamese','Korean',
                                    'Sushi','Japanese Fusion','Tibetan','Chinese','Indian']].corr()
sns.heatmap(df_cuisines_corr)

"""Strong correlations between:
- Japanese and Sushi
"""

# correlations between Asian cuisines
df2_corr=df2.ix[:,['American','South American','Central American','Fast Food','Native American','Steakhouse','Street Food']].corr()
sns.heatmap(df2_corr)


# Correlations between Cuisines and Price

df_cuisines_price=dataset[['price_range','cuisines']]
df_cuisines_price.dropna(inplace=True)
df_cuisines_price=df_cuisines_price[df_cuisines_price['price_range']!='[]']
df_cuisines_price['mean_price']=df_cuisines_price['price_range'].apply(lambda x: mean_price_ranges(x))
for cuisine in cuisines:
    df3[cuisine]=df3['cuisines_list'].apply(lambda x: map_count_list(x, cuisine))

plot_cuisines_vs_prices(df_cuisines_price)