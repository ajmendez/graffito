#!/usr/bin/env python

import sys
import select
import time
import threading
import Queue as queue
import serial

TIMEOUT = 0.2

def idle():
  print '.',
  sys.stdout.flush()

def tracefunc(frame, event, arg, indent=[0]):
  if event == "call":
    indent[0] += 2
    print "-" * indent[0] + "> call function", frame.f_code.co_name
  elif event == "return":
    print "<" + "-" * indent[0], "exit function", frame.f_code.co_name
    indent[0] -= 2
  return tracefunc

import sys
# sys.settrace(tracefunc)

interrupt = threading.Lock()
interrupt.acquire()

thread = threading.Thread(target=self.read)
thread.start()

class Run(object):
  def __init__(self, name, fileobj, timeout=TIMEOUT):
    self.name = name
    self.timeout = timeout
    self.files = [fileobj]
    self.queue = queue.Queue()
    
  
  def run(self):
    if (self.queue.empty() and self.thread.is_alive()):
      return 'done'
    else:
      try:
        self.treat(self.queue.get(timeout=self.timeout))
      except queue.Empty:
        idle()
  
  def treat(self, line):
    print "[%s]: %s"%(self.name, line)
  
  def read(self):
    while (self.files and not interrupt.acquire(0)):
      resp = select.select(self.files, [], [], self.timeout)[0]
      for item in resp:
        line = item.readline()
        if line.strip():
          self.queue.put(line)
    print "[%s] reading is done."%(self.name)
  
  def cleanup(self):
    while not self.queue.empty():
      item = self.queue.get()
      print "[%s] did not handle: %s"%(self.name, item)
    


if __name__ == '__main__':
  
  
  inputreader = Run('input', sys.stdin)
  try:
    while True:
      status = inputreader.run()
      if status is not None:
        break
  except KeyboardInterrupt:
    inputreader.cleanup()
  
  print 'main is done'
  interrupt.release()


