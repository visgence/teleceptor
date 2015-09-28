"""
    Contributing Authors:
        Bretton Murphy (Visgence, Inc.)
        Evan Salazar (Visgence, Inc.)
        Victor Szczepanski (Visgence, Inc.)
        Jessica Greenling (Visgence, Inc.)

    Resource endpoint for SensorReadings that is used as part of the RESTful api.  Handles
    the creation and retrieval of SensorReadings.

    API:
        Unless otherwise noted api will return data as JSON.


        TODO:
        POST /api/readings/  -  Create a new SensorReading.


Dependencies:
    global:
    cherrypy
    sqlalchemy
    (optional) simplejson

    local:
    teleceptor.models
    teleceptor.sessionManager


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
from whisper import WhisperException
from time import time
from sqlalchemy.orm.exc import NoResultFound
try:
    import simplejson as json
except ImportError:
    import json

import re
import logging

# Local Imports
from teleceptor import SQLDATA,SQLREADTIME, USE_DEBUG, USE_SQL_ALWAYS
from teleceptor.models import SensorReading, DataStream
from teleceptor.sessionManager import sessionScope
from teleceptor import USE_ELASTICSEARCH
if USE_ELASTICSEARCH:
    from teleceptor.elasticsearchUtils import getReadings as esGetReadings
    from teleceptor.elasticsearchUtils import insertReading as esInsert

else:
    from teleceptor.whisperUtils import getReadings, insertReading as whisperInsert


class SensorReadings:
    exposed = True

    if USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

    validFilterArgs = {
        'datastream': '^\d+$',
        'start':      '^\d+$',
        'end':        '^\d+$'
    }

    validOperatorArgs = {
        'condense':    '^true|false$',
        'granularity': '^\d+$'
    }

    @staticmethod
    def condense(readings):
        """
            Takes a array of SensorReading objects and returns back a array of arrays.
            Ex: [ [timestamp1, value1], [timestamp2, value2], ...]

            Returns: Array of SensorReadings values in the denoted format.
         """

        logging.debug("Condensing SensorReading objects to simple [timestamp, value] format: %s", str(readings))
        data = []
        for reading in readings:
            data.append([reading.timestamp, reading.value])

        logging.debug("Made readings list: %s", str(data))
        return data


    def cleanInputs(self, params):
        """
            Checks that the supplied params only contains valid key/value parameters for filtering readings and
            performing any special operations on them.

            Valid Parameters:
                Check file doc for list of valid arguments

            Returns: Dict with clean parameters and None if any parameter was unrecognized or the parameter
                     did not have a correct value format.
        """

        logging.debug("Validating parameters: %s", str(params))

        valueConversions = {
            'null': None
        }

        safeParams = {}
        paramsCopy = params.copy()

        for key, value in paramsCopy.iteritems():

            if key in self.validFilterArgs:
                arg = self.validFilterArgs[key]
            elif key in self.validOperatorArgs:
                arg = self.validOperatorArgs[key]
            else:
                logging.error("Key %s is invalid filter or operator argument.", str(key))
                return None

            if key in self.validFilterArgs and value in valueConversions:
                value = valueConversions[value]
            elif re.match(arg, value) is None:
                return None

            safeParams[key] = value

        logging.debug("Returning safe parameters: %s", str(safeParams))
        return safeParams


    def filterReadings(self, session, params):
        """
        A filter that will give all data received from a sensor in the last hour for high resolution data.

        session : Session
            Refers to the session of the user.
        params : dict
            Contains the start time, end time, and datastream.
        """
        logging.debug("Filtering readings with parameters: %s", str(params))
        filterArgs = {}
        paramsCopy = params.copy()

        query = session.query(SensorReading)
        end = time()
        start = end - 25200
        uuid = '1'

        #Seperate out filter arguments first
        for key, value in paramsCopy.iteritems():
            if key in self.validFilterArgs:
                if key == "start":
                    start = value
                    query = query.filter(SensorReading.timestamp >= value)
                elif key == "end":
                    end = value
                    query = query.filter(SensorReading.timestamp <= value)
                elif key == "datastream":
                    uuid = value
                    filterArgs['datastream'] = value
                else:
                    filterArgs[key] = value

                del params[key]

        if USE_SQL_ALWAYS or (SQLDATA and (int(end) - int(start) < SQLREADTIME)) or USE_ELASTICSEARCH:
            if USE_ELASTICSEARCH:
                logging.debug('Getting Elasticsearch data.')
                readings = esGetReadings(ds=uuid, start=start, end=end)
            else:
                logging.debug("Request time %s less than SQLREADTIME %s. Getting high-resolution data.", str((int(end) - int(start))), str(SQLREADTIME))

                readings = query.filter_by(**filterArgs).order_by('timestamp').all()
                readings = [(reading.timestamp, reading.value) for reading in readings]
        else:
            logging.debug("Getting low resolution data.")
            readings = getReadings(uuid, start, end)

        return readings

    def GET(self, **kwargs):
        """
        GET /api/readings/
            Obtain a list of available SensorReadings.

            Returns:
            {
                'error':   <error str if applicable>
                'readings': [List of readings]
            }

        GET /api/readings/?arg1=value&arg2=value...
            Obtain a list of available SensorReadings filtered by url arguments.

            Valid Arguments:
                NOTE: Unless otherwise specified all filter arguments accept the value null.

                Filter Arguments:
                'stream' (Numeric) - id of DataStream

                Operator Arguments:
                'condense' (String)  - If value is 'true' then the readings returned will
                                        only consist of their values and timestamps.

                                        Format: [ [timestamp1, value1], [timestamp2, value2], ...]


            Returns:
            {
                'error':   <error str if applicable>
                'readings': [List of readings]
            }
        """
        logging.info("GET request to readings.")

        cherrypy.response.headers['Content-Type'] = 'application/json'
        status_code = "200"
        data = {}
        inputs = self.cleanInputs(kwargs)
        logging.debug("Got clean input arguments %s", str(inputs))

        if len(kwargs) > 0 and inputs is None:
            logging.error("Got invalid url parameters %s", str(kwargs))
            data['error'] = "Invalid url parameters"
            status_code = "400"
        else:
            with sessionScope() as s:
                data['readings'] = self.filterReadings(s, inputs)

        cherrypy.response.status = status_code
        logging.info("Finished GET request to readings.")
        return json.dumps(data, indent=4)


    def POST(self):
        """
        Inserts the readings into the database.  Expects a json object in data section of the http request and the object must have a readings key.

        Returns:
            {
                'error':   <error str if applicable>
                'readings': [List of readings]
            }
        """
        logging.info("POST request to readings.")

        cherrypy.response.headers['Content-Type'] = 'application/json'
        data = {}
        status_code = "200"

        try:
            reading_data = json.load(cherrypy.request.body)
        except (ValueError, TypeError):
            logging.error("Request body is not in JSON format.")
            data['error'] = "Bad json"
            status_code = "400"
            cherrypy.response.status = status_code
            return json.dumps(data, indent=4)

        logging.debug("Request body: %s", str(reading_data))

        try:
            data = insertReadings(reading_data['readings'])
        except KeyError:
            logging.error("No readings in request body to insert.")
            data['error'] = "No readings to insert"
            status_code = "400"

        cherrypy.response.status = status_code
        logging.info("Finished POST request to readings.")
        return json.dumps(data, indent=4)

def insertReadings(readings, session=None):
    """
    Tries to insert the readings provided into whisper database, and optionally into the SQL database if SQLDATA is set.
    :param readings: List of reading tuples of the form (datastreamid, value, timestamp)
    :return: A dict with keywords "insertions_attempted", "successfull_insertions", and "failed_insertions"
    """

    logging.debug("Inserting readings.")
    if session is None:
        with sessionScope() as session:
            data = _insertReadings(readings, session)
    else:
        data = _insertReadings(readings, session)

    logging.debug("Stats from attempted insertions: %s", str(data))
    return data

def _insertReadings(readings, session=None):
    """
    Tries to insert the readings provided into whisper database, and optionally into the SQL database if SQLDATA is set.
    :param readings: List of reading tuples of the form (datastreamid, value, timestamp)
    :return: A dict with keywords "insertions_attempted", "successfull_insertions", and "failed_insertions"
    """
    data = {
        "insertions_attempted":    0
        , "successfull_insertions": 0
        , "failed_insertions":      0
    }

    DS = 0
    VAL = 1
    TIME = 2

    for reading in readings:
        logging.debug("Looking at reading %s", str(reading))
        data['insertions_attempted'] += 1

        try:
            streamId = reading[DS]
            rawVal = reading[VAL]
            timestamp = reading[TIME]
        except:
            logging.error("Error separating %s into streamId, rawVal, and timestamp.", str(reading))
            continue

        # If no sensor value then skip this reading
        if rawVal is None or rawVal == "":
            logging.error("Provided rawVal is invalid: %s", str(rawVal))
            continue

        # TODO: handle errors better
        # Get the datastream, if possible
        try:
            # TODO: will need to validate retrieved ds
            logging.debug("Looking up datastream with id %s", str(streamId))
            ds = session.query(DataStream).filter_by(id=streamId).one()
        except NoResultFound:
            logging.error("No datastream with id %s exists.", str(streamId))
            continue

        try:
            logging.debug("Inserting into whisper database with streamId %s, rawVal %s, and timestamp %s", str(streamId), str(rawVal), str(timestamp))
            if USE_ELASTICSEARCH:
                esInsert(streamId, rawVal, timestamp)
            else:
                whisperInsert(streamId, rawVal, timestamp)
            if SQLDATA:
                logging.debug("Creating new sensor reading in SQL database...")
                new_reading = SensorReading()
                new_reading.datastream = streamId
                new_reading.value = rawVal
                new_reading.timestamp = timestamp
                logging.debug("Adding new_reading...")
                session.add(new_reading)
                logging.debug("Added new_reading.")

            data['successfull_insertions'] += 1
        except IOError:
            logging.error("Failed to insert reading into whisper %s", str(streamId))
            continue
        except WhisperException:
            logging.error("Failed to insert reading into whisper %s", str(streamId))
            continue

    data['failed_insertions'] = data['insertions_attempted'] - data['successfull_insertions']
    return data


def reduceData(readings, granularity, reduction_method='mean'):
    """
    Take a a list of tuples containing at [0] a timeStamp and at [1] a raw data value from a sensor reading, and reduce this list to about granularity datapoints, using different methods.

    Keyword arguments:
      readings : list of 2-tuples
        Tuples are (SensorReading.timestamp, SensorReading.sensorValue)
      granularity : int
        The number of datapoints to which to reduce the list. (will not be exact)
      reduction_method : str
        The reduction method.  Can be 'mean', 'sample', etc.
    """

    logging.debug("Reducing data with granularity %s and method %s", str(granularity), str(reduction_method))

    if reduction_method not in reductMethods:
        logging.error("Method %s not a valid reduction method.", str(reduction_method))
        return []

    increment = len(readings)/granularity
    data = []
    for i in range(0, len(readings), increment):
        data.append(reductMethods[reduction_method](readings[i:i+increment]))

    logging.debug("Finished reducing data.")
    return data


def incrementMean(readings):
    """
    Return the timeCenter of the increment and the mean of the readings_values within the increment as a list of 2 values
    """
    logging.debug("Using incrementMean method for reducing data.")
    mid_time = (readings[len(readings)-1][0] + readings[0][0])/2

    # convert to float before taking mean, because float operations are faster than decimal operations
    return [mid_time, sum([float(x[1]) for x in readings])/len(readings)]


reductMethods = {
    'mean': incrementMean
}


