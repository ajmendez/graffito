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

# import curses
# status_state = True
# def print_status():
#   global status_state
#   if status_state:
#     marker = 'x'
#   else:
#     marker = 'o'
#   status_state = not status_state
#   # sys.stdout.write("\033[s%s\033[1D\033[u"%marker)
#   # sys.stdout.write("\033[s\033[0;0H%s\033[u"%marker)
#   sys.stdout.write('%s\033[1D'%marker)
#   # print "\033[s",
#   # print "\033[0;0H",
#   # print "\033[K",
#   # print "\033[31m",
#   # print "%s"%marker,
#   # print "\033[=31l",
#   # print "\033[0D",
#   # print "\033[u",
#   # print "\0336n",
#   sys.stdout.flush()
#   # try:
#   #   screen = curses.initscr()
#   #   # curses.nocbreak()
#   #   # stdscr.keypad(False)
#   #   y,x = screen.getmaxyx()
#   #   screen.mvaddstr(0,0, item)
#   #   screen.refresh()
#   # except Exception as e:
#   #   screen.refresh()
#   #   print e
#   # finally:
#   #   # curses.endwin()
#   #   pass

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





# """Check for input every 0.1 seconds. Treat available input
# immediately, but do something else if idle."""
# 
# import sys
# import select
# import time
# 
# # files monitored for input
# read_list = [sys.stdin]
# # select() should wait for this many seconds for input.
# # A smaller number means more cpu usage, but a greater one
# # means a more noticeable delay between input becoming
# # available and the program starting to work on it.
# timeout = 0.1 # seconds
# last_work_time = time.time()
# last_marker = True
# 
# def treat_input(linein):
#   global last_work_time
#   print("Workin' it!", linein)
#   time.sleep(1) # working takes time
#   print('Done')
#   last_work_time = time.time()
# 
# def idle_work():
#   global last_work_time
#   global last_marker
#   
#   now = time.time()
#   # do some other stuff every 2 seconds of idleness
#   if now - last_work_time > 0.1:
#     # print('Idle for too long; doing some other stuff.')
#     if last_marker:
#         print '\r.',
#         last_marker = False
#     else:
#         print '\ro',
#         last_marker = True
#         
#     # sys.stdout.flush()
#     last_work_time = now
# 
# def main_loop():
#   global read_list
#   # while still waiting for input on at least one file
#   while read_list:
#     ready = select.select(read_list, [], [], timeout)[0]
#     if not ready:
#       idle_work()
#     else:
#       for file in ready:
#         line = file.readline()
#         if not line: # EOF, remove file from input list
#           read_list.remove(file)
#         elif line.rstrip(): # optional: skipping empty lines
#           treat_input(line)
# 
# try:
#     main_loop()
# except KeyboardInterrupt:
#   pass























# import threading, serial, sys
# 
# connected = False
# port = '/dev/tty.usbmodem12341'
# baud = 19200
# 
# 
# 
# def handle_data(data):
#     print(data)
# 
# def read_from_port(ser):
#     global connected
#     while not connected:
#         #serin = ser.read()
#         connected = True
# 
#         while True:
#            # print("test")
#            reading = ser.readline().decode()
#            handle_data(reading)
# 
# 
# if __name__ == '__main__':
#     try:
#         serialport = serial.Serial(port, baud, timeout=0)
#         thread = threading.Thread(target=read_from_port, args=(serialport,))
#         thread.start()
#     except KeyboardInterrupt as e:
#         print 'Done'


# 
# import sys
# import time
# import threading
# import Queue as queue
# 
# TIMEOUT = 0.1 # seconds
# LAST = time.time()
# 
# # threading stuff
# # will hold all input read, until the work thread has chance
# # to deal with it
# input_queue = queue.Queue()
# # will signal to the work thread that it should exit when
# # it finishes working on the currently available input
# no_more_input = threading.Lock()
# no_more_input.acquire()
# # will signal to the work thread that it should exit even if
# # there's still input available
# interrupted = threading.Lock()
# interrupted.acquire()
# 
# work_thread = threading.Thread(target=treat_input_loop)
# work_thread.start()
# 
# 
# def treat_input(linein):
#   print 'Working on line:', linein
#   time.sleep(0.5) # working takes time
#   print 'Done working on line:', linein
#   LAST = time.time()
# 
# def idle_work():
#   now = time.time()
#   # do some other stuff every 2 seconds of idleness
#   if now - LAST > 2:
#     print 'Idle for too long; doing some other stuff.'
#     LAST = now
# 
# def input_cleanup():
#   print()
#   while not input_queue.empty():
#     line = input_queue.get()
#     print "Didn't get to work on this line:", line
# 
# # work thread' loop: work on available input until main
# # thread exits
# def treat_input_loop():
#   while not interrupted.acquire(False):
#     try:
#       treat_input(input_queue.get(timeout=TIMEOUT))
#     except queue.Empty:
#       # if no more input, exit
#       if no_more_input.acquire(False):
#         break
#       else:
#         idle_work()
#   print 'Work loop is done.'
# 
# 
# def main():
# 
#     # main loop: stuff input in the queue until there's either
#     # no more input, or the program gets interrupted
#     try:
#       for line in sys.stdin:
#         print line
#         if line: # optional: skipping empty lines
#             print line
#       #     input_queue.put(line)
#       # 
#       # # inform work loop that there will be no new input and it
#       # # can exit when done
#       # no_more_input.release()
#       # 
#       # # wait for work thread to finish
#       # work_thread.join()
# 
#     except KeyboardInterrupt:
#         # interrupted.release()
#         # input_cleanup()
#         pass
#     
#     print('Main loop is done.')
# 
# 
# 
# if __name__ == '__main__':
#     for line in sys.stdin:
#         print line
#     # main()
# 
# 
# 
# 
# def talk():
#     device = '/dev/tty.usbmodem12341'
#     baud = 19200
#     with serial.Serial(device, baud, timeout=0.2) as s:
#         pass