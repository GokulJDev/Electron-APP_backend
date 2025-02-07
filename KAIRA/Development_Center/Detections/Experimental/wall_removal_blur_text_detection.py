import cv2
import numpy as np
import os
import sys

# Use os.path.join for better path handling
floorplan_lib_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../")
example_image_path = os.path.join(floorplan_lib_path, "Images/Examples/example.png")

sys.path.insert(0, floorplan_lib_path)
from FloorplanToBlenderLib import detect  # Assuming detect is the only needed name

def test():
    """
    Test function for floorplan image processing and shape detection.
    """
    img = cv2.imread(example_image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, _, _ = img.shape

    # Example of wall detection (wall_filter and other functions assumed defined elsewhere)
    wall_img = detect.wall_filter(gray)
    _, _ = detect.and_remove_precise_boxes(wall_img, output_img=gray)

    # Morphological processing example
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 50, 250)
    kernel = cv2.getStructuringElement(2, (6, 6))
    closed = cv2.morphologyEx(edged, 3, kernel)

    # Detect contours
    cnts, _ = cv2.findContours(closed.copy(), 0, 1)
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        area = cv2.contourArea(c)

        if len(approx) >= 4 and area < 2000 and area > 450:
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(gray, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("Detected Shapes", gray)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("Test Done!")

if __name__ == "__main__":
    test()
