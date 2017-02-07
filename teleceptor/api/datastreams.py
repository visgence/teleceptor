"""
datastreams.py

Authors: Victor Szczepanski
         Bretton Murphy
         Jessica Greenling

 Resource endpoint for DataStreams that is used as part of the RESTful api.  Handles
    the creation, updating, and retrieval of Datastreams.

    API:
        Unless otherwise noted api will return data as JSON.

        GET /api/datastreams/
            Obtain a list of available Datastreams.

            Returns:
            {
                'error':   <error str if applicable>
                'datastreams': [List of datastreams]
            }

        GET /api/datastreams/?arg1=value&arg2=value...
            Obtain a list of available Datastreams filtered by url arguments.

            Valid Aruments:
                NOTE: Unless otherwise specified all arguments accept the value null.

                'sensor' (Alphanumeric) - uuid of the Sensor

            Returns:
            {
                'error':   <error str if applicable>
                'datastreams': [List of datastreams]
            }

        GET /api/datastreams/<stream_id>/
            Obtain a single Datastreams for the given stream_id.

            Returns:
            {
                'error':   <error str if applicable>
                'stream':  A single stream
            }

        PUT /api/datastreams/<stream_id>/
            Updates stream with valid id

        TODO:
        POST /api/datastreams/  -  Create a new Datastreams.
"""

# System Imports
import cherrypy
import json
from sqlalchemy.orm.exc import NoResultFound
import re
import logging

# Local Imports
from teleceptor.models import DataStream, Sensor, Path
from teleceptor.sessionManager import sessionScope
from teleceptor import USE_DEBUG, USE_ELASTICSEARCH
from teleceptor.auth import require
if USE_ELASTICSEARCH:
    from teleceptor import elasticsearchUtils as esUtils


