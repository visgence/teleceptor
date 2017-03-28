"""
messages.py

    Authors: Victor Szczepanski
             Jessica Greenling

    This module handles message sending, receiving, and deleting.

    API:
        Unless otherwise noted api will return data as JSON.

        Functions include GET, POST, DELETE, and PURGE.
"""


# System Imports
import cherrypy
from time import time
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
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

    def GET(self, sensor_id=None):
        """
        A GET to this module should include the sensor_id. No content is
        needed.
        All message queues are returned if sensor_id is not given (is None)

        :return:
            a json object with the form
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

        :param sensor_id: Unique identifier for a sensor.
        :type sensor_id: int
        """

        logging.debug("GET request to messages.")

        cherrypy.response.headers['Content-Type'] = 'application/json'
        data = {}
        status_code = "200"

        if sensor_id is not None:
            logging.debug("Request for sensor_id %s", str(sensor_id))
            try:
                messages = getMessages(sensor_id)
            except NoResultFound:
                logging.error("Sensor with id %s does not exist.", str(sensor_id))
                status_code = "400"
                data['error'] = "Sensor with id %s doesn't exist" % sensor_id
            else:
                if messages is not None:
                    logging.debug("Found message queue for sensor with id %s: %s", str(sensor_id), str(messages))
                    data['message_queue'] = {}
                    data['message_queue']['messages'] = messages
                else:
                    logging.error("Sensor with id %s does not have a message queue.", str(sensor_id))
                    status_code = "400"
                    data['error'] = "Sensor with id %s doesn't have a message queue" % sensor_id

        else:
            logging.debug("Getting message queues for all sensors.")
            message_queues = getAllMessages()
            data['message_queues'] = message_queues

        logging.debug("Completed GET request to messages.")
        cherrypy.response.status = status_code
        return json.dumps(data, indent=4)

    @staticmethod
    def is_valid_type(message, sensor_type):
        """
        This function validates that the message type matches with the sensor type.

        :returns: bool
        """
        if type(message) == int:
            message = float(message)
        if sensor_type == "bool":
            return type(message) == bool
        elif sensor_type == "float":
            return type(message) == float
        logging.error("Provided sensor type %s does not match int, bool, or float")
        return False

    def POST(self):
        """
        A POST to this module should include a sensor_id and the
        content of the request should include the data to go in the message.
        :returns:
            the message that was created.
            Content form should be
            content = {
                    "message": message_value
                   ,"duration:" duration_value
            }

        :param sensor_id: Unique identifier for a sensor.
        :type sensor_id: int
        """
        logging.debug("POST request to messages.")

        cherrypy.response.headers['Content-Type'] = 'application/json'
        status_code = "200"
        return_data = {}

        data = json.loads(cherrypy.request.body.read())
        print"\ngot message\n"
        print data
        if "message" not in data:
            logging.error("POST request to messages has no message data.")
            return_data['error'] = "POST to messages does not contain message data"
            status_code = "400"
            cherrypy.response.status = status_code
            return json.dumps(return_data, indent=4)
        if "duration" not in data:
            logging.error("POST request to messages has no duration data.")
            return_data['error'] = "POST to messages does not contain duration data"
            status_code = "400"
            cherrypy.response.status = status_code
            return json.dumps(return_data, indent=4)

        try:
            msg = addMessage(data['sensor_id'], float(data['message']), data['duration'])
        except NoResultFound as e:
            return_data['error'] = e.message
            status_code = "400"
        except ValueError as e:
            return_data['error'] = e.message
            status_code = "400"
        else:
            return_data['message'] = msg

        logging.debug("Finished POST request to messages.")
        cherrypy.response.status = status_code
        return json.dumps(return_data, indent=4)

    def DELETE(self, sensor_id, message_id):
        """
        A DELETE to this module should remove one message (based on its id)
        from the message queue it is stored in.

        :returns: the deleted message as confirmation that the message was deleted.

        :param sensor_id: Unique identifier for a sensor.
        :type sensor_id: int
        :param message_id: Unique identifier for a message.
        :type message_id: int
        """

        logging.debug("DELETE request to messages.")
        cherrypy.response.headers['Content-Type'] = 'application/json'
        status_code = "200"
        return_data = {}

        try:
            msg = deleteMessage(sensor_id, message_id)
        except NoResultFound as e:
            return_data['error'] = e.message
            status_code = "400"
        except ValueError as e:
            return_data['error'] = e.message
            status_code = "400"
        else:
            return_data['message'] = msg

        logging.debug("Finished DELETE request to messages.")
        cherrypy.response.status = status_code
        return json.dumps(return_data, indent=4)

    @cherrypy.expose
    def PURGE(self, sensor_id, timeout):
        """
        A PURGE to this module should delete all messages from the message
        queue that belongs to the sensor with uuid sensor_id with
        timeout <= timeout.

        :returns: an error message if an error occurred or a success message if no error occurred.

        :param sensor_id: Unique identifier for a sensor.
        :type sensor_id: int
        :param timeout: The time at which the message(s) will expire.
        :type timeout: float
        """
        logging.debug("PURGE request to messages.")

        cherrypy.response.headers['Content-Type'] = 'application/json'
        status_code = "200"
        return_data = {}

        try:
            rows_deleted = deleteAllMessages(sensor_id, timeout)
        except NoResultFound as e:
            return_data['error'] = e.message
            status_code = "400"
        except ValueError as e:
            return_data['error'] = e.message
            status_code = "400"
        else:
            return_data['success'] = "Deleted %s messages" % rows_deleted

        logging.debug("Finished PURGE request to messages.")
        cherrypy.response.status = status_code
        return json.dumps(return_data, indent=4)


