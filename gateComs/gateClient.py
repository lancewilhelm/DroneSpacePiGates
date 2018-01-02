import DSElement
import sys
import argparse

#lets allow the user to call this script with options
parser = argparse.ArgumentParser(description="Starts a gate client")
parser.add_argument('--h', type=str, help="-h: help\n-l: \n-d: ")
parser.add_argument('-l', default="medium", help="log level (high,medium,low,off)")
parser.add_argument('-f', default="/home/pi/DSElement.log", help="location to save the log file")
parser.add_argument('-d', default=False, help="developer mode (1,0)")
parser.add_argument('-ledCount', default=337, help="the number of leds this device controls (integer)")
parser.add_argument('-i', default="gatemaster", help="the ip address of the gateServer")
parser.add_argument('-p', default=13246, help="gateServer port")
parser.add_argument('-c', default="green", help="the color of the element before we connect to the server")
args = parser.parse_args()
#all options have defaults, so we don't HAVE to provide them when calling the script

print("Starting gate client with arguments "+str(args))
DSElement.gate(args).start()
