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


#set all the hight to 8.5, might need modified
#1-6 B  7-13 1  14-21 2  22-38 3  39-55 4  56-72 5
emitter_location_dic_full = {"mac_beacon1_b": [12.5,-2.6,7.75],         #1 Basement
                            "mac_beacon2_b": [51.4,-22.7,7.42], 
                            "mac_beacon3_b": [61.4, -22.7, 7.58], 
                            "mac_beacon4_b": [61.4, 17.1, 8.25], 
                            "mac_beacon5_b": [61.4, 58.2, 8.5],         #5 unknow height
                            "mac_beacon6_b": [-8.3, 37.9, 7.83],
                            "mac_beacon7_1": [-26.3, 75.5, 7.42],       #1st floor
                            "mac_beacon8_1": [48.6, 117.2, 7.75],
                            "mac_beacon9_1": [87.8, 157.3, 8.33],
                            "mac_beacon10_1": [48.6, 157.3, 8.58],       #10
                            "mac_beacon11_1": [10.7, 157.3, 9.83],
                            "mac_beacon12_1": [-42.1, 157.3, 8.0],
                            "mac_beacon13_1": [-26.3, 117.2, 11.0],
                            "mac_beacon14_2": [13.3, -23.2, 6.08],       #2nd floor
                            "mac_beacon15_2": [52.8, -42.6, 7.17],       #15
                            "mac_beacon16_2": [92.5, -63.3, 7.67],
                            "54:0F:57:D0:7C:C9": [72.0, -2.7, 7.25],
                            "mac_beacon18_2": [92.5, 37.5, 6.41],
                            "mac_beacon19_2": [72.0, 51.2, 7.92],
                            "mac_beacon20_2": [-26.3, 31.4, 8.75],       #20
                            "84:BA:20:71:F3:AD": [-6.4, 18.0, 8.5],      #didn't find the router
                            "mac_beacon22_3": [13.3, -23.2, 8.92],       #3rd floor
                            "mac_beacon23_3": [-26.3, -63.3, 7.25],
                            "mac_beacon24_3": [39.2, -63.3, 7.75],
                            "mac_beacon25_3": [65.6, -19.1, 8.0],       #25
                            "mac_beacon26_3": [83.5, -62.3, 7.5],
                            "mac_beacon27_3": [83.5, 18.0, 7.75],
                            "84:BA:20:71:E6:B4": [83.5, 71.3, 7.25],
                            "BC:02:6E:9C:88:0A": [83.5, 127.4, 7.75],
                            "BC:02:6E:9C:88:3C": [29.8, 146.9, 7.25],    #30
                            "BC:02:6E:9C:87:E8": [0.0, 108.8, 7.34],
                            "BC:02:6E:9C:88:42": [-19.1, 146.9, 7.34],
                            "BC:02:6E:9C:8A:3D": [-30.1, 72.9, 7.75],
                            "A4:9E:69:96:0F:7E": [-30.1, 36.3, 7.25],
                            "BC:02:6E:9C:72:94": [-30.1, -37.7, 5.92],   #35
                            "BC:02:6E:9C:87:F6": [48.2, 53.9, 8.5],
                            "00:3C:84:2A:C0:79": [29.8, 108.8, 8.5],
                            "00:3C:84:2A:B8:97": [29.8, 53.9, 8.5],
                            "54:0F:57:D0:80:73": [13.3, -23.2, 8.92],    #4th floor
                            "84:BA:20:71:RC:CD": [-26.3, -63.3, 7.25],   #40
                            "00:3C:84:2A:C4:A5": [39.2, -63.3, 7.75],
                            "84:BA:20:6E:23:32": [65.6, -19.1, 8.0],
                            "84:BA:20:71:F5:56": [83.5, -62.3, 7.5],
                            "00:3C:84:22:39:D1": [83.5, 18.0, 7.75],
                            "84:BA:20:71:E6:92": [83.5, 71.3, 7.25],     #45
                            "00:3C:84:2A:D2:A7": [83.5, 127.4, 7.75],
                            "84:BA:20:6E:22:D2": [29.8, 146.9, 7.25],
                            "BC:02:6E:9C:72:89": [0.0, 108.8, 7.34],
                            "00:3C:84:2A:BD:CD": [-19.1, 146.9, 7.34],
                            "00:3C:84:20:ED:38": [-30.1, 72.9, 7.75],    #50
                            "00:3C:84:20:E3:DC": [-30.1, 36.3, 7.25],
                            "00:3C:84:20:EB:AD": [-30.1, -37.7, 5.92],
                            "54:0F:57:D0:73:50": [48.2, 53.9, 8.5],
                            "84:BA:20:6E:3A:31": [29.8, 108.8, 8.5],
                            "00:3C:84:22:47:7E": [29.8, 53.9, 8.5],     #55
                            "84:BA:20:6E:3A:C4": [13.3, -23.2, 8.92],   #5th floor
                            "84:BA:20:71:E7:47": [-26.3, -63.3, 7.25],
                            "00:3C:84:20:EA:17": [39.2, -63.3, 7.75],
                            "00:3C:84:20:ED:2C": [65.6, -19.1, 8.0],
                            "84:BA:20:v6:E3:9F": [83.5, -62.3, 7.5],    #60
                            "00:3C:84:20:EE:38": [83.5, 18.0, 7.75],
                            "00:3C:84:20:E4:66": [83.5, 71.3, 7.25],
                            "00:3C:84:28:7E:19": [83.5, 127.4, 7.75],
                            "84:BA:20:6E:38:4B": [29.8, 146.9, 7.25],
                            "84:BA:20:90:20:8A": [0.0, 108.8, 7.34],     #65
                            "00:3C:84:2A:BD:45": [-19.1, 146.9, 7.34],
                            "00:3C:84:22:36:09": [-30.1, 72.9, 7.75],
                            "00:3C:84:22:39:23": [-30.1, 36.3, 7.25],
                            "84:BA:20:90:18:81": [-30.1, -37.7, 5.92],
                            "00:3C:84:20:EC:B2": [48.2, 53.9, 8.5],     #70
                            "00:3C:84:28:7A:84": [29.8, 108.8, 8.5],
                            "00:3C:84:22:36:82": [29.8, 53.9, 8.5],
                            }
     

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


