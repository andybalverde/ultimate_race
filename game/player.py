# game/player.py
import math
from panda3d.core import Vec3, TransformState, BitMask32
from direct.task import Task
from panda3d.bullet import BulletTriangleMesh, BulletTriangleMeshShape, BulletRigidBodyNode

from constants import (
    MAX_SPEED, ACCEL, BRAKE, FRICTION, TURN_RATE, TURN_MIN,
    CAR_SCALE, CAR_SPAWN_POS, CAR_SPAWN_YAW,
    TRACK_SCALE, SPEED_MULT,
)
from engine.assets import p3, TRACK, TESLA
from engine.utils.ground import GroundSolver, build_tilted_chassis


class Player:
    def __init__(self, base, inputmap):
        self.base = base
        self.inp = inputmap

        # --- Track (visual) ---
        self.track = base.loader.loadModel(p3(TRACK))
        self.track.reparentTo(base.render)
        self.track.setScale(TRACK_SCALE)

        # --- Static collider from visual track ---
        mesh = BulletTriangleMesh()
        for np in self.track.find_all_matches('**/+GeomNode'):
            gnode = np.node()
            net = np.getNetTransform()
            for i in range(gnode.get_num_geoms()):
                geom = gnode.get_geom(i)
                mesh.addGeom(geom, True, TransformState.makeMat(net.getMat()))
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        rb = BulletRigidBodyNode('track_static')
        rb.addShape(shape)
        rb.setMass(0.0)
        self.track_phys = self.base.render.attachNewNode(rb)
        self.track_phys.setCollideMask(BitMask32.allOn())
        self.base.bworld.attach(rb)

        # --- Car (visual only) ---
        self.car = base.loader.loadModel(p3(TESLA))
        self.car.reparentTo(base.render)
        self.car.setScale(CAR_SCALE)
        self.car.setPos(CAR_SPAWN_POS)
        self.car.setHpr(CAR_SPAWN_YAW + 90.0, 0.0, 0.0)

        # Ride clearance
        self.ride_clearance = 0.25

        # Half-extents for sampling
        bmin, bmax = self.car.getTightBounds()
        dims = bmax - bmin
        self.half_w = 0.5 * abs(dims.x)
        self.half_l = 0.5 * abs(dims.y)

        # Drive state
        self.speed = 0.0

        # Ground solver
        self.ground = GroundSolver(base)

        base.taskMgr.add(self._update, "player_update")

    # ---------- Driving (arcade) ----------
    def _apply_drive(self, dt: float):
        if self.inp.held.get("up"):    self.speed += ACCEL * dt
        if self.inp.held.get("down"):  self.speed -= BRAKE * dt

        if not self.inp.held.get("up") and not self.inp.held.get("down"):
            if self.speed > 0:  self.speed = max(0.0, self.speed - FRICTION * dt)
            if self.speed < 0:  self.speed = min(0.0, self.speed + FRICTION * dt)

        self.speed = max(-10.0, min(MAX_SPEED, self.speed))

        steer = (1.0 if self.inp.held.get("left") else 0.0) + (-1.0 if self.inp.held.get("right") else 0.0)
        steer_scale = TURN_MIN + (TURN_RATE - TURN_MIN) * min(1.0, abs(self.speed) / (0.6 * MAX_SPEED))
        self.car.setH(self.car.getH() + steer * steer_scale * dt * (1 if self.speed >= 0 else -1))

        self.car.setPos(self.car, Vec3(0, self.speed * SPEED_MULT * dt, 0))

    # ---------- Ground follow / banking ----------
    def _apply_ground_follow(self):
        yaw = self.car.getH()
        up, z_suggest = self.ground.estimate(self.car, self.half_w, self.half_l)

        # Roll/pitch from ground; yaw stays exactly as steering decided
        q = build_tilted_chassis(yaw, up)
        self.car.setQuat(q)
        self.car.setH(yaw)

        if z_suggest is not None:
            self.car.setZ(z_suggest + self.ride_clearance)

    # ---------- Per-frame ----------
    def _update(self, task: Task):
        dt = min(self.base.clock.getDt(), 1 / 30.0)
        self._apply_drive(dt)
        self._apply_ground_follow()
        return Task.cont
