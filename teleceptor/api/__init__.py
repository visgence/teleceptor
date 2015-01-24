"""
    Contributing Authors:
        Bretton Murphy (Visgence, Inc.)
        Evan Salazar (Visgence, Inc.)

    This module contains the routes for the various api's in the system.

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
import cherrypy
import json

# Local Imports
from teleceptor import __version__
from datastreams import DataStreams
from sensors import Sensors
from readings import SensorReadings
from delegation import Delegation
from messages import Messages


class SysData:
    exposed = True
    # @require()
    def GET(self, sensor_id=None):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        data = {'version':__version__}
        return json.dumps(data, indent=4)


class ResourceApi:

    sysdata      = SysData()
    datastreams  = DataStreams()
    sensors      = Sensors()
    readings     = SensorReadings()
    station      = Station()
    messages     = Messages()
