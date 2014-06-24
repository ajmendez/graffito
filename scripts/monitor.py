#!/usr/bin/env python
import sys
import serial.tools.miniterm
import time
import fcntl

def main(device, baud, timeout=0.1):
    while True:
        try:
            term = serial.tools.miniterm.main()
            # Miniterm(device, baud)
        except KeyboardInterrupt:
            print 'User is done'
            return
    
    # try:
    #     while True:
    #         s = serial.Serial(device, baud, timeout=timeout)
    #         fcntl.lockf(s,fcntl.LOCK_UN)
    #         
    #         # while True:
    #             # loop over lines
    #         try:
    #             out = s.readline()
    #             if len(out.strip()) == 0:
    #                 continue
    #                 time.sleep(timeout)
    #             else:
    #                 print out
    #         except Exception as e:
    #             print e
    #             
    #                 
    #                     
    # except KeyboardInterrupt as e:
    #     print 'User is done'
    #     return



if __name__ == '__main__':
    print len(sys.argv)
    main(None, None)