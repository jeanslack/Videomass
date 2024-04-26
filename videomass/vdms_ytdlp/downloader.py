# -*- coding: UTF-8 -*-
"""
Name: ydl_downloader.py
Porpose: long processing task using yt_dlp python library
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Apr.09.2024
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
#from multiprocessing import Process
#import time
#import signal
#import os
#from videomass.vdms_utils.utils import Popen


import sys
import json
import yt_dlp


#class Stop_Download(Exception): # This is our own special Exception class
#     pass
#
#def usr1_handler(signum, frame): # When signal comes, run this func
#     raise Stop_Download


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
        # wx.CallAfter(pub.sendMessage,
        #              "UPDATE_YDL_EVT",
        #              output=msg,
        #              duration='',
        #              status='DEBUG',
        #              )
        self.msg = msg
        #return '---debug----:', msg

    def warning(self, msg):
        """
        Get warning messages
        """
        msg = f'WARNING: {msg}'
        #return '---warning----:', msg
        # wx.CallAfter(pub.sendMessage,
        #              "UPDATE_YDL_EVT",
        #              output=msg,
        #              duration='',
        #              status='WARNING',
        #              )

    def error(self, msg):
        """
        Get error messages
        """
        # wx.CallAfter(pub.sendMessage,
        #              "UPDATE_YDL_EVT",
        #              output=msg,
        #              duration='',
        #              status='ERROR',
        #              )
        #return '---error----:', msg
        msg
# -------------------------------------------------------------------------#


def my_hook(data):
    """
    progress_hooks is A list of functions that get called on
    download progress. See  `help(youtube_dl.YoutubeDL)`
    """
    if data['status'] == 'downloading':
        keys = ('_percent_str', '_total_bytes_str', '_speed_str', '_eta_str')
        # wx.CallAfter(pub.sendMessage,
        #              "UPDATE_YDL_EVT",
        #              output='',
        #              duration={x: data.get(x, 'N/A') for x in keys},
        #              status='DOWNLOAD',
        #              )
        '---download----:', {x: data.get(x, 'N/A') for x in keys}
    if data['status'] == 'finished':
        # wx.CallAfter(pub.sendMessage,
        #              "COUNT_YTDL_EVT",
        #              count='',
        #              fsource='',
        #              destination='',
        #              duration='',
        #              end='ok',
        #              )
        # wx.CallAfter(pub.sendMessage,
        #              "UPDATE_YDL_EVT",
        #              output='',
        #              duration='Done downloading, now converting ...',
        #              status='FINISHED',
        #              )
        '---finished----:', 'Done downloading, now converting ...'
# -------------------------------------------------------------------------#


def download(args, url):
    """
    Apply the option arguments passed by
    the user for the download process.
    """
    ydl_opts = {**args,
                'logger': MyLogger(),
                'progress_hooks': [my_hook],
                }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"{url}"])
    except Exception as err:
        return err

    return None


class MyProcessing():

    def __init__(self, args, urls, logfile):
        self.stop_work_thread = False  # process terminate
        #self.urls = urls
        #self.logfile = logfile
        #self.arglist = args
        #self.countmax = len(self.arglist)
        #self.count = 0
        self.p1 = None
        self.proc = None
        self.execute = YdlDownloader(args, urls, logfile)

        #Thread.__init__(self)

    def process_start(self):

        # with Popen(['python', self.execute.run] ,
        #            stderr=subprocess.PIPE,
        #            stdin=subprocess.PIPE,
        #            universal_newlines=True,
        #            encoding='utf-8',
        #            ) as self.proc:

        #resume_event=multiprocessing.Event()
        self.p1 = multiprocessing.Process(target=self.execute.run)
        self.p1.start()
        print("mp start")



    def stop(self):
        """
        Sets the stop work thread to
        terminate the current process
        """
        self.stop_work_thread = True
        os.kill(self.p1.pid, signal.SIGUSR2)
        #lambda: os.kill(self.p1.pid, CTRL_C_EVENT)


#     def getpid(self):
#
#         return(self.proc.pid)

if __name__ == '__main__':
    opts = json.loads(sys.argv[1])
    url = sys.argv[2]
    data = download(opts, url)




