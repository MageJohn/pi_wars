from evdev import InputDevice, list_devices
from smbus2 import SMBus

from pi_wars import Controller, Stick, drive_from_vector
from yrk_oo.motors import MOTOR1, MOTOR2, MOTOR3, MOTOR4, MotorDriver, ecodes

if __name__ == "__main__":
    device = InputDevice(list_devices()[0])
    stick = Stick(ecodes.ABS_X, ecodes.ABS_Y, deadzone=0.1)
    controller = Controller(device, [stick])
    bus = SMBus(13)
    m1 = MotorDriver(MOTOR1, bus)
    m2 = MotorDriver(MOTOR4, bus)
    m11 = MotorDriver(MOTOR2, bus)
    m22 = MotorDriver(MOTOR3, bus)

    for _ in controller.read_loop():
        m1_v, m2_v = drive_from_vector(*stick.value)
        print(stick.value, m1_v, m2_v)
        m1.set(m1_v)
        m11.set(m1_v)
        m22.set(m2_v)
        m2.set(m2_v)
