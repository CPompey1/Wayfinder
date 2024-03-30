import threading
from time import sleep


EMITTER_LOC_DICT = {"DD:34:02:07:E3:0A": [7.85,-27.6,8.5],
                        "DD:34:02:08:F9:FC": [56.6,-45.68,8.5],
                        "DD:34:02:08:FD:1E": [75.44, -64.52, 8.5],
                        "DD:34:02:08:FC:89": [75.44, 22.65, 3.17],
                        "DD:34:02:08:FD:59": [57.19, -22.35, 8.5],
                        "DD:34:02:08:FB:B1": [57.19, 37.98, 9.25],
                        "DD:34:02:08:FC:48": [75.44, 22.65, 3.17]}

SIMULATION = True
ELEVATOR_PIXEL_X = 130
ELEVATOR_PIXEL_Y = 403
PIXELS_PER_GRID = 17

# the pixel location is from left down as pixel (0,0)

PIXELS_PER_GRID_FLOOR_B = 13
ELEVATOR_PIXEL_Y_FLOOR_B = 312
ELEVATOR_PIXEL_X_FLOOR_B = 208

PIXELS_PER_GRID_FLOOR_1 = 24
ELEVATOR_PIXEL_Y_FLOOR_1 = 288
ELEVATOR_PIXEL_X_FLOOR_1 = 264

PIXELS_PER_GRID_FLOOR_3 = 26
ELEVATOR_PIXEL_Y_FLOOR_3 = 338
ELEVATOR_PIXEL_X_FLOOR_3 = 260

PIXELS_PER_GRID_FLOOR_4 = 26
ELEVATOR_PIXEL_Y_FLOOR_4 = 338
ELEVATOR_PIXEL_X_FLOOR_4 = 260

PIXELS_PER_GRID_FLOOR_5 = 26
ELEVATOR_PIXEL_Y_FLOOR_5 = 338
ELEVATOR_PIXEL_X_FLOOR_5 = 260

IMU_ADDR = 0x68
IMU_BUS = 1
class SharedData:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.estimated_location = None
        self.closing = False

sharedData = SharedData()

def sim_mpu(): 
    while True and not sharedData.closing: 
        # print("Simulating mpu")
        sleep(.1)
