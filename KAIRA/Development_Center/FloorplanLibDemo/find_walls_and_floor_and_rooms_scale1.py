"""
Small demo program for floorplan detections
Demonstrates wall, floor, room, and detail detection from a floorplan image
"""

import cv2
import numpy as np
import sys
import os

# Define paths to required libraries and example image
floorplan_lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
example_image_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../Images/Examples/example.png")
)

# Import the FloorplanToBlenderLib detection library
try:
    sys.path.insert(0, floorplan_lib_path)
    from FloorplanToBlenderLib import detect
except ImportError as e:
    print("Error importing FloorplanToBlenderLib:", e)
    sys.exit(1)


def test_floorplan_detections(image_path):
    """
    Perform detections for walls, floors, rooms, and details from a floorplan image.

    Args:
        image_path (str): Path to the floorplan image.

    Displays:
        - Detection results using OpenCV windows.
    """

    # Step 1: Load the input image
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Error: Image not found at {image_path}")

    # Make a copy for further use
    original_image = img.copy()

    # Step 2: Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Create a blank output image of the same size as the original
    height, width, _ = img.shape
    blank_image = np.zeros((height, width, 3), np.uint8)

    # -----------------------------------------
    # Wall Detection
    # -----------------------------------------
    print("Detecting walls...")
    wall_img = detect.wall_filter(gray)  # Filter out small objects to detect walls
    _, wall_detection_image = detect.precise_boxes(
        wall_img, blank_image.copy(), color=(0, 0, 255)
    )  # Mark walls with red color

    # -----------------------------------------
    # Floor Detection
    # -----------------------------------------
    print("Detecting floors...")
    _, floor_detection_image = detect.outer_contours(
        gray, blank_image.copy(), color=(255, 0, 0)
    )  # Detect outer contours (floor/roof) in blue

    # -----------------------------------------
    # Room Detection
    # -----------------------------------------
    print("Detecting rooms...")
    gray_inverted = ~wall_img  # Invert the wall image for room detection
    _, colored_rooms = detect.find_rooms(
        gray_inverted.copy(),
        noise_removal_threshold=50,
        corners_threshold=0.01,
        room_closing_max_length=130,
        gap_in_wall_min_threshold=5000,
    )
    _, room_detection_image = detect.precise_boxes(
        cv2.cvtColor(colored_rooms, cv2.COLOR_BGR2GRAY),
        blank_image.copy(),
        color=(0, 100, 200),
    )  # Rooms marked with light blue

    # -----------------------------------------
    # Detail Detection (Doors, etc.)
    # -----------------------------------------
    print("Detecting details...")
    _, colored_doors = detect.find_details(
        gray_inverted.copy(),
        noise_removal_threshold=50,
        corners_threshold=0.01,
        room_closing_max_length=130,
        gap_in_wall_max_threshold=5000,
        gap_in_wall_min_threshold=10,
    )
    _, details_detection_image = detect.precise_boxes(
        cv2.cvtColor(colored_doors, cv2.COLOR_BGR2GRAY),
        blank_image.copy(),
        color=(0, 200, 100),
    )  # Details marked with green

    # -----------------------------------------
    # Display Results
    # -----------------------------------------
    print("Displaying results...")
    cv2.imshow("Original Image", original_image)
    cv2.imshow("Wall Detection", wall_detection_image)
    cv2.imshow("Floor Detection", floor_detection_image)
    cv2.imshow("Room Detection", room_detection_image)
    cv2.imshow("Detail Detection", details_detection_image)

    # Wait for user input and clean up
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # Run the test function
    try:
        test_floorplan_detections(example_image_path)
    except Exception as e:
        print("An error occurred:", e)
