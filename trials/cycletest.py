import sys
import time
from beautifulhue.api import Bridge
from threading import Thread, Event

username = '1cd503803c2588ef8ea97d02a2520df'
bridge = Bridge(device={'ip':'192.168.1.24'}, user={'name':username})
beacon = 2
sleep = 2

colors = [0, 46920] # red, blue
colors_xy = [[0.7,0.2986],[0.139,0.081]]
sequence = [0, -1, 1, -1] # red, off, blue, off

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
        print "self._counter is %d" % self._counter
        colorIndex = self._sequence[self._counter]
        print "Color index is %d" % colorIndex
        if (colorIndex >= 0) :
            print "On, color %d" % colors[colorIndex]
        else:
            print "Off"
        print ""
        self._counter += 1
        if (self._counter >= len(self._sequence)):
            self._counter = 0
        

def hardcoded():
    # Red, off, blue, off
    resource_red = { 'which':beacon, 'data': { 'state': {'on':True, 'hue':0, 'sat':255, 'bri':255}}}
    resource_blue = { 'which':beacon, 'data': { 'state': {'on':True, 'hue':46920, 'sat':255, 'bri':255}}}
    resource_off = { 'which':beacon, 'data': { 'state': {'on':False}}}
    bridge.light.update(resource_red)
    time.sleep(sleep)
    bridge.light.update(resource_off)
    time.sleep(sleep)
    bridge.light.update(resource_blue)
    time.sleep(sleep)
    bridge.light.update(resource_off)

def runSequence():
    print "runSequence.counter is %d" % runSequence.counter
    colorIndex = sequence[runSequence.counter]
    print "Color index is %d" % colorIndex
    if (colorIndex >= 0) :
        print "On, color %d" % colors[colorIndex]
    else:
        print "Off"
    print ""
    runSequence.counter += 1
    if (runSequence.counter >= len(sequence)):
        runSequence.counter = 0

def main():
    response = getSystemData()

    if 'lights' in response:
        print 'Connected to Hub'
    else:
        error = response[0]['error']
        print error

    #runSequence.counter = 0;
    #timer = IntervalTimer(sleep, runSequence)
    #timer.start()
    #time.sleep(20)
    #timer.stop()

    sequencer = ColorSequencer(sleep, sequence)
    sequencer.start()
    time.sleep(20)
    sequencer.stop()
    
main()
