import time
from smbus2 import SMBus

from pi_wars import drive_from_vector
from yrk_oo.motors import Motors, MotorDriver

if __name__ == "__main__":
    with SMBus(13) as bus:
        m1 = MotorDriver(Motors.MOTOR1, bus, 0.1)
        m2 = MotorDriver(Motors.MOTOR4, bus, 0.1)
        m11 = MotorDriver(Motors.MOTOR2, bus, 0.1)
        m22 = MotorDriver(Motors.MOTOR3, bus, 0.1)

        print("Drive forward")
        m1_v, m2_v = drive_from_vector(0, 1)
        m1.set(m1_v)
        m11.set(m1_v)
        m22.set(m2_v)
        m2.set(m2_v)
        time.sleep(3)

        print("Turn")
        m1_v, m2_v = drive_from_vector(1, 0)
        m1.set(m1_v)
        m11.set(m1_v)
        m22.set(m2_v)
        m2.set(m2_v)
        time.sleep(1)

        print("Drive backward")
        m1_v, m2_v = drive_from_vector(0, -1)
        m1.set(m1_v)
        m11.set(m1_v)
        m22.set(m2_v)
        m2.set(m2_v)
        time.sleep(3)

        m1.set(0)
        m11.set(0)
        m22.set(0)
        m2.set(0)
