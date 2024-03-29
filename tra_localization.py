from scipy.optimize import minimize
import numpy as np
from BeaconManager import BeaconManager
import math


emitter_location_dic = {"DD340207E30A": [7.85,-27.6,8.5], 
                        "DD340208F9FC": [56.6,-45.68,8.5], 
                        "DD340208FD1E": [75.44, -64.52, 8.5], 
                        "DD340208FC89": [75.44, 22.65, 3.17], 
                        "DD340208FD59": [57.19, -22.35, 8.5], 
                        "DD340208FBB1": [57.19, 37.98, 9.25], 
                        "DD340208FC48": [75.44, 22.65, 3.17]}

#signal_a, b, c should be int, name_a, b, c should be string. Emitter_location_dic is a dictionary which key: name of emitter(string)  value: location(list)
def tra_localization():
    
    beaconMana = BeaconManager()
    cloest3_beacon_list= sorted(beaconMana.closest.items(), key=lambda x: x[2])[:3]
    
    # point a, b, c is the location of the emitter
    point_a = emitter_location_dic[cloest3_beacon_list[0][1]]
    point_b = emitter_location_dic[cloest3_beacon_list[1][1]]
    point_c = emitter_location_dic[cloest3_beacon_list[2][1]]
    # Example known points (x, y, z)
    points = np.array([point_a, point_b, point_c])

    # distance is the distance from each emitter
    # dis_a = 9.2143 * math.log(cloest3_beacon_list[0][2]) + 47.283
    # dis_b = 9.2143 * math.log(cloest3_beacon_list[1][2]) + 47.283
    # dis_c = 9.2143 * math.log(cloest3_beacon_list[2][2]) + 47.283
    
    dis_a = 51.044 * math.log(cloest3_beacon_list[0][2]) - 200.8
    dis_b = 51.044 * math.log(cloest3_beacon_list[1][2]) - 200.8
    dis_c = 51.044 * math.log(cloest3_beacon_list[2][2]) - 200.8
  

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

    print("Estimated location:", estimated_location)

    beaconMana.clear_closest()
