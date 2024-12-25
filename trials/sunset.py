from astral import *
from datetime import *

runTimes = [['sunset','23:00'], ['6:00','sunrise']]

a = Astral()
location = a['Boston']
print ('Information for ' + location.name + " " + location.region)
sunset = location.sunset()
sunrise = location.sunrise()
now = datetime.now(sunset.tzinfo)
today = date.today()
tz = now.tzinfo
print ('Today is ' + str(today))
print ('Sunrise today at ' + str(sunset))
print ('Sunset today at ' + str(sunset))
print ('TZ is ' + str(tz))

for onoff in runTimes:
    if onoff[0] == 'sunset':
        onstamp = sunset
    elif onoff[0] == 'sunrise':
        onstamp = sunrise
    else:
        ontime = datetime.strptime(onoff[0], '%H:%M').time()
        onstamp = datetime(today.year, today.month, today.day, ontime.hour,
                           ontime.minute, tzinfo=tz)
    if onoff[1] == 'sunset':
        offstamp = sunset
    elif onoff[1] == 'sunrise':
        offstamp = sunrise
    else:
        offtime = datetime.strptime(onoff[1], '%H:%M').time()
        offstamp = datetime(today.year, today.month, today.day, offtime.hour,
                            offtime.minute, tzinfo=tz)
    print ('Run from ' + str(onstamp) + ' to ' + str(offstamp))
    if (now >= onstamp):
        print 'After onstamp'
    if (now <= offstamp):
        print 'Before offstamp'


    
