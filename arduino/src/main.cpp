#include <Arduino.h>
#include <LiquidCrystal.h>


const int rs = 7, en = 8, d4 = 9, d5 = 10, d6 = 11, d7 = 12;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);


const byte buffSize = 40;
char inputBuffer[buffSize];
const char startMarker = '<';
const char endMarker = '>';
byte bytesRecvd = 0;
boolean readInProgress = false;
boolean newDataFromPC = false;
char messageFromPC[buffSize] = {0};
unsigned long curMillis;
unsigned long prevReplyToPCmillis = 0;
unsigned long replyToPCinterval = 1000;
//char* storedMessagesFromPC[20];
uint8_t counterMessage = 0;
//uint8_t counterStoredMessage = 0;
uint8_t counterDestination = 0;
uint8_t counterHour = 0;
//char* formattedStoredMessages[2][1];
char formattedHour[15][15];
char formattedDestination[15][15];
uint8_t i;

boolean transmissionDone = false;
int tailleTableaux = 0;

//=============
 
void parseData() {

    // split the data into its parts
    
  char * strtokIndx; // this is used by strtok() as an index
  
  strtokIndx = strtok(inputBuffer,",");     // get the first part - the string
  strcpy(messageFromPC, strtokIndx);        // copy it to messageFromPC
  
  // discriminate data whether it's letters, digits or END message
  if (messageFromPC[0] != '\0') {
      
      
    if (strcmp(messageFromPC, "END") == 0) {
        transmissionDone = true;
    }
    else  {
      char premierCaractere = messageFromPC[0];
      
      if (isUpperCase(premierCaractere)) {
        strcpy(formattedDestination[counterDestination], messageFromPC);
        counterDestination++;
      } 
      else if (isdigit(premierCaractere)) {
        strcpy(formattedHour[counterHour], messageFromPC);
        counterHour++;
      }
    }
  }
}

  

//=============

void getDataFromPC() {

    // receive data from PC and save it into inputBuffer
    
  if(Serial.available() > 0) {

    char x = Serial.read();

      // the order of these IF clauses is significant
      
    if (x == endMarker) {
      readInProgress = false;
      newDataFromPC = true;
      inputBuffer[bytesRecvd] = 0;
      parseData();
    }
    
    if(readInProgress) {
      inputBuffer[bytesRecvd] = x;
      bytesRecvd ++;
      if (bytesRecvd == buffSize) {
        bytesRecvd = buffSize - 1;
      }
    }

    if (x == startMarker) { 
      bytesRecvd = 0; 
      readInProgress = true;
    }
  }
}


//=============

void showParsedDataSerial() {
    
    if (newDataFromPC) {

        newDataFromPC = false;
        Serial.print("<Tableau des destinations : ");
        Serial.println(formattedDestination[counterMessage]);
        Serial.print("Tableau des heures : ");
        Serial.println(formattedHour[counterMessage]);
        Serial.print("Tableau des destinations -1: ");
        Serial.println(formattedDestination[counterMessage-1]);
        Serial.print("Tableau des heures -1: ");
        Serial.println(formattedHour[counterMessage-1]);
        Serial.print("messageFromPC: ");
        Serial.println(messageFromPC);
        Serial.print("tailleTableaux Hour : ");
        Serial.println(counterHour); 
        Serial.print("tailleTableaux Destination : ");
        Serial.println(counterDestination); 
        //Serial.print(">");
        Serial.print(" Time : ");
        Serial.print(curMillis >> 9); // divide by 512 is approx = half-seconds      
        Serial.println(">");
        
        counterMessage++;

        }
}

void displayHappyMessage() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.write("Job done !");
  lcd.setCursor(0, 1);
  lcd.write("        (^v^)/");
  delay(1500);
  lcd.setCursor(0, 0);
  lcd.write("Sleep time.");
  lcd.setCursor(0, 1);
  lcd.write("        (-.-) ");
  uint8_t j;
  for(j=0; j<8;j++) {
    delay(800);
    lcd.setCursor(10, 0);
    lcd.write(". Z z");
    lcd.setCursor(10, 1);
    lcd.write("_");
    delay(800);
    lcd.setCursor(10, 0);
    lcd.write(". z Z");
    lcd.setCursor(10, 1);
    lcd.write(".");
  }
}

void displayLCD() {

  // Displaying tramway data   
  for(i=0; i<=counterHour; i++) {  
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.write(formattedHour[i]);
    lcd.setCursor(0, 1);
    lcd.write(formattedDestination[i]);
    delay(1200);

    // Displaying happy message at the end
    if (i == counterHour) {
      displayHappyMessage();
    }
  }

  transmissionDone = false;
}

//=============

void setup() {
  Serial.begin(9600);
  lcd.begin(16, 2);
  lcd.write("  Waiting for  ");
  lcd.setCursor(0,1);
  lcd.write("      data");

  // tell the PC we are ready
  Serial.println("<Arduino is ready>");
}

//=============

void loop() {
  
  curMillis = millis();
  getDataFromPC();
  showParsedDataSerial();
  
   if (transmissionDone == true) {
     displayLCD();
   }
 
  
}