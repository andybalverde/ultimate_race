from panda3d.core import Vec3

# -------- Per-track defaults (spawn & scale) ----------------------------------
# Tweak from HUD, then bake your final values here.
# Spielberg is kept exactly as your working MVP.
TRACK_DEFAULTS = {
    "usa_spielberg": {
        "scale": 20.0,
        "spawn_pos": Vec3(0, -5, 0.20),  # starting/finish line you already liked
        "spawn_yaw": 0.0,                # car H, we add +90° in player to align Tesla +Y forward
    },
    "bahrain": {
        "scale": 20.0,
        "spawn_pos": Vec3(0, 0, 1.0),    # placeholder until you HUD-lock it
        "spawn_yaw": 0.0,
    },
    "bermudas": {
        "scale": 31.03,
        "spawn_pos": Vec3(-1578.41, 598.14, -7.41),
        "spawn_yaw": 279.24,
    },

    "scotland": {
        "scale": 25.41,
        "spawn_pos": Vec3(20786.24, -27910.24, 23.58),
        "spawn_yaw": 360.22,
    },

}

# -------- Camera tuning --------
CAM_DISTANCE_DEFAULT = 200.0
CAM_DISTANCE_MIN     = 6.0
CAM_DISTANCE_MAX     = 200.0
CAM_ZOOM_SPEED       = 80.0

CAM_HEIGHT_DEFAULT   = 28.66
CAM_HEIGHT_MIN       = 1.0
CAM_HEIGHT_MAX       = 60.0
CAM_HEIGHT_SPEED     = 20.0
CAM_LAG              = 8.0

# -------- Car dynamics (arcade) --------
MAX_SPEED = 80.0
ACCEL     = 25.0
BRAKE     = 40.0
FRICTION  = 4.0
TURN_RATE = 90.0
TURN_MIN  = 25.0
SPEED_MULT = 100.0

# -------- Ground fit / banking (unchanged from your last good state) --------
GROUND_Z_MIN         = 0.25
GROUND_MAX_DEG_STEP  = 30.0
GROUND_SMOOTH_ALPHA  = 0.35
GROUND_RAY_HEIGHT    = 4.0
GROUND_RAY_LENGTH    = 30.0
SAMPLE_FWD_FRACTION  = 0.70
SAMPLE_REAR_FRACTION = 0.60
SAMPLE_W_FRAC        = 0.60

MAX_SLOPE_DEG        = 55.0
DELTA_DEG_TRIGGER    = 10.0
ACCEPT_FRAMES        = 5

# -------- DEV helpers ---------------------------------------------------------
DEV_FLY_SPEED = 12.0        # meters/sec for Q/A vertical nudging
SCALE_STEP    = 0.5         # amount added/subtracted to the track scale per second while holding P/M
