#!/bin/bash
sudo rm -rf dronespacepigates/
git clone git@gitlab.com:planetarymotion/dronespacepigates.git
cd dronespacepigates/
git checkout develop
sudo reboot now
