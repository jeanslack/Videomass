# -*- coding: UTF-8 -*-
"""
Name: ffmpeg.py
Purpose: FFmpeg long processing task
Compatibility: Python >= 3.11, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.10.2026
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


def get_raw_cmdline_args(**kwa):
    """
    Return a list of raw command lines.
    """
    if kwa["type"] == "One pass":
        model = simple_one_pass(1, 1, **kwa)

    elif kwa["type"] == "Two pass EBU":
        model = one_pass_ebu(1, 1, **kwa)

    elif kwa["type"] == "Two pass VIDSTAB":
        model = one_pass_stab(1, 1, **kwa)

    elif kwa["type"] == "Two pass":
        model = one_pass(1, 1, **kwa)
    else:
        return None

    spl1 = model["stamp1"].split("\n")
    idx1 = spl1.index("[COMMAND]:") + 1
    cmd1 = spl1[idx1]

    if not kwa["args"][1]:
        return (cmd1,)

    if kwa["type"] == "Two pass EBU":
        filters = (
            f"{kwa['EBU']}"
            f":measured_I=<?>"
            f":measured_LRA=<?>"
            f":measured_TP=<?>"
            f":measured_thresh=<?>"
            f":offset=<?>"
            f":linear=true:dual_mono=true"
        )
        model = two_pass_ebu(1, 1, filters, **kwa)

    elif kwa["type"] == "Two pass VIDSTAB":
        model = two_pass_stab(1, 1, **kwa)

    elif kwa["type"] == "Two pass":
        model = two_pass(1, 1, **kwa)

    spl2 = model["stamp2"].split("\n")
    idx2 = spl2.index("[COMMAND]:") + 1
    cmd2 = spl2[idx2]

    return cmd1, cmd2


# ----------------------------------------------------------------------


def ffmpeg_cmd_args():
    """
    Get ffmpeg command and default args
    """
    get = wx.GetApp()
    appdata = get.appset
    defargs = f"-y -stats -hide_banner {appdata['ffmpeg_loglev']}"
    return {
        "ffmpeg_cmd": appdata["ffmpeg_cmd"],
        "ffmpeg-default-args": defargs,
    }


# ----------------------------------------------------------------------


def one_pass(*args, **kwa):
    """
    Command builder for first pass of two
    """
    cmd = ffmpeg_cmd_args()
    nul = "NUL" if sys.platform == "win32" else "/dev/null"
    pass1 = (
        f'"{cmd["ffmpeg_cmd"]}" '
        f"{cmd['ffmpeg-default-args']} "
        f"{kwa.get('pre-input-1', '')} "
        f"{kwa['start-time']} "
        f'-i "{kwa["source"]}" '
        f"{kwa['end-time']} "
        f"{kwa['args'][0]} "
        f"{nul}"
    )
    count1 = (
        f"File {args[0]}/{args[1]} - Pass One\n"
        f'Source: "{kwa["source"]}"\nDestination: "{nul}"'
    )
    stamp1 = f"{count1}\n\n[COMMAND]:\n{pass1}"

    pass1 = shlex.split(pass1) if sys.platform != "win32" else pass1

    return {"pass1": pass1, "count1": count1, "stamp1": stamp1}


# ----------------------------------------------------------------------


def two_pass(*args, **kwa):
    """
    Command builder for second pass of two
    """
    cmd = ffmpeg_cmd_args()
    pass2 = (
        f'"{cmd["ffmpeg_cmd"]}" '
        f"{cmd['ffmpeg-default-args']} "
        f"{kwa.get('pre-input-2', '')} "
        f"{kwa['start-time']} "
        f'-i "{kwa["source"]}" '
        f"{kwa['end-time']} "
        f"{kwa['args'][1]} "
        f"{kwa.get('volume', '')} "
        f'"{kwa["destination"]}"'
    )
    count2 = (
        f"File {args[0]}/{args[1]} - Pass Two\n"
        f'Source: "{kwa["source"]}"\nDestination: '
        f'"{kwa["destination"]}"'
    )
    stamp2 = f"\n{count2}\n\n[COMMAND]:\n{pass2}"

    pass2 = shlex.split(pass2) if sys.platform != "win32" else pass2

    return {"pass2": pass2, "count2": count2, "stamp2": stamp2}


# ----------------------------------------------------------------------


def one_pass_stab(*args, **kwa):
    """
    Command builder for one pass video stabilizer
    """
    cmd = ffmpeg_cmd_args()
    nul = "NUL" if sys.platform == "win32" else "/dev/null"
    pass1 = (
        f'"{cmd["ffmpeg_cmd"]}" '
        f"{cmd['ffmpeg-default-args']} "
        f"{kwa.get('pre-input-1', '')} "
        f"{kwa['start-time']} "
        f'-i "{kwa["source"]}" '
        f"{kwa['end-time']} "
        f"{kwa['args'][0]} "
        f"{nul}"
    )
    count1 = (
        f"File {args[0]}/{args[1]} - Pass One\n"
        f"Detecting statistics for measurements...\n\nSource: "
        f'"{kwa["source"]}"\nDestination: "{nul}"'
    )
    stamp1 = f"{count1}\n\n[COMMAND]:\n{pass1}"

    pass1 = shlex.split(pass1) if sys.platform != "win32" else pass1

    return {"pass1": pass1, "count1": count1, "stamp1": stamp1}


# ----------------------------------------------------------------------


def two_pass_stab(*args, **kwa):
    """
    Command builder for two pass video stabilizer
    """
    cmd = ffmpeg_cmd_args()
    pass2 = (
        f'"{cmd["ffmpeg_cmd"]}" '
        f"{cmd['ffmpeg-default-args']} "
        f"{kwa.get('pre-input-2', '')} "
        f"{kwa['start-time']} "
        f'-i "{kwa["source"]}" '
        f"{kwa['end-time']} "
        f"{kwa['args'][1]} "
        f"{kwa.get('volume', '')} "
        f'"{kwa["destination"]}"'
    )
    count2 = (
        f"File {args[0]}/{args[1]} - Pass Two\n"
        f"Application of Audio/Video filters...\n\nSource: "
        f'"{kwa["source"]}"\nDestination: "{kwa["destination"]}"'
    )
    stamp2 = f"\n{count2}\n\n[COMMAND]:\n{pass2}"

    pass2 = shlex.split(pass2) if sys.platform != "win32" else pass2

    return {"pass2": pass2, "count2": count2, "stamp2": stamp2}


# ----------------------------------------------------------------------


def simple_one_pass(*args, **kwa):
    """
    Command builder for one pass ebu
    """
    cmd = ffmpeg_cmd_args()
    pass1 = (
        f'"{cmd["ffmpeg_cmd"]}" '
        f"{cmd['ffmpeg-default-args']} "
        f"{kwa.get('pre-input-1', '')} "
        f"{kwa['start-time']} "
        f'-i "{kwa["source"]}" '
        f"{kwa['end-time']} "
        f"{kwa['args'][0]} "
        f"{kwa.get('volume', '')} "
        f'"{kwa["destination"]}"'
    )
    count1 = (
        f"File {args[0]}/{args[1]}\nSource: "
        f'"{kwa["source"]}"\nDestination: "{kwa["destination"]}"'
    )
    stamp1 = f"{count1}\n\n[COMMAND]:\n{pass1}"

    pass1 = shlex.split(pass1) if sys.platform != "win32" else pass1

    return {"pass1": pass1, "count1": count1, "stamp1": stamp1}


# ----------------------------------------------------------------------


def one_pass_ebu(*args, **kwa):
    """
    Command builder for one pass ebu
    """
    cmd = ffmpeg_cmd_args()
    nul = "NUL" if sys.platform == "win32" else "/dev/null"
    pass1 = (
        f'"{cmd["ffmpeg_cmd"]}" '
        f"{cmd['ffmpeg-default-args']} "
        f"{kwa.get('pre-input-1', '')} "
        f"{kwa['start-time']} "
        f'-i "{kwa["source"]}" '
        f"{kwa['end-time']} "
        f"{kwa['args'][0]} "
        f"{nul}"
    )
    count1 = (
        f"File {args[0]}/{args[1]} - Pass One\n"
        f"Detecting statistics for measurements...\n\nSource: "
        f'"{kwa["source"]}"\nDestination: "{nul}"'
    )
    stamp1 = f"{count1}\n\n[COMMAND]:\n{pass1}"

    pass1 = shlex.split(pass1) if sys.platform != "win32" else pass1

    summary = {
        "Input Integrated:": None,
        "Input True Peak:": None,
        "Input LRA:": None,
        "Input Threshold:": None,
        "Output Integrated:": None,
        "Output True Peak:": None,
        "Output LRA:": None,
        "Output Threshold:": None,
        "Normalization Type:": None,
        "Target Offset:": None,
    }
    return {
        "pass1": pass1,
        "count1": count1,
        "stamp1": stamp1,
        "summary": summary,
    }


# ----------------------------------------------------------------------


def two_pass_ebu(*args, **kwa):
    """
    Command builder for two pass ebu
    """
    cmd = ffmpeg_cmd_args()
    pass2 = (
        f'"{cmd["ffmpeg_cmd"]}" '
        f"{cmd['ffmpeg-default-args']} "
        f"{kwa.get('pre-input-2', '')} "
        f"{kwa['start-time']} "
        f'-i "{kwa["source"]}" '
        f"{kwa['end-time']} "
        f"{kwa['args'][1]} "
        f"-filter:a:{kwa['audiomap'][1]} "
        f"{args[2]} "
        f'"{kwa["destination"]}"'
    )
    count2 = (
        f"File {args[0]}/{args[1]} - Pass Two\n"
        f"Application of Audio/Video filters...\n\nSource: "
        f'"{kwa["source"]}"\nDestination: "{kwa["destination"]}"'
    )
    stamp2 = f"\n{count2}\n\n[COMMAND]:\n{pass2}"

    pass2 = shlex.split(pass2) if sys.platform != "win32" else pass2

    return {"pass2": pass2, "count2": count2, "stamp2": stamp2}


# ----------------------------------------------------------------------


class FFmpeg(BaseVideomassThread):
    """
    This class performs a long processing task in a separate thread.
    It is able to pipe up to two FFmpeg subprocesses to execute
    tasks in succession using command concatenation.

    NOTE capturing output in real-time (Windows, Unix):
    https://stackoverflow.com/questions/1388753/how-to-get-output-
    from-subprocess-popen-proc-stdout-readline-blocks-no-dat?rq=1

    """

    def __init__(self, *args):
        """
        Called from `long_processing_task.topic_thread`.
        Also see `main_frame.switch_to_processing`.

        """
        super().__init__(logfile=args[0])

        get = wx.GetApp()  # get data from bootstrap
        self.appdata = get.appset
        self.count = 0  # count loops
        self.kwargs = args[1]  # it is a list of dictionaries
        self.nargs = len(self.kwargs)  # how many items...

    def run(self):
        """
        Run the separated thread.
        """
        last_gui_update = 0
        last_file_flush = 0
        throttle_interval = 0.1
        flush_interval = 2.0
        filedone = []

        with open(self.logfile, "a", encoding="utf-8") as logfile:
            for kwa in self.kwargs:
                self.count += 1
                if kwa["type"] == "One pass":
                    model = simple_one_pass(self.count, self.nargs, **kwa)

                elif kwa["type"] == "Two pass EBU":
                    model = one_pass_ebu(self.count, self.nargs, **kwa)

                elif kwa["type"] == "Two pass VIDSTAB":
                    model = one_pass_stab(self.count, self.nargs, **kwa)

                elif kwa["type"] == "Two pass":
                    model = one_pass(self.count, self.nargs, **kwa)
                else:
                    return

                wx.CallAfter(
                    pub.sendMessage,
                    "COUNT_EVT",
                    count=model["count1"],
                    duration=kwa["duration"],
                    end="CONTINUE",
                )
                tolog(
                    model["stamp1"], logfile, sep=True, wdate=True, openf=False
                )
                try:
                    with subprocess.Popen(
                        model["pass1"],
                        stderr=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                        bufsize=1,
                        text=True,
                        encoding=self.appdata["encoding"],
                        errors="replace",
                        creationflags=self.creationflags,
                    ) as self.process:
                        for line in self.process.stderr:
                            logfile.write(f"[FFMPEG]: {line}")
                            current_time = time.time()
                            if (
                                current_time - last_file_flush
                            ) > flush_interval:
                                logfile.flush()
                                last_file_flush = current_time
                            if (
                                current_time - last_gui_update
                            ) > throttle_interval:
                                wx.CallAfter(
                                    pub.sendMessage,
                                    "UPDATE_EVT",
                                    output=line,
                                    duration=kwa["duration"],
                                    status=0,
                                )
                                last_gui_update = current_time

                            if kwa["type"] == "Two pass EBU":
                                summary = model["summary"]
                                for k in summary:
                                    if line.startswith(k):
                                        summary[k] = line.split(":")[
                                            1
                                        ].split()[0]

                            if self.stop_work_thread:
                                if self.fatal:
                                    return
                                out = self.process.communicate()[1]
                                self.process.wait()
                                stopstr = "[VIDEOMASS]: STOP command received."
                                wx.CallAfter(
                                    pub.sendMessage,
                                    "ERROR_MSG_EVT",
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
                        time.sleep(2)  # WARNING need time here
                        exit_code = self.process.poll()
                        if exit_code is not None:
                            if exit_code != 0:
                                errstr = (
                                    f"[VIDEOMASS]: Failed! Error "
                                    f"Exit Code: {exit_code}"
                                )
                                logfile.write(errstr)
                                wx.CallAfter(
                                    pub.sendMessage,
                                    "ERROR_MSG_EVT",
                                    msg="FAILED",
                                    output=errstr,
                                )
                                time.sleep(2)
                                continue  # go to next file

                            else:
                                if not kwa["args"][1]:
                                    filedone.append(kwa["source"])
                                wx.CallAfter(
                                    pub.sendMessage,
                                    "COUNT_EVT",
                                    count="",
                                    duration=kwa["duration"],
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
                    break  # completely exiting from loops

                if not kwa["args"][1]:
                    continue

                # --------------- second pass ----------------#
                if kwa["type"] == "Two pass EBU":
                    filters = (
                        f"{kwa['EBU']}"
                        f":measured_I={summary['Input Integrated:']}"
                        f":measured_LRA={summary['Input LRA:']}"
                        f":measured_TP={summary['Input True Peak:']}"
                        f":measured_thresh={summary['Input Threshold:']}"
                        f":offset={summary['Target Offset:']}"
                        f":linear=true:dual_mono=true"
                    )
                    model = two_pass_ebu(
                        self.count, self.nargs, filters, **kwa
                    )
                    time.sleep(0.5)

                elif kwa["type"] == "Two pass VIDSTAB":
                    model = two_pass_stab(self.count, self.nargs, **kwa)

                elif kwa["type"] == "Two pass":
                    model = two_pass(self.count, self.nargs, **kwa)

                wx.CallAfter(
                    pub.sendMessage,
                    "COUNT_EVT",
                    count=model["count2"],
                    duration=kwa["duration"],
                    end="CONTINUE",
                )
                tolog(model["stamp2"], logfile, openf=False)

                with subprocess.Popen(
                    model["pass2"],
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    bufsize=1,
                    text=True,
                    encoding=self.appdata["encoding"],
                    errors="replace",
                    creationflags=self.creationflags,
                ) as self.process:
                    for line2 in self.process.stderr:
                        logfile.write(f"[FFMPEG]: {line2}")
                        current_time = time.time()
                        if (current_time - last_file_flush) > flush_interval:
                            logfile.flush()
                            last_file_flush = current_time
                        if (
                            current_time - last_gui_update
                        ) > throttle_interval:
                            wx.CallAfter(
                                pub.sendMessage,
                                "UPDATE_EVT",
                                output=line2,
                                duration=kwa["duration"],
                                status=0,
                            )
                            last_gui_update = current_time

                        if self.stop_work_thread:
                            if self.fatal:
                                return
                            out = self.process.communicate()[1]
                            self.process.wait()
                            stopstr = "[VIDEOMASS]: STOP command received."
                            wx.CallAfter(
                                pub.sendMessage,
                                "ERROR_MSG_EVT",
                                msg="STOP",
                                output=stopstr,
                            )
                            logfile.write(f"{out}\n{stopstr}")

                            time.sleep(0.5)
                            wx.CallAfter(
                                pub.sendMessage, "END_EVT", filetotrash=None
                            )
                            return
                    time.sleep(2)  # WARNING need time here
                    exit_code = self.process.poll()
                    if exit_code is not None:
                        if exit_code != 0:
                            errstr = (
                                f"[VIDEOMASS]: Failed! Error "
                                f"Exit Code: {exit_code}"
                            )
                            logfile.write(errstr)
                            wx.CallAfter(
                                pub.sendMessage,
                                "ERROR_MSG_EVT",
                                msg="FAILED",
                                output=errstr,
                            )
                            time.sleep(2)
                            continue  # go to next file

                        else:
                            if not kwa["args"][1]:
                                filedone.append(kwa["source"])
                            wx.CallAfter(
                                pub.sendMessage,
                                "COUNT_EVT",
                                count="",
                                duration=kwa["duration"],
                                end="DONE",
                            )
            time.sleep(0.5)
            wx.CallAfter(pub.sendMessage, "END_EVT", filetotrash=filedone)
