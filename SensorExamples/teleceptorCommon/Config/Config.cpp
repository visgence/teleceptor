/*
Author: Victor Szczepanski

Config.cpp - Implementation of generalized configuration file for teleimperium or Arduino based microcontrollers.

This file defines the values for the data structures declared in Config.h. The user only needs to configure the jsonData string,
and the output/input arrays based on the configuration of the teleimperium. It is the user's responsibility to 
ensure that this file is compatible with Config.h, i.e. defines the same number of elements in the arrays as declared in Config.h.

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

#include "Config.h"
#include "Arduino.h"

//Use Flash memory to save Ram
const char jsonData[] PROGMEM = "{\"model\": \"001-TEMP0002\",\"description\": \"TEMPMIC Sensor A\", \"in\": [], \"uuid\": \"TEMPMIC\", \"out\": [{\"name\": \"temp1\", \"description\": \"Temp Sensor\",\"units\":\"degrees F\",\"model\":\"m\",\"sensor_type\":\"float\", \"scale\": [0.18,32], \"timestamp\" : 1404436932.2},{\"name\": \"temp2\", \"description\": \"Temp Sensor\",\"units\":\"degrees F\",\"model\":\"m\",\"sensor_type\":\"float\", \"scale\": [0.18,32], \"timestamp\" : 1404436932.2},{\"name\": \"RMSValue\", \"description\": \"Temp Sensor\",\"units\":\"degrees F\",\"model\":\"m\",\"sensor_type\":\"float\", \"scale\": [1,0], \"timestamp\" : 1404436932.2},{\"name\": \"RMSCurrent\", \"description\": \"Temp Sensor\",\"units\":\"degrees F\",\"model\":\"m\",\"sensor_type\":\"float\", \"scale\": [1,0], \"timestamp\" : 1404436932.2}]}";


#if USESOFTSERIAL
TELECEPTORSERIAL serial = SoftSerial(SOFTSERIALRX,SOFTSERIALTX);
#else
TELECEPTORSERIAL serial  = Serial;
#endif

int outputsensorpins[] = {OUTPUTSENSORA, OUTPUTSENSORB};
int outputsensorvalues[] = {0, 0};
char * outputsensornames[] = {OUTPUTNAMEA, OUTPUTNAMEB};

int inputsensorpins[] = {INPUTSENSORA};
boolean inputsensorstate[] = {true};
char * inputsensornames[] = {INPUTNAMEA};

