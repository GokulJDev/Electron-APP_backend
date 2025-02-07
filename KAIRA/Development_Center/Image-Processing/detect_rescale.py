import cv2
import numpy as np
import os
import sys

try:
    sys.path.insert(1, sys.path[0] + "/../..")
    from FloorplanToBlenderLib import detect  # floorplan to blender lib
except ImportError as e:
    print(e)
    raise ImportError  # floorplan to blender lib


def main():
    try:
        # Get preferred pixel per wall size from the first image
        path = os.path.dirname(os.path.realpath(__file__)) + "/../../Images/Examples/example.png"
        img = cv2.imread(path)
        preferred = calculate_wall_width_average(img)

        # Get 2 examples to test against and calculate scale factors
        path = os.path.dirname(os.path.realpath(__file__)) + "/../../Images/Examples/example2.png"
        img = cv2.imread(path)
        too_small1 = calculate_wall_width_average(img)
        scalefactor1 = calculate_scale_factor(preferred, too_small1)

        path = os.path.dirname(os.path.realpath(__file__)) + "/../../Images/Examples/example3.png"
        img = cv2.imread(path)
        too_small2 = calculate_wall_width_average(img)
        scalefactor2 = calculate_scale_factor(preferred, too_small2)

        # Output the results
        print("The preferred pixel size per wall is : ", preferred)
        print("Example image 2 should be scaled by : ", scalefactor1)
        print("Example image 3 should be scaled by : ", scalefactor2)

    except Exception as e:
        print("Error in processing:", e)


def calculate_scale_factor(preferred, value):
    return preferred / value


def calculate_wall_width_average(img):
    # Calculates average pixels per image wall
    try:
        # grayscale image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Resulting image
        height, width, _ = img.shape
        blank_image = np.zeros(
            (height, width, 3), np.uint8
        )  # output image same size as original

        # Create wall image (filter out small objects from image)
        wall_img = detect.wall_filter(gray)

        # Detect walls (precise bounding boxes)
        boxes, img = detect.detectPreciseBoxes(wall_img, blank_image)

        # Filter out to only count walls
        filtered_boxes = list()
        for box in boxes:
            if len(box) == 4:  # Only consider boxes with 4 corners (rectangles)
                _, _, w, h = cv2.boundingRect(box)
                # Calculate the shortest side (either width or height)
                shortest = min(w, h)
                filtered_boxes.append(shortest)

        # Calculate and return the average of all the shortest wall sizes
        return average(filtered_boxes)

    except Exception as e:
        print("Error in wall detection:", e)
        return 0  # Return 0 if something goes wrong


def average(lst):
    return sum(lst) / len(lst) if lst else 0


if __name__ == "__main__":
    main()
