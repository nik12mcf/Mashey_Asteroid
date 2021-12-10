import main
import json


def test_closest_asteroid_approach():
    asteroids = json.loads(main.asteroid_closest_approach())

    # Determined closest miss in kilometers through manual calculations for certain asteroid ids.
    asteroidKilometerApproachDict = {'2000433': '22359243.131520978'}

    #  Corroborate that manually calculated asteroid miss distances are equal to scraped asteroid miss distances
    for asteroid in asteroids:
        if asteroid['id'] in asteroidKilometerApproachDict:
            scrapedMissDistance = float(asteroid['close_approach_data']['miss_distance']['kilometers'])
            correctMissDistance = float(asteroidKilometerApproachDict[asteroid['id']])

            assert(scrapedMissDistance == correctMissDistance)


"""
    Test the month closest approaches function
"""
def test_month_closest_approaches():
    """
        First test from Jan 3 to Feb 3. Uses manually generated data stored in the form
        of dictionaries to cross examine scraped data.
    """
    response = json.loads(main.month_closest_approaches('2001-01-03'))

    # Dictionary with ID as key and Date as value
    asteroidDict_ID_Date = {'2086450': '2001-01-11', '2162854': '2001-01-11'}
    # Dictionary with ID as key and Miss Distance (km) as value
    asteroidDict_ID_Dist = {'2086450': '29895911.596269342', '2162854': '32448956.549979647'}

    for asteroid in response['near_monthly_approaches']:
        # Check 0 index only since close_approach data will only have on entry
        if asteroid['id'] in asteroidDict_ID_Date:
            assert asteroid['close_approach_data'][0]['close_approach_date'] == asteroidDict_ID_Date[asteroid['id']]
        if asteroid['id'] in asteroidDict_ID_Dist:
            assert asteroid['close_approach_data'][0]['miss_distance']['kilometers'] == asteroidDict_ID_Dist[asteroid['id']]


"""
    Used the https://cneos.jpl.nasa.gov/ca/ to find the all time nearest misses for asteroids.
    Then used that database to corroborate scraped data from program.
"""
def test_nearest_misses():
    #asteroids = json.loads(main.nearest_misses())

    #with open('testing_data/nearest_misses.txt', 'w') as outfile:
    #    json.dump(asteroids, outfile)

    asteroids = json.load(open('testing_data/nearest_misses.txt'))

    # Ordered top ten nearest misses tuple with id and miss distance in kilometers
    asteroidDict_ID_Dist = [('54087809', '6745.532515957'),
                              ('54051131', '9316.925424026'),
                              ('54212443', '9426.685381245'),
                              ('3556206', '11851.666853945'),
                              ('3892165', '12613.434167772'),
                              ('3430497', '12638.162695683'),
                              ('3249978', '12913.13854053'),
                              ('54000953', '13104.32461839'),
                              ('54016959', '13403.654996473'),
                              ('3831871', '13672.003655679')]

    asteroidDict_ID_Date = {'54087809': '2020-11-13',
                            '54051131': '2020-08-16',
                            '54212443': '2021-10-25',
                            '3556206': '2011-02-04',
                            '3892165': '2019-10-31',
                            '3430497': '2008-10-09',
                            '3249978': '2004-03-31',
                            '54000953': '2019-04-04',
                            '54016959': '2020-05-04',
                            '3831871': '2018-10-19'}

    # Cross examine scraped top ten nearest misses with manually determined top ten nearest misses.
    for index in range(10):
        # Check asteroid ID matches
        assert(asteroidDict_ID_Dist[index][0] == asteroids[index]['id'])
        # Check asteroid distance matches
        assert(asteroidDict_ID_Dist[index][1] == asteroids[index]['close_approach_data']['miss_distance']['kilometers'])
        # Check asteroid closest approach date matches
        assert(asteroidDict_ID_Date[asteroids[index]['id']] == asteroids[index]['close_approach_data']['close_approach_date'])


    print("SUCCESS")


    #for index,

    #for index, asteroid in enumerate(asteroids):


#test_closest_asteroid_approach()

test_nearest_misses()

#test_month_closest_approaches()
