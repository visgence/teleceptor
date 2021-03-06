"""
    Authors: Bretton Murphy (Visgence, Inc.)
             Victor Szczepanski (Visgence, Inc.)
             Jessica Greenling (Visgence, Inc.)
             Cyrille Gindreau (Visgence, Inc.)

    Resource endpoint for Sensors that is used as part of the RESTful api.  Handles
    the creation, updating, and retrieval of Sensors.

    TODO:
        POST /api/sensors/  -  Create a new Sensor.

"""

# System Imports
import cherrypy
import json
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

    def GET(self, sensor_id=None):
        """
        Gets a sensor's or all sensor's information.

        :param sensor_id: The UUID of a sensor
        :type sensor_id: str

        :returns: JSON -- If a valid `sensor_id` is given, returns the information stored in the database for the sensor with uuid `sensor_id`.
        If `sensor_id` does not refer to a sensor in the database, an error string will be returned. If `sensor_id` is None, returns a list of all sensors in the database.

        .. seealso:: `models.Sensor`
        """
        logging.debug("GET request to sensors.")

        cherrypy.response.headers['Content-Type'] = 'application/json'
        data = {}
        statusCode = "200"

        with sessionScope() as session:
            if sensor_id is not None:
                logging.debug("Getting single sensor with id %s", str(sensor_id))
                try:
                    sensor = getSensor(sensor_id, session)
                    data['sensor'] = sensor
                except NoResultFound:
                    logging.error("Requested sensor %s does not exist.", str(sensor_id))
                    data['error'] = "Sensor with id %s doesn't exist." % sensor_id
            else:
                logging.debug("Getting all sensors.")
                sensors = getAllSensors(session)
                data['sensors'] = sensors

        cherrypy.response.status = statusCode
        logging.debug("Finished GET request to sensors.")
        return json.dumps(data, indent=4)

    @require()
    def POST(self):

        logging.debug("POST request to sensors.")

        returnData = {}
        statusCode = "200"
        cherrypy.response.headers['Content-Type'] = 'application/json'
        try:
            data = json.loads(cherrypy.request.body.read())
        except ValueError:
            # no json object to decode, just use an empty dictionary
            data = {}
            return json.dumps({'error': 'mangled json'})

        logging.debug("Request body: %s", data)

        if 'uuid' not in data:
            return json.dumps({'error': 'A UUID is needed.'}, indent=4)
        sensor_data = {
            "sensor_IOtype": False,
            "name": data["uuid"],
            "uuid": data["uuid"]
        }

        if 'in' in data:
            sensor_data['sensor_IOtype'] = True
        if 'name' in data:
            sensor_data['name'] = data['name']
        if 'last_calibration' in data:
            sensor_data['last_calibration'] = data['last_calibration']

        with sessionScope() as session:
            try:
                sensor_info = Sensors.updateSensor(data=sensor_data, session=session)
            except NoResultFound:
                # sensor_data.pop('last_calibration', None)
                Sensors.createSensor(sensor_data, session)
            try:
                sensor = Sensors.updateSensor(data, session)
                returnData['sensor'] = sensor
            except NoResultFound:
                logging.error("Sensor with id %s doesn't exist.", str(data['uuid']))
                returnData['error'] = "Sensor with id %s doesn't exist." % data['uuid']
                statusCode = "400"
        cherrypy.response.status = statusCode

        logging.debug("Finished PUT request to sensors.")
        return json.dumps(returnData, indent=4)

    @require()
    def PUT(self):
        """
        Updates the sensor with uuid `sensor_id`.

        Using the JSON formatted data in the HTTP request body, updates the sensor information in the database. Valid key/value pairs correspond to the columns in `models.Sensor`.

        :param sensor_id: The UUID of a sensor
        :type sensor_id: str

        :returns: Dictionary -- A JSON object with an 'error' key if an error occured or 'sensor' key if update succeeded.
        If 'error', the value is an error string. If 'sensor', the value is a JSON object representing the updated sensor in the database.

        .. seealso:: `models.Sensor`

        .. todo:: Decide on new behaviour if no json object so we don't incur an extra db lookup.
        """
        logging.debug("PUT request to sensors.")

        returnData = {}
        statusCode = "200"
        cherrypy.response.headers['Content-Type'] = 'application/json'
        try:
            data = json.loads(cherrypy.request.body.read())
        except ValueError:
            # no json object to decode, just use an empty dictionary
            data = {}

        logging.debug("Request body: %s", data)

        with sessionScope() as session:
            try:
                sensor = Sensors.updateSensor(data, session)
                returnData['sensor'] = sensor
            except NoResultFound:
                logging.error("Sensor with id %s doesn't exist.", str(data['uuid']))
                returnData['error'] = "Sensor with id %s doesn't exist." % data['uuid']

        cherrypy.response.status = statusCode

        logging.debug("Finished PUT request to sensors.")
        return json.dumps(returnData, indent=4)

    @require()
    def DELETE(self, sensor_id):
        """
        Deletes the sensor with uuid `sensor_id`.

        This function cannot be undone, but the sensor may be created again
        in a separate transaction.

        :param sensor_id: The UUID of a sensor
        :type sensor_id: str

        :returns: Dictionary -- A JSON object with an 'error' key if an error occured or 'sensor' key if update succeeded.
        If 'error', the value is an error string. If 'sensor', the value is a JSON object representing the deleted sensor in the database.

        .. seealso:: `models.Sensor`
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

    # expects sensor to be a Sensor() from model
    @staticmethod
    def createSensor(sensor_data, session):
        """
        Adds `sensor` to the database.

        :param session: The context for accessing the database.
        :type session: sessionScope() context
        :param sensor: The Sensor to add to the database.
        :type sensor: model.Sensor

        .. seealso:: `models.Sensor`
        """
        caliTime = time.time()
        if 'scale' in sensor_data:
            coefs = sensor_data['scale']
            del sensor_data['scale']
        elif 'last_calibration' in sensor_data:
            coefs = sensor_data['last_calibration']['coefficients']
            caliTime = sensor_data['last_calibration']['timestamp']
            sensor_data.pop('last_calibration')
        else:
            coefs = [1, 0]

        sensor = Sensor(**sensor_data)
        calib = Calibration(sensor_id=sensor.toDict()['uuid'], timestamp=caliTime)
        calib.setCoefficients(coefs)
        sensor.last_calibration = calib
        sensor.last_calibration_id = calib.id
        logging.debug("Creating sensor %s", str(sensor))
        session.add(sensor)
        session.add(calib)
        session.commit()
        return sensor

    @staticmethod
    def updateSensor(data, session):
        """
        Updates sensor with id `sensor_id` with new key/values in `data`. Note that this function will incur a db lookup.

        :param sensor_id: The id of the Sensor to modify.
        :type sensor_id: str
        :param data: The new data to update `sensor` with.
        :type data: dictionary

        :returns: Dictionary -- The dictionary view of the updated sensor.

        .. seealso:: `models.Sensor`

        .. note:: This function contains a blacklist of keys that may not be updated. If `data` contains these keys, they are ignored. This documentation should contain the full blacklist:
            blacklist = ["uuid","message"]
            whitelist = ["sensor_IOtype", "sensor_type", "name", "units", ""]
        """

        logging.debug("Updating sensor with id %s with data %s", str(data['uuid']), str(data))
        return _updateSensor(data, session)

    @staticmethod
    def updateCalibration(sensor, coefficients, timestamp, session):
        """
        Updates the calibration for `sensor`.

        Using `coefficients` and `timestamp`, creates a new Calibration for `sensor` if `timestamp` is newer than `sensor`'s timestamp and `coefficients` is different from `sensor`'s coefficients.

        :param session: The context for accessing the database.
        :type session: sessionScope() context
        :param sensor: The Sensor to update.
        :type sensor: model.Sensor
        :param coefficients: The new coefficients of the Calibration function.
        :param timestamp: The timestamp for `coefficients`
        :type timestamp: int

        .. seealso::
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

        return _updateCalibration(sensor, coefficients, timestamp, session)


