class InputMap:
    """
    Simple held-key state map.
    Arrows = drive, Z/X = zoom out/in, Q/A = camera height up/down.
    """
    def __init__(self, base):
        self.held = {
            "up": False, "down": False, "left": False, "right": False,
            "zoom_out": False, "zoom_in": False,
            "cam_up": False, "cam_down": False,
        }

        b = base
        b.accept("arrow_up",       self._set, ["up", True])
        b.accept("arrow_up-up",    self._set, ["up", False])
        b.accept("arrow_down",     self._set, ["down", True])
        b.accept("arrow_down-up",  self._set, ["down", False])
        b.accept("arrow_left",     self._set, ["left", True])
        b.accept("arrow_left-up",  self._set, ["left", False])
        b.accept("arrow_right",    self._set, ["right", True])
        b.accept("arrow_right-up", self._set, ["right", False])

        # Zoom + camera height
        b.accept("z",     self._set, ["zoom_out", True])
        b.accept("z-up",  self._set, ["zoom_out", False])
        b.accept("x",     self._set, ["zoom_in", True])
        b.accept("x-up",  self._set, ["zoom_in", False])

        b.accept("q",     self._set, ["cam_up", True])
        b.accept("q-up",  self._set, ["cam_up", False])
        b.accept("a",     self._set, ["cam_down", True])
        b.accept("a-up",  self._set, ["cam_down", False])

    def _set(self, key, val):
        self.held[key] = val
