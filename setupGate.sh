#!/bin/bash
#let's get neopixel set up
sudo apt-get update
sudo apt-get -y install build-essential python-dev git scons swig avrdude

#install arduino stuff
wget https://downloads.arduino.cc/arduino-1.8.5-linuxarm.tar.xz
tar -xf arduino-1.8.5-linuxarm.tar.xz --verbose
cd arduino-1.8.5
./install.sh
export PATH=$PATH:~/arduino-1.8.5
cd ..
sudo usermod -a -G dialout pi

#install LED control code
git clone https://github.com/jgarff/rpi_ws281x.git
cd rpi_ws281x

scons
cd python
sudo python setup.py install
cd ~

#let's install screen
sudo apt-get install screen

#let's get flask installed
sudo apt-get install python-pip

#let's give python permission to alter gpio pins without sudo
sudo chown pi /dev/mem

#let's get py ready for i2c
git clone git://git.drogon.net/wiringPi
cd ~/wiringPi
git pull origin
./build

####enable i2c#####

# enable I2C on Raspberry Pi
sudo echo '>>> Enable I2C'
sudo echo 'i2c-bcm2708' >> /etc/modules
sudo echo 'i2c-dev' >> /etc/modules
sudo echo 'dtparam=i2c1=on' >> /boot/config.txt
sudo echo 'dtparam=i2c_arm=on' >> /boot/config.txt
sudo sed -i 's/^blacklist spi-bcm2708/#blacklist spi-bcm2708/' /etc/modprobe.d/raspi-blacklist.conf
sudo sed -i 's/^blacklist i2c-bcm2708/#blacklist i2c-bcm2708/' /etc/modprobe.d/raspi-blacklist.conf
sudo apt-get install -y i2c-tools
####enable i2c#####

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

#lets install psutil so that we can restart our python process on update
sudo pip install psutil
sudo pip install flask-socketio
