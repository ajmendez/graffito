
/* HW Flow Control
 * Mendez 06.2014
 * partially from http://rpgduino.wordpress.com/2010/03/27/vdip1-usb-host-controller/
 */
 
// RX TX
#define HW_RX PIN_D2 // originally 2
#define HW_TX PIN_D3 // Originally 3
#define HW_CTS PIN_B6 // originally 5
#define HW_RTS PIN_B7 // originally 4

//#include 
//#include <NewSoftSerial.h>
//NewSoftSerial usb(HW_RX, HW_TX);
#include <SoftwareSerial.h>
#include <SoftwareSerial.h>
SoftwareSerial usb(HW_RX, HW_TX);

//#define usb 


//int RTSPin = 5;
//int CTSPin = 4;
char usbRx;
byte charIn;


void setup() {
  pinMode(HW_RTS, INPUT);
  pinMode(HW_CTS, OUTPUT);
  
  usb.begin(19200);
  Serial.begin(19200);
  // usb.begin(57600); // You can modify the default speed of the VDIP1 with firmware updates to be up to 57600 through newSoftSerial.
  
  digitalWrite(HW_CTS, LOW); // Set the CTS to low and keep it there.
  Serial.begin(9600);	 // opens serial port, sets data rate to 9600 bps
  Serial.print("Starting");

  usb.print("IPA"); // Set to ascii mode.
  usb.print(13, BYTE);
}


void SendToUsb(char val) {
  while (digitalRead(HW_RTS) == HIGH) { }
  usb.print(val);
  digitalWrite(HW_CTS, LOW);
}

void SendToUsbTermCmd() {
  while (digitalRead(HW_RTS) == HIGH) { }
  usb.print(13, BYTE);
  digitalWrite(HW_CTS, LOW);
}

void loop() {
  // Disable the sending on the USB device if you have filled more than 50% of your buffer (64 bytes by default)
  if (usb.available() > 32) {
    digitalWrite(HW_CTS, HIGH);
  } else {
    digitalWrite(HW_CTS, LOW);
  }
  
  if (usb.available() > 0) { // read the incoming byte
    usbRx = usb.read();
    if (usbRx == 0x0D) {
      Serial.println();
    } else {
      Serial.print(usbRx);
    }
  }
  
  if (Serial.available() > 0) { // read the incoming byte
    if (Serial.read() == (byte)'~') {
      charIn = 0;
      while (charIn != (byte)'~') { // wait for header byte again
        if (Serial.available() > 0) {
          charIn = Serial.read();
          Serial.print(charIn, HEX);
          if (charIn == (byte)'~') {
            Serial.println("breaking");
            break;
          }
          SendToUsb(charIn);
        }
      }
      SendToUsbTermCmd();
    }
  }
}
