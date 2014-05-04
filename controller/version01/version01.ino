/* Telescope Controller Version 01
Mendez Apr 2014
*/


#include <stdio.h>
// include the library code:
#include <LiquidCrystal.h>

int jx,jy, sx,sy;
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

void telescopeStatus() {
  /* Read and Parse any status received from the telescope.
  */
  if (Uart.available() > 0) {
//    if ( (millis()-last) > 500 ) Serial.println("");
//    last = millis();
    
    inbyte = Uart.read();
    if (inbyte == 59) {
      if (istatus > 0) {
        printArray("Status: ", STATUS);
      }
      clearArray(STATUS);
      istatus = 0;
    }
    STATUS[istatus] = inbyte;
    istatus++;
    
    if (istatus == 8) parseStatus();
    
//    Serial.print(inbyte);
//    Serial.print(' ');
//    lcd.setCursor(0,3);
//    lcd.print(inbyte);
//    lcd.print('.');
  }
}


String parseArgs(int imax) {
  String out;
  char tmp[2];
  for (int i=0; i<imax+1; i++) {
    sprintf(tmp, "%d", STATUS[4+i]);
    out += tmp;
  }
  return out;
}

String  parseUnknown(int s) {
  char out[3];
  sprintf(out,"? [%03d]", s);
  return (String)out;
}

String parseCommand() {
  String out = "";
  int s = STATUS[2]; 
  switch (s) {
    case POS:
      out = "Move +" + parseArgs(1);
      break;
    case NEG:
      out = "Move -" + parseArgs(1);
      break;
    default:
      out = parseUnknown(STATUS[2]);
      break;
  }
  return out;
}

String parseMotor() {
  String out = "";
  int s = STATUS[3];
  switch (s) {
    case DIRX: 
      out = "X";
      break;
    case DIRY: 
      out = "Y"; 
      break;
    default:
      out = parseUnknown(STATUS[3]);
      break;
  }
  return out;
}

void parseStatus() {
  // Parse the status
  String out = "";
  out += parseCommand();
  out += parseMotor();
}






void sendMove(int x[]) {
  // Write a set of bytes to the telescope
  for (int i=0; i<8; i++) Uart.write(x[i]);
}



int getSpeed(int j) {
  /* Takes the joystick value between [0,1024] and convert it into a speed
     Using 514 as the center since that seems to be how this joystick is centered
     Probably due to the reference voltage.  56 roughly divides up the space equally. */
  return constrain((j-514)/56, -9, 9);
}



void clearArray(int m[]) {
  for (int i=0; i<7; i++) {
    m[i] = 0;
  }
}

void printArray(String mesg, int m[]) {
  /* Write a command array to the lcd screen
  */
  Serial.print(mesg);
  
  char tmp[2];
  lcd.setCursor(2,4);
  Serial.println();
  for (int i=0; i<7; i++) {
    sprintf(tmp, "%02X", m[i]);
    Serial.print(m[i]);
    Serial.print(' ');
    lcd.print(tmp);
  }
  Serial.println();
}


int checksum(int m[]) {
  // Serial checksum
  int t = 0;
  for (int i=1; i<6; i++) t += m[i];
  return lowByte(~t+1);
}

void sendSpeed(int dir, int spd) {
  /* Parse speed variable and tell the telescope
      dir -- DIRX/DIRY -- direction
      spd -- (-9)-(9) speed int
  */
  MOVE[3] = dir;
  MOVE[4] = spd > 0 ? POS : NEG;
  MOVE[5] = abs(spd);
  MOVE[6] = checksum(MOVE);
  
  printArray("Move: ", MOVE);
  sendMove(MOVE);
}




void speedDir(int dir, int* spd, int joy) {
  /* Setup the speed for a direction
      dir -- either DIRX/DIRY
      spd -- pointer to the speed variable for this direction
      joy -- the value of the joystick
  */
  int newspd = getSpeed(joy);
  int offset = (dir == DIRX) ? 0 : 6;
  char cdir = (dir == DIRX) ? 'x' : 'y';
  
  if ( *spd != newspd ) {
    lcd.setCursor(offset,2);
    lcd.print(cdir);
    lcd.print(":    ");
    lcd.setCursor(offset+2,2);
    lcd.print(newspd);
    sendSpeed(dir, newspd);
    *spd = newspd;
  }
}

void telescopeSpeed() {
  // Read the Joystick and set the telescope in motion
  jx = analogRead(PIN_F0);
  jy = analogRead(PIN_F1);  
  speedDir(DIRX, &sx, jx);
  speedDir(DIRY, &sy, jy);
}




void setup() {
  Serial.begin(19200);
  Uart.begin(19200);
  lcd.begin(16, 4);
}



void loop() {
  showSpinner();
  
//  telescopeStatus();
  telescopeSpeed();
  
//  lcdWrite();
}

