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

import os
from .version import __version__
PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
#Data FIles
DBFILE = os.path.abspath(os.path.join(PATH,'database','base_station.db'))
WHISPER_DATA =  os.path.abspath(os.path.join(PATH,'whisperData'))
WEBROOT = os.path.abspath(os.path.join(PATH,'webroot'))
TEMPLATES = os.path.abspath(os.path.join(PATH,'templates'))
LOG = os.path.abspath(os.path.join(PATH,'sitemontior.log'))

#SAVE DATA TO SQL DB
SQLDATA = True

#Read from SQL database if time delta is less than SQLREADTIME
SQLREADTIME = 7200

#Server Port
PORT = 8000
