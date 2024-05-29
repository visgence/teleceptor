"""Django Models"""
import json
import os
# from ulid import ULID
import ulid
import uuid
from django.db import models
from django_ulid.models import ULIDField
from django.conf import settings

def new_ulid():
    """Create New Ulid"""
    # return ULID(os.urandom(16))
    # return ulid.new()
    # buf = f'uuid: {os.urandom(16)}'
    ret = uuid.UUID(None, os.urandom(16))
    print(ret)
    return ret


class SensorReading(models.Model):
    """
    id : int
        Uniquely identifies the SensorReading.
    datastream : int
        Used to identify a SensorReading to a DataStream.
    sensor : str
        Used to identify a SensorReading to a Sensor.
    value : float
        The value read from the sensor.
    timestamp : BigInt
        The time that the reading was taken.
    """


    id = models.IntegerField(primary_key=True)
    datastream = models.ForeignKey('DataStream', on_delete=models.PROTECT)
    sensor = models.ForeignKey('Sensor', on_delete=models.PROTECT)
    value = models.FloatField()
    timestamp = models.BigIntegerField()

    def to_dict(self):
        """dict"""
        return {
            'id': self.id,
            'datastream': self.datastream,
            'sensor': self.sensor,
            'value': self.value,
            'timestamp': self.timestamp
        }


class MessageQueue(models.Model):
    """
    Each sensor will have it's own unique message queue with its own identification number.
    The message queue can contain many messages.  Message handling can be found in messages.

    id : int
        Uniquely identifies the MessageQueue.
    messages : list of Message
        Can be an empty list or have many elements. Used to store pending messages for sensor.
    sensor_id : str
        Used to identify a MessageQueue to a Sensor.
    """

    # id = ULIDField(default=new_ulid, primary_key=True, editable=False)
    id = models.UUIDField(default=new_ulid, primary_key=True, editable=False)
    messages = models.ForeignKey('Message', on_delete=models.CASCADE)
    sensor = models.CharField(max_length=100)

    def to_dict(self):
        """dict"""
        data = {
            'id': self.id,
            'sensor_id': self.sensor.id
        }

        if self.messages is not None:
            try:
                data['messages'] = [m.to_dict() for m in self.messages]
            except TypeError:
                data['messages'] = self.messages.to_dict()

        return data


class Message(models.Model):
    """
    A message contains instructions for the sensor.

    id : int
        Uniquely identifies a Message.
    message : str
        Instructions for the sensor to perform some action that corresponds with
        the sensors capabilities.
    message_queue_id : int
        Used to identify a Message to a MessageQueue.
    timeout : float
        The expiration time for a Message. Old messages should not be used by the sensor.
    read : bool
        Indicates whether the Message as been sent to the basestation or read/acknowledged
        in some other way.
    """

    id = models.UUIDField(default=new_ulid, primary_key=True, editable=False)
    # id = ULIDField(default=new_ulid, primary_key=True, editable=False)
    message = models.CharField(max_length=100)
    message_queue = models.ForeignKey(MessageQueue, on_delete=models.PROTECT)
    timeout = models.FloatField(default=30000.0)
    read = models.BooleanField(default=False)

    def to_dict(self):
        """dict"""
        data = {
            'id': self.id,
            'message': json.loads(self.message),
            'timeout': self.timeout,
            'read': self.read
        }

        return data


