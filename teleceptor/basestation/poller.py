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
import re
import time
#Local Imports
from teleceptor.basestation import queryer


def grepfinddevices(previousDevices=[]):
        """
        Searches for a mote connected through a USB port.
        Gathers info about all ports from /dev/, splits each item by a newline character, and a process is created for each new mote found. A mote is described by having these two properties in the /dev/ folder: '    DRIVERS=="ftdi_sio" and '    ATTRS{product}=="FT232R USB UART"

        previousDevices : a list of process names
        	Refers to previously found motes that were stored to this list via their process name.
        """
	df = subprocess.Popen("ls /dev | grep ttyUSB",shell=True,stdout=subprocess.PIPE,)
	stdout_list = df.communicate()[0].split('\n')

	for dev in stdout_list:
		if dev == "":
			continue
		if dev in previousDevices:
			continue
		print dev
		devpath = "/dev/" + dev
		bashcommand = "udevadm info -a -n " + devpath
		#print bashcommand + 'j'
		df2 = subprocess.Popen(bashcommand,shell=True,stdout=subprocess.PIPE,)
		udev_list = df2.communicate()[0].split('\n')
		#print udev_list
		if '    DRIVERS=="ftdi_sio"' in udev_list and '    ATTRS{product}=="FT232R USB UART"' in udev_list:
			print "Looks like device " + dev + " is a mote. Making process..."
			p = multiprocessing.Process(target=queryer.main,name=dev,args=(devpath,3))
			p.start()
			print "Made process"

	#print(stdout_list)
	return [p.name for p in multiprocessing.active_children()]


if __name__ == "__main__":
	#print finddevices()

	foundDevices = []

	while(1):
		foundDevices = grepfinddevices(foundDevices)

		time.sleep(6)


