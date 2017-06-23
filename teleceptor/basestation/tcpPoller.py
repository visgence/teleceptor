"""
Authors:
    Evan Salazar (Visgence, Inc)
    Victor Szczepanski (Visgence, Inc)
    Jessica Greenling (Visgence, Inc)


Poller can be run with or without the server.

"""

import multiprocessing
import time
import logging

# Local Imports
from teleceptor import TCP_POLLER_HOSTS, USE_DEBUG
from teleceptor.basestation import GenericQueryer


def tcpDevices(previousDevices, devices):

    for dev in devices:
        if dev in previousDevices:
            continue
        logging.debug("Got new host:port %s", dev)
        host, port = dev.split(":")
        port = int(port)

        p = multiprocessing.Process(target=GenericQueryer.main, name=dev, args=(10, ), kwargs={"host": host, "port": port, "timeout": 3, "debug": USE_DEBUG})
        p.start()

        logging.debug("Began process.")

    return [pr.name for pr in multiprocessing.active_children()]


if __name__ == "__main__":
    if USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

    logging.debug("Beginning polling cycle.")

    deviceList = TCP_POLLER_HOSTS
    foundDevices = []

    while(1):
        foundDevices = tcpDevices(foundDevices, deviceList)
        time.sleep(6)
