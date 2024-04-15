<<<<<<< HEAD
from scipy.optimize import minimize
import numpy as np
import math

# Example known points (x, y, z)
points = np.array([[10, 0, 0], [0, 0, 0], [0, 10, 0]])

# Example distances from the unknown point to each of the known points
# dis_a = 9.2143 * math.log(55) + 47.283
# dis_b = 9.2143 * math.log(66) + 47.283
# dis_c = 9.2143 * math.log(70) + 47.283

dis_a = 51.044 * math.log(55) - 200.8
dis_b = 51.044 * math.log(66) - 200.8
dis_c = 51.044 * math.log(70) - 200.8

distances = np.array([dis_a, dis_b, dis_c])

# Objective function: sum of squared differences between actual and calculated distances
def objective_function(unknown, points, distances):
    return sum((np.linalg.norm(unknown - points[i]) - distances[i])**2 for i in range(len(points)))

# Initial guess for the unknown point
initial_guess = np.mean(points, axis=0)

# Minimize the objective function
result = minimize(objective_function, initial_guess, args=(points, distances))

# Extract the estimated location of the unknown point
estimated_location = result.x

print("Estimated location:", estimated_location)
=======
from scipy.optimize import minimize
import numpy as np
import math

# Example known points (x, y, z)
points = np.array([[10, 0, 0], [0, 0, 0], [0, 10, 0]])

# Example distances from the unknown point to each of the known points
# dis_a = 9.2143 * math.log(55) + 47.283
# dis_b = 9.2143 * math.log(66) + 47.283
# dis_c = 9.2143 * math.log(70) + 47.283

dis_a = 51.044 * math.log(55) - 200.8
dis_b = 51.044 * math.log(66) - 200.8
dis_c = 51.044 * math.log(70) - 200.8

distances = np.array([dis_a, dis_b, dis_c])

# Objective function: sum of squared differences between actual and calculated distances
def objective_function(unknown, points, distances):
    return sum((np.linalg.norm(unknown - points[i]) - distances[i])**2 for i in range(len(points)))

# Initial guess for the unknown point
initial_guess = np.mean(points, axis=0)

# Minimize the objective function
result = minimize(objective_function, initial_guess, args=(points, distances))

# Extract the estimated location of the unknown point
estimated_location = result.x

print("Estimated location:", estimated_location)
>>>>>>> UI
