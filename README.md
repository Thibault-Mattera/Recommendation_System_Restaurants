# Recommendation System for Zurich Restaurants

## Project Description

A Recommendation System to find the restaurants in Zurich city that correspond you.

3 phasis in this project:
- Gather the data: scraping Trip Advisor data of all restaurants in Zurich (restaurants info, reviews, reviewer profiles)
- Build reviewer profiles: unsupervised learning
- Create recommendation system: flask api and user interface


## How does it work?

First, you select criteria that define your "restaurant customer profile":
- Cuisine style
- Price range
- Restaurant' popularity

Your profile is compared to a database containing different types of profile.
Each type of profile correspond to a specific cluster of Trip Advisor reviewers.

The system find the profiles that are closest yours and extract the restaurants these profiles have the most visited.


## Try it!

1. Clone repo locally
git clone https://github.com/Thib-Matt/Recommendation_System_Zurich_Restaurants.git

2. Create virtual environment & activate it
python3 -m venv my_env
source env/bin/activate

3. Install librairies
pip install -r requirements.txt

4. Run flask webapp
flask run

5. Go to your localhost to access webapp:
http://127.0.0.1:5000/

