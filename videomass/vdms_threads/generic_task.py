# -*- coding: UTF-8 -*-
"""
Name: generic_task.py
Purpose: Execute a generic task with FFmpeg
Compatibility: Python >= 3.11 (Unix, win32)
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Oct.31.2026
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

import subprocess
import sys
import time
from threading import Thread

import wx
from pubsub import pub

from videomass.vdms_io.make_filelog import tolog
from videomass.vdms_utils.utils import Popen


if sys.platform != "win32":
    import shlex


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

    STOP = (
        "WARNING: [VIDEOMASS]: STOP command received by signal "
        "event.\nTerminated process "
    )

    def __init__(self, args, procname="Unknown", logfile="logfile.log"):
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
        self.fatal = None  # fatal error I/O flag before `communicate`
        self.process = None  # process data set on context

        Thread.__init__(self)
        self.start()

    # ----------------------------------------------------------------#

    def run(self):
        """
        Start thread

        """
        outlist = []
        cmd = (
            f'"{self.appdata["ffmpeg_cmd"]}" '
            f"{self.appdata['ffmpeg-default-args']} "
            f"{self.appdata['ffmpeg_loglev']} "
            f"{self.args}"
        )
        tolog(
            f"INFO: VIDEOMASS TASK: {self.procname}\n"
            f"INFO: VIDEOMASS COMMAND: {cmd}",
            self.logfile,
            sep=True,
            wdate=True,
        )
        if sys.platform != "win32":
            cmd = shlex.split(cmd)
        try:
            with Popen(
                cmd,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                encoding=self.appdata["encoding"],
            ) as self.process:
                for line in self.process.stderr:
                    outlist.append(line)
                    if self.stop_work_thread:
                        if self.fatal:
                            return
                        output = self.process.communicate()[1]
                        self.process.wait()
                        tolog(
                            FFmpegGenericTaskOutLines.STOP
                            + f"with PID {self.process.pid}",
                            self.logfile,
                        )
                        self.status = "STOP"
                        break

                    if self.process.wait():
                        output = self.process.communicate()[1]
                        tolog(f"[FFMPEG] ERROR:\n{output}", self.logfile)
                        self.status = "ERROR"
                        break

        except (OSError, FileNotFoundError) as err:
            tolog(f"[VIDEOMASS]: ERROR: {err}", self.logfile)
            self.status = "ERROR"

        if not self.status:
            output = "".join(outlist)
            tolog(f"INFO: [FFMPEG] OUTPUT:\n{output}", self.logfile)

        wx.CallAfter(pub.sendMessage, "RESULT_EVT", status="")

    # ----------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the current process.
        This method has been revised and expanded to make the GUI
        more responsive and less dependent on the subprocess's output
        messages during `readlines` loops. This speeds up the process
        of closing the subprocess within the background thread while
        also improving error handling, ensuring the GUI remains completely
        free from potential blocks or freezes while waiting for termination
        outputs.

        `flush()` forces Python to immediately clear the write buffer
         and send the 'q' char to the pipe connected to FFmpeg.

        WARNING:
        How catch ValueError for tests:
            replaace `proc.stdin and not proc.stdin.closed` with:
                if proc.stdin:  # WARNING ALERT  remove after test
            place `proc.stdin.close()` on top `proc.stdin.write('q')`
                proc.stdin.close()  # WARNING ALERT remove after test
        """
        self.stop_work_thread = True

        try:
            proc = self.process if self.process.poll() is None else None
        except AttributeError:
            proc = None

        # Check if the process exists
        if proc is not None:
            try:
                # Verify that stdin is open and available before writing
                if proc.stdin and not proc.stdin.closed:
                    proc.stdin.write("q")  # stop ffmpeg
                    proc.stdin.flush()

            # Make sure the process isn't already finished
            except (
                BrokenPipeError,
                ValueError,
                AttributeError,
                OSError,
            ) as err:
                self.fatal = True
                msg = "CRASH_STOP: forcing FFmpeg to terminate"
                wx.CallAfter(
                    pub.sendMessage,
                    "COUNT_EVT",
                    count=f"{msg}: {err}",
                    duration=0,
                    end="ERROR",
                )
                tolog(f"[VIDEOMASS]: {msg}: {err}", self.logfile)

                # Force event end notification to unlock GUI
                time.sleep(0.5)
                wx.CallAfter(pub.sendMessage, "END_EVT", filetotrash=None)


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

    def __init__(self, args, procname="Unknown", logfile="logfile.log"):
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
        cmd = (
            f'"{self.appdata["ffmpeg_cmd"]}" '
            f"{self.appdata['ffmpeg-default-args']} "
            f"{self.appdata['ffmpeg_loglev']} "
            f"{self.args}"
        )
        tolog(
            f"INFO: VIDEOMASS TASK: {self.procname}\n"
            f"INFO: VIDEOMASS COMMAND: {cmd}",
            self.logfile,
            sep=True,
            wdate=True,
        )
        if sys.platform != "win32":
            cmd = shlex.split(cmd)
        try:
            with Popen(
                cmd,
                stderr=subprocess.PIPE,
                text=True,
                encoding=self.appdata["encoding"],
            ) as proc:
                output = proc.communicate()[1]
                tolog(f"INFO: [FFMPEG] OUTPUT:\n{output}", self.logfile)
                if proc.returncode:  # ffmpeg error
                    self.status = f"[FFMPEG] OUTPUT ERROR:\n{output}"

        except OSError as err:  # command not found
            self.status = f"[VIDEOMASS]: ERROR:\n{err}"

        if self.status:
            tolog(f"{self.status}", self.logfile)

        wx.CallAfter(pub.sendMessage, "RESULT_EVT", status="")
