'''
apiTests.py

Cyrille Gindrea
4/20/17

This script is ment to test all functionality of Teleceptors api.
The readings test and datastream test need the data stream test run first.
Currently only GET and POST or PUT methods are tested.
TODO: Write tests for delete, complete Teleceptor api to include all methods.

'''
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


# ==========================================================READING TESTS============================================ #


def TestReading(app):
    logging.info("Being reading tests")
    failures = TestReadingPost(app)
    failures = failures + TestReadingGet(app)
    logging.info("Reading tests completed")
    return failures


def TestReadingPost(app):
    logging.info("Begin no info test")
    failures = PostReadingNoInfo(app)
    logging.info("No info test complete")
    logging.info("Begin ds test")
    failures = failures + PostReadingDS(app)
    logging.info("DS test complete")
    logging.info("Begin DS & Val test")
    failures = failures + PostReadingDSVal(app)
    logging.info("DS & val test complete")
    logging.info("Begin DS, Val, & Time test")
    failures = failures + PostReadingDSValTime(app)
    logging.info("DS, Val, & Time test complete")
    logging.info("Begin wrong DS test")
    failures = failures + PostReadingWrongDS(app)
    logging.info("Wrong DS test complete")
    logging.info("Begin multiple readings test.")
    failures = failures + PostMultipleReadings(app)
    logging.info("multiple readings test complete.")
    return failures


def TestReadingGet(app):
    logging.info("Begin all readings test")
    failures = GetAllReadings(app)
    logging.info("All readings test complete")
    logging.info("Begin readings with start test")
    failures = failures + GetReadingsWithStart(app)
    logging.info("Readings with start test complete")
    logging.info("Begin readings with end test")
    failures = failures + GetReadingsWithEnd(app)
    logging.info("Readings with end test complete")
    logging.info("Begin readings with both test")
    failures = failures + GetReadingsWithBoth(app)
    logging.info("Readings with both test complete")
    logging.info("Begin readings for sensor test")
    failures = failures + GetReadingsForSensor(app)
    logging.info("Readings for sensor test complete")
    logging.info("Being readings for sensor with start test")
    failures = failures + GetReadingsForSensorWithStart(app)
    logging.info("Readings for sensor with start test complete")
    logging.info("Begin readings for sensor with end test")
    failures = failures + GetReadingsForSensorWithEnd(app)
    logging.info("Readings for sensor with end test complete")
    logging.info("Begin readings for sensor with both test")
    failures = failures + GetReadingsForSensorWithBoth(app)
    logging.info("Readings for sensor with both test complete")
    return failures


def PostReadingNoInfo(app):
    reading = json.dumps({})
    failures = []
    try:
        response = app.post_json('/api/readings/', json.loads(reading))
        if 'error' not in response.json:
            failures.append({
                'TestName': "PostReadingNoInfo",
                'ErrorGiven': "Did not receive error from server."
            })
    except Exception, e:
        failures.append({
            'TestName': "PostReadingNoInfo",
            'ErrorGiven': e
        })
    return failures


def PostReadingDS(app):
    reading = json.dumps({
        "readings": [(
            3,
            None,
            None
            )]
        })
    failures = []
    try:
        response = app.post_json('/api/readings/', json.loads(reading))
        if response.json['successfull_insertions'] != 0:
            failures.append({
                'TestName': "PostReadingDS",
                'ErrorGiven': "A reading was inserted when it wasn't supposed to be"
            })
    except Exception, e:
        failures.append({
            'TestName': "PostReadingDS",
            'ErrorGiven': e
        })
    return failures


def PostReadingDSVal(app):
    reading = json.dumps({
        "readings": [(
            1,
            5,
            None
            )]
        })
    failures = []
    try:
        response = app.post_json('/api/readings/', json.loads(reading))
        if response.json['successfull_insertions'] != 1:
            failures.append({
                'TestName': "PostReadingDSVal",
                'ErrorGiven': "The reading wasn't inserted when it should of been"
            })
    except Exception, e:
        failures.append({
            'TestName': "PostReadingDSVal",
            'ErrorGiven': e
        })
    return failures


def PostReadingDSValTime(app):
    reading = json.dumps({
        "readings": [(
            1,
            10,
            100000
            )]
        })
    failures = []
    try:
        response = app.post_json('/api/readings/', json.loads(reading))
        if response.json['successfull_insertions'] != 1:
            failures.append({
                'TestName': "PostReadingDSValTime",
                'ErrorGiven': "The reading wasn't inserted when it should of been"
            })
    except Exception, e:
        failures.append({
            'TestName': "PostReadingDSValTime",
            'ErrorGiven': e
        })
    return failures


