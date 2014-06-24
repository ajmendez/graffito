# a telescope 

import os
import sys
import serial
from pprint import pprint


DEVICES = [
    '/dev/tty.usbserial-A100OZXL',
    '/dev/tty.usbmodem12341',
    '/dev/tty.usbmodem1',
    '/dev/tty.Bluetooth-Serial-1',
]
BAUD = 19200
TIMEOUT = 0.2

TEMP = True

# bytes of interest
PREFIX = 59

HOSTS = {
    13: ['mc', 'controller'],
    16: ['at', 'altitude'],
    17: ['az', 'azimuth'],
}
rsHOSTS = {v[0]:k for k,v in HOSTS.iteritems()}
rHOSTS  = {v[1]:k for k,v in HOSTS.iteritems()}
sHOSTS  = {k:v[0] for k,v in HOSTS.iteritems()}
HOSTS   = {k:v[1] for k,v in HOSTS.iteritems()}




COMMANDS = {
    1:   'location',
    2:   'goto_fast',
    3:   'set_pos',        # Different
    5:   'get_unknown',    # Unknown
    4:   'set_loc',        # Unknown
    6:   'pos_guiderate',  
    7:   'neg_guiderate',
    19:  'isslew',
    23:  'goto_slow',
    36:  'neg_move',
    37:  'pos_move',
    56:  'cordwrap',
    58:  'cordwrap_pos',
    252: 'approach',
    254: 'version',
}
rCOMMANDS = {v:k for k,v in COMMANDS.iteritems()}




