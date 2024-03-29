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
