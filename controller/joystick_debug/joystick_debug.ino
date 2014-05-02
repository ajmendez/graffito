/* JoyStick Debug
Mendez Apr 2014

*/


// include the library code:
#include <LiquidCrystal.h>

int jx,jy, sx,sy;
String time;
int inbyte;
long last;

int DIRX = 16;
int DIRY = 17;
int POS = 37;
int NEG = 36;
int MOVE[] = {59, 4, 13, 0, 0, 0, 0};



int  move_left[7] = {59, 4, 13, 16, 37, 9, 177};
int  move_lend[7] = {59, 4, 13, 16, 36, 0, 187};
int move_right[7] = {59, 4, 13, 16, 36, 9, 178};
int  move_rend[7] = {59, 4, 13, 16, 36, 0, 187};

int   move_up[7] = {59, 4, 13, 17, 36, 9, 177};
int move_uend[7] = {59, 4, 13, 17, 36, 0, 186};
int move_down[7] = {59, 4, 13, 17, 37, 9, 176};
int move_dend[7] = {59, 4, 13, 17, 36, 0, 186};


// initialize the library with the numbers of the interface pins
//LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
LiquidCrystal lcd(PIN_B0, PIN_B1, PIN_B2, PIN_B3, PIN_B7, PIN_D0);

// Lets grab a serial device
HardwareSerial Uart = HardwareSerial();


void setup() {
  Serial.begin(19200);
  Uart.begin(19200);
  lcd.begin(16, 4);
}

void serialWrite() {
//  if (Serial.available() > 0) {
    Serial.print("X = ");
    Serial.print(jx);
    Serial.print(", Y = ");
    Serial.println(jy);
//  }

//  if (Uart.available() > 0) {
//    val = analogRead(0);
//    Serial.println(val);
//    Uart.println(val);
//  }  
}

void lcdWrite() {
  lcd.setCursor(0,0);
  lcd.print("[000.000,000.000]");
  
  lcd.setCursor(20-time.length(), 0);
  lcd.print(time);
  lcd.setCursor(0, 1);
  lcd.print("X:");
  lcd.print(jx);
  lcd.print(" Y:");
  lcd.print(jy);
  lcd.print("        ");
}

void hwSerialRead() {
  if (Uart.available() > 0) {
    if ( (millis()-last) > 500 ) Serial.println("");
    last = millis();
    
    inbyte = Uart.read();
    if (inbyte == 59) {
      Serial.println();
      lcd.setCursor(0,2);
    }
    
    Serial.print(inbyte, DEC);
    Serial.print(' ');
    lcd.print(inbyte,HEX);
    lcd.print(' ');
    
    
//    Serial.print("uart: ");
//    Serial.print(inbyte, HEX);
//    Serial.print(" [");
//    Serial.print(inbyte);
//    Serial.println("]");
  }
}

void sendMove(int x[]) {
  for (int i=0; i<8; i++) {
    Uart.write(x[i]);
    Serial.print(x[i], HEX);
//    Serial.print(i);
//    Serial.print(' ');
  }
}



int getSpeed(int j) {
  // 515 seems to be the actual middle -- depends on the reference voltage
  // 56 roughly divids
  int s = (j-515)/56;
  if (s < -9) s = -9;
  if (s > 9) s = 9;
  return s;
}

int checksum(int m[]) {
  int t = 0;
  for (int i=1; i<7; i++) {
    t += m[i];
  }
  return lowByte(~t);
}

void printArray(int m[]) {
  lcd.setCursor(1,4);
  Serial.println();
  for (int i=1; i<8; i++) {
    Serial.print(m[i]);
    Serial.print(' ');
    lcd.print(m[i],HEX);
    lcd.print(' ');
  }
  Serial.println();
}


void sendSpeed(int dir, int spd) {
  /* 3=axis   
     4=pos/neg
     5=sped
     6 = chksum
  */
  MOVE[3] = dir;
  MOVE[4] = spd > 0 ? POS : NEG;
  MOVE[5] = abs(spd);
  MOVE[6] = checksum(MOVE);
  printArray(MOVE);
}


void speedTelescope() {
  int tx = getSpeed(jx);
  int ty = getSpeed(jy);
  if (sx != tx) {
    sendSpeed(DIRX, tx);
    sx = tx;
  }
  if (sy != ty) {
    sendSpeed(DIRY, ty);
    sy = ty;
  }
}
  


void moveTelescope() {
  if (jx < 400) {
    Serial.println();
    Serial.print("left");
    sendMove(move_left);
    delay(1000);
    sendMove(move_lend);
  }
  if (jx > 600) {
    Serial.println();
    Serial.print("right");
    sendMove(move_right);
    delay(1000);
    sendMove(move_rend);
  }
  if (jy < 400) {
    Serial.println();
    Serial.print("down");
    sendMove(move_down);
    delay(1000);
    sendMove(move_dend);
  }
  if (jy > 600) {
    Serial.println();
    Serial.print("up");
    sendMove(move_up);
    delay(1000);
    sendMove(move_uend);
  }
}

void loop() {
  jx = analogRead(PIN_F0);
  jy = analogRead(PIN_F1);
  time = String(millis()/1000);
  
  hwSerialRead();
  moveTelescope();
  speedTelescope();
  
  // serialWrite();
  lcdWrite();
//  delay(100);
}

