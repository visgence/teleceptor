"""
Utilites for using whisper

Authors: Evan Salazar

"""

import whisper
import os
import errno
from time import time
import logging


from teleceptor import WHISPER_DATA
from teleceptor import WHISPER_ARCHIVES
from teleceptor import USE_DEBUG

PATH = os.path.abspath(os.path.dirname(__file__))
# Create this if not already in existence
# WHISPER_DATA = PATH + "/whisperData/"

if USE_DEBUG:
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)


def createDs(uuid):
    logging.info("Creating Whisper database with uuid %s", str(uuid))
    archives = [whisper.parseRetentionDef(retentionDef) for retentionDef in WHISPER_ARCHIVES]
    dataFile = os.path.join(WHISPER_DATA, str(uuid) + ".wsp")
    logging.debug("Creating database at %s", str(dataFile))
    try:
        os.makedirs(WHISPER_DATA)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            logging.error("Got OS error when making directory for whisper files: %s", str(exception))
            raise OSError
    try:
        whisper.create(dataFile, archives, xFilesFactor=0.5, aggregationMethod="average")
    except whisper.WhisperException, exc:
        logging.error("Error creating whisper database: %s", str(exc))


def insertReading(uuid, value, timestamp=None):
    logging.debug("Inserting reading with uuid %s, value %s, and timestamp %s into whisper database.", str(uuid), str(value), str(timestamp))
    dataFile = os.path.join(WHISPER_DATA, str(uuid) + ".wsp")
    logging.debug("Got dataFile as %s", str(dataFile))
    try:
        logging.debug("Updating whisper...")
        whisper.update(dataFile, value, timestamp)
    except whisper.WhisperException, exc:
        logging.error("Got WhisperException %s", str(exc))
        raise exc
    logging.debug("Finished inserting to whisper.")


def getReadings(uuid, start, end):
    assert time()-int(start) >= 60
    dataFile = os.path.join(WHISPER_DATA, str(uuid) + ".wsp")
    try:
        (timeInfo, values) = whisper.fetch(dataFile, start, end)
    except whisper.WhisperException, exc:
        logging.error("Got WhisperException %s", str(exc))
        raise exc

    (start, end, step) = timeInfo

    data = []
    t = start
    for value in values:
        if value is not None:
            data.append((t, value))
        t += step

    return data
