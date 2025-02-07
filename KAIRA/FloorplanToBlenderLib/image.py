import cv2
import numpy as np
from PIL import Image
from . import calculate
from . import const

# Rescale an image using PIL
def pil_rescale_image(image, factor):
    """
    Rescale image using PIL.
    
    Parameters:
    - image: The PIL Image object to be rescaled.
    - factor: The scaling factor by which the image size should be changed.
    
    Returns:
    - Rescaled PIL image.
    """
    width, height = image.size
    return image.resize((int(width * factor), int(height * factor)), resample=Image.BOX)

# Rescale an image using OpenCV
def cv2_rescale_image(image, factor):
    """
    Rescale image using OpenCV.
    
    Parameters:
    - image: The image array to be rescaled.
    - factor: The scaling factor to rescale the image dimensions.
    
    Returns:
    - Rescaled OpenCV image.
    """
    return cv2.resize(image, None, fx=factor, fy=factor)

# Convert PIL image to OpenCV format
def pil_to_cv2(image):
    """
    Convert PIL image to OpenCV format.
    
    Parameters:
    - image: The PIL Image object.
    
    Returns:
    - OpenCV image (BGR format).
    """
    return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)

# Calculate scale factor based on preferred and actual values
def calculate_scale_factor(preferred: float, value: float):
    """
    Calculate the scale factor for resizing an image.
    
    Parameters:
    - preferred: The desired reference size.
    - value: The current value to compare with the preferred size.
    
    Returns:
    - The scale factor to adjust the image size.
    """
    return preferred / value

# Denoising the image using OpenCV's fastNlMeansDenoisingColored function
def denoising(img):
    """
    Apply denoising to the image to reduce noise.
    
    Parameters:
    - img: The input image to be denoised.
    
    Returns:
    - Denoised image.
    """
    return cv2.fastNlMeansDenoisingColored(
        img,
        None,
        const.IMAGE_H,
        const.IMAGE_HCOLOR,
        const.IMAGE_TEMPLATE_SIZE,
        const.IMAGE_SEARCH_SIZE,
    )

# Remove noise from the image using a specified threshold
def remove_noise(img, noise_removal_threshold):
    """
    Remove noise from the image and return a mask based on the threshold.
    This function helps in identifying and isolating the room area from other noise.
    
    Parameters:
    - img: The input image to remove noise from.
    - noise_removal_threshold: The threshold for the minimum area of valid contours to keep.
    
    Returns:
    - mask: A binary mask where areas of significant contours are kept, and others are set to 0.
    """
    # Convert pixel values below 128 to 0 and above 128 to 255 (binary thresholding)
    img[img < 128] = 0
    img[img > 128] = 255
    
    # Find external contours in the image
    contours, _ = cv2.findContours(~img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(img)
    
    # Fill the contours with significant areas in the mask
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > noise_removal_threshold:
            cv2.fillPoly(mask, [contour], 255)
    
    return mask

# Mark the outside of the house as black, used for eliminating irrelevant areas
def mark_outside_black(img, mask):
    """
    Mark the outside areas (outside the house) as black in the image, useful for focusing on internal features.
    
    Parameters:
    - img: The image to process.
    - mask: The mask to guide which areas to modify.
    
    Returns:
    - img: The processed image with the outside marked as black.
    - mask: Updated mask.
    """
    # Find the external contours of the image (outside the house)
    contours, _ = cv2.findContours(~img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]
    biggest_contour = max(contour_sizes, key=lambda x: x[0])[1]
    
    # Create a new mask filled with black except for the biggest contour
    mask = np.zeros_like(mask)
    cv2.fillPoly(mask, [biggest_contour], 255)
    
    # Set all areas outside the biggest contour to black
    img[mask == 0] = 0
    
    return img, mask

# Detect how much the image needs to be rescaled based on wall size
def detect_wall_rescale(reference_size, image):
    """
    Detect the scaling factor needed for the image based on the reference wall size.
    
    Parameters:
    - reference_size: The reference size to scale the image to.
    - image: The image to analyze for wall width.
    
    Returns:
    - scale factor: The calculated scaling factor, or None if no walls are detected.
    """
    # Calculate the average width of the walls in the image
    image_wall_size = calculate.wall_width_average(image)
    
    # If no walls were found, return None
    if image_wall_size is None:  
        return None
    
    # Return the scale factor for resizing the image
    return calculate_scale_factor(float(reference_size), image_wall_size)
