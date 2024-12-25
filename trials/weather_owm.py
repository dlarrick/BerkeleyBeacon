import pyowm
import owmkey
import datetime
import pytz

sunsetCity = 'Boston'

OWM_KEY = owmkey.get_owm_key()

owm = pyowm.OWM(OWM_KEY)

# You have a pro subscription? Use:
# owm = pyowm.OWM(API_key='your-API-key', subscription_type='pro')

# Will it be sunny tomorrow at this time in Milan (Italy) ?
#forecast = owm.daily_forecast("Milan,it")
#tomorrow = pyowm.timeutils.tomorrow()
#forecast.will_be_sunny_at(tomorrow)  # Always True in Italy, right? ;-)

# Search for current weather in London (UK)
#observation = owm.weather_at_place('London,uk')
#w = observation.get_weather()
#print(w)                      # <Weather - reference time=2013-12-18 09:20, 
                              # status=Clouds>

# Weather details
#w.get_wind()                  # {'speed': 4.6, 'deg': 330}
#w.get_humidity()              # 87
#w.get_temperature('celsius')  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}

# Search current weather observations in the surroundings of 
# lat=22.57W, lon=43.12S (Rio de Janeiro, BR)
#observation_list = owm.weather_around_coords(-22.57, -43.12)

cityId = 4945283

forecaster = owm.three_hours_forecast_at_id(cityId)
#forecaster = owm.daily_forecast_at_id(cityId,limit=2)
forecast = forecaster.get_forecast()

#print forecast.get_location().to_JSON()
#print forecast.to_JSON()
#for weather in forecast:
#    print (weather.get_reference_time('iso'),weather.get_detailed_status(),weather.get_weather_code())


rainlist = forecaster.when_rain()
snowlist = forecaster.when_snow()
cloudlist = forecaster.when_clouds()
print (len(cloudlist),len(rainlist), len(snowlist))
# Codes here: http://openweathermap.org/weather-conditions

#tomorrow = pyowm.timeutils.tomorrow()
#forecast.will_be_sunny_at(tomorrow)  # Always True in Italy, right? ;-)

# What we really want:
# Before noon local time, use the forecasts for today
# After noon use the forecasts for tomorrow
# Cateorize each forecast into the 4 indicators: clear, cloudy, rainy, snowy
# Return the worst indicator

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

local_tz = pytz.timezone('America/New_York') # use your local timezone name here

def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt) # .normalize might be unnecessary

usingToday = False
if (datetime.datetime.now().hour < 12):
    usingToday = True

if (usingToday):
    print "using Today:"
    comparedate = datetime.datetime.now().date()
else:
    print "using Tomorrow:"
    comparedate = datetime.date.today() + datetime.timedelta(days=1)

startdatetime = datetime.datetime.combine(comparedate, datetime.time(6,00,00,0,local_tz))
stopdatetime = datetime.datetime.combine(comparedate, datetime.time(18,00,00,0,local_tz))

worst_indicator = 0
found = False
worst_weather = 0
for weather in forecast:
    weatherdatetime = utc_to_local(datetime.datetime.fromtimestamp(weather.get_reference_time('unix')))
    if (weatherdatetime >= startdatetime and weatherdatetime <= stopdatetime):
        weather_code = weather.get_weather_code()
        beacon_indicator = owm_indicator(weather_code)
        if (beacon_indicator > worst_indicator or
            found == False):
            worst_indicator = beacon_indicator
            worst_weather = weather
            found = True
        print (weather.get_reference_time('iso'),weather.get_detailed_status(),weather_code,beacon_indicator)

print ("Worst indicator is " + str(worst_indicator) + " " + worst_weather.get_detailed_status())
