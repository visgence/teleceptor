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

#include <SoftwareSerial.h>


#define LED 13

char serialRead;
char channel;
char value;
int sensorValue = 0;
SoftwareSerial mySerial(6,7);

static const char jsonData[] = "{\"model\": \"WifiTmp\",\"description\": \"Wifi Sensor\", \"in\": [{\"timestamp\": 1404436932.2,\"name\": \"LED1\" ,\"units\": \"F\", \"description\": \"status\", \"sensor_type\": \"bool\"}], \"uuid\": \"TEMPWIFI1\", \"out\": [{\"name\": \"WIFITEMP1\", \"description\": \"Temperature Sensor\",\"units\":\"Degrees F\",\"model\":\"LM335\",\"sensor_type\":\"float\", \"scale\": [1,0], \"timestamp\" : 1404436932.2}]}";

// the setup routine runs once when you press reset:
void setup() {
    // initialize serial communication at 9600 bits per second:
    mySerial.begin(9600);
    pinMode(LED, OUTPUT);
}

// the loop routine runs over and over again forever:
void loop() {
    // read the input on analog pin 0:
    sensorValue = analogRead(A0);
    // print out the value you read:

    while( mySerial.available() > 0) {
        serialRead = mySerial.read();

	if (serialRead == '%') {
            mySerial.println(jsonData);
            mySerial.print("[[\"WIFITEMP1\",");
 	    mySerial.print(sensorValue);
            mySerial.print("],[");
            mySerial.print("\"LED1\",");
            mySerial.println("true]]");
        }

        if (serialRead == '#') {
            mySerial.println(jsonData);
        }

        if (serialRead == '$') {

            mySerial.println(sensorValue);
        }

        if (serialRead == '@') {
            while (true) {
                if (mySerial.available() >= 2) {
                    channel = mySerial.read();
                    value = mySerial.read();
                    if (channel == '0' && value == '1') {
                        digitalWrite(LED, HIGH);
                        mySerial.println('&');
                    }
                    if (channel == '0' && value == '0') {
                        digitalWrite(LED, LOW);
                        mySerial.println('&');
                    }

                    break;
                }
            }
        }
    }
}
