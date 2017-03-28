import os
import sys
import IPython
from webtest import TestApp
import time
import json
import logging
import math
PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(PATH)
from teleceptor.server import application


def TestStation(app):
    IPython.embed()
    logging.info("Begining tests.")
    TestStationPost(app)
    logging.info("Tests complete.")


def TestStationPost(app):
    logging.info("Begining stations test.")
    CreateStations(app)
    logging.info("Stations test complete.")
    logging.info("Begining readings test.")
    AddReadings(app)
    logging.info("Readings test complete.")
    logging.info("Begining calibration change test.")
    CalibrationOne(app)
    logging.info("Calibration test complete.")
    logging.info("Begining second calibration test.")
    CalibrationTwo(app)
    logging.info("Second calibration test complete.")


def CreateStations(app):
    for i in range(0, 10):
        uuid = "station_test_{}".format(i)
        sensor = json.dumps([{
            'info': {
                'uuid': uuid,
                'name': uuid,
                'description': 'test {}'.format(uuid),
                'out': [],
                'in':[{
                    'name': "avg",
                    'sensor_type': "float",
                    'timestamp': time.time(),
                    'meta_data': {}
                }, {
                    'name': "var",
                    'sensor_type': "float",
                    'timestamp': time.time(),
                    'meta_data': {}
                }]
            }
        }])
        app.post_json('/api/station', json.loads(sensor))


def AddReadings(app):
    for i in range(0, 10):
        uuid = "station_test_{}".format(i)
        sensor = [{
            'info': {
                'uuid': uuid
            },
            'readings': []
        }]
        for j in range(0, 1000):
            sensor[0]['readings'].append(['test_reading', math.sin(j)*100, time.time()-j*60])
        # app.post_json('/api.station', json.loads(json.dumps(sensor)))


def CalibrationOne(app):
    for i in range(0, 10):
        uuid = "station_test_{}".format(i)
        sensor = json.dumps([{
            'info': {
                'uuid': uuid,
                'scale': "({}, {}".format(i, i),
                'calibration_timestamp': time.time()
            }
        }])
        # app.post_json('/api.station', json.loads(sensor))


def CalibrationTwo(app):
    for i in range(0, 10):
        uuid = "station_test_{}".format(i)
        sensor = json.dumps([{
            'info': {
                'uuid': uuid,
                'scale': "({}, {}".format(100-i, 100-i),
                'calibration_timestamp': time.time() - 1000000
            }
        }])
        # app.post_json('/api.station', json.loads(sensor))


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    app = TestApp(application)
    TestStation(app)
