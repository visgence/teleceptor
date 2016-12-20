"""
Sets up webpage and displays current sensor readings.

Authors: Victor Szczepanski
         Cyrille Gindreau

"""

# System Imports
import os
import sys
import json
import cherrypy
import jinja2
import logging

# local Imports
from teleceptor import TEMPLATES
from teleceptor import USE_DEBUG
from teleceptor import api
from teleceptor.api import ResourceApi
from teleceptor.auth import AuthController, require, member_of, name_is
env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=TEMPLATES))


class Root(object):
    auth = AuthController()
    api = ResourceApi()

    if USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

    @require()
    def index(self, sensor_name=None, *args, **kwargs):
        params = cherrypy.request.params

        sensors = api.Sensors()
        datastreams = api.DataStreams()
        sysdata = api.SysData()
        sysdata_dict = json.loads(sysdata.GET())

        sensorsList = json.loads(sensors.GET())['sensors']
        streamList = json.loads(datastreams.GET())['datastreams']

        activeSensor = sensorsList[0] if len(sensorsList) > 0 else None

        if sensor_name is not None:
            try:
                activeSensor = json.loads(sensors.GET(sensor_name))["sensor"]
            except KeyError, ke:
                logging.error("Error: no sensor with id %s", sensor_name)
                logging.error(str(ke))
        datastream = None
        if activeSensor is not None:
            dsList = json.loads(datastreams.GET())
            logging.info("dslist")
            logging.info(dsList)
            if len(dsList['datastreams']) > 0:
                datastream = dsList['datastreams'][0]
                datastream['paths'] = dsList['paths']

        cherrypy.response.headers['Content-Type'] = 'text/html'
        activeSensor['datastream'] = datastream

        returnData = {
            "sysdata": sysdata_dict,
            "sensorsList": sensorsList,
            "streamsList": streamList,
            "activeSensor": activeSensor,
            "activeSensorJSON": json.dumps(activeSensor),
            "datastreamJSON": json.dumps(datastream),
        }
        returnData.update(**kwargs)
        t = env.get_template("sensorsIndex.html")

        return t.render(returnData)

    index.exposed = True

    @require()
    def generateJson(self, **kwargs):
        t = env.get_template("generateJson.html")
        sysdata = api.SysData()
        sysdata_dict = json.loads(sysdata.GET())

        cherrypy.response.headers['Content-Type'] = 'text/html'
        return t.render({"sysdata": sysdata_dict})

    generateJson.exposed = True
