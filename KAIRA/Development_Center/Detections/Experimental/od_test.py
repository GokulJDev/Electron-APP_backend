import cv2
import numpy as np
import os

def rotate_image(image, angle):
    """Rotate an image by the given angle."""
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image, matrix, (w, h))
    return rotated_image

def template_matching_with_rotation(image, templates, rotation_step=10):
    """Perform template matching by rotating each template through all angles."""
    best_matches = []
    
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    for template in templates:
        max_val = -1
        best_match = None
        best_angle = 0
        template_w, template_h = template.shape

        # Try different rotations for the current template
        for angle in range(0, 360, rotation_step):
            rotated_template = rotate_image(template, angle)
            result = cv2.matchTemplate(gray_image, rotated_template, cv2.TM_CCOEFF)
            _, max_temp_val, _, max_loc = cv2.minMaxLoc(result)

            # Update the best match if a better match is found
            if max_temp_val > max_val:
                max_val = max_temp_val
                best_match = max_loc
                best_angle = angle

        if best_match:
            best_matches.append((best_match, best_angle, template_w, template_h))

    return best_matches

# Paths to the images
example_image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../Images/Examples/example.png")
window_image_paths = [
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../Images/Models/Windows/window1.png"),
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../Images/Models/Windows/window2.png"),
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../Images/Models/Windows/window3.png"),
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../Images/Models/Windows/window4.png")
]

# Load images
image = cv2.imread(example_image_path)
templates = [cv2.imread(path, 0) for path in window_image_paths]  # Load templates in grayscale

# Perform template matching with rotation for multiple templates
best_matches = template_matching_with_rotation(image, templates)

# Draw bounding boxes around the detected windows
for match in best_matches:
    top_left = match[0]
    template_w, template_h = match[2], match[3]
    bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
    cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 5)

    print(f"Best match found at angle: {match[1]} degrees")

# Show the result
cv2.imshow("Objects found", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
