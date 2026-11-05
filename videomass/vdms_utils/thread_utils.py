# -*- coding: UTF-8 -*-
"""
Name: thread_utils.py
Purpose: Encapsulate inheritable code to the subclasses
Compatibility: Python >= 3.11, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.04.2026
Code checker: flake8, pylint, Ruff

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
import threading
import time

import wx
from pubsub import pub

from videomass.vdms_io.make_filelog import tolog


class BaseVideomassThread(threading.Thread):
    """
    This class encapsulates inheritable code for extending
    functionality common to multiple family members.
    In particular, it offers an interface for the instant
    termination of running processes using ffmpeg.
    """

    def __init__(self, logfile=None):
        """Base class for common working threads."""

        super().__init__()

        self.logfile = logfile  # log path/filename
        self.process = None  # process data set on context
        self.stop_work_thread = False  # set stop ffmpeg
        self.fatal = None  # fatal error I/O flag before `communicate`

        self.creationflags = (
            subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )

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
                    proc.stdin.write("q")  # quit/stop ffmpeg
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
