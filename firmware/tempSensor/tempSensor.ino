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
#define FS(x) (__FlashStringHelper*)(x)

char serialRead;
char channel;
char value;
int sensorValue = 0;
//We only care about inputs 1
//All other JSON name/value pairs will be ignored to save memory
char * jsonFilter[] = {"LED1"};
int inputPins[1] = {13};
boolean pinState[1] = {true};

//Use Flash memory to save Ram
const char jsonData[] PROGMEM = "{\"model\": \"001-TEMP0001\",\"description\": \"Temperature Sensor A\", \"in\": [{\"timestamp\": 1404436932.2,\"name\": \"LED1\" ,\"units\": \"T/F\", \"description\": \"status\", \"sensor_type\": \"bool\"}], \"uuid\": \"TEMP1234\", \"out\": [{\"name\": \"TEMP1\", \"description\": \"Temperature Sensor\",\"units\":\"Degrees F\",\"model\":\"LM335\",\"sensor_type\":\"float\", \"scale\": [0.18, 32], \"timestamp\" : 1404436932.2}]}";

aJsonStream serial_stream(&Serial);

// the setup routine runs once when you press reset:
void setup() {
    // initialize serial communication at 9600 bits per second:
    Serial.begin(9600);
    pinMode(inputPins[0], OUTPUT);
    digitalWrite(inputPins[0], HIGH);
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
    sensorValue = analogRead(A0);
    // print out the value you read:

    if(Serial.available() > 0){
       serialRead = Serial.read();

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

       if(serialRead == '%'){
            Serial.println(FS(jsonData));

            Serial.print("[[");

            Serial.print("\"LED1\",");
            Serial.print(pinState[0]);
            Serial.print("],");

            Serial.print("[\"TEMP1\",");
            Serial.print(sensorValue);

            Serial.println("]]");
       }
     }
}



