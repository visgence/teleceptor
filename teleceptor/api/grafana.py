"""
    Authors: Cyrille Gindreau
             Evan Salazar

"""

# System Imports
import cherrypy
import json
import logging
import delorean
import dateutil.parser

# Local Imports
from readings import SensorReadings
from teleceptor.sessionManager import sessionScope
from teleceptor import USE_DEBUG
import sensors
import datastreams
from datastreams import DataStreams


class Query():
    exposed = True

    if USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

    def GET(self, *args, **kwargs):
        return "query"

    def POST(self, *args, **kwargs):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        try:
            queryData = json.load(cherrypy.request.body)
            logging.debug("Got data:")
            logging.debug(queryData)
        except (ValueError, TypeError):
            logging.error("Request data is not JSON: %s", cherrypy.request.body)
            statusCode = "400"
            cherrypy.response.status = statusCode
            return json.dumps({}, indent=4)

        sr = SensorReadings()
        response = []
        with sessionScope() as session:
            for i in queryData['targets']:

                datastream = datastreams.get_datastream_by_name(i['target'], session)
                sensor = sensors.getSensor(datastream['sensor'], session)
                readingParams = {
                    'datastream': datastream['id'],
                    'start': int(delorean.Delorean(dateutil.parser.parse(queryData['range']['from'])).epoch),
                    'end': int(delorean.Delorean(dateutil.parser.parse(queryData['range']['to'])).epoch)
                }

                readings = sr.filterReadings(session, readingParams)
                newObj = {
                    "target": i['target'],
                    "datapoints": []
                }
                if type(sensor['last_calibration']['coefficients']) == unicode:
                    coefficients = json.loads(sensor['last_calibration']['coefficients'])
                else:
                    coefficients = sensor['last_calibration']['coefficients']

                for j in readings[0]:
                    val = j[1] * coefficients[0] + coefficients[1]
                    newObj['datapoints'].append([val, int(j[0] * 1000)])

                response.append(newObj)

        return json.dumps(response)


class Search():
    exposed = True

    def GET(self, *args, **kwargs):
        return "search"

    def POST(self, *args, **kwargs):
        cherrypy.response.headers['Content-Type'] = 'application/json'

        response = []
        ds = DataStreams()
        streams = json.loads(ds.GET())
        for i in streams['datastreams']:
            response.append({"text": i['name'], "value": i['id']})
        return json.dumps(response)


class GrafanaApi:
    exposed = True

    query = Query()
    search = Search()

    def GET(self, *args, **kwargs):
        return "hello"
