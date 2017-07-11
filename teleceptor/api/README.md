# Teleceptor API

## Station

### POST:
teleceptorurl/api/station

Handles incoming data from a basestation by updating (or creating) sensor information, including metadata and calibration. Additionally updates sensor readings, if any.

#### Params:
A JSON array formatted string stored in the data section of the HTTP POST request.
It is not optional, but some elements can be omitted. The JSON object should be a list, even if there is only one element in it.
The full format is listed in the TeleceptorStandardFormat ReadMe.

#### Returns:
A JSON object with either a key 'error' or 'newValues'. In the case of 'error', the value is an error string.
In the case of 'newValues', the value is an object with key/value pairs as "sensorname" : messagelist, where messagelist is all unread, unexpired messages for the sensor with name sensorname.
The receiving function must determine how to handle the messages (e.g. to consider only the newest message, or to use all messages.)


## Datastreams

### GET:

teleceptorurl/api/datastreams/

Obtain a list of all available Datastreams .
Returns:
A JSON object with either a key 'error' or 'datastreams'.
In the case of 'error', the value is an error string.
In the case of 'datastreams', the value is a list of all datastreams.

teleceptorurl/api/datastreams/?sensor=value1&sensor=value2&...

Obtain a list of all available datastreams filtered by sensor uuid arguments.
Returns:
A JSON object with either a key 'error' or 'datastreams'.
In the case of 'error', the value is an error string.
In the case of 'datastream', the value is a list of selected datastreams.

teleceptorurl/api/datastreams/<stream_id>/

Obtain a single datastream for the given stream_id.
Returns:
A JSON object with either a key 'error' or 'stream'.
In the case of 'error', the value is an error string.
In the case of 'stream', the value will be a single stream

### PUT

teleceptorurl/api/datastreams/stream_id

Updates the stream with stream_id.

Using the JSON formatted data in the HTTP request body, updates the datastream information in the database.

param stream_id: The UUID of a datastream
Valid key/value pairs correspond to the columns in `models.DataStreams`.

Returns a JSON object with an 'error' key if an error occurred or 'datastream' key if update succeeded.
If 'error', the value is an error string. If 'datastream', the value is a JSON object representing the updated datastream in the database.


## SensorReadings

### GET

teleceptorurl/api/sensor

Returns a list of all the sensors in the database

teleceptorurl/api/sensor/sensor_id=sensor

returns all of the sensor data for sensor with sensor_id


## PUT

teleceptorurl/api/sensor

Creates or updates a sensor model in the database.
Expects a json object with key 'uuid' with the sensors uuid and any of the following optional arguments:
    "sensor_IOtype" - Is the sensor an input or output sensor
    "name" - human readable representation of the sensor
    "units" - the units used on the graph
    "model" - the modal of the physical sensor being used.
    "description" - A description of the sensor.
    "meta_data" - Any metadata needed, can be a nested dictionary


## SensorReadings

### GET

/api/readings/

Obtain a list of available SensorReadings.
Returns a JSON object with an 'error' key if an error occurred or 'readings' key of time, value arrays and a 'source' key that list the source of the readings.

teleceptorurl/api/readings?arg1=foo&arg2=bar&etc..

Obtain a list of available SensorReadings filtered by url arguments.
Filter Arguments:
    'stream' (Numeric) - id of DataStream
    'start' (Numeric) - start time of the readings
    'end' (Numeric) - end time of the readings
    'source' (String) - one of SQL or ElasticSearch. Selects data source to pull from (overrides any server-side source selection unless the USE_SQL_ALWAYS flag is set.)
Returns a JSON object with an 'error' key if an error occurred or 'readings' key of time, value arrays and a 'source' key that list the source of the readings.

### POST

teleceptorurl/api/readings

Adds (a) reading(s) to a stream.
Expects a json object with key 'readings' which is an array of tuples (datastreamid, value, timestamp)



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
