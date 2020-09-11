# -*- coding: UTF-8 -*-
# Name: two_pass.py
# Porpose: FFmpeg long processing task on 2 pass conversion
# Compatibility: Python3, wxPython4 Phoenix
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
import itertools
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


class TwoPass(Thread):
    """
    This class represents a separate thread which need to read the
    stdout/stderr in real time mode. The subprocess module is instantiated
    twice for two different tasks: the process on the first video pass and
    the process on the second video pass for video only.

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    OS = get.OS
    LOGDIR = get.LOGdir
    FFMPEG_URL = get.FFMPEG_url
    FFMPEG_LOGLEV = get.FFMPEG_loglev
    FF_THREADS = get.FFthreads
    NOT_EXIST_MSG = _("Is 'ffmpeg' installed on your system?")

    def __init__(self, varargs, duration, logname, timeseq):
        """
        The 'volume' attribute may have an empty value, but it will
        have no influence on the type of conversion.
        """
        self.stop_work_thread = False  # process terminate
        self.filelist = varargs[1]  # list of files (elements)
        self.passList = varargs[5]  # comand list set for double-pass
        self.outputdir = varargs[3]  # output path
        self.extoutput = varargs[2]  # format (extension)
        self.duration = duration  # duration list
        self.time_seq = timeseq  # a time segment
        self.volume = varargs[7]  # volume compensation data
        self.count = 0  # count first for loop
        self.countmax = len(varargs[1])  # length file list
        self.logname = logname  # title name of file log
        self.nul = 'NUL' if TwoPass.OS == 'Windows' else '/dev/null'

        Thread.__init__(self)
        """initialize"""
        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        """
        for (files,
             folders,
             volume,
             duration) in itertools.zip_longest(self.filelist,
                                                self.outputdir,
                                                self.volume,
                                                self.duration,
                                                fillvalue='',
                                                ):
            basename = os.path.basename(files)  # nome file senza path
            filename = os.path.splitext(basename)[0]  # nome senza ext
            source_ext = os.path.splitext(basename)[1].split('.')[1]  # ext
            outext = source_ext if not self.extoutput else self.extoutput

            # --------------- first pass
            pass1 = ('%s %s %s -i "%s" %s %s '
                     '-y %s' % (TwoPass.FFMPEG_URL,
                                TwoPass.FFMPEG_LOGLEV,
                                self.time_seq,
                                files,
                                self.passList[0],
                                TwoPass.FF_THREADS,
                                self.nul,
                                ))
            self.count += 1
            count = 'File %s/%s - Pass One' % (self.count, self.countmax)
            cmd = "%s\n%s" % (count, pass1)
            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=count,
                         duration=duration,
                         fname=files,
                         end='',
                         )
            logWrite(cmd,
                     '',
                     self.logname,
                     TwoPass.LOGDIR,
                     )  # write n/n + command only

            if not TwoPass.OS == 'Windows':
                pass1 = shlex.split(pass1)
                info = None
            else:  # Hide subprocess window on MS Windows
                info = subprocess.STARTUPINFO()
                info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            try:
                with subprocess.Popen(pass1,
                                      stderr=subprocess.PIPE,
                                      bufsize=1,
                                      universal_newlines=True,
                                      startupinfo=info,) as p1:

                    for line in p1.stderr:
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output=line,
                                     duration=duration,
                                     status=0
                                     )
                        if self.stop_work_thread:  # break second 'for' loop
                            p1.terminate()
                            break

                    if p1.wait():  # will add '..failed' to txtctrl
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output=line,
                                     duration=duration,
                                     status=p1.wait(),
                                     )
                        logWrite('',
                                 "Exit status: %s" % p1.wait(),
                                 self.logname,
                                 TwoPass.LOGDIR
                                 )  # append exit error number

            except (OSError, FileNotFoundError) as err:
                e = "%s\n  %s" % (err, TwoPass.NOT_EXIST_MSG)
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count=e,
                             duration=0,
                             fname=files,
                             end='error',
                             )
                break

            if self.stop_work_thread:  # break first 'for' loop
                p1.terminate()
                break  # fermo il ciclo for, altrimenti passa avanti

            if p1.wait() == 0:  # will add '..terminated' to txtctrl
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count='',
                             duration='',
                             fname='',
                             end='ok'
                             )
            # --------------- second pass ----------------#
            pass2 = ('%s %s %s -i "%s" %s %s %s '
                     '-y "%s/%s.%s"' % (TwoPass.FFMPEG_URL,
                                        TwoPass.FFMPEG_LOGLEV,
                                        self.time_seq,
                                        files,
                                        self.passList[1],
                                        volume,
                                        TwoPass.FF_THREADS,
                                        folders,
                                        filename,
                                        outext,
                                        ))
            count = 'File %s/%s - Pass Two' % (self.count, self.countmax,)
            cmd = "%s\n%s" % (count, pass2)
            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=count,
                         duration=duration,
                         fname=files,
                         end='',
                         )
            logWrite(cmd, '', self.logname, TwoPass.LOGDIR)

            if not TwoPass.OS == 'Windows':
                pass2 = shlex.split(pass2)
                info = None
            else:  # Hide subprocess window on MS Windows
                info = subprocess.STARTUPINFO()
                info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            with subprocess.Popen(pass2,
                                  stderr=subprocess.PIPE,
                                  bufsize=1,
                                  universal_newlines=True,
                                  startupinfo=info,) as p2:

                for line2 in p2.stderr:
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output=line2,
                                 duration=duration,
                                 status=0,
                                 )
                    if self.stop_work_thread:
                        p2.terminate()
                        break

                if p2.wait():  # will add '..failed' to txtctrl
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output=line,
                                 duration=duration,
                                 status=p2.wait(),
                                 )
                    logWrite('',
                             "Exit status: %s" % p2.wait(),
                             self.logname,
                             TwoPass.LOGDIR,
                             )  # append exit error number

            if self.stop_work_thread:  # break first 'for' loop
                p2.terminate()
                break  # fermo il ciclo for, altrimenti passa avanti

            if p2.wait() == 0:  # will add '..terminated' to txtctrl
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count='',
                             duration='',
                             fname='',
                             end='ok'
                             )
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT")
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
