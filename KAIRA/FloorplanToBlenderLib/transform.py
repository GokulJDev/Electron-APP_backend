import math
import cv2
import numpy as np

from . import const

"""
Transform
This file contains functions for transforming data between different formats, such as scaling, rotating, and generating vertices for floorplans.

FloorplanToBlender3d
Copyright (C) 2022 Daniel Westberg
"""


def rescale_rect(list_of_rects, scale_factor):
    """
    Rescale rectangles relative to their center point.
    
    @param list_of_rects: List of rectangles, where each is a contour (array of points).
    @param scale_factor: The scaling factor to apply to the rectangle.
    @return: A list of rescaled rectangles (contours).
    """
    rescaled_rects = []
    for rect in list_of_rects:
        x, y, w, h = cv2.boundingRect(rect)  # Get bounding rectangle

        # Find the center of the rectangle
        center = (x + w / 2, y + h / 2)

        # Calculate how much the sides of the rectangle should change
        xdiff = abs(center[0] - x)
        ydiff = abs(center[1] - y)

        # Apply the scale factor
        xshift = xdiff * scale_factor
        yshift = ydiff * scale_factor

        # New dimensions of the rescaled rectangle
        width = 2 * xshift
        height = 2 * yshift

        # Top-left corner of the rescaled rectangle
        new_x = x - abs(xdiff - xshift)
        new_y = y - abs(ydiff - yshift)

        # Create a contour for the rescaled rectangle
        contour = np.array(
            [
                [[new_x, new_y]],
                [[new_x + width, new_y]],
                [[new_x + width, new_y + height]],
                [[new_x, new_y + height]],
            ]
        )
        rescaled_rects.append(contour)

    return rescaled_rects


def flatten(in_list):
    """
    Flatten a multidimensional list into a single-dimensional array.
    
    @param in_list: The input list to flatten.
    @return: A flattened list.
    """
    if in_list == []:
        return []
    elif type(in_list) is not list:
        return [in_list]
    else:
        return flatten(in_list[0]) + flatten(in_list[1:])