def deleteSensor(sensor_id, session):
    """
    Deletes the sensor with given uuid.

    :param sensor_id: The UUID of a sensor.
    :type sensor_id: str.

    :returns: Dictionary -- The dictionary representation of the sensor that was deleted if successful; otherwise None.

    .. seealso::
        `models.Sensor`
        `sensors.DELETE
    """
    logging.debug("Deleting sensor %s", sensor_id)

    try:
        sensor = session.query(Sensor).filter_by(uuid=sensor_id).one()
    except NoResultFound:
        logging.error("Requested sensor %s does not exist.", str(sensor_id))
        return None
    else:
        logging.debug("Got Sensor.")
        sensor_dict = sensor.toDict()
        session.delete(sensor)
        return sensor_dict

    return None


def getSensor(sensor_id, session):
    """
    :param sensor_id: The id of the sensor to query on.
    "param session: Optional session context. If None, this function creates its own context. Otherwise, uses this context.

    :returns: Dictionary -- A dictionary representing the sensor (as described in Models.Sensor) if found, else None

    :raises: NoResultFound -- If a sensor with id sensor_id was not found.
    """

    logging.debug("Getting Sensor %s", str(sensor_id))
    return session.query(Sensor).filter_by(uuid=sensor_id).one().toDict()


def getAllSensors(session):
    """
    Returns the view of every sensor in the database.

    :returns: Dictionary -- A list of dictionaries representing all sensors in the database.
    """
    logging.debug("Getting all sensors.")
    sensors = session.query(Sensor).order_by(Sensor.name).all()
    return [s.toDict() for s in sensors]


