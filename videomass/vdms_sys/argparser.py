# -*- coding: UTF-8 -*-
"""
Name: argparser.py
Porpose: Videomass Command line arguments
Compatibility: Python3
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: October.03.2021
Code checker: pycodestyle, flake8, pylint .

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
import os
import sys
from shutil import which
import argparse
from videomass.vdms_sys.msg_info import current_release
try:
    import wx
    MSGWX = f"{wx.version()})"
except ModuleNotFoundError as errwx:
    MSGWX = f"not installed! ({errwx})"


def args():
    """
    Parser of the users inputs (positional/optional arguments)

    USE:
        videomass -h
    """
    parser = argparse.ArgumentParser(description=('GUI for FFmpeg and '
                                                  'youtube-dl/yt-dlp'),)
    parser.add_argument('-v', '--version',
                        help="show the current version and exit",
                        action="store_true",
                        )
    parser.add_argument('-c', '--check',
                        help=('List of executables used by Videomass '
                              'found in your operating system'),
                        action="store_true",
                        )

    argmts = parser.parse_args()

    if argmts.check:
        deps = {'Required': {'ffmpeg': None, 'ffprobe': None, 'ffplay': None},
                'Recommended': {'youtube-dl': None, 'yt-dlp': None},
                'Optional': {'atomicparsley': None}
                }
        for key, val in deps.items():
            if key in ('Required', 'Recommended', 'Optional'):
                for exe in val:
                    val[exe] = which(exe, mode=os.F_OK | os.X_OK, path=None)
        print('\nList of executables used by Videomass:')
        for key, val in deps.items():
            for exe, path in val.items():
                if path:
                    print(f"\t[{key}] '{exe}' ...Ok")
                    print(f"\tpath: '{path}'\n")
                else:
                    print(f"\t[{key}] '{exe}' ...Not Installed")
                    print(f"\tpath: {path}\n")

    elif argmts.version:
        crel = current_release()
        print(f'{crel[0]}: {crel[2]} ({crel[3]})')
        print(f'Python: {sys.version}')
        print(f'wxPython: {MSGWX}')

    else:
        print("Type 'videomass -h' for help.")
