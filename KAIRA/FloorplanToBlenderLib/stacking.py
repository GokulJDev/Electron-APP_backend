from . import IO
from . import execution
from . import const
from . import floorplan
from . import transform

import numpy as np

"""
Stacking
This file contains functions for handling stacking file parsing and creating larger stacking.
These functions help in arranging multiple floorplans into a single scene, automating the process of stacking and placing them.
FloorplanToBlender3d
Copyright (C) 2022 Daniel Westberg
"""

def parse_stacking_file(path):
    """
    Parse strictly formatted stacking files.
    These are used to easily place many floorplans in one scene.
    
    @param path: The path to the stacking file to be parsed.
    @return: A list of worlds, each containing a set of commands or floorplans.
    """
    array_of_commands = IO.readlines_file(path)

    world = []
    worlds = []

    print("Building stack from file " + path)

    for index, line in enumerate(array_of_commands):
        process_line(line, index, world, worlds)

    worlds.extend(world)
    return worlds


def process_line(line, index, world, worlds):
    args = line.split(" ")
    command = args[0]

    # Skip commented or empty lines
    if command[0] in ["#", "\n", "", " "]:
        return

    try:
        args.remove("\n")
    except Exception:
        pass

    args = clean_arguments(args)

    argstring = build_argstring(args)

    print(">Line", index, "Command:", command + "(" + argstring + ")")

    process_command(command, argstring, world, worlds)


def clean_arguments(args):
    new_args = []
    for cmd in args:
        if cmd == '"_"':
            new_args.append("None")
        else:
            new_args.append(cmd)
    return new_args


def build_argstring(args):
    argstring = ""
    for index, arg in enumerate(args[1:]):
        if index == len(args[1:]) - 1:
            argstring += arg
        else:
            argstring += arg + ","
    return argstring


def process_command(command, argstring, world, worlds):
    if command == "separate":
        worlds.append(world)
        world = []
    elif command == "CLEAR":
        eval(command.lower() + "(" + argstring + ")")
    else:
        world.extend(eval(command.lower() + "(" + argstring + ")"))


def clear():
    """
    Clean up by removing data files in the base path.
    """
    IO.clean_data_folder(const.BASE_PATH)


def separate():
    """
    Placeholder function for SEPARATE command in the stacking file.
    Currently does nothing, but can be customized later.
    """
    pass


def file(stacking_file_path):
    """
    Load a stacking file and return the parsed worlds and commands.

    @param stacking_file_path: The path to the stacking file to be processed.
    @return: The list of worlds parsed from the stacking file.
    """
    return parse_stacking_file(stacking_file_path)


def add(
    config=None,
    image_path=None,
    amount=1,
    mode="x",
    margin=np.array([0, 0, 0]),
    worldpositionoffset=np.array([0, 0, 0]),
    worldrotationoffset=np.array([0, 0, 0]),
    worldscale=np.array([1, 1, 1]),
    amount_per_level=None,
    radie=None,
    degree=None,
):
    """
    Add a floorplan to the configuration and set its parameters such as amount, position, rotation, etc.

    @param config: The configuration file to use. If None, defaults to IMAGE_DEFAULT_CONFIG_FILE_NAME.
    @param image_path: Path to the image to associate with the floorplan (optional).
    @param amount: Number of floorplans to add.
    @param mode: The stacking mode (e.g., "x", "y", "z", or "cylinder").
    @param margin: Margin between floorplans.
    @param worldpositionoffset: Offset for the position of the floorplan in the world.
    @param worldrotationoffset: Rotation offset for the floorplan in the world.
    @param worldscale: Scaling factor for the floorplan.
    @param amount_per_level: The number of floorplans per level for cylindrical stacking (optional).
    @param radie: Radius for cylindrical stacking (optional).
    @param degree: The degree or angular spread for cylindrical stacking (optional).
    @return: The execution result of adding the floorplans in the specified mode.
    """
    conf = config
    if config is None:
        conf = const.IMAGE_DEFAULT_CONFIG_FILE_NAME

    if amount is None:
        amount = 1

    # Create the specified number of floorplans
    floorplans = [floorplan.new_floorplan(conf) for _ in range(amount)]

    # Update image paths if provided
    if image_path is not None:
        for f in floorplans:
            f.image_path = image_path

    # Determine direction based on mode
    direction = 1
    if mode is None:
        mode = "x"
    if mode[0] == "-":
        direction = -1
        mode = mode[1]

    # Handle the stacking modes
    if mode == "cylinder":
        return execution.multiple_cylinder(
            floorplans,
            amount_per_level,
            radie,
            degree,
            world_direction=direction,
            world_position=transform.list_to_nparray(worldpositionoffset, np.array([0, 0, 0])),
            world_rotation=transform.list_to_nparray(worldrotationoffset, np.array([0, 0, 0])),
            world_scale=transform.list_to_nparray(worldscale),
            margin=transform.list_to_nparray(margin, np.array([0, 0, 0])),
        )
    else:
        return execution.multiple_axis(
            floorplans,
            mode,
            direction,
            transform.list_to_nparray(margin, np.array([0, 0, 0])),
            transform.list_to_nparray(worldpositionoffset, np.array([0, 0, 0])),
            transform.list_to_nparray(worldrotationoffset, np.array([0, 0, 0])),
            transform.list_to_nparray(worldscale),
        )
