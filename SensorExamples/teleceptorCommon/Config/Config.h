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


#ifndef CONFIG_H
#define CONFIG_H

#include "Arduino.h"
#include "HardwareSerial.h"


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

#if USESOFTSERIAL
typedef SoftSerial *TELECEPTORSERIAL;
extern TELECEPTORSERIAL serial;
#else
typedef HardwareSerial TELECEPTORSERIAL;
extern TELECEPTORSERIAL serial;
#endif

//modify the array defs based on the defined sensors above.
extern int outputsensorpins[];
extern int outputsensorvalues[];
extern char * outputsensornames[];


extern int inputsensorpins[];
extern boolean inputsensorstate[];
extern char * inputsensornames[];

extern const char jsonData[] PROGMEM;


#endif
