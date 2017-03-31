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


# ==========================================================SENSOR TESTS============================================ #


def TestSensor(app):
    logging.debug("Begin sensor tests.")
    failures = TestSensorPost(app)
    failures = failures + TestSensorGet(app)
    logging.debug("Sensor tests completed.")
    return failures


def TestSensorPost(app):
    logging.debug("Begin add sensor test.")
    failures = AddSensor(app)
    logging.debug("Add sensor test complete.")
    logging.debug("Begin add sensor with calibration test.")
    failures = failures + AddSensorWithCalibration(app)
    logging.debug("Add sensor with calibration test complete.")
    logging.debug("Begin add sensor with no id test.")
    failures = failures + AddSensorNoId(app)
    logging.debug("Add sensor with no id test complete.")
    logging.debug("Begin update new calibration test.")
    failures = failures + UpdateNewCalibration(app)
    logging.debug("Update new calibration test complete.")
    logging.debug("Begin update old calibration test.")
    failures = failures + UpdateOldCalibration(app)
    logging.debug("Update old calibration test complete.")
    logging.debug("Begin update no timestamp test.")
    return failures


def TestSensorGet(app):
    logging.debug("Begin get sensor test.")
    failures = GetSensor(app)
    logging.debug("Get sensor test complete.")
    logging.debug("Begin get all sensors test.")
    failures = failures + GetAllSensors(app)
    logging.debug("Get all sensors test complete.")
    logging.debug("Begin get incorrect sensor test.")
    failures = failures + GetIncorrectSensor(app)
    logging.debug("Get incorrect sensor test complete.")
    return failures


def AddSensor(app):
    # Creates a bare bones sensor.
    sensor = json.dumps({
        'uuid': "sensor_test_0",
    })

    failures = doSensorPost(sensor)

    test = session.query(Sensor).filter_by(uuid='sensor_test_0').first()
    if test is None:
        failures.append({
            'TestName': "AddSensor",
            'ErrorGiven': "query was None"
        })

    return failures


def AddSensorWithCalibration(app):
    # Creates a new sensor with some initial coefficients.
    sensor = json.dumps({
        'uuid': "sensor_test_1",
        'calibration': {
            'timestamp': time.time(),
            'coefficients': "[10,10]"
        }
    })

    failures = doSensorPost(sensor)

    test = session.query(Sensor).filter_by(uuid='sensor_test_1').first()
    if test is None:
        failures.append({
            'TestName': "AddSensor",
            'ErrorGiven': "query was None."
        })
    elif test.toDict()['last_calibration']['coefficients'] != "[10, 10]":
        failures.append({
            'TestName': "AddSensor",
            'ErrorGiven': "coefficients wern't recorded properly."
        })

    return failures


def AddSensorNoId(app):
    # This should NOT do anything including updating coefficients.
    sensor = json.dumps({
        'name': 'sensor_test_0',
        'calibration': {
            'timestamp': time.time(),
            'coefficients': "(5, 5)"
        }
    })

    failures = doSensorPost(sensor)

    test = session.query(Sensor).filter_by(uuid='sensor_test_0').first()
    if test is None:
        failures.append({
            'TestName': "AddSensorNoId",
            'ErrorGiven': "Sensor doesn't exit when it should from test #1"
        })
    elif test.toDict()['last_calibration']['coefficients'] == "[5, 5]":
        failures.append({
            'TestName': "AddSensorNoId",
            'ErrorGiven': "coefficients were overwritten when they shouldn't have been."
        })

    return failures


def UpdateNewCalibration(app):
    # Updates a sensors calibration.
    sensor = json.dumps({
        'uuid': "sensor_test_0",
        'calibration': {
            'timestamp': time.time(),
            'coefficients': "(7,7)"
        }
    })

    failures = doSensorPost(sensor)

    test = session.query(Sensor).filter_by(uuid='sensor_test_0').first()
    if test is None:
        failures.append({
            'TestName': "UpdateNewCalibration",
            'ErrorGiven': "Sensor doesn't exit when it should from test #1"
        })
    elif test.toDict()['last_calibration']['coefficients'] != "[7, 7]":
        failures.append({
            'TestName': "UpdateNewCalibration",
            'ErrorGiven': "coefficients wern't overwritten when they should have been."
        })

    return failures


def UpdateOldCalibration(app):
    # This should NOT update any calibrations.
    sensor = json.dumps({
        'uuid': "sensor_test_0",
        'calibration': {
            'timestamp': time.time()-10000,
            'coefficients': "(3,3)"
        }
    })

    failures = doSensorPost(sensor)

    test = session.query(Sensor).filter_by(uuid='sensor_test_0').first()
    if test is None:
        failures.append({
            'TestName': "UpdateOldCalibration",
            'ErrorGiven': "Sensor doesn't exit when it should from test #1"
        })
    elif test.toDict()['last_calibration']['coefficients'] == "[3, 3]":
        failures.append({
            'TestName': "UpdateOldCalibration",
            'ErrorGiven': "coefficients were overwritten when they shouldn't have been."
        })

    return failures


