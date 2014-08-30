"""
    (c) 2014 Visgence, Inc.

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

import requests
import json
import time

import teleceptor

queryrate = 60
blockchainURL = "http://blockchain.info/ticker"
teleceptorURL = "http://localhost:"+str(teleceptor.PORT)+"/api/delegation/"
caltime = time.time()
def main():
    #loop forever getting 15 minute rate updates
    while True :
        data = getData()
        if data is None:
            #requests failed or JSON was garbled
            time.sleep(queryrate)
            continue
        motestring = {"info":
        {"uuid":"MyFirstBTCSensor", "name":"BTCRateSensor",
         "description":"Gets the 15 minute Bitcoin exchange rate",
         "in":[], "out":[]}}
        readings = {'readings':[]}
        for d in data:
            if d == "symbol":
                continue
            motestring['info']['out'].append({"units":data['symbol']})
            motestring['info']['out'][-1]["model"] = "BTCSensor"
            motestring['info']['out'][-1]["name"] = d
            motestring['info']['out'][-1]["description"] = str(d) + " Sensor"
            motestring['info']['out'][-1]["timestamp"] = caltime
            motestring['info']['out'][-1]["sensor_type"] = "float"
            readings['readings'].append([d, data[d], time.time()])
            print(d, data[d])
        postmessage = [{'info':motestring['info'], 'readings':readings['readings']}]

        for sensor in postmessage[0]['info']['in']:
            sensor.update({'meta_data':{'unixtime':time.time(),'pid' : 2, 'tty' : "Web", "complex":{"nested": ["Hi","Bye"]}}})
        for sensor in postmessage[0]['info']['out']:
            sensor.update({'meta_data':{'unixtime':time.time(),'pid' : 2, 'tty' : "Web", "complex":{"nested": ["Hi","Bye"]}}})
        print(postmessage)
        response = requests.post(teleceptorURL,data=json.dumps(postmessage))
        print(response)
        time.sleep(queryrate)



def getData():
	data = requests.get(blockchainURL)
	print(data)
	jdata = None
	try:
		jdata = json.loads(data.content)
	except:
		return None

	return jdata['USD']


if "__main__" == __name__:
    main()

