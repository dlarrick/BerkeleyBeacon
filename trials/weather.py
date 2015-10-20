import pywapi

#city = "West Newton, MA"
 
#this will give you a dictionary of all cities in the world with this city's name Be specific (city, country)!
#lookup = pywapi.get_location_ids(city)
 
#workaround to access last item of dictionary
#for i in lookup:
#    location_id = i
#print lookup
#print ("location_id is " + location_id)
#location_id now contains the city's code

#location_id = "USMA0515"
#weather_com_result = pywapi.get_weather_from_weather_com(location_id)
#print ("Weather.com says: It is " + weather_com_result['current_conditions']['text'].lower() + " and " + weather_com_result['current_conditions']['temperature'] + "C now in West Newton")

#print weather_com_result

#station_id = "KBED"
#noaa_result = pywapi.get_weather_from_noaa(station_id)
#print ("NOAA says it is " + noaa_result['weather'] + " and " + noaa_result['temp_f'] + "F now in Bedford")

#print noaa_result

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
yahoo_result = pywapi.get_weather_from_yahoo("02465")

now_code = int(yahoo_result['condition']['code'])
today_code = int(yahoo_result['forecasts'][0]['code'])
tomorrow_code = int(yahoo_result['forecasts'][1]['code'])

print ("Now: code " + str(now_code) + "(" + str(yahoo_codes[now_code]['code']) + " " + yahoo_codes[now_code]['description'] + ") is indicator " + str(yahoo_codes[now_code]['indicator']))

print ("Today: code " + str(today_code) + "(" + str(yahoo_codes[today_code]['code']) + " " + yahoo_codes[today_code]['description'] + ") is indicator " + str(yahoo_codes[today_code]['indicator']))

print ("Tomorrow: code " + str(tomorrow_code) + "(" + str(yahoo_codes[tomorrow_code]['code']) + " " + yahoo_codes[tomorrow_code]['description'] + ") is indicator " + str(yahoo_codes[tomorrow_code]['indicator']))
