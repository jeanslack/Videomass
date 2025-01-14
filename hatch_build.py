#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Name: hatch_build.py
Porpose: Defines code that will be executed at various stages
         of the build process, see [tool.hatch.build.hooks.custom] on
         pyproject.toml file.
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: July.22.2024
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

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from babel.messages.frontend import compile_catalog


class VideomassLanguageBuildHook(BuildHookInterface):
    """
    Compile the translation files from their PO-format into
    their binary representating MO-format using python `babel`
    pluggin.
    """
    def initialize(self, version, build_data):
        """
        Compile catalog only if the target includes binary
        distribution (wheel). Source distribution (sdist)
        does not have to include MO files.
        """
        if self.target_name == "wheel":
            cmd = compile_catalog()
            cmd.directory = "videomass/data/locale/"
            cmd.domain = "videomass"
            cmd.statistics = True
            cmd.finalize_options()
            cmd.run()
