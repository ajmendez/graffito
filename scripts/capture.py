#!/usr/bin/env python
# capture.py -- captures data from usb serial port.
#  $ capture.py [device]
# 06.2014: Mendez

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
  '''get the device assumes that items higher up on the list are more 
  important.'''
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
    '''Trigger item fires when delta [seconds] have past'''
    def __init__(self, delta=1.0):
        ''''''
        self.last = datetime.now()
        self.delta = delta
        
    def trigger(self):
        now = datetime.now()
        trig = ((now-self.last).total_seconds() > self.delta)
        if trig:
            self.last = now
        return trig


# Names of the different microcontrollers that are called.
CONTROLLERS = {
    13:'mc',
    16:'at',
    17:'az',
}


# Dec values and names of the different commands that are relevant.
COMMANDS = {
    1:   'location',
    2:   'goto_fast',
    3:   'set_pos',        # Different
    5:   'get_unknown',    # Unknown
    4:   'set_loc?',       # Unknown
    6:   'pos_guiderate',  
    7:   'neg_guiderate',
    19:  'isslew',
    23:  'goto_slow',
    36:  'move neg',
    37:  'move pos',
    56:  'enable_cordwrap',
    58:  'set_cordwrap_pos',
    252: 'get_approach',
    254: 'version',
}



def get_value(arr):
    '''Parse the 24bit values into a float.  
    TODO: check sign '''
    value = sum([x<<(8*i) for i,x in enumerate(reversed(arr))])
    return value/float(1<<24)
    
def get_location(arr):
    '''Return the location as a fraction of a circle.
    TODO: check the value in the alt vs az -- might be 180 vs 360.'''
    return 'L{:0.2f}'.format(get_value(arr)*360.0)

def get_guiderate(arr):
    '''Return the 24bit guide rate as a decimal'''
    return '{:0.4f}'.format(get_value(arr))

def get_data(command, cmd):
    '''parse the data from the command.
    TODO: massive clean up!  
    TODO: use the length of bits passed back
    TODO: parse depending on what is talking to what.
    '''
    if isinstance(command, int):
        return
    ncmd = len(cmd)
    
    if command == 'version':
        if len(cmd) == 8:
            return cmd[5] + cmd[6]/100.
        else:
            return 'request'
    
    elif 'move' in command:
        # if len(cmd) == 6:
        return cmd[5]
    
    elif 'goto' in command:
        if ncmd == 9:
            return get_location(cmd[5:7])
        elif ncmd == 7:
            return 'OK' if cmd[5] else 'Failed?'
    
    
    elif command == 'location':
        if len(cmd) == 9:
            return get_location(cmd[5:7])
        else:
            return 'request'
    
    elif command == 'get_approach':
        if len(cmd) == 7:
            return 'pos' if cmd[5] == 0 else 'neg'
        else:
            return 'request'
    
    elif 'guiderate' in command:
        if len(cmd)== 9:
            return get_guiderate(cmd[5:7])
        else:
            return 'request'
    
    elif command == 'isslew':
        if len(cmd) == 7:
            return 'done' if cmd[5] == 255 else 'slewing...'
        else:
            return 'request'
    
    elif 'set_loc' in command:
        if len(cmd) == 9:
            return get_location(cmd[5:7])
        elif len(cmd) == 7:
            return cmd[5]
        else:
            return 'request'
    
    elif command == 'get_unknown':
        if len(cmd) == 8:
            return cmd[5:7]
        else:
            return 'request'
    
    elif command == 'enable_cordwrap':
        if ncmd == 7:
            return cmd[5]
        else:
            return 'request'
    
    elif command == 'set_cordwrap_pos':
        if ncmd == 9:
            return get_location(cmd[5:7])
        elif ncmd == 7:
            return cmd[5]
    
    
    
    
    return ''


TEMPLATE = '''    {tx} > {rx} : {len}.{ncmd} : {command} {data} | {cmd}'''
SHORT_TEMPLATE = '''    {tx} > {rx} : {len}.{ncmd} : {command:15s} {data}'''

def parse(cmd):
    '''Parse a byte array of from the hand paddle.'''
    if len(cmd) < 5: return cmd
    ncmd = len(cmd)
    command = COMMANDS.get(cmd[4], cmd[4])
    data = get_data(command, cmd)
    items = {
        'tx': CONTROLLERS.get(cmd[2], cmd[2]),
        'rx': CONTROLLERS.get(cmd[3], cmd[3]),
        'len': cmd[1]-1,
        'command': command,
        'data': data,
        'ncmd': ncmd,
        'cmd': cmd[5:-1] if len(cmd) > 3 else cmd,
    }
    template = TEMPLATE if (data is None or data == '') else SHORT_TEMPLATE
    
    return '{:60s} | {}'.format(template.format(**items), cmd)



def main(device=DEVICE, baud=BAUD, timeout=TIMEOUT):
    '''Listen to the device and attempt to write out some nice data 
    on what the command did.'''
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
                trigger = ( trig.trigger() and False )
                
                
                if hasdata and (newcommand or trigger):
                    # print cmd
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


if __name__ == '__main__':
    from pysurvey import util
    util.setup_stop()
    
    main()