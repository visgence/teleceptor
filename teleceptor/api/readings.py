"""
    readings.py

    Authors: Bretton Murphy
             Evan Salazar
             Victor Szczepanski
             Jessica Greenling
             Cyrille Gindreau

    Resource endpoint for SensorReadings that is used as part of the RESTful api.  Handles
    the creation and retrieval of SensorReadings.

    API:
        Unless otherwise noted api will return data as JSON.

        TODO:
        POST /api/readings/  -  Create a new SensorReading.

"""

from rest_framework.views import APIView
import logging
import json
import re
import time

from teleceptor.models import DataStream, SensorReading, Sensor
from django.conf import settings

class SensorReadings(APIView):
    exposed = True
    if settings.DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)
    validFilterArgs = {
        'datastream': '^\d+$',
        'start':      '^\d+$',
        'end':        '^\d+$',
        'points':     '^\d+$',
        'source':    '^SQL|ElasticSearch$'
    }
    validOperatorArgs = {
        'condense':    '^true|false$',
        'granularity': '^\d+$'
    }

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

            Args:
                .. note:: Unless otherwise specified all filter arguments accept the value null.

                Filter Arguments:
                'stream' (Numeric) - id of DataStream
                'source' (String) - one of SQL or ElasticSearch. Selects data source to pull from (overrides any server-side source selection)

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
        logging.debug("GET request to readings.")
        data = {}
        inputs = self.cleanInputs(kwargs)
        logging.debug("Got clean input arguments %s", str(inputs))
        if len(kwargs) > 0 and inputs is None:
            logging.error("Got invalid url parameters %s", str(kwargs))
            data['error'] = "Invalid url parameters"
        else:
            try:
                data['readings'], data['source'] = self.filterReadings(inputs)
            except ValueError as e:
                data['error'] = str(e)

        logging.debug("Finished GET request to readings.")
        return json.dumps(data, indent=4).encode('utf-8')

    def POST(self, request):
        """
        Inserts the readings into the database.  Expects a json object in data section of the http request and the object must have a readings key.

        :returns: Dictionary --
            'error':   <error str if applicable>
            'readings': [List of readings]
        """
        logging.debug("POST request to readings.")

        try:
            reading_data = json.dumps(request.data)
            reading_data = json.loads(reading_data)
        except (ValueError, TypeError):
            logging.error("Request body is not in JSON format.")
            data['error'] = "Bad json"
            return json.dumps(data, indent=4).encode('utf-8')

        logging.debug("Request body: %s", str(reading_data))

        try:
            data = insertReadings(reading_data['readings'])
        except KeyError:
            logging.error("No readings in request body to insert.")
            data['error'] = "No readings to insert"

        logging.debug("Finished POST request to readings.")
        return json.dumps(data, indent=4).encode('utf-8')

    def DELETE(self, datastream_id=None):
        """
        Deletes all sensor readings for a given datastream.

        :returns: A JSON object with an 'error' key if an error occured or 'readings' key if delete was successful.
        """
        logging.debug("DELETE request to readings with datastream_id {}".format(datastream_id))

        if datastream_id is not None:
            data = {}
            try:
                deleted_readings = deleteReadingsByDatastream(datastream_id)
                data['readings'] = deleted_readings
            except Exception as e:
                error_string = "Unexpected error while deleting readings by datastream: {}".format(e)
                logging.error(error_string)
                data['error'] = error_string

        logging.debug("Finished DELETE request to datastreams.")
        return json.dumps(data, indent=4).encode('utf-8')

    @staticmethod
    def condense(readings):
        """
        Takes an array of SensorReading objects and returns back a array of arrays.
        Ex: [ [timestamp1, value1], [timestamp2, value2], ...]

        :returns: Array -- SensorReadings values in the denoted format.
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

        :param params: Check file doc for list of valid arguments

        :returns: Dictionary -- Dict with clean parameters and None if any parameter was unrecognized or the parameter
            did not have a correct value format.
        """
        logging.debug("Validating parameters: %s", str(params))
        valueConversions = {
            'null': None
        }
        safeParams = {}
        paramsCopy = params.copy()
        for key, value in paramsCopy.items():

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

    def filterReadings(self, params):
        """
        A filter that will give all data received from a sensor in the last hour for high resolution data.

        :param session: Refers to the session of the user.
        :type session: Session
        :param params: Contains the start time, end time, and datastream.
        :type params: dictionary
        """
        logging.debug("Filtering readings with parameters: %s", str(params))
        filterArgs = {}
        paramsCopy = params.copy()

        end = time()
        readings = SensorReading.objects.filter(datastream=paramsCopy['datastream'], timestamp__gt=end).order_by('timestamp')

        readings = [(reading.timestamp, reading.value) for reading in readings]

        return readings


def insertReadings(readings, s):
    """
    Tries to insert the readings provided into database, and optionally into the SQL database if SQLDATA is set.

    :param readings: List of reading tuples of the form (datastreamid, value, timestamp)

    :returns: Dictionary -- A dict with keywords "insertions_attempted", "successfull_insertions", and "failed_insertions"

    .. todo::
        handle errors better
        Get the datastream, if possible
    """
    data = {
        "insertions_attempted": 0,
        "successfull_insertions": 0,
        "failed_insertions": 0
    }
    DS = 0
    VAL = 1
    TIME = 2
    for reading in readings:
        # logging.debug("Looking at reading %s", str(reading))
        data['insertions_attempted'] += 1
        try:
            streamId = reading[DS]
            rawVal = reading[VAL]
            timestamp = reading[TIME]
        except Exception as e:
            logging.error("Error separating %s into streamId, rawVal, and timestamp.", str(reading))
            logging.debug(e)
            continue
        # If no sensor value then skip this reading
        if rawVal is None or rawVal == "":
            logging.error("Provided rawVal is invalid: %s", str(rawVal))
            continue
        # TODO: handle errors better
        # Get the datastream, if possible

        # logging.debug("Looking up datastream with id %s", str(streamId))
        ds = DataStream.objects.get(id=streamId)
        if not ds:
            logging.error("No datastream with id %s exists.", str(streamId))
            continue
        try:
            # logging.debug("Inserting into database with streamId %s, rawVal %s, and timestamp %s", str(streamId), str(rawVal), str(timestamp))

            # logging.debug("Creating new sensor reading in SQL database...")
            SensorReading.objects.create(datastream=ds, value=rawVal, timestamp=timestamp, sensor=s)
            # logging.debug("Added new_reading.")

            data['successfull_insertions'] += 1
        except IOError:
            logging.error("Failed to insert reading into database %s", str(streamId))
            continue

    data['failed_insertions'] = data['insertions_attempted'] - data['successfull_insertions']
    return data

def deleteReadingsByDatastream(datastream_id):
    """
    Deletes all readings with the datastream id `datastream_id`.
    :param datastream_id: id of the datastream to delete all of the readings for
    :type datastream_id: int
    :param session: Existing context into a sqlalchemy database session. Can be created by a call to `sessionScope()`
    :type session: context object from `sessionScope()`
    :returns: A list of the deleted readings

    .. seealso::
        `models.DataStream`
        `models.SensorReading`
        `readings.DELETE`
    """
    try:
        readings = SensorReading.objects.filter(datastream=datastream_id)
    except Exception as e:
        logging.debug("No readings found to delete for datastream {}".format(datastream_id))
        return []
    else:
        logging.debug("Deleting sensor readings for datastream {}".format(datastream_id))
        readings.delete()
        return readings
    return []
