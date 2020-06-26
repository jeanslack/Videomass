#!/usr/bin/env python3

#########################################################
# Name: makeAppImage.py.py
# Porpose: automates the building of AppImage for videomass
# Compatibility: Python3
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: June.26.2020
#########################################################

# This file is part of Videomass.

#    Videomass is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass.  If not, see <http://www.gnu.org/licenses/>.

#########################################################
import os
import sys
import platform
import subprocess

if not platform.system() == 'Linux':
    sys.exit('ERROR: invalid platform, this tool work on Linux only, exit.')

RELEASES = os.path.realpath("./APPDIR_RELESES/")


def make_appimage(releases=RELEASES):
    """
    Deploy Videomass.AppImage.
    All of This assume that follow resources exists:
        1)  The Videomass source directory is intact (as by git sources)
        2)  That the '~/Application/linuxdeploy-x86_64.AppImage' exists
        3)  That the 'dist/videomass/videomass' executable exists (after
            build it by pyinstaller, of course)

    """
    this = os.path.realpath(os.path.abspath(__file__))
    base_src = os.path.dirname(os.path.dirname(os.path.dirname(this)))
    sys.path.insert(0, base_src)
    try:
        from videomass3.vdms_sys.msg_info import current_release
        cr = current_release()
        version = cr[2]
    except ModuleNotFoundError as error:
        sys.exit(error)

    appdir = os.path.join(releases, version)
    executable = "./dist/videomass"
    desktop_file = "./videomass3/art/videomass.desktop"
    icon = "./videomass3/art/icons/videomass.png"

    # create appdir with linuxdeploy.AppImage:
    cmd = ["version={}".format(version),
           "$HOME/Applications/linuxdeploy-x86_64.AppImage",
           "--appdir={}".format(appdir),
           "--executable={}".format(executable),
           "--desktop-file={}".format(desktop_file),
           "--icon-file={}".format(icon)
           ]
    os.system(" ".join(cmd))

    # package AppImage from appdir
    cmd2 = ["version={}".format(version),
            "$HOME/Applications/linuxdeploy-x86_64.AppImage",
            "--appdir={}".format(appdir),
            "--output appimage"
            ]
    os.system(" ".join(cmd2))


def main(releases=RELEASES):
    """
    check for releases folder and dist folder,
    if they don't exist, create them.
    """
    if not os.path.isdir(releases):
        os.mkdir(releases)

    dist = os.path.join(os.path.dirname(releases), 'dist', 'videomass')

    if not os.path.exists(dist) or not os.path.isfile(dist):
        # run pyinstaller build
        try:
            subprocess.check_call(["python3",
                                   "./dev/tools/pyinstaller_setup.py",
                                   "-m"])
        except subprocess.CalledProcessError as err:
            print("\nPyinstaller build FAILED.\n")
            sys.exit(err)
        print("\nPyinstaller build done.\n")

    make_appimage()


if __name__ == '__main__':
    main()
