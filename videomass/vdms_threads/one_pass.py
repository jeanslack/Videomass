# -*- coding: UTF-8 -*-
"""
Name: one_pass.py
Porpose: FFmpeg long processing task on one pass conversion
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Oct.18.2021
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


def logwrite(cmd, stderr, logname, logdir):
    """
    writes ffmpeg commands and status error during threads below
    """
    if stderr:
        apnd = f"...{stderr}\n\n"
    else:
        apnd = f"{cmd}\n\n"

    with open(os.path.join(logdir, logname), "a", encoding='utf8') as log:
        log.write(apnd)

# ------------------------------ THREADS -------------------------------#


class OnePass(Thread):
    """
    This class represents a separate thread for running processes,
    which need to read the stdout/stderr in real time.

    NOTE MS Windows:

    subprocess.STARTUPINFO()

    https://stackoverflow.com/questions/1813872/running-
    a-process-in-pythonw-with-popen-without-a-console?lq=1>

    NOTE capturing output in real-time (Windows, Unix):

    https://stackoverflow.com/questions/1388753/how-to-get-output-
    from-subprocess-popen-proc-stdout-readline-blocks-no-dat?rq=1

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    appdata = get.appset
    SUFFIX = '' if appdata['filesuffix'] == 'none' else appdata['filesuffix']
    NOT_EXIST_MSG = _("Is 'ffmpeg' installed on your system?")
    # ---------------------------------------------------------------

    def __init__(self, varargs, duration, logname, timeseq):
        """
        Some attribute can be empty, this depend from conversion type.
        If the format/container is not changed on a conversion, the
        'extoutput' attribute will have an empty value.
        The 'volume' attribute may also have an empty value, but it will
        no affect as well.
        """
        self.stop_work_thread = False  # process terminate
        self.filelist = varargs[1]  # list of files (items)
        self.command = varargs[4]  # comand set on single pass
        self.outputdir = varargs[3]  # output path
        self.extoutput = varargs[2]  # format (extension)
        self.duration = duration  # duration list
        self.volume = varargs[7]  # (lista norm.)se non richiesto rimane None
        self.count = 0  # count first for loop
        self.countmax = len(varargs[1])  # length file list
        self.logname = logname  # title name of file log
        self.time_seq = timeseq  # a time segment

        Thread.__init__(self)

        self.start()  # start the thread

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
            filename = os.path.splitext(basename)[0]  # nome senza estensione
            source_ext = os.path.splitext(basename)[1].split('.')[1]  # ext
            outext = source_ext if not self.extoutput else self.extoutput
            outputfile = os.path.join(folders, f'{filename}{OnePass.SUFFIX}'
                                               f'.{outext}')

            cmd = (f'"{OnePass.appdata["ffmpeg_bin"]}" {self.time_seq} '
                   f'{OnePass.appdata["ffmpegloglev"]} -i "{files}" '
                   f'{self.command} {volume} {OnePass.appdata["ffthreads"]} '
                   f'-y "{outputfile}"')

            self.count += 1

            count = f'File {self.count}/{self.countmax}'
            com = (f'{count}\nSource: "{files}"\nDestination: "{outputfile}"'
                   f'\n\n[COMMAND]:\n{cmd}')

            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=count,
                         fsource=f'Source:  "{files}"',
                         destination=f'Destination:  "{outputfile}"',
                         duration=duration,
                         end='',
                         )
            logwrite(com,
                     '',
                     self.logname,
                     OnePass.appdata['logdir'],
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
                                     duration=duration,
                                     status=0,
                                     )
                        if self.stop_work_thread:
                            proc.terminate()
                            break  # break second 'for' loop

                    if proc.wait():  # error
                        print('proc punto wait')
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output='',
                                     duration=duration,
                                     status=proc.wait(),
                                     )
                        logwrite('',
                                 f"Exit status: {proc.wait()}",
                                 self.logname,
                                 OnePass.appdata['logdir'],
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
                excepterr = f"{err}\n  {OnePass.NOT_EXIST_MSG}"
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count=excepterr,
                             fsource='',
                             destination='',
                             duration=0,
                             end='error',
                             )
                break

            if self.stop_work_thread:
                proc.terminate()
                break  # break second 'for' loop

        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT")
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
