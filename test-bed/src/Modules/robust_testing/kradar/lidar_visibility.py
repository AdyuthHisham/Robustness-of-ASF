import numpy as np

# Function to calculate point count
def calculate_point_count(points, box):
    count = 0
    for point in points:
        if point[0] >= box[0] and point[0] <= box[1] and point[1] >= box[2] and point[1] <= box[3]:
            count += 1
    return count

# Function to calculate visibility
def calculate_visibility(points, box):
    visible = []
    for point in points:
        in_fov = point[0] >= box[0] and point[0] <= box[1] and point[1] >= box[2] and point[1] <= box[3]
        in_range = np.linalg.norm(point) <= 100
        count = calculate_point_count(points, box)
        visible.append(in_fov and in_range and count > 0)
    return visible
