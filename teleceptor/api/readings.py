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
from time import time
from sqlalchemy.orm.exc import NoResultFound
try:
    import simplejson as json
except ImportError:
    import json

import re

# Local Imports
from teleceptor import SQLDATA,SQLREADTIME
from teleceptor.models import SensorReading, DataStream
from teleceptor.sessionManager import sessionScope
from teleceptor.whisperUtils import getReadings, insertReading as whisperInsert


class SensorReadings:
    exposed = True

    validFilterArgs = {
         'datastream': '^\d+$'
        ,'start':      '^\d+$'
        ,'end':        '^\d+$'
    }

    validOperatorArgs = {
         'condense':    '^true|false$'
        ,'granularity': '^\d+$'
    }

    @staticmethod
    def condense(readings):
        """
            Takes a array of SensorReading objects and returns back a array of arrays.
            Ex: [ [timestamp1, value1], [timestamp2, value2], ...]

            Returns: Array of SensorReadings values in the denoted format.
         """

        data = []
        for reading in readings:
            data.append([reading.timestamp, reading.value])

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
                return None

            if key in self.validFilterArgs and value in valueConversions:
                value = valueConversions[value]
            elif re.match(arg, value) is None:
                return None

            safeParams[key] = value

        return safeParams


    def filterReadings(self, session, params):
        """
        A filter that will give all data received from a sensor in the last hour for high resolution data.

        session : Session
            Refers to the session of the user.
        params : dict
            Contains the start time, end time, and datastream.
        """
        filterArgs = {}
        paramsCopy = params.copy()

        query = session.query(SensorReading)
        end = time()
        start = end - 25200
        uuid = '1'

        #Seperate out filter arguments first
        for key, value in paramsCopy.iteritems():
            if  key in self.validFilterArgs:
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
                    #pass

                del params[key]

        if SQLDATA and (int(end) - int(start) < SQLREADTIME):
            print "\nTIME LESS THAN " + str(SQLREADTIME)
            readings = query.filter_by(**filterArgs).order_by('timestamp').all()
            readings = [(reading.timestamp,reading.value) for reading in readings]
        else:
            readings = getReadings(uuid, start, end)
        encodeReady = False

        return readings

    @staticmethod
    def insertReadings(session, readings):

        data = {
            "insertions_attempted":    0
            ,"successfull_insertions": 0
            ,"failed_insertions":      0
        }

        DS   = 0
        VAL  = 1
        TIME = 2

        for reading in readings:
            data['insertions_attempted'] += 1

            streamId  = None
            rawVal    = None
            timestamp = None

            try:
                streamId  = reading[DS]
                rawVal    = reading[VAL]
                timestamp = reading[TIME]
            except:
                pass

            #If no sensor value then skip this reading
            if(rawVal is None or rawVal == ""):
                continue

            #TODO: handle errors better
            # Get the datastream, if possible
            try:
                #TODO: will need to validate retrieved ds
                ds = session.query(DataStream).filter_by(id = streamId).one()
            except NoResultFound:
                continue

            try:
                whisperInsert(streamId, rawVal, timestamp)
                if SQLDATA:
                    newReading = SensorReading()
                    newReading.datastream = streamId
                    newReading.value = rawVal
                    newReading.timestamp = timestamp
                    session.add(newReading)

                data['successfull_insertions'] += 1
            except IOError:
                print "Failed to insert reading into whisper %s" % str(streamId)
                continue

        data['failed_insertions'] = data['insertions_attempted'] - data['successfull_insertions']
        return data


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

            Valid Aruments:
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
        cherrypy.response.headers['Content-Type'] = 'application/json'
        data = {}
        inputs = self.cleanInputs(kwargs)

        if len(kwargs) > 0 and inputs is None:
            data['error'] = "Invalid url parameters"
        else:
            with sessionScope() as s:
                data['readings'] = self.filterReadings(s, inputs)

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
        cherrypy.response.headers['Content-Type'] = 'application/json'
        data = {}

        try:
            readingData = json.load(cherrypy.request.body)
        except (ValueError, TypeError):
            data['error'] = "Bad json"
            return json.dumps(data, indent=4)

        if 'readings' not in readingData:
            data['error'] = "No readings to insert"

        with sessionScope() as s:
            data = insertReadings(s, readingData['readings'])

        return json.dumps(data, indent=4)



def reduceData(readings, granularity, red = 'mean'):
    """
    Take a a list of tuples containing at [0] a timeStamp and at [1] a raw data value from a sensor reading, and reduce this list to about granularity datapoints, using different methods.

    Keyword arguments:
      readings : list of 2-tuples
        Tuples are (SensorReading.timestamp, SensorReading.sensorValue)
      granularity : int
        The number of datapoints to which to reduce the list. (will not be exact)
      red : str
        The reduction method.  Can be 'mean', 'sample', etc.
    """

    increment = len(readings)/granularity
    data = []
    for i in range(0, len(readings), increment):
        data.append(reductMethods[red](readings[i:i+increment]))

    return data


def incrementMean(readings):
    """
    Return the timeCenter of the increment and the mean of the readings_values within the increment as a list of 2 values
    """
    mid_time = (readings[len(readings)-1][0] + readings[0][0])/2

    # convert to float before taking mean, because float operations are faster than decimal operations
    return [mid_time, sum([float(x[1]) for x in readings])/len(readings)]


reductMethods = {
    'mean': incrementMean
}


