#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Name: hatch_build.py
Porpose: Defines code that will be executed at various stages
         of the build process, see [tool.hatch.build.hooks.custom] on
         pyproject.toml file.
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Oct.12.2026
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

from pathlib import Path
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from babel.messages.pofile import read_po
from babel.messages.mofile import write_mo


class VideomassLanguageBuildHook(BuildHookInterface):
    """
    Compile the translation files from portable object (.po format)
    into the binary machine object (.mo format) using Babel's core APIs
    without depending on setuptools.
    """
    def initialize(self, version, build_data):
        """
        Compile catalog only if the target includes binary
        distribution (wheel). Source distribution (sdist)
        does not have to include MO files.
        """
        if self.target_name != "wheel":
            return

        localedir = Path("videomass/data/locale")
        if not localedir.exists():
            return

        for po_path in localedir.rglob("*.po"):
            mo_path = po_path.with_suffix(".mo")
            print(f'Compiling "{po_path}" to "{mo_path}"...')
            with open(po_path, 'r', encoding='utf-8') as po_file:
                catalog = read_po(po_file)

            with open(mo_path, 'wb') as mo_file:
                write_mo(mo_file, catalog)
