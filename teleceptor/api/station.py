"""
    station.py

    Authors:
        Bretton Murphy (Visgence, Inc.)
        Victor Szczepanski (Visgence, Inc.)
        Jessica Greenling (Visgence, Inc.)

    Resource endpoint for accepting POST requests that is used as part of the RESTful api.
    Handles the delegation of tasks to other api modules. Specifically, this api should be used for posting new sensor readings with sensor readings.
    With all sensor information in the input data, this module will create or update sensors as needed, along with updating metadata.

    This module is the recommended way of updating sensor information and readings.

    API:
        Unless otherwise noted api will return data as JSON.

        POST /api/station/
            Update sensor information (and create if necessary) and put new sensor readings by calling respective api modules.

            In the HTTP POST request, the data field must be a JSON array of the following form:
            [
                { "info":
                    {


                    },
                  "readings":
                    [

                    ]
                },
                ...
            ]
"""

# System Imports
import cherrypy
from time import time
from sqlalchemy.orm.exc import NoResultFound
try:
    import simplejson as json
except ImportError:
    import json


import logging

# Local Imports
from teleceptor.models import DataStream, Sensor, Message, MessageQueue, StreamPath
from teleceptor.sessionManager import sessionScope
from teleceptor.api.sensors import Sensors
from teleceptor.api.datastreams import DataStreams
from teleceptor.api import readings, datastreams, sensors, messages
from teleceptor.api.readings import SensorReadings
from teleceptor import USE_DEBUG


class Station:
    exposed = True

    if USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

    def POST(self):
        """
        Handles incoming data from a basestation by updating (or creating) sensor information, including metadata, calibration, and datastream. Additionally updates sensor readings, if any.

        :param data: A JSON array formatted string stored in the data section of the HTTP POST request. It is not optional, but some elements can be omitted. The JSON object should be a list, even if there is only one element in it. The full format is listed in the Notes section.
        "type data: str


        :returns: str -- A JSON object with either a key 'error' or 'newValues'. In the case of 'error', the value is an error string.
                In the case of 'newValues', the value is an object with key/value pairs as "sensorname" : messagelist, where messagelist is all unread, unexpired messages for the sensor with name sensorname.
                The receiving function must determine how to handle the messages (e.g. to consider only the newest message, or to use all messages.)

        .. seealso::
            models.Message : The model that defines a message, which is returned in `data`.
            models.Sensor : The model that defines a sensor, whose columns are valid fields in the "info" section of the input JSON string.

        .. note::
            The JSON format for the input `data` string follows. Note that required fields are marked with a *.
            The JSON object should be an array, with elements being a object with two keys: "info" and "readings".
            "info" is always required, but "readings" is optional. See `models.Sensor` for all valid keys in the "info" object.
            Note that, while `scale` is not required for each sensor, this module will create a new `Calibration` with coefficients [1,0] for any sensors without a `scale` field.
            The `in` and `out` sections are not optional, but may have empty arrays.
            An error will be thrown, however, if there are readings whose `sensorname` does not match the `name` of either an `in` or `out` sensor.

        Full Format:
            [
                {
                    "info":
                        {
                            *"uuid": ".....",
                            "name": ".....",
                            "rev" : ".....",
                            ...
                            *"in"  : [
                                        {
                                            *"name"  : "in1",
                                            "scale" : [1,2,3,...],
                                            ...
                                        },
                                        {
                                            *"name"  : "in2",
                                            "scale" : [1,2,3,...],
                                            ...
                                        }
                                    ]
                            *"out" : [
                                        {
                                            *"name"  : "out1",
                                            "scale" : [1,2,3,...],
                                            ...
                                        },
                                        {
                                            *"name"  : "out2",
                                            "scale" : [1,2,3,...],
                                            ...
                                        }
                                    ]


                        }
                    "readings":
                        [
                            [*sensorname, *val, *time],
                            [*sensorname, *val, *time],
                            ...
                        ]
                }

            ]
        """
        logging.info("Got POST request to delegation.")

        cherrypy.response.headers['Content-Type'] = 'application/json'
        data = {'info': [], "newValues": {}}

        statusCode = "200"

        try:
            readingData = json.load(cherrypy.request.body)
            logging.info("Got data: %s", readingData)
        except (ValueError, TypeError):
            logging.error("Request data is not JSON: %s", cherrypy.request.body)
            data['error'] = "Bad json"
            statusCode = "400"
            cherrypy.response.status = statusCode
            return json.dumps(data, indent=4)

        try:
            new_values, sensor_info = update_motes(readingData)

            data['newValues'] = new_values
            data['info'] = sensor_info
        except Exception as e:
            logging.error("%s: %s", str(e.__class__), e.message)
            data['error'] = e.message
            statusCode = "400"

        logging.debug("Finished POST request to delegation.")
        cherrypy.response.status = statusCode
        return json.dumps(data, indent=4)


