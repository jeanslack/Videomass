# -*- coding: UTF-8 -*-
"""
Name: one_pass.py
Porpose: FFmpeg long processing task on one pass conversion
Compatibility: Python3, wxPython4 Phoenix
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


class ConcatDemuxer(Thread):
    """
    This class represents a separate thread for running processes,
    which need to read the stdout/stderr in real time.

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    appdata = get.appset
    CACHEDIR = appdata['cachedir']
    SUFFIX = '' if appdata['filesuffix'] == 'none' else appdata['filesuffix']
    NOT_EXIST_MSG = _("Is 'ffmpeg' installed on your system?")
    # ---------------------------------------------------------------

    def __init__(self, varargs, duration, logname):
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
        self.ftext = os.path.join(ConcatDemuxer.CACHEDIR, 'tmp', 'flist.txt')
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
        outputfile = os.path.join(self.outputdir,
                                  '%s%s.%s' % (filename,
                                               ConcatDemuxer.SUFFIX,
                                               outext)
                                  )
        cmd = ('"%s" %s -f concat -safe 0 -i "%s" -map 0:v? -map_chapters 0 '
               '-map 0:s? -map 0:a? -map_metadata 0 %s -c copy %s -y '
               '"%s"' % (ConcatDemuxer.appdata['ffmpeg_bin'],
                         ConcatDemuxer.appdata['ffmpegloglev'],
                         self.ftext,
                         self.command,
                         ConcatDemuxer.appdata['ffthreads'],
                         outputfile,
                         ))
        count = '%s Files to concat' % (self.countmax,)
        com = ('%s\nSource: "%s"\nDestination: "%s"\n\n'
               '[COMMAND]:\n%s' % (count, self.filelist, outputfile, cmd))

        wx.CallAfter(pub.sendMessage,
                     "COUNT_EVT",
                     count=count,
                     fsource='Source:  %s' % self.filelist,
                     destination='Destination:  "%s"' % outputfile,
                     duration=self.duration,
                     # fname=", ".join(self.filelist),
                     end='',
                     )
        logwrite(com,
                 '',
                 self.logname,
                 ConcatDemuxer.appdata['logdir'],
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
                                  startupinfo=info,) as proc:
                for line in proc.stderr:
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output=line,
                                 duration=self.duration,
                                 status=0,
                                 )
                    if self.stop_work_thread:
                        proc.terminate()
                        break  # break second 'for' loop

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
                             ConcatDemuxer.appdata['logdir'],
                             )  # append exit error number
                else:  # ok
                    wx.CallAfter(pub.sendMessage,
                                 "COUNT_EVT",
                                 count='',
                                 fsource='',
                                 destination='',
                                 duration='',
                                 end='ok'
                                 )
        except (OSError, FileNotFoundError) as err:
            excepterr = "%s\n  %s" % (err, ConcatDemuxer.NOT_EXIST_MSG)
            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=excepterr,
                         fsource='',
                         destination='',
                         duration=0,
                         end='error',
                         )

        if self.stop_work_thread:
            proc.terminate()

        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT")
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
