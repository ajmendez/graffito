#!/usr/bin/env python
'''Run some code'''
import sys
import time
import struct
import serial

# HEX bytes for different commands
CMD = {
    'prefix':'3b',
    'space':'',
    'pos':'25',
    'neg': '24',
    'nc':'0d',
}
HOST = {
    'HC':'04',
    'AZ':'10',
    'AT':'11',
    '??':'03',
}
MOVE = {
    'left': ['pos']
}


class Mount(serial.Serial):
    def setup(self):
        a,b = 'pos','neg'
        a,b = b,a
        # print self.run('AZ', a, '09')
        self.run('AT', a, '09')
        time.sleep(1)
        # print self.run('AZ', b, '00')
        self.run('AT', b, '09')
        time.sleep(1)
        self.run('AT', b, '00')
    
    def checksum(self, hcmd):
        items = [int(t,16) for t in hcmd[1:]]
        return hex( (1<<16) - sum(items))[-2:]
    
    def run(self, client, command, data=None):
        hcmd = [CMD['prefix'], HOST['HC'], CMD['nc'],
                HOST[client], CMD[command]]
        if data is not None:
            hcmd.append(data)
        hcmd.append(self.checksum(hcmd))
        
        print '  Run: %s'%(' '.join(hcmd))
        for hc in hcmd:
            self.write(hc.decode('hex'))
        recv = self.get()
        print '   Recv: %s'%(' '.join(recv))
        return recv
    
    def get(self, n=10):
        out = []
        while n > 0:
            tmp = self.read(1)
            if len(tmp) == 0:
                n -= 1
            else:
                out.append(tmp)
            
        return [t.encode('hex') for t in out]
        

def main():
    device = '/dev/tty.usbserial-A100OZXL'
    # device = '/dev/tty.usb'
    baud = 19200
    timeout = 0.1
    with Mount(device, baud, timeout=timeout) as mount:
        mount.setup()
    
    


if __name__ == '__main__':
    main()