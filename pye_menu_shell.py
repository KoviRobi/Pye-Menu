from pye_menu import PyeMenu
import configparser
import argparse
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango, PangoCairo

def main():
    arguments = Arguments().parse_args()
    arguments_dict = {k:v for k,v in vars(arguments).items() if v is not None}
    config = Config().config_files()
    menuitems = arguments.items
    options = {}
    profile = arguments.profile
    for key, ty in [("width", int), ("height", int), ("rotate", int),
                ("cancel-radius", int), ("accept-radius", int), ("alpha", str),
                ("fg", str), ("bg", str), ("hi-fg", str), ("hi-bg", str),
                ("cancel", str), ("hi-cancel", str), ("accept", str)]:
        if config is not None and profile in config and key in config[profile]:
            options[key] = ty(config[profile][key])
        if key in arguments_dict:
            options[key] = ty(arguments_dict[key])
    win = PyeMenu(*menuitems, **options)
    win.show_all()
    Gtk.main()

class Config():
    def __init__(self):
        self.files = []
        self.add_env_search_path("XDG_CONFIG_HOME")
        self.add_env_search_path("HOME", ".config")
        self.add_env_search_paths("XDG_CONFIG_DIRS")

    def add_env_search_path(self, env_var, *path):
        if env_var in os.environ:
            self.add_search_path(os.path.join(os.getenv(env_var), *path))

    def add_env_search_paths(self, env_var, separator=':'):
        if env_var in os.environ:
            for path in os.getenv(env_var).split(':'):
                self.add_env_search_path(path)

    def add_search_path(self, path):
        self.add_search_file(os.path.join(path, 'pye-menu.ini'))

    def add_search_file(self, file):
        if os.path.exists(file):
            self.files.append(file)

    def config_file_names(self):
        for file in self.files:
            yield file

    def config_files(self):
        from configparser import ConfigParser
        config = ConfigParser()
        for file in self.config_file_names():
            config.read(file)
            return config

class Arguments():
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Uses a pie-menu to select from a list of options.")
        parser.add_argument("items", metavar="menu-items", type=str, nargs="+")
        parser.add_argument("--width", help="Width of the pie menu window")
        parser.add_argument("--height", help="Height of the pie menu window")
        parser.add_argument("--rotate", help="Rotation, in degrees, of the first item. Default of 0 means first item is to the right.")
        parser.add_argument("--radius", help="Radius of the selection circle.")
        parser.add_argument("--cancel-radius", help="Radius of the central no-selection circle. Should be less than radius.")
        parser.add_argument("--accept-radius", help="Radius of the use current-selection circle, alternative to clicking on a pie-item. Should be greater than radius.")
        parser.add_argument("--alpha", help="Alpha of the window. Default is #ffffff00 (last two hex digits are the opacity.")
        parser.add_argument("--fg", help="Unselected foreground colour.")
        parser.add_argument("--bg", help="Unselected background colour.")
        parser.add_argument("--border", help="Menu-item order colour.")
        parser.add_argument("--hi-fg", help="Selected foreground colour.")
        parser.add_argument("--hi-bg", help="Selected background colour.")
        parser.add_argument("--cancel", help="Unselected central null option colour.")
        parser.add_argument("--hi-cancel", help="Selected central null option colour.")
        parser.add_argument("--accept", help="Outer accept circle colour.")
        parser.add_argument("--profile", default="DEFAULT", help="Section in the INI file to use.")
        self.parser = parser

    def parse_args(self):
        return self.parser.parse_args()

if (__name__ == '__main__'):
    main()
else:
    print("This is not a library, but a command-line program for the pye_menu")
