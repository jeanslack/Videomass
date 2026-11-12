# -*- coding: UTF-8 -*-

"""
Name: ffplay_file.py
Purpose: playback media file via ffplay
Compatibility: Python >= 3.11, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.07.2026
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
import time
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

    def __init__(self, parent, cmdstr):
        """
        The main init thread
        It is better to wait for initialization to complete in
        the child classes before calling run(). For this reason,
        start() has been moved to the individual instances."""

        Thread.__init__(self)

        self.parent = parent  # is the top-level window (main_frame)
        get = wx.GetApp()
        self.appdata = get.appset
        self.cmdstr = cmdstr
        self.logfile = os.path.join(self.appdata["logdir"], "ffplay.log")
        self.process = None
        self.stopped_by_user = None

        # set initial log file:
        make_log_template("ffplay.log", self.appdata["logdir"], mode="w")

    # ----------------------------------------------------------------------

    def _prepare_command(self) -> list:
        """Prepare and format the command in a cross-platform way."""

        cmdlist = shlex.split(str(self.cmdstr))

        tolog(
            f"INFO: VIDEOMASS COMMAND: {shlex.join(cmdlist)}",
            self.logfile,
            sep=True,
            wdate=True,
        )
        return cmdlist

    # ----------------------------------------------------------------------

    def _handle_error(self, error_msg):
        """Centralized error handling."""

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

    def stop(self, classname):
        """
        This method provides an interface for the orderly termination
        of the active ffplay process.
        Note that, unlike ffmpeg, ffplay does not support exiting by
        writing "q" to stdin; consequently, this implementation forces
        a call to terminate(), or, in extreme cases, kill().

        The `classname` parameter accepts a string representing the
        exact name of one of the child classes.

        Let’s let `communicate()` in the `FilePlay` class handle
        the closing of `stderr`.
        """
        if self.process and self.process.poll() is None:
            if classname == "FilePlay":
                # NON chiudere stderr qui! Lascia che sia communicate() a farlo
                self.stopped_by_user = True
                try:
                    self.process.terminate()
                except (OSError, subprocess.TimeoutExpired):
                    self.process.kill()

            if classname == "FilePlayWithprogress":
                self.stopped_by_user = True
                try:
                    self.process.terminate()
                    self.process.wait(timeout=2)

                except (OSError, subprocess.TimeoutExpired):
                    self.process.kill()
                    self.process.wait()

                finally:
                    try:
                        if self.process.stderr:
                            self.process.stderr.close()
                        if self.process.stdout:
                            self.process.stdout.close()
                    except OSError:
                        pass

    # ----------------------------------------------------------------------

    @classmethod
    def stop_all(cls):
        """
        If the user closes the Videomass app, this method will
        also close any ffplay open windows, thus freeing up background
        processes immediatly.

        """
        with cls._lock:  # block concurency access on closing app
            # Closing Videomass while ffplay is in execution
            cls._is_exiting = True

            for proc in list(cls._active_processes):
                if proc.poll() is None:
                    try:
                        proc.terminate()
                        proc.wait(timeout=1)

                    except (OSError, subprocess.TimeoutExpired):
                        proc.kill()
                        # pass
            cls._active_processes.clear()


# ----------------------------------------------------------------------


class FilePlay(BaseFilePlay):
    """
    Simple file playback using ffplay, without progress tracking.

    NOTE: If you want to obtain the output of ffplay from stderr,
    you need to set its loglevel to "info".
    """

    def run(self):
        """
        Start thread. Executes ffplay command
        """
        cmd = self._prepare_command()  # Don't use the "-stats" arg here!
        is_windows = self.appdata["ostype"] == "Windows"
        creationflags = subprocess.CREATE_NO_WINDOW if is_windows else 0

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                encoding=self.appdata["encoding"],
                errors="replace",  # do not crash if non-UTF-8 chars
                creationflags=creationflags,
            )

            with BaseFilePlay._lock:
                BaseFilePlay._active_processes.add(self.process)

            __, error = self.process.communicate()

            tolog(error, self.logfile)

            if BaseFilePlay._is_exiting:
                return

            if self.process.returncode != 0 and error:
                ret = f"[FFPLAY] ERROR (Exit Code) {self.process.returncode}"
                if self.stopped_by_user is None:
                    self._handle_error(ret)
                else:
                    self.stopped_by_user = None

                tolog(ret, self.logfile)
                return

        except OSError as err:
            tolog(err, self.logfile)
            self._handle_error(f"[VIDEOMASS]: ERROR: {err}")
            return

        with BaseFilePlay._lock:
            if self.process in BaseFilePlay._active_processes:
                BaseFilePlay._active_processes.remove(self.process)

        self._finalize_play()


# ----------------------------------------------------------------------


class FilePlayWithprogress(BaseFilePlay):
    """
    Playback local file executing ffplay media player.
    Unlike `FilePlay`, this class implements the
    capture and redirection of output messages from `stderr`
    in real time, in order to monitor playback progress.

    NOTE: If you want to obtain the output of ffplay from stderr,
    you need to set its loglevel to "info".
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
        cmd = self._prepare_command()
        is_windows = self.appdata["ostype"] == "Windows"
        creationflags = subprocess.CREATE_NO_WINDOW if is_windows else 0

        FLUSH_INTERVAL = 2.0  # Secondi tra un flush e l'altro
        last_flush = time.monotonic()
        THROTTLE_INTERVAL = 0.1
        last_gui_update = time.monotonic()

        with open(
            self.logfile, "a", newline="\n", encoding="utf-8"
        ) as logfile:
            try:
                self.process = subprocess.Popen(
                    cmd,
                    stderr=subprocess.PIPE,
                    bufsize=1,
                    text=True,
                    encoding=self.appdata["encoding"],
                    errors="replace",  # do not crash if non-UTF-8 chars
                    creationflags=creationflags,
                )
                with BaseFilePlay._lock:
                    BaseFilePlay._active_processes.add(self.process)

                try:
                    for line in self.process.stderr:
                        logfile.write(line)  # write without newline (no tolog)
                        # check if 2 seconds have passed since the last flush
                        now = time.monotonic()
                        if now - last_flush >= FLUSH_INTERVAL:
                            logfile.flush()
                            last_flush = now

                        if BaseFilePlay._is_exiting:
                            return

                        if now - last_gui_update > THROTTLE_INTERVAL:
                            wx.CallAfter(
                                pub.sendMessage,
                                "UPDATE_PLAY_COUNTER",
                                output=line,
                                status=0,
                            )
                            last_gui_update = now

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
                    err = f"[FFPLAY] ERROR (Exit Code {return_code})"
                    tolog(err, logfile, openf=False)
                    if self.stopped_by_user is None:
                        self._handle_error(err)
                    else:
                        self.stopped_by_user = None
                    return

            except OSError as err:
                tolog(err, logfile, openf=False)
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