class Sensor(models.Model):
    """
    uuid : str
        Unique identifier of this sensor.
    sensor_IOtype : bool
        True indicates that the sensor takes input.  
        False indicates that the sensor is only for output.
    sensor_type : str
        Indicates the type of sensor.  
        Used in conjunction with message to check that the message is valid for this type of sensor.
    name : str
        User-friendly (human-readable) name.
    units : str
        Identifies the type of data gathered from the sensor.
    model : str
        Identifies the model of the sensor.
    description : str
        Some information that describes the sensor. Meant for the user's purposes.
    last_calibration_id : int
        Used to identify a Sensor to a Calibration.
    last_calibration : Calibration
        Has the current calibration data for the sensor.
    message_queue: MessageQueue
        Message queue that contains message for the sensor.
    _meta_data : str
        Any extra information about the sensor.
    """

    id = models.UUIDField(default=new_ulid, primary_key=True, editable=False)
    # uuid = ULIDField(default=new_ulid, primary_key=True, editable=False)
    sensor_IOtype = models.BooleanField()
    sensor_type = models.CharField(default="", max_length=100)
    last_value = models.CharField(default="", max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    units = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    last_calibration = models.ForeignKey('Calibration', on_delete=models.CASCADE, related_name="last_calibration", null=True, blank=True)
    message_queue = models.ForeignKey(MessageQueue, on_delete=models.CASCADE, related_name='message_queue', null=True, blank=True)
    meta_data = models.JSONField(null=True, blank=True)

    def to_dict(self):
        """dict"""
        data = {
            'uuid': self.uuid,
            'sensor_type': self.sensor_type,
            'units': self.units,
            'description': self.description,
            'name': self.name,
            'model': self.model,
            'last_value': self.last_value,
            'sensor_IOtype': self.sensor_IOtype,
            'meta_data': self.meta_data
        }

        if self.last_calibration is not None:
            data['last_calibration'] = self.last_calibration.toDict()

        return data


class DataStream(models.Model):
    """
    id : int
        Unique identifier of this DataStream.
    sensor : str
        Used to identify a DataStream to a Sensor.
    owner : int
        Identifies the user for the datastream.  Currently unused.
    min_value : float
    max_value : float
    name : str
        User-friendly (human-readable) name.  Currently unused.
    description : str
        Some information that describes the datastream.  Currently unused.
    """

    id = models.UUIDField(default=new_ulid, primary_key=True, editable=False)
    # id = ULIDField(default=new_ulid, primary_key=True, editable=False)
    sensor = models.OneToOneField(Sensor, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    min_value = models.FloatField()
    max_value = models.FloatField()
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    paths = models.ForeignKey('Path', on_delete=models.PROTECT, related_name='paths')

    def to_dict(self):
        """dict"""
        return {
            'id': self.id,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'name': self.name,
            'description': self.description,
            'owner': self.owner,
            'sensor': self.sensor,
            "paths": [p.path for p in self.paths]
            }


class Path(models.Model):
    """
    id : int
        Unique identifier of this StreamPath.
    datastream : str
        What datastream does this path belong to.
    path : str
        The path String.
    """

    id = models.UUIDField(default=new_ulid, primary_key=True, editable=False)
    # id = ULIDField(default=new_ulid, primary_key=True, editable=False)
    datastream = models.ForeignKey(DataStream, on_delete=models.PROTECT)
    path = models.CharField(null=False, max_length=100)

    def to_dict(self):
        """dict"""
        return {
            'id': self.id,
            'datastream_id': self.datastream.id,
            'path': self.path
        }


class Calibration(models.Model):
    """
    id : int
        Unique identifier of this Calibration.
    sensor_id : str
        Used to identify a Calibration to a Sensor.
    timestamp : BigInt
        Indentifies the time in miliseconds when the calibration was stored.
    user : str
        Currently unused.
    coefficients: str
        Describes the coefficients of a polynomial function to a apply to the readings.
        Order of coefficients is in decreasing polynomial degree
        (e.g. [1, 0] represents the polynomial 1*x + 0)
    """


    id = models.UUIDField(default=new_ulid, primary_key=True, editable=False)
    # id = ULIDField(default=new_ulid, primary_key=True, editable=False)
    sensor = models.CharField(max_length=100)
    timestamp = models.BigIntegerField()
    user = models.CharField(max_length=100)
    coefficients = models.CharField(null=False, max_length=100)

    # pylint: disable=invalid-name
    def getCoefficients(self):
        """getcoefficients"""
        coefs = json.loads(self.coefficients)
        assert isinstance(coefs, list)
        return coefs

    def setCoefficients(self, coefs):
        """setCoefficients"""
        assert isinstance(coefs, (list, tuple))
        self.coefficients = json.dumps(coefs)

    def to_dict(self):
        """dict"""
        return {
            'id': self.id,
            'sensor_id': self.sensor.id,
            'timestamp': self.timestamp,
            'user': self.user,
            'coefficients': json.loads(self.coefficients)
        }
