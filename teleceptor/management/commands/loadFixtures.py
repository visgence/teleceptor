"""
loadFixtures.py

Adds two sensors and two datastreams
Then adds sensor readings in the form of a sine curve.

"""

import sys
import ulid
import json
from time import time
import math
import requests
import logging
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    # Loads two sensors, two datastreams, and some readings
    def handle(self, *args, **kwargs):

        if settings.DEBUG:
            logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
        else:
            logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

        serverURL = "http://0.0.0.0:8000/api/station"
        jsonExample = [{
            "info": {
                "uuid": "mote123",
                "name": "myfirstmote",
                "description": "My first mote",
                "out": [],
                "in":[{
                    "name": "1N1",
                    "sensor_type": "float",
                    "timestamp": 30000,
                    "meta_data": {
                        'meta title': 'meta description'
                    }
                }, {
                    "name": "1N2",
                    "sensor_type": "float",
                    "timestamp": 30000,
                    "meta_data": {
                        'meta title': 'meta description'
                    }
                }]
            },
            "readings": [
                ["1N1", 99, time()],
                ["1N1", 129, time() - 20],
                ["1N1", 29, time() - 40],
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
            jsonExample[0]["readings"].append(["1N1", 400 * math.sin(0.1 * counter), now])
            jsonExample[0]["readings"].append(["1N2", 600 * math.sin(0.1 * counter), now])
            now -= 10
            counter += 1

        logging.debug("Sending post")
        response = requests.post(serverURL, data=json.dumps(jsonExample))
        logging.debug("Response:")
        logging.debug(response)

