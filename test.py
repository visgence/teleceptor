#!/usr/bin/env python
import unittest
import os
import sys
import subprocess
import time
import requests
PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(PATH)
from teleceptor import WEBROOT,PORT



TEST_PORT = 20000
URL = "http://localhost:%d/" % (TEST_PORT)
print URL
class TestTeleceptor(unittest.TestCase):

    process = None

    @classmethod
    def setUpClass(self):
        os.environ["TELECEPTOR_PORT"] = str(TEST_PORT)
        self.process = subprocess.Popen(sys.executable + " "+ os.path.join(PATH,'teleceptorcmd runserver')) 
        time.sleep(2)

    @classmethod
    def tearDownClass(self):
        print "Killing Server"
        self.process.kill()        

    def test00_base_url(self):
        r = requests.get(URL)
        self.assertTrue(r.status_code == requests.codes.ok)

    def test01_json_mote(self):
        r = requests.get(URL)
        self.assertTrue(r.status_code == requests.codes.ok)
        


    def test_false(self):
        self.assertFalse(False)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTeleceptor, 'test'))
    return suite



if __name__ == "__main__":

    unittest.main()
