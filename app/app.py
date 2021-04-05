#!/usr/bin/env python
# coding: utf-8

from flask import Flask, jsonify, render_template, request
import functions as functions
import time
import math
#from database import Restaurant

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():

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

    user='Thibault'
    price_range_input=[]
    popularity_input=[]
    cuisine_regions_input=[]
    best_matching_restaurants=''
    other_restaurants=''
    message_user_profile=''
    message_results_best=''
    message_results_others=''

    if request.method == 'POST':
        
        time.sleep(4)
        price_input=int(request.form.get('price'))
        reviews_input=int(request.form.get('popularity'))
        cuisine_regions_input=[request.form.get(cuisine) for cuisine in cuisine_regions_list]
        print('cuisine_regions_input: ', cuisine_regions_input)
        cuisine_regions_input=[0 if v is None else 1 for v in cuisine_regions_input]
        
        # set default values to 1 if app didn't get user's input
        if set(cuisine_regions_input)==0:
            cuisine_regions_input=[1 for v in cuisine_regions_input]
        
        best_matching_restaurants, other_restaurants, favorite_cuisines = functions.find_restaurants(price_input,
                                                                                                    reviews_input,
                                                                                                    cuisine_regions_input)

        message_user_profile=['Your wish: ']
        for item in favorite_cuisines:
            message_user_profile.append(item)
        message_user_profile.append(' cuisine(s)')
        message_user_profile.append(' for a budget of '+str(price_input)+' CHF')
        message_user_profile.append('with a minimum of '+str(reviews_input)+' reviews')
        message_user_profile=" ".join(message_user_profile)
        
        message_results_best='Best restaurant(s) for you: '
        message_results_others='You might also like: '
   
    return render_template('index.html', user=user, cuisine_countries=cuisine_regions_list, best_matching_restaurants=best_matching_restaurants, 
                                         other_restaurants=other_restaurants, message_user_profile=message_user_profile, 
                                         message_results_best=message_results_best, message_results_others=message_results_others)

if __name__ == '__main__':
    app.run(debug=True)