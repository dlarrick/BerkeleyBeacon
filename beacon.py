import sys
import time
import datetime
import pytz
from astral import *
from beautifulhue.api import Bridge
from threading import Thread, Event
import pyowm
import owmkey

username = '1cd503803c2588ef8ea97d02a2520df'
bridge = Bridge(device={'ip':'192.168.1.24'}, user={'name':username})
beacon = 2
sleepduration = 2.5
zipcode = '02465'
sunsetCity = 'Boston'
timezone = 'America/New_York'
owmCityId = 4945283

# Note: provide 'owmkey.py' file that contains a function get_owm_key
# returning your own OpenWeatherMap key
OWM_KEY = owmkey.get_owm_key()

runTimes = [['sunset','23:00'], ['6:00','sunrise']]
#debug:
#runTimes = [['sunset','23:00'], ['6:00','23:00']]

colors_xy = [[0.2182,0.1485], [0.7,0.2986]] # blue, red

local_tz = pytz.timezone(timezone)

def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt) # .normalize might be unnecessary

# indicators: 0: blue (clear); 1: flashing blue (clouds); 2: red (rain); 3: flashing red (snow/severe)
def owm_indicator(owm_code):
    # Snow
    if (owm_code >= 600 and owm_code < 622):
        return 3
    # Freezing rain
    if (owm_code == 511):
        return 3
    # Severe
    if (owm_code == 504 or
        owm_code == 503 or
        owm_code == 961 or
        owm_code == 962 or
        owm_code == 781 or
        (owm_code >= 900 and
         owm_code <= 906)):
        return 3
    # Rain
    if ((owm_code >= 200 and
         owm_code <= 232) or
        (owm_code >= 500 and
         owm_code <= 531)):
        return 2
    # Cloudy
    # 801 (few clouds)
    if ((owm_code >= 802 and
         owm_code <= 804)):
        return 1
    return 0


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
    usingToday = False
    if (datetime.datetime.now().hour < 12):
        usingToday = True

    if (usingToday):
        comparedate = datetime.datetime.now().date()
    else:
        comparedate = datetime.date.today() + datetime.timedelta(days=1)

    owm = pyowm.OWM(OWM_KEY)
    forecaster = owm.three_hours_forecast_at_id(owmCityId)
    forecast = forecaster.get_forecast()
    
    worst_indicator = 0
    found = False
    worst_weather = 0
    for weather in forecast:
        weatherdatetime = utc_to_local(datetime.datetime.fromtimestamp(weather.get_reference_time('unix')))
        if (weatherdatetime.date() == comparedate):
            weather_code = weather.get_weather_code()
            beacon_indicator = owm_indicator(weather_code)
            if (beacon_indicator > worst_indicator or
                found == False):
                worst_indicator = beacon_indicator
                worst_weather = weather
                found = True
            #print (weather.get_reference_time('iso'),weather.get_detailed_status(),weather_code,beacon_indicator)

    print ("Worst indicator is " + str(worst_indicator) + " " + worst_weather.get_detailed_status())
    return worst_indicator

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
                    try:
                        worstWeather = getWorstWeather()
                    except:
                        print('Failed to update weather')
                        worstWeather = currentWeather
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
                try:
                    worstWeather = getWorstWeather()
                except:
                    worstWeather = 0
                    print("Failed to get weather; assume clear")
                
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
