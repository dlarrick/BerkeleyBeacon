import sys
import time
import datetime
from astral import *
from beautifulhue.api import Bridge
from threading import Thread, Event
import pywapi

username = '1cd503803c2588ef8ea97d02a2520df'
bridge = Bridge(device={'ip':'192.168.1.24'}, user={'name':username})
beacon = 2
sleep = 2.5
zipcode = '02465'
sunsetCity = 'Boston'
offHour = 21
offMinute = 30


colors = [46920, 0] # blue, red
colors_xy = [[0.139,0.081], [0.7,0.2986]]

# indicators: 0: blue (clear); 1: flashing blue (clouds); 2: red (rain); 3: flashing red (snow/severe)
yahoo_codes = [
    {'code': 0, 'description': 'tornado', 'indicator': 3},
    {'code': 1, 'description': 'tropical storm', 'indicator': 2},
    {'code': 2, 'description': 'hurricane', 'indicator': 3},
    {'code': 3, 'description': 'severe thunderstorms', 'indicator': 2},
    {'code': 4, 'description': 'thunderstorms', 'indicator': 2},
    {'code': 5, 'description': 'mixed rain and snow', 'indicator': 3},
    {'code': 6, 'description': 'mixed rain and sleet', 'indicator': 3},
    {'code': 7, 'description': 'mixed snow and sleet', 'indicator': 3},
    {'code': 8, 'description': 'freezing drizzle', 'indicator': 3},
    {'code': 9, 'description': 'drizzle', 'indicator': 2},
    {'code': 10, 'description': 'freezing rain', 'indicator': 3},
    {'code': 11, 'description': 'showers', 'indicator': 2},
    {'code': 12, 'description': 'showers', 'indicator': 2},
    {'code': 13, 'description': 'snow flurries', 'indicator': 3},
    {'code': 14, 'description': 'light snow showers', 'indicator': 3},
    {'code': 15, 'description': 'blowing snow', 'indicator': 3},
    {'code': 16, 'description': 'snow', 'indicator': 3},
    {'code': 17, 'description': 'hail', 'indicator': 3},
    {'code': 18, 'description': 'sleet', 'indicator': 3},
    {'code': 19, 'description': 'dust', 'indicator': 1},
    {'code': 20, 'description': 'foggy', 'indicator': 1},
    {'code': 21, 'description': 'haze', 'indicator': 1},
    {'code': 22, 'description': 'smoky', 'indicator': 0},
    {'code': 23, 'description': 'blustery', 'indicator': 0},
    {'code': 24, 'description': 'windy', 'indicator': 0},
    {'code': 25, 'description': 'cold', 'indicator': 0},
    {'code': 26, 'description': 'cloudy', 'indicator': 1},
    {'code': 27, 'description': 'mostly cloudy (night)', 'indicator': 1},
    {'code': 28, 'description': 'mostly cloudy (day)', 'indicator': 1},
    {'code': 29, 'description': 'partly cloudy (night)', 'indicator': 0},
    {'code': 30, 'description': 'partly cloudy (day)', 'indicator': 0},
    {'code': 31, 'description': 'clear (night)', 'indicator': 0},
    {'code': 32, 'description': 'sunny', 'indicator': 0},
    {'code': 33, 'description': 'fair (night)', 'indicator': 0},
    {'code': 34, 'description': 'fair (day)', 'indicator': 0},
    {'code': 35, 'description': 'mixed rain and hail', 'indicator': 2},
    {'code': 36, 'description': 'hot', 'indicator': 0},
    {'code': 37, 'description': 'isolated thunderstorms', 'indicator': 1},
    {'code': 38, 'description': 'scattered thunderstorms', 'indicator': 1},
    {'code': 39, 'description': 'scattered thunderstorms', 'indicator': 1},
    {'code': 40, 'description': 'scattered showers', 'indicator': 2},
    {'code': 41, 'description': 'heavy snow', 'indicator': 3},
    {'code': 42, 'description': 'scattered snow showers', 'indicator': 3},
    {'code': 43, 'description': 'heavy snow', 'indicator': 3},
    {'code': 44, 'description': 'partly cloudy', 'indicator': 0},
    {'code': 45, 'description': 'thundershowers', 'indicator': 1},
    {'code': 46, 'description': 'snow showers', 'indicator': 3},
    {'code': 47, 'description': 'isolated thundershowers', 'indicator': 1}
]


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
            OnColor(colorIndex)
        else:
            Off()
        #print ""
        self._counter += 1
        if (self._counter >= len(self._sequence)):
            self._counter = 0

