#!/usr/bin/python
from beautifulhue.api import Bridge

bridge = Bridge(device={'ip':'192.168.1.24'}, user={'name':'1cd503803c2588ef8ea97d02a2520df'})

resource = {'which':'all', 'verbose':True}
bridge.light.get(resource)
