"""
Contributing Authors:
    Victor Szczepanski (Visgence, Inc)
    Jessica Greenling (Visgence, Inc)

Queryer handles the main basestation behaviour as middleware between a mote on a serial port and a teleceptor server. The main function runs a simple query cycle on a given serial port.

This module can be run from the command line, in which case we require three arguments:

devicename -- a string representing the absolute path to a serial resource(device), e.g. /dev/ttyUSB0
queryrate -- an integer representing how frequently (number of seconds of delay) to query the mote located at devicename, e.g. 60
baudrate -- an integer representing the baudrate of the mote located at devicename, e.g. 9600. Note: Visgence motes typically use 9600.

Example usage:
python queryer.py -devicename /dev/ttyUSB0 -queryrate 60 -baudrate 9600

or

python queryer.py -d /dev/ttyUSB0 -q 60 -b 9600

Dependencies:

external libraries:
    serial
    requests
    json

local libraries:
    teleceptor

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


import serial
from serial import SerialException, SerialTimeoutException
import requests
from requests import ConnectionError
import time
import json
import argparse
import os
import logging

#local imports
import teleceptor

serverURL = "http://localhost:" + str(teleceptor.PORT) + "/api/delegation/"
serverDeleteURL = "http://localhost:" + str(teleceptor.PORT) + "/api/messages/"
pid = os.getpid()
starttime = time.time()
logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',level=logging.INFO)

class mote(serial.Serial):
    """
    This module extends the Serial port with functions to read from Visgence
    sensor motes (or any mote implementing the Visgence mote protocol).

    The module takes arguments for the serial port, timeout, and baudRate.

    All Visgence motes use a baudrate of 9600.
    """
    def __init__(self, deviceName, timeout, baudRate=9600):
        """
        Initializes the mote. Required arguments are deviceName and timeout.
        deviceName -- The path to the serial device as a string. For example: /dev/ttyUSB0
        timeout -- The timeout, in seconds, to wait for serial reads.
        baudRate -- The baud rate for the serial device. (default 9600)

        Additional Serial settings can be configured after creating the mote.
        """
        logging.debug("Calling serial.Serial...")
        super(serial.Serial,self).__init__(deviceName,timeout=3,baudrate=baudRate)
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



def main(deviceName="/dev/ttyUSB0",queryRate=60,baudRate=9600):
    """
    Creates a mote with the given deviceName, queryRate, and baudRate.
    Begins a query loop on the mote and sends POST requests to the server at serverURL.

    deviceName -- The path to the serial device the mote is connected to. Examples include /dev/ttyUSB0 and COM1.
    queryRate -- The rate to get readings from the mote and POST them.
    baudRate -- The baud rate for the mote.
    """
    logging.info("Inside queryer %s", deviceName)

    #make serial device
    device = mote(deviceName, timeout=3, baudRate=baudRate)

    #array of not sent readings, saved for various reasons
    payloads = []

    while(1):
		#get json from device
        info, readings = device.getReadings()

        try:
            info = json.loads(info)
        except ValueError:
            #device provided mangled JSON. Discard and continue?
            logging.error("Error: Mangled JSON from mote.")
            logging.debug("Mangled info data: %s", str(info))
            continue

        try:
            readings = json.loads(readings)
        except ValueError:
            #device provided mangled JSON. Discard and continue?
            logging.error("Mangled JSON data from mote.")
            logging.debug("Mangled readings data: %s", str(readings))
            continue

        for reading in readings:
            reading.append(time.time())

        #metadata info
        payload = {"info":info, "readings":readings}
        #add to each sensor
        for sensor in payload['info']['in'] + payload['info']['out']:
            sensor.update({'meta_data':{'uptime' : uptime(starttime), 'pid' : pid, 'tty' : device.deviceurl}})

        logging.info("Sending POST to server: %s", json.dumps(payload))
        payloads.append(payload)

        #build JSON to send to server

        try:
            response = requests.post(serverURL, data=json.dumps(payloads))
            payloads = []
        except ConnectionError:
            logging.error("Error connecting to server. Caching data: %s", str(payloads[-1]))


        logging.info("%s", str(response))
        logging.info("%s", str(response.text))

        if response.status_code == requests.codes.ok:
            responseData = json.loads(response.text)
            logging.info("%s", json.dumps(responseData))
            if 'newValues' in responseData:
                updateMote(device, (responseData['newValues']))


        #wait by queryRate
        time.sleep(queryRate)


def updateMote(moteHandle, newValues={}):
    """
    Updates the given mote's input sensors with the given values.

    moteHandle -- the mote object to update
    newValues -- the dictionary of sensorName: value pairs.

    newValues =
                    {
                        "in1": true,
                        "in2": false,
                        "in3": 70.0
                    }

    """
    if not newValues:
        return
    parsedNewValues = {}
    deleteMessages = []
    for sen in newValues:
        logging.info("sen: %s", sen)
        if len(newValues[sen]) == 0:
            continue
        message = newValues[sen][-1] #get the last message (ignore others)
        for senName, senMessage in message.items():
            if senName == "id":
                pass
                #deleteMessages.append({"sensor_id":moteHandle.uuid + sen,
                    #"message_id":senMessage})
            elif senName == "message":
                parsedNewValues[sen] = senMessage

    logging.info(parsedNewValues)
    logging.info(deleteMessages)
    info, readings = moteHandle.updateValues(parsedNewValues)
    info = json.loads(info)
    readings = json.loads(readings)
    logging.info("info after update: %s", info)
    logging.info("readings after update: %s", readings)


def uptime(starttime):
    """
    Convience method that returns the time since starttime.

    starttime -- the start time to compare against
    """
    return (time.time()-starttime)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Creates a process to query a Visgence mote for its data at a given rate')
    parser.add_argument('devicename', metavar='d',help='Path for the mote, e.g. /dev/ttyUSB0')
    parser.add_argument('queryrate', metavar='q',help="Rate to query the mote, in seconds",type=int)
    parser.add_argument('baudrate', metavar='b',help="Baud Rate for serial connection, e.g. 9600",type=int)

    args = parser.parse_args()

    print(args)
    main(deviceName=args.devicename,queryRate=args.queryrate,baudRate=args.baudrate)

