#include "Arduino.h"


/* 
-------------------------------------------------------------------------
Serial Config 
*/
#define SERIALTIMEOUT 1000 //milliseconds to wait for incoming bytes
#define USESOFTSERIAL 0

#if USESOFTSERIAL
#include <SoftwareSerial.h>
#define SOFTSERIALRX 6
#define SOFTSERIALTX 7
SoftwareSerial myserial(SOFTSERIALRX,SOFTSERIALTX);
#define SERIAL myserial
#else
#define SERIAL Serial
#endif

/* 
-------------------------------------------------------------------------
Json Config 
*/

typedef struct __attribute__ ((__packed__)) json{
    char* symbol;
    char type; //Can be 's':string, 'n'number, 'b',bool
    char* value;
} json;

typedef enum {START,BEGIN,SYMSTR,SYMEND,STARTVAL,STRVAL,READBOOL,READNUM,ENDSTRVAL,END} jsonState;

#define JSONMAXSIZE 64 //255 is max due to using an unsigned char counter
#define JSONMAXELEMENTS 8
//Globals needed for parser
char jsonData[JSONMAXSIZE];
json jsonRefs[JSONMAXELEMENTS];
unsigned char jsonRefCount=0;
unsigned char jsonDataCount=0;

/* 
-------------------------------------------------------------------------
Station Config 
*/

const char *  StationName = "Voltage Example";
const char * StationDescription = "Reads Voltage from A0-A5";
const char * Uuid = "VOLTS001"; 

#define NUMOUTPUTSENSORS 6
int outputSensorValues[] = {0,0,0,0,0,0};
const char * outputSensorNames[] = {"A0","A1","A2","A3","A4","A5"};

const char * outputSensorUnits[] = {"v", "v", "v", "v", "v", "v"};
const float outputSensorCoefficents[NUMOUTPUTSENSORS][2] = {{0.0049,0},{0.0049,0},{0.0049,0},{0.0049,0},{0.0049,0},{0.0049,0} };

#define NUMINPUTSENSORS 4
const int inputSensorPins[] = {2,3,4,5};
boolean inputSensorState[] = {false,false,false,false};
const char * inputSensorNames[] = {"D2","D3","D4","D5"};
const char * inputSensorDesc[] = {"Power Relay","Power Relay","Power Relay","Power Relay"};

/* 
-------------------------------------------------------------------------
Function Prototypes 
*/

void writeSensorState();
jsonState parseJson(char,jsonState);
void serialComm();

/*
--------------------------------------------------------------------------
void setup()
Set all pinModes and send them default values
--------------------------------------------------------------------------
*/

void setup(){
 
  SERIAL.begin(9600);  // start serial for output

  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);

  digitalWrite(2,LOW);
  digitalWrite(3,LOW);
  digitalWrite(4,LOW);
  digitalWrite(5,LOW);
}

/*
--------------------------------------------------------------------------
void loop()
Main program loop
Send sensor values back to teleceptor
--------------------------------------------------------------------------
*/

void loop() {
  for(int i = 0; i < 6;i++){
    outputSensorValues[i] = analogRead(i);
  }
  
  serialComm();
}

/*
--------------------------------------------------------------------------
serialComm()
Function that sends and recives data to teleceptor.
Send '%' to recive all sensor data formatted in json.
Send '@' plus json parameters to give instructions.
  ex: @{"PWR1":true, "PWR2":true}
  Turns pins 1 & 2 on
--------------------------------------------------------------------------
*/
void serialComm(){
    if(SERIAL.available() > 0){
        char serialRead = SERIAL.read();

        if(serialRead == '@'){
            unsigned long starttime = millis();
            jsonState state = START;
            while (state != END){
                if(millis() - starttime > SERIALTIMEOUT) break;
                if(SERIAL.available()){
                    starttime = millis();
                    state = parseJson(SERIAL.read(),state);
                }
            }

            if(state != END){
                //JSON from serial is bad, discard and continue
                return;
            }
            for(int i=0; i < jsonRefCount; i++){
                //we support only boolean right now (we only have boolean type inputs)

                //find the input sensor referred to by jsonRefs[i].symbol
                for(int j = 0; j < NUMINPUTSENSORS; j++){

                    if(strcmp(inputSensorNames[j],jsonRefs[i].symbol) == 0){
                        //message is for this sensor
                        if(jsonRefs[i].type == 'b'){
                            if(strcmp(jsonRefs[i].value,"t") == 0){
                                inputSensorState[j] = true;
                                //set pin high
                                digitalWrite(inputSensorPins[j], HIGH);
                            }
                            else{
                                inputSensorState[j] = false;
                                //set pin high
                                digitalWrite(inputSensorPins[j], LOW);
                            }
                        }
                        break; //done checking sensor names since we found a match
                    }
                }
            }
        }
        if(serialRead == '%'){
            printSensorInfo();
            writeSensorStates();
        }
        //flush any remaining bytes in serial buffer
        while(SERIAL.available() > 0){
            SERIAL.read();
        }
    }
}

