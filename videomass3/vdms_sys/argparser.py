# -*- coding: UTF-8 -*-
"""
Name: argparser.py
Porpose: Check for command line arguments before starting
Compatibility: Python3
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: September.11.2020
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
import os
from shutil import which
import argparse
from videomass3.vdms_sys.msg_info import current_release


def args():
    """
    Parser of the users inputs (positional/optional arguments)

    USE:
        videomass -h
    """
    parser = argparse.ArgumentParser(description=('GUI for FFmpeg and '
                                                  'youtube-dl'),)
    parser.add_argument('-v', '--version',
                        help="show the current version and exit",
                        action="store_true",
                        )
    parser.add_argument('-c', '--check',
                        help=('List of executables used by Videomass '
                              'found on the system'),
                        action="store_true",
                        )

    argmts = parser.parse_args()

    if argmts.check:
        listing = ['ffmpeg',
                   'ffprobe',
                   'ffplay',
                   'youtube-dl',
                   'atomicparsley'
                   ]
        print('List of executables used by Videomass:')
        for required in listing:
            if required == 'atomicparsley':
                opt = '[Optional]'
            else:
                opt = '[Required]'
            if which(required, mode=os.F_OK | os.X_OK, path=None):
                print("\t%s '%s' ..Ok" % (opt, required))
            else:
                print("\t%s '%s' ..Not Installed" % (opt, required))

    elif argmts.version:
        crel = current_release()
        print('%s version %s released on %s' % (crel[0], crel[2], crel[3]))

    else:
        print("Type 'videomass -h' for help.")
