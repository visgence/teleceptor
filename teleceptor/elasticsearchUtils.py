"""

Authors: Victor Szczepanski


"""
import time
import math
import logging
import requests
import json
from teleceptor import ELASTICSEARCH_URI, USE_DEBUG
from teleceptor.timeAggregationUtils import getElasticSearchAggregationLevel


if USE_DEBUG:
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)


def insertReading(ds, value, session, timestamp=None):
    if timestamp is None:
        timestamp = int(time.time())

    data = {"@timestamp": int(timestamp*1000), "value": value, "ds": ds}
    session.insertEsReading([data])


def getReadings(ds, start, end, points=None):
    """
    Get the readings from elastic search for datastream `ds` between dates `start` and `end`.

    :param ds: The datastream id
    :type ds: int
    :param start: The time in seconds since UNIX epoch to start the query from.
    :type start: float
    :param end: The time in seconds since UNIX epoch to end the query at.
    :type end: float
    :param points:The number of points to retrieve. This affects the level of aggregation when combined with the start and end times.
    :type points: optional int

    .. note::
        We return data points at `start` and `end`. That is, this function is inclusive of the end points.

    .. note::
        If `points` is None, we use the default aggregation of 1 minute.

    :returns:
        list[(float,float)] -- pairs of the form (timestamp, value) for all data in datastream `ds` between dates `start` and `end`.
    """
    aggregation_string = getElasticSearchAggregationLevel(int(start), int(end))

    logging.debug("Aggregating on every {}".format(aggregation_string))

    # need to scale incoming start and end, since elasticsearch keeps the timestamp in ms
    start = int(start) * 1000
    end = int(end) * 1000

    res = requests.post(ELASTICSEARCH_URI + '/teleceptor-*/_field_stats?level=indices', json={
        "fields": ["@timestamp"],
        "index_constraints": {
            "@timestamp": {
                 "min_value": {
                    "lte": end,
                    # "format": "epoch_millis"
                 },
                 "max_value": {
                    "gte": start,
                    # "format": "epoch_millis"
                 }
              }
            }
        })

    # Example kibana query: {"index":["teleceptor-2015.09.28","teleceptor-2015.09.29"],"search_type":"count","ignore_unavailable":True}
    # {"size":0,"query":{"filtered":{"query":{"query_string":{"analyze_wildcard":true,"query":"ds:1"}},"filter":{"bool":{"must":[{"range":{"@timestamp":{"gte":1443407578481,"lte":1443493978481,"format":"epoch_millis"}}}],"must_not":[]}}}},"aggs":{"2":{"date_histogram":{"field":"@timestamp","interval":"1m","time_zone":"America/Denver","min_doc_count":1,"extended_bounds":{"min":1443407578481,"max":1443493978481}},"aggs":{"1":{"avg":{"field":"value"}}}}}}

    logging.debug("res.json: {}", res.json())
    index_query = res.json()['indices'].keys()

    if len(index_query) == 0:
        raise ValueError('No indices found in range ({}, {}), {}'.format(start, end, end - start))

    query = {
        "size": 0,
        "query": {
            "filtered": {
                "query": {
                    "query_string": {
                        "analyze_wildcard": True,
                        "query": "ds:{}".format(ds)
                    }
                },
                "filter": {
                    "bool": {
                        "must": [{
                            "range": {
                                "@timestamp": {
                                    "gte": start,
                                    "lte": end,
                                    "format": "epoch_millis"
                                }
                            }
                        }],
                        "must_not": []
                    }
                }
            }
        }, "aggs": {
            "2": {
                "date_histogram": {
                    "field": "@timestamp",
                    "interval": aggregation_string,
                    "min_doc_count": 1,
                    "extended_bounds": {
                        "min": start,
                        "max": end
                    }
                },
                "aggs": {
                    "1": {
                        "avg": {
                            "field": "value"
                        }
                    }
                }
            }
        }
    }

    # first we will match on datastream
    # query['match'] = {'ds':ds}

    # then we filter on dates starting with start and ending with end.
    # logging.info("Querying on timestamp range {} - {}".format(start, end))
    # query['range'] = {'@timestamp': {'gte': start, 'lte': end}}

    # TODO: Add aggregation option. Look into the Date Histogram Aggregation

    # TODO: Should we do some calculation for the aggregation time here, or have it passed in as a parameter?

    # query['aggs'] = {'values': {'date_histogram': {'field': '@timestamp', 'interval': '1m'}}}

    # final_query = {'filter': {'and': [
    # {key: query[key]} for key in query
    # ]}}
    # final_query['sort'] = [{'@timestamp': {'order': 'asc'}}]
    '''
    final_query['aggs'] = {
                           'values':
                               {'date_histogram':
                                    {'field': '@timestamp', 'interval': '1m', 'min_doc_count': 1},
                                'aggs':
                               {'avg_value':
                                    {'avg':
                                         {'field': 'value'}
                                     }
                                }
                                }
                           }
    '''
    # logging.debug("Built query: {}".format(final_query))
    # return get_elastic(elastic_buffer=final_query)
    logging.debug("Built query: {}".format(query))
    return get_elastic(elastic_buffer=query, index_info=index_query)


def get_elastic(elastic_buffer, index_info=None):
    """
    Make a query to elasticsearch with args in `elastic_buffer`.

    :parma elastic_buffer: The query json to provide to elastic search.
    :type elastic_buffer: dictionary

    :returns:
        list[(float,float)] -- pairs of the form (timestamp, value) for all data that matches the query in `elastic_buffer`

    .. todo::
        May want to pass in a list of indicies to search on

    """

    data = "{}\n{}\n".format(json.dumps({"index": index_info}), json.dumps(elastic_buffer))

    url = ELASTICSEARCH_URI + '_msearch'
    headers = {'Content-Type': 'application/x-ndjson'}

    response = requests.post(url, data=data, headers=headers).json()

    logging.debug("Got elasticsearch results: {}".format(response))

    return [(bucket['key']/1000, bucket['1']['value']) for bucket in response['responses'][0]['aggregations']['2']['buckets']]


if __name__ == "__main__":
    """
    Generate a simple sine wave
    """
    days = 30
    # min
    period = 12*60
    max = 1023

    start = time.time() - (days*period*2*60)

    docs = []
    for i in range(days*period*2):
        value = int(math.sin(i*(2.0*math.pi/period))*(max/2.0) + (max/2.0))
        docs.append({'@timestamp': int((i*60+start)*1000), 'value': value, 'ds': 1000})

        if(i % 500 == 0):
            insert_elastic(docs)
            docs = []
