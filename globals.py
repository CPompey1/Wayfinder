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

sharedData = SharedData()

def sim_mpu(): 
    while True and not sharedData.closing: 
        # print("Simulating mpu")
        sleep(.1)
