import sys
import time
from beautifulhue.api import Bridge
from threading import Thread, Event

username = '1cd503803c2588ef8ea97d02a2520df'
bridge = Bridge(device={'ip':'192.168.1.24'}, user={'name':username})
beacon = 2
sleep = 2

colors = [0, 46920] # red, blue

def getSystemData():
    resource = {'which':'system'}
    return bridge.config.get(resource)['resource']

# StoppableThread is from user Dolphin, from http://stackoverflow.com/questions/5849484/how-to-exit-a-multithreaded-program
class StoppableThread(Thread):  

    def __init__(self):
        Thread.__init__(self)
        self.stop_event = Event()        

    def stop(self):
        if self.isAlive() == True:
            # set event to signal thread to terminate
            self.stop_event.set()
            # block calling thread until thread really has terminated
            self.join()

class IntervalTimer(StoppableThread):

    def __init__(self, interval, worker_func):
        StoppableThread.__init__(self)
        self._interval = interval
        self._worker_func = worker_func

    def run(self):
        while not self.stop_event.is_set():
            self._worker_func(self)
            time.sleep(self._interval)

class ColorSequencer(IntervalTimer):

    def __init__(self, interval, sequence):
        IntervalTimer.__init__(self, interval, ColorSequencer.sequencer)
        self._sequence = sequence
        self._counter = 0

    def sequencer(self):
        #print "self._counter is %d" % self._counter
        colorIndex = self._sequence[self._counter]
        #print "Color index is %d" % colorIndex
        if (colorIndex >= 0) :
            print "On, color %d" % colors[colorIndex]
        else:
            print "Off"
        #print ""
        self._counter += 1
        if (self._counter >= len(self._sequence)):
            self._counter = 0

def main():
    response = getSystemData()

    if 'lights' in response:
        print 'Connected to Hub'
    else:
        error = response[0]['error']
        print error

    allSequence = [0, -1, 1, -1] # red, off, blue, off
    redSequence = [0, -1]
    blueSequence = [1, -1]
    redSequencer = ColorSequencer(sleep, redSequence)
    blueSequencer = ColorSequencer(sleep, blueSequence)
    redSequencer.start()
    time.sleep(10)
    redSequencer.stop()
    blueSequencer.start();
    time.sleep(10)
    blueSequencer.stop()
main()
