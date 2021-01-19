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
                        'Chinese',
                        'South American',
                        'Vietnamese',
                        'Spanish',
                        'German',
                        'Italian']
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
        
        time.sleep(4)
        price_range_input=int(request.form.get('price'))

        popularity_input=int(request.form.get('popularity'))

        for cuisine in cuisine_countries:
            cuisine_countries_input.append(request.form.get(cuisine))

        
        cuisine_countries_input=['0' if v is None else '1' for v in cuisine_countries_input]
        cuisine_countries_input_list =[int(x) for x in cuisine_countries_input]

        best_matching_restaurants, other_restaurants, favorite_cuisines = functions.get_list(price_range_input,popularity_input,cuisine_countries_input_list)
        time.sleep(2)


        message_user_profile=['Your wish: ']
        for item in favorite_cuisines:
            message_user_profile.append(item)
        message_user_profile.append('with budget of  '+str(price_range_input)+' CHF')
        message_user_profile.append(' and with around '+str(popularity_input)+' reviews')
        message_user_profile=" ".join(message_user_profile)
        
        print(best_matching_restaurants)
        message_results_best='Best restaurants for you: '
        message_results_others='You might also like: '
   
    return render_template('index.html', user=user, cuisine_countries=cuisine_countries, best_matching_restaurants=best_matching_restaurants, 
                                         other_restaurants=other_restaurants, message_user_profile=message_user_profile, 
                                         message_results_best=message_results_best, message_results_others=message_results_others)