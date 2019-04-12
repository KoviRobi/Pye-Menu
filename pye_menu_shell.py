from pye_menu import PyeMenu
import configparser
import argparse
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango, PangoCairo

def main():
    parser = argparse.ArgumentParser()
    config = configparser.ConfigParser()
    arguments = ["Foo", "Bar", "Baz", "Quux", "What duck?"]
    for config_file in config_files():
        config.read(config_file)
        config.sections()
        break
    win = PyeMenu(*arguments)
    win.show_all()
    Gtk.main()

class Config():
    from configparser import ConfigParser
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

    def add_search_path(self, file):
        self.add_search_file(os.path.join(path, 'pye-menu.ini'))

    def add_search_file(self, file):
        if os.path.exists(file):
            self.files.append(file)

    def config_file_names(self):
        for file in self.files:
            yield file

    def config_files(self):
        config = ConfigParser()
        for file in self.config_file_names():
            config.read(file)

def config_files():
    xdg_config_home = os.getenv("XDG_CONFIG_HOME")
    if xdg_config_home != None:
        path = os.path.join(xdg_config_home, "pye_menu.ini")
        if os.path.isfile(path):
            yield path

    xdg_config_dirs = os.getenv("XDG_CONFIG_DIRS")
    xdg_config_dirs = xdg_config_dirs.split() if xdg_config_dirs != None else []
    for path in xdg_config_dirs:
        path = os.path.join(path, "pye_menu.ini")
        if os.path.isfile(path):
            yield path

if (__name__ == '__main__'):
    main()
else:
    print("This is not a library, but a command-line program for the pye_menu")
