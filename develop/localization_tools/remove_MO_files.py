# -*- coding: UTF-8 -*-
"""
Name: remove_PO_files.py
Purpose: Removes all "*.mo" file from "locale" directory.
Platform: Gnu-Linux, MacOs, MS-Windows
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.02.2026

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
import glob
import os

while True:
    quest = input('\nDo you want to permanently remove all machine '
                  'object files (".mo" format) in the "locale" '
                  'directory? [y/Y-n/N] ')

    if quest.strip() in ('Y', 'y', 'n', 'N'):
        break
    print(f"\nInvalid option '{quest}'")
    continue

ext = '.mo'
mofiles = glob.glob(f'videomass/data/locale/**/*{ext}', recursive=True)

if mofiles:
    for mf in mofiles:
        if os.path.exists(mf) and os.path.isfile(mf):
            print(f"...Deleting >> '{mf}'")
            os.remove(mf)
        else:
            print(f"File not found: \"{mf}\"")
else:
    print(f"\nNo \"{ext}\" file found: No changes made.\n")
