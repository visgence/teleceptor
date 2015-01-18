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
        assert subprocess.call(sys.executable + " "+ os.path.join(PATH,'teleceptorcmd setup')) == 0
        self.process = subprocess.Popen(sys.executable + " "+ os.path.join(PATH,'teleceptorcmd runserver')) 
        time.sleep(2)
    def test00_base_url(self):
        r = requests.get(URL)
        self.assertTrue(r.status_code == requests.codes.ok)

    def test01_json_mote(self):
        r = requests.get(URL + "/api/sensors")
        sensors = r.json()
        self.assertTrue(r.status_code == requests.codes.ok)
        self.assertTrue('sensors' in sensors)


        

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
