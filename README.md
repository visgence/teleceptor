# Teleceptor
#### 2014 Visgence Inc.
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

# Design Goals


# Getting Started (Ubuntu and Raspberry Pi)
## Dependencies
```
sqlalchemy
pip
cherrypy (pip install --no-use-wheel cherrypy on windows)
requests
psycopg2
pyserial
```
## Setting Up Teleceptor
1. Pull the latest version of Teleceptor from GitHub.
2. To install a local config customizable first run ```./teleceptorcmd copyconfig``` app will print path
3. Start up Elastic Search, Kibana, and Postgres and in your config, make sure they Everything is pointing to the correct destination.
4. In teleceptor folder, run command ```./teleceptorcmd setup``` and wait until _Done!_ is printed.
  * **Note:** All commands should be run in the teleceptor folder unless installed with pip or setuptools
5. Run command ```./teleceptorcmd runserver 0.0.0.0:8000```. You will now be running teleceptor as a local host.
6. Open up either a Chrome or Mozilla Firefox browser and go to page http://0.0.0.0:8000/
  * If you do not have any sensors connected, you can run the loadfixtures command below.
7. Set up desired sensors and start collecting data.(_See below for setting up sensors_)

## Example Data
The ```./teleceptorcmd loadfixtures``` command will run a program that will create two datastreams and fill them with an hours worth of data in the form of a sine curve.

## Example Sensor
The ```./teleceptorcmd btcmote``` command will run a program that requests data from http://blockchain.info/ticker and sends the data to teleceptor.


# Sensor Firmware
Sensor firmware can be found in the [firmware](https://github.com/visgence/teleceptor/tree/master/firmware) folder. Download the appropriate firmware for your type of sensor, and then upload it to your sensor.


## Setting Up Sensors
1. Plug in your sensor through a USB port.
* Make sure you have the most current firmware for your sensor. (_See **Sensor Firmware**._)
2. Run command ```./teleceptorcmd serialPoller PathOfSensor```. This will begin to look for sensors via USB ports.
Note: On OS X, to find the name of your sensor, in terminal, type ```ls /dev/```. This will give you a list of all sensors currently connected. To use the serialPoller then, you would type ```./teleceptorcmd serialPoller /dev/tty.myUSBSensor1234```.



# Teleceptor Front-End Usage
* To view sensor data that has been collected, click on a sensor under the _Sensors_ tab.
* To look at a certain time period of data, select a range under the _Time Controls_ tab.
  * :star: Specific data can also be viewed by passing the mouse on the graph to observe data points and the time it was collected.
  * :star2: By clicking and dragging on a certain part of _either_ graph, you can zoom-in on points.
* Some information about the sensor is editable and will change the graph accordingly such as _Units_ or _Calibration_.
  * Be sure to save after editing for the configuration information to be available later.
  * _Metadata_ cannot be changed. However, you can change it in the firmware and then re-upload the firmware to the sensor.
* If you download updates from teleceptor but and are not sure if the webpage is up-to-date as well, clear your web browser's cache:
  * **Chrome:** Right-click in a blank spot on the page -> Inspect element -> Settings (gear symbol) -> Disable cache (while DevTools is open) -> Refresh the page
 * **Mozilla Firefox**: _ctrl+Shift+R_ will reload the page without cache and/or _ctrl+Shift+Delete_ -> Details -> Cache checkbox -> Clear Now


