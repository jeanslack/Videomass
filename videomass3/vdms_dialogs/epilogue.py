# -*- coding: UTF-8 -*-
# Name: epilogue.py
# Porpose: show dialog box before start process
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Aug.16.2020 *PEP8 compatible*
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


class Formula(wx.Dialog):
    """
   Show a dialog box before run process. It accept a couple
   of tuples: settingss and parameters.

   Example:
            settings = ("\nEXAMPLES:\n\\nExample 1:\nExample 2:\n etc."
            param = ("type 1\ntype 2\ntype 3\n etc."
    """
    def __init__(self, parent, settings, param, title):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)

        panel = wx.Panel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        label1 = wx.StaticText(panel, wx.ID_ANY, settings)
        label2 = wx.StaticText(panel, wx.ID_ANY, param)
        self.button_1 = wx.Button(self, wx.ID_CANCEL, "")
        self.button_2 = wx.Button(self, wx.ID_OK, "")

        # ----------------------Properties----------------------#
        self.SetTitle(title)
        panel.SetBackgroundColour('#262222')
        label1.SetForegroundColour('#008000')
        label2.SetForegroundColour('#959595')

        # ---------------------- Layout ----------------------#
        s1 = wx.BoxSizer(wx.VERTICAL)
        gr_s1 = wx.FlexGridSizer(1, 2, 0, 0)
        gr_s1.Add(label1, 0, wx.ALL, 5)
        gr_s1.Add(label2, 0, wx.ALL, 5)
        btngrid = wx.FlexGridSizer(1, 2, 0, 0)
        btngrid.Add(self.button_1, 0, wx.ALL, 5)
        btngrid.Add(self.button_2, 0, wx.ALL, 5)
        panel.SetSizer(gr_s1)
        s1.Add(panel, 1, wx.ALL | wx.EXPAND, 5)
        s1.Add(btngrid, flag=wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=0)
        self.SetSizer(s1)
        s1.Fit(self)
        self.Layout()
        # ----------------------Binders (EVT)--------------------#
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.button_2)

        # --------------  Event handler (callback)  --------------#

    def on_cancel(self, event):
        # self.Destroy()
        event.Skip()

    def on_ok(self, event):
        # self.Destroy()
        event.Skip()
