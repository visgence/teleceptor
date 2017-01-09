import requests
import time
import json
import argparse


class simpleInput():
    def __init__(self):
        self.caltime = time.time()
        self.examplevalue = 22

    def sendData(self, data=None, host=None):
        # build object to send to server
        if data is None:
            data = [{
                "info": {
                    "uuid": "mote1234",
                    "name": "myfirstmote",
                    "description": "My first mote",
                    "out": [],
                    "in":[{
                        "name": "in1",
                        "sensor_type": "float",
                        "timestamp": self.caltime,
                        "meta_data": {}
                    }]
                },
                "readings": [["in1", self.examplevalue, time.time()]]
            }]

        # send to server
        if host is None:
            host = "localhost"

        serverURL = "http://" + host + ":" + str(8000) + "/api/station/"
        response = requests.post(serverURL, data=json.dumps(data))

        # decode response
        responseData = json.loads(response.text)

        # check for any new values from server
        if 'newValues' in responseData:
            parsedNewValues = {}
            for sen in responseData['newValues']:
                if len(responseData['newValues'][sen]) == 0:
                    continue
                message = responseData['newValues'][sen][-1]
                for senName, senMessage in message.items():
                    if senName == "id":
                        pass
                    elif senName == "message":
                        parsedNewValues[sen] = senMessage

            # update value
            if "in1" in parsedNewValues:
                self.examplevalue = parsedNewValues["in1"]

        return response


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='By default acts as a sample input sensor. With arguments, can post data.')
    parser.add_argument('--name',  help="name of sensor", default=None, dest='name')
    parser.add_argument('--value', type=float, help="value to post", default=None, dest='value')
    parser.add_argument('--host', help="IP of host server.", default=None, dest='host')

    args = parser.parse_args()
    if args.name is not None and args.value is not None and args.host is not None:

        data = [{
            "info": {
                "uuid": "",
                "name": "myfirstmote",
                "description": "My first mote",
                "in": [],
                "out":[{
                    "name": args.name,
                    "sensor_type": "float",
                    "timestamp": time.time(),
                    "meta_data": {}
                }]
            },
            "readings": [[args.name, args.value, time.time()]]}]

        si = simpleInput()

    else:
        while True:
            sendData()

            # sleep based on rate of query
            time.sleep(3)