def OnColor(colorIndex):
    print ("On, color " +  str(colors_xy[colorIndex]))
    sys.stdout.flush()
    #resource = { 'which':beacon, 'data': { 'state': {'on':True, 'hue':colors[colorIndex], 'sat':255, 'bri':255}}}
    resource = { 'which':beacon, 'data': { 'state': {'on':True, 'xy':colors_xy[colorIndex], 'sat':255, 'bri':255}}}
    bridge.light.update(resource)

def Off():
    print "Off"
    sys.stdout.flush()
    resource = { 'which':beacon, 'data': { 'state': {'on':False}}}
    bridge.light.update(resource)

def getWorstWeather():
    yahoo_result = pywapi.get_weather_from_yahoo(zipcode)
    tomorrow_code = int(yahoo_result['forecasts'][1]['code'])
    tomorrow_indicator = yahoo_codes[tomorrow_code]['indicator']
    
    worst = tomorrow_indicator
    worst_code = tomorrow_code
    worst_day = 'tomorrow'
    print ("Worst weather is " + yahoo_codes[worst_code]['description'] + " " + worst_day)
    return worst

def main():
    response = getSystemData()

    if 'lights' in response:
        print 'Connected to Hub'
    else:
        error = response[0]['error']
        print error

    # FIXME, ask for button if can't connect
        
    redSequence = [1, -1]
    blueSequence = [0, -1]
    redSequencer = ColorSequencer(sleep, redSequence)
    blueSequencer = ColorSequencer(sleep, blueSequence)

    ast = Astral()
    location = ast[sunsetCity]

    running = False
    shouldRun = False
    runningSequencer = None
    #debugCounter = 0

    try:
        while (True):
            #if (debugCounter > 10 and debugCounter < 20):
            #    shouldRun = True
            #else:
            #    shouldRun = False
            #debugCounter += 1
            
            sunset = location.sunset()
            now = datetime.datetime.now(sunset.tzinfo)
            today = datetime.date.today()
            offtime = datetime.time(offHour, offMinute, 0, 0, now.tzinfo)
            offstamp = datetime.datetime.combine(today, offtime)

            print('Should run between ' + str(sunset) + ' and ' + str(offstamp) + '; now ' + str(now))
            if (now >= sunset and now <= offstamp):
                shouldRun = True
            else:
                shouldRun = False

            if (running and shouldRun):
                print 'Running'

            if (not running and not shouldRun):
                print 'Not running'

            if (shouldRun and not running):
                # Get weather and start running
                print 'Not running but should be - start'
                worstWeather = getWorstWeather()

                if (worstWeather == 0):
                    OnColor(0)
                elif (worstWeather == 1):
                    runningSequencer = blueSequencer
                    blueSequencer.start()
                elif (worstWeather == 2):
                    OnColor(1)
                elif (worstWeather == 3):
                    runningSequencer = redSequencer
                    redSequencer.start()
                running = True

            if (running and not shouldRun):
                # Stop running
                print 'Running but should not be - stop'
                if (runningSequencer):
                    runningSequencer.stop()
                Off()
                running = False

            sys.stdout.flush()
            time.sleep(60)

    except KeyboardInterrupt:
        print 'Bye!'
        if (runningSequencer):
            runningSequencer.stop()
        Off()
        
main()
