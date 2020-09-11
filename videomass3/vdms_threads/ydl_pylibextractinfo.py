# -*- coding: UTF-8 -*-
# Name: ydl_pylibextractinfo.py
# Porpose: get informations data with youtube_dl
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2019/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.06.2020 *PEP8 compatible*
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
import sys
import os
from pubsub import pub
from threading import Thread
try:
    import youtube_dl
except (ModuleNotFoundError, ImportError) as nomodule:
    pass


class MyLogger(object):
    """
    Intercepts youtube-dl's output by setting a logger object .
    Log messages to a logging.Logger instance.
    https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd3157df2457df7274d0c842421945#embedding-youtube-dl
    """
    def __init__(self):
        """
        make attribute to log messages error
        """
        self.msg_error = []

    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        self.msg_error.append(msg)

    def get_message(self):
        """
        get message error from error method
        """
        return None if not len(self.msg_error) else self.msg_error.pop()


class Ydl_EI_Pylib(Thread):
    """
    Embed youtube-dl as module into a separated thread in order
    to get output during process (see help(youtube_dl.YoutubeDL) ) .

    """
    get = wx.GetApp()  # get data from bootstrap
    OS = get.OS

    def __init__(self, url):
        """
        Attributes defined here:
        self.url  str('url')
        self.data  tupla(None, None)
        """
        self.url = url
        self.data = None
        if Ydl_EI_Pylib.OS == 'Windows' or '/tmp/.mount_' \
           in sys.executable or os.path.exists(os.getcwd() + '/AppRun'):
            self.nocheckcertificate = True
        else:
            self.nocheckcertificate = False

        Thread.__init__(self)
        """initialize"""
        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        """
        mylogger = MyLogger()
        ydl_opts = {'ignoreerrors': True,
                    'noplaylist': True,
                    'no_color': True,
                    'nocheckcertificate': self.nocheckcertificate,
                    'logger': mylogger,
                    }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
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
