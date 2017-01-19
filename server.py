import cherrypy
import json
import os
import requests
import time

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
STATIC = os.path.join(PATH, 'static')


class Root(object):

    @cherrypy.expose
    def getData(self, **kwargs):
        # Get stream id - names
        returnData = {}
        returnData['info'] = []
        baseUrl = "http://0.0.0.0:8000/api/"
        streamInfo = requests.get("{}datastreams".format(baseUrl)).json()['datastreams']
        print json.dumps(streamInfo, indent=2)
        for i in streamInfo:
            if i['sensor'] == kwargs['node']:
                returnData['info'].append({"stream": i})

        sensorInfo = requests.get("{}sensors".format(baseUrl)).json()
        for i in sensorInfo['sensors']:
            if i['uuid'] == kwargs['node']:
                returnData['info'].append({"sensor": i})
                node_id = i['last_calibration']['id']
                returnData['units'] = i['units']
                returnData['name'] = i['uuid']
                break

        if 'endTime' in kwargs:
            endTime = int(kwargs['endTime'])/1000
        else:
            endTime = int(time.time())
        if 'startTime' in kwargs:
            startTime = int(kwargs['startTime'])/1000
        else:
            startTime = endTime - 36000

        startTime = int(startTime)
        endTime = int(endTime)

        streamUrl = "{}readings/?datastream={}&start={}&end={}".format(baseUrl, node_id, startTime, endTime)
        streamData = requests.get(streamUrl).json()
        returnData['startTime'] = startTime
        returnData['endTime'] = endTime

        # print json.dumps(sensorInfo, indent=2)
        returnData['readings'] = streamData['readings']
        return json.dumps(returnData, indent=4)

    @cherrypy.expose
    def setData(self, **kwargs):
        url = "http://0.0.0.0:8000/api/"+kwargs['url']+"/"+kwargs['id']
        data = {}
        for key, value in kwargs.iteritems():
            if key == 'url' or key == 'id':
                continue
            data[key] = value
        requests.put(url, data)


def get_cp_config():
    return {
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': STATIC,
            'tools.staticdir.index': 'index.html',
        },
    }


def runserver(config):
    cherrypy.tree.mount(Root(), '/', config)
    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == "__main__":
    runserver(get_cp_config())
else:
    cherrypy.config.update({'environment': 'embedded'})
    application = cherrypy.Application(
        Root(), script_name=None, config=get_cp_config())