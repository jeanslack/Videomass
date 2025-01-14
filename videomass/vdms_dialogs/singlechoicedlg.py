# -*- coding: UTF-8 -*-
"""
Name: singlechoice.py
Porpose: shows a single choice dialog box
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.27.2024
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
import wx


class SingleChoice(wx.Dialog):
    """
    Shows a custom dialog for single-choice actions.
    This simple dialog box asks the user to select an item
    from the available options.
    Return index (int) of selected item.

    """
    get = wx.GetApp()  # get data from bootstrap
    APPICON = get.iconset['videomass']

    def __init__(self,
                 parent,
                 caption='Single Choice dialog',
                 message='Test message',
                 choices=('1', '2', '3', '4'),
                 setsel=0,
                 ):
        """
        Usage: `parent, -1` to make parent, use 'None' otherwise
        caption: the text dialog caption to display (str)
        message: message head to display on top of this dialog (str)
        choices: Two or more choice items to list (list)
        setsel: Sets the index of the initially selected item (int)

        """
        wx.Dialog.__init__(self, parent, -1,
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        # ------ Add widget controls
        sizbase = wx.BoxSizer(wx.VERTICAL)
        sizbase.Add((0, 20), 0)
        lab = wx.StaticText(self, label=message)
        sizbase.Add(lab, 0, wx.LEFT | wx.EXPAND, 5)
        sizbase.Add((0, 10), 0)
        self.listchoice = wx.ListBox(self, wx.ID_ANY,
                                     choices=choices,
                                     style=0,
                                     name='ListBox',
                                     )
        self.listchoice.SetSelection(setsel)
        sizbase.Add(self.listchoice, 1, wx.ALL | wx.EXPAND, 5)

        # ------ bottom layout buttons
        sizbott = wx.BoxSizer(wx.HORIZONTAL)
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "")
        sizbott.Add(btn_cancel, 0)
        btn_ok = wx.Button(self, wx.ID_OK)
        sizbott.Add(btn_ok, 0, wx.LEFT, 5)
        sizbase.Add(sizbott, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=5)

        # ------ Properties
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(SingleChoice.APPICON,
                                      wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetTitle(caption)
        self.SetMinSize((620, 270))
        self.SetSizer(sizbase)
        sizbase.Fit(self)
        self.Layout()

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)

    # ------------------------------------------------------------------#

    def getvalue(self):
        """
        This method return values via the interface getvalue()
        by the caller. See the caller for more info and usage.
        """
        return self.listchoice.GetSelection()

    # ----------------------Event handler (callback)----------------------#

    def on_close(self, event):
        """
        Close this dialog without saving anything
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Don't use self.Destroy() in this dialog
        """
        event.Skip()
