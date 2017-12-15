import time
import logging
import json
from pyelasticsearch import ElasticSearch
from teleceptor import ELASTICSEARCH_URI, ELASTICSEARCH_INDEX, ELASTICSEARCH_DOC, USE_DEBUG

import jsonlines
import io
import requests

if USE_DEBUG:
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)


class ElasticSession:

    def __init__(self):
        self.buffer = []

    def insertReading(self, ds, value, timestamp=None):
        if timestamp is None:
            timestamp = int(time.time())

        data = {"@timestamp": int(timestamp*1000), "value": value, "ds": ds}
        self.buffer.append(data)

    def commit(self):
        if len(self.buffer) > 0:
            logging.debug("Inserting {} to elasticsearch".format(len(self.buffer)))

            es = ElasticSearch(ELASTICSEARCH_URI)

            data = ''
            for doc in self.buffer:
                t = time.gmtime(int(doc['@timestamp']/1000))
                index = ELASTICSEARCH_INDEX + "-" + str(t.tm_year).zfill(2) + "." + str(t.tm_mon).zfill(2) + "." + str(t.tm_mday).zfill(2)

                line1 = {"index": {"_index": index, "_type": ELASTICSEARCH_DOC}}

                # the + """...""" is how we can create the newline for ndjson.
                data += json.dumps(line1) + """
"""
                data += json.dumps(doc) + """
"""

            try:
                url = "{}/_bulk".format(ELASTICSEARCH_URI)
                headers = {'Content-Type': 'application/x-ndjson'}
                print "here:"
                print data
                print ELASTICSEARCH_URI
                response = requests.post(url, headers=headers, data=data)
                print "done"
                print response
                print response.content
            except Exception as e:
                logging.error("Insert Exception " + str(e))


# def send_request(self, method, path_components, body='', query_params=None):
#
#     def _utf8(self, thing):
#         if isinstance(thing, binary_type):
#             return thing
#         if not isinstance(thing, text_type):
#             thing = text_type(thing)
#         return thing.encode('utf-8')
#
#     path = '/'.join(quote_plus(self._utf8(p), '') for p in path_components if p is not None and p != '')
#     if not path.startswith('/'):
#         path = '/' + path
#
#     # We wrap to use pyelasticsearch's exception hierarchy for backward
#     # compatibility:
#     try:
#         # This implicitly converts dicts to JSON. Strings are left alone:
#         _, prepped_response = self._transport.perform_request(
#             method,
#             path,
#             params=dict((k, self._utf8(self._to_query(v)))
#                         for k, v in iteritems(query_params)),
#             body=body)
#     except SerializationError as exc:
#         raise InvalidJsonResponseError(exc.args[0])
#     except (ConnectionError, ConnectionTimeout) as exc:
#         # Pull the urllib3-native exception out, and raise it:
#         raise exc.info
#     except TransportError as exc:
#         status = exc.args[0]
#         error_message = exc.args[1]
#         self._raise_exception(status, error_message)
#
#     return prepped_response
