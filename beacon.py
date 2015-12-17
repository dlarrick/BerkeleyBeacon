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
sleepduration = 2.5
zipcode = '02465'
sunsetCity = 'Boston'
runTimes = [['sunset','23:00'], ['6:00','sunrise']]
#runTimes = [['sunset','23:00'], ['6:00','8:00']]


colors = [46920, 0] # blue, red
colors_xy = [[0.2182,0.1485], [0.7,0.2986]]

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
    {'code': 38, 'description': 'scattered thunderstorms', 'indicator': 2},
    {'code': 39, 'description': 'scattered thunderstorms', 'indicator': 2},
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
        self._counter += 1
        if (self._counter >= len(self._sequence)):
            self._counter = 0

def OnColor(colorIndex):
    resource = { 'which':beacon, 'data': { 'state': {'on':True, 'xy':colors_xy[colorIndex], 'sat':255, 'bri':255}}}
    bridge.light.update(resource)

def Off():
    resource = { 'which':beacon, 'data': { 'state': {'on':False}}}
    bridge.light.update(resource)

def getWorstWeather():
    yahoo_result = pywapi.get_weather_from_yahoo(zipcode)
    today = datetime.date.today()
    date0str = yahoo_result['forecasts'][0]['date']
    date0 = datetime.datetime.strptime(date0str, '%d %b %Y').date()
    today_offset = 0
    if date0 != today:
        today_offset = 1
    today_code = int(yahoo_result['forecasts'][today_offset]['code'])
    tomorrow_code = int(yahoo_result['forecasts'][today_offset+1]['code'])
    # now and today are ['condition']['code'] and ['forecasts'][0]['code'] respectively
    # Sometimes it has yesterday's forecasts still, so check that [0] is really today
    # Before noon, use today's weather; after noon, use tomorrow's
    now = datetime.datetime.now()
    if (now.hour < 12):
        worst_code = today_code
        worst_day = 'today'
    else:
        worst_code = tomorrow_code
        worst_day = 'tomorrow'
    indicator = yahoo_codes[worst_code]['indicator']
    print ("Worst weather is " + yahoo_codes[worst_code]['description'] + " " +
           worst_day)
    return indicator

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
    redSequencer = ColorSequencer(sleepduration, redSequence)
    blueSequencer = ColorSequencer(sleepduration, blueSequence)

    ast = Astral()
    location = ast[sunsetCity]

    running = False
    shouldRun = False
    runningSequencer = None
    weatherTime = None
    worstWeather = None

    try:
        while (True):            
            sunrise = location.sunrise()
            sunset = location.sunset()
            now = datetime.datetime.now(sunset.tzinfo)
            today = datetime.date.today()
            tz = now.tzinfo
            shouldRun = False
            for onoff in runTimes:
                if onoff[0] == 'sunset':
                    onstamp = sunset
                elif onoff[0] == 'sunrise':
                    onstamp = sunrise
                else:
                    ontime = datetime.datetime.strptime(onoff[0], '%H:%M').time()
                    onstamp = datetime.datetime(today.year, today.month, today.day,
                                                ontime.hour, ontime.minute, tzinfo=tz)
                if onoff[1] == 'sunset':
                    offstamp = sunset
                elif onoff[1] == 'sunrise':
                    offstamp = sunrise
                else:
                    offtime = datetime.datetime.strptime(onoff[1], '%H:%M').time()
                    offstamp = datetime.datetime(
                        today.year, today.month, today.day,
                        offtime.hour, offtime.minute, tzinfo=tz)
                print('Should run between ' + str(onstamp) + ' and ' +
                      str(offstamp) + '; now ' + str(now))
                if (now >= onstamp and now <= offstamp):
                    shouldRun = True
            
            if (running and shouldRun):
                print 'Running'
                # Re-check weather once an hour
                if ((now - weatherTime).total_seconds() > 60*60):
                    currentWeather = worstWeather
                    worstWeather = getWorstWeather()
                    weatherTime = now
                    if (worstWeather != currentWeather):
                        print 'Weather changed'
                        if (runningSequencer):
                            runningSequencer.stop()
                            Off()
                        if (worstWeather == 0):
                            OnColor(0)
                            print 'On, steady blue'
                        elif (worstWeather == 1):
                            runningSequencer = blueSequencer
                            runningSequencer.start()
                            blueSequencer = ColorSequencer(sleepduration, blueSequence)
                            print 'On, flashing blue'
                        elif (worstWeather == 2):
                            OnColor(1)
                            print 'On, steady red'
                        elif (worstWeather == 3):
                            runningSequencer = redSequencer
                            runningSequencer.start()
                            redSequencer = ColorSequencer(sleepduration, redSequence)
                            print 'On, flashing red'
                        

            if (not running and not shouldRun):
                print 'Not running'

            if (shouldRun and not running):
                # Get weather and start running
                print 'Not running but should be - start'
                worstWeather = getWorstWeather()
                weatherTime = now

                if (worstWeather == 0):
                    OnColor(0)
                    print 'On, steady blue'
                elif (worstWeather == 1):
                    runningSequencer = blueSequencer
                    runningSequencer.start()
                    blueSequencer = ColorSequencer(sleepduration, blueSequence)
                    print 'On, flashing blue'
                elif (worstWeather == 2):
                    OnColor(1)
                    print 'On, steady red'
                elif (worstWeather == 3):
                    runningSequencer = redSequencer
                    runningSequencer.start()
                    redSequencer = ColorSequencer(sleepduration, redSequence)
                    print 'On, flashing red'
                running = True

            if (running and not shouldRun):
                # Stop running
                print 'Running but should not be - stop'
                if (runningSequencer):
                    runningSequencer.stop()
                Off()
                print 'Off'
                running = False

            sys.stdout.flush()
            time.sleep(60)

    except KeyboardInterrupt:
        print 'Bye!'
        if (runningSequencer):
            runningSequencer.stop()
        Off()
        
main()
