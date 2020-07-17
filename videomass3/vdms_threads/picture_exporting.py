# -*- coding: UTF-8 -*-
# Name: pictures_exporting.py
# Porpose: FFmpeg long processing task on save as pictures
# Compatibility: Python3, wxPython4 Phoenix (OS Unix-like only)
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
import time
from pubsub import pub


def logWrite(cmd, sterr, logname, logdir):
    """
    writes ffmpeg commands and status error during threads below
    """
    if sterr:
        apnd = "...%s\n\n" % (sterr)
    else:
        apnd = "%s\n\n" % (cmd)

    with open(os.path.join(logdir, logname), "a") as log:
        log.write(apnd)

# ------------------------------ THREADS -------------------------------#


"""
NOTE MS Windows:

subprocess.STARTUPINFO()

https://stackoverflow.com/questions/1813872/running-
a-process-in-pythonw-with-popen-without-a-console?lq=1>

NOTE capturing output in real-time (Windows, Unix):

https://stackoverflow.com/questions/1388753/how-to-get-output-
from-subprocess-popen-proc-stdout-readline-blocks-no-dat?rq=1
"""


class PicturesFromVideo(Thread):
    """
    This class represents a separate thread for running simple
    single processes to save video sequences as pictures.

    """
    # get videomass wx.App attribute
    get = wx.GetApp()
    OS = get.OS
    LOGDIR = get.LOGdir
    FFMPEG_URL = get.FFMPEG_url
    FFMPEG_LOGLEV = get.FFMPEG_loglev
    NOT_EXIST_MSG = _("Is 'ffmpeg' installed on your system?")
    # ------------------------------------------------------

    def __init__(self, varargs, duration, logname, timeseq):
        """
        self.cmd contains a unique string that comprend filename input
        and filename output also.
        The duration adds another 10 seconds due to problems with the
        progress bar
        """
        Thread.__init__(self)
        """initialize"""
        self.stop_work_thread = False  # process terminate
        self.cmd = varargs[4]  # comand set on single pass
        self.duration = duration[0]+10  # duration list
        self.time_seq = timeseq  # a time segment
        self.count = 0  # count first for loop
        self.logname = logname  # title name of file log
        self.fname = varargs[1]  # file name

        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        """
        cmd = ('%s %s %s -i "%s" %s ' % (PicturesFromVideo.FFMPEG_URL,
                                         self.time_seq,
                                         PicturesFromVideo.FFMPEG_LOGLEV,
                                         self.fname,
                                         self.cmd,
                                         ))
        count = 'File %s/%s' % ('1', '1',)
        com = "%s\n%s" % (count, cmd)

        wx.CallAfter(pub.sendMessage,
                     "COUNT_EVT",
                     count=count,
                     duration=self.duration,
                     fname=self.fname,
                     end='',
                     )
        logWrite(com,
                 '',
                 self.logname,
                 PicturesFromVideo.LOGDIR,
                 )  # write n/n + command only

        if not PicturesFromVideo.OS == 'Windows':
            cmd = shlex.split(cmd)
            info = None
        else:  # Hide subprocess window on MS Windows
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        try:
            with subprocess.Popen(cmd,
                                  stderr=subprocess.PIPE,
                                  bufsize=1,
                                  universal_newlines=True,
                                  startupinfo=info,) as p:
                for line in p.stderr:
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output=line,
                                 duration=self.duration,
                                 status=0,
                                 )
                    if self.stop_work_thread:  # break second 'for' loop
                        p.terminate()
                        break

                if p.wait():  # error
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output=line,
                                 duration=self.duration,
                                 status=p.wait(),
                                 )
                    logWrite('',
                             "Exit status: %s" % p.wait(),
                             self.logname,
                             PicturesFromVideo.LOGDIR,
                             )  # append exit error number

                else:  # status ok
                    wx.CallAfter(pub.sendMessage,
                                 "COUNT_EVT",
                                 count='',
                                 duration='',
                                 fname='',
                                 end='ok'
                                 )
        except (OSError, FileNotFoundError) as err:
            e = "%s\n  %s" % (err, PicturesFromVideo.NOT_EXIST_MSG)
            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=e,
                         duration=0,
                         fname=self.fname,
                         end='error',
                         )
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT")
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
