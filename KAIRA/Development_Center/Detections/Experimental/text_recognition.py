import cv2
import numpy as np
import pytesseract  # Tesseract OCR for text recognition
import os

"""
Text recognition test with Tesseract OCR integration
"""

example_image_path = (
    os.path.dirname(os.path.realpath(__file__)) + "/../../../Images/Examples/example.png"
)

# Read image
img = cv2.imread(example_image_path)
mask = np.zeros(img.shape, dtype=np.uint8)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Pre-process image: Gaussian Blur and Thresholding
gray = cv2.GaussianBlur(gray, (9, 9), 1)
_, threshold = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

# Find contours in the thresholded image
contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Create list to store ROIs
ROI = []

# Process each contour
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    if h < 20:  # Filter small contours based on height
        cv2.drawContours(mask, [cnt], 0, (255, 255, 255), 1)

# Dilation to fill in gaps between contours
kernel = np.ones((7, 7), np.uint8)
dilation = cv2.dilate(mask, kernel, iterations=1)
gray_d = cv2.cvtColor(dilation, cv2.COLOR_BGR2GRAY)

# Threshold the dilated image to get contours for potential text areas
_, threshold_d = cv2.threshold(gray_d, 150, 255, cv2.THRESH_BINARY)
contours_d, hierarchy = cv2.findContours(threshold_d, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Loop over the contours to detect ROI
for cnt in contours_d:
    x, y, w, h = cv2.boundingRect(cnt)
    if w > 50:  # Filter contours based on width
        # Draw a green rectangle around detected text areas
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        roi_c = img[y : y + h, x : x + w]  # Extract the region of interest
        ROI.append(roi_c)

        # Use Tesseract OCR to extract text from each ROI
        text = pytesseract.image_to_string(roi_c)
        print(f"Detected text: {text.strip()}")  # Print detected text for each ROI

# Show the result with rectangles drawn around detected text areas
cv2.imshow("Detected Text Areas", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
