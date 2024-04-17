# 1 "/Users/bmarafino/Documents/AserscopeV3/SPI_slave/SPI_slave.ino"
# 2 "/Users/bmarafino/Documents/AserscopeV3/SPI_slave/SPI_slave.ino" 2






ESP32DMASPI::Slave slave;

static constexpr size_t BUFFER_SIZE = 4096;
static constexpr size_t QUEUE_SIZE = 1;
uint8_t *dma_tx_buf;
uint8_t *dma_rx_buf;
uint8_t *dma_rx_bufB;
typedef struct __attribute__((packed)) point {
    uint16_t x;
    uint16_t y;
    uint8_t laser;
} point;


void setup()
{
    Serial.begin(115200);
    Serial.print(sizeof(point));
    // to use DMA buffer, use these methods to allocate buffer
    dma_tx_buf = slave.allocDMABuffer(BUFFER_SIZE);
    dma_rx_buf = slave.allocDMABuffer(BUFFER_SIZE);
    slave.setDataMode(0); // default: SPI_MODE0
    slave.setMaxTransferSize(BUFFER_SIZE); // default: 4092 bytes
    slave.setQueueSize(QUEUE_SIZE); // default: 1
    // begin() after setting
    slave.begin(0, 11, -1, 13, 12);
    Serial.println("setUP");
}
int start=0;
int end =0;
void blinkGPIO(int pinNum){
  digitalWrite(pinNum,0x0);
  digitalWrite(pinNum,0x1);
  delay(500);
  digitalWrite(pinNum,0x0);

}
void loop()
{
    // do some initialization for tx_buf and rx_buf
    // start and wait to complete one BIG transaction (same data will be received from slave)
        unsigned long start = millis(); // Store the start time
        blinkGPIO(GPIO_NUM_14);
        delay(500);
        blinkGPIO(GPIO_NUM_14);
        delay(500);
        blinkGPIO(GPIO_NUM_14);
    const size_t received_bytes = slave.transfer(dma_tx_buf, dma_rx_buf, BUFFER_SIZE);
unsigned long end = millis(); // Store the end time
unsigned long duration = end - start; // Calculate the duration
Serial.print("Time taken: ");
Serial.println(duration); // Print the duration in milliseconds
    // do something with received_bytes and rx_buf if needed
   Serial.println("loop");

if (received_bytes > 0)
{
    Serial.print("Received points: ");
    Serial.print(received_bytes/5);
    for (size_t i = 0; i < received_bytes; i += sizeof(point))
    {
        // Cast the received bytes to a point struct
        point* p = (point*)&dma_rx_buf[i];

        // Print the values of the point struct
        Serial.print("x: ");
        Serial.print(p->x);
        Serial.print(", y: ");
        Serial.print(p->y);
        Serial.print(", laser: ");
        Serial.println(p->laser, 16);
    }

}

}
