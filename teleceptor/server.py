"""
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

# System Imports
import os,sys
import cherrypy
from cherrypy.lib.static import serve_file
PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
sys.path.append(PATH)
# Local Imports
from teleceptor import WEBROOT,PORT
from teleceptor.auth import AuthController, require, member_of, name_is
from teleceptor.pages import Root

def runserver():
    cherrypy.tree.mount(Root(), '/', config = {
        '/': {
             'tools.staticdir.on': True
            ,'tools.staticdir.dir': WEBROOT
            # ,'tools.auth.on': True
            ,'tools.sessions.on': True
        },
        '/api': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        }
    })

    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.server.socket_port = PORT
    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == "__main__":
    runserver()
