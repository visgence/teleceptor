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

        TODO:
        POST /api/datastreams/  -  Create a new Datastreams.
        PUT /api/datastreams/<stream_id>/  -  Update an existing stream.
"""

# System Imports
import cherrypy
import json
from sqlalchemy.orm.exc import NoResultFound
import re
import logging

# Local Imports
from teleceptor.models import DataStream, Sensor
from teleceptor.sessionManager import sessionScope
from teleceptor import USE_ELASTICSEARCH, USE_DEBUG
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
        logging.debug("GET request to datastreams.")

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
                    logging.debug("Found stream with id %s: %s", str(stream_id), str(stream.toDict()))
                    data['stream'] = stream.toDict()
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
                    data['datastreams'] = [stream.toDict() for stream in datastreams]

        cherrypy.response.status = statusCode
        return json.dumps(data, indent=4)

    def POST(self, stream_id=None):
        # TODO: Implement this for datastream creation
        logging.error("POST request to datastreams. This API end point is not implemented.")
        pass

    def PUT(self, streamid=None):
        # TODO: Implement this for datastream update
        logging.error("PUT request to datastreams. This API end point is not implemented.")
        pass

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
        sensor = session.query(Sensor).filter_by(uuid=stream.sensor).one()
    except NoResultFound:
        logging.error("Requested datastream {} does not exist.".format(datastream_id))
    else:
        logging.debug("Deleting datastream...")
        stream_dict = stream.toDict()
        session.delete(stream)
        session.delete(sensor)
        session.commit()
        return stream_dict
    return None


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
