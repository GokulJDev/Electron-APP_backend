import cv2
import os
import numpy as np
from PIL import Image

# Define image path
example_image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../Images/Examples/example2.png")

# Scaling factor (upscale or downscale)
scalefactor = 2.5  # < 1 for downscale, > 1 for upscale

def pil_rescale_image(image, factor):
    """
    Rescale image using Pillow.
    :param image: Pillow Image object
    :param factor: scaling factor (1 means no change)
    :return: Resized Pillow Image object
    """
    width, height = image.size
    resized_image = image.resize((int(width * factor), int(height * factor)), resample=Image.BOX)
    return resized_image

def cv2_rescale_image(image, factor):
    """
    Rescale image using OpenCV.
    :param image: OpenCV image (numpy array)
    :param factor: scaling factor (1 means no change)
    :return: Resized OpenCV image (numpy array)
    """
    return cv2.resize(image, None, fx=factor, fy=factor)

def pil_to_cv2(image):
    """
    Convert Pillow image to OpenCV image (numpy array).
    :param image: Pillow Image object
    :return: OpenCV image (numpy array)
    """
    return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)

def main():
    # Open the image using PIL
    pil_image = Image.open(example_image_path)

    # Rescale image using OpenCV
    cv2_resized = cv2_rescale_image(pil_to_cv2(pil_image), scalefactor)

    # Rescale image using Pillow
    pil_resized = pil_rescale_image(pil_image, scalefactor)
    pil_resized_cv2 = pil_to_cv2(pil_resized)  # Convert resized Pillow image to OpenCV format

    # Display the original, OpenCV resized, and Pillow resized images
    cv2.imshow("Original Image", pil_to_cv2(pil_image))
    cv2.imshow("Resized with OpenCV", cv2_resized)
    cv2.imshow("Resized with Pillow", pil_resized_cv2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Optionally save the resized images
    # cv2.imwrite(os.path.join(os.path.dirname(os.path.realpath(__file__)), "rescaled_cv2.png"), cv2_resized)
    # cv2.imwrite(os.path.join(os.path.dirname(os.path.realpath(__file__)), "rescaled_pil.png"), pil_resized_cv2)

if __name__ == "__main__":
    main()
