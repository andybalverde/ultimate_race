# game/player.py
from math import sin, cos, radians
from panda3d.core import Vec3, Quat, Mat3, TransformState, BitMask32
from direct.task import Task
from panda3d.bullet import (
    BulletTriangleMesh, BulletTriangleMeshShape, BulletRigidBodyNode
)

from constants import (
    MAX_SPEED, ACCEL, BRAKE, FRICTION, TURN_RATE, TURN_MIN,
    CAR_SCALE, CAR_SPAWN_POS, CAR_SPAWN_YAW,
    TRACK_SCALE, SPEED_MULT
)
from engine.assets import p3, TRACK, TESLA


class Player:
    def __init__(self, base, inputmap):
        self.base = base
        self.inp = inputmap

        # ---------- Load track (visual) ----------
        assert TRACK.exists(), f"Track not found: {TRACK}"
        self.track = base.loader.loadModel(p3(TRACK))
        self.track.reparentTo(base.render)
        self.track.setScale(TRACK_SCALE)

        # ---------- Build static Bullet collider from the visual track ----------
        # Bake each Geom into a single BulletTriangleMesh using the net transform,
        # so physics and visuals line up perfectly (including scale).
        mesh = BulletTriangleMesh()
        for np in self.track.find_all_matches('**/+GeomNode'):
            gnode = np.node()
            net = np.getNetTransform()
            for i in range(gnode.get_num_geoms()):
                geom = gnode.get_geom(i)
                mesh.addGeom(geom, True, TransformState.makeMat(net.getMat()))

        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        track_rb = BulletRigidBodyNode('track_static')
        track_rb.addShape(shape)
        track_rb.setMass(0.0)  # static
        self.track_phys = self.base.render.attachNewNode(track_rb)
        self.track_phys.setCollideMask(BitMask32.allOn())
        self.base.bworld.attach(track_rb)

        # ---------- Load car (visual) ----------
        assert TESLA.exists(), f"Car not found: {TESLA}"
        self.car = base.loader.loadModel(p3(TESLA))
        self.car.reparentTo(base.render)
        self.car.setScale(CAR_SCALE)
        self.car.setPos(CAR_SPAWN_POS)
        self.car.setHpr(CAR_SPAWN_YAW + 90.0, 0, 0)

        # Dynamics state
        self.speed = 0.0

        # Per-frame update
        base.taskMgr.add(self._update, "player_update")

    # ------ simple helpers ------
    def _apply_drive(self, dt: float):
        # Throttle / brake / friction
        if self.inp.held.get("up"):
            self.speed += ACCEL * dt
        if self.inp.held.get("down"):
            self.speed -= BRAKE * dt

        if not self.inp.held.get("up") and not self.inp.held.get("down"):
            if self.speed > 0:
                self.speed = max(0.0, self.speed - FRICTION * dt)
            elif self.speed < 0:
                self.speed = min(0.0, self.speed + FRICTION * dt)

        # Clamp
        self.speed = max(-10.0, min(MAX_SPEED, self.speed))

        # Steering (scale with speed; invert for reverse)
        steer_scale = TURN_MIN + (TURN_RATE - TURN_MIN) * min(1.0, abs(self.speed) / (0.6 * MAX_SPEED))
        steer = (1.0 if self.inp.held.get("left") else 0.0) + (-1.0 if self.inp.held.get("right") else 0.0)
        self.car.setH(self.car.getH() + steer * steer_scale * dt * (1 if self.speed >= 0 else -1))

        # Forward along local Y (don’t touch Z here; ground-follow fixes it)
        self.car.setPos(self.car, Vec3(0, self.speed * SPEED_MULT * dt, 0))

    def _ground_follow(self):
        """
        Raycast down and snap the car to the terrain.
        Optional: align pitch/roll to the surface normal (banking).
        """
        # Start above car center, cast down
        cpos = self.car.getPos(self.base.render)
        ray_from = cpos + Vec3(0, 0, 2.0)
        ray_to = cpos + Vec3(0, 0, -50.0)

        hit = self.base.bworld.rayTestClosest(ray_from, ray_to)
        if not hit.hasHit():
            return  # nothing below (edge of world?), leave Z unchanged

        hp = hit.getHitPos()       # hit point
        hn = hit.getHitNormal()    # surface normal

        # Keep wheels slightly above ground (tweak to your wheel radius)
        WHEEL_CLEARANCE = 0.25
        self.car.setZ(hp.z + WHEEL_CLEARANCE)

        # ------- OPTIONAL BANKING -------
        # Comment this block if you want to keep the car perfectly upright.
        yaw = self.car.getH()

        # World forward from yaw
        fwd_yaw = Vec3(sin(radians(yaw)), cos(radians(yaw)), 0)
        if fwd_yaw.length_squared() == 0:
            return
        fwd_yaw.normalize()

        up = hn.normalized()
        right = fwd_yaw.cross(up)
        if right.length_squared() < 1e-6:
            return  # degenerate frame on near-vertical walls
        right.normalize()
        fwd = right.cross(up)  # <— flip to fix pitch (nose now tilts uphill)
        fwd.normalize()

        mat = Mat3(
            right.x, right.y, right.z,
            fwd.x,   fwd.y,   fwd.z,
            up.x,    up.y,    up.z
        )
        q = Quat()
        q.setFromMatrix(mat)
        self.car.setQuat(q)
        self.car.setH(yaw)  # keep heading from steering input

    # ------ per-frame update ------
    def _update(self, task: Task):
        dt = min(self.base.clock.getDt(), 1 / 30.0)

        self._apply_drive(dt)
        self._ground_follow()

        return Task.cont
