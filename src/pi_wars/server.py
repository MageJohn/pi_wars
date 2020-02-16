#!/usr/bin/env python3

import socketserver
import io
import logging
import subprocess
import threading
from http import server

import cv2
import numpy as np
import picamera


PAGE = """\
<html>
<head>
<title>picamera MJPEG streaming demo</title>
</head>
<body>
<h1>PiCamera MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""


class StreamingOutput:
    def __init__(self, camera):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = threading.Condition()
        # Size in bytes
        self.camera = camera

    def write(self, buf):
        try:
            written = self.buffer.write(buf)
            res = self.camera.resolution
            if self.buffer.tell() == (res[0] * res[1] * 3):
                with self.condition:
                    self.analyze()
                    self.buffer.truncate()
                    self.frame = self.buffer.getvalue()
                    self.condition.notify_all()
                self.buffer.seek(0)
            return written
        except Exception as e:
            logging.error(e)

    def analyze(self):
        frame = np.frombuffer(self.buffer.getvalue(), dtype=np.uint8)
        frame = frame.reshape([*self.camera.resolution[::-1], 3])

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        low = np.array([-10, 50, 50])
        high = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, low, high)
        res = cv2.bitwise_and(frame, frame, mask=mask)

        retval, buf = cv2.imencode(".jpeg", res)
        self.buffer.seek(0)
        self.buffer.write(buf)


class StreamingHandler(server.BaseHTTPRequestHandler):
    output = None

    def __init__(self, *args, **kwargs):
        if self.output is None:
            raise Exception("output not set on StreamingHandler")
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == "/":
            self.send_response(301)
            self.send_header("Location", "/index.html")
            self.end_headers()
        elif self.path == "/index.html":
            self.get_html(self.path)
        elif self.path == "/stream.mjpg":
            self.get_stream()
        elif self.path == "/start_proc":
            self.start_proc()
        elif self.path == "/end_proc":
            self.end_proc()
        else:
            self.send_error(404)
            self.end_headers()

    def get_stream(self):
        self.send_response(200)
        self.send_header("Age", 0)
        self.send_header("Cache-Control", "no-cache, private")
        self.send_header("Pragma", "no-cache")
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
        self.end_headers()
        try:
            while True:
                with self.output.condition:
                    self.output.condition.wait()
                    frame = self.output.frame
                self.wfile.write(b"--FRAME\r\n")
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", len(frame))
                self.end_headers()
                self.wfile.write(frame)
                self.wfile.write(b"\r\n")
        except Exception as e:
            logging.warning(
                "Removed streaming client %s: %s", self.client_address, str(e)
            )

    def get_html(self, path):
        content = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", len(content))
        self.end_headers()
        self.wfile.write(content)

    def start_proc(self):
        if self.headers["Subprocess-Cmdline"]:
            self.send_response(200)
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header("Content-Type", "application/json")
            self.subproc_event = threading.Event()
            proc_id, event = self.server.register_subproc()
            self.send_header("Subprocess-Id", f"{proc_id}")
            self.end_headers()
            try:
                proc = subprocess.Popen(
                    self.headers["Subprocess-Cmdline"],
                    stdout=self.wfile,
                    stderr=self.wfile,
                    bufsize=0,
                    shell=True,
                )
                logging.info(
                    f"""Started process with internal id {proc_id} and command line:\
                    {self.headers['Subprocess-Cmdline']}"""
                )
                while proc.poll() is None:
                    if event.is_set():
                        proc.kill()
                        break
                self.wfile.write(f"Return code: {proc.returncode}")

            except Exception as e:
                logging.warning(f"Removed subprocess client {self.client_address}: {e}")
        else:
            self.send_response(400)

    def end_proc(self):
        proc_id = self.headers["Subprocess-Id"]
        if (
            proc_id is None
            or not proc_id.isdecimal()
            or not self.server.end_subproc(int(proc_id))
        ):
            self.send_response(400)
            logging.warning("Request did not give a valid process id")

        self.send_response(200)


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True
    _subprocs = None

    def __init__(self, *args, **kwargs):
        self.lock = threading.Lock()
        super().__init__(*args, **kwargs)

    def register_subproc(self):
        with self.lock:
            if self._subprocs is None:
                self._subprocs = []
            self._subprocs.append(threading.Event())
            return len(self._subprocs) - 1, self._subprocs[-1]

    def end_subproc(self, proc_id):
        with self.lock:
            if self._subproc is None or proc_id >= len(self._subprocs):
                logging.warning(
                    f"Client requested to kill unknown process id {proc_id}"
                )
                return False
            else:
                self._subproc[proc_id].set()
                return True


def main():
    with picamera.PiCamera(resolution="640x480", framerate=24) as camera:
        output = StreamingOutput(camera)
        StreamingHandler.output = output
        camera.start_recording(output, format="bgr")
        try:
            address = ("", 8000)
            server = StreamingServer(address, StreamingHandler)
            server.serve_forever()
        finally:
            camera.stop_recording()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
