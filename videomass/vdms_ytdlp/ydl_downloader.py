# -*- coding: UTF-8 -*-
"""
Name: ydl_downloader.py
Porpose: long processing task using yt_dlp python library
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Apr.29.2024
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
import os
from threading import Thread
import signal
import time
import itertools
import platform
import subprocess
import wx
from pubsub import pub
from videomass.vdms_utils.utils import Popen
from videomass.vdms_io.make_filelog import logwrite
if not platform.system() == 'Windows':
    import shlex
if wx.GetApp().appset['yt_dlp'] is True:
    import yt_dlp


def killbill(pid):
    """
    kill the process sending a Ctrl+C event to yt-dlp
    """
    lambda: os.kill(pid, signal.CTRL_C_EVENT)


class YtdlExecDL(Thread):
    """
    YtdlExecDL represents a separate thread for running
    youtube-dl executable with subprocess class to download
    media and capture its stdout/stderr output in real time .

    """
    STOP = '[Videomass]: STOP command received.'
    # -----------------------------------------------------------------------#

    def __init__(self, args, urls, logfile):
        """
        Attributes defined here:
        self.stop_work_thread -  boolean process terminate value
        self.urls - type list
        self.logfile - str path object to log file
        self.arglist - option arguments list
        """
        self.stop_work_thread = False  # process terminate
        self.urls = urls
        self.logfile = logfile
        self.arglist = args
        self.countmax = len(self.arglist)
        self.count = 0

        Thread.__init__(self)
        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        Subprocess run thread.
        """
        for url, opts in itertools.zip_longest(self.urls,
                                               self.arglist,
                                               fillvalue='',
                                               ):
            self.count += 1
            count = f"URL {self.count}/{self.countmax}"

            wx.CallAfter(pub.sendMessage,
                         "COUNT_YTDL_EVT",
                         count=count,
                         fsource=f'Source: {url}',
                         destination='',
                         duration=100,
                         end='CONTINUE',
                         )
            cmd = f'{opts} "{url}"'
            logwrite(f'{count}\n{cmd}\n', '', self.logfile)  # write log cmd
            if not platform.system() == 'Windows':
                cmd = shlex.split(cmd)
            try:
                with Popen(cmd,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           bufsize=1,
                           universal_newlines=True,
                           encoding='utf-8',
                           ) as proc:
                    for line in proc.stdout:
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_YDL_EXECUTABLE_EVT",
                                     output=line,
                                     duration=100,
                                     status=0,
                                     )
                        if self.stop_work_thread:
                            killbill(proc.pid)
                            wx.CallAfter(pub.sendMessage,
                                         "UPDATE_YDL_EXECUTABLE_EVT",
                                         output='STOP',
                                         duration=100,
                                         status='ERROR',
                                         )
                            logwrite('', YtdlExecDL.STOP, self.logfile)
                            time.sleep(.5)
                            wx.CallAfter(pub.sendMessage, "END_YTDL_EVT")
                            return

                    if proc.wait():
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_YDL_EXECUTABLE_EVT",
                                     output='FAILED',
                                     duration=100,
                                     status='ERROR',
                                     )
                        logwrite('', (f"[VIDEOMASS]: Error Exit Status: "
                                      f"{proc.wait()}"), self.logfile)
                        time.sleep(1)
                        continue

            except (OSError, FileNotFoundError) as err:
                wx.CallAfter(pub.sendMessage,
                             "COUNT_YTDL_EVT",
                             count=err,
                             fsource='',
                             destination='',
                             duration=0,
                             end='ERROR'
                             )
                logwrite('', err, self.logfile)
                break

            if proc.wait() == 0:  # ..Finished
                wx.CallAfter(pub.sendMessage,
                             "COUNT_YTDL_EVT",
                             count='',
                             fsource='',
                             destination='',
                             duration=100,
                             end='DONE',
                             )
                time.sleep(1)
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_YTDL_EVT")
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
# ------------------------------------------------------------------------#


