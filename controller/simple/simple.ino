/* Debug communication 
   Mendez May 2014
   Take in data from the serial, and push it out to the telescope
   CMD: 59 4 13 17 36 9 177
   CMD: 59 4 13 17 37 0 185
*/

#include <LiquidCrystal.h>
#define HWSERIAL Serial1 //switch to this

LiquidCrystal lcd(PIN_B0, PIN_B1, PIN_B2, PIN_B3, PIN_B7, PIN_D0);
//HardwareSerial Uart = HardwareSerial();
#define Uart Serial1

int inbyte;
char outbyte;
String outstr = "";
char sep = ' ';
char newline = '\n';
boolean isdone = false;
boolean ispython = true;
int iskip = 59;
int ichar = 0;


void communicate() {
  while (Uart.available() > 0 ) {
    inbyte = Uart.read();
    if (ispython) {
      Serial.print((char)inbyte);
    } else {
      if (inbyte == 59) Serial.println();
      Serial.print(inbyte);
      Serial.print(' ');
    }
  }
  
  while (Serial.available() > 0) {
    outbyte = Serial.read();
//    if (outbyte == newline) isdone = true;
    if ((outbyte == sep)|(outbyte==newline)) break;
    outstr += outbyte;
  }
}



void sendMesg() {
  if (outstr.length() > 0 ) {
    outstr += ' ';
    
    int s = outstr.toInt();
    
    lcd.setCursor(ichar, 1);
    if (s == iskip) ichar = 0;
    ichar += outstr.length();
    lcd.print(s);
    Uart.write((char)s);
    outstr = "";
  }
}


void setup() {
  Serial.begin(19200);
  Uart.begin(19200);
  lcd.begin(16,4);
}

void loop() {
  communicate();
  sendMesg();
  lcd.setCursor(0,0);
  lcd.print(millis()/100);
}
