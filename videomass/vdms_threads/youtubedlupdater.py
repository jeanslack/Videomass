# -*- coding: UTF-8 -*-
"""
Name: youtubedlupdater.py
Porpose: update tasks
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Aug.02.2021
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
import shlex
import sys
import os
from threading import Thread
import wx
from pubsub import pub


class UpdateYoutubedlAppimage(Thread):
    """
    Install or Update `youtube_dl` python package (library) using
    xterm terminal emulator with subprocess for displaying and
    redirecting the output to log file.

    """

    def __init__(self, log, appimage):
        """
        Attributes defined here:
        executable       current python executable
        self.status      exit status value
        self.cmd         command for execution

        matches of xterm options used here:

        +hold  ......... not retains window after exit
        -u8 ............ use UTF8 mode coding
        -bg ............ background console color
        -fa ............ the font used (FreeType font-selection pattern)
        -fs ............ the font size
        -geometry ...... window width and height respectively
        -title ......... title on the window
        -e ............. start your command after e.g. 'ls -l'

        type `xterm -h` for major info

        """
        name = os.path.basename(appimage)
        binpath = os.path.dirname(sys.executable)
        exe = os.path.join(binpath + '/youtube_dl_update_appimage.sh')
        self.status = None
        self.cmd = shlex.split(
            f"xterm +hold -u8 -bg 'grey15' -fa 'Monospace' "
            f"-fs 9 -geometry 120x35 -title '..Updating "
            f"youtube_dl package on {name}' -e '{exe} {appimage} "
            f"2>&1 | tee {log}'"
            )

        Thread.__init__(self)
        self.start()  # start the thread
    # ----------------------------------------------------------------#

    def run(self):
        """
        Spawn process to xterm emulator.

        """
        try:
            proc = subprocess.run(self.cmd, shell=False)

        except FileNotFoundError as err:
            self.status = err

        if proc.returncode:
            self.status = "EXIT: {proc.returncode}\nERROR: {proc.stderr}"
        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
