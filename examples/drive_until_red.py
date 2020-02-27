import smbus2
from pi_wars import drive_from_vector
from yrk_oo.motors import Motors, MotorDriver
import time

SPEED = -0.69
BUS = smbus2.SMBus(7)

BUS.write_byte_data(0x39, 0x00 | 0x80, 0x03)
BUS.write_byte_data(0x39, 0x01 | 0x80, 0x02) 

class MotorsGroup:
    def __init__(self):
        bus = smbus2.SMBus(13)
        self.m1 = MotorDriver(Motors.MOTOR1, bus, 0.1)
        self.m2 = MotorDriver(Motors.MOTOR4, bus, 0.1)
        self.m11 = MotorDriver(Motors.MOTOR2, bus, 0.1)
        self.m22 = MotorDriver(Motors.MOTOR3, bus, 0.1)
    def set(self, m1, m2):
        self.m1.set(m1)
        self.m11.set(m1)
        self.m22.set(m2)
        self.m2.set(m2)
    def clean(self):
        self.set(0, 0)

def read_lux():
    data = BUS.read_i2c_block_data(0x39, 0x0C | 0x80, 2)
    data1 = BUS.read_i2c_block_data(0x39, 0x0E | 0x80, 2)
    ch0 = data[1] * 256 + data[0]
    ch1 = data1[1] * 256 + data1[0]
    return ch0 - ch1

def calibrate(sensitivity):
    visible = []
    for i in range(sensitivity):
        visible.append(read_lux())
    scale = max(visible) - min(visible)
    visible = sum(visible)/sensitivity  
    return visible, scale

if __name__ == "__main__":
    lux_set = calibrate(1000)
    target = lux_set[0]
    offset = 200
    motors = MotorsGroup()
    motors.set(SPEED, SPEED)
    while True:
        lux = read_lux()
        if lux > target + offset or lux < target - offset:
            motors.set(0,0)
            break




    

