"""
abstractTest.py

Contributing Authors:
Evan Salazar (Visgence, Inc.)
Victor Szczepanski (Visgence, Inc.)

This module defines the setup and teardown methods that all teleceptor test suites can inherit from.

Depencencies:
unittest

"""

# !/usr/bin/env python
import unittest
import os
import sys
import subprocess
import time
import json
import requests
import tempfile
import shutil
PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__))))
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
            "USE_DEBUG": False,
            "SUPRESS_SERVER_OUTPUT": True,
            "USE_SQL_ALWAYS": False}

    conf = open(os.path.join(DATAPATH, 'config.json'), "w")
    json.dump(data, conf, indent=4)
    conf.close()


class AbstractTeleceptorTest(unittest.TestCase):

    process = None

    @classmethod
    def setUpClass(self):
        build_config()
        os.environ["TELECEPTOR_DATAPATH"] = DATAPATH
        # Set up the database and create config information
        assert subprocess.call([sys.executable, os.path.join(PATH, 'teleceptorcmd'), 'setup']) == 0
        # Add some test sensors to database
        assert subprocess.call([sys.executable, os.path.join(PATH, 'teleceptorcmd'), 'loadfixtures']) == 0
        # start server
        self.process = subprocess.Popen([sys.executable, os.path.join(PATH, 'teleceptorcmd'), 'runserver'])
        time.sleep(2)

    """
    Set up and teardown before and after each test
    """
    def setUp(self):
        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print "\n%s: %.3f\n" % (self.id(), t)

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
