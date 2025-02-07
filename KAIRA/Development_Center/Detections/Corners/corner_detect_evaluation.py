import cv2
import numpy as np
import os

example_image_path = (
    os.path.dirname(os.path.realpath(__file__)) + "/../../../Images/Examples/example.png"
)

# Read the image and convert to grayscale
img = cv2.imread(example_image_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply Gaussian blur to smooth the image and reduce noise
img_gaussian = cv2.GaussianBlur(gray, (3, 3), 0)

# Canny edge detection
img_canny = cv2.Canny(img, 100, 200)

# Sobel edge detection (X and Y gradients)
img_sobelx = cv2.Sobel(img_gaussian, cv2.CV_8U, 1, 0, ksize=5)  # X-direction
img_sobely = cv2.Sobel(img_gaussian, cv2.CV_8U, 0, 1, ksize=5)  # Y-direction
img_sobel = img_sobelx + img_sobely  # Combine both X and Y gradients

# Prewitt edge detection (X and Y gradients)
kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])  # Prewitt X kernel
kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])  # Prewitt Y kernel
img_prewittx = cv2.filter2D(img_gaussian, -1, kernelx)  # Apply Prewitt X
img_prewitty = cv2.filter2D(img_gaussian, -1, kernely)  # Apply Prewitt Y

# Laplacian edge detection (second derivative)
laplacian = cv2.Laplacian(img, cv2.CV_64F)

# Show all the results
cv2.imshow("Original Image", img)
cv2.imshow("Canny", img_canny)  # Appears to be best for general edge detection
cv2.imshow("Sobel X", img_sobelx)
cv2.imshow("Sobel Y", img_sobely)
cv2.imshow("Sobel", img_sobel)
cv2.imshow("Prewitt X", img_prewittx)
cv2.imshow("Prewitt Y", img_prewitty)
cv2.imshow("Prewitt", img_prewittx + img_prewitty)
cv2.imshow("Laplacian", laplacian)  # Second best for edge detection

cv2.waitKey(0)
cv2.destroyAllWindows()
