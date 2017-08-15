"""
The server that runs Teleceptor.

Authors: Evan Salazar (Visgence Inc.)
         Cyrille Gindreau (Visgence Inc.)

"""

# System Imports
import os
import sys
import cherrypy
import jinja2
import json

# Local Imports
from teleceptor import WEBROOT, PORT, SUPRESS_SERVER_OUTPUT
from teleceptor.auth import AuthController, require
from teleceptor.api import ResourceApi
from teleceptor.version import __version__, __buildDate__

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PATH)

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(searchpath=os.path.join(PATH, 'static/')), )


class Root(object):
    auth = AuthController()
    api = ResourceApi()

    @require()
    def index(self, *args, **kwargs):
        src = json.load(open(os.path.join(PATH, 'webpack-stats.json')))
        vendor = json.load(open(os.path.join(PATH, 'webpack-stats.json')))
        context = {
            "src": src['chunks']['app'][0]['name'],
            "vendor": vendor['chunks']['vendor'][0]['name'],
            "version": __version__,
            "buildDate": __buildDate__
        }
        t = env.get_template("index.html")
        return t.render(context)

    index.exposed = True


def get_cp_config():
    """Creates config file for server.

    :returns:
        a dictionary with the server settings

    """

    config = {
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': WEBROOT,
            # 'tools.auth.on': True,
            'tools.sessions.on': True
        },
        '/api': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        }
    }
    return config


def runserver(config):
    """
    Runs a cherrypy server.

    :param server: configuration file

    """

    cherrypy.tree.mount(Root(), '/', config)

    if SUPRESS_SERVER_OUTPUT:
        cherrypy.config.update({"environment": "embedded"})

    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.server.socket_port = PORT
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == "__main__":
    runserver(get_cp_config())
else:
    # cherrypy.config.update({'environment': 'embedded'})
    application = cherrypy.Application(Root(), script_name=None, config=get_cp_config())
