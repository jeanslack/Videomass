# -*- coding: UTF-8 -*-
"""
Name: slideshow.py
Purpose: FFmpeg long processing task
Compatibility: Python >= 3.11, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.21.2026
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
import sys
import tempfile
import time

import wx
from pubsub import pub

from videomass.vdms_io.make_filelog import tolog
from videomass.vdms_utils.thread_utils import BaseVideomassThread
from videomass.vdms_utils.utils import split_args


def convert_images(*varargs, **kwargs):
    """
    Convert images to PNG format and assign
    progressive digits to them.
    """
    flist = varargs[0]  # list
    tmpdir = varargs[1]
    logfile = varargs[2]
    imagenames = varargs[3]
    creationflags = varargs[4]

    count1 = (
        f"Preparing temporary files...\nSource: Imported file list\n"
        f'Destination: "{tmpdir}"\n'
    )
    wx.CallAfter(
        pub.sendMessage,
        "COUNT_EVT",
        count=count1,
        duration=len(flist),
        end="CONTINUE",
    )
    with open(logfile, "a", encoding="utf-8") as logf:
        tolog(
            f"Preparing temporary files...\n\n[TEMPDIR]:\n{tmpdir}",
            logf,
            sep=True,
            wdate=True,
            openf=False,
        )
        for prognum, files in enumerate(flist, start=1):
            tmpf = os.path.join(tmpdir, f"{imagenames}{prognum}.bmp")
            cmd_1 = [
                kwargs["ffmpeg_cmd"],
                *split_args(kwargs["ffmpeg-default-args"]),
                *split_args(kwargs["ffmpeg_loglev"]),
                "-i",
                files,
                tmpf,
            ]
            cmd_log = (
                subprocess.list2cmdline(cmd_1)
                if sys.platform != "win32"
                else shlex.join(cmd_1)
            )
            logf.write(f"\n|{prognum}|[COMMAND]:\n{cmd_log}\n")

            try:
                with subprocess.Popen(
                    cmd_1,
                    stderr=subprocess.PIPE,
                    bufsize=1,
                    text=True,
                    encoding=kwargs["encoding"],
                    errors="replace",
                    creationflags=creationflags,
                ) as proc1:
                    error = proc1.communicate()[1]

                if proc1.returncode:  # ffmpeg error
                    if error:
                        status = (
                            f"[VIDEOMASS]: Error Exit Status: "
                            f"{proc1.returncode} {error}"
                        )
                        wx.CallAfter(
                            pub.sendMessage,
                            "NOTIFICATIONS_MSG_EVT",
                            msg="FAILED",
                            output=status,
                        )
                        logf.write(status)
                        return error

                else:  # done
                    wx.CallAfter(
                        pub.sendMessage,
                        "NOTIFICATIONS_MSG_EVT",
                        msg="INFO",
                        output=f" |{prognum}|  {files}  >  {tmpf}\n",
                    )

            except (OSError, FileNotFoundError) as err:  # cmd not found
                wx.CallAfter(
                    pub.sendMessage,
                    "COUNT_EVT",
                    count=err,
                    duration=0,
                    end="ERROR",
                )
                logf.write(f"[PYTHON]: error: {err}")
                return f"[PYTHON]: error: {err}"

    time.sleep(0.5)
    wx.CallAfter(
        pub.sendMessage, "COUNT_EVT", count="", duration=0, end="DONE"
    )
    return None


def resizing_process(*varargs, **kwargs):
    """
    After the images have been converted to the required format,
    this process performs the resizing using ffmpeg filters.
    This is a necessary workaround for proper video playback.
    """
    flist = varargs[0]
    tmpdir = varargs[1]
    cmdargs = varargs[2]
    logfile = varargs[3]
    creationflags = varargs[4]

    count1 = (
        f"\n\nFile resizing...\nSource: Temporary directory\n"
        f'Destination: "{tmpdir}"'
    )

    wx.CallAfter(
        pub.sendMessage,
        "COUNT_EVT",
        count=count1,
        duration=len(flist),
        end="CONTINUE",
    )

    tmpf = os.path.join(tmpdir, "TMP_%d.bmp")
    tmpfout = os.path.join(tmpdir, "IMAGE_%d.bmp")
    cmd_1 = [
        kwargs["ffmpeg_cmd"],
        *split_args(kwargs["ffmpeg-default-args"]),
        *split_args(kwargs["ffmpeg_loglev"]),
        "-i",
        tmpf,
        *split_args(cmdargs),
        tmpfout,
    ]
    cmd_log = (
        subprocess.list2cmdline(cmd_1)
        if sys.platform != "win32"
        else shlex.join(cmd_1)
    )
    tolog(
        f"\nFile resizing...\n\n[COMMAND]:\n{cmd_log}",
        logfile,
        sep=True,
        wdate=True,
        openf=True,
    )
    try:
        with subprocess.Popen(
            cmd_1,
            stderr=subprocess.PIPE,
            bufsize=1,
            text=True,
            encoding=kwargs["encoding"],
            errors="replace",
            creationflags=creationflags,
        ) as proc1:
            error = proc1.communicate()[1]

        if proc1.returncode:  # ffmpeg error
            if error:
                status = (
                    f"[VIDEOMASS]: Error Exit Status: "
                    f"{proc1.returncode} {error}"
                )
                wx.CallAfter(
                    pub.sendMessage,
                    "NOTIFICATIONS_MSG_EVT",
                    msg="FAILED",
                    output=status,
                )
                tolog(status, logfile)
                return error

        else:  # ok
            wx.CallAfter(
                pub.sendMessage,
                "NOTIFICATIONS_MSG_EVT",
                msg="INFO",
                output="\nResizing completed successfully.\n",
            )
            tolog(error, logfile)

    except (OSError, FileNotFoundError) as err:  # cmd not found
        wx.CallAfter(
            pub.sendMessage,
            "COUNT_EVT",
            count=err,
            duration=0,
            end="ERROR",
        )
        tolog(f"[PYTHON]: error: {err}", logfile)
        return f"[PYTHON]: error: {err}"

    time.sleep(0.5)
    wx.CallAfter(
        pub.sendMessage, "COUNT_EVT", count="", duration=0, end="DONE"
    )
    return None


class SlideshowMaker(BaseVideomassThread):
    """
    Represents the ffmpeg subprocess to produce a video in
    mkv format from a sequence of images already converted
    and resized in a temporary context.
    """

    def __init__(self, *args, **kwargs):
        """
        Called from `long_processing_task.topic_thread`.
        Also see `main_frame.switch_to_processing`.
        """
        super().__init__(logfile=args[0])

        get = wx.GetApp()  # get videomass wx.App attribute
        self.appdata = get.appset
        self.duration = kwargs["duration"]
        self.count = 0  # count first for loop
        self.countmax = kwargs["nmax"]
        self.destination = kwargs["destination"]
        self.kwa = kwargs

    # ----------------------------------------------------------------#

    def _prepare_command(self, tempdir, logf) -> list:
        """
        Prepare and format the command in a cross-platform way
        and writes logfile.
        Return list of command args.

        """
        tmpgroup = os.path.join(tempdir, "IMAGE_%d.bmp")
        cmd_2 = [
            self.appdata["ffmpeg_cmd"],
            *split_args(self.appdata["ffmpeg-default-args"]),
            *split_args(self.appdata["ffmpeg_loglev"]),
            *split_args(self.kwa["pre-input-1"]),
            "-i",
            tmpgroup,
            *split_args(self.kwa["args"]),
            self.destination,
        ]
        cmd_log = (
            subprocess.list2cmdline(cmd_2)
            if self.appdata["ostype"] == "Windows"
            else shlex.join(cmd_2)
        )
        count = (
            f'\n\nVideo production...\nSource: "{tempdir}"\n'
            f'Destination: "{self.destination}"\n'
        )
        tolog(
            f"{count}\n\n[COMMAND]:\n{cmd_log}",
            logf,
            sep=True,
            wdate=True,
            openf=False,
        )
        wx.CallAfter(
            pub.sendMessage,
            "COUNT_EVT",
            count=count,
            duration=self.duration,
            end="CONTINUE",
        )
        return cmd_2

    # ----------------------------------------------------------------#

    def run(self):
        """
        Subprocess initialize thread.
        """
        last_gui_update = time.monotonic()
        THROTTLE_INTERVAL = 0.1
        last_file_flush = time.monotonic()
        FLUSH_INTERVAL = 2.0  # Secondi tra un flush e l'altro (constant)

        imgtmpnames = "TMP_" if self.kwa["resize"] else "IMAGE_"
        filedone = []

        with tempfile.TemporaryDirectory() as tempdir:  # make tmp dir
            tmpproc1 = convert_images(
                self.kwa["source"],
                tempdir,
                self.logfile,
                imgtmpnames,
                self.creationflags,
                **self.appdata,
            )
            if tmpproc1 is not None or self.stop_work_thread:
                msg = "STOP" if self.stop_work_thread else "FAILED"
                stopcmd = "[VIDEOMASS]: STOP command received."
                errstr = f"[VIDEOMASS]: Failed! Error Exit Code: {tmpproc1}"
                out = stopcmd if self.stop_work_thread else errstr

                wx.CallAfter(
                    pub.sendMessage,
                    "NOTIFICATIONS_MSG_EVT",
                    msg=msg,
                    output=out,
                )
                self.end_process(None)
                return

            if imgtmpnames == "TMP_":
                tmpproc2 = resizing_process(
                    self.kwa["source"],
                    tempdir,
                    self.kwa["resize"],
                    self.logfile,
                    self.creationflags,
                    **self.appdata,
                )

                if tmpproc2 is not None or self.stop_work_thread:
                    msg = "STOP" if self.stop_work_thread else "FAILED"
                    stopcmd = "[VIDEOMASS]: STOP command received."
                    errstr = (
                        f"[VIDEOMASS]: Failed! Error Exit Code: {tmpproc2}"
                    )
                    out = stopcmd if self.stop_work_thread else errstr

                    wx.CallAfter(
                        pub.sendMessage,
                        "NOTIFICATIONS_MSG_EVT",
                        msg=msg,
                        output=out,
                    )
                    self.end_process(None)
                    return

            # ------------------------------- make video
            with open(self.logfile, "a", encoding="utf-8") as logfile:
                cmd_2 = self._prepare_command(tempdir, logfile)

                try:
                    with subprocess.Popen(
                        cmd_2,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                        bufsize=1,
                        text=True,
                        encoding=self.appdata["encoding"],
                        errors="replace",
                        creationflags=self.creationflags,
                    ) as self.process:
                        for line in self.process.stderr:
                            logfile.write(line)
                            now = time.monotonic()
                            if (now - last_file_flush) > FLUSH_INTERVAL:
                                logfile.flush()
                                last_file_flush = now

                            if (now - last_gui_update) > THROTTLE_INTERVAL:
                                wx.CallAfter(
                                    pub.sendMessage,
                                    "UPDATE_EVT",
                                    output=line,
                                    duration=self.duration,
                                    status=0,
                                )
                                last_gui_update = now

                            if self.stop_work_thread:
                                if self.fatal:
                                    return
                                out = self.process.communicate()[1]

                                stopstr = "[VIDEOMASS]: STOP command received."
                                wx.CallAfter(
                                    pub.sendMessage,
                                    "NOTIFICATIONS_MSG_EVT",
                                    msg="STOP",
                                    output=stopstr,
                                )
                                logfile.write(f"{out}\n{stopstr}")
                                self.end_process(None)
                                return

                    exit_code = self.process.wait()
                    if exit_code != 0:  # ffmpeg error
                        out = self.process.communicate()[1]
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
                    else:  # status ok
                        filedone = self.kwa["source"]
                        wx.CallAfter(
                            pub.sendMessage,
                            "COUNT_EVT",
                            count="",
                            duration=self.duration,
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
                    logfile.write(f"[PYTHON]: error: {err}", self.logfile)

        self.end_process(filedone)

    def end_process(self, filedone):
        """
        The process is finished
        """
        time.sleep(0.5)
        wx.CallAfter(pub.sendMessage, "END_EVT", filetotrash=filedone)
