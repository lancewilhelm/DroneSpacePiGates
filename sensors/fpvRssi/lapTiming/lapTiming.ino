#include <Wire.h>

// Node Setup -- Set the i2c address here
// Node 1 = 8, Node 2 = 10, Node 3 = 12, Node 4 = 14
// Node 5 = 16, Node 6 = 18, Node 7 = 20, Node 8 = 22

const int16_t initLength = 100;

const int deviceNumber = 4;
const int pilotNumber = 4;
const int averaging = 3;
const int spiDataPin = 11;
const int spiClockPin = 13;

int rssiOffsets[] = {0,0,0,0,0,0,0,0};
int rxLoop = -1;
const int enterThreshold = 125;
const int exitThreshold = 90;
unsigned long raceStart = millis();

//these are the states we'll use to let our loop know what a given RX is doing atm
#define CALIBRATE 0          //the moments while a module is discovering its noise floor
#define STANDBY 1            //the moments before a race starts
#define START 2              //the moment when the race starts
#define FAR 3                //the moments while a quad is out of the bubble
#define ENTER 4              //the moments while quad passes through the bubble
#define PASS 5               //the moment an rssi peaks inside the bubble
#define EXIT 6               //the moment when a quad exits the bubble
#define CHANNEL_HOP 9        //the moments while a module stablizes after a channel change. this should only happen when a quad is out of the bubble
#define FINISHED 10          //the moment when the race is completed
#define SET_ENTER_THRESH 11  //the moment we want to change the enter threshold
#define SET_EXIT_THRESH 12   //the moment we want to change the exit threshold
#define SET_MULTIPLIER 13    //the moment we want to change the rssi multiplier
#define COMMAND_START 96     //the moment when we start listening for a command
#define COMMAND_ID 97        //the moment when we start listening for a command
#define COMMAND_PARAM 98     //the moments when we are listening for command parameter
#define COMMAND_RX_ID 99     //the moments when we are listening for command module id

//used for serial communication
int8_t currentCommandState = -1;     //this should only ever be set to one of our command states (COMMAND_START,COMMAND_ID,COMMAND_PARAM)
int8_t currentCommand = -1;          //this should only be set to one of our moduel states
int8_t currentCommandRx = -1;        //this should be the id of one of our modules
int8_t currentCommandParam = -1;     //this should be the data needed to complete the command

//let's define some popular channel maps
//if you are using something other than these, reconsider your life choices
#define IMD5 {5685,5760,5800,5860,5905}
#define IMD6 {5645,5685,5760,5800,5860,5905}
#define RACEBAND {5658,5695,5732,5769,5843,5905,5880,5917}
#define RACEBAND_ODDS {5658,5732,5843,5880}
#define RACEBAND_EVENS {5695,5769,5905,5917}

struct {
  uint16_t channel[8] = raceband;
  uint16_t volatile rssi[8] = {0,0,0,0,0,0,0,0};
  uint16_t rssiMultiplier[8] = {1,1,1,1,1,1,1,1};
  // Subtracted from the peak rssi during a calibration pass to determine the trigger value
  uint16_t volatile noiseFloor[8] = {0,0,0,0,0,0,0,0};
  // Rssi must fall below trigger - settings.calibrationThreshold to end a calibration pass
  unsigned long maxRssiTime[8] = {0,0,0,0,0,0,0,0};
  uint16_t volatile maxRssi[8] = {0,0,0,0,0,0,0,0};
  // Setup data pins for rx5808 comms
  unsigned long lapStartTime[8] = {raceStart,raceStart,raceStart,raceStart,raceStart,raceStart,raceStart,raceStart};
  uint8_t slaveSelectPins[8] = {10,9,8,7,6,5,4,3};
  uint8_t rssiPins[8] = {0,1,2,3,4,5,6,7};
  uint8_t state[8] = {START,START,START,START,START,START,START,START};
} rxModules;


// Define vtx frequencies in mhz and their hex code for setting the rx5808 module
uint16_t vtxFreqTable[] = {
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

  //setupRace(rxModules.channel);

  //set ADC prescaler to 16 to speedup ADC readings
  sbi(ADCSRA,ADPS2);
  cbi(ADCSRA,ADPS1);
  cbi(ADCSRA,ADPS0);
  pinMode (spiDataPin, OUTPUT);
  pinMode (spiClockPin, OUTPUT);

  for (int i = 0; i < deviceNumber; i++) {
    Serial.print("setting channel for module on pin");
    Serial.print(rxModules.slaveSelectPins[i]);
    Serial.print(" to ");
    Serial.println(rxModules.channel[i]);
    pinMode (rxModules.slaveSelectPins[i], OUTPUT); // RX5808 comms
    setRxModule(rxModules.channel[i],rxModules.slaveSelectPins[i]);
    digitalWrite(rxModules.slaveSelectPins[i],HIGH);
  }

  for (int i = 0; i < deviceNumber; i++){ //we need to set all the pins low now
    digitalWrite(rxModules.slaveSelectPins[i], LOW);
  }
  digitalWrite(spiClockPin, LOW);
  digitalWrite(spiDataPin, LOW);

  calibrateModules();
  startRace();
}

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

