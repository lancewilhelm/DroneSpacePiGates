#!/bin/bash
ps auxww | grep 'webapp.py' | awk '{print $2}' | xargs kill
ps auxww | grep 'gateServer.py' | awk '{print $2}' | xargs kill
ps auxww | grep '[c]elery worker' | awk '{print $2}' | xargs kill
ps auxww | grep 'redis-server' | awk '{print $2}' | xargs kill
