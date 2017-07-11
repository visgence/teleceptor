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

#include <SerialHelper.h>
#include <Config.h>


// the setup routine runs once when you press reset:
void setup() {
    // initialize serial communication at 9600 bits per second:
    serial.begin(9600);

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
    serialComm(serial);


}




