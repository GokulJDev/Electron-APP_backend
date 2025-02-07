"""
Demo program for floorplan detections
Allows detection of walls and details (e.g., doors/windows) in floorplan images.

Dependencies:
- OpenCV
- FloorplanToBlenderLib (custom library)
"""

import cv2
import numpy as np
import sys
import os

# Paths setup
floorplan_lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
example_image_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../Images/Examples/example.png")
)

# Import the detect module from FloorplanToBlenderLib
try:
    sys.path.insert(0, floorplan_lib_path)
    from FloorplanToBlenderLib import detect  # Import detect functions
except ImportError as e:
    print("Error importing FloorplanToBlenderLib.detect:", e)
    sys.exit(1)


def process_floorplan(image_path):
    """
    Process a floorplan image to detect walls and details.

    Args:
        image_path (str): Path to the input floorplan image.

    Displays:
        - Detection results via OpenCV windows.
    """

    # Step 1: Read the floorplan image
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Error: Image not found at {image_path}")
    original_image = img.copy()

    # Step 2: Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Create a blank output image (same size as original)
    height, width, _ = img.shape
    blank_image = np.zeros((height, width, 3), np.uint8)

    # -----------------------------------------
    # Wall Detection
    # -----------------------------------------
    print("Detecting walls...")
    wall_img = detect.wall_filter(gray)  # Filter walls
    _, wall_detection_image = detect.precise_boxes(
        wall_img, blank_image.copy(), color=(0, 0, 255)
    )  # Mark walls in red

    # -----------------------------------------
    # Detail Detection (Doors/Windows)
    # -----------------------------------------
    print("Detecting details...")
    inverted_gray = ~wall_img  # Invert wall image for detail detection
    _, colored_doors = detect.find_details(
        inverted_gray,
        noise_removal_threshold=50,
        corners_threshold=0.1,
        room_closing_max_length=150,
        gap_in_wall_max_threshold=2000,
        gap_in_wall_min_threshold=100,
    )

    # Mark detected details (e.g., doors/windows) in green
    gray_details = cv2.cvtColor(colored_doors, cv2.COLOR_BGR2GRAY)
    _, details_detection_image = detect.precise_boxes(
        gray_details, blank_image.copy(), color=(0, 200, 100)
    )

    # -----------------------------------------
    # Display Results
    # -----------------------------------------
    print("Displaying results...")
    cv2.imshow("Original Floorplan", original_image)
    cv2.imshow("Wall Detection", wall_detection_image)
    cv2.imshow("Details Detection (Doors/Windows)", details_detection_image)

    # Wait for user input to close windows
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        process_floorplan(example_image_path)
    except Exception as e:
        print("An error occurred:", e)
