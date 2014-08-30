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


#define in1 4
#define in2 6
#define in3 5
#define in4 7

char serialRead;
char channel;
char value;
int sensorValue = 0;
//We only care about inputs 1, 2, 3, and 4
//All other JSON name/value pairs will be ignored to save memory
char** jsonFilter = (char *[]){"in1","in2","in3","in4",NULL};
int inputPins[4] = {4, 6, 5, 7};
boolean pinState[4] = {true, true, true, true};

static const char jsonData[] = "{\"model\": \"001-RELAY0001\",\"description\": \"4 Channel Relay Board\", \"in\": [{\"timestamp\": 1404436932.2,\"name\": \"in1\" ,\"units\": \"T\F\", \"description\": \"status\", \"sensor_type\": \"bool\"}, {\"timestamp\": 1404436932.2,\"name\": \"in2\" ,\"units\": \"T\F\", \"description\": \"status\", \"sensor_type\": \"bool\"}, {\"timestamp\": 1404436932.2,\"name\": \"in3\" ,\"units\": \"T\F\", \"description\": \"status\", \"sensor_type\": \"bool\"}, {\"timestamp\": 1404436932.2,\"name\": \"in4\" ,\"units\": \"T\F\", \"description\": \"status\", \"sensor_type\": \"bool\"}], \"uuid\": \"RELAY1234\", \"out\": []}";


aJsonStream serial_stream(&Serial);

// the setup routine runs once when you press reset:
void setup() {
    // initialize serial communication at 9600 bits per second:
    Serial.begin(9600);
    //Serial.println("Started");
    pinMode(in1, OUTPUT);
    pinMode(in2, OUTPUT);
    pinMode(in3, OUTPUT);
    pinMode(in4, OUTPUT);
    digitalWrite(in1, HIGH);
    digitalWrite(in2, HIGH);
    digitalWrite(in3, HIGH);
    digitalWrite(in4, HIGH);
}


/* Process message like: { "in1": true/false, "in2": true/false, "in3": true/false, "in4": true/false } */
void processMessage(aJsonObject *msg)
{

  for(int i = 0; i < 4; i++)
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
          Serial.println(jsonData);
          Serial.print("[[\"in1\",");
   	Serial.print(pinState[0]);
          Serial.print("],");
          Serial.print("[\"in2\",");
   	Serial.print(pinState[1]);
          Serial.print("],");
          Serial.print("[\"in3\",");
   	Serial.print(pinState[2]);
          Serial.print("],");
          Serial.print("[\"in4\",");
   	Serial.print(pinState[3]);
          Serial.println("]]");

       }
     }

}//end loop




