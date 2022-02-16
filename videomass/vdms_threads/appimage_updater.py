# -*- coding: UTF-8 -*-
"""
Name: appimage_updater.py
Porpose: update tasks
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.16.2022
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


class AppImageUpdate(Thread):
    """
    This class is responsible for updating the Python packages
    on Videomass.Appimage using the xterm terminal emulator for
    displaying the output command in real time. Furthermore all
    output will be saved to a log file.

    """
    def __init__(self, logname, appimage_loc):
        """
        Attributes defined here:
        executable       current python executable
        self.status      exit status value
        self.cmd         command for execution

        matches of xterm options used here:

        +hold  ......... not retains window after exit
        -u8 ............ use UTF8 mode coding
        -bg ............ background console color
        -fg ............ foreground console color
        -fa ............ the font used (FreeType font-selection pattern)
        -fs ............ the font size
        -geometry ...... window width and height respectively
        -title ......... title on the window
        -xrm 'xterm*iconHint: /path/to/icon.xpm' .... to embed icon
        -e ............. start your command after e.g. 'ls -l'

        type `xterm -h` for major info

        """
        get = wx.GetApp()  # get data from bootstrap
        # background/foreground colours:
        colorscheme = get.appset['icontheme'][1]
        backgrd = colorscheme['BACKGRD']
        foregrd = colorscheme['TXT0']
        # icon:
        spath = get.appset['srcpath']
        xpm = 'art/icons/hicolor/48x48/apps/videomass.xpm'
        icon = os.path.join(os.path.dirname(spath), xpm)
        # set command:
        name = os.path.basename(appimage_loc)
        binpath = os.path.dirname(sys.executable)
        exe = os.path.join(binpath + '/youtube_dl_update_appimage.sh')
        self.status = None
        self.cmd = shlex.split(
            f"xterm +hold -u8 -bg '{backgrd}' -fg '{foregrd}' -fa "
            f"'Monospace' -fs 9 -geometry 120x35 -title 'Update of "
            f"downloaders on {name}' -xrm 'xterm*iconHint: "
            f"{icon}' -e '{exe} {appimage_loc} 2>&1 | tee {logname}'"
            )

        Thread.__init__(self)
        self.start()  # start the thread
    # ----------------------------------------------------------------#

    def run(self):
        """
        Spawn process to xterm emulator.

        """
        try:
            proc = subprocess.run(self.cmd, check=True, shell=False)

        except FileNotFoundError as err:
            self.status = err

        if proc.returncode:
            self.status = "EXIT: {proc.returncode}\nERROR: {proc.stderr}"
        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
