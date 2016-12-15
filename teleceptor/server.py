"""
server.py
   The server that runs Teleceptor

Authors: Evan Salazar

"""

# System Imports
import os
import sys
import cherrypy
from cherrypy.lib.static import serve_file

# Local Imports
from teleceptor import WEBROOT, PORT, SUPRESS_SERVER_OUTPUT
from teleceptor.auth import AuthController, require, member_of, name_is
from teleceptor.pages import Root

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PATH)


def get_cp_config():
    """Creates config file for server

    Returns:
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
    """Runs a cherrypy server

    Args:
        server configuration file

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
    cherrypy.config.update({'environment': 'embedded'})
    application = cherrypy.Application(Root(), script_name=None, config=get_cp_config())
