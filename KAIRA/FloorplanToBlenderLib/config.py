import configparser
import os
import cv2
import json

from . import IO
from . import const
from . import calculate

"""
Config
This file contains functions for handling config files.

"""
'''
# TODO: settings for coloring all objects
# TODO: add config security check, before startup!
# TODO: safe read, use this function instead of repeating code everywhere!
# TODO: add blender path addition to system.ini
'''

def read_calibration(floorplan):
    """
    Read all calibrations
    """
    if floorplan.wall_size_calibration == 0:
        floorplan.wall_size_calibration = create_image_scale_calibration(floorplan)
    return floorplan.wall_size_calibration


def create_image_scale_calibration(floorplan):
    """
    Create and save image size calibrations
    """
    calibration_img = cv2.imread(floorplan.calibration_image_path)
    return calculate.wall_width_average(calibration_img)


def generate_file():
    """
    Generate new config file, if not exist
    """
    # Create System Settings
    conf = configparser.ConfigParser()
    conf["SYSTEM"] = {
        const.STR_OVERWRITE_DATA: const.DEFAULT_OVERWRITE_DATA,  
        const.STR_BLENDER_INSTALL_PATH: IO.get_blender_os_path(),
        const.STR_OUT_FORMAT: json.dumps(const.DEFAULT_OUT_FORMAT),
    }

    os.makedirs(os.path.dirname(const.SYSTEM_CONFIG_FILE_NAME), exist_ok=True)
    with open(const.SYSTEM_CONFIG_FILE_NAME, "w") as configfile:
        conf.write(configfile)

    # Create Default floorplan Settings
    conf = configparser.ConfigParser()
    conf["IMAGE"] = {
        const.STR_IMAGE_PATH: json.dumps(const.DEFAULT_IMAGE_PATH),
        "COLOR": json.dumps([0, 0, 0]),
    }

    conf["TRANSFORM"] = {
        "position": json.dumps([0, 0, 0]),
        "rotation": json.dumps([0, 0, 90]),
        "scale": json.dumps([1, 1, 1]),
        "margin": json.dumps([0, 0, 0]),
    }

    conf[const.FEATURES] = {
        const.STR_FLOORS: json.dumps(const.DEFAULT_FEATURES),
        const.STR_ROOMS: json.dumps(const.DEFAULT_FEATURES),
        const.STR_WALLS: json.dumps(const.DEFAULT_FEATURES),
        const.STR_DOORS: json.dumps(const.DEFAULT_FEATURES),
        const.STR_WINDOWS: json.dumps(const.DEFAULT_FEATURES),
    }

    conf[const.SETTINGS] = {
        const.STR_REMOVE_NOISE: json.dumps(const.DEFAULT_REMOVE_NOISE),
        const.STR_RESCALE_IMAGE: json.dumps(const.DEFAULT_RESCALE_IMAGE),
    }

    conf[const.WALL_CALIBRATION] = {
        const.STR_CALIBRATION_IMAGE_PATH: json.dumps(
            const.DEFAULT_CALIBRATION_IMAGE_PATH
        ),
        const.STR_WALL_SIZE_CALIBRATION: json.dumps(
            const.DEFAULT_WALL_SIZE_CALIBRATION
        ),
    }

    with open(const.IMAGE_DEFAULT_CONFIG_FILE_NAME, "w") as configfile:
        conf.write(configfile)


def show(conf):
    """
    Visualize all config settings
    """
    for section in conf.sections():
        print(f"[{section}]")
        for key, value in conf.items(section):
            print(f"{key}: {value}")
        print()


def update(path, key, config):
    """
    Update a config category with a config object
    """
    conf = get_all(path)
    conf[key] = config
    with open(path, "w") as configfile:
        conf.write(configfile)


def file_exist(name):
    """
    Check if file exists
    @Param name
    @Return boolean
    """
    return os.path.isfile(name)


def get_all(path):
    """
    Read and return all values from the config
    @Return default values
    """
    return get(path)


def get(config_path, *args):
    """
    Read and return specific values from the config
    @Return default values
    """
    conf = configparser.ConfigParser()

    if not file_exist(config_path):
        generate_file()
    
    conf.read(config_path)

    for key in args:
        conf = conf[key]

    return conf


def get_default_image_path():
    """
    Get the default image path from the config
    """
    return get(const.IMAGE_DEFAULT_CONFIG_FILE_NAME, "IMAGE", const.STR_IMAGE_PATH)


def get_default_blender_installation_path():
    """
    Get the default Blender installation path from the config
    """
    return get(const.SYSTEM_CONFIG_FILE_NAME, "SYSTEM", const.STR_BLENDER_INSTALL_PATH)
