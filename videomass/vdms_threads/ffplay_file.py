# -*- coding: UTF-8 -*-

"""
Name: ffplay_file.py
Purpose: playback media file via ffplay
Compatibility: Python >= 3.11, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.03.2026
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

import os
import shlex
import subprocess
from threading import Lock, Thread
from typing import ClassVar

import wx
from pubsub import pub

from videomass.vdms_io.io_tools import show_msg_notify
from videomass.vdms_io.make_filelog import make_log_template, tolog


class BaseFilePlay(Thread):
    """
    Base class for the shared management of playback using ffplay.

    NOTE: The attributes defined here keep track of all active
          processes and are shared by all instances of this class.
    """

    _active_processes: ClassVar[set] = set()
    _is_exiting: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()  # thread-safety of the shared set

    # ----------------------------------------------------------------------

    def __init__(self, parent, param=""):
        """
        The main init thread
        It is better to wait for initialization to complete in
        the child classes before calling run(). For this reason,
        start() has been moved to the individual instances."""

        Thread.__init__(self)

        self.parent = parent  # is the top-level window (main_frame)
        get = wx.GetApp()
        self.appdata = get.appset
        self.param = param  # additional parameters if present
        self.logfile = os.path.join(self.appdata["logdir"], "ffplay.log")
        self.process = None

        # set initial log file:
        make_log_template("ffplay.log", self.appdata["logdir"], mode="w")

    # ----------------------------------------------------------------------

    def _prepare_command(self, extra_args=""):
        """Prepare and format the command in a cross-platform way."""

        cmd_parts = [
            f'"{self.appdata["ffplay_cmd"]}"',
            self.appdata.get("ffplay-default-args", ""),
            self.appdata.get("ffplay_loglev", ""),
            extra_args,
            self.param,
        ]
        cmd = " ".join([str(part).strip() for part in cmd_parts if part])
        tolog(
            f"INFO: VIDEOMASS COMMAND: {cmd}",
            self.logfile,
            sep=True,
            wdate=True,
        )

        if self.appdata["ostype"] != "Windows":
            return shlex.split(cmd)
        return cmd

    # ----------------------------------------------------------------------

    def _handle_error(self, error_msg):
        """Centralized error handling."""
        tolog(error_msg, self.logfile)

        if BaseFilePlay._is_exiting:
            return

        wx.CallAfter(show_msg_notify, self.parent, logname="ffplay.log")

    # ----------------------------------------------------------------------

    def _finalize_play(self):
        """Always notify the GUI when playback ends."""
        if BaseFilePlay._is_exiting:
            return

        wx.CallAfter(pub.sendMessage, "END_PLAY")

    # ----------------------------------------------------------------------

    @classmethod
    def stop_all(cls):
        """If the user closes the Videomass app, this method
        will also force close ALL open ffplay windows."""

        with cls._lock:  # block concurency access on closing app
            # Closing Videomass while ffplay is in execution
            cls._is_exiting = True

            for proc in list(cls._active_processes):
                if proc.poll() is None:
                    try:
                        proc.terminate()
                        proc.wait(timeout=1)
                    except (OSError, subprocess.TimeoutExpired):
                        pass
            cls._active_processes.clear()


# ----------------------------------------------------------------------


class FilePlay(BaseFilePlay):
    """Simple file playback using ffplay, without progress tracking."""

    def run(self):
        """
        Start thread. Executes ffplay command
        """
        cmd = self._prepare_command()  # Don't use the "-stats" arg here!
        shell = self.appdata["ostype"] == "Windows"
        creationflags = subprocess.CREATE_NO_WINDOW if shell else 0

        try:
            self.process = subprocess.Popen(
                cmd,
                shell=shell,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                encoding=self.appdata["encoding"],
                creationflags=creationflags,
            )

            with BaseFilePlay._lock:
                BaseFilePlay._active_processes.add(self.process)

            __, error = self.process.communicate()

            if BaseFilePlay._is_exiting:
                return

            if self.process.returncode != 0 and error:
                self._handle_error(f"[FFPLAY] OUTPUT ERROR:\n{error}")
                return

        except OSError as err:
            self._handle_error(f"[VIDEOMASS]: ERROR: {err}")
            return

        finally:
            if self.process:
                try:
                    if self.process.stderr:
                        self.process.stderr.close()
                except OSError:
                    pass

            with BaseFilePlay._lock:
                if self.process in BaseFilePlay._active_processes:
                    BaseFilePlay._active_processes.remove(self.process)

        self._finalize_play()


# ----------------------------------------------------------------------


class FilePlayback_GetOutput(BaseFilePlay):
    """
    Playback local file executing ffplay media player.
    This class differs from `FilePlay` in that it implements
    capturing and redirecting output messages from stderr
    in real time.
    """

    def run(self):
        """
        Start thread. Executes ffplay command.
        RESOLVES ResourceWarning: Ensures that all I/O channels
        opened by the process are explicitly closed before the
        thread is destroyed, and safely removes all processes
        from the global set at the end of the thread.
        See the `finally` clause.
        """
        # -stats argument updates output messages progressively
        cmd = self._prepare_command(extra_args="-stats")
        full_output = []
        creationflags = (
            subprocess.CREATE_NO_WINDOW
            if self.appdata["ostype"] == "Windows"
            else 0
        )
        try:
            self.process = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                bufsize=1,
                text=True,
                encoding=self.appdata["encoding"],
                creationflags=creationflags,
            )

            with BaseFilePlay._lock:
                BaseFilePlay._active_processes.add(self.process)

            try:
                for line in self.process.stderr:
                    full_output.append(line)  # for the log in case of errors

                    if BaseFilePlay._is_exiting:
                        return

                    wx.CallAfter(
                        pub.sendMessage,
                        "UPDATE_PLAY_COUNTER",
                        output=line,
                        status=0,
                    )
            except ValueError:
                # file descriptor is forcibly closed from the outside
                if BaseFilePlay._is_exiting:
                    return

            return_code = self.process.wait()

            if BaseFilePlay._is_exiting:
                return

            if return_code != 0:
                wx.CallAfter(
                    pub.sendMessage,
                    "UPDATE_PLAY_COUNTER",
                    output=None,
                    status=return_code,
                )
                error_context = "".join(full_output[-5:])
                self._handle_error(
                    f"[FFPLAY] ERROR (Exit Code "
                    f"{return_code}):\n{error_context}"
                )
                return

        except OSError as err:
            self._handle_error(f"[VIDEOMASS]: ERROR: {err}")
            return

        finally:
            if self.process:
                try:
                    if self.process.stderr:
                        self.process.stderr.close()
                    if self.process.stdout:
                        self.process.stdout.close()
                except OSError:
                    pass

            with BaseFilePlay._lock:
                if self.process in BaseFilePlay._active_processes:
                    BaseFilePlay._active_processes.remove(self.process)

        self._finalize_play()
