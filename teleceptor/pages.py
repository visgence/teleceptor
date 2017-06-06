"""
Sets up webpage and displays current sensor readings.

Authors: Victor Szczepanski
         Cyrille Gindreau

"""

# System Imports
import os.path
import cherrypy
import logging

# local Imports
from teleceptor import WEBROOT
from teleceptor import USE_DEBUG
from teleceptor.auth import AuthController, require


class Root(object):
    auth = AuthController()

    if USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

    @require()
    def index(self, *args, **kwargs):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        return open(os.path.join(WEBROOT, "index.html"))

    index.exposed = True
