import cv2
import os

# Construct the image path
example_image_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "../../../Images/Examples/example.png"
)

# Read the image
img = cv2.imread(example_image_path)
if img is None:
    raise FileNotFoundError(f"Image not found at path: {example_image_path}")

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Detect corners using Shi-Tomasi method (cv2.goodFeaturesToTrack)
# The method is used to detect good features to track in an image, which are typically corners.
# Parameters:
# - 1000: Max number of corners to detect.
# - 0.01: Quality level (lower value detects more corners).
# - 10: Minimum distance between detected corners.
corners = cv2.goodFeaturesToTrack(gray, 1000, 0.01, 10)

# Draw circles around detected corners
if corners is not None:
    for corner in corners:
        x, y = corner[0]
        cv2.circle(img, (int(x), int(y)), 5, (0, 255, 0), -1)

# Display the image
cv2.imshow("Corners Found", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

