# -*- coding: UTF-8 -*-
"""
Name: generic_task.py
Purpose: Execute a generic task with FFmpeg
Compatibility: Python >= 3.11 (Unix, win32)
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Oct.31.2026
Code checker: flake8, pylint, ruff

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
from threading import Thread

import wx
from pubsub import pub

from videomass.vdms_io.make_filelog import tolog
from videomass.vdms_utils.thread_utils import BaseVideomassThread


if sys.platform != "win32":
    import shlex


class FFmpegGenericTaskOutLines(BaseVideomassThread):
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

        If your interface allows it, you can stop the process with:
        >>> self.thread.stop()

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
        """
        super().__init__(logfile=logfile)

        get = wx.GetApp()
        self.appdata = get.appset
        self.procname = procname
        self.args = args

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
        with open(self.logfile, "a", encoding="utf-8") as logfile:
            tolog(
                f"INFO: VIDEOMASS TASK: {self.procname}\n"
                f"INFO: VIDEOMASS COMMAND: {cmd}",
                logfile,
                sep=True,
                wdate=True,
                openf=False,
            )
            cmd = shlex.split(cmd) if sys.platform != "win32" else cmd
            try:
                with subprocess.Popen(
                    cmd,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    encoding=self.appdata["encoding"],
                    errors="replace",
                    creationflags=self.creationflags,
                ) as self.process:
                    for line in self.process.stderr:
                        tolog(
                            line,
                            logfile,
                            openf=False,
                        )
                        if self.stop_work_thread:
                            if self.fatal:
                                return
                            output = self.process.communicate()[1]
                            tolog(
                                FFmpegGenericTaskOutLines.STOP
                                + f"with PID {self.process.pid}",
                                logfile,
                                openf=False,
                            )
                            break

                        if self.process.poll():
                            output = self.process.communicate()[1]
                            tolog(
                                f"[FFMPEG] ERROR:\n{output}",
                                logfile,
                                openf=False,
                            )
                            break

            except (OSError, FileNotFoundError) as err:
                tolog(f"[VIDEOMASS]: ERROR: {err}", logfile, openf=False)

        wx.CallAfter(pub.sendMessage, "RESULT_EVT", status="")


class FFmpegGenericTask(Thread):
    """
    Run a simple generic task using FFmpeg subprocess as
    a separate thread. This class does not provide a control
    interface to read progress output in realtime, so you need
    to wait for the end of the subprocess to get the result
    about the status error. See also FFmpegGenericTaskOutLines.

    USAGE:
        >>> thread = FFmpegGenericTask(args)
        >>> thread.start()
        >>> error = thread.status
        >>> if error:
        >>>     error

        If your interface allows it, you can stop the process using:
        >>> self.thread.stop()

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
        self.stop_work_thread = None
        self.proc = None
        self.creationflags = (
            subprocess.CREATE_NO_WINDOW
            if self.appdata["ostype"] == "Windows"
            else 0
        )

        Thread.__init__(self)

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
        cmd = shlex.split(cmd) if sys.platform != "win32" else cmd
        try:
            with subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                text=True,
                encoding=self.appdata["encoding"],
                errors="replace",
                creationflags=self.creationflags,
            ) as self.proc:
                output = self.proc.communicate()[1]
                tolog(f"INFO: [FFMPEG] OUTPUT:\n{output}", self.logfile)

                exit_code = self.proc.returncode
                if exit_code:  # ffmpeg error
                    if self.stop_work_thread:
                        self.status = "STOP"
                    else:
                        self.status = f"[FFMPEG]: (Exit Code): {exit_code}"

        except OSError as err:  # command not found
            self.status = f"[VIDEOMASS]: ERROR:\n{err}"
            tolog(f"{self.status}", self.logfile)

        wx.CallAfter(pub.sendMessage, "RESULT_EVT", status="")

    # ----------------------------------------------------------------#

    def stop(self):
        """
        Terminate the running FFmpeg subprocess immediately.
        """
        self.stop_work_thread = True
        if self.proc is not None:
            try:
                self.proc.terminate()
            except OSError:
                pass
