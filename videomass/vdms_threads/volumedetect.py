# -*- coding: UTF-8 -*-
"""
Name: volumedetect.py
Purpose: Get FFmpeg audio Peak level volume analyzes
Compatibility: Python >= 3.11, wxPython Phoenix
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

import wx
from pubsub import pub

from videomass.vdms_io.make_filelog import tolog
from videomass.vdms_utils.thread_utils import BaseVideomassThread


if sys.platform != "win32":
    import shlex


class VolumeDetectThread(BaseVideomassThread):
    """
    This class represents a separate subprocess thread to get
    audio volume peak level when required for audio normalization
    process.

    NOTE: all error handling (including verification of the
    existence of files) is entrusted to ffmpeg, except for the
    lack of ffmpeg of course.

    """

    STOP = (
        "WARNING: [VIDEOMASS]: STOP command received by signal "
        "event.\nTerminated process "
    )

    def __init__(self, timeseq, filelist, audiomap, logfile):
        """
        Replace /dev/null with NUL on Windows.

        self.status: None, if nothing error,
                     tuple(str(message), str(info/error/warn)) if errors.
        self.data: it is a tuple containing the list of audio volume
                   parameters and the self.status of the output error,
                   in the form:
                   ([[maxvol, medvol], [etc,etc]], None or "str errors")
        """
        super().__init__(logfile=logfile)

        get = wx.GetApp()
        self.appdata = get.appset
        self.filelist = filelist
        self.time_seq = timeseq
        self.audiomap = audiomap
        self.status = None
        self.data = None
        self.nul = "NUL" if sys.platform == "win32" else "/dev/null"
        self.logfile = logfile

    # ----------------------------------------------------------------#

    def run(self):
        """
        Audio volume data is getted by the thread's caller using
        the thread.data method (see io_tools).
        NOTE: wx.callafter(pub...) do not send data to pop-up
              dialog, but a empty string that is useful to get
              the end of the process to close of the pop-up

        """
        volume = []
        for files in self.filelist:
            cmd = (
                f'"{self.appdata["ffmpeg_cmd"]}" '
                f"{self.appdata['ffmpeg-default-args']} "
                f"{self.appdata['ffmpeg_loglev']} "
                f"{self.time_seq[0]} "
                f'-i "{files}" '
                f"{self.time_seq[1]} "
                f"{self.audiomap} "
                f"-af volumedetect -vn -sn -dn -f null "
                f"{self.nul}"
            )
            tolog(
                f"INFO: VIDEOMASS COMMAND: {cmd}",
                self.logfile,
                sep=True,
                wdate=True,
            )

            if sys.platform != "win32":
                cmd = shlex.split(cmd)
            try:
                with subprocess.Popen(
                    cmd,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    bufsize=1,
                    text=True,
                    encoding=self.appdata["encoding"],
                    creationflags=self.creationflags,
                ) as self.process:
                    meanv, maxv = "", ""
                    for line in self.process.stderr:
                        if "max_volume:" in line:
                            maxv = line.split(":")[1].strip()
                        if "mean_volume:" in line:
                            meanv = line.split(":")[1].strip()

                        if self.stop_work_thread:
                            if self.fatal:
                                return
                            self.process.communicate()[1]
                            out = (
                                VolumeDetectThread.STOP
                                + f"with PID {self.process.pid}"
                            )
                            tolog(out, self.logfile)
                            self.process.wait()
                            self.status = "STOP"
                            break

                        if self.process.wait():
                            output = self.process.communicate()[1]
                            tolog(f"[FFMPEG] ERROR:\n{output}", self.logfile)
                            self.status = "ERROR"
                            break

                    volume.append((maxv, meanv))

            except (OSError, FileNotFoundError) as err:
                tolog(f"[VIDEOMASS]: ERROR: {err}", self.logfile)
                self.status = "ERROR"

            if self.status:
                break

        self.data = (volume, self.status)

        wx.CallAfter(pub.sendMessage, "RESULT_EVT", status="")
