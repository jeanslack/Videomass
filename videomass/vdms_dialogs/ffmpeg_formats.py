# -*- coding: UTF-8 -*-
"""
Name: ffmpeg_formats.py
Porpose: Show the available formats on the FFmpeg
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.13.2023
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
from pubsub import pub


class FFmpegFormats(wx.Dialog):
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
        get = wx.GetApp()  # get data from bootstrap
        vidicon = get.iconset['videomass']
        wx.Dialog.__init__(self, None,
                           style=wx.DEFAULT_DIALOG_STYLE
                           | wx.RESIZE_BORDER
                           | wx.DIALOG_NO_PARENT
                           )
        # add panel
        self.panel = wx.Panel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL
                              | wx.BORDER_THEME,
                              )
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(self.panel, wx.ID_ANY)
        sizer_base.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        # ----- nb1
        notebook_pane_1 = wx.Panel(notebook, wx.ID_ANY)
        dmx = wx.ListCtrl(notebook_pane_1,
                          wx.ID_ANY,
                          style=wx.LC_REPORT
                          | wx.SUNKEN_BORDER,
                          )
        sizer_tab1 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab1.Add(dmx, 1, wx.ALL | wx.EXPAND, 5)
        notebook_pane_1.SetSizer(sizer_tab1)
        notebook.AddPage(notebook_pane_1, (_("Demuxing only")))
        # ----- nb2
        notebook_pane_2 = wx.Panel(notebook, wx.ID_ANY)
        mx = wx.ListCtrl(notebook_pane_2,
                         wx.ID_ANY,
                         style=wx.LC_REPORT
                         | wx.SUNKEN_BORDER,
                         )
        sizer_tab2 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab2.Add(mx, 1, wx.ALL | wx.EXPAND, 5)
        notebook_pane_2.SetSizer(sizer_tab2)
        notebook.AddPage(notebook_pane_2, (_("Muxing only")))
        # ----- nb3
        notebook_pane_3 = wx.Panel(notebook, wx.ID_ANY)
        dmx_mx = wx.ListCtrl(notebook_pane_3,
                             wx.ID_ANY,
                             style=wx.LC_REPORT
                             | wx.SUNKEN_BORDER,
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

        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(vidicon, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetTitle(_("FFmpeg file formats"))
        self.SetMinSize((500, 400))
        dmx.SetMinSize((500, 400))
        self.panel.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        # ----------------------Properties----------------------#
        dmx.InsertColumn(0, _('supported formats'), width=180)
        dmx.InsertColumn(1, _('description'), width=450)
        # mx.SetMinSize((500, 400))
        mx.InsertColumn(0, _('supported formats'), width=180)
        mx.InsertColumn(1, _('description'), width=450)
        # dmx_mx.SetMinSize((500, 400))
        dmx_mx.InsertColumn(0, _('supported formats'), width=180)
        dmx_mx.InsertColumn(1, _('description'), width=450)

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
            for a in ds:
                s = " ".join(a.split()).split(None, 1)
                if len(s) == 1:
                    key, value = s[0], ''
                else:
                    key, value = s[0], s[1]
                dmx.InsertItem(index, key)
                dmx.SetItem(index, 1, value)
                index = 0

        # populate mx listctrl output:
        index = 0
        ms = dict_formats['Muxing Supported']
        if ms:
            for a in ms:
                s = " ".join(a.split()).split(None, 1)
                if len(s) == 1:
                    key, value = s[0], ''
                else:
                    key, value = s[0], s[1]
                mx.InsertItem(index, key)
                mx.SetItem(index, 1, value)
                index = 0

        # populate dmx_mx listctrl output:
        index = 0
        mds = dict_formats["Mux/Demux Supported"]
        if mds:
            for a in mds:
                s = " ".join(a.split()).split(None, 1)
                if len(s) == 1:
                    key, value = s[0], ''
                else:
                    key, value = s[0], s[1]
                dmx_mx.InsertItem(index, key)
                dmx_mx.SetItem(index, 1, value)
                index = 0

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)  # controlla la chiusura (x)

    # ----------------------Event handler (callback)----------------------#

    def on_close(self, event):
        """
        Destroy this window
        """
        pub.sendMessage("DESTROY_ORPHANED_WINDOWS", msg='FFmpegFormats')
