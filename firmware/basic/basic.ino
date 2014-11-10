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
#include "Arduino.h"
#include <SoftwareSerial.h>
#define FS(x) (__FlashStringHelper*)(x)


/*
--------------------------------------------------------------------------
Configuration
--------------------------------------------------------------------------
*/

/* Serial config */
#define USESOFTSERIAL 0

//Values below are irrelevent if softserial is not used.
#if USESOFTSERIAL

#define SOFTSERIALRX 6
#define SOFTSERIALTX 7

#endif


/*Sensor pin config. May use Arduino macros. Value of 0 indicates no pin -
this is useful for e.g. 'soft' sensors that collect data not from a pin. See
RMSValue on MicSensor.*/
#define OUTPUTSENSORA A0
#define OUTPUTSENSORB A1
#define OUTPUTNAMEA "Sensor1"
#define OUTPUTNAMEB "Sensor2"

#define INPUTSENSORA 13
#define INPUTNAMEA "LED1"

//Required defines. Use 0 if no sensors of that type are present.
#define NUMOUTPUTSENSORS 2
#define NUMINPUTSENSORS 1

//Do not change
#if USESOFTSERIAL
SoftwareSerial myserial(SOFTSERIALRX,SOFTSERIALTX);
#define SERIAL myserial
#else
#define SERIAL Serial
#endif


/*
--------------------------------------------------------------------------
Variable declarations

Variables:
const char jsonData[] PROGMEM
TELECEPTORSERIAL serial
int outputsensorpins[]
int outputsensorvalues[]
char * outputsensornames[]
int inputsensorpins[]
boolean inputsensorstate[]
char * inputsensornames[]
--------------------------------------------------------------------------
*/

//Use Flash memory to save Ram
const char jsonData[] PROGMEM = "{\"model\": \"001-TEMP0002\",\"description\": \"TEMPMIC Sensor A\", \"in\": [], \"uuid\": \"TEMPMIC\", \"out\": [{\"name\": \"temp1\", \"description\": \"Temp Sensor\",\"units\":\"degrees F\",\"model\":\"m\",\"sensor_type\":\"float\", \"scale\": [0.18,32], \"timestamp\" : 1404436932.2},{\"name\": \"temp2\", \"description\": \"Temp Sensor\",\"units\":\"degrees F\",\"model\":\"m\",\"sensor_type\":\"float\", \"scale\": [0.18,32], \"timestamp\" : 1404436932.2},{\"name\": \"RMSValue\", \"description\": \"Temp Sensor\",\"units\":\"degrees F\",\"model\":\"m\",\"sensor_type\":\"float\", \"scale\": [1,0], \"timestamp\" : 1404436932.2},{\"name\": \"RMSCurrent\", \"description\": \"Temp Sensor\",\"units\":\"degrees F\",\"model\":\"m\",\"sensor_type\":\"float\", \"scale\": [1,0], \"timestamp\" : 1404436932.2}]}";

//modify the array defs based on the defined sensors above.
int outputsensorpins[] = {OUTPUTSENSORA, OUTPUTSENSORB};
int outputsensorvalues[] = {0, 0};
char * outputsensornames[] = {OUTPUTNAMEA, OUTPUTNAMEB};

int inputsensorpins[] = {INPUTSENSORA};
boolean inputsensorstate[] = {true};
char * inputsensornames[] = {INPUTNAMEA};



/*
--------------------------------------------------------------------------
Helper Functions

Functions:
void writeSensorStates()
void serialComm()
--------------------------------------------------------------------------
*/
/**
Convience function to write out the values of each sensor in the nested array format [ ["sensorname", sensorvalue], ["sensorname", sensorvalue], ... ]
*/
void writeSensorStates(){
    int numsensors = NUMOUTPUTSENSORS + NUMINPUTSENSORS;
    SERIAL.print("[");
    for(int i = 0; i < numsensors; i++){
        SERIAL.print("[");
        if(i < NUMOUTPUTSENSORS){
            SERIAL.print('"');
            SERIAL.print(outputsensornames[i]);
            SERIAL.print('"');
            SERIAL.print(",");
            SERIAL.print(outputsensorvalues[i]);
        }
        else{
            SERIAL.print('"');
            SERIAL.print(inputsensornames[i-NUMOUTPUTSENSORS]);
            SERIAL.print('"');
            SERIAL.print(",");
            SERIAL.print(inputsensorstate[i-NUMOUTPUTSENSORS]);
        }
        SERIAL.print("]");
        if(i < numsensors-1) SERIAL.print(",");
    }
    SERIAL.println("]");
}


/**
Param: Stream s - object of type Stream. Stream inherits from Print, so we still have access to print statements.

serialComm will read in serial data as described in the file basestationHOWTO (TODO: Update basestationHOWTO with current serial protocol). It will write out sensor states upon receiving a '%' symbol, and will interpret a flat JSON object upon receiving a '@' symbol. Input sensor states will be changed accordingly.

See Also: writeSensorStates
*/
void serialComm(){
    if(SERIAL.available() > 0){
        char serialRead = SERIAL.read();

        if(serialRead == '@'){
            while(!SERIAL.available()){} //wait for more data
            if (SERIAL.available()) {
                /* First, skip any accidental whitespace like newlines. */
                char whitespace = SERIAL.peek();
                while(whitespace == ' ' || whitespace == '\t' || whitespace == '\n'){SERIAL.read(); whitespace = SERIAL.peek();}
            }

            if (SERIAL.available()) {
                //replace this section with new JSON parser.
                /*
                aJsonObject *msg = aJson.parse(&serial_stream, jsonFilter);
                processMessage(msg);
                aJson.deleteItem(msg);
                */
            }
        }

        if(serialRead == '%'){
            SERIAL.println(FS(jsonData));

            writeSensorStates();
       }
    }
}



/*
--------------------------------------------------------------------------
Main Program code

Functions:
void setup()
void loop()
--------------------------------------------------------------------------
*/

// the setup routine runs once when you press reset:
void setup() {
    // initialize serial communication at 9600 bits per second:
    SERIAL.begin(9600);

    //initialize all input pins as OUTPUT and set HIGH
    for(int i = 0; i < NUMINPUTSENSORS; i++){
      pinMode(inputsensorpins[i], OUTPUT);
      digitalWrite(inputsensorpins[i], HIGH);
    }
}

// the loop routine runs over and over again forever:
void loop() {

    for(int i = 0; i < NUMOUTPUTSENSORS; i++){
      if(outputsensorpins[i] != 0)
        outputsensorvalues[i] = analogRead(outputsensorpins[i]);
    }


    /* Since we track and modify the state of the sensors via messages from serial, we don't read from their pin to get their state.
    */
    /*
    for(int i = 0; i < NUMINPUTSENSORS; i++{
      inputsensorstate[i] = analogRead(inputsensorpins[i]);
    }
    */


    //check for data on serial
    serialComm();


}