def update_motes(mote_datas=[]):
    logging.info("Updating motes %s", str(mote_datas))
    new_values = {}
    for mote in mote_datas:
        if 'info' not in mote:
            logging.error("Mote %s did not report its info", str(mote))
            continue

        sensor_list = []
        if 'out' in mote['info']:
            sensor_list = mote['info']['out']
        if 'in' in mote['info']:
            sensor_list = sensor_list + mote['info']['in']
        logging.info("Sensor_list: %s", str(sensor_list))
        sensor_datastream_ids = {}
        for sensor in sensor_list:
            sensor_datastream_ids[mote['info']['uuid'] + sensor['name']] = None

        updated_sensors = []
        with sessionScope() as session:
            for sensor in sensor_list:

                if 'in' in mote['info'] and sensor in mote['info']['in']:
                    sensor['sensor_IOtype'] = True
                else:
                    sensor['sensor_IOtype'] = False

                # update data in db
                sensor['name'] = mote['info']['uuid'] + sensor['name']
                sensor['uuid'] = sensor['name']
                sensorUuid = sensor['name']
                logging.info("Updating sensor %s", str(sensor))
                sensor_info = update_sensor_data(sensor, session)
                logging.info("Sensor_info after update: %s", str(sensor_info))
                updated_sensors.append(sensor_info)

                # Get message queue for input sensors
                if 'in' in mote['info'] and sensor in mote['info']['in']:
                    logging.info("Getting messages for sensor %s", sensorUuid)
                    message_list = messages.getMessages(sensorUuid, by_timestamp=True, unread_only=True)
                    logging.info("Got unread messages: %s", str(message_list))
                    new_values[sensor['name']] = message_list

                # get datastream to pass to insertReadings
                try:
                    logging.info("Getting datastream.")
                    datastream = datastreams.get_datastream_by_sensorid(sensorUuid, session)
                except NoResultFound:
                    logging.info("No datastream. Making one for sensor %s", sensorUuid)
                    datastream = DataStream(sensor=sensorUuid)
                    DataStreams.createDatastream(session, datastream)
                    path = StreamPath(datastream=datastream)

                    datastream = datastream.toDict()
                logging.info("Got datastream id %s", str(datastream['id']))
                sensor_datastream_ids[sensorUuid] = datastream['id']

            # Swap sensorname in readings with datastream id.
            logging.info("Inserting readings...")

            for reading in mote['readings']:
                reading[0] = sensor_datastream_ids[mote['info']['uuid'] + reading[0]]

            readings.insertReadings(mote['readings'], session=session)
    return new_values, updated_sensors


def update_sensor_data(sensor_data=None, session=None):
    uuid = sensor_data['uuid']

    if 'scale' not in sensor_data:
        logging.debug("Sensor did not report a scaling function. Using identity function.")
        coefficients = json.dumps([1, 0])
    else:
        coefficients = json.dumps(sensor_data['scale'])
        del sensor_data['scale']

    # TODO: Put code in other function
    if session is None:
        with sessionScope() as session:
            # Update sensors (and create if needed)
            try:
                sensor_info = Sensors.updateSensor(sensor_id=uuid, data=sensor_data, session=session)
            except NoResultFound:
                timestamp = sensor_data['timestamp']
                del sensor_data['timestamp']

                sensor = Sensor(**sensor_data)
                Sensors.createSensor(sensor=sensor, session=session)

                sensor_data['timestamp'] = timestamp

            sensor = sensors.getSensor(uuid, session=session)
            logging.info("Got sensor %s", str(sensor))
            logging.debug("Updating calibration...")
            sensor_info = Sensors.updateCalibration(sensor, coefficients, sensor_data['timestamp'], session=session)
            logging.info("Updated calibration.")
    else:
        # Update sensors (and create if needed)
        try:
            sensor_info = Sensors.updateSensor(sensor_id=uuid, data=sensor_data, session=session)
        except NoResultFound:
            timestamp = sensor_data['timestamp']
            del sensor_data['timestamp']

            sensor = Sensor(**sensor_data)
            Sensors.createSensor(sensor, session)

            sensor_data['timestamp'] = timestamp

        sensor = sensors.getSensor(uuid, session=session)
        logging.info("Got sensor %s", str(sensor))
        logging.debug("Updating calibration...")
        sensor_info = Sensors.updateCalibration(sensor, coefficients, sensor_data['timestamp'], session=session)
        logging.info("Updated calibration")

    return sensor_info
