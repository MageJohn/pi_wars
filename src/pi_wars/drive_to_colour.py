from threading import Thread

import numpy as np
import cv2
from picamera.array import PiRGBAnalysis
import cherrypy
from PIL.ImageColor import getrgb
import time
from smbus2 import SMBus
from motor_group import MotorGroup
from unittest.mock import MagicMock
from collections import deque
import evdev

from lux_sensor import LuxSensor



class DriveToColour(Thread):
    def __init__(self, 
            camera, 
            debug_stream, 
            colour="hsv(350, 100%, 100%)", 
            min_area=2500, 
            center_size=20, 
            turn_speed=0.5, 
            drive_speed=-0.8, 
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
        bus13 = SMBus(13)
        bus7 = SMBus(7)
        motors = MotorGroup(bus13)
        #motors = MagicMock()
        lux_sensor = LuxSensor(bus7)
        start_lux = lux_sensor.calibrate(1000)
        cherrypy.engine.log(f"{self.name} was initialised")
        try:
            target_finder = TargetFinder(self.camera, self.colour, self.debug_stream)
            self.camera.start_recording(
                    output=target_finder,
                    format='bgr',
                    splitter_port=3,
                    )
            cherrypy.engine.log(f"{self.name} started the camera")

            # turn
            motors.set(-self.turn_speed, self.turn_speed)
            cherrypy.engine.log(f"{self.name} Where's the red????!")
            while self.running:
                if (target_finder.found_area >= self.min_area
                        and abs(self.camera.resolution[0]/2 - target_finder.found_centroid[0]) < self.center_size):
                    motors.set(self.drive_speed, self.drive_speed)
                    cherrypy.engine.log(f"{self.name} OOH RED! area={target_finder.found_area}")
                lux = lux_sensor.read()
                if lux not in range(int(start_lux - self.lux_range), int(start_lux + self.lux_range)):
                    motors.set(0, 0)

                    cherrypy.engine.log(f"{self.name} I found it, am I a good boy?")
                    break
            while self.running:
                time.sleep(1/float(self.camera.framerate))
        finally:
            motors.set(0, 0)
            self.camera.stop_recording(splitter_port=3)
            bus13.close()
            bus7.close()

    def join(self):
        self.running = False
        super().join()


class Framerate:
    def __init__(self):
        self.frametimes = deque(maxlen=5)
        self.starttime = time.perf_counter()
        self.fps = 0.0

    def update(self):
        t = time.perf_counter()
        self.frametimes.append(t - self.starttime)
        self.starttime = t
        self.fps = 1/(sum(self.frametimes)/len(self.frametimes))


class TargetFinder(PiRGBAnalysis):
    contour_colour = (0, 255, 0)
    marker_colour = (255, 0, 0)
    contour_thickness = 3

    def __init__(self, camera, colour, output):
        super().__init__(camera)
        self.colour(colour)
        self.output = output
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
        self.found_area = -1
        self.found_centroid = (0, 0)
        self.fps = Framerate()

    def colour(self, value=None):
        if value is not None:
            self._colour = value
            colour = np.uint8(getrgb(value)[::-1]).reshape((1, 1, 3))
            hsv = cv2.cvtColor(colour, cv2.COLOR_BGR2HSV).reshape((3))
            self.low = np.array([hsv[0] - 10, 50, 50])
            self.high = np.array([hsv[0] + 10, 255, 255])
        else:
            return self._colour

    def analyze(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.low, self.high)
        
        cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel, mask, iterations=2)
        cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel, mask, iterations=2)

        _, contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            moments_l = [cv2.moments(contour) for contour in contours]
            target_moments = max(moments_l, key=lambda m: m['m00'])
            self.found_area = target_moments['m00']
            self.found_centroid = (int(target_moments['m10']/target_moments['m00']),
                                   int(target_moments['m01']/target_moments['m00']))

            #cv2.drawContours(frame, contours, -1, self.contour_colour, self.contour_thickness)
            cv2.drawMarker(frame, self.found_centroid, self.marker_colour, thickness=3)
            cv2.putText(frame, str(self.found_area), 
                    (self.found_centroid[0] + 5, self.found_centroid[1]+5),
                    cv2.FONT_HERSHEY_PLAIN, 2, self.marker_colour, thickness=2)
        cv2.putText(frame, f"{self.fps.fps:.1f}", (10, 25),
                cv2.FONT_HERSHEY_PLAIN, 1, self.marker_colour, thickness=2)
        self.output.write(frame.data)
        self.fps.update()

if __name__ == "__main__":
    import picamera
    with picamera.camera(resolution=(640, 480), framerate=20) as camera:
        drive = DriveToColour(camera, MagicMock())
        drive.run()
