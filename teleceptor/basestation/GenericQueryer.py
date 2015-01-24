"""
Contributing Authors:
    Victor Szczepanski (Visgence, Inc)

GenericQueryer.py

GenericQueryer handles the main basestation behaviour. It expects
to receive a device (e.g. SerialMote or TCPMote) that has exposed functions

getReadings()
updateValues(newValues)

See either TCPMote or SerialMote for example usages
"""
import json
import time
import logging
import requests
from requests import ConnectionError
import os


#local imports
import teleceptor
from teleceptor.basestation import TCPMote, SerialMote


serverURL = "http://localhost:" + str(teleceptor.PORT) + "/api/station/"
serverDeleteURL = "http://localhost:" + str(teleceptor.PORT) + "/api/messages/"
pid = os.getpid()
starttime = time.time()

def moteFactory(**kwargs):
    """
    Generates a new device based on the input kwargs.
    kwargs -- the keyword arguments for the device. Currently the GenericQueryer supports two devices - TCPMote and SerialMote. Arguments for TCPMote should be of the form
            host = "192.168.0.0"
            port = 5000
            debug = False *
        Arguments for SerialMote should be of the form
            deviceName = "/dev/ttyUSB0"
            timeout = 5
            baudrate = 9600 *
            debug = False *

        Note that arguments marked with a * are optional. See the documentation for the respective device for default values.
    """
    device = None
    if "host" in kwargs.iterkeys() and "port" in kwargs.iterkeys():
        device = TCPMote.TCPMote(**kwargs)

    if "deviceName" in kwargs.iterkeys():
        device = SerialMote.SerialMote(**kwargs)

    return device



def main(queryRate=60, **kwargs):
    """
    Begins a query loop on the device and sends POST requests to
    the server at serverURL.

    queryRate -- The rate to get readings from the mote and POST them.
    kwargs -- the keyword arguments for the device. Currently the GenericQueryer supports two devices - TCPMote and SerialMote. Arguments for TCPMote should be of the form
            host = "192.168.0.0"
            port = 5000
            debug = False *
        Arguments for SerialMote should be of the form
            deviceName = "/dev/ttyUSB0"
            timeout = 5
            baudrate = 9600 *
            debug = False *

        Note that arguments marked with a * are optional. See the documentation for the respective device for default values.
    """

    if teleceptor.USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',level=logging.INFO)

    #create the device from kwargs
    try:
        device = moteFactory(**kwargs)
    except:
        logging.error("Provided kwargs caused exception during mote creation.\n kwargs: %s", str(kwargs))
        return

    if device is None:
        logging.error("Provided kwargs are not compatible with any Motes.\n kwargs: %s", str(kwargs))
        return

    #array of not sent readings, saved for various reasons
    payloads = []

    while(1):
        #get json from device
        info, readings = device.getReadings() #TODO: catch generic exception

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

        logging.debug("Info and Readings are proper JSON: %s \n %s", json.dumps(info), json.dumps(readings))

        for reading in readings:
            reading.append(time.time())

        #metadata info
        payload = {"info":info, "readings":readings}
        #add to each sensor
        sensors = []
        if 'out' in payload['info']:
            sensors = payload['info']['out']
        if 'in' in payload['info']:
            sensors = sensors + payload['info']['in']

        for sensor in sensors:
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

            sensor.update({'meta_data':dict({'uptime' : uptime(starttime), 'pid' : pid}, **device.metadata)})

        logging.info("Sending POST to server: %s", json.dumps(payload))
        payloads.append(payload)

        #build JSON to send to server

        try:
            response = requests.post(serverURL, data=json.dumps(payloads))
            payloads = []
        except ConnectionError:
            logging.error("Error connecting to server. Caching data: %s", str(payloads[-1]))
            continue


        logging.info("Server response: %s", str(response.text))

        if response.status_code == requests.codes.ok:
            responseData = json.loads(response.text)
            logging.debug("Messages from server: %s", json.dumps(responseData))
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
    for sen in newValues:
        logging.debug("sen: %s", sen)
        if len(newValues[sen]) == 0:
            continue
        message = newValues[sen][-1] #get the last message (ignore others)
        for senName, senMessage in message.items():
            if senName == "id":
                pass
            elif senName == "message":
                parsedNewValues[sen] = senMessage

    logging.debug("Values to send to mote: %s", str(parsedNewValues))
    info, readings = moteHandle.updateValues(parsedNewValues)
    info = json.loads(info)
    readings = json.loads(readings)
    logging.debug("info after update: %s", info)
    logging.debug("readings after update: %s", readings)

    return info, readings

def uptime(starttime):
    """
    Convience method that returns the time since starttime.

    starttime -- the start time to compare against
    """
    return (time.time()-starttime)

