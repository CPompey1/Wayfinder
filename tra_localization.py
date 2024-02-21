from scipy.optimize import minimize
import numpy as np
import math

#signal_a, b, c should be int, name_a, b, c should be string. Emitter_location_dic is a dictionary which key: name of emitter(string)  value: location(list)
def tra_localization(signal_a, signal_b, signal_c, name_a, name_b, name_c):

    point_a = emitter_location_dic[name_a]
    point_b = emitter_location_dic[name_b]
    point_c = emitter_location_dic[name_c]
    # Example known points (x, y, z)
    points = np.array([point_a, point_b, point_c])

    dis_a = 9.2143 * math.log(signal_a) + 47.283
    dis_b = 9.2143 * math.log(signal_b) + 47.283
    dis_c = 9.2143 * math.log(signal_c) + 47.283

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

