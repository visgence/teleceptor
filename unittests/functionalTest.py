#!/usr/bin/env python
import unittest
import json
import requests
import time

# local
from abstractTest import AbstractTeleceptorTest, URL


class TestTeleceptor(AbstractTeleceptorTest):

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
        print r.json()
        print r.status_code
        self.assertTrue(r.status_code == requests.codes.ok)
        sensors = r.json()
        self.assertTrue('sensor' in sensors)

    def test03_sensor_get_wrong_id(self):
        """
        Assumes a sensor with uuid 1 does not exist.
        """
        r = requests.get(URL + "/api/sensors/1")
        self.assertFalse(r.status_code == requests.codes.ok)
        sensors = r.json()
        print r.json()
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
        requestData = {
            "uuid": "1", "message": {
                "id": 1, "message": "true", "message_queue_id": 1, "timeout": 1, "read": False
            },
            "last_calibration": {
                "coefficients": [0, 1],
                "timestamp": 1
            },
            "sensor_IOtype": False,
            "sensor_type": "bool",
            "last_value": "last",
            "name": "v",
            "units": "V",
            "model": "m",
            "description": "desc",
            "last_calibration_id": 1,
            "message_queue_id": 1,
            "message_queue": 1,
            "meta_data": "MetaData"
        }
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

    def test07_sensor_put_incorrect_sensor(self):
        """
        Assumes sensor with uuid 1 does not exist
        """

        r = requests.put(URL + "api/sensors/1", data=json.dumps({}))
        self.assertFalse(r.status_code == requests.codes.ok)
        self.assertTrue('error' in r.json())

    """
    Tests for messages api
    """

    def test08_messages_get_correct_sensor_no_message(self):
        """
        Tests when a get is made to a sensor with no messages added.
        Assumes sensor with uuid volts does exist, and has no messages added.
        """
        r = requests.get(URL + "api/messages/volts")
        self.assertTrue(r.status_code == requests.codes.ok)
        responsedata = r.json()
        self.assertTrue('message_queue' in responsedata)
        self.assertTrue('messages' in responsedata['message_queue'])
        self.assertTrue(len(responsedata['message_queue']['messages']) == 0)

    def test09_messages_get_correct_sensor_has_messages(self):
        """
        Tests when a get is made to a sensor with messages added.
        This test adds a message to a sensor with uuid volts.
        """
        r = requests.post(URL + "api/messages/volts", data=json.dumps({"message": True, "duration": 30000}))

        self.assertTrue(r.status_code == requests.codes.ok)
        self.assertTrue('error' not in r.json())

        r = requests.get(URL + "api/messages/volts")
        self.assertTrue(r.status_code == requests.codes.ok)
        responsedata = r.json()
        self.assertTrue('message_queue' in responsedata)
        self.assertTrue('messages' in responsedata['message_queue'])
        self.assertTrue(len(responsedata['message_queue']['messages']) > 0)
        self.assertTrue(responsedata['message_queue']['messages'][-1]['message'] if True)

    def test10_messages_get_incorrect_sensor(self):
        r = requests.get(URL + "api/messages/1")
        self.assertFalse(r.status_code == requests.codes.ok)
        self.assertTrue('error' in r.json())

    def test11_messages_get_all_sensors(self):
        """
        Assumes at least one sensor is in the database.
        """
        r = requests.get(URL + "api/messages/")
        self.assertTrue(r.status_code == requests.codes.ok)
        responsedata = r.json()

        self.assertTrue('message_queues' in responsedata)
        self.assertTrue(len(responsedata['message_queues']) > 0)

    """
    Tests for station api
    """

    def test12_station_post_existing_sensor(self):
        """
        Tests when a post to station is made for a sensor
        that already exists in the database
        """
        caltime = time.time()
        examplevalue = 22

        # note here that a sensor's full uuid is the concatenation
        # of its mote uuid and its name
        # Since the uuid of our test sensor is volts, we will leave the
        # mote uuid empty. A uuid field must still be included, however.

        jsonExample = [{
            "info": {
                "uuid": "",
                "name": "myfirstmote",
                "description": "My first mote",
                "out": [],
                "in":[{
                    "name": "volts",
                    "sensor_type": "float",
                    "timestamp": caltime,
                    "meta_data": {}
                }]
            },
            "readings": [["volts", examplevalue, time.time()]]}]

        r = requests.post(URL + "/api/station", data=json.dumps(jsonExample))
        self.assertTrue(r.status_code == requests.codes.ok)

        data = r.json()

        self.assertFalse('error' in data)
        self.assertTrue('info' in data)
        self.assertTrue(len(data['info']) > 0)

        self.assertTrue('newValues' in data)

    def test13_station_post_has_messages(self):
        r = requests.post(URL + "api/messages/volts", data=json.dumps({"message": 1.0, "duration": 30000}))

        self.assertTrue(r.status_code == requests.codes.ok)
        self.assertTrue('error' not in r.json())

        print "Posted message for volts."

        caltime = time.time()
        examplevalue = 22

        jsonExample = [{
            "info": {
                "uuid": "",
                "name": "myfirstmote",
                "description": "My first mote",
                "out": [],
                "in":[{
                    "name": "volts",
                    "sensor_type": "float",
                    "timestamp": caltime,
                    "meta_data": {}
                }]
            },
            "readings": [["volts", examplevalue, time.time()]]}]

        r = requests.post(URL + "/api/station", data=json.dumps(jsonExample))
        self.assertTrue(r.status_code == requests.codes.ok)
        data = r.json()
        print "Test 13 reponse data: %s" % str(data)
        self.assertFalse('error' in data)
        self.assertTrue('info' in data)
        self.assertTrue(len(data['info']) > 0)

        self.assertTrue('newValues' in data)
        self.assertTrue('volts' in data['newValues'])
        self.assertTrue(len(data['newValues']['volts']) > 0)

    def test14_station_post_only_output(self):
        """
        Tests when a post is made for a sensor that is output only.
        We expect 'newValues' to be an empty dictionary.
        """
        caltime = time.time()
        examplevalue = 22
        jsonExample = [{
            "info": {
                "uuid": "",
                "name": "myfirstmote",
                "description": "My first mote",
                "in": [],
                "out":[{
                    "name": "volts",
                    "sensor_type": "float",
                    "timestamp": caltime,
                    "meta_data": {}
                }]
            },
            "readings": [["volts", examplevalue, time.time()]]}]

        r = requests.post(URL + "/api/station", data=json.dumps(jsonExample))
        self.assertTrue(r.status_code == requests.codes.ok)
        data = r.json()

        self.assertFalse('error' in data)
        self.assertTrue('info' in data)
        self.assertTrue(len(data['info']) > 0)

        self.assertTrue('newValues' in data)
        self.assertTrue(len(data['newValues']) == 0)

    def test15_station_post_empty_readings(self):
        caltime = time.time()
        examplevalue = 22
        jsonExample = [{
            "info": {"uuid": "", "name": "myfirstmote", "description": "My first mote", "in": [],
                     "out":[{"name": "volts", "sensor_type": "float", "timestamp": caltime, "meta_data": {}}]}, "readings": []}]

        r = requests.post(URL + "/api/station", data=json.dumps(jsonExample))
        self.assertTrue(r.status_code == requests.codes.ok)
        data = r.json()

        self.assertFalse('error' in data)
        self.assertTrue('info' in data)
        self.assertTrue(len(data['info']) > 0)

    def test16_station_post_no_readings(self):
        caltime = time.time()
        examplevalue = 22
        jsonExample = [{"info": {"uuid": "", "name": "myfirstmote", "description": "My first mote", "in": [],
                        "out":[{"name": "volts", "sensor_type": "float", "timestamp": caltime, "meta_data": {}}]}}]

        r = requests.post(URL + "/api/station", data=json.dumps(jsonExample))
        self.assertFalse(r.status_code == requests.codes.ok)

    def test17_station_post_nonexistant_sensor(self):
        """
        Tests when a sensor is not in the database. A new sensor should be created.
        """

        # get the number of sensors already in the database
        r = requests.get(URL + "/api/sensors")
        sensors = r.json()
        self.assertTrue(r.status_code == requests.codes.ok)
        self.assertTrue('sensors' in sensors)

        numSensors = len(sensors['sensors'])

        caltime = time.time()
        examplevalue = 22
        jsonExample = [{"info": {"uuid": "", "name": "myfirstmote", "description": "My first mote", "in": [],
                        "out":[{"name": "1", "sensor_type": "float", "timestamp": caltime, "meta_data": {}}]}, "readings": []}]

        r = requests.post(URL + "/api/station", data=json.dumps(jsonExample))

        self.assertTrue(r.status_code == requests.codes.ok)
        data = r.json()

        self.assertFalse('error' in data)
        self.assertTrue('info' in data)
        self.assertTrue(len(data['info']) > 0)

        self.assertTrue('1' == data['info'][0]['uuid'])

        # check that the number of sensors has increased
        r = requests.get(URL + "/api/sensors")
        sensors = r.json()
        self.assertTrue(r.status_code == requests.codes.ok)
        self.assertTrue('sensors' in sensors)

        self.assertTrue(len(sensors['sensors']) == numSensors + 1)

    def test18_station_post_update_calibration(self):
        """
        Tests changing the calibration. Assumes the test sensor uses the
        identity calibration function [1,0]
        """

        # get the test sensor's calibration
        r = requests.get(URL + "/api/sensors/volts")
        self.assertTrue(r.status_code == requests.codes.ok)
        sensors = r.json()
        self.assertTrue('sensor' in sensors)

        self.assertTrue(sensors['sensor']['uuid'] == 'volts')

        initialCalibration = sensors['sensor']['last_calibration']['coefficients']

        # create new calibration
        newCalibration = [i + 1 for i in initialCalibration]

        # post to station
        caltime = time.time()
        examplevalue = 22
        jsonExample = [{"info": {"uuid": "", "name": "myfirstmote", "description": "My first mote", "in": [],
                        "out":[{"scale": newCalibration, "name": "volts", "sensor_type": "float", "timestamp": caltime, "meta_data": {}}]}, "readings": []}]

        r = requests.post(URL + "/api/station", data=json.dumps(jsonExample))

        self.assertTrue(r.status_code == requests.codes.ok)
        data = r.json()

        print "Test 18 response data %s" % str(data)
        print "data['info'][0]['last_calibration']: %s" % str(data['info'][0]['last_calibration'])

        self.assertFalse('error' in data)
        self.assertTrue('info' in data)
        self.assertTrue(len(data['info']) > 0)

        self.assertTrue(data['info'][0]['last_calibration']['coefficients'] == newCalibration)

    """
    Tests for datastreams api
    """

    def test19_datastreams_get_all(self):
        """
        Tests getting all datastreams
        """
        r = requests.get(URL + "/api/datastreams")

        self.assertTrue(r.status_code == requests.codes.ok)
        data = r.json()

        self.assertFalse('error' in data)
        self.assertTrue('datastreams' in data)
        datastreams = data['datastreams']
        self.assertTrue(len(datastreams) > 0)

    def test20_datastreams_get_single(self):
        """
        Tests getting a specific datastream.
        Note that traditionally the client would need to
        get the datastream id by making a get request to sensors.
        """

        r = requests.get(URL + "/api/datastreams/1/")

        self.assertTrue(r.status_code == requests.codes.ok)
        data = r.json()

        self.assertFalse('error' in data)
        self.assertTrue('stream' in data)
        datastream = data['stream']

        self.assertTrue(datastream['id'] == 1)

    def test21_datastreams_get_filtered(self):
        """
        Tests getting a set of datastreams filtered by
        url arguments.
        """

        r = requests.get(URL + "api/datastreams/?sensor=volts")

        self.assertTrue(r.status_code == requests.codes.ok)
        data = r.json()

        self.assertFalse('error' in data)
        self.assertTrue('datastreams' in data)

        datastreams = data['datastreams']

        self.assertTrue(len(datastreams) == 1)
        self.assertTrue(datastreams[0]['sensor'] == "volts")

    def test22_datastreams_get_incorrect_kwarg(self):
        """
        Tests getting a set of datastreams filtered by
        an incorrect url argument.
        """

        r = requests.get(URL + "api/datastreams/?sensor=volts&calibration=[1,0]")

        self.assertFalse(r.status_code == requests.codes.ok)
        data = r.json()

        self.assertTrue('error' in data)

    """
    Tests for readings api
    """

    def test23_readings_get_all(self):
        """
        Tests getting all available readings (i.e. no url arguments).
        """
        r = requests.get(URL + "api/readings/")

        self.assertTrue(r.status_code == requests.codes.ok)

        data = r.json()

        self.assertFalse('error' in data)
        self.assertTrue('readings' in data)
        self.assertTrue(len(data['readings']) > 0)

    def test24_readings_get_condense(self):
        """
        Tests getting all readings with condense set to true.
        This should return readings that are just timestamp, value pairs.
        """
        r = requests.get(URL + "api/readings/?condense=true")

        self.assertTrue(r.status_code == requests.codes.ok)

        data = r.json()

        self.assertFalse('error' in data)
        self.assertTrue('readings' in data)
        self.assertTrue(len(data['readings']) > 0)

        # test that every reading only has two elements.
        # First element is either int or float, second is always float.
        for reading in data['readings']:
            self.assertTrue(len(reading) == 2)
            self.assertTrue(isinstance(reading[0], int) or isinstance(reading[0], float))
            self.assertTrue(isinstance(reading[1], float))

    def test25_readings_get_timeframe_with_data(self):
        """
        Tests that a recently posted reading will be retreived using
        timeframe url arguments. We use the insertion time as start and end
        to ensure we get only the reading we just posted.

        Assumes a datastream with id 1 exists in the database.

        Note that this serves as an indirect test of the readings post api, but
        is not to be used in place of a direct test.
        """

        # format of reading is [datastreamid, value, timestamp]
        insertiontime = int(time.time())
        sampleJson = {'readings': [[1, 1, insertiontime]]}
        r = requests.post(URL + "api/readings/", data=json.dumps(sampleJson))

        self.assertTrue(r.status_code == requests.codes.ok)

        data = r.json()

        self.assertFalse('error' in data)
        self.assertTrue('successfull_insertions' in data)
        self.assertTrue(data['successfull_insertions'] == 1)
        self.assertFalse(data['failed_insertions'] > 0)

        # now get reading, using url arguments
        r = requests.get(URL + "api/readings/?start=" + str(insertiontime) + "&end=" + str(insertiontime) + "&datastream=1")

        self.assertTrue(r.status_code == requests.codes.ok)

        data = r.json()

        self.assertFalse('error' in data)
        self.assertTrue('readings' in data)
        self.assertTrue(len(data['readings']) == 1)

        reading = data['readings'][0]

        self.assertTrue(reading[0] == insertiontime)
        self.assertTrue(reading[1] == 1)

    def test26_readings_post_single_reading(self):
        """
        Tests posting a single reading.

        Assumes a datastream with id 1 exists in the database.
        """
        # format of reading is [datastreamid, value, timestamp]
        sampleJson = {'readings': [[1, 1, time.time()]]}
        r = requests.post(URL + "api/readings/", data=json.dumps(sampleJson))

        self.assertTrue(r.status_code == requests.codes.ok)

        data = r.json()

        self.assertFalse('error' in data)
        self.assertTrue('successfull_insertions' in data)
        self.assertTrue(data['successfull_insertions'] == 1)
        self.assertTrue(data['failed_insertions'] == 0)
        self.assertTrue(data['successfull_insertions'] == data['insertions_attempted'])

    def test27_readings_post_multiple_readings(self):
        """
        Tests posting an array of readings (specifically tests 2 readings).

        Assumes a datastream with id 1 exists in the database.

        Note that whisper will not insert data with timestamp greater than its current time,
        so here we use the current time and current time - 1.
        """

        # format of reading is [datastreamid, value, timestamp]
        sampleJson = {'readings': [[1, 1, time.time()], [1, 2, time.time() - 1]]}
        r = requests.post(URL + "api/readings/", data=json.dumps(sampleJson))

        self.assertTrue(r.status_code == requests.codes.ok)

        data = r.json()

        self.assertFalse('error' in data)
        self.assertTrue('successfull_insertions' in data)
        self.assertTrue(data['successfull_insertions'] == 2)
        self.assertTrue(data['failed_insertions'] == 0)
        self.assertTrue(data['successfull_insertions'] == data['insertions_attempted'])

    def test28_readings_post_future_reading(self):
        """
        Tests inserting a reading with timestamp in the future. Whisper does not accept timestamps
        outside of its range, so the reading should fail to be inserted.
        """
        # format of reading is [datastreamid, value, timestamp]
        sampleJson = {'readings': [[1, 1, time.time() + 3000]]}
        r = requests.post(URL + "api/readings/", data=json.dumps(sampleJson))

        self.assertTrue(r.status_code == requests.codes.ok)

        data = r.json()

        self.assertFalse('error' in data)
        self.assertTrue('successfull_insertions' in data)
        self.assertTrue(data['successfull_insertions'] == 0)
        self.assertTrue(data['failed_insertions'] == 1)
        self.assertFalse(data['successfull_insertions'] == data['insertions_attempted'])

    def test29_readings_post_past_reading(self):
        """
        Tests inserting a reading with a 0 timestamp (far in the past).
        Reading should not be inserted.
        """
        sampleJson = {'readings': [[1, 1, 0]]}
        r = requests.post(URL + "api/readings/", data=json.dumps(sampleJson))

        self.assertTrue(r.status_code == requests.codes.ok)

        data = r.json()

        self.assertFalse('error' in data)
        self.assertTrue('successfull_insertions' in data)
        self.assertTrue(data['successfull_insertions'] == 0)
        self.assertTrue(data['failed_insertions'] == 1)
        self.assertFalse(data['successfull_insertions'] == data['insertions_attempted'])

    def test30_readings_post_empty_readings(self):
        """
        Tests posting an empty array of readings.

        Assumes a datastream with id 1 exists in the database.
        """
        # format of reading is [datastreamid, value, timestamp]
        sampleJson = {'readings': []}
        r = requests.post(URL + "api/readings/", data=json.dumps(sampleJson))

        self.assertTrue(r.status_code == requests.codes.ok)

        data = r.json()

        self.assertFalse('error' in data)
        self.assertTrue('successfull_insertions' in data)
        self.assertTrue(data['successfull_insertions'] == 0)
        self.assertTrue(data['failed_insertions'] == 0)
        self.assertTrue(data['successfull_insertions'] == data['insertions_attempted'])

    def test31_readings_post_no_readings(self):
        """
        Tests posting with no readings. That is, the data field is an empty dictionary.

        """
        r = requests.post(URL + "api/readings/", data=json.dumps({}))

        self.assertFalse(r.status_code == requests.codes.ok)

        data = r.json()

        self.assertTrue('error' in data)

    def test32_readings_post_invalid_JSON(self):
        """
        Tests posting with the data field of the request being garbage.
        """

        r = requests.post(URL + "api/readings/", data="Hi")

        self.assertFalse(r.status_code == requests.codes.ok)

        data = r.json()

        self.assertTrue('error' in data)

    def test33_sensors_delete_correct_uuid(self):
        """
        Tests deleting a sensor. The sensor should be removed from the database.

        Assumes a sensor with uuid `volts` exists.
        """
        # get the information about the sensor we will delete to test against.
        r = requests.get(URL + "api/sensors/volts")

        self.assertTrue(r.status_code == requests.codes.ok)

        getData = r.json()

        self.assertTrue('sensor' in getData)
        self.assertTrue(getData['sensor']['uuid'] == "volts")

        # delete the sensor
        r = requests.delete(URL + "api/sensors/volts")

        self.assertTrue(r.status_code == requests.codes.ok)

        data = r.json()

        self.assertTrue('sensor' in data)
        for key in getData['sensor']:
            self.assertTrue(data['sensor'][key] == getData['sensor'][key])

        # check that sensor is not retrievable from server
        r = requests.get(URL + "api/sensors/volts")

        self.assertFalse(r.status_code == requests.codes.ok)

        data = r.json()

        self.assertTrue('error' in data)
        self.assertFalse('sensor' in data)

    def test34_sensors_delete_incorrect_uuid(self):
        """
        Tests deleting a sensor that does not exist on the server.
        An error should be thrown.

        Assumes a sensor with uuid `v` does not exist.
        """
        # delete the sensor
        r = requests.delete(URL + "api/sensors/v")

        self.assertFalse(r.status_code == requests.codes.ok)

        data = r.json()

        self.assertTrue('error' in data)
        self.assertFalse('sensor' in data)


if __name__ == "__main__":

    unittest.main()