def GetSensor(app):
    # This should return sensor.
    try:
        info = app.get('/api/sensors/sensor_test_0').json
    except Exception, e:
        failures = [{
            'TestName': "GetSensor",
            'ErrorGiven': e
        }]

    test = session.query(Sensor).filter_by(uuid='sensor_test_0').first()

    if test is None:
        failures.append({
            'TestName': "GetSensor",
            'ErrorGiven': "Sensor doesn't exit when it should from test #1"
        })
    elif test.ToDict()['uuid'] != info['uuid']:
        failures.append({
            'TestName': "GetSensor",
            'ErrorGiven': "database query doesn't match get request."
        })

    return failures


def GetAllSensors(app):
    # This should return all of the sensors.
    failures = []
    try:
        info = app.get('/api/sensors').json
    except Exception, e:
        failures = [{
            'TestName': "GetAllSensors",
            'ErrorGiven': e
        }]

    test = session.query(Sensor).all()

    for i in info:
        found = False
        for j in test:
            if i['uuid'] == j.toDict()['uuid']:
                found = True
        if not found:
            failures = [{
                'TestName': "GetAllSensors",
                'ErrorGiven': "Sensor not found: {}".format(i)
            }]
    return failures


def GetIncorrectSensor(app):
    # This should not return anything and throw an error.
    failures = []
    try:
        info = app.get('/api/sensors/fictionalSensorId').json
    except Exception, e:
        failures = [{
            'TestName': "GetIncorrectSensor",
            'ErrorGiven': e
        }]

    return failures


def doSensorPost(data):
    # Does a post to app api, returns an error object if failed, an empty array if successful.
    failures = []
    try:
        app.post_json('/api/sensors', json.loads(data))
        return []
    except Exception, e:
        return [{
            'TestName': "doSensorPost: {}".format(data),
            'ErrorGiven': "dosomething"
        }]


# ==========================================================STATION TESTS============================================ #


def TestStation(app):
    logging.info("Begining station tests.")
    failures = TestStationPost(app)
    logging.info("Tests complete.")
    return failures


def TestStationPost(app):
    failures = []
    logging.info("Begining stations test.")
    failures = failures + CreateStations(app)
    logging.info("Stations test complete.")
    logging.info("Begining readings test.")
    failures = failures + AddReadings(app)
    logging.info("Readings test complete.")
    logging.info("Begining new calibration change test.")
    failures = failures + ChangeNewCalibration(app)
    logging.info("Calibration test complete.")
    logging.info("Begining old calibration test.")
    failures = failures + ChangeOldCalibration(app)
    logging.info("Old calibration test complete.")
    logging.info("Begining nothing test.")
    failures = failures + ChangeNothing(app)
    logging.info("Nothing test complete.")
    logging.info("Begining no timestamp test.")
    failures = failures + ChangeNoTimestamp(app)
    logging.info("No timestamp test complete.")
    logging.info("Begining no sensor id test")
    failures = failures + NoSensorId(app)
    logging.info("No sensor id test complete.")
    logging.info("Begining no reading id test.")
    failures = failures + NoReadingId(app)
    logging.info("No reading id test complete.")
    return failures


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

    failures = doStationPost(json.dumps(motes))

    for i in range(0, 10):
        try:
            test = session.query(Sensor).filter_by(uuid=motes[i]['info']['uuid']+'test_sensor').first()
            if test is None:
                failures.append({
                    'TestName': "CreateStations",
                    'ErrorGiven': "Query returned a None type"
                    })
        except Exception, e:
            failures.append({
                'TestName': "CreateStations",
                'ErrorGiven': e
                })
    return failures


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

    failures = doStationPost(json.dumps(motes))

    for i in range(0, 10):
        try:
            sensor = session.query(Sensor).filter_by(uuid=motes[i]['info']['uuid']+'test_sensor').first()
        except Exception, e:
            failures.append({
                'TestName': "AddReadings",
                'ErrorGiven': e
                })
        try:
            stream = session.query(DataStream).filter_by(sensor=sensor.toDict()['uuid']).first()
        except Exception, e:
            failures.append({
                'TestName': "AddReadings",
                'ErrorGiven': e
                })
        try:
            readings = session.query(SensorReading).filter_by(datastream=stream.toDict()['id']).all()
        except Exception, e:
            failures.append({
                'TestName': "AddReadings",
                'ErrorGiven': e
                })
            return failures

        if len(readings) != 100:
            failures.append({
                'TestName': "AddReadings",
                'ErrorGiven': "Incorrect number of readings returned, got: {}".format(len(readings))
                })
    return failures


