import os
import cv2 as cv
import numpy as np

"""
We test template matching on multiple door and window images from different angles or types.
"""

example_image_path = (
    os.path.dirname(os.path.realpath(__file__)) + "/../../../Images/Examples/example.png"
)

# Paths for multiple door and window templates
door_image_paths = [
    os.path.dirname(os.path.realpath(__file__)) + "/../../../Images/Models/Doors/door1.png",
    os.path.dirname(os.path.realpath(__file__)) + "/../../../Images/Models/Doors/door2.png",
    os.path.dirname(os.path.realpath(__file__)) + "/../../../Images/Models/Doors/door3.png"
]

window_image_paths = [
    os.path.dirname(os.path.realpath(__file__)) + "/../../../Images/Models/Windows/window1.png",
    os.path.dirname(os.path.realpath(__file__)) + "/../../../Images/Models/Windows/window2.png",
    os.path.dirname(os.path.realpath(__file__)) + "/../../../Images/Models/Windows/window3.png",
    os.path.dirname(os.path.realpath(__file__)) + "/../../../Images/Models/Windows/window4.png"
]

def match(image, template, name, threshold=0.99):
    """
    Match and show result
    """
    img_rgb = image
    img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)

    test(img_gray, template, cv.TM_CCOEFF_NORMED, threshold, "TM_CCOEFF_NORMED " + name)
    test(img_gray, template, cv.TM_CCORR_NORMED, threshold, "TM_CCORR_NORMED " + name)
    test(img_gray, template, cv.TM_SQDIFF_NORMED, threshold, "TM_SQDIFF_NORMED " + name)
    cv.imshow(name, template)


def test(img_gray, template, alg, threshold, name):
    res = cv.matchTemplate(img_gray, template, alg)
    loc = np.nonzero(res >= threshold)
    w, h = template.shape[::-1]
    show(loc, name, w, h)


def show(loc, name, w, h, max=100):
    i = 0
    for pt in zip(*loc[::-1]):
        # Draw rectangles around matched areas
        cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        if i > max:
            print("Max " + str(max) + " reached!")
            break
        i += 1

    cv.imshow(name, img_rgb)
    cv.waitKey(0)  # will wait here for key presses


# Load the example image
img_rgb = cv.imread(example_image_path)

# Loop through all door and window templates and perform matching
for door_image_path in door_image_paths:
    door_template = cv.imread(door_image_path, 0)  # Load each door template
    print(f"Matching for door: {door_image_path}")
    match(img_rgb, door_template, f"door_{os.path.basename(door_image_path)}")

for window_image_path in window_image_paths:
    window_template = cv.imread(window_image_path, 0)  # Load each window template
    print(f"Matching for window: {window_image_path}")
    match(img_rgb, window_template, f"window_{os.path.basename(window_image_path)}")
