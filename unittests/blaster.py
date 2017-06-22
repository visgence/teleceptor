import json
import requests
import time
import math
import uuid
import copy

# Where is the teleceptor api
TELECEPTOR_URL = "http://localhost:8000/api/station"

# How many stream do you want
NUMBER_OF_STREAMS = 10

# For how many hours should there be data
TIME_IN_HOURS = 24 * 30

# how much time should be put into a single post request (in minutes)
TIME_PER_POST = 24

# In hours
TIME_OF_PERIOD = 24

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
    totalPointCount = 0
    # Create inital object
    newStream = copy.deepcopy(Stream)
    newStream['info']['uuid'] = str(uuid.uuid4())
    lastDate = time.time()
    timeTracker = time.time()
    for i in range(0, NUMBER_OF_STREAMS):
        newStream['info']['in'].append(copy.deepcopy(InSensor))
        newStream['info']['in'][i]['name'] = str(uuid.uuid4())

    print timeTracker
    for i in range(0, TIME_IN_HOURS/TIME_PER_POST):
        newStream['readings'] = []
        request = []
        for k in range(0, TIME_PER_POST*60):
            timeTracker -= 60
            newDate = timeTracker
            # (pi * 1/number of seconds in a period/2 * date) + 3 for offset
            newValue = math.sin(math.pi * (1.0/(TIME_OF_PERIOD/2 * 60 * 60)) * newDate) + 3.0
            for j in range(0, NUMBER_OF_STREAMS):
                newStream['readings'].append([newStream['info']['in'][j]['name'], newValue, newDate])
                totalPointCount += 1
        request.append(newStream)
        requests.post(TELECEPTOR_URL, data=json.dumps(request))

    print "{} datapoints have been made.".format(totalPointCount)
    print "Total running time of program was {} seconds.".format(time.time() - curTime)
