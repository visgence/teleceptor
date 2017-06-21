import json
import requests
import time
import math
import uuid
import copy

# Where is the teleceptor api
TELECEPTOR_URL = "http://localhost:8000/api/station"

# Use api
USE_API = True

NUMBER_OF_STREAMS_PER_POST = 1
# How many stream to poll from.
NUMBER_OF_STREAMS = 1

RATE_OF_POST = 60
# For how many days should there be data
TIME_IN_DAYS = 365

startTime = 0
curTime = 0

# Generic reading outline:
# READING[0]['readings'] = [['in1', value, date]]

Stream = {
    "info": {
        "uuid": "blast_mote",
        "name": "blast_mote",
        "description": "blast_mote",
        "out": [],
        "in": []
    },
    "readings": []
}

InSensor = {
    "name": "in1",
    "sensor_type": "float",
    "timestamp": 30000,
    "meta_data": {
        'meta title': 'meta description'
    }
}


if __name__ == "__main__":
    curTime = time.time()
    request = []
    pointCount = 0

    for i in range(0, NUMBER_OF_STREAMS):
        newStream = copy.deepcopy(Stream)
        newStream['info']['uuid'] = str(uuid.uuid4())
        newStream['info']['in'].append(copy.deepcopy(InSensor))
        print i
        newStream['info']['in'][0]['name'] = str(uuid.uuid4())
        for i in range(0, TIME_IN_DAYS):
            for j in range(0, 60*24):
                newDate = curTime - (i*86400) - (j*60)
                newValue = math.sin(0.1 * pointCount) + 3.0
                newStream['readings'].append([newStream['info']['in'][0]['name'], newValue, newDate])
                pointCount += 1
        request.append(newStream)

    print "{} datapoints have been made.".format(pointCount)
    print "Took {} seconds in time to create the request object.".format(time.time() - curTime)
    postTime = time.time()

    requests.post(TELECEPTOR_URL, data=json.dumps(request))

    print "post took {} seconds.".format(time.time() - postTime)
    print "Total running time of program was {} seconds.".format(time.time() - curTime)
