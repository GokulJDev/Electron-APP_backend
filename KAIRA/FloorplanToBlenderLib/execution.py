from . import generate
import numpy as np
from scipy.spatial.transform import Rotation as R
from math import atan2, degrees

def simple_single(floorplan, show=True):
    """
    Generate a single simple floorplan.

    Parameters:
    - floorplan: The path to the image of the floorplan.
    - show: Boolean to determine if the result should be shown.

    Returns:
    - The path to the generated files.
    """
    # Generate all files for the given floorplan and return the file path
    filepath, _ = generate.generate_all_files(floorplan, show)
    return filepath


def multiple_axis(
    floorplans,
    axis,
    dir=1,
    worldpositionoffset=np.array([0, 0, 0]),
    worldrotationoffset=np.array([0, 0, 0]),
    worldscale=np.array([1, 1, 1]),
    margin=None,
):
    """
    Generates several new apartments along a specific axis ("x", "y", or "z").

    Parameters:
    - axis: The axis along which apartments should be generated ("x", "y", or "z").
    - dir: The direction of movement along the axis (+1 or -1).
    - margin: Optional margin to be added to the position.
    - worldpositionoffset: Offset for the world position of the apartments.
    - worldrotationoffset: Rotation offset applied to each floorplan.
    - worldscale: Scaling applied to the floorplans.
    - floorplans: A list of paths to the floorplan images to be used.
    
    Returns:
    - A list of paths to the generated data files.
    """
    data_paths = list()  # List to hold the file paths
    fshape = None  # Placeholder for the shape of the previous floorplan

    if margin is None:
        margin = np.array([0, 0, 0])

    # Loop through each floorplan and generate the necessary files
    for floorplan in floorplans:
        if fshape is not None:
            # Use the shape of the previous floorplan for positioning
            if axis == "y":
                filepath, fshape = generate.generate_all_files(
                    floorplan,
                    True,
                    world_direction=dir,
                    world_scale=worldscale,
                    world_position=np.array([0, fshape[1], 0]) + worldpositionoffset + margin,
                    world_rotation=worldrotationoffset,
                )
            elif axis == "x":
                filepath, fshape = generate.generate_all_files(
                    floorplan,
                    True,
                    world_scale=worldscale,
                    world_position=np.array([fshape[0], 0, 0]) + worldpositionoffset + margin,
                    world_rotation=worldrotationoffset,
                    world_direction=dir,
                )
            elif axis == "z":
                filepath, fshape = generate.generate_all_files(
                    floorplan,
                    True,
                    world_scale=worldscale,
                    world_position=np.array([0, 0, fshape[2]]) + worldpositionoffset + margin,
                    world_rotation=worldrotationoffset,
                    world_direction=dir,
                )
        else:
            filepath, fshape = generate.generate_all_files(
                floorplan,
                True,
                world_direction=dir,
                world_scale=worldscale,
                world_position=worldpositionoffset + margin,
                world_rotation=worldrotationoffset,
            )

        # Append the generated file path to the list
        data_paths.append(filepath)
    
    return data_paths


def rotate_around_axis(axis, vec, degrees):
    """
    Rotates a vector around a specified axis by a given number of degrees.

    Parameters:
    - axis: The axis of rotation (e.g., [0, 0, 1] for rotation around Z-axis).
    - vec: The vector to rotate.
    - degrees: The number of degrees to rotate the vector.

    Returns:
    - The rotated vector.
    """
    rotation_radians = np.radians(degrees)  # Convert degrees to radians
    rotation_vector = rotation_radians * axis  # Calculate the rotation vector
    rotation = R.from_rotvec(rotation_vector)  # Create a rotation object
    return rotation.apply(vec)  # Apply the rotation to the vector


def angle_btw_2_points(point_a, point_b):
    """
    Calculates the angle between two points (in degrees).

    Parameters:
    - pointA: The first point (x, y).
    - pointB: The second point (x, y).

    Returns:
    - The angle in degrees between the two points.
    """
    # Calculate the change in Y coordinates
    change_in_y = point_b[1] - point_a[1]
    # Calculate the angle using atan2 and convert it to degrees
    return degrees(atan2(change_in_y, point_b[0] - point_a[0]))


def multiple_cylinder(
    floorplans,
    amount_per_level,
    radie,
    degree,
    world_position=np.array([0, 0, 0]),
    world_scale=np.array([1, 1, 1]),
):
    """
    Generates several new apartments arranged in a cylindrical shape.

    Parameters:
    - floorplans: A list of paths to floorplan images.
    - amount_per_level: The number of apartments per level in the cylinder.
    - radie: The radius of the cylinder.
    - degree: The angular span of the circle (in degrees, e.g., 360 for full circle).
    - world_direction: The direction of the world, if needed.
    - world_rotation: Rotation to be applied to each apartment.
    - margin: Margin to be added to each apartment’s position.
    - A list of paths to the generated data files.
    """
    data_paths = list()  # List to store generated file paths
    curr_index = 0  # Index to track apartments
    curr_level = 0  # Level of the current apartment
    degree_step = int(degree / amount_per_level)  # Step size for each apartment's angle
    start_pos = (world_position[0], world_position[1] + radie, world_position[2])  # Starting position for the first apartment

    # Loop through each floorplan to generate apartments in a cylindrical arrangement
    for floorplan in floorplans:

        if curr_index == amount_per_level:
            curr_level += 1  # Move to the next level
            curr_index = 0  # Reset the index

        # Calculate the position of the current apartment by rotating around the Z-axis
        curr_pos = rotate_around_axis(np.array([0, 0, 1]), start_pos, degree_step * curr_index)
        curr_pos = (int(curr_pos[0]), int(curr_pos[1]), int(curr_pos[2]))  # Round the coordinates

        # Set the rotation for the current apartment
        curr_rot = np.array([0, 0, int(degree_step * curr_index)])

        # Generate the files for the current floorplan at the calculated position and rotation
        filepath, _ = generate.generate_all_files(
            floorplan,
            True,
            world_position=np.array(
                [
                    curr_pos[0] + world_position[0],
                    curr_pos[1] + world_position[1],
                    curr_level + world_position[2],
                ]
            ),
            world_rotation=curr_rot,
            world_scale=world_scale,
        )

        # Add the generated file path to the list
        data_paths.append(filepath)

        curr_index += 1  # Move to the next apartment

    return data_paths
