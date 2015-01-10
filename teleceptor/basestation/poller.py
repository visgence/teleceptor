"""
Contributing Authors:
    Victor Szczepanski (Visgence, Inc)
    Jessica Greenling (Visgence, Inc)


Poller actively searches for newly connected motes.  Each new mote found is sent as a new process to queryer.  Previously found motes are still returned in the list of active processes.  If a mote is disconnected, it is not returned in the list.

Poller can be run with or without the server.


Example usage:
python poller.py

or

./teleceptorcmd poller


Dependencies:

local libraries:
    queryer


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
import time
import logging
from serial import SerialException, SerialTimeoutException

#Local Imports
from teleceptor.basestation import GenericQueryer, SerialMote
from teleceptor import USE_DEBUG



def grepfinddevices(previousDevices=[]):
    """
        Searches for a mote connected through a USB port.
        Gathers info about all ports from /dev/, splits each item by a newline character, and a process is created for each new mote found. A mote is described by having these two properties in the /dev/ folder: '    DRIVERS=="ftdi_sio" and '    ATTRS{product}=="FT232R USB UART"

        previousDevices : a list of process names
            Refers to previously found motes that were stored to this list via their process name.
    """
    logging.debug("Getting all available ttyUSB paths.")
    df = subprocess.Popen("ls /dev | grep ttyUSB",shell=True,stdout=subprocess.PIPE,)
    stdout_list = df.communicate()[0].split('\n')

    logging.debug("Got paths: %s", str(stdout_list))
    for dev in stdout_list:
        if dev == "":
            continue
        if dev in previousDevices:
            continue
        logging.info("Found new device %s", dev)
        devpath = "/dev/" + dev

        bashcommand = "udevadm info -a -n " + devpath

        logging.debug("Getting device information with command %s", bashcommand)

        df2 = subprocess.Popen(bashcommand,shell=True,stdout=subprocess.PIPE,)
        udev_list = df2.communicate()[0].split('\n')

        logging.debug("Got udev_list: %s", str(udev_list))

        if '    DRIVERS=="ftdi_sio"' in udev_list and '    ATTRS{product}=="FT232R USB UART"' in udev_list:
            logging.debug("Looks like device %s is a mote. Making process...", dev)

                p = multiprocessing.Process(target=GenericQueryer.main,name=dev,args=(3,), kwargs={"deviceName":devpath, "timeout":3, "debug":USE_DEBUG})
                p.start()

                logging.debug("Began process.")

    #print(stdout_list)
    return [p.name for p in multiprocessing.active_children()]


if __name__ == "__main__":
    if USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',level=logging.INFO)

    logging.debug("Beginning polling cycle.")

    foundDevices = []

    while(1):
        foundDevices = grepfinddevices(foundDevices)

        time.sleep(6)


