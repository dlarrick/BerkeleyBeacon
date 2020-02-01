import sys
import time
import datetime
from threading import Thread, Event
import json
import pytz
import astral
from qhue import Bridge
# HA
from requests import get
# OWM
import pyowm
import owmkey

USERNAME = '1cd503803c2588ef8ea97d02a2520df'
BRIDGE = Bridge('192.168.1.24', USERNAME)
# 2 == LR Middle; 6 == actual Beacon
#BEACON = 2
BEACON = 6
SLEEP_DURATION = 2.5
SUNSET_CITY = 'Boston'
TIMEZONE = 'America/New_York'
OWM_CITY_ID = 4945283

# HA
HA_WEATHER_URL = 'http://rosie.parkercat.org:8123/api/states/weather.dark_sky_hourly'
HA_TOKEN = owmkey.get_ha_token()
USE_HA = True

# Note: provide 'owmkey.py' file that contains a function get_owm_key
# returning your own OpenWeatherMap key
OWM_KEY = owmkey.get_owm_key()

RUN_TIMES = [['sunset', '23:00'], ['6:00', 'sunrise']]
#debug/test:
#RUN_TIMES = [['sunset', '23:00'], ['6:00', '23:00']]

# blue, red -- better for 1st-get Hue bulbs
#COLORS_XY = [[0.2182,0.1485], [0.7,0.2986]]
# blue, red -- better for 3rd-gen Hue bulbs
COLORS_XY = [[0.1947, 0.2229], [0.6663, 0.2978]]

LOCAL_TZ = pytz.timezone(TIMEZONE)

def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(LOCAL_TZ)
    return LOCAL_TZ.normalize(local_dt) # .normalize might be unnecessary

# indicators: 0: blue (clear); 1: flashing blue (clouds);
# 2: red (rain); 3: flashing red (snow/severe)
def owm_indicator(owm_code):
    # See https://openweathermap.org/weather-conditions
    # Snow
    if 600 <= owm_code < 622:
        return 3
    # Freezing rain
    if owm_code == 511:
        return 3
    # Severe
    severe = [503, 504, 961, 962, 781, 900, 901, 902, 903, 904, 905, 906]
    if owm_code in severe:
        return 3
    # Rain
    if (200 <= owm_code <= 232 and \
        owm_code != 200 and \
        owm_code != 230) or \
        (500 <= owm_code <= 531 and \
         owm_code != 520):
        return 2
    # Cloudy
    # 801 (few clouds)
    if 802 <= owm_code <= 804:
        return 1
    return 0

# indicators: 0: blue (clear); 1: flashing blue (clouds);
# 2: red (rain); 3: flashing red (snow/severe)
def ha_indicator(ha_condition):
    condition_map = {'clear-night' : 0,
                     'cloudy': 1,
                     'fog': 1,
                     'hail': 3,
                     'lightning': 1,
                     'lightning-rainy': 2,
                     'partlycloudy' : 1,
                     'pouring': 2,
                     'rainy': 2,
                     'snowy': 3,
                     'snowy-rainy': 3,
                     'sunny': 0,
                     'windy': 0,
                     'windy-variant': 0,
                     'exceptional': 3, }
    try:
        return condition_map[ha_condition]
    except KeyError:
        print('Condition %s not found' % ha_condition)
    return 0

# StoppableThread is from user Dolphin,
# from http://stackoverflow.com/questions/5849484/how-to-exit-a-multithreaded-program
class StoppableThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.stop_event = Event()

    def stop(self):
        if self.isAlive():
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
        #print("self._counter is %d" % self._counter)
        color_index = self._sequence[self._counter]
        #print("Color index is %d" % color_index)
        if color_index >= 0:
            turn_on_with_color(color_index)
        else:
            turn_off()
        self._counter += 1
        if self._counter >= len(self._sequence):
            self._counter = 0

def turn_on_with_color(color_index):
    BRIDGE.lights(BEACON, 'state', bri=255, sat=255, on=True,
                  xy=COLORS_XY[color_index])

def turn_off():
    BRIDGE.lights(BEACON, 'state', on=False)

def get_worst_weather():
    if USE_HA:
        return get_worst_weather_HA()
    return get_worst_weather_OWM()

def get_worst_weather_HA():
    using_today = False
    if datetime.datetime.now().hour < 12:
        using_today = True
    if using_today:
        comparedate = datetime.datetime.now().date()
    else:
        comparedate = datetime.date.today() + datetime.timedelta(days=1)

    startdatetime = datetime.datetime.combine(
        comparedate, datetime.time(6, 00, 00, 0))
    stopdatetime = datetime.datetime.combine(
        comparedate, datetime.time(18, 00, 00, 0))

    #print('Look for forecast beween %s and %s' %
    #      (str(startdatetime), str(stopdatetime)))
    headers = {'Authorization': 'Bearer %s' % HA_TOKEN,
               'content-type': 'application/json'}
    response = get(HA_WEATHER_URL, headers=headers)
    try:
        weather = json.loads(response.text)
        forecast = weather['attributes']['forecast']
    except:
        print("Could not get forecast from HA")
        return [0, -1, 'error', str(startdatetime)]
    found = False
    worst_indicator = 0
    worst_condition = ''
    worst_datetime = startdatetime
    for period in forecast:
        periodtimestamp = datetime.datetime.strptime(
            period['datetime'], "%Y-%m-%dT%H:%M:%S+00:00")
        if startdatetime <= periodtimestamp <= stopdatetime:
            period_condition = period['condition']
            period_indicator = ha_indicator(period_condition)
            #print('Considering period at %s: %s %d' %
            #      (str(periodtimestamp), period_condition, period_indicator))
            if period_indicator > worst_indicator or not found:
                worst_indicator = period_indicator
                worst_condition = period_condition
                worst_datetime = periodtimestamp
                found = True
    return [worst_indicator, -1, worst_condition, str(worst_datetime)]