class Telescope(serial.Serial):
    '''Celestron Nextstar SLT device controller.'''
    def __init__(self, device=None, baud=BAUD, timeout=TIMEOUT, **kwargs):
        device = self.getdevice(device)
        # self._baud = baud
        # self._timeout = timeout
        # use .port, .baudrate, .timeout
        super(Telescope, self).__init__(port=device,
                                        baudrate=baud,
                                        timeout=timeout, **kwargs)
    
    def okdevice(self, device):
        '''Check that the device is there.
        TODO: should check that it is openable.'''
        return os.path.exists(device)
        
    def getdevice(self, device=None):
        '''Find the device from some default items.'''
        if device:
            if self.okdevice(device):
                return device
        else:
            for device in DEVICES:
                if self.okdevice(device):
                    return device
        raise IOError('Missing device: {}'.format(device))
    
    #
    # reading response commands
    #
    
    def getdata(self, cmd):
        '''Grab the data payload from the packet. If no data, return None'''
        try:
            n = cmd[1] - 3 # ignore the sender / receiver
            return cmd[5:5+n]
        except:
            return None
    
    def okchecksum(self, cmd):
        '''ok the packet checksum'''
        try:
            n = 2+cmd[1] # add in the prefix and length to the chars.
            return cmd[-1] == self.checksum(cmd[:n])
        except Exception as e:
            print 'Failed to get checksum: {}'.format(e)
            return False
    
    def parse(self, cmd):
        '''Parse the response from the telescope.'''
        output = dict(
            sender   = HOSTS.get(cmd[2], cmd[2]),
            receiver = HOSTS.get(cmd[3], cmd[3]),
            command  = COMMANDS.get(cmd[4], str(cmd[4])),
            data     = self.getdata(cmd),
            cmd      = cmd,
        )
        return output
    
    def parsevalue(self, data):
        '''Parse the data as a series of bits'''
        value = sum([x<<(8*i) for i,x in enumerate(reversed(data))])
        return value / float(1<<(8*len(data)))
    
    def parsedegrees(self, angle, bits=24):
        '''Convert the fraction on a circle into a 24bit array.
        TODO: handle angles > 360 -- modulo?
        TODO: handle angles very close to 360 -- this may not be a problem'''
        if (angle > 360) or ((angle-360) > 0.0001):
            raise ValueError('you should figure out how to "float" correctly')
        value = int(angle/360.0 * float(1<<24))
        return [((value & (0xFF << i)) >> i) for i in reversed(range(0,24,8))]
    
    def get(self):
        '''Get the response from command'''
        cmd = []
        while self.inWaiting():
            char = self.read()
            if len(char) > 0:
                cmd.append(ord(char))
        
        if len(cmd) > 0:
            if TEMP:
                cmd = map(int, (''.join(chr(c) for c in cmd)).strip().split(' '))
            assert self.okchecksum(cmd)
            return self.parse(cmd)
    
    def nicevalue(self, output):
        '''Adjust the output into a set of nice values'''
        if (output['command'] == 'location') and output['data']:
            output['data'] = 'L{:0.6f}'.format(output['data'])
        return output
    
    def niceprint(self, output, showcmd=False):
        '''parse the output into a nice string'''
        output = self.nicevalue(output)
        outstring = '{sender:>10s}>{receiver:<10s} {command:>15s} : {data}'.format(**output)
        if showcmd:
            outstring = '{main:60s} | {cmd}'.format(main=outstring, **output)
        return outstring
    
    #
    # running command functions
    #
    
    def packetlength(self, cmd):
        '''Get the packet length (cmd does not include chksum)'''
        return len(cmd)-2
    
    def checksum(self, cmd):
        '''Get the packet checksum'''
        return (((1<<16) - sum(cmd[1:])) & 0xFF)
    
    def craftvalue(self, command, data=None):
        '''handles special values within the command package'''
        if command == 'move':
            if data is not None:
                command = 'pos_move' if (data[0] > 0) else 'neg_move'
                data[0] = abs(data[0])
        
        cmd = rCOMMANDS.get(command, command)
        if data is None:
            data = []
        
        return cmd, data
    
    def craft(self, axis, command, data=None):
        '''Craft a byte list from a command and data.  data is a list'''
        axis = rHOSTS.get(axis, rsHOSTS.get(axis, axis))
        command, data = self.craftvalue(command, data)
        cmd = [
            PREFIX,               # binary prefix for packet
            0,                    # length of packet
            rHOSTS['controller'], # who is sending the packet
            axis,                 # which axis to talk to
            command,              # the command
        ]
        cmd.extend(data)                # add data if needed
        cmd[1] = self.packetlength(cmd) # update the length of the packet
        cmd.append(self.checksum(cmd))  # add acket checksum
        return cmd
    
    def _run(self, cmd):
        '''Internal packet run'''
        if TEMP:
            self.write(' '.join(['%d'%c for c in cmd]))
        else:
            for c in cmd:
                self.write(chr(c))
        return self.get()
    
    def run(self, axis, command, data=None):
        '''Run the a command.'''
        cmd = self.craft(axis, command, data)
        return self._run(cmd)
    
    #
    # Higher functions
    #
    
    def version(self):
        '''get the version'''
        return dict(altitude = self.run('altitude', 'version'),
                    azimuth  = self.run('azimuth', 'version'))
        
        
    def move(self, axis, direction, rate):
        '''move an axis at some rate.
        axis = 'altitude' or 'azimuth'
        direction = 'pos' or 'neg'
        rate = 0 - 9
        '''
        command = '{}_move'.format(direction)
        return self.run(axis, command, rate)
        
        
    def delta(self, axis, direction, rate, time):
        '''move an axis at some rate for some time.
        make a move for a specific time.
        '''
        self.move(axis, direction, rate)
        time.sleep(time)
        self.move(axis, direction, 0)
        
        
    def location(self):
        '''Get the current location of the telescope'''
        output = self.run('location')
        return self.parsevalue(output['data'])
        
        
    def goto(self, altitude=None, azimuth=None, fast=True):
        '''Get the location using fractions of a circle.'''
        command = 'goto_fast' if fast else 'goto_slow'
        if altitude:
            self.run('altitude', command, altitude)
        if azimuth:
            self.run('azimuth', command, azimuth)
    
    
    def blocking_goto(self, *args, **kwargs):
        '''Block while we slew'''
        self.goto(*args, **kwargs)
        while self.isslew():
            # sleweing
            time.sleep(0.1)
    
    
    def isslew(self):
        output = self.run('slew')
        return output['data'] != 0xFF
    
    
    def cordwrap(self, location):
        '''set the cord wrap position.'''
        for ax in ['at', 'az']:
            self.run(ax, 'cordwrap')
            self.run(ax, 'cordwrap_pos', self.parsefraction(location))
    