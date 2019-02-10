/*
 WiFi Web Server LED Blink

 A simple web server that lets you blink an LED via the web.
 This sketch will print the IP address of your WiFi Shield (once connected)
 to the Serial monitor. From there, you can open that address in a web browser
 to turn on and off the LED on pin 5.

 If the IP address of your shield is yourAddress:
 http://yourAddress/H turns the LED on
 http://yourAddress/L turns it off

 This example is written for a network using WPA encryption. For
 WEP or WPA, change the Wifi.begin() call accordingly.

 Circuit:
 * WiFi shield attached
 * LED attached to pin 5

 created for arduino 25 Nov 2012
 by Tom Igoe

ported for sparkfun esp32 
31.01.2017 by Jan Hendrik Berlin
 
 */

#define N_PIXELS 150



const char* ssid     = ""; //wifi ssid
const char* password = ""; //wifi password

#include <WiFi.h>
#include <ESPmDNS.h> 


#define min(a,b) ((a)<(b)?(a):(b))

#include "esp32_digital_led_lib.h"

#if defined(ARDUINO) && ARDUINO >= 100
  // No extras
#elif defined(ARDUINO) // pre-1.0
  // No extras
#elif defined(ESP_PLATFORM)
  #include "arduinoish.hpp"
#endif

// **Required** if debugging is enabled in library header
// TODO: Is there any way to put this in digitalLeds_initStrands() and avoid undefined refs?
#if DEBUG_ESP32_DIGITAL_LED_LIB
  int digitalLeds_debugBufferSz = 1024;
  char * digitalLeds_debugBuffer = static_cast<char*>(calloc(digitalLeds_debugBufferSz, sizeof(char)));
#endif

void gpioSetup(int gpioNum, int gpioMode, int gpioVal) {
  #if defined(ARDUINO) && ARDUINO >= 100
    pinMode (gpioNum, gpioMode);
    digitalWrite (gpioNum, gpioVal);
  #elif defined(ESP_PLATFORM)
    gpio_num_t gpioNumNative = static_cast<gpio_num_t>(gpioNum);
    gpio_mode_t gpioModeNative = static_cast<gpio_mode_t>(gpioMode);
    gpio_pad_select_gpio(gpioNumNative);
    gpio_set_direction(gpioNumNative, gpioModeNative);
    gpio_set_level(gpioNumNative, gpioVal);
  #endif
}


strand_t STRANDS[] = { 
  {.rmtChannel = 0, .gpioNum = 16, .ledType = LED_WS2813_V2, .brightLimit = 250, .numPixels = N_PIXELS,
   .pixels = nullptr, ._stateVars = nullptr},
};
int STRANDCNT = sizeof(STRANDS)/sizeof(STRANDS[0]);

//**************************************************************************//
int getMaxMalloc(int min_mem, int max_mem) {
  int prev_size = min_mem;
  int curr_size = min_mem;
  int max_free = 0;
  while (1) {
    void * foo1 = malloc(curr_size);
    if (foo1 == nullptr) {  // Back off
      max_mem = min(curr_size, max_mem);
      curr_size = (int)(curr_size - (curr_size - prev_size) / 2.0);
    }
    else {  // Advance
      free(foo1);
      max_free = curr_size;
      prev_size = curr_size;
      curr_size = min(curr_size * 2, max_mem);
    }
    if (abs(curr_size - prev_size) == 0) {
      break;
    }
  }
  Serial.print("checkmem: max free heap = ");
  Serial.print(esp_get_free_heap_size());
  Serial.print(" bytes, max allocable = ");
  Serial.print(max_free);
  Serial.println(" bytes");
  return max_free;
}


WiFiServer server(80);

void setup()
{
    Serial.begin(115200);
    Serial.println("asdf");
    
    /****************************************************************************
     If you have multiple strands connected, but not all are in use, the
     GPIO power-on defaults for the unused strand data lines will typically be
     high-impedance. Unless you are pulling the data lines high or low via a
     resistor, this will lead to noise on those unused but connected channels
     and unwanted driving of those unallocated strands.
     This optional gpioSetup() code helps avoid that problem programmatically.
    ****************************************************************************/
    gpioSetup(16, OUTPUT, LOW);
  
    if (digitalLeds_initStrands(STRANDS, STRANDCNT)) {
      Serial.println("Init FAILURE: halting");
      while (true) {};
    }

    getMaxMalloc(1*1024, 16*1024*1024);

    delay(10);

    // We start by connecting to a WiFi network

    Serial.println();
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected.");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
        if (!MDNS.begin("ledmatrix")) {
        Serial.println("Error setting up MDNS responder!");
        while(1){
            delay(1000);
        }
    }
    
    server.begin();
    if(digitalLeds_initStrands(STRANDS, STRANDCNT)){
      Serial.println("Init failure for LEDs");
    }
    strand_t * pStrand = &STRANDS[0];

}


