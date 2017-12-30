import DSElement
import sys
import argparse

#lets allow the user to call this script with options
parser = argparse.ArgumentParser(description="Starts a gate client")
parser.add_argument('--h', type=str, help="-h: help\n-l: \n-d: ")
parser.add_argument('-l', type=str, default="off", help="log level (high,medium,low,off)")
parser.add_argument('-f', type=str, default="/home/pi/DSElement.log", help="location to save the log file")
parser.add_argument('-d', type=bool, default=False, help="developer mode (1,0)")
parser.add_argument('-ledCount', type=int, default=527, help="the number of leds this device controls (integer)")
parser.add_argument('-i', type=str, default="gatemaster", help="the ip address of the gateServer")
parser.add_argument('-p', type=int, default=13246, help="gateServer port")
parser.add_argument('-c', type=str, default="green", help="the color of the element before we connect to the server")
args = parser.parse_args()
#all options have defaults, so we don't HAVE to provide them when calling the script

print("Starting pillar client")
DSElement.pillar(args).start()