class DataStreams:
    exposed = True

    if USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

    def GET(self, stream_id=None, *args, **filter_arguments):
        """
        Gets a specified datastream or list of datastreams filtered by keyword arguments.

        :param stream_id: The `stream_id` of the datastream to get or None to select datastreams based on filter arguments in `args` and `filter_arguments`.
        :type stream_id: int, optional

        :param args: Unused list of arguments
        :type args: list, optional

        :param filter_arguments: Keyword arguments to filter the datastream query.
        :type filter_arguments: dictionary, optional

        :returns:
            data : dictionary
                Contains an 'error' key if an error occurred with the value being a string containing the error message. Contains a 'datastreams' key if multiple datastreams are selected with the value being a list of datastreams. Contains a 'stream' key if `stream_id` selects a unique datastream with the value being the selected stream.
                `data` is returned in the `response.text` section of the HTTP response, if this function is called through the cherrypy API.

        .. seealso::
            cleanInputs : Checks that filter_arguments only contains valid parameters for filtering datastreams.


        GET /api/datastreams/
            Obtain a list of available Datastreams.

            :returns:
                'error':   <error str if applicable>
                'datastreams': [List of datastreams]


        GET /api/datastreams/?arg1=value&arg2=value...
            Obtain a list of available Datastreams filtered by url arguments.

            Valid Aruments:
                ..note:: Unless otherwise specified all arguments accept the value null.

                'sensor' (Alphanumeric) - uuid of the Sensor

            :returns:
                'error':   <error str if applicable>
                'datastreams': [List of datastreams]

        GET /api/datastreams/<stream_id>/
            Obtain a single Datastreams for the given stream_id.

            :returns:
                'error':   <error str if applicable>
                'stream':  A single stream
        """
        logging.info("GET request to datastreams.")

        cherrypy.response.headers['Content-Type'] = 'application/json'
        data = {}

        statusCode = "200"

        if stream_id is not None:
            logging.debug("Request for datastream with id %s", str(stream_id))
            with sessionScope() as s:
                try:
                    stream = s.query(DataStream).filter_by(id=stream_id).one()
                except NoResultFound:
                    logging.error("Stream with id %s does not exist.", str(stream_id))
                    data['error'] = "Stream with id %s doesn't exist." % stream_id
                    statusCode = "400"
                else:
                    logging.info("Found stream with id %s: %s", str(stream_id), str(stream.toDict()))
                    data['stream'] = stream.toDict()
                    try:
                        path = s.query(StreamPath).filter_by(datastream=stream_id)
                    except NoResultFound:
                        logging.error("There is no path for stream with id %s", str(stream_id))
                    else:
                        logging.info("Found path: %s", str(stream_id), str(path.toDict()))
                        data['path'] = path.toDict()
        else:
            logging.debug("Request for all datastreams with parameters %s", str(filter_arguments))
            inputs = clean_inputs(filter_arguments)
            if len(filter_arguments) > 0 and inputs is None:
                logging.error("Provided url parameters are invalid: %s", str(filter_arguments))
                data['error'] = "Invalid url parameters"
                statusCode = "400"
            else:
                logging.debug("Parameters are valid.")
                with sessionScope() as s:
                    datastreams = s.query(DataStream).filter_by(**inputs).all()
                    data['datastreams'] = [i.toDict() for i in datastreams]

        cherrypy.response.status = statusCode
        return json.dumps(data, indent=4)

    def POST(self, stream_id=None):
        # TODO: Implement this for datastream creation
        logging.error("POST request to datastreams. This API end point is not implemented.")
        pass

    @require()
    def PUT(self, stream_id):
        """
        Updates the stream with uuid `stream_id`.

        Using the JSON formatted data in the HTTP request body, updates the datastream information in the database. Valid key/value pairs correspond to the columns in `models.DataStreams`.

        :param stream_id: The UUID of a datastream
        :type stream_id: str

        :returns: Dictionary -- A JSON object with an 'error' key if an error occured or 'datastream' key if update succeeded. If 'error', the value is an error string. If 'datastream', the value is a JSON object representing the updated datastream in the database.

        .. seealso:: `models.DataStream`

        """
        logging.info("PUT request to datastreams. ")
        returnData = {}
        statusCode = "200"
        cherrypy.response.headers['Content-Type'] = 'application/json'
        try:
            data = json.loads(cherrypy.request.body.read())
        except ValueError:
            # no json object to decode, just use an empty dictionary
            data = {}

        logging.debug("Request body: %s", data)

        try:
            stream = DataStreams.updateStream(stream_id, data)
            returnData['stream'] = stream
        except NoResultFound:
            logging.error("Stream with id %s doesn't exist.", str(stream_id))
            returnData['error'] = "Stream with id %s doesn't exist." % stream_id
            statusCode = "400"

        cherrypy.response.status = statusCode

        logging.debug("Finished PUT request to datastream.")
        return json.dumps(returnData, indent=4)

    def DELETE(self, stream_id):
        """
        Deletes the DataStream with id `stream_id`.

        This function cannot be undone, but the stream may be created again
        in a separate transaction.

        :param stream_id: The id of a DataStream
        :type stream_id: int

        :returns:
            A JSON object with an 'error' key if an error occured or 'datastream' key if update succeeded. If 'error', the value is an error string. If 'datastream', the value is a JSON object representing the deleted DataStream in the database.

        .. seealso::
            `models.DataStream`
        """
        logging.info("DELETE request to datastreams for stream with id {}".format(stream_id))

        cherrypy.response.headers['Content-Type'] = 'application/json'
        data = {}

        statusCode = "200"

        with sessionScope() as s:
            try:
                deletedStream = deleteDatastream(s, stream_id)

                if deletedStream is None:
                    data['error'] = "Datastream with id {} could not be deleted.".format(stream_id)
                    statusCode = "400"
                else:
                    data['datastream'] = deletedStream
            except Exception as e:
                logging.exception("Unexpected error while deleting datastream {}".format(stream_id))
                data['error'] = "Unexpected error occurred while deleting datastream {}: {}".format(stream_id, e)
        cherrypy.response.status = statusCode
        logging.info("Finished DELETE request to datastreams.")
        return json.dumps(data, indent=4)

    @staticmethod
    def createDatastream(session, datastream=None):
        """
        Creates a datastream with given options.
        Convience function that adds the given `datastream` to the database in `session`. If `datastream` is None, this function does nothing.
        expects datastream to be a DataStream() from models

        :param session: Existing context into a sqlalchemy database session. Can be created by a call to `sessionScope()`
        :type session: context object from `sessionScope()`
        :param datastream: `DataStream` object to add to the database.
        :type datastream: DataStream, optional

        .. note:
            This function is *not* idempotent. That is, multiple calls to this function with the same input `datastream` will create multiple `DataStream` objects in the database.
        """
        if datastream is not None:
            logging.debug("Creating datastream with options: %s", str(datastream.toDict()))
            session.add(datastream)
            session.commit()
        else:
            logging.error("Provided datastream to createDatastream method is None.")

    @staticmethod
    def updateStream(stream_id, data, session=None):
        """
        Updates stream with id `stream_id` with new key/values in `data`. Note that this function will incur a db lookup.

        :param stream_id: The id of the stream to modify.
        :type stream_id: str
        :param data: The new data to update `stream` with.
        :type data: dictionary

        :returns: Dictionary -- The dictionary view of the updated stream.

        .. seealso:: `models.DataStream`

        .. note:: This function contains a blacklist of keys that may not be updated. If `data` contains these keys, they are ignored.

        """

        logging.info("Updating stream with id %s with data %s", str(stream_id), str(data))
        if session is None:
            with sessionScope() as session:
                stream_info = _updateStream(stream_id, data, session)
            return stream_info
        return _updateStream(stream_id, data, session)


