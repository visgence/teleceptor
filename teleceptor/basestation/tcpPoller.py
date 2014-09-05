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
#Local Imports
from teleceptor import TCP_POLLER_HOSTS
from teleceptor.basestation import tcpSensor


def tcpDevices(previousDevices,devices):

        for dev in devices:
		if dev in previousDevices:
			continue

                host,port = dev.split(":")
		port = int(port)
                print dev
                p = multiprocessing.Process(target=tcpSensor.main,name=dev,args=(host,port,10))
                p.start()
                print "Made process"

	#print(stdout_list)
	return [p.name for p in multiprocessing.active_children()]


if __name__ == "__main__":
	#print finddevices()

        deviceList = TCP_POLLER_HOSTS
	foundDevices = []

	while(1):
		foundDevices = tcpDevices(foundDevices,deviceList)
		time.sleep(6)


