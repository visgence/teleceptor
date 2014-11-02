//Evan Salazar
//2014 Visgence Inc.
//A Very simple JSON parser that can fit on a microcontroller 

#include <stdio.h>
//Only needed for strlen
#include <string.h>

typedef struct __attribute__ ((__packed__)) json{
    char* symbol;
    char type; //Can be 's':string, 'n'number, 'b',bool
    char* value;
} json;


//Max Memory used,
#define JSONMAXSIZE 64 //255 is max due to using an unsigned char counter 
#define JSONMAXELEMENTS 8

//Globals needed for parser
char jsonData[JSONMAXSIZE];
json jsonRefs[JSONMAXELEMENTS]; 
unsigned char jsonRefCount=0;
unsigned char jsonDataCount=0;

//States for json parser
typedef enum {START,BEGIN,SYMSTR,SYMEND,STARTVAL,STRVAL,READBOOL,READNUM,ENDSTRVAL,END} jsonState;

//Read in a single char at a time, run though state machine
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



int i;
void main(void) {


    //char * myJson = "  { \"asdf\" : \"as\",\"blah\":true}";  
    char * myJson = "  { \"IN1\" : \"blah\",\"IN2\": 44.2  , \"IN3\": false,\"IN4\":true }";  

    //Run the statmachine for evey char in array
    jsonState state = START;
    for (i = 0; i < strlen(myJson); i++){
        state = parseJson(myJson[i],state);
        //printf(" State %d\n",state);
    }
    
    //If last state was END it was good;
    if(state == END)
        printf("Json Parsed Clean!\n");
    else
        printf("Json did not parse correctly");


    /*
    //Print data array
    printf("\nData:\n");
    for(i=0;i<jsonDataCount;i++) {
        printf("%c",jsonData[i]);

    }
    printf("\n");
    */

    //Print out parsed json data
    for(i=0;i<jsonRefCount;i++) {
        printf("%s: %c : %s\n",jsonRefs[i].symbol,jsonRefs[i].type,jsonRefs[i].value);

    }




}
