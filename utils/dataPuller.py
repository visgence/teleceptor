import requests
import json

TOURL = "http://0.0.0.0:8000/api/station"
FROMURL = ""
DATASTREAM = "4"


if __name__ == "__main__":
    jsonObj = [{
        "info": {
            "uuid": "copiedSensor",
            "name": "copiedSensor",
            "description": "",
            "out": [],
            "in":[{
                "name": "in1",
                "sensor_type": "float",
                "timestamp": 30000,
                "meta_data": {
                    'meta title': 'meta description'
                }
            }]
        },
        "readings": []
    }]
    url = "{}/readings?datastream={}".format(FROMURL, DATASTREAM)
    data = requests.get(url).json()
    count = 0

    for i in data['readings']:
        jsonObj[0]['readings'].append(["in1", i[1], i[0]])
        count += 1

    sent = requests.post(TOURL, json.dumps(jsonObj))
