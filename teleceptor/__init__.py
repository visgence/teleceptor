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
import platform
import json
from .version import __version__
PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))

#Path to WEBROOT and Template are part of application
WEBROOT = os.path.abspath(os.path.join(PATH,'webroot'))
TEMPLATES = os.path.abspath(os.path.join(PATH,'templates'))

#Set config path based on system

if os.environ.get('TELECEPTOR_DATAPATH') is not None:
    DATAPATH = os.environ.get('TELECEPTOR_DATAPATH')
elif platform.system() == 'Windows':
    DATAPATH = os.path.join(os.getenv("APPDATA"),"teleceptor")
else:
    DATAPATH = os.path.join(os.getenv("HOME"),".config","teleceptor")

#Check if we have a config relative to library
if os.path.exists(os.path.join(PATH,'config','config.json')):
    conf = json.load(open(os.path.join(PATH,'config','config.json')))
    DATAPATH = PATH

#If not check if we have a user config
elif os.path.exists(os.path.join(DATAPATH,'config.json')):
    conf = json.load(open(os.path.join(DATAPATH,'config.json')))

#Use defaults.json
else:
    conf = json.load(open(os.path.join(PATH,'config','defaults.json')))
    DATAPATH = PATH

#Set verbose debug mode
USE_DEBUG = conf['USE_DEBUG']

#Set SQL DB File
if os.path.isabs(conf['DBFILE']):
    DBFILE = conf['DBFILE']
else:
    DBFILE = os.path.join(DATAPATH,conf['DBFILE'])

#Set Whisper Data folder
if os.path.isabs(conf['WHISPER_DATA']):
    WHISPER_DATA = conf['WHISPER_DATA']
else:
    WHISPER_DATA = os.path.join(DATAPATH,conf['WHISPER_DATA'])

#Set Logfile
if os.path.isabs(conf['LOG']):
    LOG = conf['LOG']
else:
    LOG = os.path.join(DATAPATH,conf['LOG'])

#Whisper Archives
WHISPER_ARCHIVES = conf["WHISPER_ARCHIVES"]

#SAVE DATA TO SQL DB
SQLDATA = conf["SQLDATA"]

#Read from SQL database if time delta is less than SQLREADTIME
SQLREADTIME = conf["SQLREADTIME"]

#Server Port
PORT = conf["PORT"]


#TCP Poller Hosts
TCP_POLLER_HOSTS = conf["TCP_POLLER_HOSTS"]
