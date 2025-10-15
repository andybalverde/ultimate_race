from math import sin, cos, radians
from panda3d.core import Vec3, Point3

from constants import (
    CAM_DISTANCE_DEFAULT, CAM_DISTANCE_MIN, CAM_DISTANCE_MAX, CAM_ZOOM_SPEED,
    CAM_HEIGHT_DEFAULT, CAM_HEIGHT_MIN, CAM_HEIGHT_MAX, CAM_HEIGHT_SPEED,
    CAM_LAG
)

class ChaseCamera:
    def __init__(self, base, target_np):
        self.base = base
        self.target = target_np
        self.distance = CAM_DISTANCE_DEFAULT
        self.height   = CAM_HEIGHT_DEFAULT

        self.base.camera.setPos(0, -self.distance, self.height)
        self.base.camera.lookAt(self.target, Point3(0, 5, 1.5))

    def apply_inputs(self, inp, dt):
        # Zoom continuous while holding Z/X
        if inp.held["zoom_out"]:
            self.distance = min(CAM_DISTANCE_MAX, self.distance + CAM_ZOOM_SPEED * dt)
        if inp.held["zoom_in"]:
            self.distance = max(CAM_DISTANCE_MIN, self.distance - CAM_ZOOM_SPEED * dt)

        # Camera height Q/A
        if inp.held["cam_up"]:
            self.height = min(CAM_HEIGHT_MAX, self.height + CAM_HEIGHT_SPEED * dt)
        if inp.held["cam_down"]:
            self.height = max(CAM_HEIGHT_MIN, self.height - CAM_HEIGHT_SPEED * dt)

    def _desired(self):
        h = radians(self.target.getH())
        back = Vec3(-sin(h), -cos(h), 0) * self.distance
        target_pos = self.target.getPos(self.base.render)
        pos = target_pos + back + Vec3(0, 0, self.height)
        look = target_pos + Vec3(0, 5, 1.5)
        return pos, look

    def update(self, dt):
        desired_pos, look = self._desired()
        cur = self.base.camera.getPos()
        alpha = 1.0 - pow(0.001, dt * CAM_LAG)
        self.base.camera.setPos(cur + (desired_pos - cur) * alpha)
        self.base.camera.lookAt(look)
