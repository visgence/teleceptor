"""
    station.py

    Authors:
        Bretton Murphy (Visgence, Inc.)
        Victor Szczepanski (Visgence, Inc.)
        Jessica Greenling (Visgence, Inc.)
        Cyrille Gindreau (Visgence, Inc.)

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

import json
import sys
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import logging

from teleceptor.models import DataStream, Path, Sensor
from teleceptor.api import readings, datastreams, messages
from teleceptor.api.sensors import Sensors

class Station(APIView):
    exposed = True

    if settings.DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

    def post(self, request):
        """
        Handles incoming data from a basestation by updating (or creating) sensor information, including metadata, calibration, and datastream. Additionally updates sensor readings, if any.

        :param data: A JSON array formatted string stored in the data section of the HTTP POST request.
        It is not optional, but some elements can be omitted. The JSON object should be a list, even if there is only one element in it.
        The full format is listed in the Notes section.
        "type data: str


        :returns: str -- A JSON object with either a key 'error' or 'newValues'. In the case of 'error', the value is an error string.
                In the case of 'newValues', the value is an object with key/value pairs as "sensorname" : messagelist, where messagelist is all unread,
                unexpired messages for the sensor with name sensorname.
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
        logging.debug("Got POST request to delegation.")

        data = {'info': [], "newValues": {}}

        try:
            readingData = json.dumps(request.data)
            readingData = json.loads(readingData)
            # logging.debug("Got data: %s", readingData)
        except (ValueError, TypeError):
            logging.error("Request data is not JSON: %s", request.data)
            data['error'] = "Bad json"
            data['statusCode'] = "400"
            return Response(data)

        try:
            new_values, sensor_info = update_motes(readingData)
            data['newValues'] = str(new_values)
            data['info'] = str(sensor_info)
        except Exception as e:
            logging.error("%s: %s", str(e.__class__), str(e))
            data['error'] = str(e)
            data['statusCode'] = "400"
            return Response(data)

        logging.debug("Finished POST request to delegation.")
        logging.debug(data)
        return Response(data)


def update_motes(mote_datas):
    # logging.debug("Updating motes %s", str(mote_datas))
    new_values = {}
    updated_sensors = []
    sensor_id = None
    for mote in mote_datas:
        if 'info' not in mote:
            logging.error("Mote %s did not report its info", str(mote))
            continue
        if 'readings' not in mote:
            continue
        if 'uuid' not in mote['info']:
            logging.error("Mote %s did not report its uuid", str(mote))
            continue

        sensor_list = []
        if 'out' in mote['info']:
            sensor_list = mote['info']['out']
        if 'in' in mote['info']:
            sensor_list = sensor_list + mote['info']['in']
        logging.debug("Sensor_list: %s", str(sensor_list))
        sensor_datastream_ids = {}

        for sensor in sensor_list:
            sensor_datastream_ids[mote['info']['uuid'] + sensor['name']] = None
            if 'in' in mote['info'] and sensor in mote['info']['in']:
                sensor['sensor_IOtype'] = True
            else:
                sensor['sensor_IOtype'] = False

            # update data in db
            sensor['name'] = mote['info']['uuid'] + sensor['name']
            sensor['uuid'] = sensor['name']
            sensorUuid = sensor['name']
            sensor_id = sensorUuid
            logging.debug("Updating sensor %s", str(sensor))
            sensor_info = update_sensor_data(sensor)
            logging.debug("Sensor_info after update: %s", str(sensor_info))
            updated_sensors.append(sensor_info)

            # Get message queue for input sensors
            if 'in' in mote['info'] and sensor in mote['info']['in']:
                logging.debug("Getting messages for sensor %s", sensorUuid)
                message_list = messages.getMessages(sensorUuid, by_timestamp=True, unread_only=True)
                logging.debug("Got unread messages: %s", str(message_list))
                new_values[sensor['name']] = message_list

            # get datastream to pass to insertReadings

            logging.debug("Getting datastream.")
            datastream = datastreams.get_datastream_by_sensorid(sensorUuid)
            if not datastream:
                logging.debug("No datastream. Making one for sensor %s", sensorUuid)
                s = Sensor.objects.get(uuid=sensorUuid)
                datastream = DataStream.objects.create(sensor=s, name=sensor['name'], description=sensor['uuid'])
                Path.objects.create(datastream_id=datastream.id, path="/new_sensors")
            logging.debug("Got datastream id %s", str(datastream.id))
            sensor_datastream_ids[sensorUuid] = datastream.id

        # Swap sensorname in readings with datastream id.
        logging.debug("Inserting readings...")

        for reading in mote['readings']:
            reading[0] = sensor_datastream_ids[mote['info']['uuid'] + reading[0]]
        s = Sensor.objects.get(uuid=sensor_id)
        readings.insertReadings(mote['readings'], s)


    return new_values, updated_sensors


def update_sensor_data(sensor_data):
    uuid = sensor_data['uuid']

    # Update sensors (and create if needed)
    try:
        sensor_info = Sensors.updateSensor(data=sensor_data)

    except ObjectDoesNotExist:
        logging.debug('failed to update. Creating')
        timestamp = sensor_data['timestamp']
        del sensor_data['timestamp']
        try:
            sensor = Sensors.createSensor(sensor_data)
        except Exception as e:
            logging.error(f'error creating sensor {e}')
        sensor_data['timestamp'] = timestamp
    else:
        sensor = Sensor.objects.get(uuid=uuid)

    coefficients = [1, 0]
    timestamp = 0
    if 'scale' in sensor_data and 'calibration_timestamp' in sensor_data:
        coefficients = sensor_data['scale']
        timestamp = sensor_data.calibration_timestamp
    else:
        if 'calibration_timestamp' not in sensor_data or 'scale' not in sensor_data:
            coefficients = sensor.last_calibration.coefficients

        elif sensor_data['calibration_timestamp'] < sensor['last_calibration']['timestamp']:
            coefficients = sensor.last_calibration.coefficients
        else:
            coefficients = sensor_data.scale

    logging.debug("Got sensor %s", str(sensor))
    logging.debug("Updating calibration...")

    sensor_info = Sensors.updateCalibration(sensor, coefficients, timestamp)
    logging.debug("Updated calibration")

    return sensor_info
