# -*- coding: UTF-8 -*-

"""
Name: ffplay_file.py
Porpose: playback media file via ffplay
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Apr.20.2024
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
import os
from threading import Thread
import subprocess
import platform
import wx
from pubsub import pub
from videomass.vdms_utils.utils import Popen
from videomass.vdms_io.make_filelog import make_log_template
if not platform.system() == 'Windows':
    import shlex


def showmsgerr(msg):
    """
    Receive error messages via wxCallafter
    """
    if not msg:
        msg = _('Please, see «ffplay.log» file for error details.\n')
    wx.MessageBox(f"FFplay ERROR:\n{msg}",
                  _('Videomass - Error!'), wx.ICON_ERROR)
# ----------------------------------------------------------------#


def showmsginfo(msg):
    """
    Receive info messages via wxCallafter
    """
    wx.MessageBox(f"FFplay:  {msg}", "Videomass", wx.ICON_INFORMATION)
# ----------------------------------------------------------------#


def logwrite(cmd, logf):
    """
    write ffplay command log
    """
    with open(logf, "a", encoding='utf-8') as log:
        log.write(f"{cmd}\n")
# ----------------------------------------------------------------#


def logerror(error, logf):
    """
    write ffplay errors
    """
    with open(logf, "a", encoding='utf-8') as logerr:
        logerr.write(f"\n[FFMPEG] FFplay OUTPUT:\n{error}\n")
# ----------------------------------------------------------------#


class FilePlay(Thread):
    """
    Playback local file executing ffplay media player.
    """
    def __init__(self, param=''):
        """
        Don't use the "-stats" option here to avoid too much verbose
        output being shown in the message box as an error every time.

        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.param = param  # additional parameters if present
        self.logf = os.path.join(self.appdata['logdir'], 'ffplay.log')
        make_log_template('ffplay.log', self.appdata['logdir'], mode="w")

        Thread.__init__(self)
        self.start()
    # ----------------------------------------------------------------#

    def run(self):
        """
        Executes ffplay command via subprocess.Popen .
        IMPORTANT: do not use class Popen from utils.py here,
        because 'info' flag do not work on MS-Windows using ffplay.
        This is fixed using shell=True flag.
        """
        cmd = (f'"{self.appdata["ffplay_cmd"]}" '
               f'{self.appdata["ffplay-default-args"]} '
               f'{self.appdata["ffplay_loglev"]} '
               f'{self.param}'
               )
        logwrite(cmd, self.logf)

        if not platform.system() == 'Windows':
            cmd = shlex.split(cmd)
            info = None
            shell = False
        else:
            shell = True
            info = None
            # info = subprocess.STARTUPINFO()
            # info.dwFlags |= subprocess.SW_HIDE
        try:
            with subprocess.Popen(cmd,
                                  shell=shell,
                                  stderr=subprocess.PIPE,
                                  universal_newlines=True,
                                  encoding=self.appdata['encoding'],
                                  startupinfo=info,
                                  ) as proc:

                error = proc.communicate()[1]

                if error:
                    wx.CallAfter(showmsgerr, None)
                    logerror(error, self.logf)  # append log error
                    return

        except OSError as err:
            wx.CallAfter(showmsgerr, None)
            logerror(err, self.logf)
            # do not return here, go to END_PLAY directly

        wx.CallAfter(pub.sendMessage, "END_PLAY")


class FilePlayback_GetOutput(Thread):
    """
    Playback local file executing ffplay media player.
    This class differs from `FilePlay` in that it implements
    capturing and redirecting output messages from stderr.
    """
    def __init__(self, param=''):
        """
        The `stats` argument allows ffplay to update output
        messages progressively. This allows parsing of the
        output for progress informations.

        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.param = param  # additional parameters if present
        self.stats = '-stats'
        self.logf = os.path.join(self.appdata['logdir'], 'ffplay.log')
        # set initial file LOG:
        make_log_template('ffplay.log', self.appdata['logdir'], mode="w")

        Thread.__init__(self)
        self.start()
    # ----------------------------------------------------------------#

    def run(self):
        """
        Executes ffplay command via Popen from utils.py.
        """
        # time.sleep(.5)
        line = 'NO MESSAGE PROVIDED :-('
        cmd = (f'"{self.appdata["ffplay_cmd"]}" '
               f'{self.appdata["ffplay-default-args"]} '
               f'{self.appdata["ffplay_loglev"]} {self.stats} '
               f'{self.param}'
               )
        logwrite(cmd, self.logf)

        if not platform.system() == 'Windows':
            cmd = shlex.split(cmd)
        try:
            with Popen(cmd,
                       stderr=subprocess.PIPE,
                       bufsize=1,
                       universal_newlines=True,
                       encoding=self.appdata['encoding'],
                       ) as proc:
                for line in proc.stderr:
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_PLAY_COUNTER",
                                 output=line,
                                 status=0
                                 )
                if proc.wait():  # ..Failed
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_PLAY_COUNTER",
                                 output=None,
                                 status=proc.wait(),
                                 )
                    logerror(f"{proc.wait()} {line}", self.logf)
                    wx.CallAfter(showmsgerr, None)

        except OSError as err:
            wx.CallAfter(showmsgerr, None)
            logerror(err, self.logf)
            # do not return here, go to END_PLAY

        wx.CallAfter(pub.sendMessage, "END_PLAY")
