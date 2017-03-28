import os
import sys
import IPython
from webtest import TestApp
import time
import json
import logging
PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(PATH)
from teleceptor.server import application


def TestSensor(app):
    logging.debug("Begin sensor tests.")
    TestSensorPost(app)
    TestSensorGet(app)
    logging.debug("Sensor tests completed.")
    ans = input("Would you like to enter the shell with the test data? (y/n) ")
    if ans == 'y':
        IPython.embed()


def TestSensorPost(app):
    logging.debug("Begin add sensor test.")
    AddSensor(app)
    logging.debug("Add sensor test complete.")
    logging.debug("Begin add sensor with calibration test.")
    AddSensorWithCalibration(app)
    logging.debug("Add sensor with calibration test complete.")
    logging.debug("Begin add sensor with no id test.")
    AddSensorNoId(app)
    logging.debug("Add sensor with no id test complete.")
    logging.debug("Begin update new calibration test.")
    UpdateNewCalibration(app)
    logging.debug("Update new calibration test complete.")
    logging.debug("Begin update old calibration test.")
    UpdateOldCalibration(app)
    logging.debug("Update old calibration test complete.")
    logging.debug("Begin update no timestamp test.")
    UpdateNoTimeStamp(app)
    logging.debug("Update no timestamp test complete.")


def TestSensorGet(app):
    logging.debug("Begin get sensor test.")
    GetSensor(app)
    logging.debug("Get sensor test complete.")
    logging.debug("Begin get all sensors test.")
    GetAllSensors(app)
    logging.debug("Get all sensors test complete.")
    logging.debug("Begin get incorrect sensor test.")
    GetIncorrectSensor(app)
    logging.debug("Get incorrect sensor test complete.")


def AddSensor(app):
    # Creates a bare bones sensor.
    sensor = json.dumps({
        'uuid': "sensor_test_0",
    })
    app.post_json('/api/sensors', json.loads(sensor))


def AddSensorWithCalibration(app):
    # Creates a new sensor with some initial coefficients.
    sensor = json.dumps({
        'uuid': "sensor_test_1",
        'calibration': {
            'timestamp': time.time(),
            'coefficients': "(10,10)"
        }
    })
    app.post_json('/api/sensors', json.loads(sensor))


def AddSensorNoId(app):
    # This should NOT do anything including updating coefficients.
    sensor = json.dumps({
        'name': 'sensor_test_0'
        'calibration': {
            'timestamp': time.time(),
            'coefficients': "(10,10)"
        }
    })
    app.post_json('/api/sensors', json.loads(sensor))


def UpdateNewCalibration(app):
    # Updates a sensors calibration.
    sensor = json.dumps({
        'uuid': "sensor_test_0",
        'calibration': {
            'timestamp': time.time(),
            'coefficients': "(10,10)"
        }
    })
    app.post_json('/api/sensors', json.loads(sensor))


def UpdateOldCalibration(app):
    # This should NOT update any calibrations.
    sensor = json.dumps({
        'uuid': "sensor_test_0",
        'calibration': {
            'timestamp': time.time()-10000,
            'coefficients': "(5,5)"
        }
    })
    app.post_json('/api/sensors', json.loads(sensor))


def UpdateNoTimeStamp(app):
    # This should NOT do anything.
    sensor = json.dumps({
        'uuid': "sensor_test_1",
        'calibration': {
            'coefficients': "(15,15)"
        }
    })
    app.post_json('/api/sensors', json.loads(sensor))


def GetSensor(app):
    info = app.get('/api/sensors/sensor_test_0').json
    logging.debug("\Single sensor data:\n")
    logging.debug(json.dumps(info, indent=2))


def GetAllSensors(app):
    info = app.get('/api/sensors').json
    logging.debug("\nAll sensors data:\n")
    logging.debug(json.dumps(info, indent=2))


def GetIncorrectSensor(app):
    info = app.get('/api/sensors/fictionalSensorId').json
    logging.debug("\nIncorrect sensor data:\n")
    logging.debug(json.dumps(info, indent=2))

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    app = TestApp(application)
    TestSensor(app)
