from threading import Thread

import numpy as np
import cv2
from picamera.array import PiRGBAnalysis
import cherrypy
from PIL.ImageColor import getrgb
import time

from lux_sensor import LuxSensor


I2C_BUS = 13


class DriveToColour(Thread):
    def __init__(self, 
            camera, 
            debug_stream, 
            colour="#f00", 
            min_area=10000, 
            center_size=50, 
            turn_speed=0.5, 
            drive_speed=0.7, 
            lux_range=200):
        super().__init__(name=type(self).__name__)
        self.debug_stream = debug_stream
        self.camera = camera
        self.running = False
        self.colour = colour
        self.min_area = min_area
        self.center_size = center_size
        self.turn_speed = turn_speed
        self.drive_speed = drive_speed
        self.lux_range = lux_range

    def run(self):
        self.running = True
        bus = SMBus(I2C_BUS)
        motors = MotorGroup(bus)
        lux_sensor = LuxSensor(bus)
        start_lux = lux_sensor.calibrate()
        cherrpy.engine.log(f"{self.name} was initialised")
        try:
            target_finder = TargetFinder(self.camera, self.colour, self.debug_stream)
            self.camera.start_recording(
                    output=target_finder,
                    format='bgr',
                    splitter_port=3,
                    )
            cherrypy.engine.log(f"{self.name} started the camera")

            # turn
            motors.set(-turn_speed, turn_speed)
            while self.running:
                if (target_finder.found_area >= self.min_area
                        and abs(camera.resolution[0]/2 - target_finder.found_centroid[0]) < self.center_size):
                    motors.set(self.drive_speed, self.drive_speed)
                    break
                time.sleep(1/camera.framerate)
            while self.running:
                lux = lux_sensor.read()
                if lux not in range(start_lux - self.lux_range, start_lux + self.lux_range):
                    motors.set(0, 0)
                    break
        finally:
            camera.stop_recording(splitter_port=3)
            bus.close()


class TargetFinder(PiRGBAnalysis):
    contour_colour = (0, 255, 0)
    marker_colour = (255, 0, 0)
    contour_thickness = 3

    def __init__(self, camera, colour, output):
        super().__init__(camera)
        self.colour = colour
        self.output = output
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
        self.found_area = -1
        self.found_centroid = (0, 0)

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        self._colour = value
        colour = np.uint8(getrgb(value)[::-1]).reshape((1, 1, 3))
        hsv = cv2.cvtColor(colour, cv2.COLOR_BGR2HSV).reshape((3))
        self.low = np.array([hsv[0] - 10, 50, 50])
        self.high = np.array([hsv[0] + 10, 255, 255])

    def analyze(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.low, self.high)
        
        cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel, mask, iterations=2)
        cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel, mask, iterations=2)

        _, contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        moments_l = [cv2.moments(contour) for countour in contours]
        target_moments = max(moments_l, key=lambda m: m['m00'])
        self.found_area = target_moments['m00']
        self.found_centroid = (target_moments['m10']/target_moments['m00'],
                               target_moments['m01']/target_moments['m00'])

        cv2.drawContours(frame, contours, -1, self.contour_colour, self.contour_thickness)
        cv2.drawMarker(frame, self.found-centroid, self.marker_colour)
        self.output.write(frame.data)
