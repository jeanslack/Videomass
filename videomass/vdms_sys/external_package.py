# -*- coding: UTF-8 -*-
"""
Name: external_package.py
Porpose: finds and loads a module
Compatibility: Python3
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: June.19.2024
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
import sys
import importlib
import importlib.machinery
import importlib.util


def importer(pkg, path):
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
