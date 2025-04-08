import json
import os
from shutil import which
import shutil
import cv2
import platform
from sys import platform as pf
import numpy as np

from . import const
from . import image
from . import config

"""
IO
This file contains functions for handling files, reading and saving floorplan data, 
and ensuring the necessary software (like Blender) is correctly installed.
These functions are integral to automating the workflow for generating Blender-ready 3D models from floorplans.

"""

def find_reuseable_data(image_path, path):
    """
    Check if the floorplan data for a given image already exists at the specified path.
    If it does, returns the path to the existing data and its shape. Otherwise, returns None.

    @param image_path: Path to the image for which data might already exist.
    @param path: Directory path to search for the existing data.
    @return: Tuple (path to existing data, shape) if found, otherwise (None, None).
    """
    for _, dirs, _ in os.walk(path):
        for dir in dirs:
            try:
                with open(path + dir + const.TRANSFORM_PATH) as f:
                    data = f.read()
                js = json.loads(data)
                if image_path == js[const.STR_IMAGE_PATH]:
                    return js[const.STR_ORIGIN_PATH], js[const.STR_SHAPE]
            except IOError:
                continue
    return None, None


def find_files(filename, search_path):
    """
    Find a specific file in the directory and its subdirectories.

    @param filename: The name of the file to search for.
    @param search_path: The root directory to start searching from.
    @return: Full path to the file if found, else None.
    """
    for root, _, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None


def blender_installed():
    """
    Check if Blender is installed on the system.
    Returns the path to the Blender executable if found, otherwise returns None.

    @return: Path to the Blender executable or None if not installed.
    """
    if pf == "linux" or pf == "linux2":
        return find_files("blender", "/")  # For Linux-based systems
    elif pf == "darwin":
        return find_files("blender", "/")  # For macOS (need testing)
    elif pf == "win32":
        return find_files("blender.exe", "C:\\")  # For Windows


def get_blender_os_path():
    """
    Get the default Blender installation path based on the current operating system.
    
    @return: Default path for Blender installation on the current OS.
    """
    _platform = platform.system()
    if _platform.lower() in ["linux", "linux2", "ubuntu"]:
        return const.LINUX_DEFAULT_BLENDER_INSTALL_PATH
    elif _platform.lower() == "darwin":
        return const.MAC_DEFAULT_BLENDER_INSTALL_PATH
    elif "win" in _platform.lower():
        return const.WIN_DEFAULT_BLENDER_INSTALL_PATH


def read_image(path, floorplan=None):
    """
    Read the image from the given path, apply resizing and noise reduction if needed.
    Returns the processed image, grayscale version, and scale factor.
    
    @param path: Path to the image file.
    @param floorplan: Optional floorplan object containing settings like noise removal and rescaling.
    @return: Processed image, grayscale image, and the scale factor used.
    """
    # Read the image using OpenCV
    img = cv2.imread(path)
    if img is None:
        print(f"ERROR: Image {path} could not be read by OpenCV library.")
        raise IOError

    scale_factor = 1
    if floorplan is not None:
        # Apply noise removal if needed
        if floorplan.remove_noise:
            img = image.denoising(img)
        # Rescale the image if required
        if floorplan.rescale_image:
            calibrations = config.read_calibration(floorplan)
            floorplan.wall_size_calibration = calibrations  # Store for debugging
            scale_factor = image.detect_wall_rescale(float(calibrations), img)
            if scale_factor is None:
                print(
                    "WARNING: Auto rescale failed due to non-good walls found in image."
                    + "If rescale is still needed, please rescale manually."
                )
                scale_factor = 1
            else:
                img = image.cv2_rescale_image(img, scale_factor)

    return img, cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), scale_factor


def readlines_file(path):
    """
    Read all lines from a text file and return them as a list.

    @param path: The path to the text file.
    @return: List of lines read from the file.
    """
    with open(path, "r") as f:
        return f.readlines()


def ndarray_json_dumps(obj):
    """
    Convert numpy arrays to a format that can be serialized into JSON.
    
    @param obj: The object to serialize, typically a numpy array.
    @return: The JSON-serializable version of the object.
    """
    if type(obj).__module__ == np.__name__:
        if isinstance(obj, np.ndarray):
            return obj.tolist()  # Convert numpy array to a regular list
        else:
            return obj.item()  # Convert single-value numpy objects
    raise TypeError("Unknown type:", type(obj))


def save_to_file(file_path, data, show=True):
    """
    Save the data to a JSON file at the specified file path.
    
    @param file_path: Path to save the data.
    @param data: Data to write to the file.
    @param show: Whether to print a success message.
    """
    with open(file_path + const.SAVE_DATA_FORMAT, "w") as f:
        try:
            f.write(json.dumps(data))
        except TypeError:
            f.write(json.dumps(data, default=ndarray_json_dumps))  # Handle numpy arrays

    if show:
        print("Created file : " + file_path + const.SAVE_DATA_FORMAT)


def read_from_file(file_path):
    """
    Read data from a JSON file at the specified path.

    @param file_path: Path to the file to read from.
    @return: The data read from the file.
    """
    with open(file_path + const.SAVE_DATA_FORMAT, "r") as f:
        return json.loads(f.read())


def clean_data_folder(folder):
    """
    Delete all files and subdirectories in the specified folder to clean up old data.

    @param folder: Path to the folder to clean.
    """
    for root, dirs, files in os.walk(folder):
        for f in files:
            os.unlink(os.path.join(root, f))  # Delete files
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))  # Delete subdirectories


def create_new_floorplan_path(path):
    """
    Create a new folder for floorplan data, ensuring a unique folder name.
    It checks for existing directories and creates the next available one.

    @param path: The base path to create the new folder in.
    @return: The path to the newly created directory.
    """
    res = 0
    for _, dirs, _ in os.walk(path):
        for _ in dirs:
            try:
                name_not_found = True
                while name_not_found:
                    if not os.path.exists(path + str(res) + "/"):
                        break
                    res += 1
            except Exception:
                continue

    res = path + str(res) + "/"
    if not os.path.exists(res):
        os.makedirs(res)  # Create the new directory
    return res


def get_current_path():
    """
    Get the current working directory of the program.

    @return: The path to the current working directory.
    """
    return os.path.dirname(os.path.realpath(__file__))


def find_program_path(name):
    """
    Find the installation path of a program by its name using the system's `which` command.

    @param name: The name of the program (e.g., "blender").
    @return: The path to the program if found, otherwise None.
    """
    return which(name)


def get_next_target_base_name(target_base, target_path):
    """
    Generate the next available target name by checking if a file with the same base name exists.
    If it exists, it increments the name with a number (e.g., target_base1, target_base2, etc.).

    @param target_base: The base name of the target file.
    @param target_path: The directory where the file will be saved.
    @return: The next available target base name.
    """
    fid = 0
    if os.path.isfile("." + target_path):
        for file in os.listdir("." + const.TARGET_PATH):
            filename = os.fsdecode(file)
            if filename.endswith(const.BASE_FORMAT):
                fid += 1
        target_base += str(fid)  # Increment the target base name with the next number

    return target_base
