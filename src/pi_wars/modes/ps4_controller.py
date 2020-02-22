#!/usr/bin/env python3

from threading import Thread

import numpy as np
import cv2
from evdev import ecodes, InputDevice, list_devices
from annotated import annotated
from smbus2 import SMBus
from picamera.array import PiRGBAnalysis

from .. import Controller, Stick, MotorGroup, drive_from_vector

I2C_BUS = 11


class PS4ControllerMode(Thread):
    def __init__(self, camera, debug_stream, **kwargs):
        super().__init__(**kwargs)
        self.debug_stream = debug_stream
        self.camera = camera
        self.running = True

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
        dev = InputDevice(list_devices()[0])
        controller = Controller(dev, [self.left_stick])
        left_stick = Stick(ecodes.ABS_X, ecodes.ABS_Y)
        bus = SMBus(I2C_BUS)
        motors = MotorGroup(bus)
        try:
            self.camera.start_recording(
                output=StickOverlayer(self.camera, left_stick, self.debug_stream),
                format='bgr',
                splitter_port=1
            )
            while self.running:
                controller.read_one()
                left, right = drive_from_vector(*left_stick.value)
                motors.set(left, right)
        finally:
            self.bus.close()
            self.camera.stop_recording()

    def join(self):
        self.running = False
        super().join()


class StickOverlayer(PiRGBAnalysis):
    border = 20
    thickness = 10
    colour = (75, 224, 113)

    def __init__(self, camera, stick, output):
        super().__init__(camera)
        self.stick = stick
        self.output = output

    def analyze(self, frame):
        circle_r = int(frame.shape[0] / 6)
        circle_pos = (
            self.border + circle_r,
            frame.shape[1] - (self.border + circle_r),
        )

        cv2.circle(frame, circle_pos, circle_r, self.colour, 5, cv2.LINE_AA)

        centre_r = int(circle_r / 5)
        centre_pos = (np.array(self.stick.value) * circle_r + circle_pos).astype(int)

        self.output.write(
            cv2.circle(frame, centre_pos, centre_r, self.colour, -1,)
        )
