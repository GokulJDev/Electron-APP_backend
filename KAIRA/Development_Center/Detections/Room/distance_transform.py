from __future__ import print_function
import cv2 as cv
import numpy as np
import argparse
import random as rng
import sys
import os

"""
Perform wall detection and distance transform for floorplan processing.
"""

# Set paths for images and libraries
floorplan_lib_path = os.path.dirname(os.path.realpath(__file__)) + "/../../../"
example_image_path = (
    os.path.dirname(os.path.realpath(__file__)) + "/../../../Images/Examples/example.png"
)

# Add FloorplanToBlenderLib to path for imports
try:
    sys.path.insert(0, floorplan_lib_path)
    print(sys.path)
    from FloorplanToBlenderLib import detect  # import only the detect module
except ImportError:
    from FloorplanToBlenderLib import detect

# Random seed initialization for reproducible results
rng.seed(12345)

# Read the input floorplan image
src = cv.imread(example_image_path)

if src is None:
    raise FileNotFoundError("Error: Could not load the image. Check the path.")

# Step 1: Convert to grayscale
gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)

# Step 2: Initialize blank image for result visualization
height, width, channels = src.shape
blank_image = np.zeros((height, width, 3), np.uint8)

# Step 3: Wall detection and filtering
# 'wall_filter' function removes noise and isolates walls
wall_img = detect.wall_filter(gray)

# Visualize filtered wall image
cv.imshow("Wall Image", wall_img)

# Step 4: Detect wall bounding boxes
# 'precise_boxes' finds bounding boxes around detected walls
boxes, blank_image = detect.precise_boxes(wall_img, blank_image)

# Display wall boxes over a blank image
cv.imshow("Wall Boxes", blank_image)

# Step 5: Detect outer contours
# 'outer_contours' identifies the largest wall outline
contours, blank_image = detect.outer_contours(gray, blank_image, color=(255, 0, 0))

# Step 6: Set black background for further processing
src[np.all(src == 255, axis=2)] = 0
cv.imshow("Black Background Image", src)

# Step 7: Laplacian filtering for edge enhancement
kernel = np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]], dtype=np.float32)
imgLaplacian = cv.filter2D(src, cv.CV_32F, kernel)  # Apply Laplacian filter
sharp = np.float32(src)
imgResult = sharp - imgLaplacian  # Subtract edges from original to sharpen

# Convert to 8-bit grayscale
imgResult = np.clip(imgResult, 0, 255).astype("uint8")
cv.imshow("Sharpened Image", imgResult)

# Step 8: Binary thresholding for foreground extraction
bw = cv.cvtColor(imgResult, cv.COLOR_BGR2GRAY)
_, bw = cv.threshold(bw, 40, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
cv.imshow("Binary Image", bw)

# Step 9: Distance transform
dist = cv.distanceTransform(bw, cv.DIST_L2, 3)
cv.normalize(dist, dist, 0, 1.0, cv.NORM_MINMAX)  # Normalize to [0, 1]
cv.imshow("Distance Transform", dist)

# Step 10: Threshold peaks in the distance transform
_, dist = cv.threshold(dist, 0.5, 1.0, cv.THRESH_BINARY)
kernel1 = np.ones((3, 3), dtype=np.uint8)
dist = cv.dilate(dist, kernel1)  # Dilate to merge nearby peaks
cv.imshow("Peaks", dist)

# Step 11: Find contours of the peaks
dist_8u = dist.astype("uint8")
contours, _ = cv.findContours(dist_8u, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

# Step 12: Marker-based watershed segmentation
markers = np.zeros(dist.shape, dtype=np.int32)

# Draw markers for each detected peak
for i in range(len(contours)):
    cv.drawContours(markers, contours, i, (i + 1), -1)

# Draw background marker at (5, 5)
cv.circle(markers, (5, 5), 3, (255, 255, 255), -1)

# Apply watershed algorithm
cv.watershed(imgResult, markers)

# Convert markers to 8-bit for visualization
mark = markers.astype("uint8")
mark = cv.bitwise_not(mark)

# Step 13: Generate random colors for segmented regions
colors = []
for contour in contours:
    colors.append((rng.randint(0, 256), rng.randint(0, 256), rng.randint(0, 256)))

# Step 14: Visualize the final result with random colors
dst = np.zeros((markers.shape[0], markers.shape[1], 3), dtype=np.uint8)
for i in range(markers.shape[0]):
    for j in range(markers.shape[1]):
        index = markers[i, j]
        if index > 0 and index <= len(contours):
            dst[i, j, :] = colors[index - 1]

cv.imshow("Final Result", dst)

# Wait for user input and close windows
cv.waitKey(0)
cv.destroyAllWindows()
