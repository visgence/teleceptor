/*
Author: Victor Szczepanski

Config.h - Generalized configuration file for teleimperium or Arduino based microcontrollers.

This file defines numerous settings which are used by the teleceptor compatible microcontrollers.
The user should configure this file to suit the firmware he/she wants to upload to their
microcontroller. The main area for configuration is the number of sensors, which pins they are on, and
what their names are. It is the user's responsibility to ensure the jsonData string matches the defined
sensors. Any mismatch in naming may result in unresponsive input sensors or undefined behaviour.

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

#ifndef CONFIG.H
#define CONFIG.H

#include "Arduino.h"


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


//Use Flash memory to save Ram
const char jsonData[] PROGMEM = "{\"model\": \"001-TEMP0002\",\"description\": \"TEMPMIC Sensor A\", \"in\": [], \"uuid\": \"TEMPMIC\", \"out\": [{\"name\": \"temp1\", \"description\": \"Temp Sensor\",\"units\":\"degrees F\",\"model\":\"m\",\"sensor_type\":\"float\", \"scale\": [0.18,32], \"timestamp\" : 1404436932.2},{\"name\": \"temp2\", \"description\": \"Temp Sensor\",\"units\":\"degrees F\",\"model\":\"m\",\"sensor_type\":\"float\", \"scale\": [0.18,32], \"timestamp\" : 1404436932.2},{\"name\": \"RMSValue\", \"description\": \"Temp Sensor\",\"units\":\"degrees F\",\"model\":\"m\",\"sensor_type\":\"float\", \"scale\": [1,0], \"timestamp\" : 1404436932.2},{\"name\": \"RMSCurrent\", \"description\": \"Temp Sensor\",\"units\":\"degrees F\",\"model\":\"m\",\"sensor_type\":\"float\", \"scale\": [1,0], \"timestamp\" : 1404436932.2}]}";


Stream serial;
#if USESOFTSERIAL
serial = SoftSerial(SOFTSERIALRX,SOFTSERIALTX);
#else
serial = Serial;
#endif

//modify the array defs based on the defined sensors above.
int outputsensorpins[NUMOUTPUTSENSORS] = {OUTPUTSENSORA, OUTPUTSENSORB};
int outputsensorvalue[NUMOUTPUTSENSORS] = {0, 0};
char * outputsensornames[] = {OUTPUTNAMEA, OUTPUTNAMEB};


int inputsensorpins[NUMINPUTSENSORS] = {INPUTSENSORA};
boolean inputsensorstate[NUMINPUTSENSORS] = {true};
char * inputsensornames[] = {INPUTNAMEA};



#endif
