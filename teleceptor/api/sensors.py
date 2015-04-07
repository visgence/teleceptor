"""
    Contributing Authors:
        Bretton Murphy (Visgence, Inc.)
        Victor Szczepanski (Visgence, Inc.)
        Jessica Greenling (Visgence, Inc.)

    Resource endpoint for Sensors that is used as part of the RESTful api.  Handles
    the creation, updating, and retrieval of Sensors.

    API:
        Unless otherwise noted api will return data as JSON.

        GET /api/sensors/
            Obtain a list of available Sensors.
            Returns:
            {
                'error':   <error str if applicable>
                'sensors': [List of sensors]
            }

        GET /api/sensors/<sensor_id>/
            Obtain a single Sensor for the id parameter.
            Returns:
            {
                'error':   <error str if applicable>
                'sensor':  A single sensor
            }


        PUT /api/sensors/<sensor_id>/
            Update an existing sensor.
            Returns:
            {
                'error':    <error str if applicable>
                'sensor':   The updated sensor
            }

        DELETE /api/sensors/<sensor_id>/
            Delete an existing sensor.
            Returns:
            {
                'error': <error str if applicable>
                'sensor': The deleted sensor.
            }

        TODO:
        POST /api/sensors/  -  Create a new Sensor.

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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
import time
import logging

# Local Imports
from teleceptor import models
from teleceptor.models import Sensor, Calibration
from teleceptor.sessionManager import sessionScope
from teleceptor.auth import require
from teleceptor import USE_DEBUG



class Sensors:
    exposed = True

    if USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

    # @require()
    def GET(self, sensor_id=None):
        """
        Gets a sensor's or all sensor's information.

        Parameters
        ----------
        sensor_id : str, optional
            The UUID of a sensor, or None


        Returns
        -------
        If a valid `sensor_id` is given, returns the information stored in the database for the sensor with uuid `sensor_id`. If `sensor_id` does not refer to a sensor in the database, an error string will be returned.
        If `sensor_id` is None, returns a list of all sensors in the database.

        See Also
        --------
        `models.Sensor`
        """
        logging.debug("GET request to sensors.")

        cherrypy.response.headers['Content-Type'] = 'application/json'
        data = {}
        statusCode = "200"

        if sensor_id is not None:
            logging.debug("Getting single sensor with id %s", str(sensor_id))
            try:
                sensor = getSensor(sensor_id)
                data['sensor'] = sensor
            except NoResultFound:
                logging.error("Requested sensor %s does not exist.", str(sensor_id))
                data['error'] = "Sensor with id %s doesn't exist." % sensor_id
                statusCode = "400"
        else:
            logging.debug("Getting all sensors.")
            sensors = getAllSensors()
            data['sensors'] = sensors

        cherrypy.response.status = statusCode
        logging.info("Finished GET request to sensors.")
        return json.dumps(data, indent=4)

    @require()
    def POST(self, sensor_id=None):
        logging.error("POST request to sensors. This API end point is not implemented.")
        #TODO: Implement this for sensor creation
        pass

    @require()
    def PUT(self, sensor_id):
        """
        Updates the sensor with uuid `sensor_id`.

        Using the JSON formatted data in the HTTP request body, updates the sensor information in the database. Valid key/value pairs correspond to the columns in `models.Sensor`.

        Parameters
        ----------
        sensor_id : str
            The UUID of a sensor

        Returns
        -------
        A JSON object with an 'error' key if an error occured or 'sensor' key if update succeeded. If 'error', the value is an error string. If 'sensor', the value is a JSON object representing the updated sensor in the database.

        See Also
        --------
        `models.Sensor`
        """
        logging.debug("PUT request to sensors.")

        returnData = {}
        statusCode = "200"
        cherrypy.response.headers['Content-Type'] = 'application/json'
        try:
            data = json.loads(cherrypy.request.body.read())
        except ValueError:
            #no json object to decode, just use an empty dictionary
            #TODO: Decide on new behaviour if no json object so we don't incur an extra db lookup.
            data = {}

        logging.debug("Request body: %s", data)

        try:
            sensor = Sensors.updateSensor(sensor_id, data)
            returnData['sensor'] = sensor
        except NoResultFound:
            logging.error("Sensor with id %s doesn't exist.", str(sensor_id))
            returnData['error'] = "Sensor with id %s doesn't exist." % sensor_id
            statusCode = "400"

        cherrypy.response.status = statusCode

        logging.debug("Finished PUT request to sensors.")
        return json.dumps(returnData, indent=4)

    @require()
    def DELETE(self, sensor_id):
        """
        Deletes the sensor with uuid `sensor_id`.

        This function cannot be undone, but the sensor may be created again
        in a separate transaction.

        Parameters
        ----------
        sensor_id : str
            The UUID of a sensor

        Returns
        -------
        A JSON object with an 'error' key if an error occured or 'sensor' key if update succeeded. If 'error', the value is an error string. If 'sensor', the value is a JSON object representing the deleted sensor in the database.

        See Also
        --------
        `models.Sensor`
        """
        logging.debug("DELETE request to sensors.")

        returnData = {}
        statusCode = "200"
        cherrypy.response.headers['Content-Type'] = 'application/json'

        deleted_sensor = deleteSensor(sensor_id)
        if deleted_sensor is None:
            returnData['error'] = "Sensor with id %s could not be deleted." % sensor_id
            statusCode = "400"
        else:
            returnData['sensor'] = deleted_sensor

        cherrypy.response.status = statusCode
        logging.debug("Finished DELETE request to sensors.")
        return json.dumps(returnData, indent=4)


    #expects sensor to be a Sensor() from model
    @staticmethod
    def createSensor(session, sensor=None):
        """
        Adds `sensor` to the database.

        Parameters
        ----------
        session : sessionScope() context
            The context for accessing the database.
        sensor : model.Sensor
            The Sensor to add to the database.

        See Also
        --------
        `models.Sensor`
        """
        logging.debug("Creating sensor %s", str(sensor))

        if sensor is not None:
            session.add(sensor)

    @staticmethod
    def updateSensor(sensor_id, data):
        """
        Updates sensor with id `sensor_id` with new key/values in `data`. Note that this function will incur a db lookup.

        Parameters
        ----------
        sensor_id : str
            The id of the Sensor to modify.
        data : dictionary
            The new data to update `sensor` with.

        Returns
        -------
        The dictionary view of the updated sensor.

        See Also
        --------
        `models.Sensor`

        Notes
        -----
        This function contains a blacklist of keys that may not be updated. If `data` contains these keys, they are ignored.
        This documentation should contain the full blacklist:

        blacklist = ["uuid","message"]
        whitelist = ["sensor_IOtype", "sensor_type", "name", "units", ""]
        """

        logging.debug("Updating sensor with id %s with data %s", str(sensor_id), str(data))
        blacklist = ("uuid","message")
        with sessionScope() as session:
            sensor = session.query(Sensor).filter_by(uuid=sensor_id).one()
            for key,value in data.iteritems():
                if key in blacklist:
                    logging.error("Request to updateSensor included blacklisted key %s", str(key))
                    continue
                if key == "last_calibration":
                    if type(value['coefficients']) is not type(str()):
                        value['coefficients'] = json.dumps(value['coefficients'])

                    #if no timestamp, create timestamp
                    if 'timestamp' not in value or value['timestamp'] is None or value['timestamp'] == 0:

                        logging.debug("No timestamp provided. Using current time %s", str(time.time()))
                        value['timestamp'] = time.time()

                    Sensors.updateCalibration(session, sensor, value['coefficients'], value['timestamp'])
                elif key in models.SENSORWHITELIST:
                    setattr(sensor, key, value)

            session.add(sensor)


            logging.debug("Finished updating sensor.")
            return sensor.toDict()

    @staticmethod
    def updateCalibration(session, sensor, coefficients, timestamp):
        """
        Updates the calibration for `sensor`.

        Using `coefficients` and `timestamp`, creates a new Calibration for `sensor` if `timestamp` is newer than `sensor`'s timestamp and `coefficients` is different from `sensor`'s coefficients.

        Parameters
        ----------
        session : sessionScope() context
            The context for accessing the database.
        sensor : model.Sensor
            The Sensor to update.
        coefficients : iterable of float
            The new coefficients of the Calibration function.
        timestamp : int
            The timestamp for `coefficients`

        See Also
        --------
        `models.Sensor`
        `models.Calibration`
        """
        logging.debug("Updating calibration of sensor %s with coefficients %s and timestamp %s", str(sensor), str(coefficients), str(timestamp))

        if sensor is None:
            logging.error("Input sensor is None.")

        if coefficients is None:
            logging.error("Input coefficients is None.")

        if timestamp is None:
            logging.error("Input timestamp is None.")

        updateNeeded = False
        if sensor.last_calibration_id is None:
            #sensor doesn't have a calibration id, so we need to make a new calibration
            Cal = Calibration(coefficients=coefficients,timestamp=timestamp,sensor_id=sensor.uuid)
            session.add(Cal)
            session.commit()
            updateNeeded = True
        else:
            try:
                Cal = session.query(Calibration).filter_by(id=sensor.last_calibration_id).one()
                #update calibration based on timestamps
                currentTimestamp = timestamp
                oldTimestamp = Cal.timestamp

                logging.debug("Request timestamp: %s, Database timestamp: %s", currentTimestamp, oldTimestamp)

                if currentTimestamp > oldTimestamp:
                    logging.debug("Comparing coefficients.")

                    #check if coefficients are different
                    if Cal.coefficients != coefficients:
                        logging.debug("Coefficients are different, updating...")

                        Cal = Calibration(coefficients=coefficients,timestamp=timestamp,sensor_id=sensor.uuid)
                        session.add(Cal)
                        session.commit()
                        logging.debug("Added new calibration to database.")

                        updateNeeded = True
            except NoResultFound:
                logging.debug("No calibration found for calibration id %s. Creating new calibration...", str(sensor.last_calibration_id))

                Cal = Calibration(coefficients=coefficients,timestamp=timestamp,sensor_id=sensor.uuid)
                session.add(Cal)
                session.commit()
                logging.debug("Created new calibration.")

                updateNeeded = True
            if sensor.uuid != Cal.sensor_id:
                #sensor thinks the calibration it has belongs to it, but it doesn't (may belong to another sensor). Make a new calibration.
                logging.error("Calibration has different sensor foreign key %s than input sensor uuid %s", Cal.sensor_id, sensor.uuid)

                Cal = Calibration(coefficients=coefficients,timestamp=timestamp,sensor_id=sensor.uuid)
                session.add(Cal)
                session.commit()
                logging.debug("Created new Calibration for input sensor.")

                updateNeeded = True

        #update sensor model with calibration
        if updateNeeded:
            logging.debug("Updating sensor with new calibration.")

            sensor = session.query(Sensor).filter_by(uuid = sensor.uuid).one()
            Cal = session.query(Calibration).filter_by(sensor_id=sensor.uuid)[-1] #Gets most recent (by id) calibration

            sensor.last_calibration_id = Cal.id
            sensor.last_calibration = Cal
            session.commit()

def deleteSensor(sensor_id):
    """
    Deletes the sensor with given uuid.

    Parameters
    ----------
    sensor_id : str
        The UUID of a sensor

    Returns
    -------
    The dictionary representation of the sensor that was deleted if successful; otherwise None.

    See Also
    --------
    `models.Sensor`
    `sensors.DELETE`
    """
    logging.info("Deleting sensor %s", sensor_id)

    with sessionScope() as session:
        try:
            sensor = session.query(Sensor).filter_by(uuid = sensor_id).one()
        except NoResultFound:
            logging.error("Requested sensor %s does not exist.", str(sensor_id))
            return None
        else:
            logging.debug("Got Sensor.")
            sensor_dict = sensor.toDict()
            session.delete(sensor)
            return sensor_dict
    return None


def getSensor(sensor_id):
    """
    :param sensor_id: The id of the sensor to query on
    :return: A dictionary representing the sensor (as described in Models.Sensor) if found, else None
    :raises NoResultFound: If a sensor with id sensor_id was not found.
    """

    logging.debug("Getting Sensor %s", str(sensor_id))

    with sessionScope() as session:
        sensor = session.query(Sensor).filter_by(uuid=sensor_id).one()
        return sensor.toDict()
    return None

def getAllSensors():
    """
    Returns the view of every sensor in the database.
    :return: A list of dictionaries representing all sensors in the database.
    """
    logging.debug("Getting all sensors.")
    with sessionScope() as session:
        sensors = session.query(Sensor).all()
        return [s.toDict() for s in sensors]