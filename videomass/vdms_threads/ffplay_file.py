# -*- coding: UTF-8 -*-

"""
Name: ffplay_file.py
Porpose: playback media file via ffplay
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Oct.18.2021
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
from threading import Thread
import subprocess
import platform
import wx
from pubsub import pub
from videomass.vdms_io.make_filelog import make_log_template
if not platform.system() == 'Windows':
    import shlex


def msg_error(msg):
    """
    Receive error messages via wxCallafter
    """
    wx.MessageBox(f"FFplay ERROR:  {msg}", "Videomass", wx.ICON_ERROR)


def msg_info(msg):
    """
    Receive info messages via wxCallafter
    """
    wx.MessageBox(f"FFplay:  {msg}", "Videomass", wx.ICON_INFORMATION)


class FilePlay(Thread):
    """
    Playback local file with ffplay media player via subprocess.Popen
    class (ffplay is a player which need x-window-terminal-emulator)

    """

    def __init__(self,
                 filepath,
                 timeseq,
                 param,
                 logdir,
                 ffplay_url,
                 ffplay_loglev,
                 ffplay_params,
                 autoexit
                 ):
        """
        The self.FFPLAY_loglevel has flag 'error -hide_banner' by default,
        see videomass.conf for details.
        WARNING Do not use the "-stats" option as it does not work here.

        """
        self.filename = filepath  # file name selected
        self.time_seq = timeseq  # seeking
        self.param = param  # additional parameters if present
        self.ffplay = ffplay_url
        self.ffplay_loglev = ffplay_loglev
        self.ffplay_params = ffplay_params
        self.autoexit = '-autoexit' if autoexit is True else ''
        self.logf = os.path.join(logdir, 'ffplay.log')
        make_log_template('ffplay.log', logdir)
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

        cmd = " ".join(f'"{self.ffplay}" {self.time_seq} '
                       f'{self.ffplay_loglev} {self.ffplay_params} '
                       f'{self.autoexit} -i "{self.filename}" '
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
                                  startupinfo=info,
                                  ) as proc:
                error = proc.communicate()

                if error[1]:  # ffplay error
                    wx.CallAfter(msg_info, error[1])
                    self.logerror(error[1])  # append log error
                    pub.sendMessage("STOP_DOWNLOAD_EVT",
                                    filename=self.filename)
                    return
                # Threads_Handling.stop_download(self, self.filename)
                pub.sendMessage("STOP_DOWNLOAD_EVT", filename=self.filename)
                return

        except OSError as err:  # subprocess error
            wx.CallAfter(msg_error, err)
            self.logerror(err)  # append log error
            pub.sendMessage("STOP_DOWNLOAD_EVT", filename=self.filename)
            return
    # ----------------------------------------------------------------#

    def logwrite(self, cmd):
        """
        write ffplay command log
        """
        with open(self.logf, "a", encoding='utf8') as log:
            log.write(f"{cmd}\n")
    # ----------------------------------------------------------------#

    def logerror(self, error):
        """
        write ffplay errors
        """
        with open(self.logf, "a", encoding='utf8') as logerr:
            logerr.write(f"\n[FFMPEG] FFplay "
                         f"OUTPUT:\n{error}\n")