/*
--------------------------------------------------------------------------
printSensorInfo()
Prints all of the sensor info. The resulting data should look like:
"{\"model\": \"POE Power Monitor\", \"out\": [{\"scale\": [0.0025, 0], \"u\": \"mA\", \"name\": \"CH1I\", \"s_t\":\"Current\"}, {\"scale\": [0.00125, 0], \"u\": \"v\", \"name\": \"CH1V\", \"s_t\": \"Voltage\"}, {\"scale\": [0.0025, 0], \"u\": \"mA\", \"name\": \"CH2I\", \"s_t\": \"Current\"}, {\"scale\": [0.00125, 0], \"u\": \"v\", \"name\": \"CH2V\", \"s_t\": \"Voltage\"}, {\"scale\": [0.0025, 0], \"u\": \"mA\", \"name\": \"CH3I\", \"s_t\": \"Current\"}, {\"scale\": [0.00125, 0], \"u\": \"v\", \"name\": \"CH3V\", \"s_t\": \"Voltage\"}, {\"scale\": [0.0025, 0], \"u\": \"mA\", \"name\": \"CH4I\", \"s_t\": \"Current\"}, {\"scale\": [0.00125, 0], \"u\": \"v\", \"name\": \"CH4V\", \"s_t\": \"Voltage\"}], \"in\": [{\"desc\": \"Power Relay\", \"u\": \"tf\", \"name\": \"PWR1\", \"s_t\": \"bool\"}, {\"desc\": \"Power Relay\", \"u\": \"tf\", \"name\": \"PWR2\", \"s_t\": \"bool\"}, {\"desc\": \"Power Relay\", \"u\": \"tf\", \"name\": \"PWR3\", \"s_t\": \"bool\"}, {\"desc\": \"Power Relay\", \"u\": \"tf\", \"name\": \"PWR4\", \"s_t\": \"bool\"}], \"uuid\": \"POESW00\", \"desc\": \"South Well\"}";

--------------------------------------------------------------------------
*/
void printSensorInfo(){
  SERIAL.print("{\"model\": \"");
  SERIAL.print(StationName);
  SERIAL.print("\", \"desc\": \"");
  SERIAL.print(StationDescription);
  SERIAL.print("\", \"uuid\": \"");
  SERIAL.print(Uuid);
  SERIAL.print("\", \"out\": [");
  for(int i = 0; i < NUMOUTPUTSENSORS; i++){
    if(i != 0) SERIAL.print(", ");

    SERIAL.print("{\"scale\": [");
    SERIAL.print(outputSensorCoefficents[i][0], 6);
    SERIAL.print(", ");
    SERIAL.print(outputSensorCoefficents[i][1], 6);
    SERIAL.print("], \"u\": \"");
    SERIAL.print(outputSensorUnits[i]);
    SERIAL.print("\", \"name\": \"");
    SERIAL.print(outputSensorNames[i]);
    SERIAL.print("\"}");
  }
  SERIAL.print("], \"in\": [");
  for(int i = 0; i < NUMINPUTSENSORS; i++){
    if(i != 0) SERIAL.print(", ");
    SERIAL.print("{\"name\": \"");
    SERIAL.print(inputSensorNames[i]);
    SERIAL.print("\", \"s_t\": \"");
    SERIAL.print(inputSensorState[i]);
    SERIAL.print("\", \"desc\": \"");
    SERIAL.print(inputSensorDesc[i]);
    SERIAL.print("\"}");
  }
  SERIAL.print("]}");
  SERIAL.println("");
}

