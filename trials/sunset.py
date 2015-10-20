from astral import *
a = Astral()
location = a['Boston']
print ('Information for ' + location.name + " " + location.region)
sunset = location.sunset()
print ('Sunset today at ' + str(sunset))
