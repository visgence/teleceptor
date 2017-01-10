"""
testFixtures.py

Authors: Victor Szczepanski
         Cyrille Gindreau

Adds two sensors and two datastreams and their calibration
Then adds some randomly generated sensor readings.

"""

from sessionManager import sessionScope
from models import *
import sys
import random
import json
from time import time
from teleceptor.models import MessageQueue, Sensor
from teleceptor import USE_ELASTICSEARCH
import math
import requests
if USE_ELASTICSEARCH:
    import elasticsearchUtils


def loadAdmin(session):
    kwargs = {
        "email": "admin@visgence.com",
        "firstname": "Admin",
        "lastname": "Developer",
        "active": True,
        "password": "password"
    }
    admin = User(**kwargs)
    session.add(admin)


# def loadScalingFunctions(session):
#     kwargs = {
#         "name": "Identity"
#         ,"definition": "return x;"
#     }

#     sf = ScalingFunction(**kwargs)
#     session.add(sf)

def loadSensors(session):
    sensor1 = {
        "uuid": "volts",
        "name": "Volts Sensor",
        "units": "V",
        "model": "003-SP1001",
        "description": "Volts of shivaplug",
        "last_calibration_id": 1,
        "meta_data": {
            "metafield": 5,
            "metalist": ["one", "two", "three"],
            "metadict": {
                "hue": "fue",
                "boo": "foo"
            }
        }
    }

    sensor2 = {
        "uuid": "amps",
        "name": "Amperes Sensor",
        "units": "A",
        "model": "003-SP1001",
        "description": "Amperes of shivaplug",
        "last_calibration_id": 2
    }

    sensors = [Sensor(**sensor1), Sensor(**sensor2)]
    for sensor in sensors:
        print "Adding sensor %s to db" % str(sensor.toDict())
        sensor.message_queue = MessageQueue(sensor_id=sensor.uuid)
    session.add_all(sensors)


def loadCalibrations(session):
    calibration1 = {
        "sensor_id": "volts",
        "coefficients": "[0.128755, -65.794]",
        "timestamp": time()
    }

    calibration2 = {
        "sensor_id": "amps",
        "coefficients": "[0.048828, -25.0]",
        "timestamp": time()
    }

    cals = [Calibration(**calibration1), Calibration(**calibration2)]
    session.add_all(cals)


def loadDatastreams(session):
    datastream1 = {
        "sensor": "volts",
        "owner": 1,
        # ,"scaling_function": "Identity"
    }

    datastream2 = {
        "sensor": "amps",
        "owner": 1,
        # ,"scaling_function": "Identity"
    }

    streams = [DataStream(**datastream1), DataStream(**datastream2)]
    session.add_all(streams)


def loadPaths(session):
    path1 = {
        'datastream': 1,
        'path': 'myPath'
    }
    path2 = {
        'datastream': 2,
        'path': 'myOtherPath'
    }
    paths = [StreamPath(**path1), StreamPath(**path2)]
    session.add_all(paths)


def loadReadings(session, range=None, interval=None):
    timeRanges = {
        '2hour': 7200,
        "day":  86400,
        "week": 604800
    }

    defaultRange = timeRanges['week']
    now = time()
    lastWeek = now - defaultRange
    if range is not None and range in timeRanges:
        lastWeek = now - timeRanges[range]

    interval = interval if interval is not None else 43200

    readings = []
    counter = 0
    while now >= lastWeek:
        voltReading = {
            "datastream": 1,
            "sensor": "volts",
            "value": int(600 * math.sin(0.1*counter)),
            "timestamp": now
        }

        ampReading = {
            "datastream": 2,
            "sensor": "amps",
            "value": int(400 * math.sin(0.1*counter)),
            "timestamp": now
        }
        counter += 1
        now -= 60

        if USE_ELASTICSEARCH:
            elasticsearchUtils.insertReading('1', voltReading['value'], voltReading['timestamp'])
            elasticsearchUtils.insertReading('2', ampReading['value'], ampReading['timestamp'])

        volt = SensorReading(**voltReading)
        amp = SensorReading(**ampReading)
        readings.append(volt)
        readings.append(amp)

    session.add_all(readings)


def loadviaapi():
    serverURL = "http://192.168.99.100:8000/api/station"
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
                "meta_data": {}
            }]
        },
        "readings": [
            ["in1", 99, time()],
            ["in1", 129, time()-20],
            ["in1", 29, time()-40],
        ]
    }]
    timeRanges = {
        '2hour': 7200,
        "day":  86400,
        "week": 604800
    }

    defaultRange = timeRanges['week']
    now = time()
    lastWeek = now - defaultRange
    if range is not None and range in timeRanges:
        lastWeek = now - timeRanges[range]

    counter = 0
    while now >= lastWeek:
        jsonExample[0]["readings"].append(["in1", 400 * math.sin(0.1*counter), now])
        now -= 60
        counter += 1

    requests.post(serverURL, data=json.dumps(jsonExample))


def main():
    loadviaapi()
    return
    """
    Loads two sensors, two datastreams, and some readings

    .. todo:: admin is currently unused
    .. todo:: loadScalingFunctions is unused

    .. note:: After loadSensors and after loadDatastream there is a query and a loop printing the newly added data
        For some reason, this function will not work without them. My guess is that the database needs time to submit
        the new results before it can start attaching foreign key relationships.

    """
    with sessionScope() as s:
        loadAdmin(s)
        loadCalibrations(s)
        loadSensors(s)

        myObj = s.query(Sensor)
        for i in myObj:
            print i.toDict()

        loadDatastreams(s)

        myObj = s.query(DataStream)
        for i in myObj:
            print i.toDict()

        loadReadings(s)
        # loadPaths(s)
        # loadScalingFunctions(s)


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
