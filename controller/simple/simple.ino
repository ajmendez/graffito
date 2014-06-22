/* Debug communication 
   Mendez May 2014
   BROKEN!  gaol: read in data from serial send it out to the serial port
*/

#include <LiquidCrystal.h>

LiquidCrystal lcd(PIN_B0, PIN_B1, PIN_B2, PIN_B3, PIN_B7, PIN_D0);
HardwareSerial Uart = HardwareSerial();

int inbyte;
char outbyte;
String outstr = "";
char sep = ' ';
char newline = '\n';
boolean isdone = false;
boolean ispython = false;


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
    int s = outstr.toInt();
    lcd.setCursor(0, 1);
    lcd.print(s);
    Uart.write((char)s);
    
//    if (s == 59) Serial.println();
//    
//    Serial.print('<');
//    Serial.print(s,DEC);
//    Serial.print('>');
//    Uart.write(int(s));
    outstr = "";
//    if (isdone) {
//      Serial.println();
//      isdone = false;
//    }
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
