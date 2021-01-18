# Recommendation System for Restaurants in Zurich

## Project Overview

In a world where the large commercial offer is overwhelming us, online reviews have a significant impact on customers' decision.

This project consisted in creating a tool that proposes a personalized list of restaurants based on users profiles.
The different steps:
- Scraped around 1800 restaurants and 1900 reviewers' from TripAdvisor using Python and Selenium
- Engineered features from restaurants' description to extract usable information (type of cuisine, price range and popularity)
- Built profiles' clusters based on an unspervised learning algorithm (K-means)
- Productionized the solution: created a web-app connected to a Flask API

## Data gathering: web scraping

As, the first step of the project, I scraped around 1800 restaurants from TripAdvisor.
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

## Exploratory Data Analysis

With a high number of categorical variables (over 150 types of cuisine and special diet), it was important to reduce them by studying their correlations.

Correlations between European cuisines            |  Correlations between Asian cuisines   
:-------------------------:|:-------------------------:
![](/images/correlation1_resized.PNG)  |  ![](/images/correlation2.PNG)

Also, I found interested to analyze the correlations between prices and cuisines.

![](/images/price_cuisine_corr.png)

## Cleaning, preprocessing & feature engineering

First, when analyzing the categorical variables (, I created new columns:
- cuisines regions (refering to a region)
- cuisine style (refering to a type of served food: 'Pizza', 'Street Food',...)
- specific criteria ('Accept credit cards', 'Outdoor Seating', 'Vegatarian Friendly'...)

The approach to reduce the number of categorical among the cuisine countries was to:
- remove the too "general" categories that hide the relevant information  (example: "European", "International")
- assign the categories containing very low number of restaurant to a global one (example: "Peruvian", "Chilean" to a global region "South American")


## Modeling: Unsupervised learning

After trying different clustering methods, I concluded that K-Means provided satisfying results.

We can see below 4 main profiles of restaurants' customers:
- Cluster A: the ones that prefer Asian food rather than local Swiss cuisine
- Cluster B: the fans of Italian cuisine
- Cluster C: going everywhere
- Cluster D: the ones loyal to Swiss restaurants

<img src="/images/clusters.png" width="100%">

## Productionization

This final step consisted in building a recommendation engine.
I created a flask API connected to an HTML web-interface. 
The API takes the user profile to propose him a personalized selection of restaurant based on his preferences.

<img src="/images/Screenshot_updated.PNG" width="850">

The concept is simple and intuitive.
First, you select criteria that define your "restaurant customer profile":
- Cuisine style
- Price range
- Popularity (number of reviews)
Your profile is compared to the database containing the Trip Advisor reviewers' profiles.
The system finds the profiles that are closest to yours and extract the corresponding restaurants.

### Try it!

1. Clone repo locally
2. Create virtual environment & activate it
3. Install librairies & set flask config
4. Run flask webapp (command flask run)
5. Go to your localhost to access webapp

