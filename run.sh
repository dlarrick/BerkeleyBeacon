#!/bin/bash
#python3 -m venv venv
source /home/doug/Git/BerkeleyBeacon/venv/bin/activate
#pip3 install -r requirements.txt
nohup /home/doug/Git/BerkeleyBeacon/venv/bin/python beacon.py >> beacon.log &
