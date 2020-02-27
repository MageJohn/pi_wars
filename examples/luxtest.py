import smbus
import time

bus = smbus.SMBus(7)
#Power ON mode
bus.write_byte_data(0x39, 0x00 | 0x80, 0x03)
# TSL2561 address, 0x39(57)
# Select timing register, 0x01(01) with command register, 0x80(128)
#		0x02(02)	Nominal integration time = 402ms
bus.write_byte_data(0x39, 0x01 | 0x80, 0x02)

try:
    while True:
        # Read data back from 0x0C(12) with command register, 0x80(128), 2 bytes
        # ch0 LSB, ch0 MSB
        data = bus.read_i2c_block_data(0x39, 0x0C | 0x80, 2)

        # Read data back from 0x0E(14) with command register, 0x80(128), 2 bytes
        # ch1 LSB, ch1 MSB
        data1 = bus.read_i2c_block_data(0x39, 0x0E | 0x80, 2)

        # Convert the data
        ch0 = data[1] * 256 + data[0]
        ch1 = data1[1] * 256 + data1[0]

        # Output data to screen
        #print("Full Spectrum(IR + Visible) :%d lux" %ch0)
        #print("Infrared Value :%d lux" %ch1)
        print("Visible Value :%d lux" %(ch0 - ch1))
except KeyboardInterrupt:
    pass
 
