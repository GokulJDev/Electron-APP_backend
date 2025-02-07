"""
Test function from StackOverflow:
https://stackoverflow.com/questions/55356251/how-to-detect-doors-and-windows-from-a-floor-plan-image
"""

import cv2
import matplotlib.pyplot as plt
import numpy as np
import os

# Define the path to the example image
example_image_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "../../../Images/Examples/example.png",
)

# Step 1: Load the input image
img = cv2.imread(example_image_path)
if img is None:
    raise FileNotFoundError(f"Error: Could not load image at {example_image_path}")

# Step 2: Convert image to binary (black and white) using a threshold
# - Pixels with intensity > 20 are set to white (255), others to black (0)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img_bw = 255 * (gray > 20).astype("uint8")

# Step 3: Apply morphological operations
# - Closing: Removes small holes in the foreground
# - Opening: Removes small noise in the background
se1 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))  # Structuring element for closing
se2 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))  # Structuring element for opening

mask = cv2.morphologyEx(img_bw, cv2.MORPH_CLOSE, se1)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, se2)

# Step 4: Mask the original image
# - Convert mask to 3 channels and normalize to range [0, 1]
mask = np.dstack([mask, mask, mask]) / 255  # Broadcast mask to 3 channels
out = img * mask  # Apply mask to the original image

# Step 5: Display the result
plt.figure(figsize=(15, 10))
plt.imshow(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))  # Convert BGR to RGB for Matplotlib
plt.title("Filtered Floorplan")
plt.axis("off")
plt.show()

# Step 6: Display using OpenCV (alternative)
cv2.imshow("Filtered Floorplan", out)
cv2.waitKey(0)
cv2.destroyAllWindows()