def PostReadingWrongDS(app):
    reading = json.dumps({
        "readings": [(
            100,
            10,
            100000
            )]
        })
    failures = []
    try:
        response = app.post_json('/api/readings/', json.loads(reading))
        if response.json['successfull_insertions'] != 0:
            failures.append({
                'TestName': "PostReadingWrongDS",
                'ErrorGiven': "The reading was inserted when it should of been."
            })

    except Exception, e:
        failures.append({
            'TestName': "PostReadingWrongDS",
            'ErrorGiven': e
        })
    return failures


def PostMultipleReadings(app):
    # This should add only eight readings, failing two of them.
    readings = json.dumps({
        "readings": [
            (1, 10, 456),
            (3, 10, 5432),
            (50, 10, 876),
            (7, 10, 8765),
            (9, 10, 2346),
            (10, 10, 457656),
            (2, 10, 5445632),
            (4, 10, 234),
            (99, 10, 4577),
            (1, 10, 765)
        ]
    })
    failures = []
    try:
        response = app.post_json('/api/readings/', json.loads(readings))
        if response.json['successfull_insertions'] != 8:
            failures.append({
                'TestName': "PostReadingWrongDS",
                'ErrorGiven': "The reading was inserted when it should of been."
            })
    except Exception, e:
        failures.append({
            'TestName': "PostReadingWrongDS",
            'ErrorGiven': e
        })
    return failures


def GetAllReadings(app):
    failures = []
    try:
        response = app.get('/api/readings/')
        if len(response.json['readings']) == 0:
            failures.append({
                'TestName': "GetAllReadings",
                'ErrorGiven': "The should be readings returned"
            })
        else:
            q = session.query(SensorReading).all()
            if len(q) != len(response.json['readings']):
                failures.append({
                    'TestName': "GetAllReadings",
                    'ErrorGiven': "The amount returned isn't the same as the amount in database"
                })
    except Exception, e:
        failures.append({
            'TestName': "GetAllReadings",
            'ErrorGiven': e
        })
    return failures


def GetReadingsWithStart(app):
    failures = []
    try:
        response = app.get('/api/readings/?start={}'.format(int(time.time()-70*60)))
        if len(response.json['readings']) == 0:
            failures.append({
                'TestName': "GetReadingsWithStart",
                'ErrorGiven': "The should be readings returned"
            })
        else:
            q = session.query(SensorReading)
            for i in response.json['readings']:
                if i[0] < time.time()-70*60:
                    failures.append({
                        'TestName': "GetReadingsWithStart",
                        'ErrorGiven': "There are dates that wern't filtered out."
                    })
    except Exception, e:
        failures.append({
            'TestName': "GetReadingsWithStart",
            'ErrorGiven': e
        })
    return failures


def GetReadingsWithEnd(app):
    failures = []
    try:
        response = app.get('/api/readings/?end={}'.format(int(time.time()-30*60)))
        if len(response.json['readings']) == 0:
            failures.append({
                'TestName': "GetReadingsWithEnd",
                'ErrorGiven': "The should be readings returned"
            })
        else:
            q = session.query(SensorReading)
            for i in response.json['readings']:
                if i[0] > time.time()-30*60:
                    failures.append({
                        'TestName': "GetReadingsWithEnd",
                        'ErrorGiven': "There are dates that wern't filtered out."
                    })
    except Exception, e:
        failures.append({
            'TestName': "GetReadingsWithEnd",
            'ErrorGiven': e
        })
    return failures


def GetReadingsWithBoth(app):
    failures = []
    try:
        response = app.get('/api/readings/?start={}&end={}'.format(int(time.time()-70*60), int(time.time()-30*60)))
        if len(response.json['readings']) == 0:
            failures.append({
                'TestName': "GetReadingsWithBoth",
                'ErrorGiven': "The should be readings returned"
            })
        else:
            q = session.query(SensorReading)
            for i in response.json['readings']:
                if i[0] < time.time()-70*60 or i[0] > time.time()-30*60:
                    failures.append({
                        'TestName': "GetReadingsWithBoth",
                        'ErrorGiven': "There are dates that wern't filtered out."
                    })
    except Exception, e:
        failures.append({
            'TestName': "GetReadingsWithBoth",
            'ErrorGiven': e
        })
    return failures


