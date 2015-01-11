#!/usr/bin/env python
import unittest
import os
import sys
import subprocess
import time
PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(PATH)
from teleceptor import WEBROOT,PORT



class TestTeleceptor(unittest.TestCase):

    process = None

    @classmethod
    def setUpClass(self):
        os.environ["TELECEPTOR_TEST"] = 'BLAH'
        self.process = subprocess.Popen(sys.executable + " "+ os.path.join(PATH,'teleceptorcmd envtest')) 
        time.sleep(1)

    @classmethod
    def tearDownClass(self):
        print "Killing Server"
        self.process.kill()        

    def test_true(self):
        self.assertTrue(True)

    def test_false(self):
        self.assertFalse(False)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTeleceptor, 'test'))
    return suite



if __name__ == "__main__":

    unittest.main()
