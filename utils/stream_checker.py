"""
Provides a function that returns an integer code representing the health/status of a given datastream. 
May be run from the commandline.

Sample Usage:
    python stream_checker.py http://localhost:80/ --sensor_uuid mysensoruuid
    python stream_checker.py http://localhost:80/ --id 5
    python stream_checker.py http://loaclhost:80/ --minutes 5 --sensor_uuid mysensoruuid
    python stream_checker.py http://localhost:80/ --useSQL --minutes 24.22 --sensor_uuid mysensoruuid

Args:
    teleceptorURI (str): the URI for the base teleceptor server. Defaults to http://localhost:80/
    id optional(int): the datastream id to check.
    useSQL (bool): flag to use sql or elasticsearch for testing. If True, will request sql data from teleceptor. If False, will request elasticsearch data.
    minutes (float): the number of minutes in the past from now to request data for.
    sensor_uuid optional(str): the uuid of the sensor. If present, will request the datastream id before performing main check.

Return:
    (int): a nagios compatible code. 0 for ok, 1 for no data, but successful connection, 2 for failed connection, and 3 for any other exception
"""

import argparse
import requests
import logging
import time
import json
import sys

FORMAT = '%(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger("stream_checker")
logger.setLevel(logging.INFO)


def run_check(datastream_id, teleceptorURI, useSQL, minutes, sensor_uuid=None):
    """
    Test if datastream `datastream_id` has data within the last `minutes` minutes from now.

    If `useSQL` is True, requests SQL data from teleceptor. Else, requests Elasticsearch data.

    Args:
        id (int): the datastream id to check.
        teleceptorURI (str): the URI for the base teleceptor server. Defaults to http://localhost:80/
        useSQL (bool): flag to use sql or elasticsearch for testing. If True, will request sql data from teleceptor. If False, will request elasticsearch data.
        minutes (float): the number of minutes in the past from now to request data for.
        sensor_uuid optional(str): the uuid of the sensor. If present, will request the datastream id before performing main check.

    Return:
        (int): a nagios compatible code. 0 for ok, 1 for no data, but successful connection, 2 for failed connection, and 3 for any other exception
    """
    return_code = 0

    if teleceptorURI[-1] != '/':
        teleceptorURI = teleceptorURI + '/'

    # if we have a sensor_uuid, look its datastream_id up first

    if sensor_uuid is not None:
        try:
            sensors_request_url = teleceptorURI + 'api/datastreams/'
            request_data = {'sensor': sensor_uuid}
            response = requests.get(sensors_request_url, params=request_data)

            datastream_id = response.json()['datastreams'][0]['id']
        except requests.exceptions.ConnectionError:
            logger.error("CRITICAL - Could not connect to teleceptor at URI {}".format(teleceptorURI))
            return_code = 2
            return return_code
        except requests.exceptions.HTTPError:
            logger.error("CRITICAL - {}".format(response.json()['error']))
            return_code = 2
            return return_code
        except KeyError:
            logger.error("CRITICAL - response for uuid did not contain appropriate data: {}".format(response.json()))
            return_code = 2
            return return_code


    readings_request_url = teleceptorURI + 'api/readings/'

    request_data = {'datastream': datastream_id, 'start': int(round(time.time() - minutes * 60))}

    try:
        response = requests.get(readings_request_url, params=(request_data))

        response.raise_for_status()

        if len(response.json()['readings']) == 0:
            logger.error("CRITICAL - Got no data for datastream {} for the last {} minutes.".format(datastream_id, minutes))
            return_code = 2
            return return_code

    except requests.exceptions.HTTPError:
        logger.error("CRITICAL - Error getting data for datastream {}. Maybe this stream is not formatted properly?".format(datastream_id))
        return_code = 2
        return return_code
    except requests.exceptions.ConnectionError:
        logger.error("CRITICAL - Could not connect to teleceptor at URI {}".format(teleceptorURI))
        return_code = 2
        return return_code
    except:
        logger.error("UNKNOWN - Got an unexpected exception during request.")
        return_code = 3
        return return_code

    logger.info("OK - datastream {} has {} datapoints in the last {} minutes.".format(datastream_id, len(response.json()['readings']), minutes))
    return return_code


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test the health of a given datastream.')
    parser.add_argument('teleceptorURI', type=str, help='URI for the teleceptor server. Defaults to http://localhost:80', default='http://localhost:80')
    parser.add_argument('--id', type=int, help='ID of the datastream to test.')
    parser.add_argument('-sql', '--useSQL', action='store_true', help='True to request SQL data. False to request Elasticsearch data.', default=False)
    parser.add_argument('-m', '--minutes', type=float, help='The number of minutes in the past from now to request data for.', default=30.0)
    parser.add_argument('--uuid', type=str, help='The uuid of the sensor. If present, overrides the --id, if --id is present.')
    args = parser.parse_args()

    logger.debug("Testing with arguments {}".format(args))

    sys.exit(run_check(args.id, args.teleceptorURI, args.useSQL, args.minutes, args.uuid))