def GetReadingsForSensor(app):
    failures = []
    try:
        response = app.get('/api/readings/?datastream=1')
        if len(response.json['readings']) == 0:
            failures.append({
                'TestName': "GetReadingsForSensor",
                'ErrorGiven': "The should be readings returned"
            })
        else:
            q = session.query(SensorReading).filter_by(datastream=1).all()
            if len(q) != len(response.json['readings']):
                failures.append({
                    'TestName': "GetReadingsForSensor",
                    'ErrorGiven': "The amount returned isn't the same as the amount in database"
                })
    except Exception, e:
        failures.append({
            'TestName': "GetReadingsForSensor",
            'ErrorGiven': e
        })
    return failures


def GetReadingsForSensorWithStart(app):
    failures = []
    try:
        response = app.get('/api/readings/?datastream=1&start={}'.format(int(time.time()-70*60)))
        if len(response.json['readings']) == 0:
            failures.append({
                'TestName': "GetReadingsForSensorWithStart",
                'ErrorGiven': "The should be readings returned"
            })
        else:
            q = session.query(SensorReading).filter_by(datastream=1)
            for i in response.json['readings']:
                if i[0] < int(time.time()-70*60):
                    failures.append({
                        'TestName': "GetReadingsForSensorWithStart",
                        'ErrorGiven': "There are dates that wern't filtered out."
                    })
    except Exception, e:
        failures.append({
            'TestName': "GetReadingsForSensorWithStart",
            'ErrorGiven': e
        })
    return failures


def GetReadingsForSensorWithEnd(app):
    failures = []
    try:
        response = app.get('/api/readings/?datastream=1&end={}'.format(int(time.time()-30*60)))
        if len(response.json['readings']) == 0:
            failures.append({
                'TestName': "GetReadingsForSensorWithEnd",
                'ErrorGiven': "The should be readings returned"
            })
        else:
            q = session.query(SensorReading).filter_by(datastream=1)
            for i in response.json['readings']:
                if i[0] > int(time.time()-30*60):
                    failures.append({
                        'TestName': "GetReadingsForSensorWithEnd",
                        'ErrorGiven': "There are dates that wern't filtered out."
                    })
    except Exception, e:
        failures.append({
            'TestName': "GetReadingsForSensorWithEnd",
            'ErrorGiven': e
        })
    return failures


def GetReadingsForSensorWithBoth(app):
    failures = []
    try:
        response = app.get('/api/readings/?datastream=1&start={}&end={}'.format(int(time.time()-70*60), int(time.time()-30*60)))
        if len(response.json['readings']) == 0:
            failures.append({
                'TestName': "GetReadingsForSensorWithBoth",
                'ErrorGiven': "The should be readings returned"
            })
        else:
            q = session.query(SensorReading).filter_by(datastream=1)
            for i in response.json['readings']:
                if i[0] < int(time.time()-70*60) or i[0] > int(time.time()-30*60):
                    failures.append({
                        'TestName': "GetReadingsForSensorWithBoth",
                        'ErrorGiven': "There are dates that wern't filtered out."
                    })
    except Exception, e:
        failures.append({
            'TestName': "GetReadingsForSensorWithBoth",
            'ErrorGiven': e
        })
    return failures


# ==========================================================DATASTREAM TESTS============================================ #


def TestDatastream(app):
    logging.info("Being datastream tests")
    failures = TestDatastreamPut(app)
    failures = failures + TestDatastreamGet(app)
    logging.info("Datastream tests completed")
    return failures


def TestDatastreamPut(app):
    logging.info("Begin put nothing test.")
    failures = PutNothing(app)
    logging.info("Put nothing test complete.")
    logging.info("Begin put stream with args test.")
    failures = failures + PutStreamArgs(app)
    logging.info("Put stream with args test complete.")
    logging.info("Begin put stream without args test.")
    failures = failures + PutStreamNoArgs(app)
    logging.info("Put stream without args complete.")
    logging.info("Begin put incorrect stream test.")
    failures = failures + PutIncorrectStream(app)
    logging.info("Put incorrect stream test0 complete.")
    return failures


def TestDatastreamGet(app):
    logging.info("Begin get all streams test.")
    failures = GetAllStreams(app)
    logging.info("Get all streams test complete.")
    logging.info("Begin get stream by id test.")
    failures = failures + GetStreamById(app)
    logging.info("Get stream by id test complete.")
    logging.info("Begin get stream by sensor test.")
    failures = failures + GetStreamBySensor(app)
    logging.info("Get stream by sensor test complete.")
    logging.info("Begin get stream with wrong id test.")
    failures = failures + GetStreamWrongId(app)
    logging.info("Get stream with wrong id test complete.")
    logging.info("Begin get stream with wrong sensor id test.")
    failures = failures + GetStreamWrongSensor(app)
    logging.info("Get stream by wrong sensor id test complete.")
    return failures


