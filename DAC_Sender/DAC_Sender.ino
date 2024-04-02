

#include <SPI.h>
#include "ESP32TimerInterrupt.h"
#define _TIMERINTERRUPT_LOGLEVEL_     3

// Don't use PIN_D1 in core v2.0.0 and v2.0.1. Check https://github.com/espressif/arduino-esp32/issues/5868
// Don't use PIN_D2 with ESP32_C3 (crash)
#define PIN_D19             19        // Pin D19 mapped to pin GPIO9 of ESP32
#define PIN_D3               3        // Pin D3 mapped to pin GPIO3/RX0 of ESP32

#define TIMER0_INTERVAL_US        48

//laser DAC stuff
#define PIN_NUM_MISO GPIO_NUM_32
#define PIN_NUM_MOSI GPIO_NUM_37
#define PIN_NUM_CLK GPIO_NUM_36
#define PIN_NUM_CS GPIO_NUM_35
#define PIN_NUM_LDAC GPIO_NUM_34
#define PIN_NUM_LASER GPIO_NUM_38

#define DAC_CLOCK 20000000

#define debug true

bool blink = true;
//struct for array
typedef struct
{
  int16_t X;
  int16_t Y;
  uint8_t R;
  uint8_t G;
  uint8_t B;
} point;

//pointers to store
//point * curPoints;
point * Buffer;/*
point curPoints[11] = {
  {10,10,255,255,255},
  {0, 0, 255, 255, 255},
  {0, 4094, 255, 255, 255},
  {4094, 0, 255, 255, 255},
  {4094, 4094, 255, 255, 255},
  {2047, 2047, 255, 255, 255},
  {1023, 1023, 255, 255, 255},
  {1023, 3071, 255, 255, 255},
  {3071, 1023, 255, 255, 255},
  {3071, 3071, 255, 255, 255},
  {2047, 0, 255, 255, 255}
};
*/
point curPoints[3] = {
  {2,10,255,255,255},
  {1000, 1000, 255, 255, 255},
  {3094, 3094, 255, 255, 255}
};


void sendPoint(SPIClass *spi, point data);
//what point am I at
long frameIndex=1;
//do I have to ask PI for new points
bool feedMe;



//Define SPI 
//this is to talk to pi
//fspi = new SPIClass(FSPI);

//This is to talk to DAC
SPIClass * hspi = NULL;

SPISettings spiSettings(20000000, MSBFIRST, SPI_MODE0);

bool IRAM_ATTR isrDraw(void * timerNo){

  if (debug){
    frameIndex = (frameIndex % curPoints[0].X) +1 ;
    point curPoint=curPoints[frameIndex];
    SendCartesiaon(curPoint.X,curPoint.Y,curPoint.R,curPoint.G,curPoint.B);
    return true;
  }
  if ((curPoints[0].X==frameIndex) && !feedMe){
    frameIndex=1;
    //free(curPoints);
    //curPoints=Buffer;
  }
  else if(curPoints[0].X < frameIndex){
    //sendPoint(hspi,curPoints[frameIndex]);
  }
  return true;
}


ESP32Timer ITimer0(0);

void SendCartesiaon(int16_t x, int16_t y, uint8_t r, uint8_t g, uint8_t b){
  digitalWrite(PIN_NUM_CS, LOW); // Select the DAC

  hspi->transfer(0b01010000 | ((x>>8) & 0xF)); // Send high byte (4 control bits + 4 MSB of data)
  hspi->transfer(x & 0xFF); // Send low byte (8 LSB of data)
  hspi->endTransaction(); // End SPI transaction
  digitalWrite(PIN_NUM_CS, HIGH); // Deselect the DAC

  digitalWrite(PIN_NUM_CS, LOW); // Select the DAC
  hspi->beginTransaction(spiSettings); // Begin SPI transaction with specified settings
  hspi->transfer(0b11010000 | ((y>>8) & 0xF)); // Send high byte (4 control bits + 4 MSB of data)
  hspi->transfer(y & 0xFF ); // Send low byte (8 LSB of data)
  hspi->endTransaction(); // End SPI transaction
  digitalWrite(PIN_NUM_CS, HIGH); // Deselect the DAC


  if (r == 0 && g == 0 && b == 0)
    {
      digitalWrite(PIN_NUM_LASER, HIGH);
    }
    else
    {
      digitalWrite(PIN_NUM_LASER, LOW);
    }
  digitalWrite(PIN_NUM_LDAC, HIGH); // Latch the output
  digitalWrite(PIN_NUM_LDAC, LOW); // Prepare for next operation

}

void setup()
{
  Serial.begin(115200);
  pinMode(PIN_NUM_CS, OUTPUT);
  pinMode(PIN_NUM_LDAC, OUTPUT);
  digitalWrite(PIN_NUM_CS, HIGH); // Deselect the DAC
  digitalWrite(PIN_NUM_LDAC, LOW); // Prepare LDAC for active low operation
  hspi = new SPIClass(HSPI);
  hspi->begin(PIN_NUM_CLK, -1, PIN_NUM_MOSI, PIN_NUM_CS);
	while (!Serial && millis() < 5000);
  delay(500);
	Serial.print(F("\nStarting Argument_None on 6"));
	Serial.println(ARDUINO_BOARD);
	Serial.println(ESP32_TIMER_INTERRUPT_VERSION);
	Serial.print(F("CPU Frequency = "));
	Serial.print(F_CPU / 1000000);
	Serial.println(F(" MHz"));
  Serial.println(curPoints[0].X);
	// Using ESP32  => 80 / 160 / 240MHz CPU clock ,
	// For 64-bit timer counter
	// For 16-bit timer prescaler up to 1024
	// Interval in microsecs
	if (ITimer0.attachInterruptInterval(TIMER0_INTERVAL_US, isrDraw))
		//if (ITimer0.attachInterrupt(1, TimerHandler0))
	{
		Serial.print(F("Starting  ITimer0 OK, millis() = "));
		Serial.println(millis());
	}
	else
		Serial.println(F("Can't set ITimer0. Select another Timer, freq. or timer"));
    hspi->beginTransaction(spiSettings); // Begin SPI transaction with specified settings
}


void loop()
{
}
