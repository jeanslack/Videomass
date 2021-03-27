# -*- coding: UTF-8 -*-
# Name: ffplay_file.py
# Porpose: playback media file via ffplay
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Feb.19.2021 *PEP8 compatible*
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
import wx
from pubsub import pub
import subprocess
import platform
if not platform.system() == 'Windows':
    import shlex
import os
from threading import Thread
from videomass3.vdms_io.make_filelog import write_log  # write initial log


def msg_Error(msg):
    """
    Receive error messages via wxCallafter
    """
    wx.MessageBox("FFplay ERROR:  %s" % (msg), "Videomass", wx.ICON_ERROR)


def msg_Info(msg):
    """
    Receive info messages via wxCallafter
    """
    wx.MessageBox("FFplay:  %s" % (msg), "Videomass", wx.ICON_INFORMATION)


class File_Play(Thread):
    """
    Playback local file with ffplay media player via subprocess.Popen
    class (ffplay is a player which need x-window-terminal-emulator)

    """
    def __init__(self, filepath, timeseq, param, logdir,
                 ffplay_url, ffplay_loglev, autoexit):
        """
        The self.FFPLAY_loglevel has flag 'error -hide_banner' by default,
        see videomass.conf for details.
        WARNING Do not use the "-stats" option as it does not work here.

        """
        self.filename = filepath  # file name selected
        self.time_seq = timeseq  # seeking
        self.param = param  # additional parameters if present
        logdir = logdir
        self.ffplay = ffplay_url
        self.ffplay_loglev = ffplay_loglev
        self.autoexit = '-autoexit' if autoexit is True else ''
        self.logf = os.path.join(logdir, 'ffplay.log')
        write_log('ffplay.log', logdir)
        # set initial file LOG

        Thread.__init__(self)
        ''' constructor'''
        self.start()
    # ----------------------------------------------------------------#

    def run(self):
        """
        Get and redirect output errors on p.returncode instance and on
        OSError exception. Otherwise the getted output as information
        given by error[1]

        """
        # time.sleep(.5)
        cmd = '"%s" %s %s %s -i "%s" %s' % (self.ffplay,
                                         self.time_seq,
                                         self.ffplay_loglev,
                                         self.autoexit,
                                         self.filename,
                                         self.param
                                         )
        self.logWrite(cmd)
        if not platform.system() == 'Windows':
            cmd = shlex.split(cmd)
            info = None
            shell = False
        else:
            # NOTE: info flag do not work with ffplay
            # on MS-Windows. Fixed with shell=True flag.
            shell = True
            info = None
            # info = subprocess.STARTUPINFO()
            # info.dwFlags |= subprocess.SW_HIDE
        try:
            p = subprocess.Popen(cmd,
                                 shell=shell,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True,
                                 startupinfo=info,
                                 )
            error = p.communicate()

        except OSError as err:  # subprocess error
            wx.CallAfter(msg_Error, err)
            self.logError(err)  # append log error
            pub.sendMessage("STOP_DOWNLOAD_EVT", filename=self.filename)
            return

        else:
            if error[1]:  # ffplay error
                wx.CallAfter(msg_Info, error[1])
                self.logError(error[1])  # append log error
                pub.sendMessage("STOP_DOWNLOAD_EVT", filename=self.filename)
                return
            else:
                # Threads_Handling.stop_download(self, self.filename)
                pub.sendMessage("STOP_DOWNLOAD_EVT", filename=self.filename)
                return
    # ----------------------------------------------------------------#

    def logWrite(self, cmd):
        """
        write ffplay command log
        """
        with open(self.logf, "a", encoding='utf8') as log:
            log.write("%s\n" % (cmd))
    # ----------------------------------------------------------------#

    def logError(self, error):
        """
        write ffplay errors
        """
        with open(self.logf, "a", encoding='utf8') as logerr:
            logerr.write("\n[FFMPEG] FFplay "
                         "OUTPUT:\n%s\n" % (error))
