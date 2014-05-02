#!/usr/bin/python

#  https://github.com/atomicpunk/scripts/edit/master/celestron.py
# Copyright 2012 Todd Brandt <tebrandt@frontier.com>
#
# This program is free software; you may redistribute it and/or modify it
# under the same terms as Perl itself.
#utility to organize media collections
#Copyright (C) 2012 Todd Brandt <tebrandt@frontier.com>
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along
#with this program; if not, write to the Free Software Foundation, Inc.,
#51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import sys
import time
import os
import string
import re
import array
import datetime
import struct
import serial
import ntplib

# hillsboro, OR: 45 31 5 0, 122 54 7 1

class Celestron:
    devpath = "/dev/ttyUSB0"
    devpath = "/dev/tty.usbserial-A100OZXL"
    cmdlist = {
        'test'            : 'Kx',
        'cancel'        : 'M',
        'get-time'        : 'h',
        'get-model'        : 'm',
        'get-location'    : 'w',
        'set-location'    : 'W\x2d\x1f\x05\x00\x7a\x36\x07\x01',
        'check-goto'    : 'L',
        'check-align'    : 'J',
        'version-hc'    : 'V',
        'version-azi'    : 'P\x01\x10\xfe\x00\x00\x00\x02',
        'version-alt'    : 'P\x01\x11\xfe\x00\x00\x00\x02',
        'get-tracking'    : 't',
        'start-tracking': 'T\x02',
        'stop-tracking' : 'T\x00',
        'get-az-alt16'    : 'Z',
        'get-az-alt32'    : 'z',
        'set-az-alt16'    : '^B(?P<a>[0-9,A-F]{4}),(?P<b>[0-9,A-F]{4})$',
        'set-az-alt32'    : '^b(?P<a>[0-9,A-F]{8}),(?P<b>[0-9,A-F]{8})$',
        'get-ra-dec16'    : 'E',
        'get-ra-dec32'    : 'e',
        'set-ra-dec16'    : '^R(?P<a>[0-9,A-F]{4}),(?P<b>[0-9,A-F]{4})$',
        'set-ra-dec32'    : '^r(?P<a>[0-9,A-F]{8}),(?P<b>[0-9,A-F]{8})$',
    }
    trackmodes = ["Off", "Alt/Az", "EQ North", "EQ South"]
    tracking = 0
    fp = 0
    online = False
    moving = False
    aligned = False
    version = [0.0, 0.0, 0.0]
    altitude = 90.0
    azimuth = 90.0
    wait = False
    def __init__(self):
        self.fp = serial.Serial(self.devpath, baudrate=19200,
            parity=serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
            timeout=0)
    def status(self, v):
        print 's', v, self.cmdlist['test']
        r = {False: "NO", True: "YES"}
        res = self.cmdExec(self.cmdlist['test'])
        self.online = False
        if(res == "x"): self.online = True
        if(v): print("  Connection on-line: %s" % r[self.online])
        if(not self.online): return False

        res = self.cmdExec(self.cmdlist['version-hc'])
        tmp = struct.unpack("BB", res)
        self.version[0] = float(tmp[0]) + (float(tmp[1]) / 10.0)
        if(v): print("Hand Control version: %.1f" % self.version[0])

        if(self.version[0] > 3):
            res = self.cmdExec(self.cmdlist['version-azi'])
            tmp = struct.unpack("BB", res)
            self.version[1] = float(tmp[0]) + (float(tmp[1]) / 10.0)
            if(v): print("   Azi Motor version: %.1f" % self.version[1])

            res = self.cmdExec(self.cmdlist['version-alt'])
            tmp = struct.unpack("BB", res)
            self.version[2] = float(tmp[0]) + (float(tmp[1]) / 10.0)
            if(v): print("   Alt Motor version: %.1f" % self.version[2])

        if(self.version[0] > 5):
            res = self.cmdExec(self.cmdlist['get-model'])
            models = [" ", "GPS Series", " ", "i-Series",
                "i-Series SE", "CGE", "Advanced GT", "SLT",
                " ", "CPC", "GT", "4/5 SE", "6/8 SE"]
            m = models[struct.unpack("B", res)[0]]
            if(v):
                print("     Telescope Model: %s" % m)
                print("  Telescope UTC Time: %s" % self.getTime())
                print("  Telescope Location: %s" % self.getLocation())

        res = self.cmdExec(self.cmdlist['check-goto'])
        self.moving = False
        if(res == "1"): self.moving = True
        if(v): print("   Is machine moving: %s" % r[self.moving])

        res = self.cmdExec(self.cmdlist['check-align'])
        self.aligned = False
        val = r[False]
        if(res == "1"):
            self.aligned = True
            val = r[True]
        if(v): print("  Is machine aligned: %s" % val)

        if(self.version[0] > 3):
            res = self.cmdExec(self.cmdlist['get-tracking'])
            try:
                self.tracking = struct.unpack("B", res)[0]
            except:
                self.tracking = 0
            val = self.trackmodes[(self.tracking)%4]
            if(v): print("    Machine tracking: %s" % val)

        self.getAltAzi()
        if(v):
            print("            Altitude: %.2f deg" % self.altitude)
            print("             Azimuth: %.2f deg" % self.azimuth)
        return True
    def initControl(self):
        self.status(False)
        if(not self.online):
            doError("Telescope is not connected", False)
        self.cmdExec(self.cmdlist['set-location'])
        self.setTime()
        self.cmdExec(self.cmdlist['start-tracking'])
        self.status(True)
    def setTime(self):
        cl = ntplib.NTPClient()
        try:
            response = cl.request('nist-time-server.eoni.com', version=3)
            t = time.gmtime(response.tx_time)
        except:
            print "ERROR: NTP server failed, using local time"
            t = time.gmtime()
        rawcmd = struct.pack("cBBBBBBBB", 'H', t.tm_hour, t.tm_min,
                t.tm_sec, t.tm_mon, t.tm_mday, t.tm_year-2000, 0, 0)
        self.cmdExec(rawcmd)
    def getTime(self):
        res = self.cmdExec(self.cmdlist['get-time'])
        try:
            tmp = struct.unpack("BBBBBBBB", res)
        except:
            doError("Bad return for get-time: %s" % res, False)
        t = datetime.datetime(int(tmp[5])+2000, int(tmp[3]),
            int(tmp[4]), int(tmp[0]), int(tmp[1]), int(tmp[2]))
        dH = int(tmp[6])
        if(dH > 200):
            dH = 256 - dH
        else:
            dH = 0 - dH
        dH = dH - int(tmp[7])
        t += datetime.timedelta(hours=dH)
        return t
    def getLocation(self):
        res = self.cmdExec(self.cmdlist['get-location'])
        try:
            tmp = struct.unpack("BBBBBBBB", res)
        except:
            doError("Bad return for get-location: %s" % res, False)
        ew = ['E', 'W']
        ns = ['N', 'S']
        loc = "%d %d\'%d\" %s, %d %d\'%d\" %s" % \
            (int(tmp[0]), int(tmp[1]), int(tmp[2]), ns[int(tmp[3])],
             int(tmp[4]), int(tmp[5]), int(tmp[6]), ew[int(tmp[7])])
        return loc
    def getAltAzi(self):
        res = self.cmdExec(self.cmdlist['get-az-alt32'])
        m = re.match('^(?P<azi>[0-9,A-F]{8}),(?P<alt>[0-9,A-F]{8})$', res)
        if(not m):
            print("Invalid Altitude/Azimuth data from telescope")
            return
            #doError("Invalid Altitude/Azimuth data from telescope", False)
        self.altitude = (float(int(m.group("alt"), 16)) / 0x100000000) * 360.0
        self.azimuth = (float(int(m.group("azi"), 16)) / 0x100000000) * 360.0
    def gotoAltAzi(self, alt, azi):
        print("  Current Altitude: %.2f deg" % self.altitude)
        print("   Current Azimuth: %.2f deg" % self.azimuth)
        hexalt = int((alt / 360) * 0x100000000)
        hexazi = int((azi / 360) * 0x100000000)
        cmd = "b%08X,%08X" % (hexazi, hexalt)
        res = self.cmdExec(cmd)
        if(self.wait):
            self.moving = True
            while self.moving:
                self.getAltAzi()
                msg = "  ALTITUDE %.2f deg : AZIMUTH %.2f deg" % (self.altitude, self.azimuth)
                sys.stdout.write(msg + " \r")
                sys.stdout.flush()
                time.sleep(.5)
                res = self.cmdExec(self.cmdlist['check-goto'])
                if(res == "0"):
                    self.moving = False
                    print msg
    def setTracking(self, alt, azi):
        altdir = azidir = 6
        altrate = int(alt * 4)
        azirate = int(azi * 4)
        if(alt < 0):
            altdir = 7
            altrate = -altrate
        if(azi < 0):
            azidir = 7
            azirate = -azirate
        althi = (altrate >> 8) & 0xff
        altlo = altrate & 0xff
        azihi = (azirate >> 8) & 0xff
        azilo = azirate & 0xff
        print("Altitude tracking at %.2f arcsec/sec" % (float(int(alt*4))/4))
        print(" Azimuth tracking at %.2f arcsec/sec" % (float(int(azi*4))/4))
        altcmd = struct.pack("cBBBBBBB", 'P', 3, 17, altdir, althi, altlo, 0, 0)
        azicmd = struct.pack("cBBBBBBB", 'P', 3, 16, azidir, azihi, azilo, 0, 0)
        self.cmdExec(altcmd)
        self.cmdExec(azicmd)
    def cmdName(self, cmd):
        for name in self.cmdlist:
            fmt = self.cmdlist[name]
            if(re.match(fmt, cmd)):
                return name
        return ""
    def cmdExec(self, cmd):
        self.fp.write(cmd)
        res = ""
        n = 100
        while True:
            ch = self.fp.read(16)
            tmp = ch.encode('hex')
            if len(tmp) > 0:
                print tmp
            if n == 0:
                break
            else:
                n -= 1
            
            if(ch == "#"):
                break
            res += ch
        print res
        return res

