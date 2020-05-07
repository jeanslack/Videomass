# -*- coding: UTF-8 -*-

#########################################################
# Name: mpv_url.py
# Porpose: playback URLs video via mpv
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: May.07.2020 *PEP8 compatible*
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
import time
import os
from threading import Thread
from videomass3.vdms_io.make_filelog import write_log  # write initial log

# get data from bootstrap
get = wx.GetApp()
LOGDIR = get.LOGdir
OS = get.OS

if not OS == 'Windows':
    import shlex


def msg_Error(msg):
    """
    Receive error messages via wxCallafter
    """
    wx.MessageBox("%s" % (msg),
                  "Videomass: mpv ERROR",
                  wx.ICON_ERROR
                  )


def msg_Info(msg):
    """
    Receive info messages via wxCallafter
    """
    wx.MessageBox("MPV message information:  %s" % (msg),
                  "Videomass: mpv INFORMATION",
                  wx.ICON_INFORMATION
                  )


class Url_Play(Thread):
    """
    subprocess.Popen class to run mpv media player for playback URLs .
    """
    def __init__(self, url):
        """
        self.url : It can have the quality `--ytdl-format` flag set
        """
        Thread.__init__(self)
        ''' constructor'''
        self.url = url  # file name selected
        self.logf = os.path.join(LOGDIR, 'Videomass_mpv.log')
        write_log('Videomass_mpv.log', LOGDIR)
        # set initial file LOG

        self.start()
    # ----------------------------------------------------------------#

    def run(self):
        """
        Get and redirect output errors on p.returncode instance and on
        OSError exception. Otherwise the getted output as information
        given by output .
        """

        # time.sleep(.5)
        cmd = 'mpv %s' % (self.url)
        self.logWrite(cmd)
        if not OS == 'Windows':
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
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True,
                                 startupinfo=info,
                                 )
            error, output = p.communicate()

        except OSError as err:  # subprocess error
            wx.CallAfter(msg_Error, _('{}\n\nYou need mpv to play urls '
                                    'but mpv is not installed.').format(err))
            self.logError(err)  # append log error
            return

        else:
            if p.returncode:  # mpv error
                if error:
                    msg = error
                else:
                    msg = "Unrecognized error"

                wx.CallAfter(msg_Error, error)
                self.logError(error)  # append log error
                return

        if output:  # mpv info
            wx.CallAfter(msg_Info, output)
            self.logWrite(output)  # append log info
            return
    # ----------------------------------------------------------------#

    def logWrite(self, cmd):
        """
        write mpv command log
        """
        with open(self.logf, "a") as log:
            log.write("%s\n\n" % (cmd))
    # ----------------------------------------------------------------#

    def logError(self, error):
        """
        write  mpv errors
        """
        with open(self.logf, "a") as logerr:
            logerr.write("[MPV] MESSAGE:\n%s\n\n" % (error))
