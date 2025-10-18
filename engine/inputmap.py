class InputMap:
    """
    Held-key map shared by systems once you're IN the race scene.
    Arrows  = drive
    Z / X   = camera zoom out / in
    U / J   = camera height up / down
    Q / A   = DEV: car fly up / down
    P / M   = DEV: track scale up / down
    """
    def __init__(self, base):
        self.held = {
            "up": False, "down": False, "left": False, "right": False,
            "zoom_out": False, "zoom_in": False,
            "cam_up": False, "cam_down": False,
            "fly_up": False, "fly_down": False,
            "scale_up": False, "scale_down": False,
        }

        b = base
        # Driving
        b.accept("arrow_up",       self._set, ["up", True])
        b.accept("arrow_up-up",    self._set, ["up", False])
        b.accept("arrow_down",     self._set, ["down", True])
        b.accept("arrow_down-up",  self._set, ["down", False])
        b.accept("arrow_left",     self._set, ["left", True])
        b.accept("arrow_left-up",  self._set, ["left", False])
        b.accept("arrow_right",    self._set, ["right", True])
        b.accept("arrow_right-up", self._set, ["right", False])

        # Camera zoom
        b.accept("z",     self._set, ["zoom_out", True])
        b.accept("z-up",  self._set, ["zoom_out", False])
        b.accept("x",     self._set, ["zoom_in", True])
        b.accept("x-up",  self._set, ["zoom_in", False])

        # Camera height (U/J only; Q/A reserved for dev fly)
        b.accept("u",     self._set, ["cam_up", True])
        b.accept("u-up",  self._set, ["cam_up", False])
        b.accept("j",     self._set, ["cam_down", True])
        b.accept("j-up",  self._set, ["cam_down", False])

        # DEV: car fly
        b.accept("q",     self._set, ["fly_up", True])
        b.accept("q-up",  self._set, ["fly_up", False])
        b.accept("a",     self._set, ["fly_down", True])
        b.accept("a-up",  self._set, ["fly_down", False])

        # DEV: live scale of track
        b.accept("p",     self._set, ["scale_up", True])
        b.accept("p-up",  self._set, ["scale_up", False])
        b.accept("m",     self._set, ["scale_down", True])
        b.accept("m-up",  self._set, ["scale_down", False])

    def _set(self, key, val):
        self.held[key] = val
