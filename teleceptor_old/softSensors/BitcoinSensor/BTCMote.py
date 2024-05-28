
import requests
import json
import time
import logging

import teleceptor

queryrate = 60
blockchainURL = "http://blockchain.info/ticker"
teleceptorURL = "http://localhost:"+str(teleceptor.PORT)+"/api/station/"
caltime = time.time()


def main():
    if teleceptor.USE_DEBUG:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

    # loop forever getting 15 minute rate updates
    while True:
        data = getData()
        if data is None:
            # requests failed or JSON was garbled
            time.sleep(queryrate)
            continue
        motestring = {
            "info": {
                "uuid": "MyFirstBTCSensor",
                "name": "BTCRateSensor",
                "description": "Gets the 15 minute Bitcoin exchange rate",
                "in": [],
                "out": []
            }
        }
        readings = {'readings': []}
        for d in data:
            if d == "symbol":
                continue
            motestring['info']['out'].append({"units": data['symbol']})
            motestring['info']['out'][-1]["model"] = "BTCSensor"
            motestring['info']['out'][-1]["name"] = d
            motestring['info']['out'][-1]["description"] = str(d) + " Sensor"
            motestring['info']['out'][-1]["timestamp"] = caltime
            motestring['info']['out'][-1]["sensor_type"] = "float"
            readings['readings'].append([d, data[d], time.time()])
            logging.debug(d, data[d])
        postmessage = [{'info': motestring['info'], 'readings':readings['readings']}]

        for sensor in postmessage[0]['info']['in']:
            sensor.update({'meta_data': {'unixtime': time.time(), 'pid': 2, 'tty': "Web", "complex": {"nested": ["Hi", "Bye"]}}})
        for sensor in postmessage[0]['info']['out']:
            sensor.update({'meta_data': {'unixtime': time.time(), 'pid': 2, 'tty': "Web", "complex": {"nested": ["Hi", "Bye"]}}})
        logging.debug(postmessage)
        response = requests.post(teleceptorURL, data=json.dumps(postmessage))
        logging.debug(response)
        time.sleep(queryrate)


def getData():
    data = requests.get(blockchainURL)
    logging.debug(data)
    jdata = None
    try:
        jdata = json.loads(data.content)
    except Exception, e:
        logging.error(e)
        return None

    return jdata['USD']


if "__main__" == __name__:
    main()
