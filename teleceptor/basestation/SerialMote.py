"""
Contributing Authors:
    Victor Szczepanski (Visgence, Inc)

SerialMote.py

Encapsulates a Serial connection and provides several
methods used by the Teleceptor Basestation software.

Interface functions:
getReadings() //returns tuple of JSON strings from Teleimperium-like device
updateValues(newValues) //Accepts a dictionary of sensorName: value pairs. Returns tuple as getReadings()


"""
import serial
from serial import SerialException, SerialTimeoutException
import json
import logging
import time


class SerialMote(serial.Serial):
    """
    This module extends the Serial port with functions to read from Visgence
    sensor motes (or any mote implementing the Visgence mote protocol).

    The module takes arguments for the serial port, timeout, and baudRate.

    All Visgence motes use a baudrate of 9600.
    """
    def __init__(self, deviceName, timeout, baudRate=9600, debug=False):
        """
        Initializes the mote. Required arguments are deviceName and timeout.
        deviceName -- The path to the serial device as a string. For example: /dev/ttyUSB0
        timeout -- The timeout, in seconds, to wait for serial reads.
        baudRate -- The baud rate for the serial device. (default 9600)
        debug -- Whether to display debug messages.

        Additional Serial settings can be configured after creating the mote.
        """
        logging.debug("Calling serial.Serial...")
        super(serial.Serial, self).__init__(deviceName,timeout=timeout,baudrate=baudRate)
        #wait 5 seconds to allow mote time to boot
        time.sleep(5)
        logging.debug("Finished creating serial object as self")
        logging.info("Created mote %s with timeout %s seconds and %s baudrate", deviceName, str(timeout), str(baudRate))

        #get reading to make sure device is alive
        info = ""
        #get a reading to make sure device is alive.
        try:
            info, readings = self.getReadings()
        except SerialTimeoutException, ste:
            #device may not be ready yet. Try again.
            raise ste
        except SerialException, se:
            #failed device
            raise se

        info = json.loads(info)
        self.uuid = info['uuid']
        self.deviceurl = deviceName

    def getReadings(self):
        """
        Gets the JSON formatted information from the mote on one line and current sensor readings on the next line. Returns two strings: the JSON info and the readings, where the info is a JSON object(dictionary) and readings is a JSON array(list).

        If the mote is configured correctly, it should return two JSON objects.

        >>> info, readings = self.getReadings()
        >>> json.loads(info)
        >>> json.loads(readings)

        """
        self.write('%')
        info = self.readline()
        readings = self.readline()
        return info, readings

    def updateValues(self, newValues={}):
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
            self.write('@') #TODO: Check if this is correct code.
            self.write(json.dumps(newValues))
        #get values from sensor
        return self.getReadings()
