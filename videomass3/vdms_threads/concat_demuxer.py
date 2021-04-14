# -*- coding: UTF-8 -*-
# Name: one_pass.py
# Porpose: FFmpeg long processing task on one pass conversion
# Compatibility: Python3, wxPython4 Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
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


class Concat_Demuxer(Thread):
    """
    This class represents a separate thread for running processes,
    which need to read the stdout/stderr in real time.

    """
    # get videomass wx.App attribute
    get = wx.GetApp()
    LOGDIR = get.LOGdir
    CACHEDIR = get.CACHEdir
    FFMPEG_URL = get.FFMPEG_url
    FFMPEG_LOGLEV = get.FFMPEG_loglev
    FF_THREADS = get.FFthreads
    SUFFIX = '' if get.FILEsuffix == 'none' else get.FILEsuffix
    NOT_EXIST_MSG = _("Is 'ffmpeg' installed on your system?")
    # ---------------------------------------------------------------

    def __init__(self, varargs, duration, logname, timeseq):
        """
        Some attribute can be empty, this depend from conversion type.

        """
        self.stop_work_thread = False  # process terminate
        self.filelist = varargs[1]  # list of files (items)
        self.command = varargs[4]  # additional comand
        self.outputdir = varargs[3]  # output path
        self.extoutput = varargs[2]  # format (extension)
        self.duration = sum(duration)  # duration list
        self.countmax = len(varargs[1])  # length file list
        self.logname = logname  # title name of file log
        # need to escaping some chars
        self.ftext = os.path.join(Concat_Demuxer.CACHEDIR, 'tmp','flist.txt')
        escaped = [e.replace(r"'", r"'\'") for e in self.filelist]
        with open(self.ftext, 'w', encoding='utf8') as txt:
            txt.write('\n'.join(["file '%s'" % x for x in escaped]))

        Thread.__init__(self)

        self.start()

    def run(self):
        """
        Subprocess initialize thread.

        """
        basename = os.path.basename(self.filelist[0])  # nome file senza path
        filename = os.path.splitext(basename)[0]  # nome senza estensione
        source_ext = os.path.splitext(basename)[1].split('.')[1]  # ext
        outext = source_ext if not self.extoutput else self.extoutput

        cmd = ('"%s" %s -f concat -safe 0 -i "%s" -map 0:v? -map_chapters 0 '
               '-map 0:s? -map 0:a? -map_metadata 0 %s -c copy %s -y '
               '"%s/%s%s.%s"' % (Concat_Demuxer.FFMPEG_URL,
                                 Concat_Demuxer.FFMPEG_LOGLEV,
                                 self.ftext,
                                 self.command,
                                 Concat_Demuxer.FF_THREADS,
                                 self.outputdir,
                                 filename,
                                 Concat_Demuxer.SUFFIX,
                                 outext,
                                 ))
        count = '%s files to concat' % (self.countmax,)
        com = "%s\n%s" % (count, cmd)
        wx.CallAfter(pub.sendMessage,
                        "COUNT_EVT",
                        count=count,
                        duration=self.duration,
                        fname=", ".join(self.filelist),
                        end='',
                        )
        logWrite(com,
                    '',
                    self.logname,
                    Concat_Demuxer.LOGDIR,
                    )  # write n/n + command only

        if not platform.system() == 'Windows':
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
                    if self.stop_work_thread:
                        p.terminate()
                        break  # break second 'for' loop

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
                                Concat_Demuxer.LOGDIR,
                                )  # append exit error number
                else:  # ok
                    wx.CallAfter(pub.sendMessage,
                                    "COUNT_EVT",
                                    count='',
                                    duration='',
                                    fname='',
                                    end='ok'
                                    )
        except (OSError, FileNotFoundError) as err:
            e = "%s\n  %s" % (err, Concat_Demuxer.NOT_EXIST_MSG)
            wx.CallAfter(pub.sendMessage,
                            "COUNT_EVT",
                            count=e,
                            duration=0,
                            fname=", ".join(self.filelist),
                            end='error',
                            )

        if self.stop_work_thread:
            p.terminate()

        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT")
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
