# -*- coding: UTF-8 -*-
"""
Name: concat_demuxer.py
Porpose: FFmpeg long processing task for Concatenation processing
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.08.2024
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
from threading import Thread
import time
import subprocess
import platform
import wx
from pubsub import pub
from videomass.vdms_utils.utils import Popen
from videomass.vdms_io.make_filelog import logwrite
if not platform.system() == 'Windows':
    import shlex


class ConcatDemuxer(Thread):
    """
    This class represents a separate thread for running processes,
    which need to read the stdout/stderr in real time.

    NOTE capturing output in real-time (Windows, Unix):

    https://stackoverflow.com/questions/1388753/how-to-get-output-
    from-subprocess-popen-proc-stdout-readline-blocks-no-dat?rq=1
    """
    get = wx.GetApp()  # get videomass wx.App attribute
    appdata = get.appset
    SUFFIX = appdata['filesuffix']
    NOT_EXIST_MSG = _("Is 'ffmpeg' installed on your system?")
    # ---------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        """
        Called from `long_processing_task.topic_thread`.
        Also see `main_frame.switch_to_processing`.

        """
        self.stop_work_thread = False  # process terminate
        self.logfile = args[0]  # log filename
        self.kwa = kwargs

        Thread.__init__(self)

        self.start()

    def run(self):
        """
        Subprocess initialize thread.

        """
        filedone = None
        cmd = (f'"{ConcatDemuxer.appdata["ffmpeg_cmd"]}" '
               f'{ConcatDemuxer.appdata["ffmpeg_default_args"]} -f concat '
               f'-safe 0 -i {self.kwa["args"]} "{self.kwa["destination"]}"')

        count = (f'{self.kwa["nmax"]} Items in progress...\nSource: '
                 f'"{self.kwa["source"]}"\nDestination: '
                 f'"{self.kwa["destination"]}"'
                 )
        stamp = (f'{count}\n\n[COMMAND]:\n{cmd}')

        countevt = (f'{self.kwa["nmax"]} Items in progress...\n...for '
                    f'details see Current Log.\nDestination: '
                    f'"{self.kwa["destination"]}"')

        wx.CallAfter(pub.sendMessage,
                     "COUNT_EVT",
                     count=countevt,
                     duration=self.kwa['duration'],
                     end='',
                     )
        logwrite(stamp, '', self.logfile)  # write n/n + command only

        if not platform.system() == 'Windows':
            cmd = shlex.split(cmd)
        try:
            with Popen(cmd,
                       stderr=subprocess.PIPE,
                       bufsize=1,
                       universal_newlines=True,
                       encoding='utf8',
                       ) as proc:
                for line in proc.stderr:
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output=line,
                                 duration=self.kwa['duration'],
                                 status=0,
                                 )
                    if self.stop_work_thread:
                        proc.terminate()
                        break  # break second 'for' loop

                if proc.wait():  # error
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output='',
                                 duration=self.kwa['duration'],
                                 status=proc.wait(),
                                 )
                    logwrite('',
                             f"Exit status: {proc.wait}",
                             self.logfile)  # append exit error number
                else:  # ok
                    filedone = self.kwa["source"]
                    wx.CallAfter(pub.sendMessage,
                                 "COUNT_EVT",
                                 count='',
                                 duration='',
                                 end='Done'
                                 )
        except (OSError, FileNotFoundError) as err:
            excepterr = f"{err}\n  {ConcatDemuxer.NOT_EXIST_MSG}"
            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=excepterr,
                         duration=0,
                         end='error',
                         )

        if self.stop_work_thread:
            proc.terminate()

        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT", filetotrash=filedone)
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
