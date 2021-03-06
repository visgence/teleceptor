"""
Contributing Authors:
    Victor Szczepanski (Visgence, Inc)

Simulates a teleimperium-like TCP sensor.
"""

import socket
import json
import logging

from teleceptor import USE_DEBUG

TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024

# basic sensor for testing without any input sensors.
SENSOR_INFO = {
    "Desc": "Virtual TCP Sensor",
    "out": [{
        "name": "VirtualOut1",
        "s_t": "int",
        "u": "real"
    }],
    "uuid": "VTCP001",
    "mode": "Virtual TCP Sensor"
}
IN_STATES = {
    # would be of form "sensorname": state
}

SENSOR_READINGS = [["VirtualOut1", 3.2]]


def parseJSON(data):

    # Parses incoming update data and tries to update any input sensors given in the data.

    j = json.loads(data)
    if "in" not in SENSOR_INFO:
        return
    for sensorname in j.iterkeys():
        try:
            IN_STATES["in"][sensorname] = j[sensorname]
        except Exception:
            pass


def main():
    """
    Simple TCP server that simulates a teleimperium-like sensor that is compatible with GenericQueryer basestation.

    Creates a socket connection with ip and port defined above, then
    waits forever for a connection.
    """

    if USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)

    while 1:
        (conn, addr) = s.accept()
        logging.debug('Connection address:', addr)

        data = conn.recv(1)
        if not data:
            break
        logging.debug("received data:", data)

        # check for command char
        if data[0] == '@':
            # parse rest of data as JSON
            command = conn.recv(BUFFER_SIZE)
            try:
                parseJSON(command)
            except Exception, e:
                logging.debug(e)
                continue
        elif data[0] == '%':
            logging.debug("in % block. Sending:")
            logging.debug(json.dumps(SENSOR_INFO) + '\n' + json.dumps(SENSOR_READINGS))

            conn.send(json.dumps(SENSOR_INFO) + '\n')
            conn.send(json.dumps(SENSOR_READINGS) + '\n')


if __name__ == "__main__":
    main()
