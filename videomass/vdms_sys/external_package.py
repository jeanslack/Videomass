# -*- coding: UTF-8 -*-
"""
Name: external_package.py
Purpose: finds and loads a module
Compatibility: Python >= 3.11
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Oct.31.2026
Code checker: flake8, pylint

This file is part of Videomass.

   Videomass is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   Videomass is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with Videomass.  If not, see <http://www.gnu.org/licenses/>.
"""

import importlib
import importlib.machinery
import importlib.util
import os
import sys


def importer_package_dir(pkg, path):
    """
    An object that both finds and loads a module;
    both a finder and loader object.
    """
    spec = importlib.machinery.PathFinder().find_spec(pkg, [path])
    try:
        mod = importlib.util.module_from_spec(spec)
    except AttributeError as err:
        return err
    sys.modules[pkg] = mod
    spec.loader.exec_module(mod)
    sys.modules[pkg] = importlib.import_module(pkg)
    return None


def importer_init_file(path: str, test: list[str] | None = None):
    """
    Given a pathname to a python package, import relative
    `__init__` file.
    This function implicitly handles some exceptions such as
    `FileNotFoundError` and `ModuleNotFoundError`. Optionally
    you can test a list of one or more submodules using the `test`
    argument.
    Example: from external_package import importer_init_file
             submod = ['compile_catalog','extract_messages',
                       'update_catalog','init_catalog']
             importer_init_file('/lib/python3.13/site-packages/babel/',
             submod)
    """
    pkgname = os.path.basename(path)
    initpath = os.path.join(path, "__init__.py")

    if not os.path.exists(initpath) or not os.path.isfile(initpath):
        return f"No such file or directory: «{initpath}»"

    spec = importlib.util.spec_from_file_location(pkgname, initpath)
    newmodule = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = newmodule
    spec.loader.exec_module(newmodule)

    if test:
        foundsub = []
        for mod in test:
            if not sys.modules.get(mod, None):
                foundsub.append(mod)
                # return f'Module not found: \'{mod}\''
        if foundsub:
            return f"Module not found: {', '.join(foundsub)}"
    return None
