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

ELEVATOR_PIXEL_X_FLR4 = 130
ELEVATOR_PIXEL_Y_FLR4 = 403
PIXELS_PER_GRID_FLR4 = 17


IMU_ADDR = 0x68
IMU_BUS = 1
FLOOR_4 = 4


FLOOR_4 = 4
class SharedData:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.estimated_location = None
        self.closing = False
        self.imu_orientation = None

sharedData = SharedData()

def sim_mpu(): 
    while True and not sharedData.closing: 
        # print("Simulating mpu")
        sleep(.1)
