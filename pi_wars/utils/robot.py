#!/usr/bin/env python3

from threading import Event


class Robot:
    """
    Parameters:
        modes: mapping of mode names to subclasses of RobotModeBase
    """
    def __init__(self, modes=None):
        self.modes = modes if modes is not None else {}
        self._active_mode = None

    @property
    def active_mode(self):
        return self._active_mode

    def change_mode(self, value):
        if self._active_mode is not None:
            self.modes[self._active_mode].join()
        self.modes[value].start()
        self._active_mode = value

    def stop(self):
        if self._active_mode is not None:
            self.modes[self._active_mode].join()
