"""
Contributing Authors:
        Victor Szczepanski (Visgence, Inc.)
        Jessica Greenling (Visgence, Inc.)



    This module handles message sending, receiving, and deleting.

    API:
        Unless otherwise noted api will return data as JSON.

        Functions include GET, POST, DELETE, and PURGE.


Dependencies:
    global:
    cherrypy
    sqlalchemy
    (optional) simplejson

    local:
    teleceptor.models
    teleceptor.sessionManager
    teleceptor.auth



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
import time
from sqlalchemy.orm.exc import NoResultFound
try:
    import simplejson as json
except ImportError:
    import json
import logging

# Local Imports
from teleceptor.models import Sensor, MessageQueue, Message
from teleceptor.sessionManager import sessionScope
from teleceptor.auth import require
from teleceptor import USE_DEBUG


class Messages:
    exposed = True

    if USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',level=logging.INFO)

    def GET(self, sensor_id=None):
        """
        A GET to this module should include the sensor_id. No content is
        needed.
        All message queues are returned if sensor_id is not given (is None)

        Returns a json object with the form
        data = {
                'message_queue': [
                Message,
                Message,
                ...
                ]
        }
        if the sensor_id is given.

        If no sensor_id is given, returns a json object with the form
        data = {
                'message_queues' :[
                MessageQueue,
                MessageQueue,
                ...
                ]
        }

        If the sensor_id is not found, returns an error json of the form
        data = {
                'error' : "Sensor with id __ doesn't exist"
        }

        sensor_id: int
            Unique identifier for a sensor.
        """

        logging.debug("GET request to messages.")

        cherrypy.response.headers['Content-Type'] = 'application/json'
        data = {}
        statusCode = "200"


        if sensor_id is not None:
            logging.debug("Request for sensor_id %s", str(sensor_id))
            with sessionScope() as s:
                try:
                    sensor = s.query(Sensor).filter_by(uuid=sensor_id).one()
                except NoResultFound:
                    logging.error("Sensor with id %s does not exist.", str(sensor_id))
                    data['error'] = "Sensor with id %s doesn't exist" % sensor_id
                else:
                    msgQueue = sensor.message_queue
                    if msgQueue is not None:
                        logging.debug("Found message queue for sensor with id %s: %s", str(sensor_id), str(msgQueue.to_dict()) )
                        data['message_queue'] = msgQueue.to_dict()
                    else:
                        logging.error("Sensor with id %s does not have a message queue.", str(sensor_id))
                        data['error'] = "Sensor with id %s doesn't have a message queue" % sensor_id
        else:
            logging.debug("Getting message queues for all sensors.")
            with sessionScope() as s:
                messageQueues = s.query(MessageQueue).all()
                data['messageQueues'] = [messageQueue.to_dict() for messageQueue in messageQueues]

        logging.debug("Completed GET request to messages.")
        return json.dumps(data, indent=4)


    def is_valid_type(self,message,sensor_type):
        """
        This function validates that the message type matches with the sensor type.
        Returns True or False
        """
        if type(message) == int:
            message = float(message)
        if sensor_type == "bool":
            return type(message) == bool
        elif sensor_type == "float":
            return type(message) == float
        logging.error("Provided sensor type %s does not match int, bool, or float")
        return False

    @require()
    def POST(self,sensor_id):
        """
        A POST to this module should include a sensor_id and the
        content of the request should include the data to go in the message.
        Content form should be
        content = {
                "message": message_value
               ,"duration:" duration_value
        }

        sensor_id: int
            Unique identifier for a sensor.
        """
        logging.debug("POST request to messages.")

        cherrypy.response.headers['Content-Type'] = 'application/json'
        statusCode = "200"
        returnData = {}

        data = json.loads(cherrypy.request.body.read())
        if "message" not in data:
            logging.error("POST request to messages has no message data.")
            returnData['error'] = "POST to messages does not contain message data"
            statusCode = "400"
            return json.dumps(returnData,indent=4)
        if "duration" not in data:
            logging.error("POST request to messages has no duration data.")
            returnData['error'] = "POST to messages does not contain duration data"
            statusCode = "400"
            return json.dumps(returnData,indent=4)

        with sessionScope() as s:
            try:
                sensor = s.query(Sensor).filter_by(uuid=sensor_id).one()
            except NoResultFound:
                logging.error("Sensor with id %s does not exist.", str(sensor_id))
                returnData['error'] = "Sensor with id %s doesn't exist" % sensor_id
                statusCode = "400"
            else:
                msgQueue = sensor.message_queue
                if msgQueue is None:
                    logging.debug("Sensor has no message queue. Creating one...")
                    sensor.message_queue = MessageQueue(sensor_id=sensor.uuid)
                    s.commit()
                    logging.debug("Completed message queue creation.")
                    msgQueue = sensor.message_queue
                
                msg = Message()
                logging.debug("Sensor's type is %s", str(sensor.sensor_type))
                if not self.is_valid_type(data['message'], sensor.sensor_type):
                    logging.error("Message type %s does not match sensor type %s", str(type(data['message'])), str(sensor.sensor_type))
                    returnData['error'] = "Message type does not match sensor type"
                    statusCode = "400"
                    return json.dumps(returnData,indent=4)

                msg.message = json.dumps(data['message'])
                msg.timeout = time.time() + data['duration']
                logging.debug("Adding message to database: %s", str(msg.to_dict()))
                s.add(msg)
                s.commit()

                logging.debug("Adding message to message queue...")
                msgQueue.messages.append(msg)
                s.commit()
                logging.debug("Completed adding message.")

            logging.debug("Finished POST request to messages.")
            return json.dumps(returnData,indent=4)


    def DELETE(self, sensor_id, message_id):
        """
        A DELETE to this module should remove one message (based on its id)
        from the message queue it is stored in.

        Returns the deleted message as confirmation that the message was deleted.

        sensor_id: int
            Unique identifier for a sensor.
        message_id: int
            Unique identifier for a message.
        """

        logging.debug("DELETE request to messages.")
        cherrypy.response.headers['Content-Type'] = 'application/json'
        statusCode = "200"
        returnData = {}

        with sessionScope() as s:
            try:
                sensor = s.query(Sensor).filter_by(uuid=sensor_id).one()
            except NoResultFound:
                logging.error("Sensor with id %s does not exist", str(sensor_id))
                returnData['error'] = "Sensor with id %s doesn't exist" % sensor_id
                statusCode = "400"
            msgQueue = sensor.message_queue

            if msgQueue is None:
                logging.error("Sensor with id %s has no message queue to DELETE from.", str(sensor_id))
                returnData['error'] = "DELETE to messages does not contain message data"
                statusCode = "400"
                return json.dumps(returnData,indent=4)

            try:
                msgToDel = s.query(Message).filter_by(id=message_id).one()
            except NoResultFound:
                logging.error("Message with id %s does not exist.", str(message_id))
                returnData['error'] = "Message with id %s doesn't exist" % message_id
                statusCode = "400"
                return json.dumps(returnData,indent=4)

            if msgToDel not in msgQueue.messages:
                logging.error("Message with id %s does not belong to sensor with id %s", str(message_id), str(sensor_id))
                returnData['error'] = "Message with id %(m_id)s doesn't belong to Sensor with id %(sens_id)s" % {"m_id":message_id, "sens_id":sensor_id}
                statusCode = "400"
                return json.dumps(returnData,indent=4)

            logging.debug("Removing message...")
            msgQueue.messages.remove(msgToDel)
            returnData['message'] = msgToDel.to_dict()
            s.delete(msgToDel)
            s.commit()
            logging.debug("Finished removing message.")

            logging.debug("Finished DELETE request to messages.")
            return json.dumps(returnData, indent=4)

    @cherrypy.expose
    def PURGE(self, sensor_id, timeout):
        """
        A PURGE to this module should delete all messages from the message
        queue that belongs to the sensor with uuid sensor_id with
        timeout <= timeout.

        Returns an error message if an error occurred or a success message
        if no error occurred.

        sensor_id: int
            Unique identifier for a sensor.
        timeout : float
            The time at which the message(s) will expire.
        """
        logging.debug("PURGE request to messages.")

        cherrypy.response.headers['Content-Type'] = 'application/json'
        statusCode="200"
        returnData = {}
        rowsDeleted = 0

        with sessionScope() as s:
            try:
                sensor = s.query(Sensor).filter_by(uuid=sensor_id).one()
            except NoResultFound:
                logging.error("Sensor with id %s does not exist", str(sensor_id))
                returnData['error'] = "Sensor with id %s doesn't exist" % sensor_id
                statusCode = "400"
            msgQueue = sensor.message_queue

            if msgQueue is None:
                logging.error("Sensor with id %s has no message queue.", str(sensor_id))
                returnData['error'] = "Sensor with id %s has no messages" % sensor_id
                statusCode = "400"
                return json.dumps(returnData,indent=4)
            #actually delete
            logging.debug("Deleting message queue for sensor with id %s...", str(sensor_id))
            rowsDeleted = s.query(Message).\
            filter(Message.message_queue_id==msgQueue.id, Message.timeout <= timeout).delete()
            logging.debug("Finished deleting message queue.")

        returnData['success'] = "Deleted %s messages" % rowsDeleted
        logging.debug("Deleted %s messages", rowsDeleted)
        
        logging.debug("Finished PURGE request to messages.")
        return json.dumps(returnData,indent=4)
