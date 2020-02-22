from smbus2 import SMBus
from yrk_oo.motors import Motors, MotorDriver
import RPi.GPIO as GPIO
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
    middle = 8
    left = 10
    right = 9
    forward = -0.6
    turn = -forward
    motors = MotorsGroup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(middle, GPIO.IN)
    GPIO.setup(right, GPIO.IN)
    GPIO.setup(left, GPIO.IN)
    centre_val = GPIO.input(middle)
    try:
        motors.set(forward, forward)
        while True:
            if GPIO.input(left) == centre_val:
                motors.set(forward, turn)
                while GPIO.input(left) == centre_val:
                    pass
                motors.set(forward, forward)

            elif GPIO.input(right) == centre_val:
                motors.set(turn, forward)
                while GPIO.input(right) == centre_val:
                    pass
                motors.set(forward, forward)

    except KeyboardInterrupt:
        motors.set(0, 0)


if __name__ == "__main__":
    follow_line()
