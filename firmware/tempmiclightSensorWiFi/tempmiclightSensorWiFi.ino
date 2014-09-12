/*
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
*/

#include <aJSON.h>

#include <SoftwareSerial.h>

#define LED 13
char * jsonFilter[] = {"LED1"};
int inputPins[1] = {13};
boolean pinState[1] = {true};

char serialRead;
char channel;
char value;
int tempValue = 0;
int lightValue = 0;
float RMSValue = 0;
int RMSCurrent = 0;
int numSamples = 0;
SoftwareSerial mySerial(6,7);

aJsonStream serial_stream(&mySerial);

static const char jsonData[] = "{\"model\": \"WifiTmpMicLight\",\"description\": \"Wifi Temperature/Audio/Light Sensor\", \"in\": [{\"timestamp\": 1404436932.2,\"name\": \"LED1\" ,\"units\": \"T/F\", \"description\": \"status\", \"sensor_type\": \"bool\"}], \"uuid\": \"TEMPMICLIGHTWIFI1\", \"out\": [{\"name\": \"WIFITEMP1\", \"description\": \"Temperature Sensor\",\"units\":\"Degrees F\",\"model\":\"LM335\",\"sensor_type\":\"float\", \"scale\": [0.4507,-11.4872], \"timestamp\" : 1404436932.2},{\"name\": \"WIFILIGHT1\", \"description\": \"Temperature Sensor\",\"units\":\"Lumens\",\"model\":\"Light\",\"sensor_type\":\"float\", \"scale\": [1,0], \"timestamp\" : 1404436932.2}, {\"name\": \"WIFIMIC1_RMS\", \"description\": \"Audio Sensor RMS\",\"units\":\"Degrees F\",\"model\":\"MIC\",\"sensor_type\":\"float\", \"scale\": [1,0], \"timestamp\" : 1404436932.2},{\"name\": \"WIFIMIC1_Current\", \"description\": \"Audio Sensor RMS\",\"units\":\"Degrees F\",\"model\":\"MIC\",\"sensor_type\":\"float\", \"scale\": [1,0], \"timestamp\" : 1404436932.2}]}";

// the setup routine runs once when you press reset:
void setup() {
    // initialize serial communication at 9600 bits per second:
    mySerial.begin(9600);
    pinMode(LED, OUTPUT);
}

/* Process message like: { "in1": true/false} */
void processMessage(aJsonObject *msg)
{

  for(int i = 0; i < 1; i++)
  {
    aJsonObject *value = aJson.getObjectItem(msg, jsonFilter[i]);
    if(!value){ //input not provided for particular channel
      continue;
    }
    if(value->type == aJson_True){ //turn on
      digitalWrite(inputPins[i], HIGH);
      pinState[i] = true;
    }
    else if(value->type == aJson_False){ //turn off
      digitalWrite(inputPins[i], LOW);
      pinState[i] = false;
    }
    else{ //unknown
      continue;
    }
  }

}//end processMessage

// the loop routine runs over and over again forever:
void loop() {
    // read the input on analog pin 0:
    tempValue = analogRead(A0);
    RMSCurrent = analogRead(A1)-512;
    if(RMSCurrent < 0){
      RMSCurrent = RMSCurrent *-1;
    }
    lightValue = analogRead(A2);

    RMSValue =  (RMSCurrent + numSamples*RMSValue)/(numSamples+1);
    numSamples = numSamples +1;
    if(numSamples < 0){
      numSamples = 0;
    }

    // print out the value you read:

    while( mySerial.available() > 0) {
        serialRead = mySerial.read();

    if (serialRead == '%') {
            numSamples = 0;
            mySerial.println(jsonData);
            mySerial.print("[[\"WIFITEMP1\",");
            mySerial.print(tempValue);
            mySerial.print("],[");
            mySerial.print("\"WIFILIGHT1\",");
            mySerial.print(lightValue);
            mySerial.print("],[");
            mySerial.print("\"WIFIMIC1_Current\",");
            mySerial.print(RMSCurrent);
            mySerial.print("],[");
            mySerial.print("\"WIFIMIC1_RMS\",");
            mySerial.print(RMSValue);
            mySerial.print("],[");
            mySerial.print("\"LED1\",");
            mySerial.print(pinState[0]);
            mySerial.println("]]");

        }

        if (serialRead == '#') {
            mySerial.println(jsonData);
        }

        if (serialRead == '$') {

            mySerial.println(tempValue);
        }

        if(serialRead == '@'){

        while(!serial_stream.available()){} //wait for more data
         if (serial_stream.available()) {
           /* First, skip any accidental whitespace like newlines. */
           serial_stream.skip();
         }

         if (serial_stream.available()) {
            aJsonObject *msg = aJson.parse(&serial_stream, jsonFilter);
            processMessage(msg);
            aJson.deleteItem(msg);
         }
        }
    }
}
