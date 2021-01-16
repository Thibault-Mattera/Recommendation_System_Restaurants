# Recommendation System for Restaurants in Zurich

## Project Overview

A Recommendation System to find the restaurants in Zurich city that correspond you.

3 phasis in this project:
- Gather the data: scraping Trip Advisor data of all restaurants in Zurich (restaurants info, reviews, reviewer profiles)
- Build reviewer profiles: unsupervised learning
- Create recommendation system: flask api and user interface

### Data gathering: web scraping

As, the first step of the project, I scraped aroud 1800 restaurants from TripAdvisor.
For each restaurant, we extract the following information:
- Restaurant's URL
- Restaurant's title
- Price range & category ($ symbol)
- Cuisines
- Special diets
- Location
- Number of reviews
- Reviews (reviewer name, quote, body, date, helpful vote)

In complement, I scraped reviewers' profiles:
- reviewer's location
- reviewer's contribution (number of posted reviews)
- number of helpful votes
- joining date on TripAdvisor

### Data cleaning

I looked at the correlation

### Exploratory Data Analysis

With a high number of categorical variables (over 150 types of cuisine and special diet), it was important to reduce them by studying their correlations.

Correlations between European cuisines            |  Correlations between Asian cuisines   
:-------------------------:|:-------------------------:
![](/images/correlation1_resized.PNG)  |  ![](/images/correlation2.PNG)


Also, I found interested to analyze the correlations between prices and cuisines.



### Modeling: Unsupervised learning

![](/images/clusters_analysis.PNG)

### Productionization

This final step consisted in building a recommendation engine.
I created a flask API connected to an HTML web-interface. 
The API takes the user profile to propose him a personalized selection of restaurant based on his preferences.

#### How does it work?

First, you select criteria that define your "restaurant customer profile":
- Cuisine style
- Price range
- Restaurant' popularity
Your profile is compared to a database containing the Trip Advisor reviewers profiles.
The system finds the profiles that are closest to yours and extract the most corresponding restaurants.

#### Try it!

1. Clone repo locally

2. Create virtual environment & activate it

3. Install librairies & set flask config

pip install -r requirements.txt

export FLASK_APP=recom_engine.py

4. Run flask webapp

flask run

5. Go to your localhost to access webapp:

http://127.0.0.1:5000/

