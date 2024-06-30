# System Imports
from rest_framework.response import Response
from rest_framework.views import APIView
import logging


# Local Imports
from django.conf import settings
from teleceptor.models import Calibration

class Calibrations(APIView):
    exposed = True

    if settings.DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

    def get(self, request, * args, **filter_arguments):
        """GET"""
        logging.debug("GET request to Calibration.")
        calibration_id = request.GET.get('calibration_id', None)
        sensor_id = request.GET.get('sensor_id', None)
        logging.debug(f"Calibration Sensor id {sensor_id}")
        data = {}
        q = {}
        if calibration_id is not None:
            q = Calibration.objects.filter(id=calibration_id).order_by('timestamp')
        if sensor_id is not None:
            logging.debug('Found sensor id: %s', str(sensor_id))
            q = Calibration.objects.filter(sensor=sensor_id).order_by('timestamp')

        logging.debug('Making query: %s', str(q))
        try:
            data['calibrations'] = [i.to_dict() for i in q]
        except Exception as e:
            logging.error(e)
            data['error'] = e

        return Response(data)
