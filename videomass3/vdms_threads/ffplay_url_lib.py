# -*- coding: UTF-8 -*-
# Name: ffplay_url_lib.py
# Porpose: playback online media streams with ffplay player using
#          youtube_dl embedding on code.
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: September.09.2020 *PEP8 compatible*
#########################################################
# This file is part of Videomass.

#    Videomass is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass.  If not, see <http://www.gnu.org/licenses/>.

#########################################################
import wx
import os
import sys
from threading import Thread
import time
from pubsub import pub
try:
    import youtube_dl
except (ModuleNotFoundError, ImportError) as nomodule:
    pass
from videomass3.vdms_io import IO_tools


def msg_Error(msg):
    """
    Receive error messages via wxCallafter
    """
    wx.MessageBox("%s" % (msg), "Videomass", wx.ICON_ERROR)
# ------------------------------------------------------------------------#


def msg_Warning(msg):
    """
    Receive info messages via wxCallafter
    """
    wx.MessageBox("%s" % (msg), "Videomass", wx.ICON_INFORMATION)
# ------------------------------------------------------------------------#


class MyLogger(object):
    """
    Intercepts youtube-dl's output by setting a logger object;
    * Log messages to a logging.Logger instance.
    <https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd31
    57df2457df7274d0c842421945#embedding-youtube-dl>
    """
    def debug(self, msg):
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
        wx.CallAfter(msg_Warning, msg)

    def error(self, msg):
        """send message errors"""
        wx.CallAfter(msg_Error, msg)
# -------------------------------------------------------------------------#


class Download_Stream(Thread):
    """
    Download media stream to the videomass cache directory with
    the same quality defined in the `quality` parameter.
    This Thread use embedding youtube_dl package.
    WARNING FIXME stop thead does not work since youtube_dl.YoutubeDL
                  library does not yet have an interface for stopping
                  unfinished downloads.

    The file name form stored on cache dir. is

            "title_" + "quality" + ".format"

    NOTE see also ffplay_url_exec.py on sources directory.

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    OS = get.OS
    FFMPEG_URL = get.FFMPEG_url
    CACHEDIR = get.CACHEdir
    TMP = get.TMP

    def __init__(self, url, quality):
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
        self.outputdir = Download_Stream.TMP  # pathname destination
        self.outtmpl = '%(title)s_{}.%(ext)s'.format(self.quality)  # filename
        if Download_Stream.OS == 'Windows' or '/tmp/.mount_' \
           in sys.executable or os.path.exists(os.getcwd() + '/AppRun'):
            self.nocheckcertificate = True
        else:
            self.nocheckcertificate = False

        Thread.__init__(self)
        """initialize"""
    # --------------------------------------------------------------#

    def run(self):
        """
        This atipic method is called by start() method after the instance
        this class. see Lib_Streaming class below.
        """
        if self.stop_work_thread:
            return

        ydl_opts = {
                'format': self.quality,
                'outtmpl': '{}/{}'.format(self.outputdir, self.outtmpl),
                'restrictfilenames': True,
                'nopart': True,  # see --no-part by --help
                'ignoreerrors': True,
                'continue': True,
                'no_warnings': False,
                'noplaylist': True,
                'no_color': True,
                'nocheckcertificate': self.nocheckcertificate,
                'ffmpeg_location': '{}'.format(Download_Stream.FFMPEG_URL),
                'logger': MyLogger(),
                    }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(["{}".format(self.url)])
    # --------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
# ------------------------------------------------------------------------#


class Lib_Streaming(object):
    """
    Handling Threads to download and playback media streams via
    youtube-dl library and ffmpeg executables.

    DOWNLOAD class variable makes the object's attributes available
    even outside of class, see `stop_download_listener()`
    FIXME put RICEIVER LISTENER function as methods of this class. For
          now does not work (???)

    """
    DOWNLOAD = None  # set instance thread
    # ---------------------------------------------------------------#

    def __init__(self, url=None, quality=None):
        """
        - Topic "START_FFPLAY_EVT" subscribes the start playing
          running ffplay at a certain time.
        - Topic "STOP_DOWNLOAD_EVT" subscribes a stop download listener
          which call the stop() method of `Download_Stream` class to
          stop the download when ffplay has finished or been closed by
          the user.
        """
        pub.subscribe(stop_download_listener, "STOP_DOWNLOAD_EVT")
        pub.subscribe(start_palying_listener, "START_FFPLAY_EVT")

        Lib_Streaming.DOWNLOAD = Download_Stream(url, quality)

        self.start_download()
    # ----------------------------------------------------------------#

    def start_download(self):
        """
        call Download_Stream(Thread) to run() method
        """
        Lib_Streaming.DOWNLOAD.start()
        return

# --------- RECEIVER LISTENERS


def stop_download_listener(filename):
    """
    Receive message from ffplay_file.File_Play class
    for handle interruption
    """
    Lib_Streaming.DOWNLOAD.stop()
    Lib_Streaming.DOWNLOAD.join()  # if join, wait end process


def start_palying_listener(output):
    """
    Riceive messages from MyLogger to start
    ffplay in at a given time.
    """
    IO_tools.stream_play(output, '', '')
    return