/*
--------------------------------------------------------------------------
writeSensorState()
Convience function to write out the values of each sensor in the nested array format [ ["sensorname", sensorvalue], ["sensorname", sensorvalue], ... ]
--------------------------------------------------------------------------
*/

void writeSensorStates(){
    int numsensors = NUMOUTPUTSENSORS + NUMINPUTSENSORS;
    SERIAL.print("[");
    for(int i = 0; i < numsensors; i++){
        SERIAL.print("[");
        if(i < NUMOUTPUTSENSORS){
            SERIAL.print('"');
            SERIAL.print(outputSensorNames[i]);
            SERIAL.print('"');
            SERIAL.print(",");
            SERIAL.print(outputSensorValues[i]);
        }
        else{
            SERIAL.print('"');
            SERIAL.print(inputSensorNames[i-NUMOUTPUTSENSORS]);
            SERIAL.print('"');
            SERIAL.print(",");
            SERIAL.print(inputSensorState[i-NUMOUTPUTSENSORS]);
        }
        SERIAL.print("]");
        if(i < numsensors-1) SERIAL.print(",");
    }
    SERIAL.println("]");
}

/*
--------------------------------------------------------------------------
parseJson()
Read in a single char at a time, run though state machine
--------------------------------------------------------------------------
 */
jsonState parseJson(char c,jsonState state) {

    switch(state) {

        case START:
            if(c != '{')
                return START;

        case BEGIN:
            if(c == '"') {
                jsonRefs[jsonRefCount].symbol = &jsonData[jsonDataCount];
                //printf("count %d ",jsonDataCount);
                return SYMSTR;
            }
            else
                return BEGIN;

        case SYMSTR:
            if(c == '"')
                return SYMEND;
            else {
                jsonData[jsonDataCount++] = c;
                //printf("%c",c);
                return SYMSTR;
            }

        case SYMEND:
            jsonData[jsonDataCount++] = '\0';
            if(c == ':')
                return STARTVAL;
            else
                return SYMEND;

        case STARTVAL:
            if(c == '"') {
                jsonRefs[jsonRefCount].value = &jsonData[jsonDataCount];
                //printf("count %d ",jsonDataCount);
                jsonRefs[jsonRefCount].type = 's';
                return STRVAL;
            }
            else if(c == 't' || c == 'f') {
                jsonRefs[jsonRefCount].value = &jsonData[jsonDataCount];
                //printf("count %d ",jsonDataCount);
                jsonRefs[jsonRefCount].type = 'b';
                jsonData[jsonDataCount++] = c;
                return READBOOL;
            }
            else if(c == '-' || (c>=48 && c<=57) || c == '.' ) {
                jsonRefs[jsonRefCount].value = &jsonData[jsonDataCount];
                jsonRefs[jsonRefCount].type = 'n';
                jsonData[jsonDataCount++] = c;
                return READNUM;
            }

            else
                return STARTVAL;

        case STRVAL:
            if(c == '"')
                return ENDSTRVAL;
            else {
                jsonData[jsonDataCount++] = c;
                //printf("%c",c);
                return STRVAL;
            }

        case READNUM:
            if(c == ',') {
                jsonData[jsonDataCount++] = '\0';
                jsonRefCount++;
                return BEGIN;
            }
            else if(c == '}'){
                jsonData[jsonDataCount++] = '\0';
                jsonRefCount++;
                return END;
            }
            else if(c == '-' || (c>=48 && c<=57) || c == '.' ) {
                jsonData[jsonDataCount++] = c;
                return READNUM;
            }
            else
                return READNUM;


        case READBOOL:
            if(c == ',') {
                jsonData[jsonDataCount++] = '\0';
                jsonRefCount++;
                return BEGIN;
            }
            else if(c == '}'){
                jsonData[jsonDataCount++] = '\0';
                jsonRefCount++;
                return END;
            }
            else {
                //printf("%c",c);
                return READBOOL;
            }
        case ENDSTRVAL:
            jsonData[jsonDataCount++] = '\0';
            jsonRefCount++;
            if(c == ',')
                return BEGIN;
            else if (c == '}')
                return END;
            else
                return ENDSTRVAL;
    }
}





