#!/usr/bin/env python
'''
1 20  GND or CTS
2 2   Data out
3 6,8 +12V
4 3   Data In
5 7   GND
6 23  Drop / +5v
'''
import sys
import time
import serial




def main():
    # device = '/dev/tty.usbserial-A100OZXL'
    device = '/dev/tty.usbmodem12341'
    baud = 19200
    # parity = False
    # stop = 1 bit
    # hardware flow 
    with serial.Serial(device, baud, timeout=0.2, rtscts=0) as s:
        try:
            x = []
            while True:
                ch = s.read()
                if len(ch) == 0: continue
                tmp = ch.encode('hex')
                
                
                if tmp == '3b':
                    print x
                    x = []
                x.append(tmp)
                # if tmp == '3b':
                #     print
                # print tmp,
                
                # print '[{}]'.format(ord(out))
                # print 'b:{} h:{} [{}]'.format(bin(out), hex(out), out)
        except KeyboardInterrupt as e:
            print 'User quit'
        except Exception as e:
            print 'Failure!', e
            raise
    print 'Bye!'






# def test():
#     UP = ['3b', '04', '0d', '11', '24', '07', 'b1']
#     URETURN = ['3b', '0d', '04', '11', '24', '09', 'b1']
#     STOP = ['3b', '04', '0d', '11', '24', '00', 'ba']
#     SRETURN = ['3b', '0d', '04', '11', '24', '00', 'ba']
#            
#     
#     device = '/dev/tty.usbserial-A100OZXL'
#     device = '/dev/tty.usbmodem12341'
#     baud = 19200
#     with serial.Serial(device, baud, 
#                        timeout=0.1, 
#                        parity=serial.PARITY_NONE,
#                        dsrdtr=0, rtscts=0) as s:
#         for x in UP:
#             s.write((x.decode('hex')))
#         
#         print s.read(8).encode('hex')
#         # for x in ['3b', '04', '0d', '10', '24', '01', 'ba']:
#         #     s.write((x.decode('hex')))
#         
#         time.sleep(2)
#         
#         for x in STOP:
#             s.write((x.decode('hex')))
#         
#         print s.read(8).encode('hex')
        

if __name__ == '__main__':
    main()
    # if 'test' in sys.argv[1:]:
    #     test()
    # if 'talk' in sys.argv[1:]:
    #     talk()
    # else:
    #     main()