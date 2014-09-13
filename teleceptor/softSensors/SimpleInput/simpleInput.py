import requests
import time
import json
caltime = time.time()
examplevalue = 22
while True:
    #build object to send to server
    jsonExample = [{"info":{"uuid":"mote1234", "name":"myfirstmote","description":"My first mote","out":[],"in":[{"name":"in1","sensor_type":"float","timestamp":caltime,"meta_data":{}}]},"readings":[["in1",examplevalue,time.time()]]}]

    #send to server
    serverURL = "http://localhost:" + str(8000) + "/api/delegation/"
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
            examplevalue = parsedNewValues["in1"]

    #sleep based on rate of query
    time.sleep(3)
