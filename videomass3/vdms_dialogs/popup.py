# -*- coding: UTF-8 -*-
# Name: popup.py
# Porpose: shows a small waiting dialogue
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
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
from pubsub import pub


class PopupDialog(wx.Dialog):
    """
    A pop-up dialog box for temporary user messages that tell the user
    the load in progress (required for large files).

    Usage:
            loadDlg = PopupDialog(None, ("Videomass - Loading"),
                                  ("\nWait....\nwork in progress.\n")
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
        box2.Add(graphic, 0, wx.EXPAND | wx.ALL, 10)
        # Add the message
        message = wx.StaticText(self, -1, msg)
        box2.Add(message, 0, wx.EXPAND | wx.ALL, 10)
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