def ChangeNewCalibration(app):
    # Should update the calibration on one sensor.
    sensor = json.dumps([{
        'info': {
            'uuid': "station_test_0",
            'in': [{
                'name': "test_sensor",
                'sensor_type': "float",
                'timestamp': time.time(),
                'scale': "[{}, {}]".format(10, 10),
                'calibration_timestamp': time.time(),
                'meta_data': {}
            }]
        },
        'readings': []
    }])

    failures = doStationPost(sensor)

    try:
        test = session.query(Sensor).filter_by(uuid='station_test_0test_sensor').first()
        if test.toDict()['last_calibration']['coefficients'] != "[10, 10]":
            failures.append({
                'TestName': "ChangeNewCalibration",
                'ErrorGiven': "Coefficients have not been updated."
                })
    except Exception, e:
        failures.append({
            'TestName': "ChangeNewCalibration",
            'ErrorGiven': e
            })
    return failures


def ChangeOldCalibration(app):
    # Should NOT update the calibartion on a sensor.
    sensor = json.dumps([{
        'info': {
            'uuid': "station_test_0",
            'in': [{
                'name': "test_sensor",
                'sensor_type': "float",
                'timestamp': time.time(),
                'scale': "[{}, {}]".format(5, 5),
                'calibration_timestamp': time.time()-100000,
                'meta_data': {}
            }]
        },
        'readings': []
    }])

    failures = doStationPost(sensor)

    try:
        test = session.query(Sensor).filter_by(uuid='station_test_0test_sensor').first()
        if str(test.toDict()['last_calibration']['coefficients']) != "[10, 10]":
            failures.append({
                'TestName': "ChangeOldCalibration",
                'ErrorGiven': "Coefficients were changed when they shouldn't have been."
            })
    except Exception, e:
        failures.append({
            'TestName': "ChangeOldCalibration",
            'ErrorGiven': e
        })
    return failures


def ChangeNothing(app):
    # Should do nothing
    sensor = json.dumps([{
        'info': {
            'uuid': "station_test_0",
            'name': "station_test_0",
            'description': "test station_test_0",
            'out': [],
            'in': [{
                'name': "test_sensor",
                'sensor_type': "float",
                'timestamp': time.time(),
                'meta_data': {}
            }]
        },
        'readings': []
        }])

    failures = doStationPost(sensor)

    try:
        test = session.query(Sensor).filter_by(uuid='station_test_0test_sensor').first()
        if str(test.toDict()['last_calibration']['coefficients']) != "[10, 10]":
            failures.append({
                'TestName': "ChangeNothing",
                'ErrorGiven': "Coefficients were changed when they shouldn't have been."
                })
    except Exception, e:
        failures.append({
            'TestName': "ChangeOldCalibration",
            'ErrorGiven': e
        })
    return failures


def ChangeNoTimestamp(app):
    # Should NOT update the calibartion on a sensor.
    sensor = json.dumps([{
        'info': {
            'uuid': "station_test_0",
            'name': "station_test_0",
            'description': "test station_test_0",
            'out': [],
            'in': [{
                'name': "test_sensor",
                'sensor_type': "float",
                'timestamp': time.time(),
                'meta_data': {},
                'scale': "[{}, {}]".format(7, 7),
            }]
        },
        'readings': []
        }])

    failures = doStationPost(sensor)

    try:
        test = session.query(Sensor).filter_by(uuid='station_test_0test_sensor').first()
        if str(test.toDict()['last_calibration']['coefficients']) != "[10, 10]":
            failures.append({
                'TestName': "ChangeNoTimestamp",
                'ErrorGiven': "Coefficients were changed when they shouldn't have been."
                })
    except Exception, e:
        failures.append({
            'TestName': "ChangeOldCalibration",
            'ErrorGiven': e
        })
    return failures


def NoSensorId(app):
    # Should do nothing.
    # Note: should throw an error about the mote not reporting its uuid.
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
        },
        'readings': []
    }])

    return doStationPost(sensor)


def NoReadingId(app):
    # Should do nothing.
    # Note: should throw an error about the sensor not reporting its uuid.
    sensor = [{
        'info': {},
        'readings': []
    }]
    for j in range(0, 1):
        sensor[0]['readings'].append(['test_reading', math.sin(j)*100, time.time()-j*60])

    return doStationPost(json.dumps(sensor))


def doStationPost(data):
    # Does a post to app api, returns an error object if failed, an empty array if successful.
    try:
        app.post_json('/api/station', json.loads(data))
        return []
    except Exception, e:
        return [{
            'TestName': "doStationPost: {}".format(data),
            'ErrorGiven': e
        }]


# ==========================================================MAIN==================================================== #


if __name__ == '__main__':
    logging.basicConfig(format='', level=logging.INFO)

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

    failures = []
    with sessionScope() as newSession:
        session = newSession
        # failures = failures + TestStation(app)
        failures = failures + TestSensor(app)

    if len(failures) != 0:
        logging.error("\n\nYou've had {} tests fail:\n".format(len(failures)))
        for i in failures:
            logging.info(i['TestName'])
            logging.error(i['ErrorGiven'])
    else:
        logging.info("\nAll tests have passed succesfully!\n")
    ans = raw_input("Would you like to enter the shell with the test data? (y/n) ")
    if ans == 'y':
        IPython.embed()

    teleceptor.isTesting = False
    logging.info("Removing test db.")
    os.remove(teleceptor.TESTDBFILE)








