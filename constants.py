from panda3d.core import Vec3

# -------- Asset scales & spawn --------
TRACK_SCALE = 8.0
CAR_SCALE   = 0.45
CAR_SPAWN_POS = Vec3(0, -5, 0.20)
CAR_SPAWN_YAW = 0.0

# -------- Camera tuning --------
CAM_DISTANCE_DEFAULT = 18.0
CAM_DISTANCE_MIN     = 6.0
CAM_DISTANCE_MAX     = 200.0    # much farther so you can really pull back
CAM_ZOOM_SPEED       = 80.0     # units/sec when holding Z/X

CAM_HEIGHT_DEFAULT   = 3.0
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