#!/bin/bash

# Wait a bit and turn Philips Hue bulbs back off
case $NOTIFYTYPE in
    ONLINE)
	# Just came back online... turn off all Hue bulbs
	sleep 30
	curl -X PUT -H "Content-Type: application/json" -d '{"on":false}' -o /dev/null -s http://hue.parkercat.org/api/1cd503803c2588ef8ea97d02a2520df/lights/1/state
	curl -X PUT -H "Content-Type: application/json" -d '{"on":false}' -o /dev/null -s http://hue.parkercat.org/api/1cd503803c2588ef8ea97d02a2520df/lights/2/state
	curl -X PUT -H "Content-Type: application/json" -d '{"on":false}' -o /dev/null -s http://hue.parkercat.org/api/1cd503803c2588ef8ea97d02a2520df/lights/3/state
    ;;
    ONBATT)
    ;;

exit 0
