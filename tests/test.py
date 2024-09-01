import numpy as np

x = np.array([1, 5, 10, 15,5])
split_points = [0, 4, 8, 12, 16]

print(np.digitize(x, split_points))