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

# Local Imports
from teleceptor.models import Sensor, Calibration
from teleceptor.sessionManager import sessionScope
from teleceptor.auth import require


class Sensors:
    exposed = True


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
        cherrypy.response.headers['Content-Type'] = 'application/json'
        data = {}

        if sensor_id is not None:
            with sessionScope() as s:
                try:
                    sensor = s.query(Sensor).filter_by(uuid = sensor_id).one()
                except NoResultFound:
                    data['error'] = "Sensor with id %s doesn't exist." % sensor_id
                else:
                    data['sensor'] = sensor.toDict()

            return json.dumps(data, indent=4)
        else:
            with sessionScope() as s:
                sensors = s.query(Sensor).all()
                data['sensors'] = [sensor.toDict() for sensor in sensors]

            return json.dumps(data, indent=4)


    @require()
    def POST(self, sensor_id=None):
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
        returnData = {}
        statusCode = "200"
        cherrypy.response.headers['Content-Type'] = 'application/json'
        data = json.loads(cherrypy.request.body.read())

        with sessionScope() as s:
            try:
                sensor = s.query(Sensor).filter_by(uuid = sensor_id).one()
            except NoResultFound:
                returnData['error'] = "Sensor with id %s doesn't exist." % sensor_id
                statusCode = "400"
            else:
                sensor = Sensors.updateSensor(s,sensor,data)
                returnData['sensor'] = sensor.toDict()

        cherrypy.response.status = statusCode

        return json.dumps(returnData,indent=4)

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
        print "in create Sensor. Sensor:"
        print sensor
        if sensor is not None:
		    session.add(sensor)
        print "exiting createSensor"

    @staticmethod
    def updateSensor(session, sensor, data):
        """
        Updates `sensor` with new key/values in `data`

        Parameters
        ----------
        session : sessionScope() context
            The context for accessing the database.
        sensor : model.Sensor
            The Sensor to modify.
        data : dictionary
            The new data to update `sensor` with.

        Returns
        -------
        The updated sensor.

        See Also
        --------
        `models.Sensor`

        Notes
        -----
        This function contains a blacklist of keys that may not be updated. If `data` contains these keys, they are ignored.
        This documentation should contain the full blacklist:

        blacklist = ["uuid","message"]
        """

        blacklist = ["uuid","message"]
        for key,value in data.iteritems():
            if key in blacklist:
                continue
            if key == "last_calibration":
                if type(value['coefficients']) is not type(str()):
                    value['coefficients'] = json.dumps(value['coefficients'])
                #if no timestamp, create timestamp
                if 'timestamp' not in value or value['timestamp'] is None or value['timestamp'] == 0:
                    print "timestamp not in value. Using current time."
                    value['timestamp'] = time.time()
                Sensors.updateCalibration(session,sensor,value['coefficients'],value['timestamp'])
            else:
                setattr(sensor,key,value)

        session.add(sensor)
        session.commit()

        return sensor

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
                print "new timestamp:"
                print timestamp
                print "old timestamp:"
                print oldTimestamp
                if currentTimestamp > oldTimestamp:
                    print "new calibration is newer than one in db. checking coefficients..."
                    #check if coefficients are different
                    if Cal.coefficients != coefficients:
                        print "coefficients are different, so we'll make a new calibration."
                        Cal = Calibration(coefficients=coefficients,timestamp=timestamp,sensor_id=sensor.uuid)
                        session.add(Cal)
                        session.commit()
                        updateNeeded = True
            except NoResultFound:
                Cal = Calibration(coefficients=coefficients,timestamp=timestamp,sensor_id=sensor.uuid)
                session.add(Cal)
                session.commit()
                updateNeeded = True
            if sensor.uuid != Cal.sensor_id:
                #sensor thinks the calibration it has belongs to it, but it doesn't (may belong to another sensor). Make a new calibration.
                Cal = Calibration(coefficients=coefficients,timestamp=timestamp,sensor_id=sensor.uuid)
                session.add(Cal)
                session.commit()
                updateNeeded = True

        #update sensor model with calibration
        if updateNeeded:
            sensor = session.query(Sensor).filter_by(uuid = sensor.uuid).one()
            Cal = session.query(Calibration).filter_by(sensor_id=sensor.uuid)[-1] #Gets most recent (by id) calibration
            sensor.last_calibration_id = Cal.id
            sensor.last_calibration = Cal
            session.commit()

