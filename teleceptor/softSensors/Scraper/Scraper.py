from lxml import html
import urllib2
from bs4 import BeautifulSoup as bs
import json
import requests
import time


def getPageData(ip):
    url = ""join(["http://", ip, "/top.cgi?xsrf=&1"])
    newObj = {
        "TransmitPower": 0,
        "ReceivePower": 0,
        "VectorError": 0,
        "LinkLoss": 0,
        "TransmitDataRate": 0,
        "ReceiveDataRate": 0,
        "LinkCapacity": 0,
    }

    page = urllib2.urlopen(url)
    soup = bs(page, 'lxml')
    for idx, val in enumerate(soup.find_all('table', class_='copybold')):
        newval = float(val.find(title='Latest').get_text())
        if idx is 0:
            newObj['TransmitPower'] = newval
        elif idx is 1:
            newObj['ReceivePower'] = newval
        elif idx is 2:
            newObj['VectorError'] = newval
        elif idx is 3:
            newObj['LinkLoss'] = newval
        elif idx is 4:
            newObj['TransmitDataRate'] = newval
        elif idx is 5:
            newObj['ReceiveDataRate'] = newval
        else:
            print "Something went wrong!"

    # Unfortunately, the site has no ids or class closer than copybold for the Link Capacity, that's why I'm looking directly and the indices here
    for idx, val in enumerate(soup.find_all(class_='copybold')):
        if idx == 20:
            for idx2, val2 in enumerate(val.find_all('td')):
                if idx2 == 5:
                    newObj["LinkCapacity"] = float(val2.get_text().split(" ")[0])
    return newObj


def formatData(obj):
    types = ["TransmitPower", "ReceivePower", "VectorError", "LinkLoss", "TransmitDataRate", "ReceiveDataRate"]
    formattedObject = []
    for i in types:
        formattedObject.append({
            "info": {
                "uuid": "0001",
                "name": "".join(["cambium_", i]),
                "in": [{
                    "name": "".join(["cambium_", i]),
                    "timestamp": 30000,
                    "metadata": {},
                    "sensor_type": "float"
                }],
                "out": []
            },
            "readings": [
                ["".join(["cambium_", i]), obj[i], time.time()],
            ]
        })

    return formattedObject


def sendData(obj, url):
    teleUrl = "".join(["http://", url, "/api/delegation/"])
    response = requests.post(teleUrl, data=json.dumps(obj))
    return response


if __name__ == "__main__":
    ip = '0.0.0.0'
    myObj = getPageData(ip)
    # print "myObj:"
    # print json.dumps(myObj, indent=2)
    returnObj = formatData(myObj)
    # print"\n\n\n"
    # print "returnObj:"
    # print json.dumps(returnObj, indent=2)
    teleceptorURL = "localhost:8080"
    response = sendData(returnObj, teleceptorURL)
    # print "\nThe response is: {}".format(response)
