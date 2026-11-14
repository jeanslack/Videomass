# -*- coding: UTF-8 -*-
"""
Name: volumedetect.py
Purpose: Get FFmpeg audio Peak level volume analyzes
Compatibility: Python >= 3.11, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.14.2026
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
import time

import wx
from pubsub import pub

from videomass.vdms_io.make_filelog import tolog
from videomass.vdms_utils.thread_utils import BaseVideomassThread


if sys.platform != "win32":
    import shlex


class VolumeDetectThread(BaseVideomassThread):
    """
    Run FFmpeg subprocess as a separate thread to get
    audio volume peak level data required for audio normalization
    process.

    USAGE:
        >>> thread = VolumeDetectThread(args)
        >>> thread.start()
        >>> if thread.data[1]:
        >>>     error
        >>>

        If your interface allows it, you can stop the process using:
        >>> self.thread.stop()

    Raise: `OSError` if not FFmpeg
    Return: tuple (list(volume), None or str(errors))

    """

    def __init__(self, timeseq, filelist, audiomap, logfile):
        """
        Replace /dev/null with NUL on Windows.

        parameters defined here:
        -----------------------
                timeseq: list["", ""] only two elements (from -ss to -t)
                filelist: list["file1", "file2", ...]
                audiomap: str(AudioIndex)
                logfile: str(pathname) to logfile

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
        See `io_tools.py` for more details on caller.

        NOTE: wx.callafter(pub...) do not send data to pop-up
              dialog, but a empty string that is useful to get
              the end of the process to close of the pop-up

        """
        volume = []
        FLUSH_INTERVAL = 2.0  # Secondi tra un flush e l'altro
        last_flush = time.monotonic()

        with open(self.logfile, "a", newline="\n", encoding="utf-8") as logf:
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
                    logf,
                    sep=True,
                    wdate=True,
                    openf=False,
                )
                cmd = shlex.split(cmd) if sys.platform != "win32" else cmd
                meanv, maxv = "", ""

                try:
                    with subprocess.Popen(
                        cmd,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                        bufsize=1,
                        text=True,
                        encoding=self.appdata["encoding"],
                        errors="replace",
                        creationflags=self.creationflags,
                    ) as self.process:
                        for line in self.process.stderr:
                            logf.write(line)
                            # 2 from the last flush
                            now = time.monotonic()
                            if now - last_flush >= FLUSH_INTERVAL:
                                logf.flush()
                                last_flush = now

                            if "max_volume:" in line:
                                maxv = line.split("max_volume:")[1].strip()
                            if "mean_volume:" in line:
                                meanv = line.split("mean_volume:")[1].strip()

                            if self.stop_work_thread:
                                if self.fatal:
                                    return
                                out = self.process.communicate()[1]
                                msgerr = (
                                    f"{out}\n[VIDEOMASS]: STOP command "
                                    f"received (PID {self.process.pid})\n"
                                    f"[FFMPEG]: Exit Code: "
                                    f"{self.process.returncode}"
                                )
                                tolog(msgerr, logf, openf=False)
                                self.status = "STOP"
                                break

                        exit_code = self.process.wait()
                        if exit_code != 0 and self.status != "STOP":
                            msgerr = f"[FFMPEG]: (Exit Code): {exit_code}"
                            tolog(msgerr, logf, openf=False)
                            self.status = msgerr
                        else:
                            volume.append((maxv, meanv))

                except (OSError, FileNotFoundError) as err:
                    tolog(f"[VIDEOMASS]: ERROR: {err}", logf, openf=False)
                    self.status = "ERROR"

                if self.status:  # Any ERROR or "STOP" string
                    break  # exit from files loop

            self.data = (volume, self.status)

        wx.CallAfter(pub.sendMessage, "RESULT_EVT", status="")
