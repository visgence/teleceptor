"""
__init__.py

Authors: Victor Szczepanski
"""
import cherrypy
import json

# Local Imports
from teleceptor import __version__
from datastreams import DataStreams
from sensors import Sensors
from readings import SensorReadings
from station import Station
from messages import Messages
from grafana import GrafanaApi


class SysData:
    exposed = True

    # @require()
    def GET(self, sensor_id=None):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        data = {'version': __version__}
        return json.dumps(data, indent=4)


class ResourceApi:

    sysdata = SysData()
    datastreams = DataStreams()
    sensors = Sensors()
    readings = SensorReadings()
    station = Station()
    messages = Messages()
    grafana = GrafanaApi()
