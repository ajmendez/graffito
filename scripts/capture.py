#!/usr/bin/env python

import serial


def main():
    device = '/dev/tty.usbserial-A100OZXL'
    baud = 19200
    # parity = False
    # stop = 1 bit
    # hardware flow 
    with serial.Serial(device, baud, timeout=0.2) as s:
        try:
            while True:
                ch = s.read()
                if len(ch) == 0:
                    continue
                tmp = ch.encode('hex')
                if tmp == '3b':
                    print
                print tmp,
                
                # print '[{}]'.format(ord(out))
                # print 'b:{} h:{} [{}]'.format(bin(out), hex(out), out)
        except KeyboardInterrupt as e:
            print 'User quit'
        except Exception as e:
            print 'Failure!', e
            raise
    print 'Bye!'
    
if __name__ == '__main__':
    main()