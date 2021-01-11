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

    if request.method == 'POST':
        
        time.sleep(3)
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

    
        best_matching_restaurants, other_restaurants = functions.get_list(price_range_input_list,popularity_input_list,cuisine_countries_input_list)
        time.sleep(5)
        print(best_matching_restaurants)

   
    return render_template('index.html', user=user, cuisine_countries=cuisine_countries, best_matching_restaurants=best_matching_restaurants)


