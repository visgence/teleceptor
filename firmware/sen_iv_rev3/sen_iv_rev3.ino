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

#define STATUS_LED 4
#define TX_LED 2
#define RX_LED 3

#define LCD_TX A5
#define LCD_RX A4

SoftwareSerial lcdSerial(LCD_RX, LCD_TX);

//current and voltage sensing parameters
#define Vin A0
#define Iin A1

int V_adc = 0; //ADC value of voltage sensor
int I_adc = 0; //ADC value of current sensor

float V_scale = 0.0; //scaled voltage value (volts)
float I_scale = 0.0; //scaled current value (amps)

float V_a = 0.128755; //voltage slope
float V_b = -65.794; //voltage offset

float I_a = 0.048828; //voltage slope
float I_b = -25.0; //voltage offset

char serialRead;
char channel;
char value;

static const char jsonData[] = "{\"model\": \"001-IV0001\",\"description\": \"Voltage and Ampres Sensor A\", \"in\": [{\"timestamp\": 1404436932.2,\"name\": \"in1\" ,\"units\": \"T\F\", \"description\": \"status\", \"sensor_type\": \"bool\"}], \"uuid\": \"voltAmpSensorA\", \"out\": [{\"name\": \"Vout\", \"description\": \"Voltage Sensor\",\"units\":\"Volts\",\"model\":\"001-V0001\",\"sensor_type\":\"float\", \"scale\": [0.128755, -65.794], \"timestamp\" : 1404436932.2}, {\"name\": \"Iout\",\"description\": \"Ampres Sensor\",\"model\":\"001-I0001\",\"sensor_type\":\"float\",\"units\":\"Ampres\", \"scale\": [0.048828, -25.0], \"timestamp\": 1404436932.2}]}";


// the setup routine runs once when you press reset:
void setup() {
    //initialize serial
    Serial.begin(9600);
}

void loop() {

    V_adc= analogRead(Vin);
    I_adc = analogRead(Iin);

    while( Serial.available() > 0) {
        serialRead = Serial.read();

        if (serialRead == '%') {
                Serial.println(jsonData);
                Serial.print("[[\"Vout\",");
                Serial.print(V_adc);
                Serial.print("],[");
                Serial.print("\"Iout\",");
                Serial.print(I_adc);
                Serial.print("],[");
                Serial.print("\"in1\",");
                Serial.println("true]]");
        }

        if (serialRead == '#') {
                Serial.println(jsonData);
        }

        if (serialRead == '$') {
                Serial.print(V_adc);
                Serial.print(" V | ");
                Serial.print(I_adc);
                Serial.println(" A");
        }

        if (serialRead == '@') {
            while (true) {
                if (Serial.available() >= 2) {
                    channel = Serial.read();
                    value = Serial.read();
                    if (channel == '0' && value == '1')
                            Serial.println('&');
                    if (channel == '0' && value == '0')
                            Serial.println('&');

                    break;
                }
            }
        }
    }
}
