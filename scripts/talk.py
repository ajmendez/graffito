# #!/usr/bin/env python



"""Store input in a queue as soon as it arrives, and work on
it as soon as possible. Do something with untreated input if
the user interrupts. Do other stuff if idle waiting for
input."""

import sys
import select
import time
import threading
import Queue as queue
import serial
# files monitored for input
dev = '/dev/tty.usbmodem12341'
dev = '/dev/tty.usbserial-A100OZXL'
baud = 19200
ser = serial.Serial(dev,baud,timeout=0)
read_list = [sys.stdin]
parse_list = [ser]

# select() should wait for this many seconds for input.
timeout = 0.1 # seconds
last_work_time = time.time()


  
  



def treat_input(linein):
  if linein.strip() == 'q':
    raise KeyboardInterrupt
    
  global last_work_time
  try:
    out = map(int, linein.split(','))
    print out
    for i in out:
      ser.write(str(i))
      # print i
  except Exception as e:
    print 'Failed to parse: %s [%s]'%(linein,e)
  last_work_time = time.time()

def treat_output(lineout):
  print lineout


def idle_work():
  global last_work_time
  now = time.time()
  # do some other stuff every 2 seconds of idleness
  if now - last_work_time > 0.5:
    # print_status()
    # print('Idle for too long; doing some other stuff.')
    last_work_time = now

# some sort of cleanup that involves the input
def cleanup():
  print()
  while not input_queue.empty():
    line = input_queue.get()
    print("Didn't get to work on this line:", line)
  while not output_queue.empty():
    line = output_queue.get()
    print("Didn't get to parse on this line:", line)

# will hold input
input_queue = queue.Queue()
output_queue = queue.Queue()

# will signal to the input thread that it should exit:
# the main thread acquires it and releases on exit
interrupted = threading.Lock()
interrupted.acquire()
interrupted2 = threading.Lock()
interrupted2.acquire()

# input thread's work: stuff input in the queue until
# there's either no more input, or the main thread exits
def read_input():
  while (read_list and not interrupted.acquire(0)):
    ready = select.select(read_list, [], [], timeout)[0]
    for file in ready:
      line = file.readline()
      if line.rstrip():
        input_queue.put(line)
  print('Input thread is done.')
  
def parse_output():
  while (parse_list and not interrupted2.acquire(0)):
    resp = select.select(parse_list, [], [], timeout)[0]
    for file in resp:
      line = file.read()
      if line.strip():
        output_queue.put(line)
  print('output thread is done.')




  



input_thread = threading.Thread(target=read_input)
input_thread.start()
output_thread = threading.Thread(target=parse_output)
output_thread.start()

try:
  while True:
    # if finished reading input and all the work is done,
    # exit
    if input_queue.empty() and not input_thread.is_alive():
      break
    else:
      try:
        treat_input(input_queue.get(timeout=timeout))
      except queue.Empty:
        idle_work()
    # parse with a different function
    if output_queue.empty() and not output_thread.is_alive():
      break
    else:
      try:
        treat_output(output_queue.get(timeout=timeout))
      except queue.Empty:
        idle_work()
except KeyboardInterrupt:
  cleanup()

# make input thread exit as well, if still running
interrupted.release()
interrupted2.release()
print('Main thread is done.')



