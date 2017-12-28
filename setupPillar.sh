#!/bin/bash
#let's get neopixel set up
sudo apt-get update
sudo apt-get install build-essential python-dev git scons swig
git clone https://github.com/jgarff/rpi_ws281x.git
cd rpi_ws281x
scons
cd python
sudo python setup.py install

#let's install screen
sudo apt-get install screen

#let's get flask installed
sudo apt-get install python-pip
sudo pip install Flask

#let's give python permission to alter gpio pins without sudo
sudo chown pi /dev/mem

#lets install psutil so that we can restart our python process on update
sudo pip install psutil &&
exit

#copy keys to root
sudo cp -r ~/dronespacepigates/.ssh/ ~/
sudo mkdir /root/.ssh/
sudo cp ~/.ssh/id_rsa /root/.ssh/
sudo cp ~/.ssh/id_rsa.pub /root/.ssh/

#setup cron for @reboot
sudo chmod 400 /root/.ssh/id_rsa

sudo rm /var/spool/cron/crontabs/root
sudo cp ~/dronespacepigates/crontabScript /var/spool/cron/crontabs/root
sudo chmod 600 /var/spool/cron/crontabs/root
