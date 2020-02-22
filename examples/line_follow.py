from smbus2 import SMBus
from calibration import calibration
from lf_i2c_reader import read_sensor
from pi_wars import drive_from_vector
from yrk_oo.motors import Motors, MotorDriver
import time

class MotorsGroup:
    def __init__(self):
        bus = SMBus(13)
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
        


def follow_line():
    sBus = SMBus(7)
    sAdd = 0x58

    centre = calibration(100, 7)
    sensor = read_sensor(sBus, sAdd)
    print(sensor)
    print(centre)
    high = centre[2]
    low = centre[0]
    full = -1
    half = -full
    turn_f = -0.8
    turn_h = -turn_f
    motors = MotorsGroup()

    try:
        motors.set(full, full)
        while(True):
            sensor = read_sensor(sBus,sAdd)
            LL = sensor[3]
            RR = sensor[0]
            if (low <= LL <= high):
                #set 2s half speed
                returned = False
                motors.set(turn_f, turn_h)
                while(not returned):
                    sensor = read_sensor(sBus, sAdd)
                    if (low <= sensor[1] <= high and low <= sensor[2] <= high):
                        returned = True
                        motors.set(full, full)
            elif (low <= RR <= high):
                returned = False
                motors.set(turn_h, turn_f)
                while(not returned):
                    sensor = read_sensor(sBus, sAdd)
                    if (low <= sensor[1] <= high and low <= sensor[2] <= high):
                        returned = True
                        motors.set(full, full)

    except KeyboardInterrupt:
        motors.set(0, 0)
        sBus.close()

if __name__ == "__main__":
    follow_line()
