import cv2
import numpy as np
import matplotlib.pyplot as plt

def image(image, title="FTBL", wait=0):
    """
    Display an image using OpenCV's imshow function.
    
    Parameters:
    - image: The image to display.
    - title: The window title (default is "FTBL").
    - wait: Time to wait before closing the window (0 means wait indefinitely until a key is pressed).
    """
    cv2.imshow(title, image)
    cv2.waitKey(wait)


def points(image, points):
    """
    Draw points on the image.
    
    Parameters:
    - image: The image to draw on.
    - points: A list of points to be drawn as circles.

    Returns:
    - The updated image with points drawn on it.
    """
    for point in points:
        image = cv2.circle(image, point, radius=4, color=(0, 0, 0), thickness=5)
    return image


def contours(image, contours):
    """
    Draw contours on the image.

    Parameters:
    - image: The image to draw on.
    - contours: A list of contours to be drawn.

    Returns:
    - The updated image with contours drawn on it.
    """
    return cv2.drawContours(image, contours, -1, (0, 255, 0), 3)


def lines(image, lines):
    """
    Draw lines (polylines) on the image.
    
    Parameters:
    - image: The image to draw on.
    - lines: A list of lines to be drawn.

    Returns:
    - The updated image with lines drawn on it.
    """
    for line in lines:
        image = cv2.polylines(image, line, True, (0, 0, 255), 1, cv2.LINE_AA)
    return image


def verts(image, boxes):
    """
    Draw lines between vertices of boxes and display the image.
    
    Parameters:
    - image: The image to draw on.
    - boxes: A numpy array of boxes containing vertices.

    This function will use cv2.line to connect the vertices of each box.
    """
    for box in boxes:
        for wall in box:
            # Draw line between points of the box
            cv2.line(image,
                     (int(wall[0][0]), int(wall[1][1])), 
                     (int(wall[2][0]), int(wall[2][1])), 
                     (255, 0, 0), 5)  # Draw line in blue with thickness 5


def boxes(image, boxes, text=""):
    """
    Draw bounding boxes on the image and label them with text.
    
    Parameters:
    - image: The image to draw on.
    - boxes: A list of boxes (each box is a list of points).
    - text: Optional text to display inside each box.

    Returns:
    - The updated image with boxes drawn and labeled.
    """
    for box in boxes:
        # Calculate the bounding rectangle for each box
        (x, y, w, h) = cv2.boundingRect(box)
        
        # Draw rectangle
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 5)  # Red rectangle
        
        # Put text at the top-left corner of the rectangle
        cv2.putText(image, str(text), (x, y), 7, 10, (255, 0, 0))  # Blue text
        
    return image


def doors(img, doors):
    """
    Draw doors on the image.
    
    Parameters:
    - img: The image to draw on.
    - doors: A list of doors, where each door contains points and a bounding box.

    Returns:
    - The updated image with doors drawn.
    """
    for door in doors:
        # Draw points for each door
        img = points(img, door[0])
        
        # Draw bounding box for each door
        img = boxes(img, door[1])
        
    return img


def colormap(img, mapping=cv2.COLORMAP_HSV):
    """
    Apply a colormap to a grayscale image.
    
    Parameters:
    - img: The grayscale image.
    - mapping: The colormap to apply (default is cv2.COLORMAP_HSV).
    
    Returns:
    - The colormapped image.
    """
    return cv2.applyColorMap(img, mapping)


def histogram(img, title="Histogram", wait=0):
    """
    Plot the histogram of the image's pixel intensity values.
    
    Parameters:
    - img: The image to analyze.
    - title: The title of the histogram plot (default is "Histogram").
    - wait: Time to wait before closing the plot (0 for indefinite).
    
    Displays the image and its histogram using matplotlib.
    """
    # Calculate histogram of the image
    hist = np.histogram(img, bins=np.arange(0, 256))
    
    # Create a figure with two subplots
    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3))
    
    # Show the image on the first subplot
    ax1.imshow(img, cmap=plt.cm.gray, interpolation="nearest")
    ax1.axis("off")  # Hide axes
    
    # Plot the histogram on the second subplot
    ax2.plot(hist[1][:-1], hist[0], lw=2)
    ax2.set_title(title)
    
    # Show the plot
    if wait == 0:
        plt.show()
    else:
        plt.pause(wait)