def getMessages(sensor_id, by_timestamp=False, unread_only=False):
    """
    Returns a list of all messages (read and not read) for the sensor with id `sensor_id`

    :param sensor_id: The id of the sensor to get all messages for.
    :type sensor_id: int
    :param by_timestamp: Gets only messages that have not timed out (i.e. timeout for message is greater than current time) if True
    :type by_timestamp: boolean
    :param unread_only: Gets only messages that are unread if True.
    :type unread_only: boolean

    :returns: The list of messages for the sensor with id `sensor_id`, or None if sensor doesn't have a message queue.

    :raises: NoResultFound if sensor_id is None or no Sensor found with id `sensor_id`
    """
    with sessionScope() as session:
        try:
            sensor_queue = session.query(MessageQueue).filter_by(sensor_id=sensor_id).one()
        except NoResultFound:
            logging.debug("Sensor %s has no message queue." % str(sensor_id))
            return None
        logging.debug("Got sensor_queue.")
        if unread_only:
            if by_timestamp:
                logging.debug("Getting by timestamp and unread...")
                messages = session.query(Message).filter(Message.message_queue_id == sensor_queue.id,
                                                         Message.timeout >= time(),
                                                         Message.read is not True)
            else:
                messages = session.query(Message).filter(Message.message_queue_id == sensor_queue.id,
                                                         Message.timeout >= 0,
                                                         Message.read is not True)
        else:
            if by_timestamp:
                messages = session.query(Message).filter(Message.message_queue_id == sensor_queue.id,
                                                         Message.timeout >= time())
            else:
                messages = session.query(Message).filter(Message.message_queue_id == sensor_queue.id,
                                                         Message.timeout >= 0)
        messages_view = []
        if unread_only:
            logging.debug("Got messages: %s", str([msg.to_dict() for msg in messages]))
            logging.debug("Setting messages as read.")
            for msg in messages:
                msg.read = True
                # if we don't directly append here, python decides to not include the messages in the list comprehension
                messages_view.append(msg.to_dict())
        else:
            messages_view = [msg.to_dict() for msg in messages]

    return messages_view


def getAllMessages():
    """
    Returns a list of message queues for all sensors.
    """
    with sessionScope() as session:
        message_queues = session.query(MessageQueue).all()
        return [message_queue.to_dict() for message_queue in message_queues]


