#!/bin/bash
redis.sh & 
cd webapp
celery -A webapp.celery worker &
sudo python webapp.py
