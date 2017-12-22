import time
import logging
import json
import requests
from teleceptor import ELASTICSEARCH_URI, ELASTICSEARCH_INDEX, ELASTICSEARCH_DOC, USE_DEBUG

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
                response = requests.post(url, headers=headers, data=data)

            except Exception as e:
                logging.error("Insert Exception " + str(e))
