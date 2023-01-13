# -*- coding: UTF-8 -*-
"""
Name: epilogue.py
Porpose: shows dialog box before start process
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Dec.31.2022
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
import wx.lib.scrolledpanel as scrolled


class Formula(wx.Dialog):
    """
    Show a dialog box before run process.

    Example:
            settings = ("\nEXAMPLES:\n\nExample 1:\nExample 2:\n etc."
            param = ("type 1\ntype 2\ntype 3\n etc."
    """
    def __init__(self, parent, settings, param, panelsize):

        get = wx.GetApp()  # get data from bootstrap
        colorscheme = get.appset['icontheme'][1]

        wx.Dialog.__init__(self, parent, -1,
                           style=wx.DEFAULT_DIALOG_STYLE
                           | wx.RESIZE_BORDER
                           )
        sizbase = wx.BoxSizer(wx.VERTICAL)
        panelscroll = scrolled.ScrolledPanel(self, wx.ID_ANY,
                                             size=panelsize,
                                             style=wx.TAB_TRAVERSAL
                                             | wx.BORDER_THEME,
                                             name="panelscr",
                                             )
        sizbase.Add(panelscroll, 1, wx.ALL | wx.EXPAND, 5)
        label1 = wx.StaticText(panelscroll, wx.ID_ANY, settings)
        label2 = wx.StaticText(panelscroll, wx.ID_ANY, param)
        panelscroll.SetBackgroundColour(colorscheme['BACKGRD'])
        label2.SetForegroundColour(colorscheme['TXT1'])
        label1.SetForegroundColour(colorscheme['TXT3'])
        grid_pan = wx.BoxSizer(wx.HORIZONTAL)
        grid_pan.Add(label1, 0, wx.ALL
                     | wx.ALIGN_CENTRE_VERTICAL
                     | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        grid_pan.Add(label2, 0, wx.ALL
                     | wx.ALIGN_CENTRE_VERTICAL
                     | wx.ALIGN_CENTRE_HORIZONTAL, 5)

        panelscroll.SetSizer(grid_pan)
        panelscroll.SetAutoLayout(1)
        panelscroll.SetupScrolling()

        btncancel = wx.Button(self, wx.ID_CANCEL, "")
        btnok = wx.Button(self, wx.ID_OK, "")
        btngrid = wx.FlexGridSizer(1, 2, 0, 0)
        btngrid.Add(btncancel, 0, wx.ALL, 5)
        btngrid.Add(btnok, 0, wx.ALL, 5)
        sizbase.Add(btngrid, flag=wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=0)

        self.SetTitle(_('Confirm Settings'))
        self.SetSizer(sizbase)
        sizbase.Fit(self)
        self.Layout()
        # ----------------------Binders (EVT)--------------------#
        self.Bind(wx.EVT_BUTTON, self.on_cancel, btncancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btnok)

        # --------------  Event handler (callback)  --------------#

    def on_cancel(self, event):
        """
        exit from formula dialog
        """
        # self.Destroy()
        event.Skip()

    def on_ok(self, event):
        """
        get confirmation to proceed
        """
        # self.Destroy()
        event.Skip()
