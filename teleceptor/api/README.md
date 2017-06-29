# Teleceptor API

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

## Station

### POST:
teleceptorurl/api/station

Handles incoming data from a basestation by updating (or creating) sensor information, including metadata, calibration. Additionally updates sensor readings, if any.

Params:
A JSON array formatted string stored in the data section of the HTTP POST request.
It is not optional, but some elements can be omitted. The JSON object should be a list, even if there is only one element in it.
The full format is listed in the Teleceptor Standard format ReadMe.

Returns:
A JSON object with either a key 'error' or 'newValues'. In the case of 'error', the value is an error string.
In the case of 'newValues', the value is an object with key/value pairs as "sensorname" : messagelist, where messagelist is all unread,
unexpired messages for the sensor with name sensorname.
The receiving function must determine how to handle the messages (e.g. to consider only the newest message, or to use all messages.)


## Datastreams

### GET:

teleceptorurl/api/datastreams/
Obtain a list of all available Datastreams .
Returns:
A JSON object with either a key 'error' or 'datastreams'.
In the case of 'error', the value is an error string.
In the case of 'datastreams', the value is a list of all datastreams.


teleceptorurl/api/datastreams/?sensor1=value&sensor2=value...
Obtain a list of all available datastreams filtered by sensor uuid arguments.
Returns:
A JSON object with either a key 'error' or 'datastreams'.
In the case of 'error', the value is an error string.
In the case of 'datastream', the value is a list of selected datastreams.


teleceptorurl/api/datastreams/<stream_id>/
Obtain a single Datastreams for the given stream_id.
Returns:
A JSON object with either a key 'error' or 'stream'.
In the case of 'error', the value is an error string.
In the case of 'stream', the value will be a single stream
