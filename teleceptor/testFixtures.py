"""
testFixtures.py

Authors: Victor Szczepanski
         Cyrille Gindreau

Adds two sensors and two datastreams
Then adds sensor readings in the form of a sine curve.

"""

import sys
import json
from time import time
import math
import requests


def main():
    """
    Loads two sensors, two datastreams, and some readings

    """
    serverURL = "http://0.0.0.0:8000/api/station"
    jsonExample = [{
        "info": {
            "uuid": "mote1234",
            "name": "myfirstmote",
            "description": "My first mote",
            "out": [],
            "in":[{
                "name": "in1",
                "sensor_type": "float",
                "timestamp": 30000,
                "meta_data": {
                    'meta title': 'meta description'
                }
            }, {
                "name": "in2",
                "sensor_type": "float",
                "timestamp": 30000,
                "meta_data": {
                    'meta title': 'meta description'
                }
            }]
        },
        "readings": [
            ["in1", 99, time()],
            ["in1", 129, time() - 20],
            ["in1", 29, time() - 40],
        ]
    }]
    timeRanges = {
        '2hour': 7200,
        "day": 86400,
        "week": 604800,
        "month": 18144000
    }

    defaultRange = timeRanges['2hour']
    now = time()
    lastWeek = now - defaultRange
    if range is not None and range in timeRanges:
        lastWeek = now - timeRanges[range]

    counter = 0
    while now >= lastWeek:
        jsonExample[0]["readings"].append(["in1", 400 * math.sin(0.1 * counter), now])
        jsonExample[0]["readings"].append(["in2", 600 * math.sin(0.1 * counter), now])
        now -= 60
        counter += 1

    requests.post(serverURL, data=json.dumps(jsonExample))


if __name__ == "__main__":
    cmds = {
        "loadreadings": loadReadings
    }

    args = sys.argv
    if (len(args) > 2 and args[1] in cmds):
        interval = None if len(args) <= 3 else int(args[3])
        with sessionScope() as s:
            cmds[args[1]](s, args[2], interval)
    else:
        main()
