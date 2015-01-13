"""
    Contributing Authors:
        Bretton Murphy (Visgence, Inc.)
        Victor Szczepanski (Visgence, Inc.)
        Jessica Greenling (Visgence, Inc.)


    Resource endpoint for accepting POST requests that is used as part of the RESTful api.
    Handles the delegation of tasks to other api modules. Specifically, this api should be used for posting new sensor readings with sensor readings.
    With all sensor information in the input data, this module will create or update sensors as needed, along with updating metadata.

    This module is the recommended way of updating sensor information and readings.

    API:
        Unless otherwise noted api will return data as JSON.

        POST /api/delegation/
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

Dependencies:
    global:

    cherrypy
    sqlalchemy
    (optional) simplejson

    local:
    teleceptor.models
    teleceptor.sessionManager
    teleceptor.api.sensors
    teleceptor.api.datastreams
    teleceptor.api.readings




    (c) 2014 Visgence, Inc.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>
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
from teleceptor.models import DataStream, Sensor, Message
from teleceptor.sessionManager import sessionScope
from teleceptor.api.sensors import Sensors
from teleceptor.api.datastreams import DataStreams
from teleceptor.api.readings import SensorReadings
from teleceptor import USE_DEBUG

class Delegation:
    exposed = True

    if USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',level=logging.INFO)

    def POST(self):
        """ Handles incoming data from a basestation by updating (or creating) sensor information, including metadata, calibration, and datastream. Additionally updates sensor readings, if any.

        Parameters
        ----------
        data : str
            A JSON array formatted string stored in the data section of the HTTP POST request. It is not optional, but some elements can be omitted. The JSON object should be a list, even if there is only one element in it. The full format is listed in the Notes section.

        Returns
        -------
        data : str
            A JSON object with either a key 'error' or 'newValues'. In the case of 'error', the value is an error string. In the case of 'newValues', the value is an object with key/value pairs as "sensorname" : messagelist, where messagelist is all unread, unexpired messages for the sensor with name sensorname. The receiving function must determine how to handle the messages (e.g. to consider only the newest message, or to use all messages.)

        See Also
        --------
        models.Message : The model that defines a message, which is returned in `data`.
        models.Sensor : The model that defines a sensor, whose columns are valid fields in the "info" section of the input JSON string.


        Notes
        -----
        The JSON format for the input `data` string follows. Note that required fields are marked with a *.
        The JSON object should be an array, with elements being a object with two keys: "info" and "readings". "info" is always required, but "readings" is optional. See `models.Sensor` for all valid keys in the "info" object.
        Note that, while `scale` is not required for each sensor, this module will create a new `Calibration` with coefficients [1,0] for any sensors without a `scale` field.
        The `in` and `out` sections are not optional, but may have empty arrays. An error will be thrown, however, if there are readings whose `sensorname` does not match the `name` of either an `in` or `out` sensor.

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

        cherrypy.response.headers['Content-Type'] = 'application/json'
        data = {'info':[],"newValues":{}}


        try:
            readingData = json.load(cherrypy.request.body)
            logging.debug("Got data: %s", readingData)
        except (ValueError, TypeError):
            logging.error("Request data is not JSON: %s", cherrypy.request.body)
            data['error'] = "Bad json"
            return json.dumps(data, indent=4)


        foundds = {}
        for mote in readingData:

            if 'info' not in mote:
                logging.error("Mote %s did not report its info", str(mote))
                data['error'] = "No info for this mote"
            logging.debug("mote: %s", str(mote))

            sensors = []
            if 'out' in mote['info']:
                sensors = mote['info']['out']
            if 'in' in mote['info']:
                sensors = sensors + mote['info']['in']

            logging.debug("Motes in request: %s", str(sensors))

            for sensor in sensors:
                sensorUuid = mote['info']['uuid']+sensor['name']

                coefficients = None
                if 'scale' not in sensor:
                    logging.debug("Sensor did not report a scaling function. Using identity function.")
                    coefficients = json.dumps([1, 0])
                else:
                    coefficients = json.dumps(sensor['scale'])
                    del sensor['scale']
                #check if the sensor exists
                try:
                    with sessionScope() as s:
                        foundSensor = s.query(Sensor).filter_by(uuid=sensorUuid).one()
                        logging.debug("Found sensor in database.")

                        #update metadata in sensor
                        foundSensor.meta_data = sensor['meta_data']

                        #get any new messages for input sensors
                        if 'in' in mote['info'] and sensor in mote['info']['in']:
                            if foundSensor.message_queue is not None:
                                msgList = []
                                #only send messages with a valid timestamp and haven't expired
                                msgs = s.query(Message).\
                                filter(Message.message_queue_id==foundSensor.message_queue.id, Message.timeout >= time(), Message.read != True)
                                #mark each unread message as read
                                for msg in msgs:
                                    msg.read = True
                                    msgList.append(msg.to_dict())

                                logging.debug("Got unread messages: %s", str(msgList))
                                data['newValues'][sensor['name']] = msgList



                except NoResultFound:
                    logging.debug("Sensor with uuid %s not found. Creating new entry in database.", str(sensorUuid))
                    #no sensor, so make one and try to find a datastream for it to claim (using the user+name combo)

                    sensor['uuid'] = sensorUuid
                    if 'in' in mote['info'] and sensor in mote['info']['in']:
                        sensor['sensor_IOtype'] = True
                    else:
                        sensor['sensor_IOtype'] = False

                    timestamp = sensor['timestamp']
                    del sensor['timestamp']

                    newSensor = Sensor(**sensor)

                    with sessionScope() as s:
                        Sensors.createSensor(s, newSensor)
                    logging.debug("Added sensor to database.")

                    #restore timestamp
                    sensor['timestamp'] = timestamp
                with sessionScope() as s:
                    newSensor = s.query(Sensor).filter_by(uuid=sensorUuid).one()

                    logging.debug("Updating calibration...")
                    Sensors.updateCalibration(s, newSensor, coefficients, sensor['timestamp'])
                    data['info'].append(json.dumps(newSensor.toDict()))

                ds = None
                #check if the data stream exists
                try:
                    with sessionScope() as s:
                        ds = s.query(DataStream).filter_by(sensor=sensorUuid).one()

                        logging.debug("Found datastream associated with sensor.")
                        foundds[sensor['name']] = ds.id
                #no data stream, so we need to make one
                except NoResultFound:
                    logging.debug("Sensor has no datastream. Creating one...")
                    ds = DataStream(sensor=sensorUuid)

                    with sessionScope() as s:
                        print ds.toDict()
                        DataStreams.createDatastream(s, ds)
                        foundds[sensor['name']] = ds.id

                    logging.debug("Created datastream.")


            with sessionScope() as s:

                for reading in mote['readings']:
                    sensorUuid = mote['info']['uuid']+reading[0]
                    sensor = s.query(Sensor).filter_by(uuid=sensorUuid).one()
                    sensor.last_value = reading[1]
                    reading[0] = foundds[reading[0]]
                    print reading

            with sessionScope() as s:
                logging.debug("Inserting new readings from mote into database: %s", str(mote['readings']))

                SensorReadings.insertReadings(s, mote['readings'])

        logging.debug("Finished POST request to delegation.")
        return json.dumps(data, indent=4)



