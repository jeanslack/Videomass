# -*- coding: UTF-8 -*-

#########################################################
# Name: ydl_extract.py
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
from __future__ import unicode_literals
try:
    import youtube_dl
except ModuleNotFoundError as noydl:
    print(noydl)
import wx
from pubsub import pub
from threading import Thread

# get data from bootstrap
get = wx.GetApp()
OS = get.OS


class PopupDialog(wx.Dialog):
    """
    A pop-up dialog box for temporary user messages that tell the user
    the load in progress (required for large files).

    Usage:
            loadDlg = PopupDialog(None, ("Videomass - Loading..."),
                        ("\nAttendi....\nSto eseguendo un processo .\n")
                                )
            loadDlg.ShowModal()

            loadDlg.Destroy()
    """
    def __init__(self, parent, title, msg):
        # Create a dialog
        wx.Dialog.__init__(self, parent, -1, title, size=(350, 150),
                           style=wx.CAPTION)
        # Add sizers
        box = wx.BoxSizer(wx.VERTICAL)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        # Add an Info graphic
        bitmap = wx.Bitmap(32, 32)
        bitmap = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION,
                                          wx.ART_MESSAGE_BOX, (32, 32)
                                          )
        graphic = wx.StaticBitmap(self, -1, bitmap)
        box2.Add(graphic, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 10)
        # Add the message
        message = wx.StaticText(self, -1, msg)
        box2.Add(message, 0, wx.EXPAND | wx.ALIGN_CENTER
                                       | wx.ALIGN_CENTER_VERTICAL
                                       | wx.ALL, 10)
        box.Add(box2, 0, wx.EXPAND)
        # Handle layout
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Fit()
        self.Layout()

        pub.subscribe(self.getMessage, "RESULT_EVT")
    # ----------------------------------------------------------#

    def getMessage(self, status):
        """
        Riceive msg and status from thread.
        All'inizio usavo self.Destroy() per chiudere il dialogo modale
        (con modeless ritornava dati None), ma dava warning e critical
        e su OsX non chiudeva affatto. Con EndModal ho risolto tutti
        i problemi e funziona bene. Ma devi ricordarti di eseguire
        Destroy() dopo ShowModal() nel chiamante.
        vedi: https://github.com/wxWidgets/Phoenix/issues/672
        Penso sia fattibile anche implementare un'interfaccia GetValue
        su questo dialogo, ma si perderebbe un po' di portabilità.
        """

        # self.Destroy() # do not work
        self.EndModal(1)
#######################################################################


class MyLogger(object):
    """
    Intercepts youtube-dl's output by setting a logger object.
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
#########################################################################


class Extract_Info(Thread):
    """
    Embed youtube-dl as module into a separated thread in order
    to get output during extract informations.
    See help(youtube_dl.YoutubeDL)
    """
    def __init__(self, url):
        """
        self.url  str('url')
        self.data  tupla(None, None)
        """
        Thread.__init__(self)
        """initialize"""
        self.url = url
        self.data = None
        if OS == 'Windows':
            self.nocheckcertificate = True
        else:
            self.nocheckcertificate = False

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
