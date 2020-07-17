# -*- coding: UTF-8 -*-
# Name: ffplay_file.py
# Porpose: playback media file via ffplay
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.06.2020 *PEP8 compatible*
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
    wx.MessageBox("FFplay ERROR:  %s" % (msg),
                  "Videomass: FFplay",
                  wx.ICON_ERROR
                  )


def msg_Info(msg):
    """
    Receive info messages via wxCallafter
    """
    wx.MessageBox("FFplay INFORMATION:  %s" % (msg),
                  "Videomass: FFplay",
                  wx.ICON_INFORMATION
                  )


class File_Play(Thread):
    """
    Simple multimedia playback with subprocess.Popen class to run ffplay
    by FFmpeg (ffplay is a player which need x-window-terminal-emulator)

    """

    def __init__(self, filepath, timeseq, param, logdir,
                 ffplay_url, ffplay_loglev):
        """
        The self.FFPLAY_loglevel has flag 'error -hide_banner'
        by default (see videomass.conf).
        NOTE: Do not use '-stats' option it do not work.
        """
        Thread.__init__(self)
        ''' constructor'''
        self.filename = filepath  # file name selected
        self.time_seq = timeseq  # seeking
        self.param = param  # additional parameters if present
        self.logdir = logdir
        self.ffplay = ffplay_url
        self.ffplay_loglev = ffplay_loglev
        self.logf = os.path.join(self.logdir, 'Videomass_FFplay.log')
        write_log('Videomass_FFplay.log', self.logdir)
        # set initial file LOG

        self.start()
    # ----------------------------------------------------------------#

    def run(self):
        """
        Get and redirect output errors on p.returncode instance and on
        OSError exception. Otherwise the getted output as information
        given by error [1] .
        """

        # time.sleep(.5)
        cmd = '%s %s %s -i "%s" %s' % (self.ffplay,
                                       self.time_seq,
                                       self.ffplay_loglev,
                                       self.filename,
                                       self.param,
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
            return

        else:
            if p.returncode:  # ffplay error
                if error[1]:
                    msg = error[1]
                else:
                    msg = "Unrecognized error"

                wx.CallAfter(msg_Error, error[1])
                self.logError(error[1])  # append log error
                return

        if error[1]:  # ffplay info
            wx.CallAfter(msg_Info, error[1])
            self.logWrite(error[1])  # append log info
            return
    # ----------------------------------------------------------------#

    def logWrite(self, cmd):
        """
        write ffplay command log
        """
        with open(self.logf, "a") as log:
            log.write("%s\n\n" % (cmd))
    # ----------------------------------------------------------------#

    def logError(self, error):
        """
        write ffplay errors
        """
        with open(self.logf, "a") as logerr:
            logerr.write("[FFMPEG] FFplay "
                         "ERRORS:\n%s\n\n" % (error))
