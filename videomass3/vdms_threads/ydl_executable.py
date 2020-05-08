# -*- coding: UTF-8 -*-

#########################################################
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
import os
from threading import Thread
import time
from pubsub import pub

# get videomass wx.App attribute
get = wx.GetApp()
OS = get.OS
LOGDIR = get.LOGdir
FFMPEG_URL = get.FFMPEG_url
execYdl = get.execYdl

if not OS == 'Windows':
    import shlex
    linemsg = _('Unrecognized error')
else:
    if os.path.isfile(execYdl):
        linemsg = (_('\nRequires MSVCR100.dll\nTo resolve this problem install: '
                    'Microsoft Visual C++ 2010 Redistributable Package (x86)'))
    else:
        linemsg = _('Unrecognized error')

executable_not_found_msg = _("Is 'youtube-dl' installed on your system?")


def logWrite(cmd, sterr, logname):
    """
    writes youtube-dl commands and status error during
    threads below
    """
    if sterr:
        apnd = "...%s\n\n" % (sterr)
    else:
        apnd = "%s\n\n" % (cmd)

    with open(os.path.join(LOGDIR, logname), "a") as log:
        log.write(apnd)


class Ydl_DL_Exec(Thread):
    """
    Ydl_DL_Exec represents a separate thread for running
    youtube-dl executable with subprocess class and capturing its
    stdout/stderr output in real time .
    """
    def __init__(self, varargs, logname):
        """
        Attributes defined here:
        self.stop_work_thread:  process terminate value
        self.urls:          urls list
        self.opt:           option strings to adding
        self.outtmpl:       options template to renaming on pathname
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
        self.outputdir = varargs[3]
        self.count = 0
        self.countmax = len(varargs[1])
        self.logname = logname

        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        """
        ssl = '--no-check-certificate' if OS == 'Windows' else ''

        for url in self.urls:
            cmd = ('"{0}" {1} --newline --ignore-errors -o '
                   '"{2}/{3}" {4} --ignore-config --restrict-filenames '
                   '"{5}" --ffmpeg-location "{6}"'.format(execYdl,
                                                          ssl,
                                                          self.outputdir,
                                                          self.outtmpl,
                                                          self.opt,
                                                          url,
                                                          FFMPEG_URL,
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
            logWrite(com, '', self.logname)  # write n/n + command only

            if not OS == 'Windows':
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
                            line = linemsg
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_YDL_EXECUTABLE_EVT",
                                     output=line,
                                     duration=100,
                                     status=p.wait(),
                                     )
                        logWrite('',
                                 "Exit status: %s" % p.wait(),
                                 self.logname
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
                e = "%s\n  %s" % (err, executable_not_found_msg)
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
    with subprocess class to get -at the end of the process- 'Format
    code' data and exit status from stdout/stderr output .
    """
    def __init__(self, url):
        """
        self.urls:          urls list
        """
        Thread.__init__(self)
        """initialize"""
        self.url = url
        self.status = None
        self.data = None

        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        """
        ssl = '--no-check-certificate' if OS == 'Windows' else ''
        cmd = ('"{0}" {1} --newline --ignore-errors --ignore-config '
               '--restrict-filenames -F "{2}"'.format(execYdl,
                                                      ssl,
                                                      self.url))
        if not OS == 'Windows':
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
                if not out[0] and not out[1] and OS == 'Windows':
                    self.status = linemsg, 'error'
                else:
                    self.status = (out[0], 'error')
            else:
                self.status = (out[0], out[1])

        self.data = self.status

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
