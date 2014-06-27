#!/usr/bin/env python
'''Run some code'''
import sys
import time
import struct
import serial

            # write(s, [59, 4, 13, 17, 36, 9, 177])
            # time.sleep(0.5)
            # write(s, [59, 4, 13, 17, 37, 9, 176])
            # time.sleep(0.5)
            # write(s, [59, 4, 13, 17, 37, 0, 185])
            

# 59 4 13 17 36 9 177 
# 59 4 13 17 37 0 185

# HEX bytes for different commands
CMD = {
    'prefix':'3b',
    'space':'',
    'pos':'25',
    'neg': '24',
    'nc':'0d',
    'ver':'fe',
    'unknown':'05',
}
HOST = {
    'HC':'0d',
    'AZ':'11',
    'AT':'10',
    '??':'03',
}
MOVE = {
    'left': ['pos']
}
            


class Mount(serial.Serial):
    def setup(self):
        # t = ['3b', '04', '0d', '11', 'fe']
        # t.append(self.checksum(t))
        # self.run_cmd(t)
        # self.run('AZ','unknown')
        self.run('AZ','ver')
        # return
        
        # print self.run('AZ', )
        a,b = 'pos','neg'
        a,b = b,a
        # print self.run('AZ', a, '09')
        self.run('AZ', a, '09')
        time.sleep(1)
        # print self.run('AZ', b, '00')
        self.run('AZ', b, '09')
        time.sleep(1)
        self.run('AZ', b, '00')
    
    def checksum(self, hcmd):
        items = [int(t,16) for t in hcmd[1:]]
        return hex( (1<<16) - sum(items))[-2:]
    
    def run(self, client, command, data=None):
        hcmd = [CMD['prefix'], '04', HOST['HC'],
                HOST[client], CMD[command]]
        if data is not None:
            hcmd.append(data)
        hcmd.append(self.checksum(hcmd))
        self.run_cmd(hcmd)
    
    def run_cmd(self, hcmd):
        print hcmd, [ord(hc.decode('hex')) for hc in hcmd]
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
    # device = '/dev/tty.usbserial-A100OZXL'
    device =  '/dev/tty.usbmodem12341'
    # device = '/dev/tty.usb'
    baud = 19200
    timeout = 0.1
    with Mount(device, baud, timeout=timeout) as mount:
        mount.setup()
    
    


if __name__ == '__main__':
    main()