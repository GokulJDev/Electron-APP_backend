import cv2
import numpy as np
import sys
import os
import math

# Set the paths for the library and image files
floorplan_lib_path = os.path.dirname(os.path.realpath(__file__)) + "/../../"
example_image_path = os.path.dirname(os.path.realpath(__file__)) + "/../../Images/Examples/example.png"
door_image_paths = [
    os.path.dirname(os.path.realpath(__file__)) + "/../../Images/Models/Doors/door1.png",
    os.path.dirname(os.path.realpath(__file__)) + "/../../Images/Models/Doors/door2.png",
    os.path.dirname(os.path.realpath(__file__)) + "/../../Images/Models/Doors/door3.png"
]

# Insert floorplan library path for importing functions
sys.path.insert(0, floorplan_lib_path)
from FloorplanToBlenderLib import detect  # Importing floorplan detection functions

# Core function to detect windows and doors from an image
def detect_windows_and_doors_boxes(img, door_list):
    """
    Detect and classify windows and doors in the given floorplan image.
    Args:
        img (numpy.ndarray): Input floorplan image.
        door_list (list): List of door features to match against.
    """
    # Get image dimensions and create a blank image for results
    height, width, _ = img.shape
    blank_image = np.zeros((height, width, 3), np.uint8)

    # Convert to grayscale for better feature detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = detect.wall_filter(gray)  # Apply a wall filter from the library
    gray = ~gray  # Invert the image for detection

    # Detect rooms and doors/windows
    _, _ = detect.find_rooms(gray.copy())
    _, colored_doors = detect.find_details(gray.copy())
    gray_rooms = cv2.cvtColor(colored_doors, cv2.COLOR_BGR2GRAY)

    # Get precise bounding boxes for rooms and details
    boxes, gray_rooms = detect.precise_boxes(gray_rooms, blank_image)

    # Show the initial and intermediate detection images
    cv2.imshow("input", img)
    cv2.imshow("doors and windows", gray_rooms)
    cv2.imshow("colored", colored_doors)
    cv2.waitKey(0)

    # Classify boxes as either windows, doors, or none
    classified_boxes = classify_boxes(boxes, door_list, img)

    # Draw the final result on the image
    for box in classified_boxes:
        if box["type"] == "door":
            img = cv2.line(img, box["features"][1], box["features"][2], (0, 0, 255), 5)
        elif box["type"] == "window":
            x, y, w, h = cv2.boundingRect(box["box"])
            start = (x, y)
            end = (x + w, y + h)
            img = cv2.line(img, start, end, (0, 255, 0), 5)

    # Show the final annotated image
    cv2.imshow("Final result", img)
    cv2.waitKey(0)

# Classify bounding boxes into windows, doors, or none
def classify_boxes(boxes, door_list, img):
    """
    Classifies bounding boxes into windows, doors, or none based on their characteristics.
    Args:
        boxes (list): List of bounding boxes for detected features.
        door_list (list): List of door features to match against.
        img (numpy.ndarray): Input floorplan image.
    Returns:
        list: Classified list of bounding boxes with types (window, door, or none).
    """
    classified_boxes = []

    for box in boxes:
        obj = {"type": "none"}  # Default type is none
        is_door = False

        # Check if a door is inside the box
        for door in door_list:
            if points_are_inside_or_close_to_box(door, box):
                obj["type"] = "door"
                obj["box"] = box
                obj["features"] = door
                is_door = True
                break

        if is_door:
            classified_boxes.append(obj)
            continue

        # Check if it's a window by analyzing the color distribution inside the box
        x, y, w, h = cv2.boundingRect(box)
        cropped = img[y: y + h, x: x + w]
        total = np.sum(cropped)
        colored = np.sum(cropped > 0)
        low, high = 0.001, 0.00459
        amount_of_colored = colored / total

        # If the amount of colored pixels fits the threshold, classify it as a window
        if low < amount_of_colored < high:
            obj["type"] = "window"
            obj["box"] = box
            classified_boxes.append(obj)

    return classified_boxes

