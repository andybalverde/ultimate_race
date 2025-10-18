import math
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import Vec3, TransformState, BitMask32
from direct.task import Task
from panda3d.bullet import BulletTriangleMesh, BulletTriangleMeshShape, BulletRigidBodyNode

from constants import (
    MAX_SPEED, ACCEL, BRAKE, FRICTION, TURN_RATE, TURN_MIN,
    SPEED_MULT, DEV_FLY_SPEED, SCALE_STEP,
)
from engine.assets import p3, TESLA
from engine.utils.ground import GroundSolver, build_tilted_chassis


class Player:
    """
    One race scene:
      - loads the chosen track model and Tesla
      - arcade drive + ground follow
      - DEV controls: Q/A fly, P/M live scale
      - HUD shows pos/orientation + track name & scale
    """
    def __init__(self, base, inputmap, track_def, defaults):
        self.base = base
        self.inp = inputmap
        self.track_def = track_def
        self.defaults = defaults  # dict with scale/spawn_pos/spawn_yaw

        # --- Track (visual) ---
        self.track = base.loader.loadModel(p3(track_def["model"]))
        self.track.reparentTo(base.render)
        self.scale = float(defaults["scale"])
        self.track.setScale(self.scale)

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
        self.car.setScale(0.45)  # Tesla scale stays the same as before
        self.car.setPos(defaults["spawn_pos"])
        self.car.setHpr(defaults["spawn_yaw"] + 90.0, 0.0, 0.0)

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

        # DEV HUD
        self.hud = OnscreenText(
            text="", pos=(-1.28, 0.86), scale=0.038,
            fg=(0.9, 1.0, 0.9, 1), align=0, mayChange=True, shadow=(0, 0, 0, 0.7)
        )
        self._refresh_hud(force=True)

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

        # Forward movement along car's local +Y
        self.car.setPos(self.car, Vec3(0, self.speed * SPEED_MULT * dt, 0))

        # DEV: vertical fly (Q/A)
        if self.inp.held.get("fly_up"):
            self.car.setZ(self.car.getZ() + DEV_FLY_SPEED * dt)
        if self.inp.held.get("fly_down"):
            self.car.setZ(self.car.getZ() - DEV_FLY_SPEED * dt)

        # DEV: live scale (P/M)
        changed = False
        if self.inp.held.get("scale_up"):
            self.scale += SCALE_STEP * dt
            changed = True
        if self.inp.held.get("scale_down"):
            self.scale = max(0.05, self.scale - SCALE_STEP * dt)
            changed = True
        if changed:
            self.track.setScale(self.scale)

    # ---------- Ground follow / banking ----------
    def _apply_ground_follow(self):
        yaw = self.car.getH()
        up, z_suggest = self.ground.estimate(self.car, self.half_w, self.half_l)

        q = build_tilted_chassis(yaw, up)
        self.car.setQuat(q)
        self.car.setH(yaw)

        if z_suggest is not None:
            self.car.setZ(z_suggest + self.ride_clearance)

    # ---------- HUD ----------
    def _refresh_hud(self, force=False):
        pos = self.car.getPos(self.base.render)
        h, p, r = self.car.getHpr()
        txt = (
            f"[{self.track_def['name']}] scale:{self.scale:.2f}  "
            f"X:{pos.x:7.2f}  Y:{pos.y:7.2f}  Z:{pos.z:6.2f}  "
            f"H:{h:6.2f}  P:{p:5.2f}  R:{r:5.2f}  "
            f"  (Q/A fly  P/M scale)"
        )
        if force or txt != getattr(self, "_last_txt", None):
            self.hud.setText(txt)
            self._last_txt = txt

    # ---------- Per-frame ----------
    def _update(self, task: Task):
        dt = min(self.base.clock.getDt(), 1 / 30.0)
        self._apply_drive(dt)
        self._apply_ground_follow()
        self._refresh_hud()
        return Task.cont
