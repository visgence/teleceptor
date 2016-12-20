"""

Authors: Victor Szczepanski

"""

from sessionManager import sessionScope
from models import *
import sys
import random
from time import time
from teleceptor.models import MessageQueue, Sensor
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
        "owner": 1
        # ,"scaling_function": "Identity"
    }

    datastream2 = {
        "sensor": "amps",
        "owner": 1
        # ,"scaling_function": "Identity"
    }

    streams = [DataStream(**datastream1), DataStream(**datastream2)]
    session.add_all(streams)


def loadReadings(session, range=None, interval=None):
    timeRanges = {
        '2hour': 7200,
        "day":  86400,
        "week": 604800
    }

    defaultRange = timeRanges['2hour']
    now = time()
    lastWeek = now - defaultRange
    if range is not None and range in timeRanges:
        lastWeek = now - timeRanges[range]

    interval = interval if interval is not None else 43200

    readings = []
    while now >= lastWeek:
        voltReading = {
            "datastream": 1,
            "sensor": "volts",
            "value": random.randint(550, 600),
            "timestamp": now
        }

        ampReading = {
            "datastream": 2,
            "sensor": "amps",
            "value": random.randint(550, 600),
            "timestamp": now
        }

        now -= 60

        elasticsearchUtils.insertReading('1', voltReading['value'], voltReading['timestamp'])
        elasticsearchUtils.insertReading('2', ampReading['value'], ampReading['timestamp'])

        volt = SensorReading(**voltReading)
        amp = SensorReading(**ampReading)
        readings.append(volt)
        readings.append(amp)

    session.add_all(readings)


def main():
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
