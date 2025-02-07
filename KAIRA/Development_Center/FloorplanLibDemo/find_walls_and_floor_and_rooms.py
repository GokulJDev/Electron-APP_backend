"""
Small Demo Program for Floorplan Detections
This script uses the FloorplanToBlenderLib to:
- Detect walls, rooms, and details (e.g., doors/windows) in a floorplan image.

Dependencies:
- OpenCV
- FloorplanToBlenderLib (custom library)
"""

import cv2
import numpy as np
import sys
import os

# Setup paths
floorplan_lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
example_image_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../Images/Examples/example.png")
)

# Import the 'detect' module
try:
    sys.path.insert(0, floorplan_lib_path)
    from FloorplanToBlenderLib import detect  # Import detection functions
except ImportError as e:
    print("Error importing FloorplanToBlenderLib.detect:", e)
    sys.exit(1)


def test_detection(image_path):
    """
    Test floorplan image detections: walls, rooms, and details.

    Args:
        image_path (str): Path to the input floorplan image.

    Displays:
        - Detection results for walls, rooms, and details.
    """
    # Step 1: Load and prepare the image
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Error: Image not found at {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale

    # Prepare blank output image (same dimensions as input)
    height, width, _ = img.shape
    blank_image = np.zeros((height, width, 3), np.uint8)

    # ------------------------------------------
    # Wall Detection
    # ------------------------------------------
    print("Detecting walls...")
    wall_img = detect.wall_filter(gray)
    _, wall_result = detect.precise_boxes(wall_img, blank_image.copy(), color=(0, 0, 255))  # Red walls

    # ------------------------------------------
    # Floor Detection
    # ------------------------------------------
    print("Detecting floor contours...")
    contour_result, _ = detect.outer_contours(gray, blank_image.copy(), color=(255, 0, 0))  # Blue contour

    # ------------------------------------------
    # Room Detection
    # ------------------------------------------
    print("Detecting rooms...")
    _, colored_rooms = detect.find_rooms(gray.copy())  # Detect rooms
    gray_rooms = cv2.cvtColor(colored_rooms, cv2.COLOR_BGR2GRAY)
    _, room_result = detect.precise_boxes(gray_rooms, blank_image.copy(), color=(0, 100, 200))  # Green rooms

    # ------------------------------------------
    # Detail Detection (Doors/Windows)
    # ------------------------------------------
    print("Detecting details...")
    _, colored_doors = detect.find_details(gray.copy())
    gray_details = cv2.cvtColor(colored_doors, cv2.COLOR_BGR2GRAY)
    _, details_result = detect.precise_boxes(gray_details, blank_image.copy(), color=(0, 200, 100))  # Green details

    # ------------------------------------------
    # Display Results
    # ------------------------------------------
    print("Displaying results...")
    cv2.imshow("Original Image", img)
    cv2.imshow("Wall Detection", wall_result)
    cv2.imshow("Floor Contours", contour_result)
    cv2.imshow("Room Detection", room_result)
    cv2.imshow("Detail Detection (Doors/Windows)", details_result)

    # Wait and clean up
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        test_detection(example_image_path)
    except Exception as e:
        print("An error occurred:", e)
