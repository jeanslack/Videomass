# -*- coding: UTF-8 -*-

"""
Name: ffplay_file.py
Porpose: playback media file via ffplay
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
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
from videomass.vdms_io.make_filelog import make_log_template
if not platform.system() == 'Windows':
    import shlex


def showmsgerr(msg):
    """
    Receive error messages via wxCallafter
    """
    wx.MessageBox(f"FFplay ERROR:  {msg}",
                  _('Videomass - Error!'), wx.ICON_ERROR)


def showmsginfo(msg):
    """
    Receive info messages via wxCallafter
    """
    wx.MessageBox(f"FFplay:  {msg}", "Videomass", wx.ICON_INFORMATION)


class FilePlay(Thread):
    """
    Playback local file with ffplay media player via subprocess.Popen
    class (ffplay is a player which need x-window-terminal-emulator)

    """

    def __init__(self, filepath, timeseq, param, autoexit):
        """
        The self.FFPLAY_loglevel has flag 'error -hide_banner' by default,
        see videomass.conf for details.
        WARNING Do not use the "-stats" option as it does not work here.

        """
        get = wx.GetApp()  # get videomass wx.App attribute
        self.appdata = get.appset
        self.filename = filepath  # file name selected
        self.time_seq = timeseq  # seeking
        self.param = param  # additional parameters if present
        self.autoexit = '-autoexit' if autoexit else ''
        self.logf = os.path.join(self.appdata['logdir'], 'ffplay.log')
        make_log_template('ffplay.log', self.appdata['logdir'], mode="w")
        # set initial file LOG

        Thread.__init__(self)
        self.start()
    # ----------------------------------------------------------------#

    def run(self):
        """
        Get and redirect output errors on proc.returncode instance and on
        OSError exception. Otherwise the getted output as information
        given by error[1]

        """
        # time.sleep(.5)
        cmd = " ".join(f'"{self.appdata["ffplay_cmd"]}" '
                       f'{self.appdata["ffplay-default-args"]} '
                       f'{self.appdata["ffplay_loglev"]} '
                       f'{self.autoexit} '
                       f'{self.time_seq[0]} '
                       f'-i "{self.filename}" '
                       f'{self.time_seq[1]} '
                       f'{self.param}'.split()
                       )
        self.logwrite(cmd)

        if not platform.system() == 'Windows':
            cmd = shlex.split(cmd)
            info = None
            shell = False
        else:
            # NOTE: on MS-Windows, 'info' flag do not work with ffplay
            # is Fixed with shell=True flag.
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

                if error:  # ffplay error
                    wx.CallAfter(showmsginfo, error)
                    self.logerror(error)  # append log error
                    return

        except OSError as err:  # subprocess error
            wx.CallAfter(showmsgerr, err)
            self.logerror(err)  # append log error
            return
    # ----------------------------------------------------------------#

    def logwrite(self, cmd):
        """
        write ffplay command log
        """
        with open(self.logf, "a", encoding='utf-8') as log:
            log.write(f"{cmd}\n")
    # ----------------------------------------------------------------#

    def logerror(self, error):
        """
        write ffplay errors
        """
        with open(self.logf, "a", encoding='utf-8') as logerr:
            logerr.write(f"\n[FFMPEG] FFplay "
                         f"OUTPUT:\n{error}\n")
