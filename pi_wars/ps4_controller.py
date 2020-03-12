#!/usr/bin/env python3

from threading import Thread

import numpy as np
import cv2
from evdev import ecodes, InputDevice, list_devices
from annotated import annotated
from smbus2 import SMBus
from picamera.array import PiRGBAnalysis

from controller import Controller, Stick
from motor_group import MotorGroup
from drive_from_vector import drive_from_vector

I2C_BUS = 13


class PS4ControllerMode(Thread):
    def __init__(self, camera, debug_stream):
        super().__init__(name=type(self).__name__)
        self.debug_stream = debug_stream
        self.camera = camera
        self.running = False
        self.left_stick = Stick(ecodes.ABS_X, ecodes.ABS_Y)

    @property
    def deadzone(self):
        return self.left_stick.dz

    @deadzone.setter
    @annotated
    def deadzone(self, value: int):
        if type(value) is float and (0 <= value <= 1):
            self.left_stick.dz = value
        else:
            raise ValueError(f"{value} is not a float in the range 0 <= deadzone <= 1")

    def run(self):
        self.running = True
        dev = InputDevice(list_devices()[0])
        controller = Controller(dev, [self.left_stick])
        bus = SMBus(I2C_BUS)
        motors = MotorGroup(bus)

        try:
            while self.running:
                if controller.read_one():
                    left, right = drive_from_vector(*self.left_stick.value)
                    motors.set(left, right)
            print(f"{self.name} stopping")
        finally:
            motors.set(0, 0)
            bus.close()

    def join(self):
        self.running = False
        super().join()

