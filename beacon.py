import sys
import time
import datetime
import zoneinfo
import json
import pytz
import holidays
import random
import astral
import astral.geocoder as geocoder
import astral.sun as ast_sun
# HA
from requests import get
# OWM
#import pyowm
import owmkey
import dateutil
from dateutil import parser

from bridge import BRIDGE
from conf import BEACON, RUN_TIMES, SLEEP_DURATION, SEQUENCES, HOLIDAYS, MORE_HOLIDAYS, Color
from sequencer import ColorSequencer

DEBUG = False
SUNSET_CITY = 'Boston'
TIMEZONE = 'America/New_York'
OWM_CITY_ID = 4945283

# HA
HA_WEATHER_URL = 'http://rosie.parkercat.org:8123/api/states/sensor.nws_hourly_forecast'
HA_WEATHER_URL_FALLBACK = 'http://rosie.parkercat.org:8123/api/states/weather.first_floor_heat'

HA_TOKEN = owmkey.get_ha_token()
USE_HA = True

# Note: provide 'owmkey.py' file that contains a function get_owm_key
# returning your own OpenWeatherMap key
OWM_KEY = owmkey.get_owm_key()

# blue, red -- better for 1st-get Hue bulbs
#COLORS_XY = [[0.2182,0.1485], [0.7,0.2986]]
# blue, red -- better for 3rd-gen Hue bulbs
COLORS_XY = [[0.1947, 0.2229], [0.6663, 0.2978]]

LOCAL_TZ = pytz.timezone(TIMEZONE)

running_sequencer = None

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
                     'hail': 4,
                     'lightning': 1,
                     'lightning-rainy': 2,
                     'partlycloudy' : 0,
                     'pouring': 2,
                     'rainy': 2,
                     'snowy': 3,
                     'snowy-rainy': 4,
                     'sunny': 0,
                     'windy': 0,
                     'windy-variant': 0,
                     'exceptional': 4, }
    try:
        return condition_map[ha_condition]
    except KeyError:
        print('Condition %s not found' % ha_condition)
    return 0

def get_color_sequence(weather_category: int, holidays=None):
    """
    Get colors based on holiday or current weather
    """
    today = datetime.datetime.today()
    if holidays and today in holidays:
        holiday = holidays[today]
        holiday_sequence = HOLIDAYS.get(holiday)
        if holiday_sequence and holiday_sequence in SEQUENCES:
            return SEQUENCES[holiday_sequence]
    weather_colors = [
        "clear", "clouds", "rain", "snow", "severe"]
    try:
        weather_color = weather_colors[weather_category]
    except Exception as e:
        print(f"Failed to get color: {e}")
        weather_color = "error"
    if weather_color not in SEQUENCES:
        print(f"Weather color {weather_color} not found")
        weather_color = "error"
    return SEQUENCES[weather_color]

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
        comparedate, datetime.time(6, 00, 00, 0, LOCAL_TZ))
    stopdatetime = datetime.datetime.combine(
        comparedate, datetime.time(18, 00, 00, 0, LOCAL_TZ))

    #print('Look for forecast beween %s and %s' %
    #      (str(startdatetime), str(stopdatetime)))
    headers = {'Authorization': 'Bearer %s' % HA_TOKEN,
               'content-type': 'application/json'}
    response = get(HA_WEATHER_URL, headers=headers)
    try:
        weather = json.loads(response.text)
        forecast = weather['attributes']['forecast']
    except Exception as e:
        # Try fallback
        response = get(HA_WEATHER_URL_FALLBACK, headers=headers)
        try:
            weather = json.loads(response.text)
            forecast = weather['attributes']['forecast']
            print("Using fallback weather provider")
        except Exception as fe:
            print(f"Could not get forecast from HA: {e}, {fe}")
            return [4, -1, 'error', str(startdatetime)]
    found = False
    worst_indicator = 0
    worst_condition = ''
    worst_datetime = startdatetime
    for period in forecast:
        periodtimestamp = dateutil.parser.isoparse(
            period['datetime'])
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

