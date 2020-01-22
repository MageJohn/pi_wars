from evdev import InputDevice, list_devices, ecodes
from smbus2 import SMBus

from pi_wars import Controller, Stick, drive_from_vector
from yrk_oo.motors import Motors, MotorDriver

if __name__ == "__main__":
    device = InputDevice(list_devices()[0])
    stick = Stick(ecodes.ABS_X, ecodes.ABS_Y, deadzone=0.1)
    controller = Controller(device, [stick])
    bus = SMBus(13)
    m1 = MotorDriver(Motors.MOTOR1, bus, 0.1)
    m2 = MotorDriver(Motors.MOTOR4, bus, 0.1)
    m11 = MotorDriver(Motors.MOTOR2, bus, 0.1)
    m22 = MotorDriver(Motors.MOTOR3, bus, 0.1)

    for _ in controller.read_loop():
        m1_v, m2_v = drive_from_vector(*stick.value)
        print(stick.value, m1_v, m2_v)
        m1.set(m1_v)
        m11.set(m1_v)
        m22.set(m2_v)
        m2.set(m2_v)
