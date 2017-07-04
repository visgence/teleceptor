import json
import requests
import time

SENSOR_URL = "http://localhost:8000/api/sensors"
STREAM_URL = "http://localhost:8000/api/datastreams"
READING_URL = "http://localhost:8000/api/readings"

Range = 24 * 100

if __name__ == "__main__":

    print "\nRunning stream test.\n"
    start = time.time()
    datastreams = requests.get(STREAM_URL).json()
    print "it took {} seconds to retrive {} (all) streams".format(time.time() - start, len(datastreams['datastreams']))
    start = time.time()
    for i in range(1, len(datastreams['datastreams']) + 1):
        requests.get("{}?stream_id={}".format(STREAM_URL, i))
    print "it took {} seconds to retrive each stream seperatly.".format(time.time() - start)

    print "\nRunning sensor test.\n"
    start = time.time()
    sensors = requests.get(SENSOR_URL).json()
    print "it took {} seconds to retrive {} (all) sensors".format(time.time() - start, len(sensors['sensors']))
    start = time.time()
    for i in sensors['sensors']:
        requests.get("{}?sensor_id={}".format(SENSOR_URL, i['uuid']))
    print "it took {} seconds to retrive each stream seperatly.".format(time.time() - start)

    print "Readings test."

    url = "{}?datastream={}&start={}&end={}".format(READING_URL, 1, int(time.time() - Range*3600 - 20), int(time.time()))
    print url
    start = time.time()
    response = requests.get(url).json()
    print "it took {} seconds to retrive {} readings.".format(time.time() - start, len(response['readings']))