# Check if any points of a door are inside or close to the bounding box of another feature
def points_are_inside_or_close_to_box(door, box):
    """
    Checks if any points of the door are inside or near the bounding box.
    Args:
        door (list): List of points representing the door.
        box (list): List of points representing the bounding box.
    Returns:
        bool: True if the door is inside or close to the box, otherwise False.
    """
    for point in door:
        if rect_contains_or_almost_contains(point, box):
            return True
    return False

# Check if a point is inside or close to a bounding box
def rect_contains_or_almost_contains(pt, box):
    """
    Checks if a point is inside or close to a rectangle.
    Args:
        pt (tuple): A point (x, y).
        box (list): A list of points representing the bounding box.
    Returns:
        bool: True if the point is inside or almost inside the box, otherwise False.
    """
    x, y, w, h = cv2.boundingRect(box)
    is_inside = x < pt[0] < x + w and y < pt[1] < y + h
    # Check if the point is close to the bounding box
    min_dist = min(w, h)
    for point in box:
        dist = abs(point[0][0] - pt[0]) + abs(point[0][1] - pt[1])
        if dist <= min_dist:
            return True

    return is_inside

# Detect features using ORB
def feature_detect(img):
    """
    Detects key features in an image using ORB (Oriented FAST and Rotated BRIEF).
    Args:
        img (numpy.ndarray): Input image.
    """
    orb = cv2.ORB_create(nfeatures=10000000, scoreType=cv2.ORB_FAST_SCORE)
    kp = orb.detect(img, None)
    kp, _ = orb.compute(img, kp)
    img2 = cv2.drawKeypoints(img, kp, img, color=(0, 255, 0), flags=0)
    cv2.imshow("keypoints", img2)
    cv2.waitKey(0)

# Feature matching between two images
def feature_match(img1, img2):
    """
    Matches features between two images using ORB and a brute-force matcher.
    Args:
        img1 (numpy.ndarray): First image.
        img2 (numpy.ndarray): Second image (template to match).
    Returns:
        list: List of transformed doors after matching.
    """
    orb = cv2.ORB_create(nfeatures=10000000, scoreType=cv2.ORB_FAST_SCORE)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # Detect keypoints and descriptors for both images
    kp_model, des_model = orb.detectAndCompute(img2, None)
    kp_frame, des_frame = orb.detectAndCompute(img1, None)

    # Match features
    matches = bf.match(des_model, des_frame)
    matches = sorted(matches, key=lambda x: x.distance)

    # Perform geometric transformation based on the matched features
    return calculate_transformation(matches, kp_model, kp_frame, img1, img2)

# Calculate the transformation based on feature matches
def calculate_transformation(matches, kp_model, kp_frame, img1, img2):
    """
    Calculate the geometric transformation (rotation and scaling) between matched features.
    Args:
        matches (list): List of feature matches.
        kp_model (list): Keypoints for the model image.
        kp_frame (list): Keypoints for the frame image.
        img1 (numpy.ndarray): Frame image.
        img2 (numpy.ndarray): Model image.
    Returns:
        list: List of transformed door positions.
    """

    # Calculate door positions based on matched features
    list_of_proper_transformed_doors = []  # Initialize an empty list for transformed door positions
    for match in matches:
        img2_idx = match.queryIdx
        img1_idx = match.trainIdx
        (x1, y1) = kp_model[img2_idx].pt
        (x2, y2) = kp_frame[img1_idx].pt
        list_of_proper_transformed_doors.append(((x1, y1), (x2, y2)))
    return list_of_proper_transformed_doors

# Main function to run the detection process
if __name__ == "__main__":
    # Read images
    img0 = cv2.imread(example_image_path)
    img1 = cv2.imread(example_image_path, 0)
    door_list = []

    # Feature match each door image
    for door_image_path in door_image_paths:
        door_img = cv2.imread(door_image_path, 0)
        matched_doors = feature_match(img1, door_img)
        door_list.extend(matched_doors)

    # Detect windows and doors by calling the main detection function
    detect_windows_and_doors_boxes(img0, door_list)
