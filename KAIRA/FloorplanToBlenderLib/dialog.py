from pyfiglet import Figlet

"""
Dialog
This file contains code for handling dialog and can be seen as a gui solution.

"""


def figlet(text="Floorplan to Blender3d", font="slant"):
    f = Figlet(font=font)
    print(f.renderText(text))


def init():
    print("----- CREATE BLENDER PROJECT FROM FLOORPLAN WITH DIALOG -----")
    print("Welcome to this program. Please answer the questions below to progress.")
    print("Remember that you can change data more efficiently in the config file.")
    print("")


def question(text, default):
    """
    @Param text, question string
    @Param default, possible values
    @Return input
    """
    return input(text + " [default = " + default + "]: ")


def end_copyright():
    
    print("")