def get_worst_weather_OWM():
    using_today = False
    if datetime.datetime.now().hour < 12:
        using_today = True

    if using_today:
        comparedate = datetime.datetime.now().date()
    else:
        comparedate = datetime.date.today() + datetime.timedelta(days=1)

    startdatetime = datetime.datetime.combine(
        comparedate, datetime.time(6, 00, 00, 0, LOCAL_TZ))
    stopdatetime = datetime.datetime.combine(
        comparedate, datetime.time(18, 00, 00, 0, LOCAL_TZ))

    owm = pyowm.OWM(OWM_KEY)
    forecaster = owm.three_hours_forecast_at_id(OWM_CITY_ID)
    forecast = forecaster.get_forecast()

    worst_indicator = 0
    found = False
    worst_weather = 0
    worst_code = 800
    worst_datetime = startdatetime
    for weather in forecast:
        weatherdatetime = utc_to_local(
            datetime.datetime.fromtimestamp(weather.get_reference_time('unix')))
        if startdatetime <= weatherdatetime <= stopdatetime:
            weather_code = weather.get_weather_code()
            beacon_indicator = owm_indicator(weather_code)
            if beacon_indicator > worst_indicator or not found:
                worst_indicator = beacon_indicator
                worst_weather = weather
                worst_datetime = weatherdatetime
                worst_code = weather_code
                found = True

    return [worst_indicator, worst_code, worst_weather.get_detailed_status(),
            str(worst_datetime)]

def main():
    response = BRIDGE.lights()

    if response:
        print('Connected to Hub')
    else:
        print('No lights in Hub')
        return 1

    red_sequence = [1, -1]
    blue_sequencer = [0, -1]
    red_sequencer = ColorSequencer(SLEEP_DURATION, red_sequence)
    blue_sequencerr = ColorSequencer(SLEEP_DURATION, blue_sequencer)

    ast = astral.Astral()
    location = ast[SUNSET_CITY]

    running = False
    should_run = False
    running_sequencer = None
    weather_time = None
    worst_weather = {None, None, None}

    try:
        while True:
            sunrise = location.sunrise()
            sunset = location.sunset()
            now = datetime.datetime.now(sunset.tzinfo)
            today = datetime.date.today()
            now_tz = now.tzinfo
            should_run = False
            for onoff in RUN_TIMES:
                if onoff[0] == 'sunset':
                    onstamp = sunset
                elif onoff[0] == 'sunrise':
                    onstamp = sunrise
                else:
                    ontime = datetime.datetime.strptime(
                        onoff[0], '%H:%M').time()
                    onstamp = datetime.datetime(
                        today.year, today.month, today.day,
                        ontime.hour, ontime.minute, tzinfo=now_tz)
                if onoff[1] == 'sunset':
                    offstamp = sunset
                elif onoff[1] == 'sunrise':
                    offstamp = sunrise
                else:
                    offtime = datetime.datetime.strptime(
                        onoff[1], '%H:%M').time()
                    offstamp = datetime.datetime(
                        today.year, today.month, today.day,
                        offtime.hour, offtime.minute, tzinfo=now_tz)
                if onstamp <= now <= offstamp:
                    should_run = True

            if running and should_run:
                # Re-check weather once an hour
                if (now - weather_time).total_seconds() > 60*60:
                    current_weather = worst_weather
                    try:
                        worst_weather = get_worst_weather()
                    except:
                        print('Failed to update weather')
                        worst_weather = current_weather
                    weather_time = now
                    if worst_weather != current_weather:
                        print('Weather changed; worst weather is %s'
                              % str(worst_weather))
                        if running_sequencer:
                            running_sequencer.stop()
                            turn_off()
                        if worst_weather[0] == 0:
                            turn_on_with_color(0)
                        elif worst_weather[0] == 1:
                            running_sequencer = blue_sequencerr
                            running_sequencer.start()
                            blue_sequencerr = ColorSequencer(
                                SLEEP_DURATION, blue_sequencer)
                        elif worst_weather[0] == 2:
                            turn_on_with_color(1)
                        elif worst_weather[0] == 3:
                            running_sequencer = red_sequencer
                            running_sequencer.start()
                            red_sequencer = ColorSequencer(
                                SLEEP_DURATION, red_sequence)

            if should_run and not running:
                # Get weather and start running
                try:
                    worst_weather = get_worst_weather()
                except:
                    worst_weather = [0, 800, now]
                    print("Failed to get weather; assume clear")

                print('Weather at start; worst weather is %s' % str(worst_weather))
                weather_time = now

                if worst_weather[0] == 0:
                    turn_on_with_color(0)
                elif worst_weather[0] == 1:
                    running_sequencer = blue_sequencerr
                    running_sequencer.start()
                    blue_sequencerr = ColorSequencer(SLEEP_DURATION, blue_sequencer)
                elif worst_weather[0] == 2:
                    turn_on_with_color(1)
                elif worst_weather[0] == 3:
                    running_sequencer = red_sequencer
                    running_sequencer.start()
                    red_sequencer = ColorSequencer(SLEEP_DURATION, red_sequence)
                running = True

            if running and not should_run:
                # Stop running
                if running_sequencer:
                    running_sequencer.stop()
                turn_off()
                running = False

            sys.stdout.flush()
            time.sleep(60)

    except KeyboardInterrupt:
        print('Bye!')
        if running_sequencer:
            running_sequencer.stop()
        turn_off()

main()
