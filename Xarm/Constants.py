from Boundaries import *

Y_DETECTION_BOUNDARY_FOR_LOAD = 260

WAIT_TIME_BEFORE_STOP_TRACKING = 5


LOAD_GRIP_Z = 244
LOAD_INIT_Z = 300
LOAD_POSITIONS = ((304,  373, LOAD_INIT_Z), 
                  (149, 358, LOAD_INIT_Z), 
                  (-10,  353, LOAD_INIT_Z),
                  (-251,  339,  LOAD_INIT_Z), 
                  (-413, 327,  LOAD_INIT_Z))
DROP_POSITIONS = ((235, -200, 400),
                    (235, -100, 400),
                    (235,   0, 400),
                    (235, 100, 400),
                    (235, 200, 400))

MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 45
MQTT_TOPIC = "xarmSpheroEvents"

WARMUP_CAM = 1

SCAN_NEXT_Y = 125
SCAN_NEXT_X = 135

START_X = 175
START_Y = 0
START_Z = 400

START_POS = (START_X, START_Y, START_Z)

Z_MIN = 219
Z_MAX = 550

OUTER_BOUNDARY = SquareBoundary(
    xMin=-414.8, xMax=421.2,
    yMin=-411.3, yMax=464.3,
    zMin=Z_MIN, zMax = Z_MAX)

INNER_BOUNDARY = SquareBoundary(
    xMin=-150, xMax=150,
    yMin=-150, yMax=150,
    zMin=None,    zMax = None)

BACK_BOUNDARY = LineBoundary((-150,0), (-1000,0))