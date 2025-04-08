import cv2
import math
import numpy as np
from . import detect
from . import const

"""
Calculate
This file contains functions for handling math or calculations.
"""

# Helper function to calculate average
def average(lst):
    return sum(lst) / len(lst)

# Check if points are inside a contour
def points_inside_contour(points, contour):
    """
    Return false if all of the points are outside of the contour
    """
    for x, y in points:
        if abs(cv2.pointPolygonTest(contour, (int(x), int(y)), False) - 1.0) < 1e-6:
            return True
    return False

# Remove walls that are not inside the contour
def remove_walls_not_in_contour(walls, contour):
    """
    Returns a list of boxes where walls outside of contour are removed.
    """
    res = []
    for wall in walls:
        for point in wall:
            if points_inside_contour(point, contour):
                res.append(wall)
                break
    return res

# Calculate the average width of walls in the floorplan
def wall_width_average(img):
    """
    Calculate the average width of walls in a floorplan.
    This is used to scale the image size for better accuracy.
    Returns the average as a float value (calibration).
    """
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    height, width, _ = img.shape
    blank_image = np.zeros((height, width, 3), np.uint8)  # Output image same size as original

    # Apply wall filter
    wall_img = detect.wall_filter(gray)
    boxes, img = detect.precise_boxes(wall_img, blank_image)

    # Filter to count only walls (boxes with 4 corners)
    filtered_boxes = []
    for box in boxes:
        if len(box) == 4:  # Detect rectangles (oblong)
            _, _, w, h = cv2.boundingRect(box)
            shortest = min(w, h)  # Get shortest side
            filtered_boxes.append(shortest)

    if len(filtered_boxes) == 0:
        return None  # Return None if no walls are detected

    return average(filtered_boxes)

# Compare matching features from ORB by rotating over 360 degrees to find best fit for door rotation
def best_matches_with_modulus_angle(match_list):
    """
    This function compares matching matches from ORB feature matching,
    by rotating in steps over 360 degrees to find the best fit for door rotation.
    """
    index1, index2 = 0, 0
    best = math.inf

    for i, _ in enumerate(match_list):
        for j, _ in enumerate(match_list):

            pos1_model = match_list[i][0]
            pos2_model = match_list[j][0]
            pos1_cap = match_list[i][1]
            pos2_cap = match_list[j][1]

            pt1 = (pos1_model[0] - pos2_model[0], pos1_model[1] - pos2_model[1])
            pt2 = (pos1_cap[0] - pos2_cap[0], pos1_cap[1] - pos2_cap[1])

            if pt1 == pt2 or pt1 == (0, 0) or pt2 == (0, 0):
                continue

            ang = math.degrees(angle_between_vectors_2d(pt1, pt2))
            diff = ang % const.DOOR_ANGLE_HIT_STEP

            if diff < best:
                best = diff
                index1 = i
                index2 = j

    return index1, index2

# Check if a point is inside or near a box (used for doors)
def points_are_inside_or_close_to_box(door, box):
    """
    Calculate if a point is within the vicinity of a box.
    @param door is a list of points
    @param box is a numpy box
    """
    for point in door:
        if rect_contains_or_almost_contains_point(point, box):
            return True
    return False

# Get angle between two 2D vectors in radians
def angle_between_vectors_2d(vector1, vector2):
    """
    Get angle between two 2D vectors
    returns radians
    """
    x1, y1 = vector1
    x2, y2 = vector2
    inner_product = x1 * x2 + y1 * y2
    len1 = math.hypot(x1, y1)
    len2 = math.hypot(x2, y2)
    return math.acos(inner_product / (len1 * len2))

# Check if a point is inside or near a bounding box
def rect_contains_or_almost_contains_point(pt, box):
    """
    Calculate if a point is within the vicinity of a box.
    """
    x, y, w, h = cv2.boundingRect(box)
    is_inside = x < pt[0] < x + w and y < pt[1] < y + h

    # Check if point is almost inside (within the smallest box dimension)
    min_dist = min(w, h)

    almost_inside = any(abs(point[0][0] - pt[0]) + abs(point[0][1] - pt[1]) <= min_dist for point in box)

    return is_inside or almost_inside

# Get the center of a bounding box
def box_center(box):
    """
    Get the center position of a bounding box
    """
    x, y, w, h = cv2.boundingRect(box)
    return (x + w / 2, y + h / 2)

# Calculate Euclidean distance between two points in 2D space
def euclidean_distance_2d(p1, p2):
    """
    Calculate the Euclidean distance between two points
    """
    return math.sqrt(abs(math.pow(p1[0] - p2[0], 2) - math.pow(p1[1] - p2[1], 2)))

# Calculate the magnitude (length) of a 2D point
def magnitude_2d(point):
    """
    Calculate magnitude of a 2D point
    """
    return math.sqrt(point[0] ** 2 + point[1] ** 2)

# Normalize a 2D vector
def normalize_2d(normal):
    """
    Normalize a 2D vector
    """
    mag = magnitude_2d(normal)
    return [val / mag for val in normal]
