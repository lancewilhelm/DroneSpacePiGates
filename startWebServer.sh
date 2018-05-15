#!/bin/bash
./redis.sh &
cd webapp
celery -A webapp.celery worker &
sudo python webapp.py &
cd ../gateComs
python gateServer.py -l medium -f DSServer.log &
