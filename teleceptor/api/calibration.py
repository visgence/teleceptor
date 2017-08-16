# System Imports
import cherrypy
import json
import logging
from sqlalchemy import desc


# Local Imports
from teleceptor.models import Calibration
from teleceptor.sessionManager import sessionScope
from teleceptor import USE_DEBUG


class Calibrations:
    exposed = True

    if USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

    def GET(self, calibration_id=None, * args, **filter_arguments):
        logging.debug("GET request to Calibration.")
        cherrypy.response.headers['Content-Type'] = 'application/json'
        data = {}
        with sessionScope() as s:
            q = s.query(Calibration)
            if calibration_id is not None:
                logging.debug('Found calibration id: %s', str(calibration_id))
                q = q.filter_by(id=calibration_id)
            if 'sensor_id' in filter_arguments:
                logging.debug('Found sensor id: %s', str(filter_arguments['sensor_id']))
                q = q.filter_by(sensor_id=filter_arguments['sensor_id'])

            q = q.order_by(desc(Calibration.timestamp))

            logging.debug('Making query: %s', str(q))
            try:
                data['calibrations'] = [i.toDict() for i in q]
            except Exception, e:
                logging.error(e)
                data['error'] = e

        return json.dumps(data)
