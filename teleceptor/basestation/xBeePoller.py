"""
Data collection from xBee radios.
Authors: Cyrille Gindreau (Visgence Inc.)

xBee radio must be set in api mode to be able to receive frames.
Makes use of Teleceptor api to insert data so server must be running.

TODO: Make platform independent. Currently set to run from OSX.
"""
import serial
import json
import logging
import time
import glob
import binascii
import requests
from xbee import ZigBee
from multiprocessing import Process

from teleceptor import USE_DEBUG

TELECEPTOR_URL = "http://localhost:8000/api/station"


def PollDevice(serialId):
    logging.debug('Starting Process.')
    ser = serial.Serial("/dev/tty.{}".format(serialId), 9600)
    xbee = ZigBee(ser, escaped=True)
    sampleRate = 1
    Alive = True
    while Alive:
        logging.debug('Getting data.')
        try:
            packet = xbee.wait_read_frame()
            logging.debug("Frame received")
            logging.debug(packet)
            SendToTeleceptor(packet)
        except Exception, e:
            logging.error('Error getting data')
            logging.error(e)
            Alive = False
        time.sleep(sampleRate)


def SendToTeleceptor(packet):
    print packet
    uuid = 'xBee_{}'.format(binascii.hexlify(packet['source_addr_long']))
    sensor = [{
        "info": {
            "uuid": uuid,
            "name": uuid,
            "description": 'Readings from an xBee',
            "out": [],
            "in":[]
        },
        "readings": []
    }]
    for i in packet['samples']:
        for key in i:
            sensor[0]['info']['in'].append({
                "name": "_{}".format(key),
                "sensor_type": "float",
                "timestamp": time.time(),
                "meta_data": {}
            })
            sensor[0]['readings'].append(
                ["_{}".format(key), float(i[key]), time.time()],
            )

    try:
        requests.post(TELECEPTOR_URL, data=json.dumps(sensor))
    except Exception, e:
        logging.error("Error sending data to teleceptor: {}".format(uuid, e))


if __name__ == "__main__":
    if USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)
    logging.info('Starting xBee poller.')
    pollRate = 60
    currentDevices = {}
    while(True):
        ports = glob.glob('/dev/tty.*')
        logging.debug('Polling.')
        for i in ports:
            curPort = i.split('.')[1]
            if curPort.startswith('usb'):
                if curPort not in currentDevices:
                    logging.debug('New device found!')
                    p = Process(target=PollDevice, args=(curPort, ))
                    p.start()
                    currentDevices[curPort] = p
        time.sleep(pollRate)
