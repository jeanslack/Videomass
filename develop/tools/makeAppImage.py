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
MACHINE = platform.machine()  # current machine ARCH (i386, x86_64, etc.)


def make_appimage(arch, releases=RELEASES):
    """
    Make Videomass.AppImage for deployment.
    All of This assume that follow resources exists:
        1)  The Videomass source directory (as by git sources)
        2) 'APPDIR_RELESES' directory on videomass sources base dir (root)
        2)  linuxdeploy*.AppImage in '/$HOME/Application' directory

    """
    this = os.path.realpath(os.path.abspath(__file__))
    base_src = os.path.dirname(os.path.dirname(os.path.dirname(this)))
    sys.path.insert(0, base_src)
    try:
        from videomass3.vdms_sys.msg_info import current_release
    except ModuleNotFoundError as error:
        sys.exit(error)
    else:
        cr = current_release()
        version = cr[2]

    appdir = os.path.join(releases, version)
    executable = "./dist/videomass"
    desktop_file = "./videomass3/art/videomass.desktop"
    icon = "./videomass3/art/icons/videomass.png"

    # create appdir with linuxdeploy.AppImage:
    cmd = ["version={}".format(version),
           "$HOME/Applications/linuxdeploy-%s.AppImage" % arch,
           "--appdir={}".format(appdir),
           "--executable={}".format(executable),
           "--desktop-file={}".format(desktop_file),
           "--icon-file={}".format(icon)
           ]
    os.system(" ".join(cmd))

    # package AppImage from appdir
    cmd2 = ["version={}".format(version),
            "$HOME/Applications/linuxdeploy-%s.AppImage" % arch,
            "--appdir={}".format(appdir),
            "--output appimage"
            ]
    os.system(" ".join(cmd2))


def main(releases=RELEASES, machine=MACHINE):
    """
    check for resources and requirements to make
    Videomass-i386.AppImage or Videomass-x86_64.AppImage .
    NOTE there are only linuxdeploy for i386 and x86_64 architectures for now

    """
    if not machine:
        sys.exit('ERROR: CPU architecture value cannot be determined, exit.')

    elif machine in ('i386', 'i486', 'i586', 'i686'):
        arch = 'i386'

    elif machine == 'x86_64':
        arch = machine

    else:
        sys.exit("ERROR: Sorry, there is no linuxdeploy tool available "
                 "for this architecture '%s' but only for 'i386' and "
                 "'x86_64' architectures." % machine)

    if not os.path.isdir(releases):
        os.mkdir(releases)  # make dir 'APPDIR_RELESES'

    linuxdeploy = os.path.expanduser("~/Applications/linuxdeploy-%s.AppImage"
                                     % arch)
    if not os.path.exists(linuxdeploy):
        if not os.path.isdir(os.path.dirname(linuxdeploy)):
            os.mkdir(os.path.dirname(linuxdeploy))
        # try to get linuxdeploy AppImage from url based on machine arch
        import shutil
        import stat
        import ssl
        import urllib.request

        url = ("https://github.com/linuxdeploy/linuxdeploy/releases/"
               "download/continuous/linuxdeploy-%s.AppImage" % arch)
        try:
            with urllib.request.urlopen(url) as response,\
                 open(linuxdeploy, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        except urllib.error.HTTPError as error:
            sys.exit(error)

        except urllib.error.URLError as error:
            sys.exit(error)

        # make executable linuxdeploy AppImage
        if os.path.isfile(linuxdeploy):
            st = os.stat(linuxdeploy)
            os.chmod(linuxdeploy, st.st_mode | stat.S_IXUSR |
                     stat.S_IXGRP | stat.S_IXOTH)

    dist = os.path.join(os.path.dirname(releases), 'dist', 'videomass')

    if not os.path.exists(dist) or not os.path.isfile(dist):
        try:
            # run pyinstaller build
            subprocess.check_call([sys.executable,
                                   "./develop/tools/pyinstaller_setup.py",
                                   "-m"])
        except subprocess.CalledProcessError as err:
            print("\nPyinstaller build FAILED.\n")
            sys.exit(err)
        print("\nPyinstaller build done.\n")

    make_appimage(arch)


if __name__ == '__main__':
    main()
