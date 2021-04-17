#!/usr/bin/env python
# coding: utf-8
""" 
Load transformed data
"""

##################################### Dependencies ##############################

import pandas as pd
from time import time
from datetime import datetime
from sqlalchemy import Column, Integer, Float, Date, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
Base = declarative_base()

##################################### Functions #################################

class Restaurant(Base):
    __tablename__='restaurants_info'
    restaurant_id=Column(Integer, primary_key=True)
    restaurant_url = Column(String)
    restaurant_name = Column(String)
    restaurant_location = Column(String)
    restaurant_number_reviews = Column(Integer)
    restaurant_price_min= Column(Integer)
    restaurant_price_max= Column(Integer)
    restaurant_cuisines = Column(String)
    restaurant_special_diets = Column(String)


class Reviewer(Base):
    __tablename__='reviewers'
    reviewer_id=Column(Integer, primary_key=True)
    reviewer_name = Column(String)
    reviewer_number_Zurich_reviews = Column(String)


def load_transformed_data(file_name:str, fields:list) -> dict:
    """
    Reads transformed dataset (csv file) and returns a dataframe
        Input: 
            - file_name: name csv file
            - fields: list of columns to select
        Output:
            - dictionary
    """
    data_frame = pd.read_csv(file_name,usecols=fields)
    data=data_frame.to_dict('records')
    
    return data


def create_database(database_name:str):

    #Create the database
    basedir = os.path.abspath(os.path.dirname(__file__))
    if not os.path.exists(f"./loaded_data"):
        os.makedirs(f"./loaded_data")
    engine = create_engine('sqlite:///' +os.path.join(basedir, 'loaded_data/'+database_name+'.db'))
    metadata = MetaData()
    Base.metadata.create_all(engine)

    #Create the session
    session = sessionmaker()
    session.configure(bind=engine)
    session_db = session() 

    return session_db


def seed_restaurants_table(s):
   
    """
    Creates an SQL database from scraped data (csv file)
    """

    t = time() 
    file_name = "transformed_data/restaurants_info_clean.csv" #sample CSV file used:  http://www.google.com/finance/historical?q=NYSE%3AT&ei=W4ikVam8LYWjmAGjhoHACw&output=csv
    fields = ['url','name','location','number_reviews','price_min','price_max','cuisines','special_diets']
    data=load_transformed_data(file_name,fields) 
    print('data loaded')
    indexes=[j for j in range(0,len(data),100)]
    indexes.append(len(data))
    indexes_slices=[[indexes[j],indexes[j+1]] for j in range(len(indexes)-1)]
    print('Load restaurants database...')
    for j in range(len(indexes_slices)):
        data_subset=data[indexes_slices[j][0]:indexes_slices[j][1]]
        for i in range(len(data_subset)):
            record = Restaurant(
                restaurant_url= data_subset[i]['url'],
                restaurant_name=data_subset[i]['name'],
                restaurant_location=data_subset[i]['location'],
                restaurant_number_reviews=data_subset[i]['number_reviews'],
                restaurant_price_min=data_subset[i]['price_min'],
                restaurant_price_max=data_subset[i]['price_max'],
                restaurant_cuisines=data_subset[i]['cuisines'],
                restaurant_special_diets=data_subset[i]['special_diets'],
            )
            s.add(record) #Add all the records
        s.commit() #Attempt to commit all the records
    print('...Done.')
    print("Time elapsed: " + str(time() - t) + " s.") #0.091s



def seed_reviewers_table(s):
   
    """
    Creates an SQL database from scraped data (csv file)
    """

    t = time() 
    try:
        file_name = "transformed_data/reviewers_info_clean.csv" #sample CSV file used:  http://www.google.com/finance/historical?q=NYSE%3AT&ei=W4ikVam8LYWjmAGjhoHACw&output=csv
        fields = ['reviewer_name','number_Zurich_reviews']
        data=load_transformed_data(file_name,fields) 
        indexes=[j for j in range(0,len(data),100)]
        indexes.append(len(data))
        indexes_slices=[[indexes[j],indexes[j+1]] for j in range(len(indexes)-1)]
        print('Load reviewers database...')
        for j in range(len(indexes_slices)):
            data_subset=data[indexes_slices[j][0]:indexes_slices[j][1]]
            for i in range(len(data_subset)):
                record = Reviewer(
                    reviewer_name= data_subset[i]['reviewer_name'],
                    reviewer_number_Zurich_reviews=data_subset[i]['number_Zurich_reviews']
                )
                s.add(record) #Add all the records
            s.commit() #Attempt to commit all the records
        print('...Done.')
    except:
        s.rollback() #Rollback the changes on error
    finally:
        s.close() #Close the connection
    print("Time elapsed: " + str(time() - t) + " s.") #0.091s



##################################### Execution #################################

def load_data():

    # create database
    session_db=create_database('restaurants_reviews')

    # seed restaurants table
    seed_restaurants_table(session_db)

    # seed reviewers table
    seed_reviewers_table(session_db)