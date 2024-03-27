from scipy.optimize import minimize
import numpy as np
from BeaconManager import BeaconManager
import math
import time
import asyncio

#Emitter locaiton dictionary
#Key        :   Value
#Mac Address:   emitter location(x,y,z(height))




beaconManager = None
file1 = None
#signal_a, b, c should be int, name_a, b, c should be string. Emitter_location_dic is a dictionary which key: name of emitter(string)  value: location(list)

async def main():
    global beaconManager, file1
    beaconManager = BeaconManager()
    await beaconManager.initialize_scanning()
    while (True):
        try:
            if not None in beaconManager.get_closest():
                print("Entering localization")
                await tra_localization()
                beaconManager.clear_closest()
                print("********************************FULL*************************************************")
            else:
                print("not full\n")
        except KeyboardInterrupt:
            print("CLOSING")
            await beaconManager.close()
            file1.close()
            return

    
async def tra_localization(cloest3_beacon_list, emitter_location_dic) -> list[float]:
    
    #cloest3_beacon_list = beaconManager.closest
  
    # point a, b, c is the location of the emitter
    point_a = emitter_location_dic[cloest3_beacon_list[0][0]]
    point_b = emitter_location_dic[cloest3_beacon_list[1][0]]
    point_c = emitter_location_dic[cloest3_beacon_list[2][0]]

    # Example known points (x, y, z)
    points = np.array([point_a, point_b, point_c])

    # distance is the distance from each emitter
    dis_a = 51.044 * math.log(int(cloest3_beacon_list[0][2])) - 200.8
    dis_b = 51.044 * math.log(int(cloest3_beacon_list[1][2])) - 200.8
    dis_c = 51.044 * math.log(int(cloest3_beacon_list[2][2])) - 200.8
  

    # Example distances from the unknown point to each of the known points
    distances = np.array([dis_a, dis_b, dis_c])

    # Objective function: sum of squared differences between actual and calculated distances
    def itera_guessing(unknown, points, distances):
        return sum((np.linalg.norm(unknown - points[i]) - distances[i])**2 for i in range(len(points)))

    # Initial guess for the unknown point
    initial_guess = np.mean(points, axis=0)

    # Minimize the objective function
    result = minimize(itera_guessing, initial_guess, args=(points, distances))

    # Extract the estimated location of the unknown point
    estimated_location = result.x

    return estimated_location
