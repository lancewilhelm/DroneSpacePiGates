#include <Wire.h>

// Node Setup -- Set the i2c address here
// Node 1 = 8, Node 2 = 10, Node 3 = 12, Node 4 = 14
// Node 5 = 16, Node 6 = 18, Node 7 = 20, Node 8 = 22

const int initLength = 100;

const int deviceNumber = 4;
int pilotNumber = 8;
const int averaging = 3;
const int slaveSelectPins[] = {10,9,8,7,6,5,4,3}; // Setup data pins for rx5808 comms
const int spiDataPin = 11;
const int spiClockPin = 13;
const int rssiPins[] = {0,1,2,3,4,5,6,7};
int rssiOffsets[] = {0,0,0,0,0,0,0,0};


//let's define some popular channel maps
//if you are using something other than these, reconsider your life choices
const int imd5[] = {5685,5760,5800,5860,5905};
const int imd6[] = {5645,5685,5760,5800,5860,5905};
const int raceband[] = {5658,5732,5806,5880,5860,5905,5800,5800};

#define READ_ADDRESS 0x00
#define READ_FREQUENCY 0x03
#define READ_LAP_STATS 0x05
#define READ_CALIBRATION_THRESHOLD 0x15
#define READ_CALIBRATION_MODE 0x16
#define READ_CALIBRATION_OFFSET 0x17
#define READ_TRIGGER_THRESHOLD 0x18
#define READ_FILTER_RATIO 0x19

#define WRITE_FREQUENCY 0x51
#define WRITE_CALIBRATION_THRESHOLD 0x65
#define WRITE_CALIBRATION_MODE 0x66
#define WRITE_CALIBRATION_OFFSET 0x67
#define WRITE_TRIGGER_THRESHOLD 0x68
#define WRITE_FILTER_RATIO 0x69

struct {
  uint16_t volatile vtxFreqs[8] = {5658,5732,5806,5880,5860,5905,5800,5800};
  // Subtracted from the peak rssi during a calibration pass to determine the trigger value
  uint16_t volatile calibrationOffset[8] = {8,8,8,8,8,8,8,8};
  // Rssi must fall below trigger - settings.calibrationThreshold to end a calibration pass
  uint16_t volatile calibrationThreshold = 95;
  // Rssi must fall below trigger - settings.triggerThreshold to end a normal pass
  uint16_t volatile triggerThreshold = 40;
  uint8_t volatile filterRatio = 10;
  float volatile filterRatioFloat = 0.0f;
} settings;

struct {
  uint16_t trigger = 150; //value at which we will consider a pass initiated
  uint16_t reset = 110; //value below which we will consider the pass complete
  uint16_t noiseFloor = 0; //this is the rssi initially read for a period of time before any quad has been powered on
  uint16_t frequency = raceband[0]; //the frequency this device is listening on
  uint16_t passPeakTimestamp; //this is the timestamp of the maximum value observed from trigger to reset
  uint16_t channelNumber = 0;
  uint16_t rssi;
} rxModule;

struct {
  int completedLaps = 0; //number of laps this pilot has completed
  int crossTimes[] = {}; //a list of timestamps of each start/finish pass
  uint16_t frequency = raceband[0]; //the frequency this pilot is broadcasting on
} pilot;

//create an array of rx8508 modules
struct rxModule modules[deviceNumber] = {
  {150,110,0,raceband[0],0,0,0}
  };
//create an array of pilots
struct pilot pilots[pilotNumber] = {
  {0,{},raceband[0]},
  {0,{},raceband[0]},
  {0,{},raceband[0]},
  {0,{},raceband[0]},
  {0,{},raceband[0]},
  {0,{},raceband[0]},
  {0,{},raceband[0]},
  {0,{},raceband[0]}
  };

