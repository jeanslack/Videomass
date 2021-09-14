# -*- coding: UTF-8 -*-
"""
Name: YtdlExecDL.py
Porpose: long processing task with youtube-dl executable
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Aug.13.2021
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
import itertools
import subprocess
import platform
import wx
from pubsub import pub
if not platform.system() == 'Windows':
    import shlex


def logwrite(cmd, sterr, logname, logdir):
    """
    writes youtube-dl commands and status error during
    threads below
    """
    if sterr:
        apnd = "...%s\n\n" % (sterr)
    else:
        apnd = "%s\n\n" % (cmd)

    with open(os.path.join(logdir, logname), "a", encoding='utf8') as log:
        log.write(apnd)


class YtdlExecDL(Thread):
    """
    YtdlExecDL represents a separate thread for running
    youtube-dl executable with subprocess class to download
    media and capture its stdout/stderr output in real time .

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    LOGDIR = get.appset['logdir']
    FFMPEG_URL = get.appset['ffmpeg_bin']
    EXECYDL = get.appset['EXECYDL']
    APPTYPE = get.appset['app']

    if get.appset['playlistsubfolder'] == 'true':
        SUBDIR = '%(uploader)s/%(playlist_title)s/%(playlist_index)s - '
    else:
        SUBDIR = ''

    if not platform.system() == 'Windows':
        LINE_MSG = _('Unrecognized error')
    else:
        if os.path.isfile(EXECYDL):
            LINE_MSG = ('\nERROR: MSVCR100.dll is missing!\nPlease, install '
                        '"Microsoft Visual C++ 2010 Service Pack 1 '
                        'Redistributable Package (x86)"\n'
                        'which can be found at:\n'
                        'https://download.microsoft.com/download/1/6/5/165255'
                        'E7-1014-4D0A-B094-B6A430A6BFFC/vcredist_x86.exe\n')
        else:
            LINE_MSG = _('Unrecognized error')
    # -----------------------------------------------------------------------#

    def __init__(self, varargs, logname):
        """
        Attributes defined here:
        self.stop_work_thread:  process terminate value
        self.args['urls']:          urls list
        self.args['opt']:           option strings to adding
        self.args['outtmpl']:       options template to renaming on pathname
        self.args['code']:          Format Code, else empty string ''
        self.args['outputdir']:     pathname destination
        self.count:         increases with the progressive loops
        self.countmax:      length of self.args['urls']
        self.logname:       title log name for logging

        """
        self.args = {'urls': varargs[1],
                     'opt': varargs[4][0],
                     'outtmpl': varargs[4][1],
                     'nooverwrites': varargs[4][2],
                     'restrictfn': varargs[4][3],
                     'pl_items': varargs[4][4],
                     'code': varargs[6],
                     'outputdir': varargs[3]
                     }
        self.stop_work_thread = False  # process terminate
        self.count = 0
        self.countmax = len(varargs[1])
        self.logname = logname

        if (platform.system() == 'Windows' or
                YtdlExecDL.APPTYPE == 'appimage'):
            self.ssl = '--no-check-certificate'

        else:
            self.ssl = ''

        Thread.__init__(self)
        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.

        """
        for url, code in itertools.zip_longest(self.args['urls'],
                                               self.args['code'],
                                               fillvalue='',
                                               ):
            if 'playlist' in url or '--yes-playlist' in self.args['opt']:
                outtmpl = YtdlExecDL.SUBDIR + self.args['outtmpl']
            else:
                outtmpl = self.args['outtmpl']

            if self.args['pl_items'].get(url):
                pl_items = ('--playlist-items %s ' %
                            self.args['pl_items'].get(url))
            else:
                pl_items = ''

            format_code = '--format %s' % (code) if code else ''
            cmd = ('"{0}" {1} --newline --ignore-errors {8} -o '
                   '"{2}/{3}" {4} {5} {10} --ignore-config {9} "{6}" '
                   '--ffmpeg-location "{7}"'.format(YtdlExecDL.EXECYDL,
                                                    self.ssl,
                                                    self.args['outputdir'],
                                                    outtmpl,
                                                    format_code,
                                                    self.args['opt'],
                                                    url,
                                                    YtdlExecDL.FFMPEG_URL,
                                                    self.args['nooverwrites'],
                                                    self.args['restrictfn'],
                                                    pl_items,
                                                    ))
            self.count += 1
            count = 'URL %s/%s' % (self.count, self.countmax)
            dest = 'Destination:  "%s"' % self.args['outputdir']
            com = ('%s\nSource: %s\n%s\n\n'
                   '[COMMAND]\n%s' % (count, url, dest, cmd))

            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=count,
                         fsource='Source: %s' % url,
                         destination=dest,
                         duration=100,
                         end='',
                         )
            logwrite(com,
                     '',
                     self.logname,
                     YtdlExecDL.LOGDIR,
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
                                      startupinfo=info,) as proc:

                    for line in proc.stdout:
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_YDL_EXECUTABLE_EVT",
                                     output=line,
                                     duration=100,
                                     status=0,
                                     )
                        if self.stop_work_thread:  # break second 'for' loop
                            proc.terminate()
                            break

                    if proc.wait():  # error
                        if 'line' not in locals():
                            line = YtdlExecDL.LINE_MSG
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_YDL_EXECUTABLE_EVT",
                                     output=line,
                                     duration=100,
                                     status=proc.wait(),
                                     )
                        logwrite('',
                                 "Exit status: %s" % proc.wait(),
                                 self.logname,
                                 YtdlExecDL.LOGDIR,
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
                excepterr = "%s" % err
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count=excepterr,
                             fsource='',
                             destination='',
                             duration=0,
                             end='error',
                             )
                break

            if self.stop_work_thread:  # break first 'for' loop
                proc.terminate()
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


class YtdlExecEI(Thread):
    """
    YtdlExecEI it is a separate thread to run youtube-dl executable
    with subprocess class to get 'Format code' data and exit status
    from stdout/stderr output .

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    EXECYDL = get.appset['EXECYDL']
    APPTYPE = get.appset['app']

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
        self.url:          urls list
        """
        self.url = url
        self.status = None
        self.data = None

        if (platform.system() == 'Windows' or
                YtdlExecEI.APPTYPE == 'appimage'):
            self.ssl = '--no-check-certificate'
        else:
            self.ssl = ''

        Thread.__init__(self)
        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.

        """
        cmd = ('"{0}" {1} --newline --ignore-errors --ignore-config '
               '--restrict-filenames -F "{2}"'.format(YtdlExecEI.EXECYDL,
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
            with subprocess.Popen(cmd,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True,
                                  startupinfo=info,
                                  ) as proc:

                out = proc.communicate()

                if proc.returncode:  # if returncode == 1
                    if (not out[0] and not out[1] and
                            platform.system() == 'Windows'):
                        self.status = YtdlExecEI.LINE_MSG, 'error'
                    else:
                        self.status = (out[0], 'error')
                else:
                    self.status = (out[0], out[1])

        except OSError as oserr:  # executable do not exist
            self.status = ('%s' % oserr, 'error')

        self.data = self.status

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
