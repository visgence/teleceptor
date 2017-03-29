import os
import sys
import IPython
from webtest import TestApp
import time
import json
import logging
import math
from sqlalchemy import create_engine
PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(PATH)
from teleceptor.server import application
from teleceptor.sessionManager import sessionScope
from teleceptor.models import Sensor, Calibration, SensorReading, DataStream
import teleceptor

session = None


def TestStation(app):
    logging.info("Begining tests.")
    TestStationPost(app)
    TestStationGet(app)
    logging.info("Tests complete.")
    ans = raw_input("Would you like to enter the shell with the test data? (y/n) ")
    if ans == 'y':
        IPython.embed()


def TestStationPost(app):
    logging.info("Begining stations test.")
    CreateStations(app)
    logging.info("Stations test complete.")
    logging.info("Begining readings test.")
    AddReadings(app)
    logging.info("Readings test complete.")
    logging.info("Begining new calibration change test.")
    ChangeNewCalibration(app)
    logging.info("Calibration test complete.")
    logging.info("Begining old calibration test.")
    ChangeOldCalibration(app)
    logging.info("Old calibration test complete.")
    logging.info("Begining nothing test.")
    ChangeNothing(app)
    logging.info("Nothing test complete.")
    logging.info("Begining no timestamp test.")
    ChangeNoTimestamp(app)
    logging.info("No timestamp test complete.")
    logging.info("Begining no sensor id test")
    NoSensorId(app)
    logging.info("No sensor id test complete.")
    logging.info("Begining no reading id test.")
    NoReadingId(app)
    logging.info("No reading id test complete.")


def TestStationGet(app):
    return
    logging.info("Begin all sensor test.")
    GetAllSensors(app)
    logging.info("All sensor test complete.")
    logging.info("Begining one sensor test.")
    GetOneSensor(app)
    logging.info("One sensor test complete.")


def CreateStations(app):
    # Should create 10 stations, 10 sensors, default calibration of (1,0)
    # Note: the errors about blacklisted key is to be expected.
    motes = []
    for i in range(0, 10):
        uuid = "station_test_{}".format(i)
        motes.append({
            'info': {
                'uuid': uuid,
                'name': uuid,
                'description': 'test {}'.format(uuid),
                'out': [],
                'in': [{
                    'name': "test_sensor",
                    'sensor_type': "float",
                    'timestamp': time.time(),
                    'meta_data': {}
                }]
            },
            'readings': []
        })
    app.post_json('/api/station', json.loads(json.dumps(motes)))

    sensors = session.query(Sensor)
    for i in range(0, 10):
        pass



def AddReadings(app):
    # Should create 1000 readings for each sensor.
    # Note: the errors about blacklisted key is to be expected.
    motes = []
    for i in range(0, 10):
        uuid = "station_test_{}".format(i)
        motes.append({
            'info': {
                'uuid': uuid,
                'name': uuid,
                'description': 'test {}'.format(uuid),
                'out': [],
                'in': [{
                    'name': "test_sensor",
                    'sensor_type': "float",
                    'timestamp': time.time(),
                    'meta_data': {}
                }]
            },
            'readings': []
        })
        for j in range(0, 100):
            motes[i]['readings'].append(['test_sensor', math.sin(j)*100, time.time()-j*60])
    app.post_json('/api/station', json.loads(json.dumps(motes)))


def ChangeNewCalibration(app):
    # Should update the calibration on one sensor.
    sensor = json.dumps([{
        'info': {
            'uuid': "station_test_0",
            'scale': "({}, {}".format(10, 10),
            'calibration_timestamp': time.time()
        }
    }])
    app.post_json('/api/station', json.loads(sensor))


def ChangeOldCalibration(app):
    # Should NOT update the calibartion on a sensor.
    sensor = json.dumps([{
        'info': {
            'uuid': "station_test_0",
            'scale': "({}, {}".format(100, 100),
            'calibration_timestamp': time.time() - 1000000
        }
    }])
    app.post_json('/api/station', json.loads(sensor))


def ChangeNothing(app):
    # Should do nothing
    sensor = json.dumps([{
        'info': {
            'uuid': "station_test_0",
        }
    }])
    app.post_json('/api/station', json.loads(sensor))


def ChangeNoTimestamp(app):
    # Should NOT update the calibartion on a sensor.
    sensor = json.dumps([{
        'info': {
            'uuid': "station_test_0",
            'scale': "({}, {}".format(100, 100),
        }
    }])
    app.post_json('/api/station', json.loads(sensor))


def NoSensorId(app):
    # Should do nothing.
    # Note: should throw an error about the mote not reporting its uuid
    sensor = json.dumps([{
        'info': {
            'name': "station_test_0",
            'description': 'test station_test_0',
            'out': [],
            'in':[{
                'name': "avg",
                'sensor_type': "float",
                'timestamp': time.time(),
                'meta_data': {}
            }]
        }
    }])
    app.post_json('/api/station', json.loads(sensor))


def NoReadingId(app):
    # Should do nothing.
    sensor = [{
        'info': {},
        'readings': []
    }]
    for j in range(0, 1):
        sensor[0]['readings'].append(['test_reading', math.sin(j)*100, time.time()-j*60])
    app.post_json('/api/station', json.loads(json.dumps(sensor)))


def GetAllSensors(app):
    info = app.get('/api/station').json
    logging.debug("\nAll sensor data:\n")
    logging.debug(json.dumps(info, indent=2))


def GetOneSensor(app):
    info = app.get('/api/station/station_test_0').json
    logging.debug("\nsingle sensor data:\n")
    logging.debug(json.dumps(info, indent=2))


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    app = TestApp(application)

    logging.info("Creating new teleceptor_tests.db file...")
    if not os.path.exists(os.path.dirname(teleceptor.TESTDBFILE)):
        os.makedirs(os.path.dirname(teleceptor.TESTDBFILE))
    open(teleceptor.TESTDBFILE, 'a').close()
    logging.info(teleceptor.TESTDBFILE + " created.")
    dbURL = 'sqlite:///' + teleceptor.TESTDBFILE
    db = create_engine(dbURL)

    logging.info("Initializing database tables...")
    teleceptor.models.Base.metadata.create_all(db)
    teleceptor.isTesting = True

    with sessionScope() as newSession:
        session = newSession
        TestStation(app)

    teleceptor.isTesting = False
    logging.info("Removing test db.")
    os.remove(teleceptor.TESTDBFILE)








