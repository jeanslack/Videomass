# -*- coding: UTF-8 -*-
# Name: Ydl_DL_Exec.py
# Porpose: long processing task with youtube-dl executable
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.19.2020 *PEP8 compatible*
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
import sys
from threading import Thread
import time
from pubsub import pub


def logWrite(cmd, sterr, logname, logdir):
    """
    writes youtube-dl commands and status error during
    threads below
    """
    if sterr:
        apnd = "...%s\n\n" % (sterr)
    else:
        apnd = "%s\n\n" % (cmd)

    with open(os.path.join(logdir, logname), "a") as log:
        log.write(apnd)


class Ydl_DL_Exec(Thread):
    """
    Ydl_DL_Exec represents a separate thread for running
    youtube-dl executable with subprocess class and capturing its
    stdout/stderr output in real time .

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    LOGDIR = get.LOGdir
    FFMPEG_URL = get.FFMPEG_url
    EXECYDL = get.execYdl

    if not platform.system() == 'Windows':
        LINE_MSG = _('Unrecognized error')
    else:
        if os.path.isfile(EXECYDL):
            LINE_MSG = (_('\nRequires MSVCR100.dll\nTo resolve this problem '
                          'install: Microsoft Visual C++ 2010 Redistributable '
                          'Package (x86)'))
        else:
            LINE_MSG = _('Unrecognized error')

    EXECUTABLE_NOT_FOUND_MSG = _("Is 'youtube-dl' installed on your system?")
    # -----------------------------------------------------------------------#

    def __init__(self, varargs, logname):
        """
        Attributes defined here:
        self.stop_work_thread:  process terminate value
        self.urls:          urls list
        self.opt:           option strings to adding
        self.outtmpl:       options template to renaming on pathname
        self.code:          Format Code, else empty string ''
        self.outputdir:     pathname destination
        self.count:         increases with the progressive account elements
        self.countmax:      length of self.urls
        self.logname:       title log name for logging

        """
        Thread.__init__(self)
        """initialize"""
        self.stop_work_thread = False  # process terminate
        self.urls = varargs[1]
        self.opt = varargs[4][0]
        self.outtmpl = varargs[4][1]
        self.code = varargs[6]
        self.outputdir = varargs[3]
        self.count = 0
        self.countmax = len(varargs[1])
        self.logname = logname
        if platform.system() == 'Windows' or '/tmp/.mount_' \
           in sys.executable or os.path.exists(os.getcwd() + '/AppRun'):
            self.ssl = '--no-check-certificate'
        else:
            self.ssl = ''

        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.

        """
        for url, code in itertools.zip_longest(self.urls,
                                               self.code,
                                               fillvalue='',
                                               ):
            format_code = '--format %s' % (code) if code else ''
            cmd = ('"{0}" {1} --newline --ignore-errors -o '
                   '"{2}/{3}" {4} {5} --ignore-config --restrict-filenames '
                   '"{6}" --ffmpeg-location "{7}"'.format(
                                                        Ydl_DL_Exec.EXECYDL,
                                                        self.ssl,
                                                        self.outputdir,
                                                        self.outtmpl,
                                                        format_code,
                                                        self.opt,
                                                        url,
                                                        Ydl_DL_Exec.FFMPEG_URL,
                                                        ))
            self.count += 1
            count = 'URL %s/%s' % (self.count, self.countmax,)
            com = "%s\n%s" % (count, cmd)
            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=count,
                         duration=100,
                         fname=url,
                         end='',
                         )
            logWrite(com,
                     '',
                     self.logname,
                     Ydl_DL_Exec.LOGDIR,
                     )  # write n/n + command only

            if not platform.system() == 'Windows':
                cmd = shlex.split(cmd)
                info = None
            else:
                # Hide subprocess window on MS Windows
                info = subprocess.STARTUPINFO()
                info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            try:
                with subprocess.Popen(cmd,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,
                                      bufsize=1,
                                      universal_newlines=True,
                                      startupinfo=info,) as p:

                    for line in p.stdout:
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_YDL_EXECUTABLE_EVT",
                                     output=line,
                                     duration=100,
                                     status=0,
                                     )
                        if self.stop_work_thread:  # break second 'for' loop
                            p.terminate()
                            break

                    if p.wait():  # error
                        if 'line' not in locals():
                            line = Ydl_DL_Exec.LINE_MSG
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_YDL_EXECUTABLE_EVT",
                                     output=line,
                                     duration=100,
                                     status=p.wait(),
                                     )
                        logWrite('',
                                 "Exit status: %s" % p.wait(),
                                 self.logname,
                                 Ydl_DL_Exec.LOGDIR,
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
                e = "%s\n  %s" % (err, Ydl_DL_Exec.EXECUTABLE_NOT_FOUND_MSG)
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count=e,
                             duration=0,
                             fname=url,
                             end='error',
                             )
                break

            if self.stop_work_thread:  # break first 'for' loop
                p.terminate()
                break

        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT")
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
# ------------------------------------------------------------------------#


class Ydl_EI_Exec(Thread):
    """
    Ydl_EI_Exec it is a separate thread to run youtube-dl executable
    with subprocess class to get (at the end of the process) 'Format
    code' data and exit status from stdout/stderr output .

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    EXECYDL = get.execYdl
    if not platform.system() == 'Windows':
        LINE_MSG = _('Unrecognized error')
    else:
        if os.path.isfile(EXECYDL):
            LINE_MSG = (_('\nRequires MSVCR100.dll\nTo resolve this problem '
                          'install: Microsoft Visual C++ 2010 Redistributable '
                          'Package (x86)'))
        else:
            LINE_MSG = _('Unrecognized error')
    # ---------------------------------------------------------------#

    def __init__(self, url):
        """
        self.urls:          urls list
        """
        Thread.__init__(self)
        """initialize"""
        self.url = url
        self.status = None
        self.data = None
        if platform.system() == 'Windows' or '/tmp/.mount_' \
           in sys.executable or os.path.exists(os.getcwd() + '/AppRun'):
            self.ssl = '--no-check-certificate'
        else:
            self.ssl = ''

        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.

        """
        cmd = ('"{0}" {1} --newline --ignore-errors --ignore-config '
               '--restrict-filenames -F "{2}"'.format(Ydl_EI_Exec.EXECYDL,
                                                      self.ssl,
                                                      self.url))
        if not platform.system() == 'Windows':
            cmd = shlex.split(cmd)
            info = None
        else:
            # Hide subprocess window on MS Windows
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        try:
            p = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True,
                                 startupinfo=info,
                                 )
            out = p.communicate()

        except OSError as oserr:  # executable do not exist
            self.status = ('%s' % oserr, 'error')
        else:
            if p.returncode:  # if returncode == 1
                if not out[0] and not out[1] and platform.system() == 'Windows':
                    self.status = Ydl_EI_Exec.LINE_MSG, 'error'
                else:
                    self.status = (out[0], 'error')
            else:
                self.status = (out[0], out[1])

        self.data = self.status

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
