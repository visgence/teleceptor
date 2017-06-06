"""
Sets up webpage and displays current sensor readings.

Authors: Victor Szczepanski
         Cyrille Gindreau

"""

# System Imports
import cherrypy
import jinja2
import logging

# local Imports
from teleceptor import WEBROOT
from teleceptor import USE_DEBUG
from teleceptor.auth import AuthController, require
env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=WEBROOT))


class Root(object):
    auth = AuthController()

    if USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

    @require()
    def index(self, sensor_name=None, *args, **kwargs):

        cherrypy.response.headers['Content-Type'] = 'text/html'
        returnData = {}
        returnData.update(**kwargs)
        t = env.get_template("index.html")
        return t.render(returnData)

    index.exposed = True

    @require()
    def generateJson(self, **kwargs):
        t = env.get_template("generateJson.html")

        cherrypy.response.headers['Content-Type'] = 'text/html'
        return t.render({})

    generateJson.exposed = True
