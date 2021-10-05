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
import platform
import sys
import os
import shutil
import ssl
import urllib.request
from threading import Thread
import wx
from pubsub import pub


'''
class CheckNewRelease(Thread):
    """
    Read the latest version of youtube-dl on github website (see url) .
    """
    def __init__(self, url):
        """
        Attributes defined here:
        self.data: tuple object with exit status of the process
        """
        self.url = url
        self.data = None

        Thread.__init__(self)
        """initialize"""

        self.start()  # start the thread (va in self.run())
    # ----------------------------------------------------------------#

    def run(self):
        """
        Check for new version release
        """
        # HACK fix soon the ssl certificate
        ssl._create_default_https_context = ssl._create_unverified_context
        try:
            req = (urllib.request.build_opener().open(
                   self.url).read().decode('utf-8').strip())
            self.data = req, None

        except urllib.error.HTTPError as error:
            self.data = None, error

        except urllib.error.URLError as error:
            self.data = None, error

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
'''
# -------------------------------------------------------------------------#

'''
class UpgradeLatest(Thread):
    """
    Download latest version of youtube-dl.exe, see self.url .
    """

    def __init__(self, url, dest):
        """
        Attributes defined here:
        latest: latest version available .
        self.dest: location pathname to download
        self.data: returned output of the self.status
        self.status: tuple object with exit status of the process

        """
        self.url = url
        self.dest = dest
        self.data = None
        self.status = None

        Thread.__init__(self)
        self.start()  # start the thread (va in self.run())
    # ----------------------------------------------------------------#

    def run(self):
        """
        Check for new version release
        """
        # HACK fix soon the ssl certificate
        context = ssl._create_unverified_context()
        headers = {'User-Agent': 'Mozilla/5.0'}
        page = urllib.request.Request(self.url, headers=headers)
        try:
            with urllib.request.urlopen(page, context=context) as \
                    response, open(self.dest, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

            self.status = self.url, None

        except urllib.error.HTTPError as error:
            self.status = None, error

        except urllib.error.URLError as error:
            self.status = None, error

        self.data = self.status

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
'''
# ---------------------------------------------------------------------#


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
            "xterm +hold -u8 -bg 'grey15' -fa 'Monospace' "
            "-fs 9 -geometry 120x35 -title '..Updating "
            "youtube_dl package on %s' -e '%s %s "
            "2>&1 | tee %s'" % (name, exe, appimage, log)
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
            self.status = "EXIT: %s\nERROR: %s" % (proc.returncode,
                                                   proc.stderr)
        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )


def update_ydl_windows():
    """
    Prompt pkg update program via pip on Windows.
    """
    WELCOME_MESSAGE = f'\nCheck for "{mod}" update... Please wait...\n'
    GOODBYE_MESSAGE = f'\nDone. Restart Videomass now.\nPress ENTER to exit.'

    print(WELCOME_MESSAGE)
    try:
        cmd = subprocess.run([sys.executable, '-m', 'pip', 'install', '-U',
                             'youtube_dl', 'yt_dlp'], shell=True, check=True)
    except subprocess.CalledProcessError as err:
        print('\nERROR: %s' % err)
        input('\nPress ENTER to exit.')
        return err
    else:
        input(GOODBYE_MESSAGE)
        return
