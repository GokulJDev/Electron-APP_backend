import cv2
import numpy as np

def preprocess_image(img):
    """
    Preprocess the input grayscale image by removing noise and enhancing contrast.
    
    Steps:
    1. Apply Gaussian blur to smooth the image.
    2. Use adaptive thresholding to binarize the image, making room detection more robust.
    
    :param img: Grayscale image.
    :return: Binary (thresholded) image.
    """
    blurred = cv2.GaussianBlur(img, (5, 5), 0)  # Smooth the image to reduce noise
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2  # Adaptive thresholding with Gaussian method
    )
    return thresh


def find_rooms(
    img,
    noise_removal_threshold=1,
    corners_threshold=0.001,
    room_closing_max_length=10,
    gap_in_wall_threshold=500000,
):
    """
    Detect rooms in a grayscale floorplan image.

    Steps:
    1. Preprocess the image using adaptive thresholding.
    2. Remove small noise blobs.
    3. Detect corners using Harris Corner Detection.
    4. Close rooms by connecting nearby corners with lines.
    5. Identify and segment rooms using connected components.
    6. Assign random colors to each detected room for visualization.

    :param img: Grayscale image of rooms.
    :param noise_removal_threshold: Minimal area of blobs to be retained.
    :param corners_threshold: Threshold for detecting corners (0 to 1).
    :param room_closing_max_length: Max line length to close open doors.
    :param gap_in_wall_threshold: Minimum pixels to treat a region as a room.
    :return: rooms: List of numpy boolean masks for each detected room.
             colored_house: Colored version of the input image, where each room has a random color.
    """
    assert 0 <= corners_threshold <= 1

    # Step 1: Preprocess the image to binarize it
    thresh_img = preprocess_image(img)

    # Step 2: Remove small noise blobs
    img = remove_noise_blobs(thresh_img, noise_removal_threshold)

    # Step 3: Detect corners using Harris Corner Detection
    corners = detect_corners(img, corners_threshold)

    # Step 4: Close open rooms by connecting nearby corners
    img = close_open_rooms(img, corners, room_closing_max_length)

    # Step 5: Identify connected components to segment rooms
    rooms, img_colored = segment_rooms(img, gap_in_wall_threshold)

    return rooms, img_colored


def remove_noise_blobs(thresh_img, noise_removal_threshold):
    contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(thresh_img)  # Create a blank mask
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > noise_removal_threshold:  # Keep only large blobs
            cv2.fillPoly(mask, [contour], 255)
    return mask


def detect_corners(img, corners_threshold):
    dst = cv2.cornerHarris(img, 2, 3, 0.04)
    dst = cv2.dilate(dst, None)  # Dilate to make corners more visible
    return dst > corners_threshold * dst.max()


def close_open_rooms(img, corners, room_closing_max_length):
    for y, row in enumerate(corners):
        x_same_y = np.argwhere(row)
        for x1, x2 in zip(x_same_y[:-1], x_same_y[1:]):
            if x2[0] - x1[0] < room_closing_max_length:
                cv2.line(img, (x1[0], y), (x2[0], y), 255, 1)

    for x, col in enumerate(corners.T):
        y_same_x = np.argwhere(col)
        for y1, y2 in zip(y_same_x[:-1], y_same_x[1:]):
            if y2[0] - y1[0] < room_closing_max_length:
                cv2.line(img, (x, y1[0]), (x, y2[0]), 255, 1)
    return img


def segment_rooms(img, gap_in_wall_threshold):
    _, labels = cv2.connectedComponents(img)
    img_colored = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)  # Convert to color image for visualization
    unique_labels = np.unique(labels)
    rooms = []

    for label in unique_labels:
        if label == 0:  # Skip the background
            continue
        component = labels == label
        if np.count_nonzero(component) < gap_in_wall_threshold:  # Skip small areas
            continue
        rooms.append(component)
        rng = np.random.default_rng(seed=42)
        color = rng.integers(0, 255, size=3).tolist()  # Generate random color
        img_colored[component] = color

    return rooms, img_colored


# Example usage
import os

# Load the input image paths
example_img_path = "/mnt/data/example.png"

# Read the images in grayscale
example_img = cv2.imread(example_img_path, cv2.IMREAD_GRAYSCALE)

# Process the first image
rooms1, colored_house1 = find_rooms(example_img)
cv2.imshow("Rooms in Example Image", colored_house1)

cv2.waitKey(0)
cv2.destroyAllWindows()

