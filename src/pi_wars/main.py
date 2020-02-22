#!/usr/bin/env python3

# TODO: Init:
# - [ ] Pipes
# - [ ] Networking process
# - [ ] Controller process
# - [ ] Image processing process
# - [ ] Robot settings server process
# - [ ] ffmpeg process
#
# Hook them all together, start them, then wait for them to finish.

import os
import os.path

import ffmpeg
import cherrypy
import picamera
from annotated import annotated

from robot import Robot
from modes import PS4ControllerMode
from networking import (
    StreamBroadcaster,
    JSMPEGWebSocket,
    websocket_manager,
    RobotWebApp,
    RobotStateAPI,
)


def start_ffmpeg(bitrate):
    return (
        ffmpeg.input("pipe:", format="rawvideo", pix_fmt="bgr24")
        .output("pipe:", format="mpeg1video", video_bitrate=bitrate)
        .run_async(pipe_stdin=True, pipe_stdout=True)
    )


class IoMuxer:
    """Provide a number of inputs and only and allow choosing which one gets to
    output"""

    def __init__(self, output, n_inputs):
        self.output = output
        self.inputs = [self.Input() for i in range(n_inputs)]
        self._active_in = self.inputs[0]

    @property
    def active_in(self):
        return self._active_in

    @active_in.setter
    @annotated
    def active_in(self, value: int):
        self._active_in = value

    class Input:
        def __init__(self, parent):
            self.parent = parent

        def write(self, buf):
            return self.parent._write(buf, self)

        def flush(self):
            self.parent._flush(self)

    def _write(self, buf, source):
        if source is self.active_in:
            return self.output.write(buf)
        else:
            return 0

    def _flush(self, source):
        if source is self.active_in:
            self.output.flush()


if __name__ == "__main__":
    camera = picamera.PiCamera(resolution=(640, 480), framerate=24)
    ffmpeg_proc = start_ffmpeg(bitrate=800)
    io_mux = IoMuxer(ffmpeg_proc.stdin, 2)
    camera.start_recording(output=io_mux.inputs[0], format="bgr", splitter_port=0)

    robot = Robot(
        modes={
            "ps4_controller": PS4ControllerMode(
                camera, io_mux.inputs[1]
            ),
        }
    )

    webapp = RobotWebApp()
    webapp.api = RobotStateAPI(robot, io_mux)

    cherrypy.tree.mount(
        webapp,
        "/",
        config={
            "/": {"tools.staticdir.root": os.path.abspath(os.getcwd())},
            "/ws": {
                "tools.websocket.on": True,
                "tools.websocket.handler_cls": JSMPEGWebSocket,
            },
            "/api": {"request.dispatch": cherrypy.dispatch.MethodDispatcher(),},
            "/static": {"tools.staticdir.on": True, "tools.staticdir.dir": "./website"},
        },
    )

    stream_broadcaster = StreamBroadcaster(
        ffmpeg_proc.stdout, websocket_manager
    ).start()

    robot.change_mode("ps4_controller")

    cherrypy.start()
    try:
        cherrypy.block()
    finally:
        robot.stop()
        camera.close()
        ffmpeg_proc.terminate()
