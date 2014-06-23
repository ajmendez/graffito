# a telescope 

DEVICES = [
    '/dev/tty.usbserial-A100OZXL',
    '/dev/tty.usbmodem12341',

]


class Telescope(object):
    def __init__(self, device=None, baud=None, timeout=None):
        self.device = self.getdevice(device)
    
    
    def getdevice(self, device=None):
        if device:
            return device
        else:
            for device in DEVICES