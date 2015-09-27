"""
    (c) 2015 Visgence, Inc.

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
import json
import sys
import os
import csv
import time
import math
import logging
from datetime import datetime
from pyelasticsearch import ElasticSearch
from teleceptor import ELASTICSEARCH_URI# = "http://192.168.99.100:9200/"
from teleceptor import ELASTICSEARCH_INDEX# = 'teleceptor'
from teleceptor import ELASTICSEARCH_DOC# = 'teledata'
from teleceptor import USE_DEBUG

if USE_DEBUG:
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',level=logging.DEBUG)
else:
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',level=logging.INFO)


def insert_elastic(elastic_buffer):

    es = ElasticSearch(ELASTICSEARCH_URI)

    docs = []
    for doc in elastic_buffer:
        t = time.gmtime(int(doc['@timestamp']/1000))
        index = ELASTICSEARCH_INDEX + "-" + str(t.tm_year).zfill(2) + "." +str(t.tm_mon).zfill(2) + "." + str(t.tm_mday).zfill(2)
        docs.append(es.index_op(doc,index=index,doc_type=ELASTICSEARCH_DOC))
    if len(docs) >0:
        try:
            es.bulk(docs)
            logging.debug("inserted %d records" % (len(docs)))
        except Exception as e:
            logging.error("Insert Exception " + str(e))


def insertReading(ds,value,timestamp=None):
    if timestamp == None:
        timestamp = int(time.time())

    data = {"@timestamp":int(timestamp*1000),"value":value,"ds":ds}
    insert_elastic([data])

def getReadings(ds,start,end):
    """
    Get the readings from elastic search for datastream `ds` between dates `start` and `end`.

    Args:
        ds (int): The datastream id
        start (float): The time in seconds since UNIX epoch to start the query from.
        end (float): The time in seconds since UNIX epoch to end the query at.

    Note:
        We return data points at `start` and `end`. That is, this function is inclusive of the end points.

    Returns:
        list[(float,float)]: pairs of the form (timestamp, value) for all data in datastream `ds` between dates `start` and `end`.
    """
    query = {}

    #first we will match on datastream
    query['match'] = {'ds':ds}

    #then we filter on dates starting with start and ending with end.
    query['range'] = {'@timestamp': {'gte': start, 'lte': end}}

    #TODO: Add aggregation option. Look into the Date Histogram Aggregation

    query_string = json.loads(query)
    return get_elastic(elastic_buffer=query_string)

def get_elastic(elastic_buffer: str):
    """
    Make a query to elasticsearch with args in `elastic_buffer`

    Args:
        elastic_buffer (str): The query json to provide to elastic search.

    Returns:
        list[(float,float)]: pairs of the form (timestamp, value) for all data that matches the query in `elastic_buffer`
    """

    es = ElasticSearch(ELASTICSEARCH_URI)

    # we actually use filter instead of query, since we want exact results
    result = es.search(index=ELASTICSEARCH_INDEX, body={'filter': elastic_buffer, '_source': ['@timestamp', 'value']})

    return [(hit['_source']['@timestamp'], hit['_source']['value']) for hit in result['hits']['hits']]

#Generate a simple sine wave
if __name__ == "__main__":
    days = 30
    period = 12*60 #min
    max = 1023


    start = time.time() - (days*period*2*60)

    docs = []
    for i in range(days*period*2):
        value = int(math.sin(i*(2.0*math.pi/period))*(max/2.0) + (max/2.0))
        #print str(i) + " : " + str(value)
        docs.append({'@timestamp':int((i*60+start)*1000),'value':value,'ds':1000})

        if(i%500==0):
            insert_elastic(docs)
            docs = []


