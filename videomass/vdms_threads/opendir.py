# -*- coding: UTF-8 -*-
"""
Name: opendir.py
Porpose: open file browser on given pathname
Compatibility: Python3 (Unix, Windows)
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.22.2022
Code checker:
    flake8: --ignore F821, W504
    pylint: --ignore E0602, E1101

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
import subprocess
import os


def browse(ostype, pathname):
    """
    open file in a specific location (OS independent)

    """
    if ostype == 'Windows':
        try:
            os.startfile(os.path.realpath(pathname))

        except FileNotFoundError as pathnotfound:
            return f'{pathnotfound}'

        except Exception as anyerr:
            return f'{anyerr}'

        return None

    if ostype == 'Darwin':
        cmd = ['open', pathname]

    else:  # xdg-open *should* be supported by recent Gnome, KDE, Xfce
        cmd = ['xdg-open', pathname]

    try:
        proc = subprocess.run(cmd, check=True, shell=False)
    except FileNotFoundError as err:
        return err

    if proc.returncode:
        return "EXIT: {proc.returncode}\nERROR: {proc.stderr}"

    return None