void setPilotChannels(uint16_t[] channels){
  if(sizeof(channels)==pilotNumber){
    Serial.println("we have a full heat")
    if(pilotNumber==deviceNumber){
      for(int i=0;i<pilotNumber;i++){
        pilot = pilots[i];
        pilot.frequency = channels[i];
        Serial.println("setting pilot ",i," to channel ",pilot.frequency);
      }
    }else if(pilotNumber>deviceNumber){ //we are tracking more pilots than we have modules for
      //let's distribute the devices as evenly as possible over the channels
      //later we'll scroll through the the modules up the channel as needed
      int spacing = pilotNumber/deviceNumber-(pilotNumber % deviceNumber); //FIX MEEEEEE
      Serial.print("spacing is");
      Serial.println(spacing);
      modules[0] = channels[0]; //first device
      int nextChannel = 0;
      int lastChannel = channels[sizeof(channels)-1];
      for(int i=0;i<sizeof(channels);i++){
        if(nextChannel==i){
          modules[i].frequency = channel[i];
          nextChannel = nextChannel+spacing;
        }
        if(nextChannel>channels[sizeof(channels)-1]){ //if we are at the end
          modules[i].frequency = lastChannel;
        }
      }

    }
  }else if(sizeof(channels)==pilotNumber){
    Serial.println("we don't have a full heat\n using custom channel map");
  }else{
    Serial.println("too many pilots for this channel map") //you might be trying to run 8 pilots on imd5 or imd6
  }
}

// Define vtx frequencies in mhz and their hex code for setting the rx5808 module
int vtxFreqTable[] = {
  5865, 5845, 5825, 5805, 5785, 5765, 5745, 5725, // Band A
  5733, 5752, 5771, 5790, 5809, 5828, 5847, 5866, // Band B
  5705, 5685, 5665, 5645, 5885, 5905, 5925, 5945, // Band E
  5740, 5760, 5780, 5800, 5820, 5840, 5860, 5880, // Band F
  5658, 5695, 5732, 5769, 5806, 5843, 5880, 5917  // Band C / Raceband
};

uint16_t vtxHexTable[] = {
  0x2A05, 0x299B, 0x2991, 0x2987, 0x291D, 0x2913, 0x2909, 0x289F, // Band A
  0x2903, 0x290C, 0x2916, 0x291F, 0x2989, 0x2992, 0x299C, 0x2A05, // Band B
  0x2895, 0x288B, 0x2881, 0x2817, 0x2A0F, 0x2A19, 0x2A83, 0x2A8D, // Band E
  0x2906, 0x2910, 0x291A, 0x2984, 0x298E, 0x2998, 0x2A02, 0x2A0C, // Band F
  0x281D, 0x288F, 0x2902, 0x2914, 0x2987, 0x2999, 0x2A0C, 0x2A1E  // Band C / Raceband
};

// Defines for fast ADC reads
#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))

// Initialize program
void setup() {
  Serial.begin(115200);

  while (!Serial) {
  }; // Wait for the Serial port to initialise

  setPilotChannels(raceband);

  // set ADC prescaler to 16 to speedup ADC readings
  sbi(ADCSRA,ADPS2);
  cbi(ADCSRA,ADPS1);
  cbi(ADCSRA,ADPS0);
  pinMode (spiDataPin, OUTPUT);
  pinMode (spiClockPin, OUTPUT);
  for (int i = 0; i < deviceNumber; i++) {
    pinMode (slaveSelectPins[i], OUTPUT); // RX5808 comms
    digitalWrite(slaveSelectPins[i], HIGH);
    setRxModule(settings.vtxFreqs[i],slaveSelectPins[i]);
  }
  for (int i = 0; i < deviceNumber; i++){ //we need to set all the pins low now
    digitalWrite(slaveSelectPins[i],LOW);
  }

  //let's initialize our offset
  for(int y=0;y<deviceNumber;y++){
    for(int x=0;x<initLength;x++){
      rssiOffsets[y] += getRSSIAvg(rssiPins[y]);
    }
    rssiOffsets[y] = rssiOffsets[y]/initLength;
  }

}

void addLap()