def setup_holidays():
    today = datetime.datetime.today()
    us_holidays = holidays.US(
        years=today.year, subdiv='MA',
        categories=['public', 'unofficial'], observed=True)
    for day, name in MORE_HOLIDAYS:
        try:
            func = getattr(us_holidays, f"_add_holiday_{day}")
        except AttributeError:
            func = getattr(us_holidays, f"_add_{day}")
        func(name)
    return us_holidays


def main():
    response = BRIDGE.lights()

    if response:
        print('Connected to Hub')
    else:
        print('No lights in Hub')
        return 1

    sequencer = ColorSequencer(SLEEP_DURATION, beacon=BEACON)

    location = geocoder.lookup(SUNSET_CITY, geocoder.database())
    timezone = zoneinfo.ZoneInfo(location.timezone)
    today = datetime.datetime.today()
    sun = ast_sun.sun(
        location.observer, today, tzinfo=timezone)

    us_holidays = setup_holidays()

    running = False
    should_run = False
    weather_time = None
    worst_weather = {None, None, None}
    current_sequence = None

    try:
        while True:
            sunrise = sun['sunrise']
            sunset = sun['sunset']
            now = datetime.datetime.now(sunset.tzinfo)
            today = datetime.date.today()
            now_tz = now.tzinfo
            should_run = False
            if DEBUG:
                print(f"{now=} {sunrise=} {sunset=} {RUN_TIMES=}")

            if us_holidays._year != today.year:
                # Handle year change while still running
                us_holidays = setup_holidays()

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
                if DEBUG:
                    print(f"{onstamp=} {now=} {offstamp=}")
                if onstamp <= now <= offstamp:
                    should_run = True

            if DEBUG:
                print(f"{should_run=}")
            if running and should_run:
                # Re-check weather once an hour
                current_weather = worst_weather
                if (now - weather_time).total_seconds() > 60*60:
                    try:
                        worst_weather = get_worst_weather()
                        if not worst_weather:
                            worst_weather = current_weather
                    except:
                        print('Failed to update weather')
                        worst_weather = current_weather
                    weather_time = now
                sequence = get_color_sequence(
                    worst_weather[0], holidays=us_holidays)
                if worst_weather != current_weather:
                    print('Weather changed; worst weather is %s'
                          % str(worst_weather))
                if sequence != current_sequence:
                    holiday = us_holidays.get(today)
                    if HOLIDAYS.get(holiday):
                        print(f'Override weather for {holiday=}')
                    sequencer.stop()
                    sequencer = ColorSequencer(SLEEP_DURATION)
                    sequencer.set_sequence(sequence)
                    sequencer.start()
                    current_sequence = sequence

            if should_run and not running:
                # Get weather and start running
                
                try:
                    worst_weather = get_worst_weather()
                    if not worst_weather:
                        worst_weather = [0, 800, now]
                except Exception as e:
                    worst_weather = [0, 800, now]
                    print(f"Failed to get weather({e}); assume clear")

                print('Weather at start; worst weather is %s' % str(worst_weather))
                holiday = us_holidays.get(today)
                if HOLIDAYS.get(holiday):
                    print(f'Override weather for {holiday=}')

                weather_time = now
                sequence = get_color_sequence(
                    worst_weather[0], holidays=us_holidays)
                if DEBUG:
                    print(f"{sequence=}")
                sequencer.set_sequence(sequence)
                sequencer.start()
                current_sequence = sequence
                running = True

            if running and not should_run:
                # Stop running
                if sequencer:
                    sequencer.stop(do_turn_off=True)
                running = False

            sys.stdout.flush()
            time.sleep(60)

    except KeyboardInterrupt:
        print('Bye!')
        if sequencer:
            sequencer.stop(do_turn_off=True)

if __name__ == "__main__":
    sys.exit(main())
