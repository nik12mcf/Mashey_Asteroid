from flask import Flask
from flask import request
import requests
import json
import threading
import datetime
import calendar


apiKey = 'FmrG2O4vhIIH0uDdm1blYB13CNhWmoy9QjeKfrjm'


def asteroid_closest_approach_threader(endpoint, i, asteroidClosestApproaches):
    resp = requests.get(url=endpoint)
    data = resp.json()

    for index, earth_object in enumerate(data['near_earth_objects']):
        minCloseApproachData = min(earth_object['close_approach_data'], key=lambda x: x['miss_distance']['kilometers'])

        data['near_earth_objects'][index]['close_approach_data'] = minCloseApproachData

    print("Successfully traversed page: ", i)
    print("Endpoint: ", endpoint)

    asteroidClosestApproaches += data['near_earth_objects']


"""
    Note: Page size is 20 and currently there are around 1400 pages. This means there are around
    28000 asteroids to parse.
"""
def asteroid_closest_approach():
    # http://www.neowsapp.com/rest/v1/neo/browse?page=1&size=20&api_key=FmrG2O4vhIIH0uDdm1blYB13CNhWmoy9QjeKfrjm

    # Use this endpoint to retrieve total number of pages given that the size is 20 for each page
    endpoint = 'https://api.nasa.gov/neo/rest/v1/neo/browse' + '?api_key=' + apiKey
    resp = requests.get(url=endpoint)
    data = resp.json()

    # TESTING PURPOSES #
    """
    endpoint = 'http://www.neowsapp.com/rest/v1/neo/browse?page=' + '98' + '&size=20' + '&api_key' + apiKey
    asteroid_closest_approach_threader(endpoint, 98)
    """

    threads = []
    asteroidClosestApproaches = []
    # Try to iterate over every page provided by the NASA api.
    for i in range(0, 3):
        endpoint = 'http://www.neowsapp.com/rest/v1/neo/browse?page=' + str(i) + '&size=20' + '&api_key=' + apiKey

        res = threading.Thread(target=asteroid_closest_approach_threader, args=(endpoint, i, asteroidClosestApproaches))
        res.start()
        threads.append(res)

    for th in threads:
        th.join()

    # TESTING PURPOSES #
    """
    for asteroid in asteroidClosestApproaches:
        print(asteroid)
    """

    for asteroid in asteroidClosestApproaches:
        print(asteroid)

    return json.dumps(asteroidClosestApproaches)


def add_month(startDate):
    month = startDate.month
    year = startDate.year + month // 12
    month = month % 12 + 1
    day = min(startDate.day, calendar.monthrange(year, month)[1])
    return datetime.datetime(year, month, day)


def month_closest_approaches_threader(endpoint, monthClosestApproaches):
    resp = requests.get(url=endpoint)
    data = resp.json()

    for date in data['near_earth_objects']:
        monthClosestApproaches += data['near_earth_objects'][date]

    print("Finished parsing for endpoint: ", endpoint)


def month_closest_approaches(startDate):
    # Convert to datetime object to allow for arithmetic operations
    startDate = datetime.datetime.strptime(startDate, '%Y-%m-%d')
    # Add one month to the specified startDate
    endDate = add_month(startDate)

    # Allow for threading so that simultaneous requests can be sent to improve runtime
    threads = []
    monthClosestApproaches = []
    while startDate <= endDate:
        nextDate = startDate + datetime.timedelta(days=7)

        if(nextDate > endDate):
            nextDate = endDate

        endpoint = 'https://api.nasa.gov/neo/rest/v1/feed?start_date=' + startDate.strftime('%Y-%m-%d') +'&end_date=' + nextDate.strftime('%Y-%m-%d') + '&api_key=' + apiKey

        # Implementation of threading for simultaneous requests
        res = threading.Thread(target= month_closest_approaches_threader, args=(endpoint, monthClosestApproaches))
        res.start()
        threads.append(res)

        # Add one dat to avoid traversing the same date for closest approaches,
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

    return result


def nearest_misses():
    print("NEAREST MISSES")


if __name__ == '__main__':
    # asteroid_closest_approach()

    # DATE FORMAT YEAR-MONTH-DAY
    # month_closest_approaches('2001-01-03')

    nearest_misses()