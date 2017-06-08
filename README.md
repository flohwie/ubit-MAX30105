# ubit-MAX30105
Basic functions to use the SparkFun MAX30105 Particle Sensor (with I2C interface) on the micro:bit.

see: https://www.sparkfun.com/products/14045

how to connect the breakout board:
SCL --> pin19 on the micro:bit, 
SDA --> pin20 on the micro:bit, 
5V --> 3V on the micro:bit, 
GND --> 0 on the micro:bit


Python code is not documented within .py file due to memory restrcitions on the micro:bit.
Here is what the module does:

i2c_read_register(self, REGISTER, n_BYTES=1):
Wraps cycle of consecutive write/read commands in order to
read a to be defined number of bytes from a given register address,
which makes the microbit built-in "microbit.i2.write" function more comfortable.
REGISTER: hex address of given register to be read from
n_BYTES: amount of bytes to be retrieved in burst reads, defaults to 1

i2c_set_register(self, REGISTER, VALUE):
Collects register address and value to be written, puts them
into a list for the "bytearray" function (for converting the
list into bytes to be sent),
which makes the micro:bit built-in "microbit.i2.write" function more comfortable.
REGISTER: hex address of given register to be written to
VALUE:    settings to be sent to the register

set_bitMask(self, REGISTER, MASK, NEW_VALUES):
Reads a given register, masks it and then sets the register with new values
Calls the class functions "i2c_read_register" and "i2c_set_register".
REGISTER:   hex address of given register to be written to
MASK:       bit mask
NEW_VALUES: settings to be changed sent to the register

setup_sensor(self, LED_MODE=2, LED_POWER=0x1F, PULSE_WIDTH=0):
Function to setup the sensor with all key parameters.
Parameters to be set from calling the function:
LED_MODE:    set which LEDs are used for sampling
             (1: red LED only, 2: red and IR LEDs, 3: red, IR, and green LEDs)
LED_POWER:   sets the LED current ([x00h - 0xFFh], corresponds to [0 - 50 mA]
PULSE_WIDTH: sets the LED pulse width (the IR, red, and green have the same pulse width),
             and therefore, indirectly sets the integration time of the ADC in each sample.
             The ADC resolution is directly related to the integration time: for convenient
             conversion later. 411, 215, 118 and 69 µs correspind to:
             0 = 18 bit, 1 = 17 bit, 2 = 16 bit, and 3 = 15 bit.

Parameters to be set by hard-coding within the function code:
SAMPLE_AVG:  adjacent samples (in each individual channel) can be averaged and decimated on the chip
FIFO_ROV:    enable or disable roll-over if FIFO over flows
SAMPLE_RATE: sets the effective sampling rate with one sample consisting of one IR pulse/conversion
             and one RED pulse/conversionn
ADC_RANGE:   sets the particle-sensing sensor ADC’s full-scale range

FIFO_bytes_to_int(self, FIFO_bytes, shift=None):
Unpacks the 3 bytes per channel, mask with 0x3FFFF, and
performs bit-shifting according to actual bit resolution
(which depends on the pulse width setting) of the sensor.
Makes use of the "ustruct.unpack" function (which converts
4 bytes to a 32-bit integer; the 4th byte is added as an extra x00).
FIFO_bytes: part of a buffer returned from FIFO burst reads, corresponding to 3-byte channel data
shift:      bit-shift needed to convert to either 15- (>>3), 16- (>>2), or 17-bit (>>1).
            the default setting of 18-bit needs no shifting (>>0).

read_sensor_multiLED(self, POINTER_POSITION):
Reads the sensor by retrieving data from the FIFO at a given read pointer.
Calls "FIFO_bytes_to_int" class fucntion to convert bytes into integers.
POINTER_POSITION: FIFO read pointer, one of 32 samples (0-31).

CreateImage(self, VALUE, RESOLUTION=None):
Creates a dynamic 5x5 LED image from the sensor value to visualize current reading.
Sequentially builds an image string and then uses the "microbit.Image" function
to show a representation of the current sensor value on the micro_bit LED matrix.
