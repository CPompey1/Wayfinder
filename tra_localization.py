from scipy.optimize import minimize
import numpy as np

# Example known points (x, y, z)
points = np.array([[0, 0, 0], [10, 0, 0], [0, 10, 0]])

# Example distances from the unknown point to each of the known points
distances = np.array([5, 7.07, 7.07])

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

