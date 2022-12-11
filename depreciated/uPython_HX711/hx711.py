# Example for micropython.org device, gpio mode
# Connections:
# Pin # | HX711
# ------|-----------
# 34    | data_pin, esp32 gpio 
# 5     | clock_pin, esp32 sck

# from hx711_gpio import HX711
from machine import Pin
pin_OUT = Pin(34, Pin.IN, pull=Pin.PULL_DOWN)
pin_SCK = Pin(5, Pin.OUT)

from machine import enable_irq, disable_irq, idle
import time

class HX711_GPIO:
    def __init__(self, pd_sck, dout, gain=128):
        self.pSCK = pd_sck
        self.pOUT = dout
        self.pSCK.value(False)

        self.GAIN = 0
        self.OFFSET = 0
        self.SCALE = 1

        self.time_constant = 0.25
        self.filtered = 0

        self.set_gain(gain);

    def set_gain(self, gain):
        if gain is 128:
            self.GAIN = 1
        elif gain is 64:
            self.GAIN = 3
        elif gain is 32:
            self.GAIN = 2

        self.read()
        self.filtered = self.read()

    def is_ready(self):
        return self.pOUT() == 0

    def read(self):
        # wait for the device being ready
        for _ in range(500):
            if self.pOUT() == 0:
                break
            time.sleep_ms(1)
        else:
            raise OSError("Sensor does not respond")

        # shift in data, and gain & channel info
        result = 0
        for j in range(24 + self.GAIN):
            state = disable_irq()
            self.pSCK(True)
            self.pSCK(False)
            enable_irq(state)
            result = (result << 1) | self.pOUT()

        # shift back the extra bits
        result >>= self.GAIN

        # check sign
        if result > 0x7fffff:
            result -= 0x1000000

        return result

    def read_average(self, times=3):
        sum = 0
        for i in range(times):
            sum += self.read()
        return sum / times

    def read_lowpass(self):
        self.filtered += self.time_constant * (self.read() - self.filtered)
        return self.filtered

    def get_value(self):
        return self.read_lowpass() - self.OFFSET

    def get_units(self):
        return self.get_value() / self.SCALE

    def tare(self, times=15):
        self.set_offset(self.read_average(times))

    def set_scale(self, scale):
        self.SCALE = scale

    def set_offset(self, offset):
        self.OFFSET = offset

    def set_time_constant(self, time_constant = None):
        if time_constant is None:
            return self.time_constant
        elif 0 < time_constant < 1.0:
            self.time_constant = time_constant

    def power_down(self):
        self.pSCK.value(False)
        self.pSCK.value(True)

    def power_up(self):
        self.pSCK.value(False)

######

from machine import idle
import time
import spi

class HX711_SPI:
    def __init__(self, pd_sck, dout, spi, gain=128):
        self.pSCK = pd_sck
        self.pOUT = dout
        self.spi = spi

        self.pSCK(0)

        self.clock_25 = b'\xaa\xaa\xaa\xaa\xaa\xaa\x80'
        self.clock_26 = b'\xaa\xaa\xaa\xaa\xaa\xaa\xa0'
        self.clock_27 = b'\xaa\xaa\xaa\xaa\xaa\xaa\xa8'
        self.clock = self.clock_25
        self.lookup = (b'\x00\x01\x00\x00\x02\x03\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x04\x05\x00\x00\x06\x07\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                       b'\x00\x00\x00\x00\x08\x09\x00\x00\x0a\x0b\x00\x00'
                       b'\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x0d\x00\x00'
                       b'\x0e\x0f')
        self.in_data = bytearray(7)

        self.OFFSET = 0
        self.SCALE = 1

        self.time_constant = 0.1
        self.filtered = 0

        self.set_gain(gain)

    def set_gain(self, gain):
        if gain is 128:
            self.clock = self.clock_25
        elif gain is 64:
            self.clock = self.clock_27
        elif gain is 32:
            self.clock = self.clock_26

        self.read()
        self.filtered = self.read()
        # print('Gain & initial value set')

    def read(self):
        # wait for the device to get ready
        for _ in range(500):
            if self.pOUT() == 0:
                break
            time.sleep_ms(1)
        else:
            raise OSError("Sensor does not respond")

        # get the data and set channel and gain
        self.spi.write_readinto(self.clock, self.in_data)

        # pack the data into a single value
        result = 0
        for _ in range(6):
            result = (result << 4) + self.lookup[self.in_data[_] & 0x55]

        # return sign corrected result
        return result - ((result & 0x800000) << 1)

    def read_average(self, times=3):
        sum = 0
        for i in range(times):
            sum += self.read()
        return sum / times

    def read_lowpass(self):
        self.filtered += self.time_constant * (self.read() - self.filtered)
        return self.filtered

    def get_value(self):
        return self.read_lowpass() - self.OFFSET

    def get_units(self):
        return self.get_value() / self.SCALE

    def tare(self, times=15):
        self.set_offset(self.read_average(times))

    def set_scale(self, scale):
        self.SCALE = scale

    def set_offset(self, offset):
        self.OFFSET = offset

    def set_time_constant(self, time_constant=None):
        if time_constant is None:
            return self.time_constant
        elif 0 < time_constant < 1.0:
            self.time_constant = time_constant

    def power_down(self):
        self.pSCK.value(False)
        self.pSCK.value(True)

    def power_up(self):
        self.pSCK.value(False)

######
        
# Example for micropython.org device, spi mode
# Connections:
# Pin # | HX711
# ------|-----------
# 12    | data_pin, (HX711) DT -> MISO (ESP32 GPIO
# 13    | clock_pin, (HX711) SCK -> MOSI (ESP32 GPIO
# 14    | spi clock

# from hx711_spi import HX711
#from machine import Pin

pin_OUT = Pin(34, Pin.IN, pull=Pin.PULL_DOWN)
pin_SCK = Pin(18, Pin.OUT)
spi_SCK = Pin(5)

spi = SPI(1, baudrate=1000000, polarity=0, phase=0, sck=spi_SCK, mosi=pin_SCK, miso=pin_OUT)

hx = HX711_SPI(pin_SCK, pin_OUT, spi)


######

# hx711 = HX711_GPIO(pin_SCK, pin_OUT)

hx711.tare()
while True:
    value = hx711.read()
    print(value)
    #value = hx711.get_value()
    

