import threading
from time import sleep

EMITTER_LOC_DICT = {    
                            "DD:34:02:08:FD:3B": [52.5, 17.0, 8.33],           #test4  (updated)     Basement
                            "84:BA:20:6E:23:58": [13.5, 0.0, 7.42],            #test82 (updated)
                            "84:BA:20:6E:23:8D": [52.5, -18.7, 7.92],          #test83 (updated)
                            "84:BA:20:71:E7:FE": [87.0, -16.1, 7.92],          #test84 (updated)
                            "84:BA:20:6E:3A:15": [13.5, 51.2, 8.5],            #test85 (updated)
                            "54:0F:57:D0:79:B1": [-19.3, 16.9, 7.83],          #test74 (updated)
                            "DD:34:02:08:FC:48": [-16.5, 55.5, 107.42],        #test7  (updated)     1st floor
                            "DD:34:02:08:FA:9A": [32.5, 79.5, 107.75],         #test8  (updated)
                            "DD:34:02:08:FA:EC": [69.5, 106.5, 109],           #test9  (updated)
                            "DD:34:02:08:FA:17": [36.5, 99.5, 108.58],         #test10 (updated)
                            "DD:34:02:08:FD:0E": [15.2, 106.5, 109.83],        #test11 (updated)
                            "DD:34:02:08:FC:EC": [-38.1, 106.5, 108],          #test12 (updated)
                            "DD:34:02:08:FD:38": [-16.5, 78.5, 108],           #test13 (updated)
                            "00:3C:84:20:E6:7C": [11.0, 81.0, 108],            #test77 (updated)
                            "DD:34:02:08:FB:43": [13.3, -23.2, 211],           #test14               2nd Floor
                            "DD:34:02:07:E3:46": [52.8, -42.6, 206.08],        #test15
                            "DD:34:02:08:FA:38": [92.5, -63.3, 207.17],        #test16
                            "54:0F:57:D0:7C:C9": [72.0, -2.7, 207.67],         #test17
                            "00:3C:84:20:E7:88": [92.5, 37.5, 207.25],         #test18
                            "00:3C:84:22:47:3F": [72.0, 51.2, 206.41],         #test19
                            "84:BA:20:6E:3B:7A": [-26.3, 31.4, 207.92],        #test20
                            "84:BA:20:71:F3:AD": [-13.3, 10.0, 208.75],        #test21
                            "84:BA:20:71:E7:15": [85.0, -6.3, 208.5],          #test73
                            "84:BA:20:6E:3B:67": [13.3, -23.2, 307.58],        #test22               3rd floor
                            "00:3C:84:28:91:A0": [-26.3, -55.5, 307.25],       #test23 (updated)
                            "00:3C:84:20:E3:B6": [39.2, -55.5, 307.75],        #test75 (updated)
                            "84:BA:20:71:E6:76": [65.6, -19.1, 308],           #test26
                            "00:3C:84:28:85:DB": [83.5, -55.5, 307.5],         #test76 (updated)
                            "00:3C:84:22:3A:95": [83.5, 18.0, 307.83],         #test27
                            "84:BA:20:71:E6:B4": [83.5, 71.3, 307.75],         #test28
                            "BC:02:6E:9C:88:0A": [83.5, 127.4, 307.75],        #test29
                            "BC:02:6E:9C:88:3C": [29.8, 146.9, 307.75],        #test30
                            "BC:02:6E:9C:87:E8": [-6.0, 108.8, 307.34],        #test31 (updated)
                            "BC:02:6E:9C:88:42": [-22.1, 146.9, 307.34],       #test32 (updated)
                            "BC:02:6E:9C:8A:3D": [-30.1, 72.9, 307.75],        #test33
                            "A4:9E:69:96:0F:7E": [-30.1, 36.3, 307.25],        #test34
                            "BC:02:6E:9C:72:94": [-30.1, -37.7, 308.92],       #test35
                            "BC:02:6E:9C:87:F6": [54.5, 54.5, 308.42],         #test36 (updated)
                            "00:3C:84:2A:C0:79": [-6.5, 54.5, 309],            #test37 (updated)
                            "00:3C:84:2A:B8:97": [29.8, 53.9, 308],            #test38
                            "00:3C:84:22:31:FB": [0, 0, 0],                    #test78
                            "54:0F:57:D0:80:73": [-40.5, -55.2, 407.92],       #test39 (updated)      4th floor 
                            "84:BA:20:71:RC:CD": [39.5, -55.5, 407.25],        #test40 (updated)
                            "00:3C:84:2A:C4:A5": [67.5, -18.5, 408.83],        #test41 (updated)
                            "84:BA:20:6E:23:32": [85.5, -55.5, 408],           #test42 (updated)
                            "84:BA:20:71:F5:56": [68.5, 15.3, 407],            #test43 (updated)
                            "00:3C:84:22:39:D1": [68.5, 55.5, 407.75],         #test44 (updated)
                            "84:BA:20:71:E6:92": [83.5, 66.3, 407.25],         #test45 (updated)
                            "00:3C:84:2A:D2:A7": [52.6, 108.4, 408.92],        #test46 (updated)
                            "84:BA:20:6E:22:D2": [67.5, 108.9, 408],           #test47 (updated)
                            "BC:02:6E:9C:72:89": [31.5, 108.8, 407.34],        #test48 (updated)
                            "00:3C:84:2A:BD:CD": [25.5, 146.9, 407.34],        #test49 (updated)
                            "00:3C:84:20:ED:38": [-6.1, 108.8, 407.75],        #test50 (updated)
                            "00:3C:84:20:E3:DC": [-25.5, 24.0, 407.25],        #test51 (updated)
                            "00:3C:84:20:EB:AD": [-22.5, 71.2, 405.92],        #test52 (updated)
                            "54:0F:57:D0:73:50": [-18.0, 53.9, 408.5],         #test53 (updated)
                            "84:BA:20:6E:3A:31": [-38.5, 31.8, 408.5],         #test54 (updated)
                            "00:3C:84:22:47:7E": [-22.5, 15.9, 408.5],         #test55 (updated)
                            "84:BA:20:6E:3A:C4": [-39.5, -31.2, 408.92],       #test56 (updated)
                            "54:0F:57:D0:7B:0D": [0, 0, 0],                    #test79
                            "84:BA:20:71:EA:0D": [-39.5, 90, 408.5],           #test80 (updated)
                            "84:BA:20:71:E7:47": [13.2, -16.3, 508.5],         #test57 (updated)      5th floor  
                            "00:3C:84:20:EA:17": [-3.2, -35.3, 507.5],         #test58 (updated)
                            "00:3C:84:20:ED:2C": [31.5, -54.1, 508],           #test59
                            "84:BA:20:v6:E3:9F": [76.5, -54.3, 507.5],         #test60 
                            "00:3C:84:20:EE:38": [31.5, -19.0, 507.75],        #test61 (updated)
                            "00:3C:84:20:E4:66": [66.0, -18.5, 507.25],        #test62 (updated)
                            "00:3C:84:28:7E:19": [83.5, 17.5, 5008.33],        #test63 (updated)
                            "84:BA:20:6E:38:4B": [67.5, 54.3, 508.5],          #test64 (updated)
                            "84:BA:20:90:20:8A": [67.5, 108.8, 508.5],         #test65 (updated)
                            "00:3C:84:2A:BD:45": [51.4, 107.5, 508.5],         #test66 (updated)
                            "00:3C:84:22:36:09": [135., 127.9, 508.5],         #test67 (updated)
                            "00:3C:84:22:39:23": [-25.5, 127.9, 508.5],        #test68 (updated)
                            "84:BA:20:90:18:81": [-41.5, -72.0, 508.5],        #test69 (updated)
                            "00:3C:84:20:EC:B2": [-21.5, 35.9, 508.25],        #test70 (updated)
                            "00:3C:84:28:7A:84": [-39.8, 18.8, 508.5],         #test71 (updated)
                            "00:3C:84:22:36:82": [-37.5, -53.9, 508.5],        #test72 (updated)
                            "84:BA:20:6E:39:98": [0, 0, 0],                    #test81      
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
        self.estimated_location = (50,-30,200)
        self.closing = False
        self.beacon_manager_lock = threading.Lock()
        self.navigation_started = True
        self.orientation = 0
    def get_orientation(self):
        with self.lock:
            out = self.orientation
        return out
    def get_estimated_location(self):
        with self.lock:
            out = self.estimated_location
        return out
    def set_orientation(self, ori):
        with self.lock:
            self.orientation = ori
    def set_estimated_location(self,location):
        with self.lock:
            self.estimated_location = location
    def start_navigation(self):
        with self.lock:
            self.navigation_started = True
        return
sharedData = SharedData()


