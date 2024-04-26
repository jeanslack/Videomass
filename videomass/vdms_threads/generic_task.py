# -*- coding: UTF-8 -*-
"""
Name: generic_task.py
Porpose: Execute a generic task with FFmpeg
Compatibility: Python3 (Unix, Windows)
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Apr.23.2024
Code checker: flake8, pylint

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
from threading import Thread
import platform
import subprocess
import wx
from pubsub import pub
from videomass.vdms_utils.utils import Popen
if not platform.system() == 'Windows':
    import shlex


class FFmpegGenericTask(Thread):
    """
    Run a generic task with FFmpeg as a separate thread.
    This class does not redirect any progress output information
    for debugging, however you can get the exit status message.

    USAGE:
        >>> thread = FFmpegGenericTask(args)
        >>> thread.join()
        >>> error = thread.status
        >>> if error:
        >>>     error

    Raise: `OSError` if not FFmpeg
    Return: None

    """
    ERROR = 'Please, see "generic_task.log" file for error details.'
    STOP = '[Videomass]: STOP command received. Interrupting !'

    def __init__(self, args, procname='Unknown', logfile='logfile.log'):
        """
        Attributes defined here:

        self.args, a string containing the command args
        of FFmpeg, excluding the command itself `ffmpeg`

        self.status, If the exit status is true (which can be an
        exception or error message given by returncode) it must be
        handled appropriately, in the other case it is None.

        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.stop_work_thread = False  # process terminate
        self.logfile = logfile
        self.procname = procname
        self.args = args
        self.status = None

        Thread.__init__(self)
        self.start()
    # ----------------------------------------------------------------#

    def run(self):
        """
        Get and redirect output errors on p.returncode instance and
        OSError exception. Otherwise the getted output is None

        """
        outlist = []
        cmd = (f'"{self.appdata["ffmpeg_cmd"]}" '
               f'{self.appdata["ffmpeg-default-args"]} '
               f'{self.appdata["ffmpeg_loglev"]} '
               f'{self.args}'
               )
        self.logwrite(f'From: {self.procname}\n{cmd}\n')

        if not platform.system() == 'Windows':
            cmd = shlex.split(cmd)
        try:
            with Popen(cmd,
                       stderr=subprocess.PIPE,
                       stdin=subprocess.PIPE,
                       universal_newlines=True,
                       encoding=self.appdata["encoding"],
                       ) as proc:
                for line in proc.stderr:
                    outlist.append(line)
                    if self.stop_work_thread:
                        proc.stdin.write('q')  # stop ffmpeg
                        output = proc.communicate()[1]
                        proc.wait()
                        self.status = FFmpegGenericTask.STOP
                        break

                    if proc.wait():
                        output = proc.communicate()[1]
                        self.status = FFmpegGenericTask.ERROR
                        break

        except (OSError, FileNotFoundError) as err:
            self.status = err
            output = err

        if self.status:
            self.logerror(output)
        else:
            output = ''.join(outlist)
            self.logwrite(f'[FFMPEG]:\n{output}')

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
    # ----------------------------------------------------------------#

    def logwrite(self, cmd):
        """
        write ffmpeg command log
        """
        with open(self.logfile, "a", encoding='utf-8') as log:
            log.write(f"{cmd}\n")
    # ----------------------------------------------------------------#

    def logerror(self, output):
        """
        write ffmpeg volumedected errors
        """
        with open(self.logfile, "a", encoding='utf-8') as logerr:
            logerr.write(f"\n[FFMPEG] generic_task "
                         f"ERRORS:\n{output}\n")
    # ----------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