void loop(){
  WiFiClient client = server.available();   // listen for incoming clients
  //Serial.println("test");
  
  if (client) {                             // if you get a client,
    Serial.println("New Client.");           // print a message out the serial port
    String currentLine = "";                // make a String to hold incoming data from the client
    while (client.connected()) {            // loop while the client's connected
      if (client.available()) {             // if there's bytes to read from the client,
        char c = client.read();             // read a byte, then
        
        Serial.write(c);                    // print it out the serial monitor
        
        if (c == '\n') {                    // if the byte is a newline character

          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0) {
            // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
            // and a content-type so the client knows what's coming, then a blank line:
            //client.println("HTTP/1.1 200 OK");
            //client.println("Content-type:text/html");
            //client.println();

            // the content of the HTTP response follows the header:
            //client.print("Click <a href=\"/H\">here</a> to turn the LED on pin 5 on.<br>");
            //client.print("Click <a href=\"/L\">here</a> to turn the LED on pin 5 off.<br>");

            // The HTTP response ends with another blank line:
            //client.println();
            // break out of the while loop:
            //break;
          } else {    // if you got a newline, then clear currentLine:
            currentLine = "";
          }
        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }


        uint8_t imgArray[3*N_PIXELS];
        if ( currentLine.endsWith("PUT /ImgData") ){
          Serial.println("-----------------------------\n");
          String parsedCurrent;
          
          while(1){
            char cc = client.read();
            parsedCurrent += cc;
            if(parsedCurrent.endsWith("START_IMG_DATA")){
              for(int kk=0;kk<N_PIXELS*3;kk++){
                char c_data = client.read();
                imgArray[kk] = (uint8_t)c_data;
                //Serial.print(cc); Serial.print(" - ") ; Serial.print(imgArray[kk-1]);Serial.print(" \n\r") ; 
              }
              setLedsFromPutRequest(imgArray, 0);
              client.println("HTTP/1.1 200 OK");
              client.println("Content-type:text/html");
              client.println();
              client.stop();
              break;
            }
          }
        }
        
        if (currentLine.endsWith("DELETE /ImgData")){
          digitalLeds_resetPixels(&STRANDS[0]);
        }
        if (currentLine.endsWith("POST /Animation/Rainbow")){
          // Start the rainbow animation
          
        }
      }
    }
    // close the connection:
    client.stop();
    Serial.println("Client Disconnected.");
  }
}

void setLedsFromPutRequest(uint8_t * pixVals, int valW){
  
  Serial.println("Starting to read...");
  strand_t * pStrand = &STRANDS[0];
  //digitalLeds_resetPixels(pStrand);
  for(int i=0;i<N_PIXELS;i++){
    //Serial.print(pixVals[i] ); Serial.print(" - "); Serial.print( pixVals[i+150]); Serial.print(" - "); Serial.print( pixVals[i+300]);
    //Serial.print("\n\r");
    pStrand -> pixels[i] = pixelFromRGBW(pixVals[ i ], pixVals[i+150], pixVals[i+300],valW);
  }
  digitalLeds_updatePixels(pStrand);
  Serial.println("All seem ok!");  
}

//**************************************************************************//
class Rainbower {
  private:
    strand_t * pStrand;
    const uint8_t color_div = 4;
    const uint8_t anim_step = 1;
    uint8_t anim_max;
    uint8_t stepVal1;
    uint8_t stepVal2;
    pixelColor_t color1;
    pixelColor_t color2;
  public:
    Rainbower(strand_t *);
    void drawNext();
};

Rainbower::Rainbower(strand_t * pStrandIn)
{
  pStrand = pStrandIn;
  anim_max = pStrand->brightLimit - anim_step;
  stepVal1 = 0;
  stepVal2 = 0;
  color1 = pixelFromRGBW(anim_max, 0, 0, 0);
  color2 = pixelFromRGBW(anim_max, 0, 0, 0);
}

void Rainbower::drawNext()
{
  color1 = color2;
  stepVal1 = stepVal2;
  for (uint16_t i = 0; i < pStrand->numPixels; i++) {
    pStrand->pixels[i] = pixelFromRGBW(color1.r/color_div, color1.g/color_div, color1.b/color_div, 0);
    if (i == 1) {
      color2 = color1;
      stepVal2 = stepVal1;
    }
    switch (stepVal1) {
      case 0:
      color1.g += anim_step;
      if (color1.g >= anim_max)
        stepVal1++;
      break;
      case 1:
      color1.r -= anim_step;
      if (color1.r == 0)
        stepVal1++;
      break;
      case 2:
      color1.b += anim_step;
      if (color1.b >= anim_max)
        stepVal1++;
      break;
      case 3:
      color1.g -= anim_step;
      if (color1.g == 0)
        stepVal1++;
      break;
      case 4:
      color1.r += anim_step;
      if (color1.r >= anim_max)
        stepVal1++;
      break;
      case 5:
      color1.b -= anim_step;
      if (color1.b == 0)
        stepVal1 = 0;
      break;
    }
  }
  digitalLeds_updatePixels(pStrand);
}

void rainbows(strand_t * strands[], int numStrands, unsigned long delay_ms, unsigned long timeout_ms)
{
  //Rainbower rbow(pStrand); Rainbower * pRbow = &rbow;
  Rainbower * pRbow[numStrands];
  int i;
  Serial.print("DEMO: rainbows(");
  for (i = 0; i < numStrands; i++) {
    pRbow[i] = new Rainbower(strands[i]);
    if (i > 0) {
      Serial.print(", ");
    }
    Serial.print("ch");
    Serial.print(strands[i]->rmtChannel);
    Serial.print(" (0x");
    Serial.print((uint32_t)pRbow[i], HEX);
    Serial.print(")");
  }
  Serial.print(")");
  Serial.println();
  unsigned long start_ms = millis();
  while (timeout_ms == 0 || (millis() - start_ms < timeout_ms)) {
    for (i = 0; i < numStrands; i++) {
      pRbow[i]->drawNext();
    }
    delay(delay_ms);
  }
  for (i = 0; i < numStrands; i++) {
    delete pRbow[i];
    digitalLeds_resetPixels(strands[i]);
  }
}

void rainbow(strand_t * pStrand, unsigned long delay_ms, unsigned long timeout_ms)
{
  strand_t * strands [] = { pStrand };
  rainbows(strands, 1, delay_ms, timeout_ms);
}
