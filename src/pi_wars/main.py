#!/usr/bin/env python3

import os
import os.path
from threading import Thread

import ffmpeg
import cherrypy
import picamera
from annotated import annotated
from ws4py.websocket import WebSocket

from robot import Robot
from ps4_controller import PS4ControllerMode
from drive_to_colour import DriveToColour
from networking import (
    StreamBroadcaster,
    JSMPEGWebSocket,
    websocket_plugin,
    RobotWebApp,
    RobotStateAPI,
)


class IoMuxer:
    """Provide a number of inputs and allow choosing which one gets to
    output"""

    def __init__(self, n_inputs=2, output=None):
        self.output = output
        self.inputs = [self.Input(self) for i in range(n_inputs)]
        self._active_in = self.inputs[0]

    @property
    def active_in(self):
        return self.inputs.index(self._active_in)

    @active_in.setter
    @annotated
    def active_in(self, value: int):
        self._active_in = self.inputs[value]

    def add_input(self):
        """Add an input and return it's index"""
        self.inputs.append(self.Input(self))
        return len(self.inputs) - 1

    class Input:
        def __init__(self, parent):
            self.parent = parent

        def write(self, buf):
            return self.parent._write(buf, self)

        def flush(self):
            self.parent._flush()

    def _write(self, buf, source):
        if self.output is None or source is not self._active_in:
            return len(buf)
        else:
            return self.output.write(buf)

    def _flush(self):
        self.output.flush()


class Converter:
    def __init__(self, camera):
        ffmpeg_cmd = (
            ffmpeg.input(
                "pipe:",
                format="rawvideo",
                pix_fmt="bgr24",
                s=f"{camera.resolution[0]}x{camera.resolution[1]}",
                r=str(float(camera.framerate))
            )
            .output(
                "http://localhost:8081/websocketrelay", 
                format="mpegts",
                vcodec="mpeg1video",
                video_bitrate="1000k",
                bf=0,
                r=str(float(camera.framerate)),
                s=f"{camera.resolution[0]}x{camera.resolution[1]}"
            )
        )
        cherrypy.engine.log(f"Starting ffmpeg with cmdline: \nffmpeg {' '.join(ffmpeg.get_args(ffmpeg_cmd))}")
        self.converter = ffmpeg_cmd.run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
    
    def write(self, buf):
        return self.converter.stdin.write(buf)

    def flush(self):
        cherrypy.engine.log("Waiting for ffmpeg to finish")
        self.converter.communicate()


if __name__ == "__main__":
    camera = picamera.PiCamera(resolution=(640, 480), framerate=30)
    cherrypy.engine.log("Opened camera")

    io_mux = IoMuxer()
    cherrypy.engine.log("Created IoMuxer")

    robot = Robot(
        modes={
            "ps4_controller": PS4ControllerMode(
                camera, io_mux.inputs[1]
            ),
            "drive_to_colour": DriveToColour(
                camera, io_mux.inputs[1]
            ),
        }
    )
    cherrypy.engine.log("Created robot")

    cherrypy.config.update({'server.socket_host': '0.0.0.0'})

    webapp = RobotWebApp()
    webapp.api = RobotStateAPI(robot, io_mux)

    cherrypy.tree.mount(webapp, "",
                config={
                    "/": {
                        "tools.staticdir.root": os.path.abspath(os.getcwd()),
                        },
                    "/ws": {
                        "tools.websocket.on": True,
                        "tools.websocket.handler_cls": WebSocket,
                      },
                    "/api": {"request.dispatch": cherrypy.dispatch.MethodDispatcher(),},
                    "/static": {"tools.staticdir.on": True, "tools.staticdir.dir": "./website"},
                  },
    )
    cherrypy.engine.log("Initialised cherrypy tree")

    video_converter = Converter(camera)
    io_mux.output = video_converter

    #stream_broadcaster = StreamBroadcaster(
    #    video_converter.converter.stdout, websocket_plugin
    #)
    #cherrypy.engine.log("Initialised stream broadcaster")

    camera.start_recording(output=io_mux.inputs[0], format="bgr")
    cherrypy.engine.log("Started camera recording")

    robot.change_mode("drive_to_colour")
    cherrypy.engine.log("Set default robot mode")

    io_mux.active_in = 1

    try:
        cherrypy.engine.log("Starting cherrypy")
        cherrypy.engine.start()
        #cherrypy.engine.log("Starting stream broadcaster")
        #stream_broadcaster.start()
        cherrypy.engine.block()
    except KeyboardInterrupt:
        pass
    finally:
        cherrypy.engine.log("Stopping recording")
        camera.stop_recording()
        #cherrypy.engine.log("Waiting for stream broadcaster to finish")
        #stream_broadcaster.join()
        cherrypy.engine.log("Shutting down cherrypy")
        cherrypy.engine.exit()
        cherrypy.engine.log("Closing camera")
        camera.close()