void calibrateModules(){

  for(int y=0;y<deviceNumber;y++){
    updateRxState(y,CALIBRATE);
    for(int x=0;x<initLength;x++){
      digitalWrite(LED_BUILTIN, HIGH);
      rxModules.noiseFloor[y] += analogRead(rxModules.rssiPins[y]);
      digitalWrite(LED_BUILTIN, LOW);
      delay(10);
    }
    rxModules.noiseFloor[y] = rxModules.noiseFloor[y]/initLength;
    updateRxState(y,STANDBY);
  }
}

// Set the frequency given on the rx5808 module
void setRxModule(int frequency, int slaveSelectPin) {
  uint8_t i; // Used in the for loops

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
  SERIAL_SLAVE_HIGH(slaveSelectPin);
  delay(2);
  SERIAL_SLAVE_LOW(slaveSelectPin);
  SERIAL_SENDBIT0();
  SERIAL_SENDBIT0();
  SERIAL_SENDBIT0();
  SERIAL_SENDBIT1();
  SERIAL_SENDBIT0();

  for (i = 20; i > 0; i--) SERIAL_SENDBIT0(); // Remaining zeros

  SERIAL_SLAVE_HIGH(slaveSelectPin); // Clock the data in
  delay(2);
  SERIAL_SLAVE_LOW(slaveSelectPin);

  // Second is the channel data from the lookup table, 20 bytes of register data are sent, but the
  // MSB 4 bits are zeros register address = 0x1, write, data0-15=vtxHex data15-19=0x0
  SERIAL_SLAVE_HIGH(slaveSelectPin);
  SERIAL_SLAVE_LOW(slaveSelectPin);

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

  SERIAL_SLAVE_HIGH(slaveSelectPin); // Finished clocking data in
  delay(2);
}

String readSerial(){
  String readString;
  while (Serial.available()) {
    char c = Serial.read();  //gets one byte from serial buffer
    readString += c; //makes the string readString
    delay(2);  //slow looping to allow buffer to fill with next character
  }
  return readString;
}

void handleSerialData(String dataString){
  if (dataString.length() >0){
    int data = dataString.toInt();
    //let's handle the data based on what state we are in
    //serial data should be as follows
    //1. indicate that we should handle a message by sending COMMAND_START
    //2. send the id of the module we are refering to (-1 if all modules)
    //3. send the command to be run on the module(s)
    //4. send any parameter needed to run the command
    switch (currentCommandState) {
      case -1:
        if(data==COMMAND_START){
          currentCommandState = COMMAND_START;
        }
      case COMMAND_START:
        currentCommandState = COMMAND_ID;
        break;
      case COMMAND_ID:
        currentCommand = data;
        currentCommandState = COMMAND_RX_ID;
        break;
      case COMMAND_RX_ID:
        currentCommandRx = data;
        currentCommandState = COMMAND_PARAM;
        break;
      case COMMAND_PARAM:
        currentCommandParam = data;
        //run the command
        if(currentCommandRx == -1){
          for(int i=0;i < deviceNumber;i++){
            handleCommand(currentCommand,i,currentCommandParam);
          }
        }else{
          handleCommand(currentCommand,currentCommandRx,currentCommandParam);
        }
        //reset everything
        currentCommandState = -1;
        currentCommand = -1;
        currentCommandRx = -1;
        currentCommandParam = -1;
        break;
      default:
        break;
    }

  }
}

void handleCommand(int command, int rxId, int params){
  switch (command) {
    case SET_MULTIPLIER:
      //Serial.print("setting module ");
      //Serial.print(rxId);
      //Serial.print(" rssi multiplier to ");
      //Serial.println(params);
      rxModules.rssiMultiplier[rxId] = params;
      break;
    case CALIBRATE:
      //Serial.print("setting module ");
      //Serial.print(rxId);
      //Serial.print(" rssi multiplier to ");
      //Serial.println(params);
      setRxState(rxId,params);
      break;
    default:
      break;
  }
}

unsigned long getTime(){
  return millis();
}

void setRxState(int rxId, int state){
  rxModules.state[rxId] = state;
}

void setupRace(uint16_t channels[]){
  if(pilotNumber==deviceNumber){
    Serial.println("we have enough devices for this channel map");
    for(int i=0;i<pilotNumber;i++){
      rxModules.channel[i] = channels[i];
    }
  }else if(pilotNumber>deviceNumber){ //we are tracking more pilots than we have modules for
    //let's distribute the devices as evenly as possible over the channels
    //later we'll scroll through the the modules up the channel as needed
    Serial.println("we will have to ghost channels");
    int spacing = pilotNumber/deviceNumber-(pilotNumber % deviceNumber); //FIX MEEEEEE
    Serial.print("spacing is");
    Serial.println(spacing);
    rxModules.channel[0] = channels[0]; //first device
    int nextChannel = 0;
    int lastChannel = channels[sizeof(channels)-1];
    for(int i=0;i<sizeof(channels);i++){
      if(nextChannel==i){
        rxModules.channel[i] = channels[i];
        nextChannel = nextChannel+spacing;
      }
      if(nextChannel>channels[sizeof(channels)-1]){ //if we are at the end
        rxModules.channel[i] = lastChannel;
      }
    }
  }
}

