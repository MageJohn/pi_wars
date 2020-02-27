from evdev import InputDevice, ecodes, list_devices


class Stick:
    def __init__(self, axis_x, axis_y, deadzone=0.05):
        # pass axis in as an event.code.ecodes
        self.axes = (axis_x, axis_y)
        self.value = [0, 0]
        self.mapped_events = {
            (ecodes.EV_ABS, axis_x): self,
            (ecodes.EV_ABS, axis_y): self,
        }
        self.dz = deadzone

    def handle_event(self, event):
        value = (event.value - 128) / 128
        if abs(value) <= self.dz:
            value = 0
        self.value[self.axes.index(event.code)] = value


class Controller:
    def __init__(self, device, modules):
        self.device = device
        self.mapped_events = {}
        for m in modules:
            self.mapped_events.update(m.mapped_events)

    def read_loop(self):
        for event in self.device.read_loop():
            yield self._handle_event(event)

    def read_one(self):
        event = self.device.read_one()
        if event is not None:
            return self._handle_event(event)

    def _handle_event(self, event):
        handler = self.mapped_events.get((event.type, event.code))
        if handler is not None:
            handler.handle_event(event)
            return True


if __name__ == "__main__":
    device = InputDevice(list_devices()[0])
    stick = Stick(ecodes.ABS_X, ecodes.ABS_Y)
    controller = Controller(device, [stick])
    for _ in controller.read_loop():
        print(stick.value)
