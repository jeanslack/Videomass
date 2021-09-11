# -*- coding: UTF-8 -*-
"""
Name: pictures_exporting.py
Porpose: FFmpeg long processing task on save as pictures
Compatibility: Python3, wxPython4 Phoenix (OS Unix-like only)
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: May.09.2021
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
import time
import subprocess
import platform
import wx
from pubsub import pub
if not platform.system() == 'Windows':
    import shlex


def logwrite(cmd, sterr, logname, logdir):
    """
    writes ffmpeg commands and status error during threads below
    """
    if sterr:
        apnd = "...%s\n\n" % (sterr)
    else:
        apnd = "%s\n\n" % (cmd)

    with open(os.path.join(logdir, logname), "a", encoding='utf8') as log:
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
    get = wx.GetApp()  # get videomass wx.App attribute
    appdata = get.appset
    NOT_EXIST_MSG = _("Is 'ffmpeg' installed on your system?")
    # ------------------------------------------------------

    def __init__(self, varargs, duration, logname, timeseq):
        """
        self.cmd contains a unique string that comprend filename input
        and filename output also.
        The duration adds another 10 seconds due to problems with the
        progress bar
        """
        self.stop_work_thread = False  # process terminate
        self.outputdir = varargs[3]  # output directory
        self.cmd = varargs[4]  # comand set on single pass
        self.duration = duration[0]  # duration list
        self.time_seq = timeseq  # a time segment
        self.count = 0  # count first for loop
        self.logname = logname  # title name of file log
        self.fname = varargs[1]  # file name

        Thread.__init__(self)
        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        """
        cmd = ('"%s" %s %s -i '
               '"%s" %s ' % (PicturesFromVideo.appdata['ffmpeg_bin'],
                             self.time_seq,
                             PicturesFromVideo.appdata['ffmpegloglev'],
                             self.fname,
                             self.cmd,
                             ))
        count = 'File 1/1'
        com = ('%s\nSource: "%s"\nDestination: "%s"\n\n'
               '[COMMAND]:\n%s' % (count, self.fname, self.outputdir, cmd))

        wx.CallAfter(pub.sendMessage,
                     "COUNT_EVT",
                     count=count,
                     fsource='Source:  "%s"' % self.fname,
                     destination='Destination:  "%s"' % self.outputdir,
                     duration=self.duration,
                     end='',
                     )
        logwrite(com,
                 '',
                 self.logname,
                 PicturesFromVideo.appdata['logdir'],
                 )  # write n/n + command only

        if not PicturesFromVideo.appdata['ostype'] == 'Windows':
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
                                  startupinfo=info,) as proc:
                for line in proc.stderr:
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output=line,
                                 duration=self.duration,
                                 status=0,
                                 )
                    if self.stop_work_thread:  # break second 'for' loop
                        proc.terminate()
                        break

                if proc.wait():  # error
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output=line,
                                 duration=self.duration,
                                 status=proc.wait(),
                                 )
                    logwrite('',
                             "Exit status: %s" % proc.wait(),
                             self.logname,
                             PicturesFromVideo.appdata['logdir'],
                             )  # append exit error number

                else:  # status ok
                    wx.CallAfter(pub.sendMessage,
                                 "COUNT_EVT",
                                 count='',
                                 fsource='',
                                 destination='',
                                 duration='',
                                 end='ok'
                                 )
        except (OSError, FileNotFoundError) as err:
            excepterr = "%s\n  %s" % (err, PicturesFromVideo.NOT_EXIST_MSG)
            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=excepterr,
                         fsource='',
                         destination='',
                         duration=0,
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
