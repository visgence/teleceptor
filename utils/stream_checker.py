"""
Provides a function that returns an integer code representing the health/status of a given datastream. 
May be run from the commandline.

Args:
    id (int): the datastream id to check.
    teleceptorURI (str): the URI for the base teleceptor server. Defaults to http://localhost:80/
    useSQL (bool): flag to use sql or elasticsearch for testing. If True, will request sql data from teleceptor. If False, will request elasticsearch data.
    minutes (float): the number of minutes in the past from now to request data for.

Return:
    (int): a nagios compatible code. 0 for ok, 1 for no data, but successful connection, 2 for failed connection, and 3 for any other exception
"""

import argparse
import requests
import logging

logger = logging.getLogger(__name__)


def run_check(datastream_id, teleceptorURI, useSQL, minutes):
    """
    Test if datastream `datastream_id` has data within the last `minutes` minutes from now.

    If `useSQL` is True, requests SQL data from teleceptor. Else, requests Elasticsearch data.

    Args:
        id (int): the datastream id to check.
        teleceptorURI (str): the URI for the base teleceptor server. Defaults to http://localhost:80/
        useSQL (bool): flag to use sql or elasticsearch for testing. If True, will request sql data from teleceptor. If False, will request elasticsearch data.
        minutes (float): the number of minutes in the past from now to request data for.

    Return:
        (int): a nagios compatible code. 0 for ok, 1 for no data, but successful connection, 2 for failed connection, and 3 for any other exception
    """
    return_code = 0

    if teleceptorURI[-1] != '/':
        teleceptorURI = teleceptorURI + '/'
    request_url = teleceptorURI + 'api/readings/'

    request_data = {'stream': datastream_id, 'start': time.time() - int(round(minutes * 60))}

    try:
        response = request.get(request_url, data=json.dumps(request_data))
        print(response)
    except:
        logger.exception("Got an exception during request.")
        return_code = 2

    logger.info("Finished stream_checker. Returning with code {}".format(return_code))
    return return_code


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test the health of a given datastream.')
    parser.add_argument('id', type=int, help='ID of the datastream to test.')
    parser.add_argument('teleceptorURI', type=str, help='URI for the teleceptor server. Defaults to http://localhost:80', default='http://localhost:80')
    parser.add_argument('-sql', '--useSQL', action='store_true', type=bool, help='True to request SQL data. False to request Elasticsearch data.', default=False)
    parser.add_argument('-m', '--minutes', type=float, help='The number of minutes in the past from now to request data for.', default=30.0)
    args = parser.parse_args()

    logger.debug("Testing with arguments {}".format(args))

    return run_check(args.id, args.teleceptorURI, args.useSQL, args.minutes)
