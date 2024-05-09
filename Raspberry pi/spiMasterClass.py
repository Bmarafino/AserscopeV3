import spidev
import RPi.GPIO as GPIO


class spiMaster:
    def __init__():
        # We only have SPI bus 0 available to us on the Pi
        bus = 0
        # Device is the chip select pin. Set to 0 or 1, depending on the connections
        device = 0
        # Enable SPI
        spi = spidev.SpiDev()
        # Open a connection to a specific bus and device (chip select pin)
        spi.open(bus, device)
        # Set SPI speed and mode
        spi.max_speed_hz = 60000000
        spi.mode = 0

    def send_spi_data(self, bufferSub):
        print("Sending data...")
        binary_buffer = bytearray()
        for point in random_points:
            binary_buffer += struct.pack(">HHB", *point)
        start_time = time.perf_counter()

        end_time = time.perf_counter()

    def sendBinaryPoints(self, points):
        spi.writebytes2(points)
