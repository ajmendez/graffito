/* Debug communication 
   Mendez May 2014
*/

#include <LiquidCrystal.h>

LiquidCrystal lcd(PIN_B0, PIN_B1, PIN_B2, PIN_B3, PIN_B7, PIN_D0);
HardwareSerial Uart = HardwareSerial();


void showSpinner() {
  /* A simple spinner to ensure that the user is ok */
  int tmp = (millis()/100) % 4;
  lcd.setCursor(19, 0);
  switch (tmp) {
    case 0: 
      lcd.print((char)127);
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




void clearArray(int m[]) {
  for (int i=0; i<7; i++) {
    m[i] = 0;
  }
}

void showArray(String mesg, int m[], int imax) {
  char tmp[2];
  lcd.setCursor(0,0);
  for (int i=0; i<7; i++) {
    sprintf(tmp, "%02X", m[i]);
    lcd.print(tmp);
    lcd.print(' ');
  }
}
void sendCMD(int x[], int imax) {
  // Write a set of bytes to the telescope
  for (int i=0; i<imax; i++) Uart.write(x[i]);
}



int inbyte, outbyte;
int istatus = 0;
int ostatus = 0;
int LAST[] = {0, 0, 0, 0, 0, 0, 0};
int CMD[] = {0, 0, 0, 0, 0, 0, 0};


void communicate() {
  
  lcd.setCursor(0,3);
  while (Uart.available() > 0 ) {
    inbyte = Uart.read();
    lcd.print(inbyte, DEC);
    lcd.print(' ');
  }
  
  lcd.setCursor(0,1);
  while (Serial.available() > 0) {
    outbyte = Serial.read();
    
    lcd.print(outbyte, DEC);
    lcd.print(' ');
    
    // Send to telescope
    Uart.write(outbyte);
  }
}


int stopx[] = {59,4,13,17,37,0,185};
int stopy[] = {59,4,13,16,37,0,184};
void sendStop() {
  for (int i=0; i<7; i++) Uart.write(stopx[i]);
  for (int i=0; i<7; i++) Uart.write(stopy[i]);
}

int btn = HIGH;
void stopButton() {
  // with pullup this is ok to ignore debounce
  btn = digitalRead(PIN_D6);
  if (btn == LOW) {
    sendStop();
    lcd.setCursor(0,0);
    lcd.print("STOP! ");
    delay(100);
    lcd.setCursor(0,0);
    lcd.print("Computer");
    btn = HIGH;
    Uart.clear();
  }
}

int sel = HIGH;
void selButton() {
  // with pullup this is ok[?] to ignore debounce
  sel = digitalRead(PIN_D7);
  if (sel == LOW) {
    lcd.setCursor(0,0);
    lcd.print("OK!");
    delay(100);
    lcd.setCursor(0,0);
    lcd.print("Computer");
    sel = HIGH;
    Uart.clear();
  }
}

void setup() {
  Serial.begin(19200);
  Uart.begin(19200);
  lcd.begin(16, 4);
  lcd.setCursor(0,0);
  lcd.print("Computer:");
  lcd.setCursor(0,2);
  lcd.print("Mount:");
  
  pinMode(PIN_D7, INPUT_PULLUP);
  pinMode(PIN_D6, INPUT_PULLUP);  
}

int value = 0;
void loop() {
  showSpinner();
  communicate();
  stopButton();
  selButton();
}
