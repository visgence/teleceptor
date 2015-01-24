#!/usr/bin/env python
import unittest
import os
import sys
import subprocess
import time
import json
import requests
import tempfile
import shutil
PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(PATH)

from teleceptor.sessionManager import sessionScope


DATAPATH = tempfile.mkdtemp(prefix="tmpteleceptor")
TEST_PORT = 20000
URL = "http://localhost:%d/" % (TEST_PORT)
print URL
print DATAPATH

def build_config():

    data = {"DBFILE": "database/base_station.db",
            "WHISPER_DATA": "whisperData",
            "WHISPER_ARCHIVES": ["60:1440", "15m:14d", "6h:1y"],
            "SQLDATA": True,
            "SQLREADTIME": 7200,
            "PORT": TEST_PORT,
            "LOG": "teleceptor.log",
            "TCP_POLLER_HOSTS": [],
            "USE_DEBUG": False}

    conf = open(os.path.join(DATAPATH, 'config.json'), "w")
    json.dump(data,conf,indent=4)
    conf.close()


class TestTeleceptor(unittest.TestCase):

    process = None

    @classmethod
    def setUpClass(self):
        build_config()
        os.environ["TELECEPTOR_DATAPATH"] = DATAPATH
        print sys.executable + " "+ os.path.join(PATH,'teleceptorcmd setup')
        assert subprocess.call([sys.executable, os.path.join(PATH, 'teleceptorcmd'), 'setup']) == 0
        assert subprocess.call([sys.executable, os.path.join(PATH, 'teleceptorcmd'), 'loadfixtures']) == 0
        self.process = subprocess.Popen([sys.executable,os.path.join(PATH,'teleceptorcmd'),'runserver'])
        time.sleep(2)
        #insert test sensors

    def test00_base_url(self):
        r = requests.get(URL)
        self.assertTrue(r.status_code == requests.codes.ok)

    def test01_json_mote(self):
        r = requests.get(URL + "/api/sensors")
        sensors = r.json()
        self.assertTrue(r.status_code == requests.codes.ok)
        self.assertTrue('sensors' in sensors)

    """
    Tests for sensor api
    """
    def test02_sensor_get_single(self):
        """
        Assumes a sensor with uuid volts does exist.
        """
        r = requests.get(URL + "/api/sensors/volts")
        self.assertTrue(r.status_code == requests.codes.ok)
        sensors = r.json()
        self.assertTrue('sensor' in sensors)

    def test03_sensor_get_wrong_id(self):
        """
        Assumes a sensor with uuid 1 does not exist.
        """
        r = requests.get(URL + "/api/sensors/1")
        self.assertTrue(r.status_code == requests.codes.ok)
        sensors = r.json()
        self.assertTrue('error' in sensors)

    def test04_sensor_put_correct_sensor_empty_data(self):
        """
        Assumes a sensor with uuid volts does exist
        """
        r = requests.put(URL + "/api/sensors/volts", data=json.dumps({}))
        self.assertTrue(r.status_code == requests.codes.ok)
        sensors = r.json()
        self.assertTrue('sensor' in sensors)

    def test05_sensor_put_correct_sensor_full_data(self):
        """
        Assumes a sensor with uuid volts does exist.
        """
        requestData = {"uuid":"1", "message": {"id":1, "message": "true", "message_queue_id": 1, "timeout":1, "read": False}, "last_calibration": {"coefficients": [0,1], "timestamp": 1}, "sensor_IOtype": False, "sensor_type": "bool", "last_value": "last", "name": "v", "units": "V", "model": "m", "description": "desc", "last_calibration_id": 1, "message_queue_id": 1, "message_queue": 1, "meta_data": "MetaData"}
        r = requests.put(URL + "/api/sensors/volts", data=json.dumps(requestData))
        self.assertTrue(r.status_code == requests.codes.ok)
        sensors = r.json()
        self.assertTrue('sensor' in sensors)
        self.assertFalse(requestData['uuid'] == sensors['sensor']['uuid'])
        self.assertTrue(requestData['sensor_type'] == sensors['sensor']['sensor_type'])
        self.assertTrue(requestData['units'] == sensors['sensor']['units'])
        self.assertTrue(requestData['description'] == sensors['sensor']['description'])
        self.assertTrue(requestData['name'] == sensors['sensor']['name'])
        self.assertFalse(requestData['last_value'] == sensors['sensor']['last_value'])
        self.assertTrue(requestData['sensor_IOtype'] == sensors['sensor']['sensor_IOtype'])
        self.assertTrue(requestData['meta_data'] == sensors['sensor']['meta_data'])
        self.assertFalse(requestData['last_calibration'] == sensors['sensor']['last_calibration'])

    def test06_sensor_put_correct_sensor_no_data(self):
        """
        Assumes sensor with uuid volts does exist.
        """
        r = requests.put(URL + "api/sensors/volts")
        self.assertTrue(r.status_code == requests.codes.ok)
        sensors = r.json()
        self.assertTrue('sensor' in sensors)
        self.assertTrue(sensors['sensor']['uuid'] == "volts")


    """
    Tests for messages api
    """


    @classmethod
    def tearDownClass(self):
        print "Killing Server"
        self.process.kill()
        print "Removing tempdir " + DATAPATH
        shutil.rmtree(DATAPATH)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTeleceptor, 'test'))
    return suite



if __name__ == "__main__":

    unittest.main()
