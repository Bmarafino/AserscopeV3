#include <ESP32DMASPISlave.h>
#define PIN_NUM_MISO -1
#define PIN_NUM_MOSI 13
#define PIN_NUM_CLK 11
#define PIN_NUM_CS 12

ESP32DMASPI::Slave slave;

static constexpr size_t BUFFER_SIZE = 256;
static constexpr size_t QUEUE_SIZE = 1;
uint8_t *dma_tx_buf;
uint8_t *dma_rx_buf;

void setup()
{
    Serial.begin(115200);
    // to use DMA buffer, use these methods to allocate buffer
    dma_tx_buf = slave.allocDMABuffer(BUFFER_SIZE);
    dma_rx_buf = slave.allocDMABuffer(BUFFER_SIZE);
    slave.setDataMode(SPI_MODE0);          // default: SPI_MODE0
    slave.setMaxTransferSize(BUFFER_SIZE); // default: 4092 bytes
    slave.setQueueSize(QUEUE_SIZE);        // default: 1

    // begin() after setting
    slave.begin(HSPI, PIN_NUM_CLK, PIN_NUM_MISO, PIN_NUM_MOSI, PIN_NUM_CS);
    Serial.println("setUP");
}
void loop()
{
    // do some initialization for tx_buf and rx_buf
    // start and wait to complete one BIG transaction (same data will be received from slave)
    const size_t received_bytes = slave.transfer(dma_tx_buf, dma_rx_buf, BUFFER_SIZE);
    // do something with received_bytes and rx_buf if needed
    Serial.println("loop");
    if (received_bytes > 0)
    {
        Serial.print("Received data: ");
        for (size_t i = 0; i < received_bytes; ++i)
        {
            // Print each byte of received data
            Serial.print(dma_rx_buf[i], HEX);
            Serial.print(" ");
        }
        Serial.println();
    }
    else
    {
        Serial.println("No data received.");
    }
}