def deleteDatastream(session, datastream_id):
    """ Deletes a datastream with the given `datastream_id` and its associated sensor.


    :param session: Existing context into a sqlalchemy database session. Can be created by a call to `sessionScope()`
    :type session: context object from `sessionScope()`
    :param datastream_id: id of the datastream to delete.
    :type datastrea,_id: int

    :returns:
        The dictionary representation of the datastream that was deleted if successful; otherwise None.

    .. seealso::
        `models.DataStream`
        `datastreams.DELETE`
    """

    try:
        stream = session.query(DataStream).filter_by(id=datastream_id).one()
        # sensor = session.query(Sensor).filter_by(id=stream.sensor).one()
    except NoResultFound:
        logging.error("Requested datastream {} does not exist.".format(datastream_id))
    else:
        logging.debug("Deleting datastream...")
        stream_dict = stream.toDict()
        session.delete(stream)
        # session.delete(sensor)
        session.commit()
        return stream_dict
    return None


def _updateStream(stream_id, data, session):
    stream = session.query(DataStream).filter_by(id=stream_id).one()
    paths = session.query
    for key, value in data.iteritems():
        if key == "paths":
            currentPaths = stream.toDict()['paths']
            newPaths = data[key]
            toDelete = set(currentPaths) - set(newPaths)
            toAdd = set(newPaths) - set(currentPaths)
            for i in toDelete:
                session.delete(session.query(Path).filter_by(datastream_id=stream_id, path=i)[0])
            for j in toAdd:
                session.add(Path(datastream_id=stream_id, path=j))
            session.commit()
            continue
        if key != 'uuid':
            if key == "minimum value":
                value = float(value)
                key = "min_value"
            if key == "maximum value":
                value = float(value)
                key = "max_value"
            logging.info("changing: {} to {}".format(key, value))
            setattr(stream, key, value)

    # session.add(stream)
    session.commit()

    logging.info("Finished updating stream.")
    logging.info("{}".format(stream.toDict()))
    return stream.toDict()


def clean_inputs(inputs):
        """
            Checks that the supplied inputs only contains valid parameters for filtering Datadatastreams.

            :returns:
                Dictionary with valid parameters taken from provided inputs.
        """

        validInputs = {
            'sensor': '^[a-zA-Z0-9_.]+$'
        }

        valueConversions = {
            'null': None
        }

        safeInputs = {}

        for key, value in inputs.iteritems():
            if not key in validInputs:
                return None

            if value in valueConversions:
                value = valueConversions[value]
            elif re.match(validInputs[key], value) is None:
                return None

            safeInputs[key] = value

        return safeInputs


def get_datastream(datastream_id, session=None):
    """
    Tries to get a datastream from the database with the provided datastream_id.
    Optionally uses a provided session context to interact with the database.

    :param datastream_id: ID of the datastream.
    :param session:

    :returns:
        The dictionary view of the datastream.

    :raises:
        noResultFound: If no datastream matches the datastream_id.
    """
    if session is None:
        with sessionScope() as session:
            stream = session.query(DataStream).filter_by(id=datastream_id).one()
            return stream.toDict()
    else:
        stream = session.query(DataStream).filter_by(id=datastream_id).one()
        return stream.toDict()


def get_datastream_by_sensorid(sensor_id, session=None):
    """
    Tries to get a datastream from the database with the provided sensor_id.
    Optionally uses a provided session context to interact with the database.

    :param sensor_id: ID of the sensor to retrieve the datastream for.
    :param session:

    :returns:
        The dictionary view of the datastream.

    :raises:
        NoResultFound: If no datastream matches the datastream_id.
    """
    if session is None:
        with sessionScope() as session:
            stream = session.query(DataStream).filter_by(sensor=sensor_id).one()
            return stream.toDict()
    else:
        stream = session.query(DataStream).filter_by(sensor=sensor_id).one()
        return stream.toDict()


def filter_datastreams(session=None, **filter_args):
    """
    Tries to get all datastreams from the database.
    Optionally uses a provided session context to interact with the database.

    :param session:

    "returns:
        A list of dictionary views of the datastreams currently in the database.
    """
    inputs = clean_inputs(filter_args)
    if session is None:
        with sessionScope() as session:
            streams = session.query(DataStream).filter_by(inputs).all()
            return [stream.toDict() for stream in streams]
    else:
        streams = session.query(DataStream).filter_by(inputs).all()
        return [stream.toDict() for stream in streams]
