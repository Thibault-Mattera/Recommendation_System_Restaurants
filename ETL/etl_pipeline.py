from extract import extract_data
from transform import transform_data
from load import load_data


if __name__ == '__main__':
    
    input_url=input("""Enter restaurant search url from TripAdvisor to launch pipeline.
    Examples:
        https://www.tripadvisor.com/Restaurants-g188113-Zurich.html
        https://www.tripadvisor.com/Restaurants-g188057-Geneva.html
    """)
    
    if input_url.startswith('https://www.tripadvisor.com/')==False:
        raise Exception("Please enter a valid url") 
    else:
        search_url=input_url
        restaurants_extracted=extract_data(search_url)
        transform_data(restaurants_extracted)
        load_data()