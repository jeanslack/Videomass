# -*- coding: UTF-8 -*-
"""
Name: concat_demuxer.py
Purpose: FFmpeg long processing task for Concatenation processing
Compatibility: Python >= 3.11, wxPython4 Phoenix
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
import platform
import subprocess
import time
from threading import Thread

import wx
from pubsub import pub

from videomass.vdms_io.make_filelog import tolog
from videomass.vdms_utils.utils import Popen

if platform.system() != 'Windows':
    import shlex


class ConcatDemuxer(Thread):
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
        get = wx.GetApp()  # get videomass wx.App attribute
        self.appdata = get.appset
        self.stop_work_thread = False  # process terminate
        self.logfile = args[0]  # log filename
        self.kwa = kwargs
        self.fatal = None  # fatal error I/O flag before `communicate`
        self.process = None  # process data set on context

        Thread.__init__(self)

        self.start()

    def run(self):
        """
        Subprocess initialize thread.

        """
        filedone = None
        cmd = (f'"{self.appdata["ffmpeg_cmd"]}" '
               f'{self.appdata["ffmpeg-default-args"]} '
               f'{self.appdata["ffmpeg_loglev"]} -f concat '
               f'-safe 0 -i {self.kwa["args"]} "{self.kwa["destination"]}"')

        count = (f'{self.kwa["nmax"]} Items in progress...\nSource: '
                 f'"{self.kwa["source"]}"\nDestination: '
                 f'"{self.kwa["destination"]}"'
                 )
        stamp = f'{count}\n\n[COMMAND]:\n{cmd}'

        countevt = (f'{self.kwa["nmax"]} Items in progress...\n...for '
                    f'details see Current Log.\nDestination: '
                    f'"{self.kwa["destination"]}"')

        wx.CallAfter(pub.sendMessage,
                     "COUNT_EVT",
                     count=countevt,
                     duration=self.kwa['duration'],
                     end='CONTINUE',
                     )
        tolog(stamp, self.logfile, sep=True, wdate=True)

        if platform.system() != 'Windows':
            cmd = shlex.split(cmd)
        try:
            with Popen(cmd,
                       stderr=subprocess.PIPE,
                       stdin=subprocess.PIPE,
                       bufsize=1,
                       text=True,
                       encoding=self.appdata['encoding'],
                       ) as self.process:
                for line in self.process.stderr:
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output=line,
                                 duration=self.kwa['duration'],
                                 status=0,
                                 )
                    if self.stop_work_thread:
                        if self.fatal:
                            return
                        out = self.process.communicate()[1]
                        self.process.wait()
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output='STOP',
                                     duration=self.kwa['duration'],
                                     status=1,
                                     )
                        tolog(out, self.logfile)
                        time.sleep(1)
                        wx.CallAfter(pub.sendMessage, "END_EVT",
                                     filetotrash=filedone)
                        return

                if self.process.wait():  # error
                    out = self.process.communicate()[1]
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output='FAILED',
                                 duration=self.kwa['duration'],
                                 status=self.process.wait(),
                                 )
                    tolog(f"[VIDEOMASS]: Error Exit Status: "
                          f"{self.process.wait()} {out}", self.logfile
                          )
                    time.sleep(1)

                else:  # Done
                    filedone = self.kwa["source"]
                    wx.CallAfter(pub.sendMessage,
                                 "COUNT_EVT",
                                 count='',
                                 duration='',
                                 end='DONE'
                                 )
        except (OSError, FileNotFoundError) as err:
            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=err,
                         duration=0,
                         end='ERROR',
                         )
            tolog(err, self.logfile)

        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT", filetotrash=filedone)
    # --------------------------------------------------------------------#

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
                    proc.stdin.write('q')  # stop ffmpeg
                    proc.stdin.flush()

            # Make sure the process isn't already finished
            except (BrokenPipeError, ValueError, AttributeError,
                    OSError) as err:
                self.fatal = True
                msg = "CRASH_STOP: forcing FFmpeg to terminate"
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count=f"{msg}: {err}",
                             duration=0,
                             end='ERROR',
                             )
                tolog(f"[VIDEOMASS]: {msg}: {err}", self.logfile)

                # Force event end notification to unlock GUI
                time.sleep(.5)
                wx.CallAfter(pub.sendMessage, "END_EVT", filetotrash=None)
