# -*- coding: UTF-8 -*-
"""
Name: generic_task.py
Porpose: Execute a generic task with FFmpeg
Compatibility: Python3 (Unix, Windows)
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: May.23.2024
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


def logwrite(logfile, cmd):
    """
    write ffmpeg command log
    """
    with open(logfile, "a", encoding='utf-8') as log:
        log.write(f"{cmd}\n")
# ----------------------------------------------------------------#


def logerror(logfile, output):
    """
    write ffmpeg errors
    """
    with open(logfile, "a", encoding='utf-8') as logerr:
        logerr.write(f"\n[FFMPEG] generic_task ERRORS:\n{output}\n")
# ----------------------------------------------------------------#


class FFmpegGenericTaskOutLines(Thread):
    """
    Run a generic task using FFmpeg sub-process as a separate thread.
    Unlike FFmpegGenericTask, this class also provides a control
    interface capable of communicating the stop of the command
    via PIPE on the subprocess's standard input.
    Using the main thread you can call the stop() method of this
    sparated thread which will send the stop signal to ffmpeg's
    standard input.

    USAGE:
        >>> thread = FFmpegGenericTaskOutLines(args)
        >>> thread.join()
        >>> error = thread.status
        >>> if error:
        >>>     error

    Raise: `OSError` if not FFmpeg
    Return: None

    """
    ERROR = 'Please, see "generic_task.log" file for error details.'
    STOP = '[Videomass]: STOP command received.'

    def __init__(self, args, procname='Unknown', logfile='logfile.log'):
        """
        Attributes defined here:

        self.args: a string containing only the command arguments
                   of FFmpeg, not `ffmpeg` command nor loglevel
                   nor ffmpeg-default-args.
        self.procname: any task name for identification.
        self.logfile: filename to redirect text string log
        self.status: If the exit status is true (which can be an
                     exception or error message given by returncode)
                     it must be handled appropriately, in the other
                     case it is None.
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
        Start thread

        """
        outlist = []
        cmd = (f'"{self.appdata["ffmpeg_cmd"]}" '
               f'{self.appdata["ffmpeg-default-args"]} '
               f'{self.appdata["ffmpeg_loglev"]} '
               f'{self.args}'
               )
        logwrite(self.logfile, f'From: {self.procname}\n{cmd}\n')

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
            logerror(self.logfile, output)
        else:
            output = ''.join(outlist)
            logwrite(self.logfile, f'[FFMPEG]:\n{output}')

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
    # ----------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True


class FFmpegGenericTask(Thread):
    """
    Run a simple generic task using FFmpeg subprocess as
    a separate thread. This class does not provide a control
    interface to read progress output in realtime, so you need
    to wait for the end of the subprocess to get the result
    about the status error. See also FFmpegGenericTaskOutLines.

    USAGE:
        >>> thread = FFmpegGenericTask(args)
        >>> thread.join()
        >>> error = thread.status
        >>> if error:
        >>>     error

    Raise: `OSError` if not FFmpeg
    Return: None

    """
    def __init__(self, args, procname='Unknown', logfile='logfile.log'):
        """
        Attributes defined here:

        self.args: a string containing only the command arguments
                   of FFmpeg, not `ffmpeg` command nor loglevel
                   nor ffmpeg-default-args.
        self.procname: any task name for identification.
        self.logfile: filename to redirect text string log
        self.status: If the exit status is true (which can be an
                     exception or error message given by returncode)
                     it must be handled appropriately, in the other
                     case it is None.
        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.logfile = logfile
        self.procname = procname
        self.args = args
        self.status = None

        Thread.__init__(self)
        self.start()
    # ----------------------------------------------------------------#

    def run(self):
        """
        Start thread

        """
        cmd = (f'"{self.appdata["ffmpeg_cmd"]}" '
               f'{self.appdata["ffmpeg-default-args"]} '
               f'{self.appdata["ffmpeg_loglev"]} '
               f'{self.args}'
               )
        logwrite(self.logfile, f'From: {self.procname}\n{cmd}\n')

        if not platform.system() == 'Windows':
            cmd = shlex.split(cmd)
        try:
            with Popen(cmd,
                       stderr=subprocess.PIPE,
                       universal_newlines=True,
                       encoding=self.appdata["encoding"],
                       ) as proc:
                output = proc.communicate()[1]
                logwrite(self.logfile, f'[FFMPEG]:\n{output}')
                if proc.returncode:  # ffmpeg error
                    self.status = output

        except OSError as err:  # command not found
            self.status = err

        if self.status:
            logerror(self.logfile, self.status)

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
