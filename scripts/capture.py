#!/usr/bin/env python
'''
1 20  GND or CTS
2 2   Data out
3 6,8 +12V
4 3   Data In
5 7   GND
6 23  Drop / +5v
'''
import os
import sys
import time
import serial
from datetime import datetime


DEVICES = ['/dev/tty.usbserial-A100OZXL',
           '/dev/tty.usbmodem12341']

def get_device():
  '''get the device'''
  if len(sys.argv) > 1:
    return sys.argv[1]
  else:
    for device in DEVICES:
      if os.path.exists(device):
        return device

DEVICE = get_device()
BAUD = 19200
TIMEOUT = 0.2

class Trigger(object):
    def __init__(self, delta=1.0):
        self.last = datetime.now()
        self.delta = delta
        
    def trigger(self):
        now = datetime.now()
        trig = ((now-self.last).total_seconds() > self.delta)
        if trig:
            self.last = now
        return trig


CONTROLLERS = {
    13:'mc',
    16:'at',
    17:'az',
}

COMMANDS = {
    1:   'location',
    36:  'move neg',
    37:  'move pos',
    254: 'version',
}

TEMPLATE = '''    {tx} > {rx} : {len} : {command} [{data}]'''

def get_location(arr):
    # return arr[0]/256.0*360 + arr[1]/256.0*60 + arr[2]/256.0*60
    return sum([(256*i - x)/(256.0*i) for i,x in enumerate(arr,1)])


def get_data(command, cmd):
    if command == 'version':
        if len(cmd) == 8:
            return cmd[5] + cmd[6]/100.
        else:
            return 'request'
    
    elif 'move' in command:
        return cmd[5]
    
    elif command == 'location':
        if len(cmd) == 9:
            return get_location(cmd[5:7])
        else:
            return 'request'
    
        
        

def parse(cmd):
    if len(cmd) < 5: return
    command = COMMANDS.get(cmd[4], cmd[4])
    items = {
        'tx': CONTROLLERS.get(cmd[2], cmd[2]),
        'rx': CONTROLLERS.get(cmd[3], cmd[3]),
        'len': cmd[2]-1,
        'command': command,
        'data': get_data(command, cmd)
    }
    return TEMPLATE.format(**items)

def main(device=DEVICE, baud=BAUD, timeout=TIMEOUT):
    trig = Trigger()
    cmd = []
    tmp = 0
    
    with serial.Serial(device, baud, timeout=timeout) as s:
        try:
            while True:
                char = s.read()
                
                if len(char) > 0:
                    # tmp = ch.encode('hex')
                    tmp = ord(char)
                
                hasdata = ( len(cmd) > 0 )
                newcommand = ( (tmp == 59) or (tmp == '3b') )
                trigger = ( trig.trigger() )
                
                
                if hasdata and (newcommand or trigger):
                    print cmd
                    try:
                        print parse(cmd)
                    except Exception as e:
                        print 'Failed to parse: ', e
                        raise
                        
                    
                    cmd = []
                
                if len(char)> 0:
                    cmd.append(tmp)
                
                
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
    from pysurvey import util
    util.setup_stop()
    
    main()
    # if 'test' in sys.argv[1:]:
    #     test()
    # if 'talk' in sys.argv[1:]:
    #     talk()
    # else:
    #     main()