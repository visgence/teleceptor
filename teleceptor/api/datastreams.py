"""
    Contributing Authors:
        Bretton Murphy (Visgence, Inc.)
        Victor Szczepanski (Visgence, Inc.)
        Jessica Greenling (Visgence, Inc.)

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

    (c) 2013 Visgence, Inc.

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
import json
from sqlalchemy.orm.exc import NoResultFound
import re
import logging

# Local Imports
from teleceptor.models import DataStream
from teleceptor.sessionManager import sessionScope
from teleceptor import USE_ELASTICSEARCH
if USE_ELASTICSEARCH:
    from teleceptor import elasticsearchUtils as esUtils
else:
    from teleceptor import whisperUtils
from teleceptor import USE_DEBUG


class DataStreams:
    exposed = True

    if USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)


    def GET(self, stream_id=None, *args, **filter_arguments):
        """ Gets a specified datastream or list of datastreams filtered by keyword arguments.


        Parameters
        ----------
        stream_id : int, optional
            The `stream_id` of the datastream to get or None to select datastreams based on filter arguments in `args` and `filter_arguments`.
        args : list, optional
            Unused list of arguments
        filter_arguments : dictionary, optional
            Keyword arguments to filter the datastream query.

        Returns
        -------
        data : dictionary
            Contains an 'error' key if an error occurred with the value being a string containing the error message. Contains a 'datastreams' key if multiple datastreams are selected with the value being a list of datastreams. Contains a 'stream' key if `stream_id` selects a unique datastream with the value being the selected stream.
            `data` is returned in the `response.text` section of the HTTP response, if this function is called through the cherrypy API.

        See Also
        --------
        cleanInputs : Checks that filter_arguments only contains valid parameters for filtering datastreams.


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
        """
        logging.debug("GET request to datastreams.")

        cherrypy.response.headers['Content-Type'] = 'application/json'
        data = {}

        statusCode = "200"

        if stream_id is not None:
            logging.debug("Request for datastream with id %s", str(stream_id))
            with sessionScope() as s:
                try:
                    stream = s.query(DataStream).filter_by(id = stream_id).one()
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
        #TODO: Implement this for datastream creation
        logging.error("POST request to datastreams. This API end point is not implemented.")
        pass

    def PUT(self, streamid=None):
        #TODO: Implement this for datastream update
        logging.error("PUT request to datastreams. This API end point is not implemented.")
        pass

    def DELETE(self, stream_id):
        """
        Deletes the DataStream with id `stream_id`.

        This function cannot be undone, but the stream may be created again
        in a separate transaction.

        Parameters
        ----------
        stream_id : int
            The id of a DataStream

        Returns
        -------
        A JSON object with an 'error' key if an error occured or 'datastream' key if update succeeded. If 'error', the value is an error string. If 'datastream', the value is a JSON object representing the deleted DataStream in the database.

        See Also
        --------
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


    #expects datastream to be a DataStream() from model
    @staticmethod
    def createDatastream(session, datastream=None):
        """ Creates a datastream with given options and binds a new whisper file to it.

        Convience function that adds the given `datastream` to the database in `session` and creates a whisper database file using this datastream's id. If `datastream` is None, this function does nothing.

        Parameters
        ----------
        session : context object from `sessionScope()`
            Existing context into a sqlalchemy database session. Can be created by a call to `sessionScope()`
        datastream : DataStream, optional
            `DataStream` object to add to the database and create a whisper file for.

        Notes
        -----
        This function is *not* idempotent. That is, multiple calls to this function with the same input `datastream` will create multiple `DataStream` objects in the database, each with its own whisper file.
        """
        if datastream is not None:
            logging.debug("Creating datastream with options: %s", str(datastream.toDict()))
            session.add(datastream)
            session.commit()
            if not USE_ELASTICSEARCH:    
                logging.debug("Creating whisper database with id %s", str(datastream.id))
                whisperUtils.createDs(datastream.id)
                logging.debug("Done making datastream and whisper database.")
        else:
            logging.error("Provided datastream to createDatastream method is None.")

def deleteDatastream(session, datastream_id):
    """ Deletes a datastream with the given `datastream_id`

    Parameters
    ----------
    session : context object from `sessionScope()`
        Existing context into a sqlalchemy database session. Can be created by a call to `sessionScope()`
    datastream_id : int
        id of the datastream to delete.

    Returns
    -------
    The dictionary representation of the datastream that was deleted if successful; otherwise None.

    See Also
    --------
    `models.DataStream`
    `datastreams.DELETE`
    """

    try:
        stream = session.query(DataStream).filter_by(id=datastream_id).one()
    except NoResultFound:
        logging.error("Requested datastream {} does not exist.".format(datastream_id))
    else:
        logging.debug("Deleting datastream...")
        stream_dict = steam.toDict()
        session.delete(stream)
        session.commit()
        return stream_dict
    return None

def clean_inputs(inputs):
        """
            Checks that the supplied inputs only contains valid parameters for filtering Datadatastreams.

            Returns: Dictionary with valid parameters taken from provided inputs.
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
    :return: The dictionary view of the datastream.
    :raises NoResultFound: If no datastream matches the datastream_id.
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
    :return: The dictionary view of the datastream.
    :raises NoResultFound: If no datastream matches the datastream_id.
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
    :return: A list of dictionary views of the datastreams currently in the database.
    """
    inputs = clean_inputs(filter_args)
    if session is None:
        with sessionScope() as session:
            streams = session.query(DataStream).filter_by(inputs).all()
            return [stream.toDict() for stream in streams]
    else:
        streams = session.query(DataStream).filter_by(inputs).all()
        return [stream.toDict() for stream in streams]
