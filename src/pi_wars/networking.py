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

GLOBAL_CONF = {}
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
        if json.get('active_mode'):
            self.robot.change_mode(json['active_mode'])
        if json.get('stream_source'):
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
websocket_manager = websocket_plugin.manager
del websocket_plugin
# Only the manager is needed, so remove the binding to the plugin
# The plugin is still subscribed in the background


class JSMPEGWebSocket(WebSocket):
    def opened(self):
        self.send(JSMPEG_HEADER.pack(JSMPEG_MAGIC, WIDTH, HEIGHT), binary=True)


class StreamBroadcaster(Thread):
    def __init__(self, stream, websocket_manager):
        super().__init__()
        self.stream = stream
        self.websocket_manager = websocket_manager
        self.running = True

    def run(self):
        while self.running:
            buf = self.stream.read1(32768)
            if buf:
                self.websocket_manager.broadcast(buf, binary=True)
        for stream in self.streams.values():
            stream.close()

    def stop(self):
        self.running = False

    def start(self):
        super().start()
