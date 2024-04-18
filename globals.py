import threading
from time import sleep


EMITTER_LOC_DICT = {    "00:3C:84:20:E7:88": [7.85,-27.6,8.5],          #18
                        "00:3C:84:22:47:3F": [56.6,-45.68,8.5],         #19
                        "84:BA:20:6E:3B:7A": [75.44, -64.52, 8.5],      #20
                        "84:BA:20:71:F3:AD": [75.44, 22.65, 3.17],      #21
                        "84:BA:20:6E:3B:67": [57.19, -22.35, 8.5],      #22
                        "00:3C:84:28:91:A0": [57.19, 37.98, 9.25],      #23
                        "84:BA:20:6E:3C:77": [75.44, 22.65, 3.17],      #24
                        "00:0A:45:19:CD:91": [0,0,0],
                        "46:85:24:E7:A5:5C": [0,1,0],
                        "4D:CB:64:BF:76:84": [0,2,0],
                        "00:3C:84:22:38:1D": [0,3,0], #25
                        "84:BA:20:71:E6:76": [0,4,0], #26
                        "00:3C:84:22:3A:95": [0,5,0],   #27
                        "84:BA:20:71:E6:B4": [0,6,0]
                        }
                        # "00:3C:84:22:3A:95": [0,0,0],
                        # "45:06:9D:05:98:E6": [0,1,0],
                        # "30:09:20:1D:B9:6E": [0,2,0],
                        # "00:3C:84:20:E7:88": [0,3,0] }      

SIMULATION = True

# the pixel location is from left down as pixel (0,0)

PIXELS_PER_GRID_FLOOR_B_X = 14
PIXELS_PER_GRID_FLOOR_B_Y = 17
ELEVATOR_PIXEL_X_FLOOR_B = 180
ELEVATOR_PIXEL_Y_FLOOR_B = 314

PIXELS_PER_GRID_FLOOR_1_X = 15
PIXELS_PER_GRID_FLOOR_1_Y = 15
ELEVATOR_PIXEL_X_FLOOR_1 = 288
ELEVATOR_PIXEL_Y_FLOOR_1 = 598

PIXELS_PER_GRID_FLOOR_2_X = 18
PIXELS_PER_GRID_FLOOR_2_Y = 19
ELEVATOR_PIXEL_X_FLOOR_2 = 158
ELEVATOR_PIXEL_Y_FLOOR_2 = 500

PIXELS_PER_GRID_FLOOR_3_X = 17
PIXELS_PER_GRID_FLOOR_3_Y = 15
ELEVATOR_PIXEL_X_FLOOR_3 = 160
ELEVATOR_PIXEL_Y_FLOOR_3 = 458

PIXELS_PER_GRID_FLOOR_4_X = 19
PIXELS_PER_GRID_FLOOR_4_Y = 19
ELEVATOR_PIXEL_X_FLOOR_4 = 185
ELEVATOR_PIXEL_Y_FLOOR_4 = 436

PIXELS_PER_GRID_FLOOR_5_X = 20
PIXELS_PER_GRID_FLOOR_5_Y = 19
ELEVATOR_PIXEL_X_FLOOR_5 = 180
ELEVATOR_PIXEL_Y_FLOOR_5 = 451

IMU_ADDR = 0x68
IMU_BUS = 1
class SharedData:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.estimated_location = None
        self.closing = False
        self.beacon_manager_lock = threading.Lock()
        self.navigation_started = True
        self.orientation = None
    def get_orientation(self):
        with self.lock:
            out = self.estimated_location
        return out
    def get_estimated_location(self):
        with self.lock:
            out = self.orientation
        return out
    def start_navigation(self):
        with self.lock:
            self.navigation_started = True
        return
sharedData = SharedData()