// Functions for the rx5808 module
void SERIAL_SENDBIT1() {
  digitalWrite(spiClockPin, LOW);
  delayMicroseconds(300);
  digitalWrite(spiDataPin, HIGH);
  delayMicroseconds(300);
  digitalWrite(spiClockPin, HIGH);
  delayMicroseconds(300);
  digitalWrite(spiClockPin, LOW);
  delayMicroseconds(300);
}
void SERIAL_SENDBIT0() {
  digitalWrite(spiClockPin, LOW);
  delayMicroseconds(300);
  digitalWrite(spiDataPin, LOW);
  delayMicroseconds(300);
  digitalWrite(spiClockPin, HIGH);
  delayMicroseconds(300);
  digitalWrite(spiClockPin, LOW);
  delayMicroseconds(300);
}
void SERIAL_SLAVE_LOW(int pin) {
  delayMicroseconds(100);
  digitalWrite(pin,LOW);
  delayMicroseconds(100);
}
void SERIAL_SLAVE_HIGH(int pin) {
  delayMicroseconds(100);
  digitalWrite(pin,HIGH);
  delayMicroseconds(100);
}

// Set the frequency given on the rx5808 module
void setRxModule(int frequency,int pin) {
  uint8_t i; // Used in the for loops
  Serial.print("settings device at pin ");
  Serial.print(pin);
  Serial.print(" to ");
  Serial.print(frequency);
  Serial.println(" mHz ");
  uint8_t index; // Find the index in the frequency lookup table
  for (i = 0; i < sizeof(vtxFreqTable); i++) {
    if (frequency == vtxFreqTable[i]) {
      index = i;
      break;
    }
  }

  uint16_t vtxHex; // Get the hex value to send to the rx module
  vtxHex = vtxHexTable[index];

  // bit bash out 25 bits of data / Order: A0-3, !R/W, D0-D19 / A0=0, A1=0, A2=0, A3=1, RW=0, D0-19=0
  SERIAL_SLAVE_HIGH(pin);
  delay(2);
  SERIAL_SLAVE_LOW(pin);
  SERIAL_SENDBIT0();
  SERIAL_SENDBIT0();
  SERIAL_SENDBIT0();
  SERIAL_SENDBIT1();
  SERIAL_SENDBIT0();

  for (i = 20; i > 0; i--) SERIAL_SENDBIT0(); // Remaining zeros

  SERIAL_SLAVE_HIGH(pin); // Clock the data in
  delay(2);
  SERIAL_SLAVE_LOW(pin);

  // Second is the channel data from the lookup table, 20 bytes of register data are sent, but the
  // MSB 4 bits are zeros register address = 0x1, write, data0-15=vtxHex data15-19=0x0
  SERIAL_SLAVE_HIGH(pin);
  SERIAL_SLAVE_LOW(pin);

  SERIAL_SENDBIT1(); // Register 0x1
  SERIAL_SENDBIT0();
  SERIAL_SENDBIT0();
  SERIAL_SENDBIT0();

  SERIAL_SENDBIT1(); // Write to register

  // D0-D15, note: loop runs backwards as more efficent on AVR
  for (i = 16; i > 0; i--) {
    if (vtxHex & 0x1) { // Is bit high or low?
      SERIAL_SENDBIT1();
    }
    else {
      SERIAL_SENDBIT0();
    }
    vtxHex >>= 1; // Shift bits along to check the next one
  }

  for (i = 4; i > 0; i--) // Remaining D16-D19
    SERIAL_SENDBIT0();

  SERIAL_SLAVE_HIGH(pin); // Finished clocking data in
  delay(2);


  digitalWrite(spiClockPin, LOW);
  digitalWrite(spiDataPin, LOW);
}

float refreshRssi(){
  int total = analogRead(slave);
}

// Main loop
void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(50);
  digitalWrite(LED_BUILTIN, LOW);
  delay(50);

  //Serial.println();
  Serial.println("]");
}
