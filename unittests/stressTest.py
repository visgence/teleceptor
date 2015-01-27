#!/usr/bin/env python
"""
stressTest.py

Contributing Authors:
Victor Szczepanski (Visgence, Inc.)

This module defines various stress tests of the teleceptor server and database.

May be called as:
	python stressTest.py
	python stressTest.py --type light [medium, heavy]
	python stressTest.py --numTests 100 #Note, the value may be any integer
"""

import unittest
import json
import requests
import argparse
import sys

#local
from abstractTest import AbstractTeleceptorTest, URL


testTypes = {"light":10, "medium": 20, "heavy": 100, "custom": 0}

testSelection = "light"


class StressTest(AbstractTeleceptorTest):

	def test00_base_url(self):
		for i in range(testTypes[testSelection]):
			r = requests.get(URL)
			self.assertTrue(r.status_code == requests.codes.ok)

	def test01_insert_sensor(self):
		for i in range(testTypes[testSelection]):
			pass

	def test02_get_sensor(self):
		for i in range(testTypes[testSelection]):
			r = requests.get(URL + "/api/sensors/volts")
			self.assertTrue(r.status_code == requests.codes.ok)
			#We do not do full testing here; see functionTest.py for more robust correctness testing.
	def test03_get_sensor_messages_no_message(self):
		for i in range(testTypes[testSelection]):
			r = requests.get(URL + "api/messages/volts")
        	self.assertTrue(r.status_code == requests.codes.ok)



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Run a stress test of the teleceptor backend (server/database)')
	parser.add_argument('--type', nargs='?',type=str, default="light", help='The type of stress test. May be one of ["light","medium","heavy"]')
	parser.add_argument('--numTests', nargs='?', type=int, default=10, help="The custom number of iterations of each stress test.")
	parser.add_argument('unittest_args', nargs='*')

	args = parser.parse_args()
	print args

	if args.type == "light" and args.numTests == 10:
		pass
	elif args.type == "light" and args.numTests != 10:
		testTypes["custom"] = args.numTests
		testSelection = "custom"
	elif args.type != "light" and args.type in testTypes:
		testSelection = args.type
	else:
		#Error
		sys.exit(1)

	sys.argv[1:] = args.unittest_args

	unittest.main()
