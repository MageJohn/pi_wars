#!/usr/bin/env python3

from struct import Struct
from threading import Thread

from ws4py.websocket import WebSocket
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

import cherrypy

# URLs provided by classes in this file:
# /                       - Browser redirect to /index.html
# /index.html             - Webapp main window
# /static/{js,html,css}/* - Static files
# /api                    - Robot state API endpoint, accepts GET and POST
# /ws                     - WebSocket endpoint

# TODO: Enable static file serving tool
# TODO: Enable websocket tool

WIDTH = 640
HEIGHT = 480
JSMPEG_MAGIC = b'jsmp'
JSMPEG_HEADER = Struct('>4sHH')


@cherrypy.expose
class RobotStateAPI:
    """
    API for reading and writing the robot state.
    """

    conf = {}

    def __init__(self, robot, stream_mux):
        self.robot = robot
        self.stream_mux = stream_mux

    @cherrypy.tools.json_out()
    def GET(self):
        """
        Handles a GET request to the API. Returns a json object with info about
        the current state of the robot.
        """
        return {'active_mode': self.robot.active_mode}

    @cherrypy.tools.json_in()
    def POST(self):
        json = cherrypy.request.json
        cherrypy.engine.log(f"Recieved json {json}")
        if 'active_mode' in json.keys():
            cherrypy.engine.log(f"Setting the active mode to {json['active_mode']}")
            self.robot.change_mode(json['active_mode'])
        if 'stream_source' in json.keys():
            cherrypy.engine.log(f"Setting the stream source to {json['stream_source']}")
            self.stream_mux.active_in = json['stream_source']


class RobotWebApp:
    @cherrypy.expose
    def index(self):
        raise cherrypy.InternalRedirect('/static/index.html')

    @cherrypy.expose
    def ws(self):
        pass


cherrypy.tools.websocket = WebSocketTool()
websocket_plugin = WebSocketPlugin(cherrypy.engine)
websocket_plugin.subscribe()


class JSMPEGWebSocket(WebSocket):
    def opened(self):
        self.send(JSMPEG_HEADER.pack(JSMPEG_MAGIC, WIDTH, HEIGHT), binary=True)


class StreamBroadcaster(Thread):
    def __init__(self, stream, websockets):
        super().__init__(daemon=True, name="StreamBroadcaster")
        self.stream = stream
        self.websockets = websockets

    def run(self):
        try:
            while True:
                buf = self.stream.read1(32768)
                self.websockets.broadcast(buf, binary=True)
        except ValueError:
            pass
        finally:
            self.stream.close()
