# from chatgpt :)

import pytz
from fuzzywuzzy import process  # Importing the process function

# Dictionary mapping cities to their respective timezones
cities_timezones = {
    # MLS Teams
    "Atlanta, Georgia": "America/New_York",
    "Austin, Texas": "America/Chicago",
    "Charlotte, North Carolina": "America/New_York",
    "Chicago, Illinois": "America/Chicago",
    "Cincinnati, Ohio": "America/New_York",
    "Columbus, Ohio": "America/New_York",
    "Dallas, Texas": "America/Chicago",
    "Denver, Colorado": "America/Denver",
    "Houston, Texas": "America/Chicago",
    "Kansas City, Missouri": "America/Chicago",
    "Los Angeles, California": "America/Los_Angeles",
    "Miami, Florida": "America/New_York",
    "Montreal, Quebec": "America/Montreal",
    "Nashville, Tennessee": "America/Chicago",
    "New York City, New York": "America/New_York",
    "Orlando, Florida": "America/New_York",
    "Philadelphia, Pennsylvania": "America/New_York",
    "Portland, Oregon": "America/Los_Angeles",
    "Salt Lake City, Utah": "America/Denver",
    "San Jose, California": "America/Los_Angeles",
    "Seattle, Washington": "America/Los_Angeles",
    "St. Louis, Missouri": "America/Chicago",
    "Toronto, Ontario": "America/Toronto",
    "Vancouver, British Columbia": "America/Vancouver",
    # Updated MLS Teams
    "Commerce City, Colorado": "America/Denver",
    "Carson, California": "America/Los_Angeles",  # Adding Carson for LA Galaxy
    "Chester, Pennsylvania": "America/New_York",  # Adding Chester for Philadelphia Union
}

# Function to get timezone for a given city using fuzzy matching
def get_timezone(city):
    fuzzy_match = process.extractOne(city, cities_timezones.keys())
    if fuzzy_match[1] >= 80:  # Adjust the threshold according to your preference
        return pytz.timezone(cities_timezones[fuzzy_match[0]])
    else:
        return None
