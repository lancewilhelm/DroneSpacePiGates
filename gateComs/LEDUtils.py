# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time

from neopixel import *

import argparse
import signal
import sys

def signal_handler(signal, frame):
        colorWipe(self.strip, Color(0,0,0))
        sys.exit(0)

def opt_parse():
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', action='store_true', help='clear the display on exit')
        args = parser.parse_args()
        if args.c:
                signal.signal(signal.SIGINT, signal_handler)

# LED strip configuration:
LED_COUNT      = 337      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering


class LEDStrip:
    def __init__(self):
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
        # Intialize the library (must be called once before other functions).
        strip.begin()
        # Process arguments
        opt_parse()
    # Define functions which animate LEDs in various ways.
    def clearPixels():
        #print ('Clearing')
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0,0,0))
        self.strip.show()

    def allRed():
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(255,0,0))
        self.strip.show()

    def allOrange():
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(255,127,0))
        self.strip.show()

    def allYellow():
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(125,125,0))
        self.strip.show()

    def allGreen():
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0,255,0))
        self.strip.show()

    def allBlue():
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0,0,255))
        self.strip.show()

    def allIndigo():
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(127,0,255))
        self.strip.show()

    def allPurple():
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(50,0,50))
        self.strip.show()

    def flashYellow():
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(125,125,0))
        self.strip.show()
        time.sleep(1)
        clearPixels(self.strip)
        time.sleep(1)

    def chasing():
        #clearPixels(strip)
        #Purple
        for x in range(0,self.strip.numPixels(), 1):
            #print x
            endPixel = x + 50
            #purple
            for i in range(x,endPixel):
                self.strip.setPixelColor(i % self.strip.numPixels(), Color(255,0,255))
                #Serial.println("setting pixel colors for 50");

            #green
            for i in (x+(self.strip.numPixels()/2),endPixel+(self.strip.numPixels()/2)):
                self.strip.setPixelColor(i % self.strip.numPixels(), Color(100,255,0))
                #Serial.println("setting pixel colors for 50");

            #clear purple
            for i in range(1,5):
                self.strip.setPixelColor(x - i, Color(0,0,0))

            #clear green
            for i in range(1,5):
                self.strip.setPixelColor((x+(self.strip.numPixels()/2) - i) % self.strip.numPixels(), Color(0,0,0))

            self.strip.show()
            #print ('sleep')
            time.sleep(0.005)

    def colorWipe(color, wait_ms=50):
    	"""Wipe color across display a pixel at a time."""
    	for i in range(self.strip.numPixels()):
    		self.strip.setPixelColor(i, color)
    		self.strip.show()
    		time.sleep(wait_ms/1000.0)

    def theaterChase(color, wait_ms=50, iterations=1):
    	"""Movie theater light style chaser animation."""
    	for j in range(iterations):
    		for q in range(3):
    			for i in range(0, self.strip.numPixels(), 3):
    				self.strip.setPixelColor(i+q, color)
    			self.strip.show()
    			time.sleep(wait_ms/1000.0)
    			for i in range(0, self.strip.numPixels(), 3):
    				self.strip.setPixelColor(i+q, 0)

    def wheel(pos):
    	"""Generate rainbow colors across 0-255 positions."""
    	if pos < 85:
    		return Color(pos * 3, 255 - pos * 3, 0)
    	elif pos < 170:
    		pos -= 85
    		return Color(255 - pos * 3, 0, pos * 3)
    	else:
    		pos -= 170
    		return Color(0, pos * 3, 255 - pos * 3)

    def rainbow(wait_ms=20, iterations=1):
    	"""Draw rainbow that fades across all pixels at once."""
    	for j in range(256*iterations):
    		for i in range(self.strip.numPixels()):
    			self.strip.setPixelColor(i, wheel((i+j) & 255))
    		self.strip.show()
    		time.sleep(wait_ms/1000.0)

    def rainbowCycle(wait_ms=20, iterations=1):
    	"""Draw rainbow that uniformly distributes itself across all pixels."""
    	for j in range(256*iterations):
    		for i in range(self.strip.numPixels()):
    			self.strip.setPixelColor(i, wheel((int(i * 256 / self.strip.numPixels()) + j) & 255))
    		self.strip.show()
    		time.sleep(wait_ms/1000.0)

    def theaterChaseRainbow(wait_ms=50):
    	"""Rainbow movie theater light style chaser animation."""
    	for j in range(256):
    		for q in range(3):
    			for i in range(0, self.strip.numPixels(), 3):
    				self.strip.setPixelColor(i+q, wheel((i+j) % 255))
    			self.strip.show()
    			time.sleep(wait_ms/1000.0)
    			for i in range(0, self.strip.numPixels(), 3):
    				self.strip.setPixelColor(i+q, 0)