void sendStateUpdate(int rxId,int state,unsigned long timestamp){
  unsigned long msToSeconds = 1000.0;
  unsigned long seconds = (unsigned long)timestamp/msToSeconds;
  Serial.print("[");
  Serial.print(rxId);
  Serial.print(",");
  Serial.print(state);
  Serial.print(",");
  Serial.print(seconds);
  Serial.println("]");
}

void updateRxState(int rxId, int state){
  sendStateUpdate(rxId,state,getTime());
  rxModules.state[rxId] = state;
}

int refreshRx(int rxId){
  int oldValue = rxModules.rssi[rxId];
  int newValue = (analogRead(rxModules.rssiPins[rxId])-rxModules.noiseFloor[rxId])*rxModules.rssiMultiplier[rxId];
  int dif = newValue-oldValue;
  rxModules.rssi[rxId] = oldValue+(dif*0.1); //this works basica
  return rxModules.rssi[rxId];
}

void handleRxStart(int rxId,int rssi){
  rxModules.state[rxId] = FAR;
}

void handleRxFar(int rxId, int rssi){
  if(rssi>enterThreshold){ //quad is entering the gate
    if(getTime()-rxModules.lapStartTime[rxId] > 3){ //minimum lap time is greater than 3 seconds
      updateRxState(rxId,ENTER);
      rxModules.maxRssiTime[rxId] = getTime();
      rxModules.maxRssi[rxId] = rssi;
    }
  }
}

void handleRxEnter(int rxId, int rssi){
  if(rssi<exitThreshold){
    updateRxState(rxId,EXIT); //this puts us in the handleRxExit method on the next loop
  }else{
    if(rssi>rxModules.maxRssi[rxId]){ //we found a peak, let's note the timestamp
      rxModules.maxRssiTime[rxId] = getTime();
      rxModules.maxRssi[rxId] = rssi;
    }
  }
}

void handleRxExit(int rxId){
  sendStateUpdate(rxId,PASS,rxModules.maxRssiTime[rxId]-rxModules.lapStartTime[rxId]);//this notifies the pi that a pass was made
  rxModules.lapStartTime[rxId] = rxModules.maxRssiTime[rxId];
  updateRxState(rxId,FAR);//this puts us in the handleRxFar method on the next loop
}

void handleRxStates(){
  //Serial.print("[");
  for(int i=0;i<deviceNumber;i++){
    int rssi = refreshRx(i);
    int state = rxModules.state[i];
    switch (state) {
      case CALIBRATE:
        // statements
        break;
      case STANDBY:
        // statements
        break;
      case START:
        handleRxStart(i,rssi);
        break;
      case FAR:
        handleRxFar(i,rssi);
        break;
      case ENTER:
        handleRxEnter(i,rssi);
        break;
      case EXIT:
        handleRxExit(i);
        break;
      case CHANNEL_HOP:
        // statements
        break;
      case FINISHED:
        // statements
        break;
      default:
        // statements
        break;
    }
  }
  //Serial.println("");
}

void scrollChannels(){
  //move last channel to first
  int firstChannel = rxModules.channel[0];
  rxModules.channel[pilotNumber-1] = firstChannel;

  //move all other channels up one
  for(int i=0;i<deviceNumber-1;i++){
    int nextChannel = rxModules.channel[i+1];
    rxModules.channel[i] = nextChannel;
  }
  lockModuleChannels();
}

void lockModuleChannels(){
  for(int i=0;i<deviceNumber;i++){
    int state = rxModules.state[i];
    if(state==FAR){
      //setRxModule(rxModules.channel[i],rxModules.slaveSelectPins[i]);
    }
  }
}

void startRace(){
  for(int i=0;i<deviceNumber;i++){
    updateRxState(i,START);
  }
}

void printRSSI(){
  for(int i=0;i<deviceNumber;i++){
    Serial.print(refreshRx(i));
    //Serial.print(rxModules.rssiMultiplier[i]);
    if(i!=deviceNumber-1){
      Serial.print(",");
    }else{
      Serial.println("");
    }
  }

}

// Main loop
void loop() {
  //printRSSI();
  raceStart = getTime();
  if(rxLoop == -1){  //we have enough modules for each channel
    handleRxStates();
  }else{            //we need to scroll the module channels
    scrollChannels();
    handleRxStates();
  }
  handleSerialData(readSerial());
}
