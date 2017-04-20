"""
Authors:
    Victor Szczepanski (Visgence, Inc)

Encapsulates a TCP socket connection and provides several
methods used by the Teleceptor Basestation software.

Interface functions:
getReadings() //returns tuple of JSON strings from Teleimperium-like device
updateValues(newValues) //Accepts a dictionary of sensorName: value pairs. Returns tuple as getReadings()


"""
import socket
from requests import ConnectionError
import json
import logging


class TCPMote():
    def __init__(self, host, port, timeout=3, debug=False):
        """
        Initializes the TCP socket connection. Required arguments are host and port
        host -- The IP address of the Teleimperium-like device as a string. For example 192.168.55.12
        port -- The port of the Teleimperium-like device. For example 2000
        timeout -- The timeout, in seconds, to wait for TCP communications.
        debug -- Whether to display debug messages.

        """
        if debug:
            logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
        else:
            logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

        logging.debug("Creating socket connection to host %s and port %s", str(host), str(port))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))

        logging.debug("Made socket connection.")
        s.settimeout(timeout)

        self._device = s.makefile()
        self.metadata = {'host': host, 'port': port}

        logging.info("Created mote with metadata %s", str(self.metadata))

        logging.debug("Trying to read any ack characters...")
        try:
            logging.debug("Got ack characters: %s", repr(self._device.read(7)))

        except socket.timeout as e:
            logging.debug("No Hello Line")

    def getReadings(self):
        """
        Gets the JSON formatted information from the mote on one line and current sensor readings on the next line.
        Returns two strings: the JSON info and the readings, where the info is a JSON object(dictionary) and readings is a JSON array(list).

        If the mote is configured correctly, it should return two JSON objects.

        >>> info, readings = self.getReadings()
        >>> json.loads(info)
        >>> json.loads(readings)

        .. todo::
            Raise generic timeout exception if we get a sockettimeout.

        """
        info = None
        readings = None
        try:
            logging.debug("Writing %...")
            self._device.write('%')

            logging.debug("Flushing...")
            self._device.flush()

            logging.debug("Reading a line...")
            info = self._device.readline()
            logging.debug("Read line %s \n Reading a line...", info)
            readings = self._device.readline()
            logging.debug("Read line %s.", readings)
        except socket.timeout as e:
            # try again
            logging.debug("Timed out trying to read from device. Trying again...")
            try:
                logging.debug("Writing %...")
                self._device.write('%')

                logging.debug("Flushing...")
                self._device.flush()

                logging.debug("Reading a line...")
                info = self._device.readline()

                logging.debug("Read line %s \n Reading a line...", info)
                readings = self._device.readline()

                logging.debug("Read line %s", readings)
            except socket.timeout as st:
                logging.error("Timed out trying to read from device twice. Device may be unresponsive.")
                return None, None

        return info, readings

    def updateValues(self, newValues={}):
        """
        Sends values to update this mote's input sensors. The format should be a dictionary with key/value pairs in the form sensorName: value.

        :param newValues: The dictionary of sensorName: value pairs.
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
            logging.debug("Sending new Values: %s", json.dumps(newValues))

            logging.debug("Writing @")
            # TODO: Check if this is correct code.
            self._device.write('@')
            self._device.flush()

            logging.debug("Writing new values.")
            self._device.write(json.dumps(newValues))
            self._device.flush()
        # get values from sensor
        return self.getReadings()