class MyLogger:
    """
    Intercepts youtube-dl's output by setting a logger object;
    * Log messages to a logging.Logger instance.
    <https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd315
    7df2457df7274d0c842421945#embedding-youtube-dl>
    """

    def __init__(self):
        """
        define instace attributes
        """
        self.msg = None

    def debug(self, msg):
        """
        Get debug messages. Note, both debug and info
        are passed into debug. You can distinguish them
        by the prefix '[debug] '
        """
        wx.CallAfter(pub.sendMessage,
                     "UPDATE_YDL_EVT",
                     output=msg,
                     duration='',
                     status='DEBUG',
                     )
        self.msg = msg

    def warning(self, msg):
        """
        Get warning messages
        """
        msg = f'WARNING: {msg}'
        wx.CallAfter(pub.sendMessage,
                     "UPDATE_YDL_EVT",
                     output=msg,
                     duration='',
                     status='WARNING',
                     )

    def error(self, msg):
        """
        Get error messages
        """
        wx.CallAfter(pub.sendMessage,
                     "UPDATE_YDL_EVT",
                     output=msg,
                     duration='',
                     status='ERROR',
                     )
# -------------------------------------------------------------------------#


def my_hook(data):
    """
    progress_hooks is A list of functions that get called on
    download progress. See  `help(youtube_dl.YoutubeDL)`
    """
    if data['status'] == 'downloading':
        keys = ('_percent_str', '_total_bytes_str', '_speed_str', '_eta_str')

        wx.CallAfter(pub.sendMessage,
                     "UPDATE_YDL_EVT",
                     output='',
                     duration={x: data.get(x, 'N/A') for x in keys},
                     status='DOWNLOAD',
                     )
    if data['status'] == 'finished':
        wx.CallAfter(pub.sendMessage,
                     "COUNT_YTDL_EVT",
                     count='',
                     fsource='',
                     destination='',
                     duration='',
                     end='DONE',
                     )
        wx.CallAfter(pub.sendMessage,
                     "UPDATE_YDL_EVT",
                     output='',
                     duration='Done downloading, now converting ...',
                     status='FINISHED',
                     )
# -------------------------------------------------------------------------#


class YdlDownloader(Thread):
    """
    Embed youtube-dl as module into a separated thread in order
    to get output in real time during downloading and conversion .
    For a list of available options see:

    <https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L129-L279>
    <https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/options.py>

    or by help(youtube_dl.YoutubeDL)

    """
    def __init__(self, args, urls, logfile):
        """
        Attributes defined here:
        self.stop_work_thread -  boolean process terminate value
        self.urls - type list
        self.logfile - str path object to log file
        self.arglist - option arguments list
        """
        self.stop_work_thread = False  # process terminate
        self.urls = urls
        self.logfile = logfile
        self.arglist = args
        self.countmax = len(self.arglist)
        self.count = 0

        Thread.__init__(self)
        self.start()  # run()

    def run(self):
        """
        Apply the option arguments passed by
        the user for the download process.
        """
        for url, opts in itertools.zip_longest(self.urls,
                                               self.arglist,
                                               fillvalue='',
                                               ):
            if not opts['format']:
                del opts['format']
            self.count += 1
            count = f"URL {self.count}/{self.countmax}"

            wx.CallAfter(pub.sendMessage,
                         "COUNT_YTDL_EVT",
                         count=count,
                         fsource=f'Source: {url}',
                         destination='',
                         duration=100,
                         end='CONTINUE',
                         )
            if self.stop_work_thread:
                break
            ydl_opts = {**opts,
                        'logger': MyLogger(),
                        'progress_hooks': [my_hook],
                        }
            logtxt = f'{count}\n{ydl_opts}'
            logwrite(logtxt, '', self.logfile)  # write log cmd
            if wx.GetApp().appset['yt_dlp'] is True:
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([f"{url}"])
                except Exception:
                    break

        wx.CallAfter(pub.sendMessage, "END_YTDL_EVT")

    def stop(self):
        """
        Sets the stop work thread to
        terminate the current process
        """
        self.stop_work_thread = True
