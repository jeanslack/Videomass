# -*- coding: UTF-8 -*-
# Name: ffmpeg_formats.py
# Porpose: Show the available formats on the FFmpeg
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
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


class FFmpeg_formats(wx.MiniFrame):
    """
    It shows a dialog box with a pretty kind of GUI to view
    the formats available on FFmpeg

    """
    def __init__(self, dict_formats, OS):
        """
        with 'None' not depend from parent:
        wx.Dialog.__init__(self, None, style=wx.DEFAULT_DIALOG_STYLE)

        With parent, -1:
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        if close videomass also close parent window:

        """
        wx.MiniFrame.__init__(self, None, style=wx.RESIZE_BORDER | wx.CAPTION |
                              wx.CLOSE_BOX | wx.SYSTEM_MENU
                              )
        # add panel
        self.panel = wx.Panel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(self.panel, wx.ID_ANY)
        sizer_base.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        # ----- nb1
        notebook_pane_1 = wx.Panel(notebook, wx.ID_ANY)
        dmx = wx.ListCtrl(notebook_pane_1,
                          wx.ID_ANY,
                          style=wx.LC_REPORT |
                          wx.SUNKEN_BORDER
                          )
        sizer_tab1 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab1.Add(dmx, 1, wx.ALL | wx.EXPAND, 5)
        notebook_pane_1.SetSizer(sizer_tab1)
        notebook.AddPage(notebook_pane_1, (_("Demuxing only")))
        # ----- nb2
        notebook_pane_2 = wx.Panel(notebook, wx.ID_ANY)
        mx = wx.ListCtrl(notebook_pane_2,
                         wx.ID_ANY,
                         style=wx.LC_REPORT |
                         wx.SUNKEN_BORDER
                         )
        sizer_tab2 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab2.Add(mx, 1, wx.ALL | wx.EXPAND, 5)
        notebook_pane_2.SetSizer(sizer_tab2)
        notebook.AddPage(notebook_pane_2, (_("Muxing only")))
        # ----- nb3
        notebook_pane_3 = wx.Panel(notebook, wx.ID_ANY)
        dmx_mx = wx.ListCtrl(notebook_pane_3,
                             wx.ID_ANY,
                             style=wx.LC_REPORT |
                             wx.SUNKEN_BORDER
                             )
        sizer_tab3 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab3.Add(dmx_mx, 1, wx.ALL | wx.EXPAND, 5)
        notebook_pane_3.SetSizer(sizer_tab3)
        notebook.AddPage(notebook_pane_3, (_("Demuxing/Muxing support")))

        # ----- btns
        button_close = wx.Button(self.panel, wx.ID_CLOSE, "")
        grid_buttons = wx.GridSizer(1, 1, 0, 0)
        grid_buttons.Add(button_close, 1, wx.ALL, 5)
        sizer_base.Add(grid_buttons, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=0)
        self.panel.SetSizerAndFit(sizer_base)
        self.Layout()
        # ----------------------Properties----------------------#
        self.SetTitle(_("Videomass: FFmpeg file formats"))
        self.SetMinSize((500, 400))
        # dmx.SetMinSize((500, 400))
        dmx.InsertColumn(0, _('format'), width=150)
        dmx.InsertColumn(1, _('description'), width=450)
        # dmx.SetBackgroundColour(wx.Colour(217, 255, 255))
        # mx.SetMinSize((500, 400))
        mx.InsertColumn(0, _('format'), width=150)
        mx.InsertColumn(1, _('description'), width=450)
        # mx.SetBackgroundColour(wx.Colour(217, 255, 255))
        # dmx_mx.SetMinSize((500, 400))
        dmx_mx.InsertColumn(0, _('format'), width=150)
        dmx_mx.InsertColumn(1, _('description'), width=450)
        # dmx_mx.SetBackgroundColour(wx.Colour(217, 255, 255))

        if OS == 'Darwin':
            dmx.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
            mx.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
            dmx_mx.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
        else:
            dmx.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            mx.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            dmx_mx.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))

        # delete previous append:
        dmx.DeleteAllItems()
        mx.DeleteAllItems()
        dmx_mx.DeleteAllItems()

        # populate dmx listctrl output:
        index = 0
        ds = dict_formats['Demuxing Supported']

        if ds:
            dmx.InsertItem(index, ('----'))
            dmx.SetItemBackgroundColour(index, "CORAL")
            for a in ds:
                s = " ".join(a.split()).split(None, 1)
                if len(s) == 1:
                    key, value = s[0], ''
                else:
                    key, value = s[0], s[1]
                index += 1
                dmx.InsertItem(index, key)
                dmx.SetItem(index, 1, value)

        # populate mx listctrl output:
        index = 0
        ms = dict_formats['Muxing Supported']

        if ms:
            mx.InsertItem(index, ('----'))
            mx.SetItemBackgroundColour(index, "CORAL")
            for a in ms:
                s = " ".join(a.split()).split(None, 1)
                if len(s) == 1:
                    key, value = s[0], ''
                else:
                    key, value = s[0], s[1]
                index += 1
                mx.InsertItem(index, key)
                mx.SetItem(index, 1, value)

        # populate dmx_mx listctrl output:
        index = 0
        mds = dict_formats["Mux/Demux Supported"]

        if mds:
            dmx_mx.InsertItem(index, ('----'))
            dmx_mx.SetItemBackgroundColour(index, "CORAL")
            for a in mds:
                s = " ".join(a.split()).split(None, 1)
                if len(s) == 1:
                    key, value = s[0], ''
                else:
                    key, value = s[0], s[1]
                index += 1
                dmx_mx.InsertItem(index, key)
                dmx_mx.SetItem(index, 1, value)

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)  # controlla la chiusura (x)
        # self.Bind(wx.EVT_BUTTON, self.on_help, button_help)

    # ----------------------Event handler (callback)----------------------#

    def on_close(self, event):
        self.Destroy()