def PutNothing(app):
    stream = json.dumps({
        'min_value': 0,
        'max_value': 100
    })
    failures = []
    try:
        response = app.put_json('/api/datastreams/', json.loads(stream))
        if 'error' not in response.json:
            failures.append({
                'TestName': "DataStreams PutNothing",
                'ErrorGiven': "Did not receive error from server."
            })
    except Exception, e:
        failures.append({
            'TestName': "PutNothing",
            'ErrorGiven': e
        })
    return failures


def PutStreamArgs(app):
    stream = json.dumps({
        'min_value': 0,
        'max_value': 100
    })
    failures = []
    try:
        response = app.put_json('/api/datastreams/1', json.loads(stream))
        if response.json['stream']['name'] != 'station_test_0test_sensor':
            failures.append({
                'TestName': "PutStreamArgs",
                'ErrorGiven': "streams dont' match"
            })
    except Exception, e:
        failures.append({
            'TestName': "PutStreamArgs",
            'ErrorGiven': e
        })
    return failures


def PutStreamNoArgs(app):
    stream = json.dumps({})
    failures = []
    try:
        response = app.put_json('/api/datastreams/1', json.loads(stream))
        if response.json['stream']['name'] != 'station_test_0test_sensor':
            failures.append({
                'TestName': "PutStreamNoArgs",
                'ErrorGiven': "streams dont' match"
            })
        if response.json['stream']['min_value'] != 0 or response.json['stream']['max_value'] != 100:
            failures.append({
                'TestName': "PutStreamNoArgs",
                'ErrorGiven': "Values were modified when they shouldn't have been."
            })
    except Exception, e:
        failures.append({
            'TestName': "PutStreamNoArgs",
            'ErrorGiven': e
        })
    return failures


def PutIncorrectStream(app):
    stream = json.dumps({
        'min_value': 0,
        'max_value': 100
    })
    failures = []
    try:
        response = app.put_json('/api/datastreams/99', json.loads(stream))
        if 'error' not in response.json:
            failures.append({
                'TestName': "PutIncorrectStream",
                'ErrorGiven': "Server didn't send error."
            })
    except Exception, e:
        failures.append({
            'TestName': "PutIncorrectStream",
            'ErrorGiven': e
        })
    return failures


def GetAllStreams(app):
    failures = []
    try:
        response = app.get('/api/datastreams/')
        j = 0
        for i in response.json['datastreams']:
            if str(i['name']) != "station_test_{}test_sensor".format(j):
                failures.append({
                    'TestName': "GetAllStreams",
                    'ErrorGiven': "An incorrect name was found in the streams"
                })
            j += 1
    except Exception, e:
        failures.append({
            'TestName': "GetAllStreams",
            'ErrorGiven': e
        })
    return failures


def GetStreamById(app):
    failures = []
    try:
        response = app.get('/api/datastreams/3')
        if str(response.json['stream']['name']) != "station_test_2test_sensor":
            failures.append({
                'TestName': "GetStreamById",
                'ErrorGiven': "An stream names don't match up"
            })
    except Exception, e:
        failures.append({
            'TestName': "GetStreamById",
            'ErrorGiven': e
        })
    return failures


def GetStreamBySensor(app):
    sensor = json.dumps({
        'sensor': 'station_test_0test_sensor'
    })
    failures = []
    try:
        response = app.get('/api/datastreams/', json.loads(sensor))
        if response.json['datastreams'][0]['sensor'] != "station_test_0test_sensor":
            failures.append({
                'TestName': "GetStreamBySensor",
                'ErrorGiven': "Response didn't return correct stream."
            })
    except Exception, e:
        failures.append({
            'TestName': "GetStreamBySensor",
            'ErrorGiven': e
        })
    return failures


def GetStreamWrongId(app):
    failures = []
    try:
        response = app.get('/api/datastreams/99')
        if 'error' not in response.json:
            failures.append({
                'TestName': "GetStreamWrongId",
                'ErrorGiven': "Server didn't send error."
            })
    except Exception, e:
        failures.append({
            'TestName': "GetStreamWrongId",
            'ErrorGiven': e
        })
    return failures


