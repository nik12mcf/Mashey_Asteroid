from flask import Flask
from flask import request
import requests
import json
import threading
import datetime
import calendar
import vcr


apiKey = 'FmrG2O4vhIIH0uDdm1blYB13CNhWmoy9QjeKfrjm'


"""
    Helper function for asteroid_closest_approach. Was initially modified for multithreading but later
    converted back for sequential execution. Finds the minimum miss distance for each asteroid by parsing
    the close approach data. Once the minimum miss distance data is found, all other entries all removed
    from the close approach data. The problem statement highlights this:
    
        The close_approach_data field is a list of all approaches for a given asteroid, but only the closest 
        approach should be returned.
        
    Note: one asteroid had no close approach data and returned an empty list. 
"""
def asteroid_closest_approach_threader(endpoint):
    # Sending request to the NASA api
    resp = requests.get(url=endpoint)
    data = resp.json()

    for index, earth_object in enumerate(data['near_earth_objects']):
        if len(earth_object['close_approach_data']) != 0:
            # At one point, an asteroid with no close approach data was encountered
            # id: 2162038 and name: 162038 (1996 DH) is the exception
            minCloseApproachData = min(earth_object['close_approach_data'], key=lambda x: x['miss_distance']['kilometers'])

            # Remove all other close approach data except for the calculated all time closest approach.
            data['near_earth_objects'][index]['close_approach_data'] = minCloseApproachData

    print("Successfully traversed endpoint: ", endpoint)

    return data['near_earth_objects']


"""
    Note: Page size is 20 and currently there are around 1400 pages. This means there are around
    28000 asteroids to parse. Initially tried mulithreadeing but ran into an api limit. Therefore, it was
    easier to record the Asteroid API responses on cassettes in order to avoid hitting the API 
    rate limit. While the first run is very slow since it is sequential, all subsequent runs are much faster.
    This cascades down to other functions definitions that make use of this current function call.
"""
@vcr.use_cassette('fixtures/vcr_cassettes/asteroids_closest_approach.yaml')
def asteroid_closest_approach():
    # Use this endpoint to retrieve total number of pages given that the size is 20 for each page.
    endpoint = 'https://api.nasa.gov/neo/rest/v1/neo/browse' + '?api_key=' + apiKey
    # Send initial request to NASA api.
    resp = requests.get(url=endpoint)
    data = resp.json()

    # List of all asteroids with only closest approach data.
    asteroidClosestApproaches = []
    totalPages = int(data['page']['total_pages'])
    # Try to iterate over every page provided by the NASA api. Begins at index 0 and ends at index total_pages - 1.
    # However, on the NASA api, index 0 corresponds to page 1 and index 1 to page 2, and so forth.
    for i in range(33, totalPages):
        endpoint = 'http://www.neowsapp.com/rest/v1/neo/browse?page=' + str(i) + '&size=20' + '&api_key=' + apiKey

        asteroidClosestApproaches += asteroid_closest_approach_threader(endpoint)

    # TESTING PURPOSES #
    """
    for asteroid in asteroidClosestApproaches:
        print(asteroid)
    """
    # Return asteroid closest approach data in form of json object
    return json.dumps(asteroidClosestApproaches)


"""
    Helper function to extrapolate one calendar month from the start date input.
    This returns a datetime object.
"""
def add_month(startDate):
    month = startDate.month
    year = startDate.year + month // 12
    month = month % 12 + 1
    day = min(startDate.day, calendar.monthrange(year, month)[1])
    return datetime.datetime(year, month, day)


"""
    Helper function for month_closest_approaches to allow for multithreading.
"""
def month_closest_approaches_threader(endpoint, monthClosestApproaches):
    resp = requests.get(url=endpoint)
    data = resp.json()

    for date in data['near_earth_objects']:
        monthClosestApproaches += data['near_earth_objects'][date]

    print("Finished parsing for endpoint: ", endpoint)


"""
    Return the closest asteroid approaches for the calendar month. Calendar month was determined
    via merriam websters definition:
        1: one of the months as named in the calendar
        2: the period from a day of one month to the corresponding day of the next month if such 
        exists or if not to the last day of the next month (as from January 3 to February 3 or from 
        January 31 to February 29).
    Correctly adjust the requests to not have overlapping dates when submitting request to NASA's
    api. 
    NOTE: Make use of multithreading to allow for parallel execution and faster runtime.
"""
def month_closest_approaches(startDate):
    # Convert to datetime object to allow for arithmetic operations
    startDate = datetime.datetime.strptime(startDate, '%Y-%m-%d')
    # Add one month to the specified startDate
    endDate = add_month(startDate)

    # Allow for threading so that simultaneous requests can be sent to improve runtime
    threads = []
    monthClosestApproaches = []
    while startDate <= endDate:
        # Can only request one week worth of information from the NASA api.
        nextDate = startDate + datetime.timedelta(days=7)

        if(nextDate > endDate):
            nextDate = endDate

        # Correct formatting for endpoints using start and end dates.
        endpoint = 'https://api.nasa.gov/neo/rest/v1/feed?start_date=' + startDate.strftime('%Y-%m-%d') + '&end_date=' + nextDate.strftime('%Y-%m-%d') + '&api_key=' + apiKey

        # Implementation of threading for simultaneous requests
        res = threading.Thread(target=month_closest_approaches_threader, args=(endpoint, monthClosestApproaches))
        res.start()
        threads.append(res)

        # Add one day to avoid traversing the same date for closest approaches;
        # overlap occurs between current endDate and the next startDate.
        startDate = nextDate + datetime.timedelta(days=1)

    for th in threads:
        th.join()

    # Format for correct JSON output
    result = {'element_count': len(monthClosestApproaches), 'near_monthly_approaches': monthClosestApproaches}

    # TESTING #
    """
    for asteroid in result['near_monthly_approaches']:
        print(asteroid)
    """

    # Return result as json data
    return json.dumps(result)


"""
    Return the 10 nearest misses, historical or in the future, for asteroids. Uses previously implemented
    function asteroid closes approaches in order to get all closest approaches of asteroids. Then sorts
    all asteroids by nearest miss and returns the first 10 entries.
"""
def nearest_misses():
    closest_approaches = json.loads(asteroid_closest_approach())

    sorted_closest_approaches = sorted(closest_approaches, key=lambda i: i['close_approach_data']['miss_distance']['kilometers'])

    for asteroid in sorted_closest_approaches[:10]:
        print(asteroid)


if __name__ == '__main__':
    asteroid_closest_approach()

    # DATE FORMAT YEAR-MONTH-DAY
    # month_closest_approaches('2001-01-03')

    # nearest_misses()
