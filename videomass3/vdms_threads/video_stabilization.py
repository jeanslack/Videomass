# -*- coding: UTF-8 -*-
# Name: video_stabilization.py
# Porpose: FFmpeg long processing vidstab
# Compatibility: Python3, wxPython4 Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: March.20.2021 *PEP8 compatible*
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


class VidStab(Thread):
    """
    This class represents a separate thread which need
    to read the stdout/stderr in real time mode for
    different tasks.

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    OS = get.OS
    LOGDIR = get.LOGdir
    FFMPEG_URL = get.FFMPEG_url
    FFMPEG_LOGLEV = get.FFMPEG_loglev
    FF_THREADS = get.FFthreads
    SUFFIX = '' if get.FILEsuffix == 'none' else get.FILEsuffix
    NOT_EXIST_MSG = _("Is 'ffmpeg' installed on your system?")

    def __init__(self, varargs, duration, logname, timeseq):
        """
        The 'volume' attribute may have an empty value, but it will
        have no influence on the type of conversion.
        """
        self.stop_work_thread = False  # process terminate
        self.filelist = varargs[1]  # list of files (elements)
        self.passList = varargs[5]  # comand list set for double-pass
        self.makeduo = varargs[4]  # one more process for the duo file
        self.outputdir = varargs[3]  # output path
        self.extoutput = varargs[2]  # format (extension)
        self.duration = duration  # duration list
        self.time_seq = timeseq  # a time segment
        self.volume = varargs[7]  # volume compensation data
        self.count = 0  # count first for loop
        self.countmax = len(varargs[1])  # length file list
        self.logname = logname  # title name of file log
        self.nul = 'NUL' if VidStab.OS == 'Windows' else '/dev/null'

        spl = [s for s in varargs[6].split('-vf ')][1]
        addspl = ','.join([x for x in spl.split(',') if '-vf' not
                           in x and 'vidstabtransform' not in x and
                           'unsharp' not in x])  # if other filters
        self.addflt = '' if addspl == '' else '%s,' % (addspl)

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
            pass1 = ('"%s" %s %s -i "%s" %s %s '
                     '-y %s' % (VidStab.FFMPEG_URL,
                                VidStab.FFMPEG_LOGLEV,
                                self.time_seq,
                                files,
                                self.passList[0],
                                VidStab.FF_THREADS,
                                self.nul,
                                ))
            self.count += 1
            count = ('File %s/%s - Pass One: Video stabilization detect' % (
                     self.count, self.countmax))
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
                     VidStab.LOGDIR,
                     )  # write n/n + command only

            if not VidStab.OS == 'Windows':
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
                                 VidStab.LOGDIR
                                 )  # append exit error number

            except (OSError, FileNotFoundError) as err:
                e = "%s\n  %s" % (err, VidStab.NOT_EXIST_MSG)
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
            pass2 = ('"%s" %s %s -i "%s" %s %s %s '
                     '-y "%s/%s%s.%s"' % (VidStab.FFMPEG_URL,
                                          VidStab.FFMPEG_LOGLEV,
                                          self.time_seq,
                                          files,
                                          self.passList[1],
                                          volume,
                                          VidStab.FF_THREADS,
                                          folders,
                                          filename,
                                          VidStab.SUFFIX,
                                          outext,
                                          ))
            count = ('File %s/%s - Pass Two: Video transform' % (
                     self.count, self.countmax,))
            cmd = "%s\n%s" % (count, pass2)
            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=count,
                         duration=duration,
                         fname=files,
                         end='',
                         )
            logWrite(cmd, '', self.logname, VidStab.LOGDIR)

            if not VidStab.OS == 'Windows':
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
                             VidStab.LOGDIR,
                             )  # append exit status error

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

            # --------------- make duo ----------------#
            if self.makeduo:
                pass3 = ('"%s" %s %s -i "%s" %s -vf "[in] %spad=2*iw:ih '
                         '[left]; movie=%s/%s%s.%s [right]; '
                         '[left][right] overlay=main_w/2:0 [out]" '
                         '-y "%s/%s%s_DUO.%s"' % (VidStab.FFMPEG_URL,
                                                  VidStab.FFMPEG_LOGLEV,
                                                  self.time_seq,
                                                  files,
                                                  VidStab.FF_THREADS,
                                                  self.addflt,
                                                  folders,
                                                  filename,
                                                  VidStab.SUFFIX,
                                                  outext,
                                                  folders,
                                                  filename,
                                                  VidStab.SUFFIX,
                                                  outext,
                                                  ))
                count = 'File %s/%s - Make duo' % (self.count, self.countmax,)
                cmd = "%s\n%s" % (count, pass3)
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count=count,
                             duration=duration,
                             fname=files,
                             end='',
                             )
                logWrite(cmd, '', self.logname, VidStab.LOGDIR)

                if not VidStab.OS == 'Windows':
                    pass3 = shlex.split(pass3)
                    info = None
                else:  # Hide subprocess window on MS Windows
                    info = subprocess.STARTUPINFO()
                    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                with subprocess.Popen(pass3,
                                      stderr=subprocess.PIPE,
                                      bufsize=1,
                                      universal_newlines=True,
                                      startupinfo=info,) as p3:

                    for line3 in p3.stderr:
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output=line3,
                                     duration=duration,
                                     status=0,
                                     )
                        if self.stop_work_thread:
                            p3.terminate()
                            break

                    if p3.wait():  # will add '..failed' to txtctrl
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output=line,
                                     duration=duration,
                                     status=p3.wait(),
                                     )
                        logWrite('',
                                 "Exit status: %s" % p3.wait(),
                                 self.logname,
                                 VidStab.LOGDIR,
                                 )  # append exit error number

                if self.stop_work_thread:  # break first 'for' loop
                    p3.terminate()
                    break  # fermo il ciclo for, altrimenti passa avanti

                if p3.wait() == 0:  # will add '..terminated' to txtctrl
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
