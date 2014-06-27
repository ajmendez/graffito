/* Debug communication 
   Mendez May 2014
   Take in data from the serial, and push it out to the telescope
   CMD: 59 4 13 17 36 9 177
   CMD: 59 4 13 17 37 0 185
*/

#include <LiquidCrystal.h>
LiquidCrystal lcd(PIN_B0, PIN_B1, PIN_B2, PIN_B3, PIN_B7, PIN_D0);

#define CTS PIN_F6
#include <SoftwareSerial.h>
SoftwareSerial ser(PIN_F4, PIN_F5); //rx, tx


int inbyte;
int outbyte;
String outstr = "";
int iskip = 59;
int ichar = 0;
boolean raise = false;

void communicate() {
  
  while (digitalRead(CTS) == LOW) {
    lcd.setCursor(0,1);
    lcd.print(millis()/100);
    ser.listen();
    while (ser.available() > 0) {
      outbyte = ser.read();
      Serial.print(outbyte);
//      Serial.print(' ');
    }
//    Serial.println();
    digitalWrite(CTS, HIGH);
  }
  
//  Serial.listen();
  if (Serial.available()) {
    digitalWrite(CTS, LOW);
    raise = true;
  }
  while (Serial.available() > 0) {
    inbyte = Serial.read();
    ser.print(inbyte);
  }
  if (raise) {
    digitalWrite(CTS, HIGH);
//    pinMode(CTS,INPUT);
    raise = false;
  }
}

void ping() {
  while (digitalRead(CTS) == LOW) { }
  digitalWrite(CTS, LOW);
  ser.write('a');
  digitalWrite(CTS, HIGH);
}

void setup() {
  Serial.begin(19200);
  
//  pinMode(CTS, INPUT);
  pinMode(CTS, OUTPUT);
//  pinMode(CTS, INPUT_PULLUP);
  digitalWrite(CTS, HIGH);
  ser.begin(19200);
  lcd.begin(16,4);
}

void loop() {
  communicate();
//  sendMesg();
//  ping();
  lcd.setCursor(0,0);
  lcd.print(millis()/100);
}
