from math import exp
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import Vec3

from constants import (
    CAM_DISTANCE_DEFAULT, CAM_DISTANCE_MIN, CAM_DISTANCE_MAX, CAM_ZOOM_SPEED,
    CAM_HEIGHT_DEFAULT,   CAM_HEIGHT_MIN,   CAM_HEIGHT_MAX,   CAM_HEIGHT_SPEED,
    CAM_LAG,
)

class ChaseCamera:
    """
    Rally-style drone chase camera:
      - sticks behind & above the car using its real world-forward
      - smooth spring/lag for position
      - look-ahead down the road
      - Z/X: zoom  |  U/J: height
    """
    def __init__(self, base, target_np):
        self.base   = base
        self.target = target_np

        self.distance = float(CAM_DISTANCE_DEFAULT)
        self.height   = float(CAM_HEIGHT_DEFAULT)

        pos, look = self._desired()
        self.base.camera.setPos(pos)
        self.base.camera.lookAt(look)

        self._last_hud = None
        self.hud = OnscreenText(
            text="", pos=(-1.28, 0.93), scale=0.04,
            fg=(1, 1, 1, 1), align=0, mayChange=True, shadow=(0, 0, 0, 0.7)
        )
        self._update_hud(force=True)

    def apply_inputs(self, inputmap, dt: float):
        # Zoom
        if inputmap.held.get("zoom_in"):
            self.distance += CAM_ZOOM_SPEED * dt
        if inputmap.held.get("zoom_out"):
            self.distance -= CAM_ZOOM_SPEED * dt
        self.distance = max(CAM_DISTANCE_MIN, min(CAM_DISTANCE_MAX, self.distance))

        # Height (U/J)
        if inputmap.held.get("cam_up"):
            self.height += CAM_HEIGHT_SPEED * dt
        if inputmap.held.get("cam_down"):
            self.height -= CAM_HEIGHT_SPEED * dt
        self.height = max(CAM_HEIGHT_MIN, min(CAM_HEIGHT_MAX, self.height))

    def _target_forward_world(self):
        q = self.target.getQuat(self.base.render)
        fwd = q.xform(Vec3(0, 1, 0))
        fwd.normalize()
        return fwd

    def _desired(self):
        tpos = self.target.getPos(self.base.render)
        fwd  = self._target_forward_world()

        back = -fwd * self.distance
        cam_pos = tpos + back + Vec3(0, 0, self.height)

        look_ahead = 8.0
        look_up    = 1.5
        look = tpos + fwd * look_ahead + Vec3(0, 0, look_up)
        return cam_pos, look

    def _update_hud(self, force=False):
        txt = f"cam distance: {self.distance:.2f}   cam height: {self.height:.2f}   lag: {CAM_LAG:.1f}"
        if force or txt != self._last_hud:
            self.hud.setText(txt)
            self._last_hud = txt

    def update(self, dt: float):
        desired_pos, look = self._desired()
        alpha = 1.0 - exp(-CAM_LAG * dt)
        cur = self.base.camera.getPos(self.base.render)
        self.base.camera.setPos(cur + (desired_pos - cur) * alpha)
        self.base.camera.lookAt(look)
        self._update_hud()
