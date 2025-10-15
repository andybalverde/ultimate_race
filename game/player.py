from panda3d.core import Vec3
from direct.task import Task

from constants import (
    MAX_SPEED, ACCEL, BRAKE, FRICTION, TURN_RATE, TURN_MIN,
    CAR_SCALE, CAR_SPAWN_POS, CAR_SPAWN_YAW,
    TRACK_SCALE, SPEED_MULT
)

from engine.assets import p3, TRACK, TESLA

class Player:
    def __init__(self, base, inputmap):
        self.base = base
        self.inp  = inputmap
        # Load track
        assert TRACK.exists(), f"Track not found: {TRACK}"
        self.track = base.loader.loadModel(p3(TRACK))
        self.track.reparentTo(base.render)
        self.track.setScale(TRACK_SCALE)

        # Load car
        assert TESLA.exists(), f"Car not found: {TESLA}"
        self.car = base.loader.loadModel(p3(TESLA))
        self.car.reparentTo(base.render)
        self.car.setScale(CAR_SCALE)
        self.car.setPos(CAR_SPAWN_POS)
        self.car.setHpr(CAR_SPAWN_YAW, 0, 0)

        self.speed = 0.0
        base.taskMgr.add(self._update, "player_update")


    def _update(self, task: Task):
        dt = min(self.base.clock.getDt(), 1/30)

        # Throttle / brake
        # Inverted: Up = brake, Down = accelerate
        if self.inp.held["up"]:
            self.speed -= BRAKE * dt
        if self.inp.held["down"]:
            self.speed += ACCEL * dt

        if not self.inp.held["up"] and not self.inp.held["down"]:
            if self.speed > 0:  self.speed = max(0.0, self.speed - FRICTION * dt)
            elif self.speed < 0: self.speed = min(0.0, self.speed + FRICTION * dt)

        self.speed = max(-10.0, min(MAX_SPEED, self.speed))

        # Steering
        steer_scale = TURN_MIN + (TURN_RATE - TURN_MIN) * min(1.0, abs(self.speed) / (0.6 * MAX_SPEED))
        # Inverted: Left turns right, Right turns left
        steer = (1.0 if self.inp.held["left"] else 0.0) + (-1.0 if self.inp.held["right"] else 0.0)
        self.car.setH(self.car.getH() + steer * steer_scale * dt * (1 if self.speed >= 0 else -1))

        # Advance forward along local Y (scaled)
        self.car.setPos(self.car, Vec3(0, self.speed * SPEED_MULT * dt, 0))

        return Task.cont