def rotate_round_origin_vector_2d(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.
    The angle should be given in radians.
    
    @param origin: The point of rotation (x, y).
    @param point: The point to rotate (x, y).
    @param angle: The rotation angle in radians.
    @return: The new point coordinates (x, y) after rotation.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def scale_model_point_to_origin(origin, point, x_scale, y_scale):
    """
    Scale a 2D vector between two points.
    
    @param origin: The origin point to scale from.
    @param point: The point to scale.
    @param x_scale: The scaling factor in the x direction.
    @param y_scale: The scaling factor in the y direction.
    @return: The scaled point.
    """
    dx, dy = (point[0] - origin[0], point[1] - origin[1])
    return (dx * x_scale, dy * y_scale)


def flatten_iterative_safe(thelist, res):
    """
    Iteratively flatten a list, handling empty elements and nested structures.
    Useful when flattening floorplan vertices.
    
    @param thelist: The incoming list to flatten.
    @param res: The resulting list, preferably empty.
    @return: A flattened list.
    """
    if not thelist or not isinstance(thelist, list):
        return res
    else:
        if isinstance(thelist[0], int) or isinstance(thelist[0], float):
            res.append(thelist[0])
            return flatten_iterative_safe(thelist[1:], res)
        else:
            res.extend(flatten_iterative_safe(thelist[0], []))
            return flatten_iterative_safe(thelist[1:], res)


def verts_to_poslist(verts):
    """
    Convert vertices to a list of positions (x, y, z).
    
    @param verts: The list of vertices (undecided size).
    @return: A list of positions in 3D space (x, y, z).
    """
    list_of_elements = flatten_iterative_safe(verts, [])  # Flatten the vertices

    res = []
    i = 0
    while i < len(list_of_elements) - 2:  # Might miss one vertex here!
        res.append(
            [list_of_elements[i], list_of_elements[i + 1], list_of_elements[i + 2]]
        )
        i += 3
    return res


def scale_point_to_vector(boxes, pixelscale=100, height=0, scale=np.array([1, 1, 1])):
    """
    Scale points to a vector based on pixel scale and height.
    
    @param boxes: List of boxes to scale.
    @param pixelscale: The scale factor for pixel resolution.
    @param height: The height at which the box should be placed.
    @param scale: The scale factor for each axis.
    @return: The scaled positions as a list of vectors.
    """
    res = []
    for box in boxes:
        for pos in box:
            res.extend([[(pos[0]) / pixelscale, (pos[1]) / pixelscale, height]])
    return res


def list_to_nparray(list, default=np.array([1, 1, 1])):
    """
    Convert a list to a numpy array, defaulting to a specified value if the list is None.
    
    @param list: The list to convert.
    @param default: The default value to return if the list is None.
    @return: A numpy array representation of the list.
    """
    if list is None:
        return default
    else:
        return np.array([list[0], list[1], list[2]])


def create_4xn_verts_and_faces(
    boxes,
    height=1,
    pixelscale=100,
    scale=np.array([1, 1, 1]),
    ground=False,
    ground_height=const.WALL_GROUND,
):
    """
    Create vertices and faces for 3D objects based on box contours.
    
    @param boxes: List of boxes to generate vertices for.
    @param height: Height of the objects in 3D space.
    @param scale: Scale factors for the x, y, and z axes.
    @param ground: Whether to include a ground level.
    @param ground_height: The height of the ground.
    @return: Vertices and faces for the boxes, along with the number of walls created.
    """
    counter = 0
    verts = []

    # Create vertices
    for box in boxes:
        verts.extend([scale_point_to_vector(box, pixelscale, height, scale)])
        if ground:
            verts.extend([scale_point_to_vector(box, pixelscale, ground_height, scale)])
        counter += 1

    faces = []

    # Create faces
    for room in verts:
        count = 0
        temp = ()
        for _ in room:
            temp = temp + (count,)
            count += 1
        faces.append([(temp)])

    return verts, faces, counter


def create_nx4_verts_and_faces(
    boxes, height=1, scale=np.array([1, 1, 1]), pixelscale=100, ground=const.WALL_GROUND
):
    """
    Create vertices and faces for vertical 3D objects based on box contours.
    
    @param boxes: List of boxes to generate vertices for.
    @param height: Height of the objects in 3D space.
    @param scale: Scale factors for the x, y, and z axes.
    @param pixelscale: The scale factor for pixel resolution.
    @param ground: The height of the ground level.
    @return: Vertices and faces for the boxes, along with the number of walls created.
    """
    counter = 0
    verts = []

    for box in boxes:
        box_verts = []
        for index in range(0, len(box)):
            temp_verts = []
            current = box[index][0]  # Current position
            next_vert = box[index + 1][0] if len(box) - 1 >= index + 1 else box[0][0]

            # Create the 3D positions for each wall
            temp_verts.extend([((current[0]) / pixelscale, (current[1]) / pixelscale, ground)])
            temp_verts.extend([((current[0]) / pixelscale, (current[1]) / pixelscale, height)])
            temp_verts.extend([((next_vert[0]) / pixelscale, (next_vert[1]) / pixelscale, ground)])
            temp_verts.extend([((next_vert[0]) / pixelscale, (next_vert[1]) / pixelscale, height)])

            box_verts.extend([temp_verts])
            counter += 1

        verts.extend([box_verts])

    faces = [(0, 1, 3, 2)]
    return verts, faces, counter


def create_verts(boxes, height, pixelscale=100):
    """
    Simplified function to convert 2D positions to 3D positions and add height.
    
    @param boxes: List of 2D boxes to convert.
    @param height: Height to assign in the z-axis.
    @param scale: Scale factor for the x, y, and z axes.
    @return: A list of 3D vertices.
    """
    verts = []

    # Convert each 2D box to 3D by adding the height value
    for box in boxes:
        temp_verts = []
        for pos in box:
            temp_verts.extend([((pos[0][0]) / pixelscale, (pos[0][1]) / pixelscale, 0.0)])
            temp_verts.extend([((pos[0][0]) / pixelscale, (pos[0][1]) / pixelscale, height)])

        verts.extend(temp_verts)

    return verts
