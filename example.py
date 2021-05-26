#!/usr/bin/env python3

"Example usage for the recipe.py"

import subprocess
import sys
import os

import recipe

OPTIONS = ["-Wall", "-Wextra", "-g"]


def build_c_file(_, the_recipe):
    "Builds a single C file with default options"

    c_file = the_recipe["deps"][0]
    command = ["gcc", c_file, "-c"] + OPTIONS
    print(command)
    res = subprocess.run(command, check=False)
    return res.returncode


def link_objects(target, the_recipe):
    "Links object in the recipe into a target"

    objects = the_recipe["deps"]
    command = ["gcc"] + objects + ["-o", target]
    print(command)
    res = subprocess.run(command, check=False)
    return res.returncode


def main():
    "Entry point"

    recipes = {
        "main.o": {
            "deps": ["main.c"],
            "action": build_c_file
        },
        "b.o": {
            "deps": ["b.c"],
            "action": build_c_file
        },
        "c.o": {
            "deps": ["c.c"],
            "action": build_c_file
        },
        "d.o": {
            "deps": ["d.c"],
            "action": build_c_file
        },
        "hw": {
            "deps": ["main.o", "b.o", "c.o", "d.o"],
            "action": link_objects
        }
    }

    if len(sys.argv) >= 2 and sys.argv[1] == "clean":
        for target in recipes:
            try:
                os.remove(target)
            except OSError:
                pass
    else:
        recipe.make_thing("hw", recipes)


main()