def GetStreamWrongSensor(app):
    sensor = json.dumps({
        'sensor': 'incorrectSensorUUID'
    })
    failures = []
    try:
        response = app.get('/api/datastreams/', json.loads(sensor))
        if len(response.json['datastreams']) != 0:
            failures.append({
                'TestName': "GetStreamWrongSensor",
                'ErrorGiven': "Server responded with streams when it shouldn't of."
            })
    except Exception, e:
        failures.append({
            'TestName': "GetStreamWrongSensor",
            'ErrorGiven': e
        })
    return failures


# ==========================================================SENSOR TESTS============================================ #


def TestSensor(app):
    logging.info("Begin sensor tests.")
    failures = TestSensorPost(app)
    failures = failures + TestSensorGet(app)
    logging.info("Sensor tests completed.")
    return failures


def TestSensorPost(app):
    logging.info("Begin add sensor test.")
    failures = AddSensor(app)
    logging.info("Add sensor test complete.")
    logging.info("Begin add sensor with calibration test.")
    failures = failures + AddSensorWithCalibration(app)
    logging.info("Add sensor with calibration test complete.")
    logging.info("Begin add sensor with no id test.")
    failures = failures + AddSensorNoId(app)
    logging.info("Add sensor with no id test complete.")
    logging.info("Begin update new calibration test.")
    failures = failures + UpdateNewCalibration(app)
    logging.info("Update new calibration test complete.")
    logging.info("Begin update old calibration test.")
    failures = failures + UpdateOldCalibration(app)
    logging.info("Update old calibration test complete.")
    logging.info("Begin update no timestamp test.")
    return failures


def TestSensorGet(app):
    logging.info("Begin get sensor test.")
    failures = GetSensor(app)
    logging.info("Get sensor test complete.")
    logging.info("Begin get all sensors test.")
    failures = failures + GetAllSensors(app)
    logging.info("Get all sensors test complete.")
    logging.info("Begin get incorrect sensor test.")
    failures = failures + GetIncorrectSensor(app)
    logging.info("Get incorrect sensor test complete.")
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
        'last_calibration': {
            'timestamp': time.time(),
            'coefficients': "[10,10]"
        }
    })
    failures = doSensorPost(sensor)
    test = session.query(Sensor).filter_by(uuid='sensor_test_1').first()
    if test is None:
        failures.append({
            'TestName': "AddSensorWithCalibration",
            'ErrorGiven': "query was None."
        })
    elif str(test.toDict()['last_calibration']['coefficients']) != "[10,10]":
        failures.append({
            'TestName': "AddSensorWithCalibration",
            'ErrorGiven': "coefficients wern't recorded properly."
        })
    return failures


def AddSensorNoId(app):
    # This should NOT do anything including updating coefficients.
    sensor = json.dumps({
        'name': 'sensor_test_0',
        'last_calibration': {
            'timestamp': time.time(),
            'coefficients': "[5, 5]"
        }
    })
    failures = doSensorPost(sensor)
    test = session.query(Sensor).filter_by(uuid='sensor_test_0').first()
    if test is None:
        failures.append({
            'TestName': "AddSensorNoId",
            'ErrorGiven': "Sensor doesn't exist when it should from test #1"
        })
    elif 'last_calibration' in test.toDict():
        failures.append({
            'TestName': "AddSensorNoId",
            'ErrorGiven': "coefficients were added when they shouldn't have been."
        })
    return failures


def UpdateNewCalibration(app):
    # Updates a sensors calibration.
    sensor = json.dumps({
        'uuid': "sensor_test_0",
        'last_calibration': {
            'timestamp': time.time(),
            'coefficients': "[7,7]"
        }
    })

    failures = doSensorPost(sensor)

    test = session.query(Sensor).filter_by(uuid='sensor_test_0').first()
    if test is None:
        failures.append({
            'TestName': "UpdateNewCalibration",
            'ErrorGiven': "Sensor doesn't exit when it should from test #1"
        })
    elif test.toDict()['last_calibration']['coefficients'] != "[7,7]":
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
    failures = []
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
    elif test.toDict()['uuid'] != info['sensor']['uuid']:
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
    for i in info['sensors']:
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
    try:
        app.post_json('/api/sensors', json.loads(data))
        return []
    except Exception, e:
        return [{
            'TestName': "doSensorPost: {}".format(data),
            'ErrorGiven': e
        }]


# ==========================================================STATION TESTS============================================ #


def TestStation(app):
    logging.info("Begining station tests.")
    failures = TestStationPost(app)
    logging.info("Station tests complete.")
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
        failures = failures + TestStation(app)
        failures = failures + TestSensor(app)
        failures = failures + TestDatastream(app)
        failures = failures + TestReading(app)
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
