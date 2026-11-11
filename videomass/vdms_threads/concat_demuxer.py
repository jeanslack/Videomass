# -*- coding: UTF-8 -*-
"""
Name: concat_demuxer.py
Purpose: FFmpeg long processing task for Concatenation processing
Compatibility: Python >= 3.11, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.11.2026
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


class ConcatDemuxer(BaseVideomassThread):
    """
    This class represents a separate thread for running processes,
    which need to read the stdout/stderr in real time.

    NOTE capturing output in real-time (Windows, Unix):

    https://stackoverflow.com/questions/1388753/how-to-get-output-
    from-subprocess-popen-proc-stdout-readline-blocks-no-dat?rq=1
    """

    # ---------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        """
        Called from `long_processing_task.topic_thread`.
        Also see `main_frame.switch_to_processing`.

        """
        super().__init__(logfile=args[0])

        get = wx.GetApp()  # get videomass wx.App attribute
        self.appdata = get.appset
        self.kwa = kwargs

    def run(self):
        """
        Subprocess initialize thread.

        """
        filedone = None
        cmd = (
            f'"{self.appdata["ffmpeg_cmd"]}" '
            f"{self.appdata['ffmpeg-default-args']} "
            f"{self.appdata['ffmpeg_loglev']} -f concat "
            f'-safe 0 -i {self.kwa["args"]} "{self.kwa["destination"]}"'
        )

        count = (
            f"{self.kwa['nmax']} Items in progress...\nSource: "
            f'"{self.kwa["source"]}"\nDestination: '
            f'"{self.kwa["destination"]}"'
        )
        stamp = f"{count}\n\n[COMMAND]:\n{cmd}"

        # countevt = (
        #     f"{self.kwa['nmax']} Items in progress...\n...for "
        #     f"details see Current Log.\nDestination: "
        #     f'"{self.kwa["destination"]}"'
        # )
        strsrc = "\n".join(self.kwa["source"])
        countevt = (
            f"{self.kwa['nmax']} Items in progress...\n...for "
            f"details see Current Log.\n\nSource:\n{strsrc}\n\nDestination: "
            f'"{self.kwa["destination"]}"'
        )
        wx.CallAfter(
            pub.sendMessage,
            "COUNT_EVT",
            count=countevt,
            duration=self.kwa["duration"],
            end="CONTINUE",
        )
        cmd = shlex.split(cmd) if sys.platform != "win32" else cmd

        with open(self.logfile, "a", encoding="utf-8") as logfile:
            tolog(stamp, logfile, sep=True, wdate=True, openf=False)
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
                        wx.CallAfter(
                            pub.sendMessage,
                            "UPDATE_EVT",
                            output=line,
                            duration=self.kwa["duration"],
                            status=0,
                        )
                        logfile.write(line)
                        if self.stop_work_thread:
                            if self.fatal:
                                return
                            out = self.process.communicate()[1]
                            self.process.wait()
                            stopstr = "[VIDEOMASS]: STOP command received."
                            wx.CallAfter(
                                pub.sendMessage,
                                "NOTIFICATIONS_MSG_EVT",
                                msg="STOP",
                                output=stopstr,
                            )
                            logfile.write(f"{out}\n{stopstr}")

                            time.sleep(0.5)
                            wx.CallAfter(
                                pub.sendMessage,
                                "END_EVT",
                                filetotrash=None,
                            )
                            return

                    exit_code = self.process.wait()
                    if exit_code != 0:  # ffmpeg error
                        errstr = (
                            f"[VIDEOMASS]: Failed! Error "
                            f"Exit Code: {exit_code}"
                        )
                        logfile.write(errstr)
                        wx.CallAfter(
                            pub.sendMessage,
                            "NOTIFICATIONS_MSG_EVT",
                            msg="FAILED",
                            output=errstr,
                        )
                        time.sleep(1)
                    else:
                        filedone = self.kwa["source"]
                        wx.CallAfter(
                            pub.sendMessage,
                            "COUNT_EVT",
                            count="",
                            duration="",
                            end="DONE",
                        )
            except (OSError, FileNotFoundError) as err:
                wx.CallAfter(
                    pub.sendMessage,
                    "COUNT_EVT",
                    count=err,
                    duration=0,
                    end="ERROR",
                )
                logfile.write(f"[PYTHON]: error: {err}")

        time.sleep(0.5)
        wx.CallAfter(pub.sendMessage, "END_EVT", filetotrash=filedone)
