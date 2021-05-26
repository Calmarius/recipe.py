#!/usr/bin/env python3

import os.path
import json
from enum import Enum
import pathlib

class RecipeStatus(Enum):
    UP_TO_DATE = 0
    FAILED_TO_MAKE = 1
    CHANGED = 2

def make_thing_inner(target, recipes, aux_data):
    if target in recipes:
        recipe = recipes[target]
        old_recipe = aux_data["recipes"][target] if target in aux_data["recipes"] else None
        needs_rebuild = False
        if not os.path.exists(target):
            print("Target {} doesn't exist therefore it needs to be built.".format(target))
            needs_rebuild = True
        if old_recipe is None or (old_recipe["deps"] != recipe["deps"]):
            print("Dependencies of {} has been changed, therefore it needs to be rebuilt regardless of dependency changes.".format(target))
            needs_rebuild = True
        print("Checking dependencies of {}...".format(target))
        for dependency in recipe["deps"]:
            res = make_thing_inner(dependency, recipes, aux_data)
            if res == RecipeStatus.FAILED_TO_MAKE:
                return RecipeStatus.FAILED_TO_MAKE
            if res == RecipeStatus.CHANGED:
                needs_rebuild = True

        if needs_rebuild:
            print("{} needs to be rebuilt".format(target))
            res = recipe["action"](target, recipe)
            if res == 0:
                return RecipeStatus.CHANGED
            else:
                print(">>> Building of {} failed with error code {}".format(target, res))
                return RecipeStatus.FAILED_TO_MAKE
        else:
            print("Dependencies of  {} are up to date, therefore up to date.".format(target))
            return RecipeStatus.UP_TO_DATE
    else:
        fileids = aux_data["fileids"]
        target_file = pathlib.Path(target)
        # It has no recipe just check if it's up to date.
        if target_file.exists():
            mtime = target_file.stat().st_mtime
            if target in fileids:
                # We have seen the file before
                aux_mtime = fileids[target]
                if mtime != aux_mtime:
                    # It's modification time changed. Therefore its changed.
                    aux_data["fileids"][target] = mtime
                    print("{} mtime has been changed (old: {}, new: {})".format(target, aux_mtime, mtime))
                    return RecipeStatus.CHANGED
                else:
                    # It's modification time not changed. Therefore it's up to date.
                    print("{} is up to date".format(target))
                    return RecipeStatus.UP_TO_DATE    
            else:
                # We haven't seen this file before
                aux_data["fileids"][target] = mtime
                print("{} is not seen before".format(target))
                return RecipeStatus.CHANGED

        else:
            # We need the file but it doesn't exists and doesn't exist bailing out.
            print(">>> No recipe to make {}".format(target))
            return RecipeStatus.FAILED_TO_MAKE

def cycle_check(target, recipes):
    seen = {}

    def cycle_check_inner(target, recipes, seen):
        if target in seen:
            # Already seen this indicates a cycle.
            print("Circular dependencies: {} is part of a circular dependency".format(target))
            return False
        seen[target] = True
        if target in recipes:
            recipe = recipes[target]
            for dependency in recipe["deps"]:
                if not cycle_check_inner(dependency, recipes, seen):
                    return False

        return True

    return cycle_check_inner(target, recipes, seen)


def make_thing(target, recipes, aux_file = "recipes.aux"):
    if not cycle_check(target, recipes):        
        return False

    if os.path.exists(aux_file):
        with open(aux_file)  as f:
            aux_data = json.load(f)
    else:
        aux_data = {
            "recipes":{},
            "fileids": {}
        }

    if make_thing_inner(target, recipes, aux_data) == RecipeStatus.FAILED_TO_MAKE:
        print("Failed to make {}".format(target))
        return False

    aux_data["recipes"] = recipes
    with open(aux_file, 'w') as f:
        json.dump(aux_data, f, default=lambda o: '<not serializable>')
    
    return True