celestron = Celestron()

def printHelp():
    global celestron

    print("")
    print("Celestron Controller")
    print("Usage: celestron.py <options>")
    print("")
    print("Description:")
    print("  Controls a celestron telescope via a serial port")
    print("")
    print("Options:")
    print("  -h               Print this help text")
    print("  -cmd rawcmd      Execute a raw command")
    print("  -init            Initialize the telescope computer")
    print("  -status          Print the telescope status")
    print("  -cancel          Cancel a goto move, but leave tracking")
    print("  -stop            Completely stop the telescope")
    print("  -altazi alt azi  Goto altitude azimuth")
    print("  -track alt azi   Set tracking rates for alt-azi in arcsec/sec (15 is earth rotation)")
    print("")
    return True

def doError(msg, help):
    print("ERROR: %s") % msg
    if(help == True):
        printHelp()
    sys.exit()

# -- script main --
# loop through the command line arguments
cmd = []
args = iter(sys.argv[1:])
for arg in args:
    if(arg == "-h"):
        printHelp()
        sys.exit()
    elif(arg == "-cmd"):
        try:
            rawcmd = args.next()
        except:
            doError("No cmd supplied", True)
        print("Issuing cmd : '%s' ..." % (rawcmd))
        res = celestron.cmdExec(rawcmd)
        print("Result from '%s' = '%s'" % (rawcmd, res))
        sys.exit()
    elif(arg == "-status"):
        celestron.status(True)
        sys.exit()
    elif(arg == "-track"):
        try: altrate = args.next()
        except: doError("No altitude rate supplied", True)
        try: altrate = float(altrate)
        except:    doError("Bad altitude rate, what the hell is this? [%s]" % altrate, False)
        try: azirate = args.next()
        except: doError("No azimuth rate supplied", True)
        try: azirate = float(azirate)
        except: doError("Bad azimuth rate, what the hell is this? [%s]" % azirate, False)
        cmd = ["track", altrate, azirate]
    elif(arg == "-init"):
        celestron.initControl()
        sys.exit()
    elif(arg == "-wait"):
        celestron.wait = True
    elif(arg == "-cancel"):
        celestron.status(False)
        if(celestron.online):
            celestron.cmdExec(celestron.cmdlist['cancel'])
        else:
            doError("Connection off-line", False)
        sys.exit()
    elif(arg == "-stop"):
        celestron.status(False)
        if(celestron.online):
            celestron.cmdExec(celestron.cmdlist['cancel'])
            celestron.cmdExec(celestron.cmdlist['stop-tracking'])
        else:
            doError("Connection off-line", False)
        sys.exit()
    elif(arg == "-altazi"):
        try: alt = args.next()
        except: doError("No altitude supplied", True)
        try: alt = float(alt)
        except: doError("Bad altitude, what the hell is this? [%s]" % alt, False)
        try: azi = args.next()
        except: doError("No azimuth supplied", True)
        try: azi = float(azi)
        except: doError("Bad azimuth, what the hell is this? [%s]" % azi, False)
        if(alt < 0 or alt >= 360):
            doError("Altitude %.2f is not between 0 and 360" % alt, False)
        if(azi < 0 or azi >= 360):
            doError("Azimuth %.2f is not between 0 and 360" % azi, False)
        cmd = ["altazi", alt, azi]
    else:
        doError("Invalid argument: "+arg, True)

if(cmd):
    celestron.status(False)
    if(not celestron.online):
        doError("Connection off-line", False)
    if(cmd[0] == "altazi"):
        celestron.gotoAltAzi(cmd[1], cmd[2])
    elif(cmd[0] == "track"):
        celestron.setTracking(cmd[1], cmd[2])
