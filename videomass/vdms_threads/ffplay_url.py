# -*- coding: UTF-8 -*-
"""
Name: ffplay_url.py
Porpose: playback online media streams with ffplay player using
         youtube_dl embedding on code.
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.02.2022
Code checker:
    flake8: --ignore F821, W504
    pylint: --ignore E0602, E1101

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
import sys
from threading import Thread
import wx
from pubsub import pub
from videomass.vdms_io import io_tools
if 'youtube_dl' in sys.modules:
    import youtube_dl
elif 'yt_dlp' in sys.modules:
    import yt_dlp


def msg_error(msg):
    """
    Receive error messages via wxCallafter
    """
    wx.MessageBox(f"{msg}", "Videomass", wx.ICON_ERROR)
# ------------------------------------------------------------------------#


def msg_warning(msg):
    """
    Receive info messages via wxCallafter
    """
    wx.MessageBox(f"{msg}", "Videomass", wx.ICON_INFORMATION)
# ------------------------------------------------------------------------#


class MyLogger():
    """
    Intercepts youtube-dl's output by setting a logger object;
    * Log messages to a logging.Logger instance.
    <https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd31
    57df2457df7274d0c842421945#embedding-youtube-dl>
    """

    def __init__(self):
        """Initialize"""
        self.msg = None

    def debug(self, msg):
        """intercept msg"""
        # print('DEBUG: ', msg)
        if '[download]' in msg:  # ...in processing
            # print(msg)
            if 'Destination' in msg:
                # print(msg)
                pub.sendMessage("START_FFPLAY_EVT",
                                output=msg.split()[2]
                                )
            elif 'has already been downloaded' in msg:
                pub.sendMessage("START_FFPLAY_EVT",
                                output=msg.split()[1]
                                )
        self.msg = msg

    def warning(self, msg):
        """send warning messages to masg_"""
        wx.CallAfter(msg_warning, msg)

    def error(self, msg):
        """send message errors"""
        wx.CallAfter(msg_error, msg)
# -------------------------------------------------------------------------#


class DownloadStream(Thread):
    """
    Download media stream to the videomass cache directory with
    the same quality defined in the `quality` parameter.
    This Thread use embedding youtube_dl package.
    WARNING FIXME stop thead does not work since youtube_dl.YoutubeDL
                  library does not yet have an interface for stopping
                  unfinished downloads.

    The file name form stored on cache dir. is

            "title_" + "quality" + ".format"

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    OS = get.appset['ostype']
    FFMPEG_URL = get.appset['ffmpeg_cmd']
    TMP = os.path.join(get.appset['cachedir'], 'tmp')
    APP = get.appset['app']
    DOWNLOADER = get.appset['downloader']

    def __init__(self, url, quality, ssl):
        """
        Accept a single url as a string.
        The quality parameter sets the quality of the stream
        in the form required by youtube-dl, e.g one of the
        following strings can be valid:
            worst, best, bestvideo+bestaudio, Format Code

        """
        self.stop_work_thread = False  # process terminate value
        self.url = url  # single url
        self.quality = quality  # output quality e.g. worst, best, Format code
        self.nocheckcertificate = ssl
        self.outputdir = DownloadStream.TMP  # pathname destination
        self.outtmpl = f'%(title)s_{self.quality}.%(ext)s'  # filename

        Thread.__init__(self)
    # --------------------------------------------------------------#

    def run(self):
        """
        This atipic method is called by start() method after the instance
        this class. see Streaming class below.
        """
        if self.stop_work_thread:
            return

        ydl_opts = {
            'format': self.quality,
            'outtmpl': f'{self.outputdir}/{self.outtmpl}',
            'restrictfilenames': True,
            'nopart': True,  # see --no-part by --help
            'ignoreerrors': True,
            'continue': True,
            'no_warnings': False,
            'noplaylist': True,
            'no_color': True,
            'nocheckcertificate': self.nocheckcertificate,
            'ffmpeg_location': f'{DownloadStream.FFMPEG_URL}',
            'logger': MyLogger(),
        }
        if DownloadStream.DOWNLOADER == 'yt_dlp':
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"{self.url}"])

        elif DownloadStream.DOWNLOADER == 'youtube_dl':
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"{self.url}"])
    # --------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
# ------------------------------------------------------------------------#


class Streaming():
    """
    Handling Threads to download and playback media streams via
    youtube-dl library and ffmpeg executables.

    DOWNLOAD class variable makes the object's attributes available
    even outside of class, see `stop_download_listener()`
    FIXME put RICEIVER LISTENER function as methods of this class. For
          now does not work (???)

    """
    DOWNLOAD = None  # set instance thread
    TIMESTAMP = None
    AUTOEXIT = None
    # ---------------------------------------------------------------#

    def __init__(self, timestamp, autoexit, ssl, url=None, quality=None):
        """
        - Topic "START_FFPLAY_EVT" subscribes the start playing
          running ffplay at a certain time.
        - Topic "STOP_DOWNLOAD_EVT" subscribes a stop download listener
          which call the stop() method of `DownloadStream` class to
          stop the download when ffplay has finished or been closed by
          the user.
        """
        pub.subscribe(stop_download_listener, "STOP_DOWNLOAD_EVT")
        pub.subscribe(start_palying_listener, "START_FFPLAY_EVT")

        Streaming.DOWNLOAD = DownloadStream(url, quality, ssl)
        Streaming.TIMESTAMP = timestamp
        Streaming.AUTOEXIT = autoexit

        self.start_download()
    # ----------------------------------------------------------------#

    def start_download(self):
        """
        call DownloadStream(Thread) to run() method
        """
        Streaming.DOWNLOAD.start()

# --------- RECEIVER LISTENERS


def stop_download_listener(filename):
    """
    Receive message from ffplay_file.FilePlay class
    for handle interruption
    """
    Streaming.DOWNLOAD.stop()
    Streaming.DOWNLOAD.join()  # if join, wait end process


def start_palying_listener(output):
    """
    Riceive messages from MyLogger to start
    ffplay in at a given time.
    """
    io_tools.stream_play(output,
                         '',
                         Streaming.TIMESTAMP,
                         Streaming.AUTOEXIT
                         )
