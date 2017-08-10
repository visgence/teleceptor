# Teleceptor

Teleceptor is an open-source data logger and feature-rich dashboard.

## Features
Data-sources:
  * Serial
  * TCP
  * xBee
  * Soft sensors

Database support:
  * SQL
  * Postgres
  * ElasticSearch

# Getting Started
## Dependencies
  * pip
  * node
  * npm


## Setting Up Teleceptor
1. git clone https://github.com/visgence/teleceptor.git
2. pip install -r requirements.txt
3. To install a local config customizable first run ```./teleceptorcmd copyconfig``` app will print path
4. In your config, you can set your Postgres and ElasticSearch settings.
5. In the Teleceptor folder, run command ```./teleceptorcmd setup``` and wait until _Done!_ is printed.
6. Run command ```./teleceptorcmd runserver 0.0.0.0:8000```. You will now be running Teleceptor at http://localhost:8000/
7. To load test data, run ```./teleceptorcmd loadfixtures```.
8. Set up desired sensors and start collecting data.(_See below for setting up sensors_)

## Example Data
The ```./teleceptorcmd loadfixtures``` command will run a program that will create two datastreams and fill them with an hours worth of data in the form of a sine curve.

## Example Sensor
The ```./teleceptorcmd btcmote``` command will run a program that requests data from http://blockchain.info/ticker and sends the data to Teleceptor.


# Sensor Firmware
Sensor firmware can be found in the [firmware](https://github.com/visgence/teleceptor/tree/master/firmware) folder. Download the appropriate firmware for your type of sensor, and then upload it to your sensor.

## Setting Up Sensors

#### Serial poller
1. Plug in your sensor through a USB port.
* Make sure you have the most current firmware for your sensor.
2. Run command ```./teleceptorcmd serialPoller PathOfSensor```. This will begin to look for sensors via USB ports.
Note: To find the name of your sensor, in a terminal window, type ```ls /dev/```. This will give you a list of all sensors currently connected.


# Teleceptor Front-End Usage
* To view sensor data that has been collected, click on a sensor stream under the _Stream Select_ tab.
* To look at a certain time period of data, select a range under the _Time Controls_ tab.
  * :star: Specific data can also be viewed by passing the mouse on the graph to observe data points and the time it was collected.
  * :star2: By clicking and dragging on a certain part of the graph, you can zoom-in on points.
* Some information about the sensor is editable and will change the graph accordingly such as _Units_ or _Calibration_.
  * Be sure to save after editing so the configuration information to be available later.
  * _Metadata_ cannot be changed. However, you can change it in the firmware and then re-upload the firmware to the sensor. (_See Teleceptor Concepts_)
* If you download updates from Teleceptor but and are not sure if the webpage is up-to-date as well, clear your web browser's cache:
  * **Chrome:** Right-click in a blank spot on the page -> Inspect element -> Settings (gear symbol) -> Disable cache (while DevTools is open) -> Refresh the page
 * **Mozilla Firefox**: _ctrl+Shift+R_ will reload the page without cache and/or _ctrl+Shift+Delete_ -> Details -> Cache checkbox -> Clear Now


## Setting up an mFi
* cd .ssh
* ssh-keygen
* cat id_rsa.pub
* copy the key given
* ssh to mFi
* vim authorized_keys
* paste key
* chmod 600 authorized_keys
* enter 'save' in command line

# Teleceptor Concepts

## Sensor
The source location that posts data to the Teleceptor station api. Base data must include the sensors uuid and the names for each input/output source.
You can find example firmware and software in the SensorExamples folder.

## Datastream
Datastreams connect sensors to readings. If a sensor should fail or need to be replaced, it's uuid will change however its stream and history should remain intact. They also serve as an organizational tool for the front end.
Datastreams are automatically created when a Sensor posts to the Teleceptor station api.

## Sensor Reading
The raw value coming from a sensor attached to a timestamp of when the reading occurred and the data stream that it is connected to.

In the teleceptor/api folder, you will find a more detailed guide on how the api works.

## License
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






Notes:
we don't run webpack using the '-p' flag in production because this auto sets uglyifly to use mangle which breaks angular.
instead we define the production environment ourselves and run uglyifly ourselves.
Note: apparently there is a way to write angular modules in such a way that mangle can be run.
