import pandas as pd
from time import time
from datetime import datetime
from sqlalchemy import Column, Integer, Float, Date, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

class Restaurant(Base):
    __tablename__='restaurants'
    restaurant_id=Column(Integer, primary_key=True)
    restaurant_url = Column(String)
    restaurant_name = Column(String)
    restaurant_price_range = Column(String)
    restaurant_cuisines = Column(String)
    restaurant_special_diets = Column(String)
    restaurant_location = Column(String)
    restaurant_reviews = Column(String)

def Load_Data(file_name):
    """
    Reads scraped data (csv file) and returns a dataframe 
    """

    fields = ['url','name','price_range','cuisines','special_diets','location','num reviews']
    data_frame = pd.read_csv(file_name,usecols=fields)
    data=data_frame.to_dict('records')
    return data

def create_database():

    #Create the database
    basedir = os.path.abspath(os.path.dirname(__file__))
    engine = create_engine('sqlite:///' +os.path.join(basedir, 'restaurants.db'))
    metadata = MetaData()
    Base.metadata.create_all(engine)

    #Create the session
    session = sessionmaker()
    session.configure(bind=engine)
    session_db = session() 

    return session_db


def seed_data_base(s):
   
    """
    Creates an SQL database from scraped data (csv file)
    """

    t = time() 
    try:
        file_name = "../data/restaurants_database.csv" #sample CSV file used:  http://www.google.com/finance/historical?q=NYSE%3AT&ei=W4ikVam8LYWjmAGjhoHACw&output=csv
        data=Load_Data(file_name) 
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
                    restaurant_price_range=data_subset[i]['price_range'],
                    restaurant_cuisines=data_subset[i]['cuisines'],
                    restaurant_special_diets=data_subset[i]['special_diets'],
                    restaurant_location=data_subset[i]['location'],
                    restaurant_reviews=data_subset[i]['num reviews']
                )
                s.add(record) #Add all the records
            s.commit() #Attempt to commit all the records
        print('...Done.')
    except:
        s.rollback() #Rollback the changes on error
    finally:
        s.close() #Close the connection
    print("Time elapsed: " + str(time() - t) + " s.") #0.091s

session_db=create_database()
seed_data_base(session_db)