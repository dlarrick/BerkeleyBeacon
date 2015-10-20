import sys 
from beautifulhue.api import Bridge
username = '1cd503803c2588ef8ea97d02a2520df'
bridge = Bridge(device={'ip':'192.168.1.24'}, user={'name':username})

def createConfig():
  created = False
  print 'Press the button on the Hue bridge'
  while not created:
     resource = {'user':{'devicetype': 'beautifulhuetest', 'name': username}}
     response = bridge.config.create(resource)['resource']
     if 'error' in response[0]:
        if response[0]['error']['type'] != 101:
          print 'Unhandled error creating configuration on the Hue'
          sys.exit(response)
     else:
        created = True

def getSystemData():
  resource = {'which':'system'}
  return bridge.config.get(resource)['resource']

def main():
  response = getSystemData()

  if 'lights' in response:
     print 'Connected to the Hub'
     print response['lights']
  elif 'error' in response[0]:
     error = response[0]['error']
     if error['type'] == 1:
        createConfig()
        main()

main()
