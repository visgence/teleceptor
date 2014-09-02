#Teleceptor
####2014 Visgence Inc.
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

#Design Goals


#Getting Started (Ubuntu and Raspberry Pi)
##Dependencies
```
jinja2
sqlalchemy
whisper
pip
cherrypy (pip install --no-use-wheel cherrypy)
requests
```
##Setting Up Teleceptor
1. Pull the latest version of Teleceptor from GitHub.
2. In teleceptor folder, run command ```./teleceptorcmd setup``` and wait until _Done!_ is printed.
  * **Note:** All commands should be run in the teleceptor folder
3. Run command ```./teleceptorcmd runserver```. You will now be running teleceptor as a local host.
4. Open up either a Chrome or Mozilla Firefox browser and go to page [http://0.0.0.0:8000/] (http://0.0.0.0:8000/)
  * If you do not have any sensors connected, you should see two default sensors producing a graph per tab with random data.
5. Set up desired sensors and start collecting data.(_See below for setting up sensors_)

##Setting Up Sensors
1. Run command ```./teleceptorcmd poller```. This will begin to look for sensors via USB ports.
2. Plug in your sensor through a USB port.
  * Make sure you have the most current firmware for your sensor. (_See **Sensor Firmware**._)


#Sensor Firmware
Sensor firmware can be found in the [firmware](https://github.com/visgence/teleceptor/tree/master/firmware) folder. Download the appropriate firmware for your type of sensor, and then upload it to your sensor.

**Important:**
* You will need to download aJSON and add it to your adruino IDE.
* In the .ino file that you download for your firmware, change the uuid found in _static const char jsonData[ ]_ to be a unique name of your choosing.


#Teleceptor Front-End Usage
* To view sensor data that has been collected, click on a sensor under the _Sensors_ tab.
* To look at a certain time period of data, select a range under the _Time Controls_ tab.
  * :star: Specifc data can also be viewed by passing the mouse on the graph to observe data points and the time it was collected.
  * :star2: By clicking and dragging on a certain part of _either_ graph, you can zoom-in on points.
* Some information about the sensor is editable and will change the graph accordingly such as _Units_ or _Calibration_.
  * Be sure to save after editing for the configuration information to be available later.
  * _Metadata_ cannot be changed. However, you can change it in the firmware and then re-upload the firmware to the sensor.
* If you download updates from teleceptor but and are not sure if the webpage is up-to-date as well, clear your web browser's cache:
  * **Chrome:** Right-click in a blank spot on the page -> Inspect element -> Settings (gear symbol) -> Disable cache (while DevTools is open) -> Refresh the page
 * **Mozilla Firefox**: _ctrl+Shift+R_ will reload the page without cache and/or _ctrl+Shift+Delete_ -> Details -> Cache checkbox -> Clear Now


