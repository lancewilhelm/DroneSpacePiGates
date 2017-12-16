from flask import Flask, request, render_template
import DSClient
#from blink import Blink
#import leddimmer as l
#from getButtonStatus import getButtonStatus
app = Flask(__name__)

@app.route("/", methods=['POST','GET'])
def index():
    if request.method == 'POST':
      color = request.form['color']
      if color == 'rainbow':
        rainbow(strip)
        return 'rainbow'
      elif color == 'red':
        #allRed(strip)
        DSClient.sendGateUpdate("localhost",13246,[255,0,0])
        return 'red'
      elif color == 'chasing':
        #chasing(strip)

        return 'chasing'
      elif color == 'green':
        #allGreen(strip)
        DSClient.sendGateUpdate("localhost",13246,[0,255,0])
        return 'green'
      elif color == 'yellow':
        DSClient.sendGateUpdate("localhost",13246,"yellow")
        #flashYellow(strip)
        return 'yellow'
    else:
        return render_template('index.html')

if __name__ == "__main__":
  # Create NeoPixel object with appropriate configuration.
  #strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
  # Intialize the library (must be called once before other functions).
  #strip.begin()

  app.run(host='0.0.0.0', port=80, debug=True)
