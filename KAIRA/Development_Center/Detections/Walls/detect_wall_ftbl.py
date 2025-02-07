import cv2
import numpy as np
import os
import sys

# Attempt to import external library for floorplan processing
try:
    # Add FloorplanToBlenderLib path
    sys.path.insert(1, sys.path[0] + "/../../..")
    print("Updated sys.path:", sys.path)
    from FloorplanToBlenderLib import detect  # Import only the detect function from custom floorplan library
except ImportError as e:
    print(f"Error: {e}")
    raise ImportError("FloorplanToBlenderLib module not found. Ensure the path is correct.")


def main():
    """
    Main function to perform floorplan wall detection and display results.
    """
    # Define image path
    example_image_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "../../../Images/Examples/example.png",
    )

    # Step 1: Load floorplan image
    img = cv2.imread(example_image_path)
    if img is None:
        print("Error: Could not read the image. Check the path:", example_image_path)
        return

    # Step 2: Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Step 3: Initialize a blank image for results
    height, width, _ = img.shape
    blank_image = np.zeros((height, width, 3), np.uint8)

    # Step 4: Detect walls using custom library function
    # wall_filter removes unnecessary small objects, leaving prominent walls
    wall_img = detect.wall_filter(gray)

    # Step 5: Detect precise wall bounding boxes
    # precise_boxes returns bounding box coordinates over detected walls
    _, result_img = detect.precise_boxes(wall_img, blank_image)

    # Step 6: Display original and result images
    cv2.imshow("Original Image", img)
    cv2.imshow("Wall Detection Result", result_img)
    cv2.waitKey(0)  # Wait until a key is pressed
    cv2.destroyAllWindows()  # Close all image windows


if __name__ == "__main__":
    main()
