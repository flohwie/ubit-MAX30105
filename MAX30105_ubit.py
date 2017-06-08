from microbit import i2c, sleep, display, Image
from ustruct import unpack


class ParticleSensor(object):
    def __init__(self, HEX_ADDRESS):
        self._address = HEX_ADDRESS
        self._led_mode = None
        self._pulse_width_set = None
        try:
            i2c.read(self._address, 1)
        except OSError as error:
            raise SystemExit(error)
        else:
            print("Found MAX30105 ParticleSensor: [%s]" % hex(self._address))

    def i2c_read_register(self, REGISTER, n_bytes=1):
        i2c.write(self._address, bytearray([REGISTER]))
        return i2c.read(self._address, n_bytes)

    def i2c_set_register(self, REGISTER, VALUE):
        i2c.write(self._address, bytearray([REGISTER, VALUE]))
        return

    def set_bitMask(self, REGISTER, MASK, NEW_VALUES):
        newCONTENTS = (ord(self.i2c_read_register(REGISTER)) & MASK) | NEW_VALUES
        self.i2c_set_register(REGISTER, newCONTENTS)
        return

    def setup_sensor(self, LED_MODE=2, LED_POWER=0x1F, PULSE_WIDTH=0):
        self.set_bitMask(0x09, 0xBF, 0x40)
        sleep(1000)
        # 3: 69 (15-bit), 2: 118 (16-bit), 1: 215 (17-bit), 0: 411 (18-bit)          
        self.set_bitMask(0x0A, 0xFC, PULSE_WIDTH)
        self._pulse_width_set = PULSE_WIDTH

        if LED_MODE not in [1, 2, 3]:
            raise ValueError('wrong LED mode:{0}!'.format(LED_MODE))
        elif LED_MODE == 1:
            self.set_bitMask(0x09, 0xF8, 0x02)
            self.i2c_set_register(0x0C, LED_POWER)
        elif LED_MODE == 2:
            self.set_bitMask(0x09, 0xF8, 0x03)
            self.i2c_set_register(0x0C, LED_POWER)
            self.i2c_set_register(0x0D, LED_POWER)
        elif LED_MODE == 3:
            self.set_bitMask(0x09, 0xF8, 0x07)
            self.i2c_set_register(0x0C, LED_POWER)
            self.i2c_set_register(0x0D, LED_POWER)
            self.i2c_set_register(0x0E, LED_POWER)
            self.i2c_set_register(0x11, 0b00100001)
            self.i2c_set_register(0x12, 0b00000011)
        self._led_mode = LED_MODE

        self.set_bitMask(0x0A, 0xE3, 0x00)  # sampl. rate: 50
        # 50: 0x00, 100: 0x04, 200: 0x08, 400: 0x0C,
        # 800: 0x10, 1000: 0x14, 1600: 0x18, 3200: 0x1C

        self.set_bitMask(0x0A, 0x9F, 0x00)  # ADC range: 2048
        # 2048: 0x00, 4096: 0x20, 8192: 0x40, 16384: 0x60

        self.set_bitMask(0x08, ~0b11100000, 0x00)  # FIFO sample avg: (no)
        # 1: 0x00, 2: 0x20, 4: 0x40, 8: 0x60, 16: 0x80, 32: 0xA0

        self.set_bitMask(0x08, 0xEF, 0x10)  # FIFO rollover: enable
        # 0x00/0x01: dis-/enable

        self.i2c_set_register(0x04, 0)
        self.i2c_set_register(0x05, 0)
        self.i2c_set_register(0x06, 0)

    def FIFO_bytes_to_int(self, FIFO_bytes):
        value = unpack(">i", b'\x00' + FIFO_bytes)
        return (value[0] & 0x3FFFF) >> self._pulse_width_set

    def read_sensor_multiLED(self, pointer_position):
        self.i2c_set_register(0x06, pointer_position)
        fifo_bytes = self.i2c_read_register(0x07, self._led_mode * 3)
        red_int = self.FIFO_bytes_to_int(fifo_bytes[0:3])
        IR_int = self.FIFO_bytes_to_int(fifo_bytes[3:6])
        green_int = self.FIFO_bytes_to_int(fifo_bytes[6:9])
        print("[Red:", red_int, " IR:", IR_int, " G:", green_int, "]", sep='')
        return red_int, IR_int, green_int

    def CreateImage(self, value):
        unit = (2 ** (18 - self._pulse_width_set)) // (250)
        image_p1 = (value // (unit * 50)) * (str(9) * 5)
        image_p2 = ((value % (unit * 50)) // (unit * 10)) * str(9)
        points = (((value % (unit * 50)) % (unit * 10))) // unit
        if points > 0:
            image_p3 = str(points)
        else:
            image_p3 = ""
        image_p4 = ((25) - len(image_p1 + image_p2 + image_p3)) * str(0)
        tmp_image = image_p1 + image_p2 + image_p3 + image_p4
        return ':'.join([tmp_image[i:i+5] for i in range(0, len(tmp_image), 5)])


if __name__ == '__main__':
    print('\n', "Demonstrating functions of MAX30105_ubit.py")
    MAX30105 = ParticleSensor(HEX_ADDRESS=0x57)
    part_id = MAX30105.i2c_read_register(0xFF)
    rev_id = MAX30105.i2c_read_register(0xFE)
    print("MAX30105: part ID", hex(ord(part_id)), "revision:", ord(rev_id))
    print("Setting up sensor now:", '\n')
    MAX30105.setup_sensor(LED_MODE=3, LED_POWER=0x1F, PULSE_WIDTH=0)

    try:
        while True:
            for FIFO_pointer in range(32):
                sensor_data = MAX30105.read_sensor_multiLED(FIFO_pointer)
                brightness = MAX30105.CreateImage(int(sensor_data[1]))
                sensor_image = Image(brightness)
                display.show(sensor_image)

    except (KeyboardInterrupt):
        print('\n', "Exit on Ctrl-C: Good bye!")

    finally:
        print('\n', "Resetting sensor to power-on defaults!")
        MAX30105.set_bitMask(0x09, 0xBF, 0x40)  # reset to POR
        display.clear()
