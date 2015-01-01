"""
Contributing Authors:
    Evan Salazar (Visgence, Inc)
    Victor Szczepanski (Visgence, Inc)
    Jessica Greenling (Visgence, Inc)


Poller can be run with or without the server.
./teleceptorcmd tcppoller
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

import multiprocessing
import subprocess
import re
import time
import argparse
import logging

#Local Imports
from teleceptor import TCP_POLLER_HOSTS, USE_DEBUG
from teleceptor.basestation import GenericQueryer


def tcpDevices(previousDevices,devices):

    for dev in devices:
        if dev in previousDevices:
            continue
        logging.debug("Got new host:port %s", dev)
        host,port = dev.split(":")
        port = int(port)

        #make a new TCPMote to pass to new process
        logging.debug("Creating new TCPMote.")

        device = TCPMote(host, port, 3, debug=USE_DEBUG)

        logging.debug("Succeeded making device, starting query process.")

        p = multiprocessing.Process(target=GenericQueryer.main,name=dev,args=(device,10))
        p.start()

        logging.debug("Began process.")

    #print(stdout_list)
    return [p.name for p in multiprocessing.active_children()]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Creates a poller that checks serial ports periodically and creates a new query process for new motes.')
    parser.add_argument('debug', metavar='d',help='Turns on or off the debug messages for spawned queryers.')
    parser.set_defaults(debug=False)
    args = parser.parse_args()

    if args.debug == "True" or args.debug == "true" or args.debug == "t":
        USE_DEBUG=True
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',level=logging.INFO)

    logging.info(args)
    logging.debug("Beginning polling cycle.")

    deviceList = TCP_POLLER_HOSTS
    foundDevices = []

    while(1):
        foundDevices = tcpDevices(foundDevices,deviceList)
        time.sleep(6)


