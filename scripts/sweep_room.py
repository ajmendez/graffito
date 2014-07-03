#!/usr/bin/env python
# sweep_room.py -- Move the mount incrementally to get across the room

import sys
import time
from graffito import telescope
from datetime import datetime
DEBUG = ('debug' in sys.argv)
RETURN = ('return' in sys.argv)


START = datetime.now()
def updatescreen(step,steps):
    sys.stdout.write('.')
    sys.stdout.flush()
    if (step%(steps/10)==0) or (step==steps) :
        deltatime = float(steps-step)/step*(datetime.now()-START).total_seconds()
        print ' Step: {:02d} Time Left: {:0.2f}[s]'.format(
                  step, deltatime)
                  
        
    


def main(device):
    '''A simple no feedback run of the telescope to
    sweep a room with multiple steps.'''
    speed = 8    # Mount movement speed
    delta = 0.3  # [seconds] to wait during move
    delza = 1.7  # [seconds] additional time to wait for at
    pause = 4.0  # [seconds] between frames
    steps = 40   # number of steps
    
    if DEBUG:
        pause = 0.5
    
    with telescope.Telescope(device) as tele:
        try:
            moves = [0,0]
            try:
                for step in range(1,steps+1):
                    # step is 1 indexed
                    tele.run('az', 'move', [-speed])
                    tele.run('at', 'move', [-speed])
                    time.sleep(delta)
                    tele.run('az', 'move', [0])
                    time.sleep(delza)
                    tele.run('at', 'move', [0])
                    time.sleep(pause)
                    # take a picture now
                    moves[0] += delta
                    moves[1] += delza
                    updatescreen(step, steps)
            except KeyboardInterrupt as e:
                print 'Bye!'
            finally:
                # return back to staring position.
                if RETURN:
                    user = raw_input('Press [enter] to return camera')
                    print 'Wait {} seconds'.format(sum(moves))
                    tele.run('az', 'move', [speed])
                    tele.run('at', 'move', [speed])
                    time.sleep(moves[0])
                    tele.run('az', 'move', [0])
                    time.sleep(moves[1])
                    tele.run('az', 'move', [0])
                
        except KeyboardInterrupt as e:
            print 'Goodbye!'
        finally:
            tele.run('az', 'move', [0])
            tele.run('at', 'move', [0])
            


if __name__ == '__main__':
    device = telescope.getdevice()
    main(device)