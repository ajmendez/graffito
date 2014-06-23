# a telescope 

import os
import sys
import serial


DEVICES = [
    '/dev/tty.usbserial-A100OZXL',
    '/dev/tty.usbmodem12341',
    '/dev/tty.usbmodem1',
]
BAUD = 19200
TIMEOUT = 0.2


class Telescope(serial.Serial):
    '''Celestron Nextstar SLT device controller.'''
    def __init__(self, device=None, baud=BAUD, timeout=TIMEOUT):
        self.device = self.getdevice(device)
        self.baud = baud
        self.timeout = timeout
        super(Telescope, self).__self__(device=self.device, baud=self.baud, timeout=self.timeout)
    
    
    def getdevice(self, device=None):
        '''Find the device from some default items.'''
        if device:
            return device
        else:
            for device in DEVICES:
                if os.path.exists(device):
                    return device
    
    # Some base functions.
    
    def run(self, command):
        '''Run the a command.'''
        if isinstance(command, str):
            self.write(command)
        elif isinstance(command, (list, tuple)):
            for cmd in command:
                self.write(command)
        # 
        raise ValueError('Missing command translator')
    
    
    def translate(self, cmd):
        '''translate a command into the decimal equivalents '''
        
    
    def get(self):
        '''Get the response from command'''
        
    
    def parse(self, response):
        '''Parse the response from the telescope.'''
    
    
    # Higher functions
    
    def version(self):
        '''get the vesion'''
    
    def move(self, axis, rate):
        '''move an axis at some rate'''
        
    def delta(self, axis, rate, time):
        '''move an axis at some rate for some time.'''
    
    def location(self):
        '''Get the current location of the telescope'''
    
    def goto(self, alt=None, az=None, fast=True):
        '''Get the location using fractions of a circle.'''
    
    def cordwrap(self, location):
        '''set the cord wrap position.'''
    
    