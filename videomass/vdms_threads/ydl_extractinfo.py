# -*- coding: UTF-8 -*-
"""
Name: ydl_extractinfo.py
Porpose: get informations data with youtube_dl
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: May.09.2021
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
import sys
from threading import Thread
import wx
from pubsub import pub
if 'youtube_dl' in sys.modules:
    import youtube_dl
elif 'yt_dlp' in sys.modules:
    import yt_dlp


class MyLogger():
    """
    Intercepts youtube-dl's output by setting a logger object .
    Log messages to a logging.Logger instance.
    <https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd3157df2457df7274d0c842421945#embedding-youtube-dl>
    """

    def __init__(self):
        """
        make attribute to log messages error
        """
        self.msg_error = []

    def debug(self, msg):
        """
        Get debug messages
        """
        pass

    def warning(self, msg):
        """
        Get warning messages
        """
        pass

    def error(self, msg):
        """
        Get error messages
        """
        self.msg_error.append(msg)

    def get_message(self):
        """
        get message error from error method
        """
        return None if len(self.msg_error) == 0 else self.msg_error.pop()


class YdlExtractInfo(Thread):
    """
    Embed youtube-dl as module into a separated thread in order
    to get output during process (see help(youtube_dl.YoutubeDL) ) .

    """

    def __init__(self, url, ssl):
        """
        Attributes defined here:
        self.url  str('url')
        self.data  tupla(None, None)
        """
        get = wx.GetApp()  # get videomass wx.App attribute
        self.appdata = get.appset
        self.url = url
        self.data = None
        self.nocheckcertificate = ssl

        Thread.__init__(self)
        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        Defines options to extract_info with youtube_dl
        """
        mylogger = MyLogger()
        ydl_opts = {'ignoreerrors': True,
                    'noplaylist': True,
                    'no_color': True,
                    'nocheckcertificate': self.nocheckcertificate,
                    'logger': mylogger,
                    }

        if self.appdata['downloader'] == 'youtube_dl':
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                meta = ydl.extract_info(self.url, download=False)

        elif self.appdata['downloader'] == 'yt_dlp':
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                meta = ydl.extract_info(self.url, download=False)

        error = mylogger.get_message()

        if error:
            self.data = (None, error)
        elif meta:
            self.data = (meta, None)

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
