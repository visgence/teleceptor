"""
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

import requests
import time
import json
import argparse
import sys
import socket
from requests import ConnectionError
import os
import logging
logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',level=logging.INFO)
#local imports
import teleceptor

serverURL = "http://localhost:" + str(teleceptor.PORT) + "/api/delegation/"
pid = os.getpid()

def getReadings(device):
    device.write('%')
    device.flush()
    info = device.readline()
    readings = device.readline()
    return info, readings

def updateValues(device,newValues={}):
    if newValues:
        logging.info("Sending new Values: %s", json.dumps(newValues))
        device.write('@') #TODO: Check if this is correct code.
        device.flush()
        device.write(json.dumps(newValues))
        device.flush()
    #get values from sensor
    return getReadings(device)

def main(host="192.168.55.12",port=2000,queryRate=60):
    print "in queryer"
    #make serial device

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.settimeout(3)
    device = s.makefile()

    timeoutretry = False

    #Read initinal hello:
    try:
        print device.read(7)

    except socket.timeout as e:
        print "NO Hello Line"

    #array of not sent readings, saved for various reasons
    payloads = []
    starttime = time.time()

    while(1):
		#get json from device
        try:
            logging.debug("Sending command:")
            receivedJSON, receivedData = getReadings(device)
        except socket.timeout as e:
            #device is still not ready. Just exit and poller may try again.
            logging.error("Error reading device")
            logging.error(str(e))
            continue

        try:
            info = json.loads(receivedJSON)
        except ValueError:
            #device provided mangled JSON. Discard and continue?
            logging.error("Error: Mangled Value JSON from mote.")
            logging.error(receivedJSON)
            continue

        try:
            logging.debug("parse receive")
            readings = json.loads(receivedData)
            logging.debug(str(readings))
        except ValueError:
            #device provided mangled JSON. Discard and continue?
            logging.error("Error: Mangled Data JSON data from mote.")
            logging.error(receivedData)
            continue

        for reading in readings:
            reading.append(time.time())

        #metadata info
        uptime = time.time() - starttime
        payload = {"info":info, "readings":readings}
        #add to each sensor
        for sensor in payload['info']['in'] + payload['info']['out']:

            #do some translation from sensor mini-json to full JSON
            if "t" not in sensor and "timestamp" not in sensor:
                sensor.update({'timestamp':0})
            elif "timestamp" not in sensor:#then t is in sensor, translate t to timestamp
                sensor['timestamp'] = sensor['t']
                del sensor['t']

            if "s_t" in sensor:
                sensor['sensor_type'] = sensor['s_t']
                del sensor['s_t']

            if "desc" in sensor:
                sensor['description'] = sensor['desc']
                del sensor['desc']

            if "u" in sensor:
                sensor['units'] = sensor['u']
                del sensor['u']

            if "model" not in sensor:
                sensor['model'] = ""

            if "scale" not in sensor:
                sensor['scale'] = [1, 0]

            if "desc" not in sensor and "description" not in sensor:
                sensor['description'] = ""


            sensor.update({'meta_data':{'uptime' : uptime, 'pid' : pid, 'host' : host,'port':port}})

        payloads.append(payload)

        #build JSON to send to server
        try:
            response = requests.post(serverURL,data=json.dumps(payloads))
            payloads = []
            print response
        except ConnectionError:
            print "Error connecting to server. Caching data:"
            print payloads[-1]

        if response.status_code == requests.codes.ok:
            responseData = json.loads(response.text)
            logging.info("%s", json.dumps(responseData))
            if 'newValues' in responseData:
                updateMote(device, (responseData['newValues']))

        #wait by queryRate
        time.sleep(queryRate)


def updateMote(moteHandle, newValues={}):
    if not newValues:
        return
    parsedNewValues = {}
    deleteMessages = []
    for sen in newValues:
        logging.info("sen: %s",sen)
        if len(newValues[sen]) == 0:
            continue
        message = newValues[sen][-1] #get the last message (ignore others)
        for senName, senMessage in message.items():
            if senName == "id":
                pass
            elif senName == "message":
                parsedNewValues[sen] = senMessage

    logging.info(parsedNewValues)
    logging.info(deleteMessages)
    info, readings = updateValues(moteHandle, parsedNewValues)
    info = json.loads(info)
    readings = json.loads(readings)
    logging.info("info after update: %s", info)
    logging.info("readings after update: %s", readings)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Creates a process to query a Visgence mote for its data at a given rate')
    parser.add_argument('host', metavar='h',help='Host for the mote, e.g. /dev/ttyUSB0')
    parser.add_argument('queryrate', metavar='q',help="Rate to query the mote, in seconds",type=int)
    parser.add_argument('port', metavar='p',help="TCP Port",type=int)

    args = parser.parse_args()

    print(args)
    main(host=args.host,queryRate=args.queryrate,port=args.port)

