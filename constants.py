from panda3d.core import Vec3

# -------- Asset scales & spawn --------
TRACK_SCALE = 20.0
CAR_SCALE   = 0.45
CAR_SPAWN_POS = Vec3(0, -5, 0.20)
CAR_SPAWN_YAW = 0.0

# -------- Camera tuning --------
CAM_DISTANCE_DEFAULT = 200.0
CAM_DISTANCE_MIN     = 6.0
CAM_DISTANCE_MAX     = 200.0    # much farther so you can really pull back
CAM_ZOOM_SPEED       = 80.0     # units/sec when holding Z/X

CAM_HEIGHT_DEFAULT   = 28.66
CAM_HEIGHT_MIN       = 1.0
CAM_HEIGHT_MAX       = 60.0
CAM_HEIGHT_SPEED     = 20.0     # units/sec when holding Q/A
CAM_LAG              = 8.0      # follow "snappiness"

# -------- Car dynamics (arcade) --------
MAX_SPEED = 80.0
ACCEL     = 25.0
BRAKE     = 40.0
FRICTION  = 4.0
TURN_RATE = 90.0
TURN_MIN  = 25.0
# Multiplies forward displacement each frame (100.0 = 100× current speed)
SPEED_MULT = 100.0

# --- robust ground fit (tiny + safe) ---
# --- robust ground fit (tiny + safe) ---
GROUND_Z_MIN         = 0.25
GROUND_MAX_DEG_STEP  = 30.0
GROUND_SMOOTH_ALPHA  = 0.35
GROUND_RAY_HEIGHT    = 4.0
GROUND_RAY_LENGTH    = 30.0
SAMPLE_FWD_FRACTION  = 0.70
SAMPLE_REAR_FRACTION = 0.60
SAMPLE_W_FRAC        = 0.60

# --- new guards against early flips ---
MAX_SLOPE_DEG        = 55.0   # treat steeper surfaces like walls/curbs; pull toward world-up
DELTA_DEG_TRIGGER    = 10.0   # big change must persist before we accept it
ACCEPT_FRAMES        = 5      # consecutive frames required to accept a big change
