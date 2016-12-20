"""

Authors: Victor Szczepanski

"""

import os
import platform
import json
from .version import __version__
import softSensors
PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Path to WEBROOT and Template are part of application
WEBROOT = os.path.abspath(os.path.join(PATH, 'webroot'))
TEMPLATES = os.path.abspath(os.path.join(PATH, 'templates'))

# Set config path based on system
if os.environ.get('TELECEPTOR_DATAPATH') is not None:
    DATAPATH = os.environ.get('TELECEPTOR_DATAPATH')
elif platform.system() == 'Windows':
    DATAPATH = os.path.join(os.getenv("APPDATA"), "teleceptor")
else:
    DATAPATH = os.path.join(os.getenv("HOME"), ".config", "teleceptor")

# Check if we have a config relative to library
if os.path.exists(os.path.join(PATH, 'config', 'config.json')):
    conf = json.load(open(os.path.join(PATH, 'config', 'config.json')))
    DATAPATH = PATH

# If not check if we have a user config
elif os.path.exists(os.path.join(DATAPATH, 'config.json')):
    conf = json.load(open(os.path.join(DATAPATH, 'config.json')))

# Use defaults.json
else:
    conf = json.load(open(os.path.join(PATH, 'config', 'defaults.json')))
    DATAPATH = PATH

# Set verbose debug mode
USE_DEBUG = conf['USE_DEBUG']

# Set SQL DB File
if os.path.isabs(conf['DBFILE']):
    DBFILE = conf['DBFILE']
else:
    DBFILE = os.path.join(DATAPATH, conf['DBFILE'])

# Set DB type (postgres or sqlite). Defaults to postgres
if "USEPG" in conf:
    USEPG = conf["USEPG"]
else:
    USEPG = False

if "PGSQLDBHOST" in conf:
    PGSQLDBHOST = conf['PGSQLDBHOST']
else:
    PGSQLDBHOST = "pg"

if "PGSQLDBNAME" in conf:
    PGSQLDBNAME = conf['PGSQLDBNAME']
else:
    PGSQLDBNAME = "tele"

if "PGSQLDBPORT" in conf:
    PGSQLDBPORT = conf['PGSQLDBPORT']
else:
    PGSQLDBPORT = 5432

if "PGSQLDBUSERNAME" in conf:
    PGSQLDBUSERNAME = conf['PGSQLDBUSERNAME']
else:
    PGSQLDBUSERNAME = "tele"

if "PASSWORD" in conf:
    PASSWORD = conf['PASSWORD']
else:
    PASSWORD = "password"

# Set Logfile
if os.path.isabs(conf['LOG']):
    LOG = conf['LOG']
else:
    LOG = os.path.join(DATAPATH, conf['LOG'])

# SAVE DATA TO SQL DB
SQLDATA = conf["SQLDATA"]

# Read from SQL database if time delta is less than SQLREADTIME
SQLREADTIME = conf["SQLREADTIME"]

# Server Port
PORT = conf["PORT"]


# TCP Poller Hosts
TCP_POLLER_HOSTS = conf["TCP_POLLER_HOSTS"]

# Supress server output
SUPRESS_SERVER_OUTPUT = conf["SUPRESS_SERVER_OUTPUT"]

# Set data output to use only SQL or not
if "USE_SQL_ALWAYS" in conf:
    USE_SQL_ALWAYS = conf["USE_SQL_ALWAYS"]
else:
    USE_SQL_ALWAYS = False

if "USE_ELASTICSEARCH" in conf:
    USE_ELASTICSEARCH = conf["USE_ELASTICSEARCH"]
    if USE_ELASTICSEARCH:
        ELASTICSEARCH_URI = conf["ELASTICSEARCH_URI"]
        ELASTICSEARCH_INDEX = conf["ELASTICSEARCH_INDEX"]
        ELASTICSEARCH_DOC = conf["ELASTICSEARCH_DOC"]
else:
    USE_ELASTICSEARCH = False
