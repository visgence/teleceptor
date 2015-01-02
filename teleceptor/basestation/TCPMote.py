"""
Contributing Authors:
    Victor Szczepanski (Visgence, Inc)

TCPMote.py

Encapsulates a TCP socket connection and provides several
methods used by the Teleceptor Basestation software.

Interface functions:
getReadings() //returns tuple of JSON strings from Teleimperium-like device
updateValues(newValues) //Accepts a dictionary of sensorName: value pairs. Returns tuple as getReadings()


"""
import socket
from requests import ConnectionError
import json

class TCPMote():
    def __init__(self,host,port,timeout=3, debug=False):
        """
        Initializes the TCP socket connection. Required arguments are host and port
        host -- The IP address of the Teleimperium-like device as a string. For example 192.168.55.12
        port -- The port of the Teleimperium-like device. For example 2000
        timeout -- The timeout, in seconds, to wait for TCP communications.
        debug -- Whether to display debug messages.

        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.settimeout(timeout)
        self._device = s.makefile()

        try:
            print self._device.read(7)

        except socket.timeout as e:
            print "NO Hello Line"


    def getReadings():
        """
        Gets the JSON formatted information from the mote on one line and current sensor readings on the next line. Returns two strings: the JSON info and the readings, where the info is a JSON object(dictionary) and readings is a JSON array(list).

        If the mote is configured correctly, it should return two JSON objects.

        >>> info, readings = self.getReadings()
        >>> json.loads(info)
        >>> json.loads(readings)

        """
        #TODO: Raise generic timeout exception if we get a sockettimeout.
        self._device.write('%')
        self._device.flush()
        info = self._device.readline()
        readings = self._device.readline()
        return info, readings

    def updateValues(device,newValues={}):
        """
        Sends values to update this mote's input sensors. The format should be a dictionary with key/value pairs in the form sensorName: value.

        newValues -- The dictionary of sensorName: value pairs.

        newValues =
                    {
                        "in1": true,
                        "in2": false,
                        "in3": 70.0
                    }

        >>> info, readings = this.updateValues()
        >>> json.loads(info)
        >>> json.loads(readings)

        """
        if newValues:
            logging.info("Sending new Values: %s", json.dumps(newValues))
            self._device.write('@') #TODO: Check if this is correct code.
            self._device.flush()
            self._device.write(json.dumps(newValues))
            self._device.flush()
        #get values from sensor
        return self.getReadings()
