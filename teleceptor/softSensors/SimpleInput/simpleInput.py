import requests
import time
import json


class simpleInput():
    def __init__(self):
        self.caltime = time.time()
        self.examplevalue = 22

    def sendData(self):
        #build object to send to server
        jsonExample = [{"info":{"uuid":"mote1234", "name":"myfirstmote","description":"My first mote","out":[],
        "in":[{"name":"in1","sensor_type":"float","timestamp":self.caltime,"meta_data":{}}]},"readings":[["in1",self.examplevalue,time.time()]]}]

        #send to server
        serverURL = "http://localhost:" + str(8000) + "/api/station/"
        response = requests.post(serverURL, data=json.dumps(jsonExample))

        print response
        print response.text
        #decode response
        responseData = json.loads(response.text)

        #check for any new values from server
        if 'newValues' in responseData:
            parsedNewValues = {}
            for sen in responseData['newValues']:
                if len(responseData['newValues'][sen]) == 0:
                    continue
                message = responseData['newValues'][sen][-1]
                for senName,senMessage in message.items():
                    if senName == "id":
                        pass
                    elif senName == "message":
                        parsedNewValues[sen] = senMessage

            #update value
            if "in1" in parsedNewValues:
                self.examplevalue = parsedNewValues["in1"]

        return response


if __name__ == "__main__":
    while True:
        sendData()

        #sleep based on rate of query
        time.sleep(3)