def addMessage(sensor_id, message, duration):
    """
    Creates a new Message from `message` and `duration` and appends it to the msgQueue of the sensor with id `sensor_id`.
    If the requested sensor does not have a message queue yet, this function creates one.

    :param sensor_id:
    :param message:
    :param duration:

    :returns:
        A dictionary representing the added message.

    :raises:
        NoResultFound: If sensor_id is None or no Sensor found with id `sensor_id`
        ValueError: If type of message is not valid for sensor with id `sensor_id`
    """
    with sessionScope() as s:
        try:
            sensor = s.query(Sensor).filter_by(uuid=sensor_id).one()
        except NoResultFound:
            raise NoResultFound("No such Sensor with id %s" % str(sensor_id))
        else:
            msg_queue = sensor.message_queue
            if msg_queue is None:
                logging.debug("Sensor has no message queue. Creating one...")
                sensor.message_queue = MessageQueue(sensor_id=sensor.uuid)
                s.commit()
                logging.debug("Completed message queue creation.")
                msg_queue = sensor.message_queue

            msg = Message()
            msg.read = False
            logging.debug("Sensor's type is %s", str(sensor.sensor_type))

            if not Messages.is_valid_type(message, sensor.sensor_type):
                logging.error("Message type %s does not match sensor type %s", str(type(message)), str(sensor.sensor_type))
                raise ValueError("Message type does not match sensor type")

            msg.message = json.dumps(message)
            msg.timeout = time() + duration
            logging.debug("Adding message to database: %s", str(msg.to_dict()))
            s.add(msg)
            s.commit()

            logging.debug("Adding message to message queue...")
            msg_queue.messages.append(msg)
            s.commit()
            logging.debug("Completed adding message.")
            logging.debug("Returning added message: %s", str(msg.to_dict()))
            return msg.to_dict()


def deleteMessage(sensor_id, message_id):
    with sessionScope() as session:
        try:
            sensor = session.query(Sensor).filter_by(uuid=sensor_id).one()
        except NoResultFound as e:
            logging.error("Sensor with id %s does not exist", str(sensor_id))
            raise NoResultFound("Sensor with id %s does not exist", str(sensor_id))
        else:
            msgQueue = sensor.message_queue

            if msgQueue is None:
                logging.error("Sensor with id %s has no message queue to DELETE from.", str(sensor_id))
                raise ValueError("Sensor with id %s has no message queue to DELETE from.", str(sensor_id))

            try:
                msgToDel = session.query(Message).filter_by(id=message_id).one()
            except NoResultFound:
                logging.error("Message with id %s does not exist.", str(message_id))
                raise NoResultFound("Message with id %s does not exist.", str(message_id))

            if msgToDel not in msgQueue.messages:
                logging.error("Message with id %s does not belong to sensor with id %s", str(message_id), str(sensor_id))
                raise ValueError("Message with id %s does not belong to sensor with id %s", str(message_id), str(sensor_id))

            logging.debug("Removing message...")
            msgQueue.messages.remove(msgToDel)
            msg = msgToDel.to_dict()
            session.delete(msgToDel)
            session.commit()
            logging.debug("Finished removing message.")
            return msg
    return None


def deleteAllMessages(sensor_id, timeout):
    rows_deleted = None
    with sessionScope() as session:
        try:
            sensor = session.query(Sensor).filter_by(uuid=sensor_id).one()
        except NoResultFound:
            logging.error("Sensor with id %s does not exist", str(sensor_id))
            raise NoResultFound("Sensor with id %s doesn't exist" % sensor_id)

        msgQueue = sensor.message_queue

        if msgQueue is None:
            logging.error("Sensor with id %s has no message queue.", str(sensor_id))
            raise ValueError("Sensor with id %s has no messages" % sensor_id)

        # actually delete
        logging.debug("Deleting message queue for sensor with id %s...", str(sensor_id))
        rows_deleted = session.query(Message).\
            filter(Message.message_queue_id == msgQueue.id, Message.timeout <= timeout).delete()
        logging.debug("Finished deleting message queue.")
        logging.debug("Deleted %s messages", rows_deleted)

    return rows_deleted