def _updateSensor(data, session):
    blacklist = ("uuid", "message")
    sensor = session.query(Sensor).filter_by(uuid=data['uuid']).one()
    for key, value in data.iteritems():
        logging.debug("Key: {}, Value: {}".format(key, value))
        if key in blacklist:
            logging.debug("Request to updateSensor included blacklisted key %s", str(key))
            continue
        if 'last_calibration' in key:
            logging.debug("value: {} and type: {}".format(value, type(value)))
            if isinstance(value['coefficients'], basestring):
                    value['coefficients'] = json.dumps(value['coefficients'])

            # if no timestamp, create timestamp
            logging.debug("value: {}".format(value))
            if 'timestamp' not in value or value['timestamp'] is None or value['timestamp'] == 0:

                logging.debug("No timestamp provided. Using current time %s", str(time.time()))
                value['timestamp'] = time.time()

            sensor = Sensors.updateCalibration(sensor.toDict(), value['coefficients'], value['timestamp'], session)
            # we want to keep using a Sensor, not the dict, so look it up
            # TODO: This is pretty smelly, but should work for now. Maybe in the future we want updateCalibration and _updateCalibration return a Sensor, or find some other way to update it.
            sensor = session.query(Sensor).filter_by(uuid=data['uuid']).one()
        elif 'scale' in key:
            continue
        elif key in models.SENSORWHITELIST:
            setattr(sensor, key, value)
    session.add(sensor)

    logging.debug("Finished updating sensor.")
    return sensor.toDict()


def _updateCalibration(sensor, coefficients, timestamp, session):
    updateNeeded = False
    logging.debug("Trying to update sensor %s with coefficiencts %s with new coefficients %s", str(sensor['uuid']), str(sensor['last_calibration']['coefficients']), str(coefficients))

    if 'last_calibration' not in sensor or 'id' not in sensor['last_calibration'] or sensor['last_calibration']['id'] is None:
        # sensor doesn't have a calibration id, so we need to make a new calibration
        Cal = Calibration(timestamp=timestamp, sensor_id=sensor['uuid'])
        Cal.setCoefficients(coefficients)
        session.add(Cal)
        session.commit()
        updateNeeded = True
    else:
        try:
            Cal = session.query(Calibration).filter_by(id=sensor['last_calibration']['id']).one()
            # update calibration based on timestamps
            currentTimestamp = timestamp
            oldTimestamp = Cal.timestamp

            logging.debug("Request timestamp: %s, Database timestamp: %s", currentTimestamp, oldTimestamp)

            if currentTimestamp > oldTimestamp:
                logging.debug("Comparing coefficients.")

                if type(coefficients) == tuple:
                    coefficients = list(coefficients)
                assert type(coefficients) == list

                # check if coefficients are different
                if Cal.getCoefficients() != coefficients:
                    logging.debug("Coefficients are different, updating...")

                    Cal = Calibration(timestamp=timestamp, sensor_id=sensor['uuid'])
                    Cal.setCoefficients(coefficients)
                    session.add(Cal)
                    session.commit()
                    logging.debug("Added new calibration to database.")

                    updateNeeded = True
        except (NoResultFound, KeyError) as e:
            logging.debug("No calibration found for sensor %s. Creating new calibration...", str(sensor))
            logging.debug(e)
            Cal = Calibration(timestamp=timestamp, sensor_id=sensor['uuid'])
            Cal.setCoefficients(coefficients)
            session.add(Cal)
            session.commit()
            logging.debug("Created new calibration.")

            updateNeeded = True
        if sensor['uuid'] != Cal.sensor_id:
            # sensor thinks the calibration it has belongs to it, but it doesn't (may belong to another sensor). Make a new calibration.
            logging.error("Calibration has different sensor foreign key %s than input sensor uuid %s", Cal.sensor_id, sensor['uuid'])

            Cal = Calibration(timestamp=timestamp, sensor_id=sensor['uuid'])
            Cal.setCoefficients(coefficients)
            session.add(Cal)
            session.commit()
            logging.debug("Created new Calibration for input sensor.")

            updateNeeded = True

    # update sensor model with calibration
    if updateNeeded:
        logging.debug("Updating sensor with new calibration.")

        sensor = session.query(Sensor).filter_by(uuid=sensor['uuid']).one()
        logging.debug("Got sensor %s", str(sensor.toDict()))
        # Gets most recent (by id) calibration
        Cal = session.query(Calibration).filter_by(sensor_id=sensor.uuid)[-1]
        logging.debug("Got calibration %s", str(Cal.toDict()))

        sensor.last_calibration_id = Cal.id
        logging.debug("Updated calibration id.")
        sensor.last_calibration = Cal
        session.commit()
        sensor = sensor.toDict()
    logging.debug("Sensor after updateCalibration: %s", str(sensor))
    return sensor
