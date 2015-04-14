'''
Parse data from URL and report highest magnitude earthquake
within 100 miles of Interana office in last 7 days

Requirements: Python 3
External Modules: geopy, simplejson
'''

import time
import urllib.request
import simplejson
from geopy.distance import vincenty
from geopy.geocoders import Nominatim
from urllib.error import HTTPError, URLError

def main():
    '''
    Define some constants
    TODO: better way to input data like street address, radius, time-period

    1. Use geopy module to get latitude, longitude of given address
    2. Use urllib module to read geojson data from USGS website
    3. Use simplejson module to convert geojson binary data to python json-object
    4. Sort json-object by magnitude key
    5. Iterate and filter by magnitude-threshold, time period and range
    5. Magnitude-threshold : Update magnitude threshold everytime an earthquake is detected within time and range
                             this improves performance as we can skip all entries below magnitude threshold
    6. Time-period         : Only look at entries that are within time period ie 7 days before NOW
    7. Range               : Use geopy module to filter all earthquake epicenters within 100 mile radius of given address
    '''
    address = "68 Willow Rd, Menlo Park, CA, USA"
    url = 'http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson'
    origin = (37.45, -122.16) # Default address of Interana office in California
    radius = 100 # miles
    period = 7 # days

    if (get_source_location(address)):
        origin = get_source_location(address)
        origin = (origin.latitude, origin.longitude)
    else:
        print("Could not find geo co-ordinates for address = ", address)
        print("Using default geo co-ordinates =", origin)

    jsondata = get_json_data(url)
    get_result(jsondata, origin, radius, period)

def get_source_location(address):
    '''
    Use geopy module to get geolocation from given street address

    :param address: given street address
    :return: geolocation object
    '''
    try:
        geolocator = Nominatim(timeout=10)
        location = geolocator.geocode(address)
    except:
        print("Geocoding Exception")
    else:
        return location

def get_json_data(url):
    '''
    Use urllib to read URL and then use simplejson module to convert to python json-object

    :param url: URL to read
    :return: jsondata: python json object
    '''
    try:
        response = urllib.request.urlopen(url)
    except HTTPError as e:
        print("Cannot full fill request for URL:", url)
        print("Error code: ", e.code)
        exit(1)
    except URLError as e:
        print("URL not reachable :", url)
        print("Reason: ", e.reason)
        exit(1)
    else:
        jsondata = simplejson.loads(response.read())
        return jsondata

def within_range(origin, destination, radius):
    '''
    This method uses geopy module's vincenty algorithm to calculate distance between origin and destination in miles.
    If this distance is less than radius then return True else False

    :param origin: source location of interest
    :param destination: earthquake epicenter location
    :param radius: range of interest
    :return: True or False
    '''
    return True if(vincenty(origin, destination).miles < radius) else False

def within_period(previous_time, period, current_time):
    '''
    Calculate if previous time is within given period from now

    :param previous_time: earthquake occurence time in milliseconds from epoch
    :param period: in days so convert to milliseconds
    :param current_time: current time in milliseconds from epoch
    :return: True or False
    '''
    period = period*24*60*60*1000
    return True if (current_time - previous_time < period) else False

def get_result(jsondata, origin, radius, period):
    '''
    Iterate through magnitude-sorted json data and filter by magnitude threshold, time period and range

    :param jsondata: unsorted json data
    :param origin: source location
    :param radius: range from source location in miles
    :param period: time period in days
    :return: void: Print result
    '''
    current_time = int(round(time.time() * 1000)) # milliseconds from epoch
    mag_threshold = 0
    result = "[ No Earthquakes !!! ]"
    for feature in sorted(jsondata['features'], key=lambda fea: fea['properties']['mag'], reverse=True):
        magnitude = feature['properties']['mag']
        event_time = feature['properties']['time']
        is_not_within_period = not within_period(event_time, period, current_time)

        if(is_not_within_period or magnitude < mag_threshold):
            continue

        longitude = feature['geometry']['coordinates'][0]
        latitude = feature['geometry']['coordinates'][1]
        destination = (latitude,longitude)
        is_within_range = within_range(origin, destination, radius)
        epicenter = feature['properties']['place']
        if(is_within_range):
            result = "\n\t[ Earthquake of Magnitude {0} at {1} ]".format(magnitude, epicenter)
            mag_threshold = magnitude
    print("Highest magnitude earthquake located within {0} miles from {1} in last {2} days:".format(radius, origin, period))
    print(result)

if __name__ == '__main__':
    main()
