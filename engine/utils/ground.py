# engine/utils/ground.py
import math
from panda3d.core import Vec3, Quat, Mat3

from constants import (
    GROUND_Z_MIN, GROUND_MAX_DEG_STEP, GROUND_SMOOTH_ALPHA,
    GROUND_RAY_HEIGHT, GROUND_RAY_LENGTH,
    SAMPLE_FWD_FRACTION, SAMPLE_REAR_FRACTION, SAMPLE_W_FRAC,
    MAX_SLOPE_DEG,  # still used, but gently
)

WORLD_UP = Vec3(0, 0, 1)

class GroundSolver:
    """
    Minimal, conservative estimator:
      - 3 rays (FL, FR, RC) in car local space
      - plane fit if 3 points; else average valid normals
      - upward enforcement; gentle pull toward WORLD_UP on steep slopes
      - small temporal smoothing; small per-frame step clamp
    """
    def __init__(self, base):
        self.base = base
        self.last_up = Vec3(0, 0, 1)

    def _ray_down(self, origin_world: Vec3, length: float):
        to = origin_world - Vec3(0, 0, length)
        res = self.base.bworld.rayTestClosest(origin_world, to)
        if res.hasHit():
            return res.getHitPos(), res.getHitNormal()
        return None, None

    def estimate(self, car_np, half_w: float, half_l: float):
        r = self.base.render
        q = car_np.getQuat(r)
        pos = car_np.getPos(r)

        # sample offsets (local)
        off_fl = Vec3(  half_w * SAMPLE_W_FRAC,  half_l * SAMPLE_FWD_FRACTION, 0)
        off_fr = Vec3( -half_w * SAMPLE_W_FRAC,  half_l * SAMPLE_FWD_FRACTION, 0)
        off_rc = Vec3(  0.0,                    -half_l * SAMPLE_REAR_FRACTION, 0)

        points, normals, zs = [], [], []
        for off in (off_fl, off_fr, off_rc):
            origin = pos + q.xform(off) + Vec3(0, 0, GROUND_RAY_HEIGHT)
            hp, n = self._ray_down(origin, GROUND_RAY_LENGTH)
            if hp is None:
                continue
            if n.z < 0: n = -n
            if n.z >= GROUND_Z_MIN:
                points.append(hp)
                normals.append(n)
                zs.append(hp.z)

        if not points and not normals:
            return self.last_up, None

        # raw normal
        if len(points) >= 3:
            v1 = points[0] - points[2]
            v2 = points[1] - points[2]
            n = v1.cross(v2)
        else:
            n = Vec3(0, 0, 0)
            for u in normals: n += u

        if n.length_squared() == 0:
            n = self.last_up
        else:
            n.normalize()
            if n.z < 0: n = -n

        # gentle pull toward world-up only when very steep
        slope_deg = math.degrees(math.acos(max(-1.0, min(1.0, n.z))))
        if slope_deg > MAX_SLOPE_DEG:
            t = 0.6  # gentle (not heavy) pull
            n = (n * (1.0 - t) + WORLD_UP * t); n.normalize()

        # step clamp vs last_up
        max_dot = math.cos(math.radians(GROUND_MAX_DEG_STEP))
        d = max(-1.0, min(1.0, n.dot(self.last_up)))
        if d < max_dot:
            t = (max_dot - d) / (1.0 - d + 1e-6)
            n = (self.last_up * t + n * (1.0 - t))
            if n.length_squared() > 0: n.normalize()

        # small smoothing
        up = (self.last_up * (1.0 - GROUND_SMOOTH_ALPHA) + n * GROUND_SMOOTH_ALPHA)
        if up.length_squared() > 0: up.normalize()

        z_suggest = None if not zs else sorted(zs)[len(zs)//2]

        self.last_up = up
        return up, z_suggest


# ----- Chassis build (yaw preserved) -----------------------------------------
def build_tilted_chassis(yaw_deg: float, up: Vec3):
    """
    Keep yaw from steering, then tilt the chassis so its Z aligns with 'up'.
    Steps:
      1) q_yaw: rotation about WORLD_UP by yaw.
      2) q_tilt: shortest-arc rotation aligning WORLD_UP -> up.
      3) fwd = q_tilt * (q_yaw * +Y)
      4) right = fwd x up ; rebuild orthonormal frame → quaternion.
    This avoids the fragile cross-product permutations and preserves yaw.
    """
    # q_yaw about world Z
    q_yaw = Quat()
    q_yaw.setHpr((yaw_deg, 0.0, 0.0))

    # shortest rotation from WORLD_UP to 'up'
    up_n = up if up.length_squared() > 0 else WORLD_UP
    up_n = up_n.normalized()
    axis = WORLD_UP.cross(up_n)
    axis_len2 = axis.length_squared()
    if axis_len2 < 1e-10:
        q_tilt = Quat()  # identity (already aligned)
    else:
        axis.normalize()
        cosang = max(-1.0, min(1.0, WORLD_UP.dot(up_n)))
        ang = math.degrees(math.acos(cosang))
        q_tilt = Quat()
        q_tilt.setFromAxisAngle(ang, axis)

    # forward: yawed +Y, then tilted
    fwd_world = q_yaw.xform(Vec3(0, 1, 0))
    fwd = q_tilt.xform(fwd_world)
    # remove any tiny component along 'up' and renormalize
    fwd = fwd - up_n * fwd.dot(up_n)
    if fwd.length_squared() < 1e-9:
        fwd = Vec3(1, 0, 0)  # safe fallback
    fwd.normalize()

    right = fwd.cross(up_n); right.normalize()
    fwd   = up_n.cross(right); fwd.normalize()

    m = Mat3()
    m.setRow(0, right)
    m.setRow(1, fwd)
    m.setRow(2, up_n)

    q = Quat()
    q.setFromMatrix(m)
    return q
