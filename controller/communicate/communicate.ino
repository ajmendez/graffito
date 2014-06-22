/* Telescope Controller Version 01
Mendez Apr 2014
Read the values coming out of the telescope
*/


#include <stdio.h>
#include <LiquidCrystal.h>

String time;
int inbyte;
unsigned long last;

const int DIRX = 16;
const int DIRY = 17;
const int POS = 37;
const int NEG = 36;
int MOVE[] = {59, 4, 13, 0, 0, 0, 0};

int istatus = 0;
int STATUS[] = {0, 0, 0, 0, 0, 0, 0};

int START[] = {};

byte SLASH[8] = {B0,16,8,4,2,1,B0}; // it is not clear why i need to specify B0 rather than 0


// initialize the library with the numbers of the interface pins
//LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
LiquidCrystal lcd(PIN_B0, PIN_B1, PIN_B2, PIN_B3, PIN_B7, PIN_D0);

// Lets grab a serial device to talk to the telescope
// This is connected to PIN_D2,PIN_D3 -- RX/TX
HardwareSerial Uart = HardwareSerial();



void showSpinner() {
  /* A simple spinner to ensure that the user is ok */
  int tmp = (millis()/100) % 4;
  lcd.setCursor(19, 0);
  switch (tmp) {
    case 0: 
      lcd.write((byte)0); // custom slash char.
      break;
    case 1: 
      lcd.print('|');
      break;
    case 2:
      lcd.print('/');
      break;
    case 3:
      lcd.print('-');
      break;
  }
}



void telescopeStatus() {
  /* Read and Parse any status received from the telescope.*/
  if (Uart.available() > 0) {
    inbyte = Uart.read();
    if (inbyte == 59) {
      if (istatus > 0) {
        printStatus();
      }
    }
    STATUS[istatus] = inbyte;
    istatus++;
  }
}

String printMC(int i) {
  switch (i) {
    case 13: return "MC";
    case 16: return "AT";
    case 17: return "AZ";
  }
}

char tmp[2];
void printStatus() {
  /* Write a command array to the lcd screen */
  
  lcd.setCursor(0,4);
  Serial.println();
  for (int i=0; i<istatus; i++) {
    sprintf(tmp, "%02X", STATUS[i]);
    Serial.print(STATUS[i]);
    Serial.print(' ');
    switch (i) {
      case 0:
        break;
      case 2:
        lcd.print(printMC(STATUS[i]));
        lcd.print('>');
        break;
      case 3:
        lcd.print(printMC(STATUS[i]));
        lcd.print(' ');
        break;
      default:
        lcd.print(STATUS[i]);
        lcd.print(' ');
        break;
    }
    STATUS[i] = 0;
  }
  Serial.println();
  istatus = 0;
}




void setup() {
  Serial.begin(19200);
  Uart.begin(19200);
  lcd.createChar(0, SLASH);
  lcd.begin(16, 4);
  
}

void loop() {
  showSpinner();
  telescopeStatus();
//  lcdWrite();
}

