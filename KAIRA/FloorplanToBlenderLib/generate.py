from . import IO
from . import const
from . import transform
import numpy as np

from FloorplanToBlenderLib.generator import Door, Floor, Room, Wall, Window

"""
Generate
This file contains code for generating data files used when creating a Blender project.
It temporarily stores calculated data and transfers data to the Blender script.

"""

def generate_all_files(
    floorplan,
    info,
    world_direction=None,
    world_scale=np.array([1, 1, 1]),
    world_position=np.array([0, 0, 0]),
    world_rotation=np.array([0, 0, 0]),
):
    """
    Generate all data files required for the floorplan.
    
    Parameters:
    - floorplan: The floorplan object containing image, scale, position, rotation, etc.
    - info: Boolean flag to control whether information should be printed.
    - world_direction: Direction of building (positive/negative direction).
    - world_scale: The scale applied to the floorplan.
    - world_position: The position where the floorplan is placed.
    - world_rotation: The rotation of the floorplan.

    Returns:
    - path: The generated file path for the floorplan data.
    - shape: The shape of the floorplan after transformations.
    """
    if world_direction is None:
        world_direction = 1  # Default direction if not provided

    scale = apply_world_scale(floorplan, world_scale)

    if info:
        print_info(floorplan, world_position, world_rotation, scale)

    path, origin_path, shape = get_paths_and_shape(floorplan)

    if origin_path is None:
        origin_path = path
        shape = process_floorplan_components(floorplan, path, scale, info)

    generate_transform_file(
        floorplan.image_path,
        path,
        info,
        floorplan.position,
        world_position,
        floorplan.rotation,
        world_rotation,
        scale,
        shape,
        path,
        origin_path,
    )

    shape = update_shape_with_world_position(floorplan, shape, world_position, world_direction)

    return path, shape


def apply_world_scale(floorplan, world_scale):
    return [
        floorplan.scale[0] * world_scale[0],
        floorplan.scale[1] * world_scale[1],
        floorplan.scale[2] * world_scale[2],
    ]


def print_info(floorplan, world_position, world_rotation, scale):
    print(
        " ----- Generate ",
        floorplan.image_path,
        " at pos ",
        transform.list_to_nparray(floorplan.position) + transform.list_to_nparray(world_position),
        " rot ",
        transform.list_to_nparray(floorplan.rotation) + transform.list_to_nparray(world_rotation),
        " scale ",
        scale,
        " -----",
    )


def get_paths_and_shape(floorplan):
    path = IO.create_new_floorplan_path(const.BASE_PATH)
    origin_path, shape = IO.find_reuseable_data(floorplan.image_path, const.BASE_PATH)
    return path, origin_path, shape


def process_floorplan_components(floorplan, path, scale, info):
    _, gray, scale_factor = IO.read_image(floorplan.image_path, floorplan)
    shape = None

    if floorplan.floors:
        shape = Floor(gray, path, scale, info).shape

    if floorplan.walls:
        shape = process_component(Wall, gray, path, scale, info, shape)

    if floorplan.rooms:
        shape = process_component(Room, gray, path, scale, info, shape)

    if floorplan.windows:
        Window(gray, path, floorplan.image_path, scale_factor, scale, info)

    if floorplan.doors:
        Door(gray, path, floorplan.image_path, scale_factor, scale, info)

    return shape


def process_component(component_class, gray, path, scale, info, shape):
    new_shape = component_class(gray, path, scale, info).shape
    if shape is not None:
        shape = validate_shape(shape, new_shape)
    else:
        shape = new_shape
    return shape


def update_shape_with_world_position(floorplan, shape, world_position, world_direction):
    if floorplan.position is not None:
        shape = [
            world_direction * shape[0] + floorplan.position[0] + world_position[0],
            world_direction * shape[1] + floorplan.position[1] + world_position[1],
            world_direction * shape[2] + floorplan.position[2] + world_position[2],
        ]

    if shape is None:
        shape = [0, 0, 0]

    return shape


def validate_shape(old_shape, new_shape):
    """
    Validates and calculates the total shape by comparing the old and new shapes.

    Parameters:
    - old_shape: The previous shape of the object.
    - new_shape: The new shape to compare with.

    Returns:
    - shape: The total shape after comparing the old and new shapes.
    """
    shape = [0, 0, 0]
    shape[0] = max(old_shape[0], new_shape[0])
    shape[1] = max(old_shape[1], new_shape[1])
    shape[2] = max(old_shape[2], new_shape[2])
    return shape


def generate_transform_file(
    img_path,
    path,
    info,
    position,
    world_position,
    rotation,
    world_rotation,
    scale,
    shape,
    data_path,
    origin_path,
):
    """
    Generates a transformation file containing information about position, rotation, scale, and shape.

    Parameters:
    - img_path: The path to the image of the floorplan.
    - path: The path where the data should be saved.
    - info: Boolean flag to print information.
    - position: The local position of the floorplan.
    - world_position: The global position of the floorplan.
    - rotation: The rotation of the floorplan.
    - world_rotation: The global rotation applied to the floorplan.
    - scale: The scale of the floorplan.
    - shape: The shape of the floorplan.
    - data_path: The path where the generated data is stored.
    - origin_path: The original data path.

    Returns:
    - transform: The transformation dictionary containing position, rotation, scale, shape, etc.
    """
    # Create a dictionary for the transformation
    transform = {}
    
    # Position: Default to [0, 0, 0] if position is None
    if position is None:
        transform[const.STR_POSITION] = np.array([0, 0, 0])
    else:
        transform[const.STR_POSITION] = position + world_position

    # Scale: Default to [1, 1, 1] if scale is None
    if scale is None:
        transform["scale"] = np.array([1, 1, 1])
    else:
        transform["scale"] = scale

    # Rotation: Default to [0, 0, 0] if rotation is None
    if rotation is None:
        transform[const.STR_ROTATION] = np.array([0, 0, 0])
    else:
        transform[const.STR_ROTATION] = rotation + world_rotation

    # Shape: Default to [0, 0, 0] if shape is None
    if shape is None:
        transform[const.STR_SHAPE] = np.array([0, 0, 0])
    else:
        transform[const.STR_SHAPE] = shape

    # Store additional information such as image path, origin path, and data path
    transform[const.STR_IMAGE_PATH] = img_path
    transform[const.STR_ORIGIN_PATH] = origin_path
    transform[const.STR_DATA_PATH] = data_path

    # Save the transform data to a file
    IO.save_to_file(path + "transform", transform, info)

    return transform
