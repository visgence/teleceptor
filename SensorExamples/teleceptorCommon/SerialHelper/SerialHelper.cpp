/*
Author: Victor Szczepanski

SerialHelper - Library to simplify using the teleceptor serial protocol.

serialComm is the main entry point, and it calls other functions in this library to interpret incoming serial data. Read the description for serialComm for more information.

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

#include <Config.h>
#include "Arduino.h"
#define FS(x) (__FlashStringHelper*)(x)

/**
Convience function to write out the values of each sensor in the nested array format [ ["sensorname", sensorvalue], ["sensorname", sensorvalue], ... ]
*/
void writeSensorStates(TELECEPTORSERIAL s){
    int numsensors = NUMOUTPUTSENSORS + NUMINPUTSENSORS;
    s.print("[");
    for(int i = 0; i < numsensors; i++){
        s.print("[");
        if(i < NUMOUTPUTSENSORS){
            s.print(outputsensornames[i]);
            s.print(",");
            s.print(outputsensorvalues[i]);
        }
        else{
            s.print(inputsensornames[i-NUMOUTPUTSENSORS]);
            s.print(",");
            s.print(inputsensorstate[i-NUMOUTPUTSENSORS]);
        }
        s.print("]");
        if(i < numsensors-1) s.print(",");
    }
    s.print("]");
}


/**
Param: Stream s - object of type Stream. Stream inherits from Print, so we still have access to print statements.

serialComm will read in serial data as described in the file basestationHOWTO (TODO: Update basestationHOWTO with current serial protocol). It will write out sensor states upon receiving a '%' symbol, and will interpret a flat JSON object upon receiving a '@' symbol. Input sensor states will be changed accordingly.

See Also: writeSensorStates
*/
void serialComm(TELECEPTORSERIAL s){
    if(s.available() > 0){
        char serialRead = s.read();

        if(serialRead == '@'){
            while(!s.available()){} //wait for more data
            if (s.available()) {
                /* First, skip any accidental whitespace like newlines. */
                char whitespace = s.peek();
                while(whitespace == ' ' || whitespace == '\t' || whitespace == '\n'){s.read(); whitespace = s.peek();}
            }

            if (s.available()) {
                //replace this section with new JSON parser.
                /*
                aJsonObject *msg = aJson.parse(&serial_stream, jsonFilter);
                processMessage(msg);
                aJson.deleteItem(msg);
                */
            }
        }

        if(serialRead == '%'){
            s.println(FS(jsonData));

            writeSensorStates(s);
       }
    }
}



