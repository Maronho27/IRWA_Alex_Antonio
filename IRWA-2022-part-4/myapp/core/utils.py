import csv
import datetime
import json
from random import random
from flask import request
import requests

from faker import Faker

fake = Faker()


# fake.date_between(start_date='today', end_date='+30d')
# fake.date_time_between(start_date='-30d', end_date='now')
#
# # Or if you need a more specific date boundaries, provide the start
# # and end dates explicitly.
# start_date = datetime.date(year=2015, month=1, day=1)
# fake.date_between(start_date=start_date, end_date='+30y')

#def get_random_date():
#    """Generate a random datetime between `start` and `end`"""
#    return fake.date_time_between(start_date='-30d', end_date='now')


#def get_random_date_in(start, end):
#    """Generate a random datetime between `start` and `end`"""
#    return start + datetime.timedelta(
#        # Get a random amount of seconds between `start` and `end`
#        seconds=random.randint(0, int((end - start).total_seconds())), )

def user_information():
    """
    Collect user information such as the IP address, the city, the region and the country

    Returns:
    location: a dictionary containing the IP address, the city, the region and the country of the user
    """

    ip_address = request.remote_addr # collect the ip_addr

    # collect the city, country and region
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name")
    }
    return location_data


def load_json_file(path):
    """Load JSON content from file in 'path'

    Parameters:
    path (string): the file path

    Returns:
    json_data: an array containing the tweets
    """

    # Load the file into a unique string
    json_data = []
    # open the JSON file
    with open(path) as fp:
        for jsonObj in fp:
            tweetsDict = json.loads(jsonObj)
            json_data.append(tweetsDict) # add the tweets in our array tweets
    return json_data

def load_name_docs(path):
    """Load CSV content from file in 'path'

    Parameters:
    path (string): the file path

    Returns:
    doc_id: a dictionary containing the name associated to each tweet id
    """

    doc_id = {}
    # open the CSV file
    with open(path, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar=' ')
        for row in spamreader:
            doc_id[row[0].split()[1]] = row[0].split()[0] # add the doc number as an entry of our dictionary, having the tweet id as the key of this entry
    return doc_id