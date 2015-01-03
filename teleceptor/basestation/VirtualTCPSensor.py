"""
Contributing Authors:
    Victor Szczepanski (Visgence, Inc)
VirtualTCPSensor.py


"""

import socket
import json

TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024

SENSOR_INFO = {"Desc": "Virtual TCP Sensor",
                "out": [
                        {
                            "name": "VirtualOut1",
                             "s_t": "int",
                             "u": "real"
                        }],
                "uuid": "VTCP001",
                "mode": "Virtual TCP Sensor"

                }
IN_STATES = {

}#would be of form "sensorname": state
SENSOR_READINGS = [["VirtualOut1", 3.2]]

def parseJSON(data):
    j = json.loads(data)
    if "in" not in SENSOR_INFO:
        return
    for sensorname in j.iterkeys():
        try:
            IN_STATES["in"][sensorname] = j[sensorname]
        except:
            pass


def main():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)




    while 1:
        (conn, addr) = s.accept()
        print 'Connection address:', addr

        data = conn.recv(1)
        if not data:
            break
        print "received data:", data

        #check for command char
        if data[0] == '@':
            #parse rest of data as JSON
            command = conn.recv(BUFFER_SIZE)
            try:
                parseJSON(command)
            except:
                continue
        elif data[0] == '%':
            print "in % block. Sending:"
            print json.dumps(SENSOR_INFO) + '\n' + json.dumps(SENSOR_READINGS)
            #return SENSOR_INFO
            conn.send(json.dumps(SENSOR_INFO) + '\n')
            conn.send(json.dumps(SENSOR_READINGS) + '\n')


if __name__ == "__main__":
    main()
