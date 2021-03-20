# -*- coding: UTF-8 -*-
# Name: generic_task.py
# Porpose: Execute a generic task with FFmpeg
# Compatibility: Python3 (Unix, Windows)
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Dec.03.2020 *PEP8 compatible*
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
from threading import Thread


class FFmpegGenericTask(Thread):
    """
    Run a generic task with FFmpeg as a separate thread.
    This class does not redirect any progress output information
    for debugging, however you can get the exit status message

    USE:
        thread = FFmpegGenericTask(args)
        thread.join()
        error = thread.status
        if error:
            print('%s' % error)
            return

    """
    get = wx.GetApp()
    FFMPEG_URL = get.FFMPEG_url
    FFMPEG_LOGLEV = get.FFMPEG_loglev

    def __init__(self, param):
        """
        Attributes defined here:

        self.param, a string containing the command parameters
        of FFmpeg, excluding the command itself `ffmpeg`

        self.status, If the exit status is true (which can be an
        exception or error message given by returncode) it must be
        handled appropriately, in the other case it is None.

        """
        self.param = param
        self.status = None

        Thread.__init__(self)
        ''' constructor'''
        self.start()
    # ----------------------------------------------------------------#

    def run(self):
        """
        Get and redirect output errors on p.returncode instance and
        OSError exception. Otherwise the getted output is None

        """
        cmd = ('"%s" %s %s' % (FFmpegGenericTask.FFMPEG_URL,
                               FFmpegGenericTask.FFMPEG_LOGLEV,
                               self.param,
                               ))

        if not platform.system() == 'Windows':
            command = shlex.split(cmd)
            info = None
        else:  # Hide subprocess dos window on MS Windows
            command = cmd
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        try:
            p = subprocess.Popen(command,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True,
                                 startupinfo=info,
                                 )
            error = p.communicate()

        except OSError as err:  # command not found
            self.status = err
            return

        else:
            if p.returncode:  # ffmpeg error
                if error[1]:
                    self.status = error[1]
                else:
                    self.status = "Unrecognized error"
                return
