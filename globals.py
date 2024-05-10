import threading
from time import sleep


EMITTER_LOC_DICT = {    
                            "DD:34:02:08:FC:EC": [12.5,-2.6,0],             #12        #1 Basement
                            "DD:34:02:08:F9:FC": [51.4,-22.7,0],            #2
                            "DD:34:02:08:FB:43": [61.4, -22.7, 0],          #14
                            "DD:34:02:08:FD:1E": [61.4, 17.1, 0],           #3
                            "DD:34:02:08:FD:38": [61.4, 58.2, 0],           #13 unknow height
                            "DD:34:02:08:FC:48": [-8.3, 37.9, 0],           #7
                            "DD:34:02:08:FA:38": [-26.3, 75.5, 100],        #16        #1st floor
                            "DD:34:02:08:FD:0E": [48.6, 117.2, 100],        #11
                            "DD:34:02:07:E3:0A": [87.8, 157.3, 100],        #1
                            "DD:34:02:08:FA:17": [36.5, 99.5, 100],        #10
                            "DD:34:02:08:FA:EC": [10.7, 157.3, 100],        #9
                            "DD:34:02:08:EB:B1": [-42.1, 157.3, 100],       #6
                            "DD:34:02:08:FB:43": [13.3, -23.2, 200],        #   test14 #Second Floor
                            "DD:34:02:07:E3:46": [52.8, -42.6, 200],        #   test15
                            "DD:34:02:08:FA:38": [92.5, -63.3, 200],        #   test16
                            "54:0F:57:D0:7C:C9": [72.0, -2.7, 200],         #   test17
                            "00:3C:84:20:E7:88": [92.5, 37.5, 200],         #   test18
                            "00:3C:84:22:47:3F": [72.0, 51.2, 200],         #   test19
                            "84:BA:20:6E:3B:7A": [-26.3, 31.4, 200],        #   test20
                            "84:BA:20:71:F3:AD": [-13.3, 10.0, 200],        #   test21
                            "84:BA:20:71:E7:15": [85.0, -6.3, 200],         #   test73
                            "mac_beacon22_3": [13.3, -23.2, 300],           #3rd floor
                            "mac_beacon23_3": [-26.3, -55.5, 300],          # (updated)
                            "mac_beacon24_3": [39.2, -55.5, 300],           # (updated)
                            "mac_beacon25_3": [65.6, -19.1, 300],           #25
                            "mac_beacon26_3": [83.5, -55.5, 300],           # (updated)
                            "mac_beacon27_3": [83.5, 18.0, 300],            #
                            "84:BA:20:71:E6:B4": [83.5, 71.3, 300],         #
                            "BC:02:6E:9C:88:0A": [83.5, 127.4, 300],        #
                            "BC:02:6E:9C:88:3C": [29.8, 146.9, 300],        #30
                            "BC:02:6E:9C:87:E8": [-6.0, 108.8, 300],         # (updated)
                            "BC:02:6E:9C:88:42": [-22.1, 146.9, 300 ],      # (updated)
                            "BC:02:6E:9C:8A:3D": [-30.1, 72.9, 300],  
                            "A4:9E:69:96:0F:7E": [-30.1, 36.3, 300],  
                            "BC:02:6E:9C:72:94": [-30.1, -37.7, 300],     #35
                            "BC:02:6E:9C:87:F6": [54.5, 54.5, 300],       #36(updated)
                            "00:3C:84:2A:C0:79": [-6.5, 54.5, 300]  ,     # (updated)
                            "00:3C:84:2A:B8:97": [29.8, 53.9, 300],  
                            "54:0F:57:D0:80:73": [-40.5, -55.2, 400]  ,        #4th floor (updated)
                            "84:BA:20:71:RC:CD": [39.5, -55.5, 400  ],      #40 (updated)
                            "00:3C:84:2A:C4:A5": [67.5, -18.5, 400],        # (updated)
                            "84:BA:20:6E:23:32": [85.5, -55.5, 400],        # (updated)
                            "84:BA:20:71:F5:56": [68.5, 15.3, 400],         # (updated)
                            "00:3C:84:22:39:D1": [68.5, 55.5, 400],         # (updated)
                            "84:BA:20:71:E6:92": [83.5, 66.3, 400],           #45 (updated)
                            "00:3C:84:2A:D2:A7": [52.6, 108.4, 400],        # (updated)
                            "84:BA:20:6E:22:D2": [67.5, 108.9, 400],        # (updated)
                            "BC:02:6E:9C:72:89": [31.5, 108.8, 400],        # (updated)
                            "00:3C:84:2A:BD:CD": [25.5, 146.9, 400],        # (updated)
                            "00:3C:84:20:ED:38": [-6.1, 108.8, 400],        #50 (updated)
                            "00:3C:84:20:E3:DC": [-25.5, 24.0, 400],        # (updated)
                            "00:3C:84:20:EB:AD": [-22.5, 71.2, 400],        # (updated)
                            "54:0F:57:D0:73:50": [-18.0, 53.9, 400],        # (updated)
                            "84:BA:20:6E:3A:31": [-38.5, 31.8, 400],        # (updated)
                            "00:3C:84:22:47:7E": [-22.5, 15.9, 400],           #55 (updated)
                            "84:BA:20:6E:3A:C4": [-39.5, -31.2, 500],       # (updated)
                            "84:BA:20:71:E7:47": [13.2, -16.3, 500],        # 5th floor  (updated)
                            "00:3C:84:20:EA:17": [-3.2, -35.3, 500],        # (updated)
                            "00:3C:84:20:ED:2C": [31.5, -54.1, 500],        # missing
                            "84:BA:20:v6:E3:9F": [76.5, -54.3, 500],        #60 
                            "00:3C:84:20:EE:38": [31.5, -19.0, 500],        # (updated)
                            "00:3C:84:20:E4:66": [66.0, -18.5, 500],        # (updated)
                            "00:3C:84:28:7E:19": [83.5, 17.5, 500]  ,       # (updated)
                            "84:BA:20:6E:38:4B": [67.5, 54.3, 500]  ,       # (updated)
                            "84:BA:20:90:20:8A": [67.5, 108.8, 500],        #65 (updated)
                            "00:3C:84:2A:BD:45": [51.4, 107.5, 500],        # (updated)
                            "00:3C:84:22:36:09": [135., 127.9, 500],        # (updated)
                            "00:3C:84:22:39:23": [-25.5, 127.9, 500],       # (updated)
                            "84:BA:20:90:18:81": [-41.5, -72.0, 500],       # (updated)
                            "00:3C:84:20:EC:B2": [-21.5, 35.9, 500],        #70 (updated)
                            "00:3C:84:28:7A:84": [-39.8, 18.8, 500],        # (updated)
                            "00:3C:84:22:36:82": [-37.5, -53.9, 500],       # (updated)
                            "beacon80": [-39.5,90.5,400]        
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

    def set_estimated_location(self,location):
        with self.lock:
            self.estimated_location = location
    def start_navigation(self):
        with self.lock:
            self.navigation_started = True
        return
sharedData = SharedData()


