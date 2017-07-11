import time
import logging
from pyelasticsearch import ElasticSearch
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

            es = ElasticSearch(ELASTICSEARCH_URI)

            docs = []
            for doc in self.buffer:
                t = time.gmtime(int(doc['@timestamp']/1000))
                index = ELASTICSEARCH_INDEX + "-" + str(t.tm_year).zfill(2) + "." + str(t.tm_mon).zfill(2) + "." + str(t.tm_mday).zfill(2)
                docs.append(es.index_op(doc, index=index, doc_type=ELASTICSEARCH_DOC))
            if len(docs) > 0:
                try:
                    es.bulk(docs)
                    logging.debug("inserted %d records" % (len(docs)))
                except Exception as e:
                    logging.error("Insert Exception " + str(e))
