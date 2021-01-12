#!/usr/bin/env python
# coding: utf-8

from flask import render_template, request
from . import functions as functions
from app import app
import time
import math

@app.route('/', methods=['GET', 'POST'])
def index():

    user = {'username': 'Thibault'}
    price_ranges=["Cheap","Middle Range", "Gastronomic"]
    popularity_choices=["Mainstream","Medium","Promising Discovery"]
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

    price_range_input=[]
    popularity_input=[]
    cuisine_countries_input=[]
    best_matching_restaurants=''
    other_restaurants=''
    message_user_profile=''
    message_results_best=''
    message_results_others=''

    if request.method == 'POST':
        
        time.sleep(5)
        for price_range in price_ranges:
            price_range_input.append(request.form.get(price_range))

        for popularity in popularity_choices:
            popularity_input.append(request.form.get(popularity))

        for cuisine in cuisine_countries:
            cuisine_countries_input.append(request.form.get(cuisine))
        
        price_range_input_list = ['0' if v is None else v for v in price_range_input]
        popularity_input_list = ['0' if v is None else v for v in popularity_input]
        cuisine_countries_input_list = ['0' if v is None else v for v in cuisine_countries_input]

        print(price_range_input_list)
        print(popularity_input_list)
        print(cuisine_countries_input_list)

        #convert input to integer
        price_range_input_list=[int(x) for x in price_range_input_list]
        popularity_input_list=[int(x) for x in popularity_input_list]
        cuisine_countries_input_list =[int(x) for x in cuisine_countries_input_list]

        best_matching_restaurants, other_restaurants, favorite_cuisines = functions.get_list(price_range_input_list,popularity_input_list,cuisine_countries_input_list)
        time.sleep(2)

        sorted_prices = [[x,y] for x,y in sorted(zip(price_range_input_list,price_ranges), reverse=True)]
        favorite_prices=[item[1] if item[0]>0 else '' for item in sorted_prices]
        sorted_popularity = [[x,y] for x,y in sorted(zip(popularity_input_list,popularity_choices), reverse=True)]
        favorite_popularity=[item[1] if item[0]>0 else '' for item in sorted_popularity]

        message_user_profile=['Your profile: ']
        for item in favorite_cuisines:
            message_user_profile.append(item)
        message_user_profile.append(favorite_prices[0])
        message_user_profile.append(favorite_popularity[0])
        message_user_profile=" ".join(message_user_profile)
        
        print(best_matching_restaurants)
        message_results_best='Best restaurants for you: '
        message_results_others='You might also like: '
   
    return render_template('index.html', user=user, cuisine_countries=cuisine_countries, best_matching_restaurants=best_matching_restaurants, 
                                         other_restaurants=other_restaurants, message_user_profile=message_user_profile, 
                                         message_results_best=message_results_best, message_results_others=message_results_others)


