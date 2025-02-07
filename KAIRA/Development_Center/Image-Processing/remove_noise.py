import numpy as np
import cv2
import os

def main():
    # Set the path for the example image
    example_image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../Images/Examples/example.png")

    # Load the image
    img = cv2.imread(example_image_path)

    # Apply Non-Local Means Denoising for color images
    # Parameters:
    # - None: For default mask (use entire image)
    # - 10: Denoising strength (higher value means stronger denoising)
    # - 10: The same as above, but for color channels
    # - 7: Window size for pixel neighborhood (larger value = more neighbors)
    # - 21: Size of the search window used for denoising (larger value = more search area)
    denoised_img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

    # Display original and denoised images
    cv2.imshow("Original Image", img)
    cv2.imshow("Denoised Image", denoised_img)
    
    # Wait for a key press and close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
