"""
    Authors: Cyrille Gindreau
             Evan Salazar

"""

# System Imports
import cherrypy
import json
import requests
import logging
from delorean import parse

# Local Imports
from readings import SensorReadings
from teleceptor.sessionManager import sessionScope
import sensors
import datastreams


class Query():
    exposed = True

    def GET(self, *args, **kwargs):
        return "query"

    def POST(self, *args, **kwargs):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        try:
            queryData = json.load(cherrypy.request.body)
            logging.debug("Got data:")
            print json.dumps(queryData, indent=4)
        except (ValueError, TypeError):
            logging.error("Request data is not JSON: %s", cherrypy.request.body)
            statusCode = "400"
            cherrypy.response.status = statusCode
            return json.dumps({}, indent=4)

        sr = SensorReadings()
        response = []
        with sessionScope() as session:
            for i in queryData['targets']:
                sensor = sensors.getSensor(i['target'], session)
                datastream = datastreams.get_datastream_by_sensorid(i['target'], session)
                readingParams = {
                    'datastream': datastream['id'],
                    'start': parse(queryData['range']['from']).epoch,
                    'end': parse(queryData['range']['to']).epoch
                }
                readings = sr.filterReadings(session, readingParams)
                newObj = {
                    "target": i['target'],
                    "datapoints": []
                }
                for j in readings[0]:
                    newObj['datapoints'].append([j[1], int(j[0] * 1000)])

                response.append(newObj)

        return json.dumps(response)


class Search():
    exposed = True

    def GET(self, *args, **kwargs):
        return "search"

    def POST(self, *args, **kwargs):
        cherrypy.response.headers['Content-Type'] = 'application/json'

        response = []
        streams = requests.get('http://localhost:8000/api/datastreams').json()
        for i in streams['datastreams']:
            response.append({"text": i['name'], "value": i['id']})
        return json.dumps(response)


class GrafanaApi:
    exposed = True

    query = Query()
    search = Search()

    def GET(self, *args, **kwargs):
        return "hello"
