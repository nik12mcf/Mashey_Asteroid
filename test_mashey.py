import pytest
import main
import json
import vcr

def test_closest_asteroids():
    asteroids = json.loads(main.asteroid_closest_approach())

    # Determined through manual calculations for certain asteroid ids.
    asteroidKilometerApproachDict = {'2000433': '22359243.131520978'}

    #  Corroborate that manually calculated asteroid miss distances are equal to scraped asteroid miss distances
    for asteroid in asteroids:
        if asteroid['id'] in asteroidKilometerApproachDict:
            scrapedMissDistance = float(asteroid['close_approach_data']['miss_distance']['kilometers'])
            correctMissDistance = float(asteroidKilometerApproachDict[asteroid['id']])

            assert(scrapedMissDistance == correctMissDistance)

test_closest_asteroids()