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
        percent = float(step)/steps
        deltatime = (steps-step)/float(step)*(datetime.now()-START).total_seconds()
        print ' Step: {:02d} Time Left: {:0.0f}[s] Percent: {:0.0f}%'.format(
                  step, deltatime, percent*100.0)
                  
        
    


def main(device):
    '''A simple no feedback run of the telescope to
    sweep a room with multiple steps.'''
    speed = 7    # Mount movement speed
    delta = 0.1  # [seconds] to wait during move
    delza = 0.9  # [seconds] additional time to wait for at
    pause = 11.0  # [seconds] between frames
    steps = 200   # number of steps
    
    azsign = -1
    atsign = 1
    
    if DEBUG:
        pause = 0.5
    
    with telescope.Telescope(device) as tele:
        try:
            moves = [0,0]
            try:
                for step in range(1,steps+1):
                    # step is 1 indexed
                    tele.run('az', 'move', [azsign*speed])
                    tele.run('at', 'move', [atsign*speed])
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
                    raw_input('Press [enter] to return camera')
                    print 'Wait {} seconds'.format(sum(moves))
                    tele.run('az', 'move', [-azsign*speed])
                    tele.run('at', 'move', [-atsign*speed])
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