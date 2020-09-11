# -*- coding: UTF-8 -*-
# Name: mediainfo.py
# Porpose: show media streams information through ffprobe
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
import os
import webbrowser


class Mediainfo(wx.MiniFrame):
    """
    Display streams information from ffprobe json data.
    """
    def __init__(self, data, OS):
        """
        NOTE constructor: with 'None' not depend from videomass.
        With 'parent, -1' if close videomass also close mediainfo window
        """
        self.data = data

        wx.MiniFrame.__init__(self, None, style=wx.RESIZE_BORDER | wx.CAPTION |
                              wx.CLOSE_BOX | wx.SYSTEM_MENU
                              )
        '''constructor'''

        # add panel
        self.panel = wx.Panel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        # Add widget controls
        self.file_select = wx.ListCtrl(self.panel,
                                       wx.ID_ANY,
                                       style=wx.LC_REPORT |
                                       wx.SUNKEN_BORDER |
                                       wx.LC_SINGLE_SEL
                                       )
        notebook = wx.Notebook(self.panel, wx.ID_ANY)
        nb_panel_1 = wx.Panel(notebook, wx.ID_ANY)
        self.format_ctrl = wx.ListCtrl(nb_panel_1,
                                       wx.ID_ANY,
                                       style=wx.LC_REPORT |
                                       wx.SUNKEN_BORDER
                                       )
        nb_panel_2 = wx.Panel(notebook, wx.ID_ANY)

        self.video_ctrl = wx.ListCtrl(nb_panel_2,
                                      wx.ID_ANY,
                                      style=wx.LC_REPORT |
                                      wx.SUNKEN_BORDER
                                      )
        nb_panel_3 = wx.Panel(notebook, wx.ID_ANY)
        self.audio_ctrl = wx.ListCtrl(nb_panel_3,
                                      wx.ID_ANY,
                                      style=wx.LC_REPORT |
                                      wx.SUNKEN_BORDER
                                      )
        nb_panel_4 = wx.Panel(notebook, wx.ID_ANY)

        self.subtitle_ctrl = wx.ListCtrl(nb_panel_4,
                                         wx.ID_ANY,
                                         style=wx.LC_REPORT |
                                         wx.SUNKEN_BORDER
                                         )
        button_close = wx.Button(self.panel, wx.ID_CLOSE, "")

        # ----------------------Properties----------------------#
        self.SetTitle(_('Videomass - FFprobe streams analyzer'))
        self.SetMinSize((640, 400))
        self.file_select.SetMinSize((640, 200))
        self.file_select.InsertColumn(0, _('FILE SELECTION'), width=500)
        # file_select.InsertColumn(1, _('Parameters'), width=450)

        self.format_ctrl.SetMinSize((640, 300))
        # self.format_ctrl.SetBackgroundColour(wx.Colour(217, 255, 255))
        self.format_ctrl.InsertColumn(0, _('References'), width=200)
        self.format_ctrl.InsertColumn(1, _('Parameters'), width=450)
        # self.video_ctrl.SetBackgroundColour(wx.Colour(217, 255, 255))
        self.video_ctrl.InsertColumn(0, _('References'), width=200)
        self.video_ctrl.InsertColumn(1, _('Parameters'), width=450)
        # self.format_ctrl.SetBackgroundColour(wx.Colour(217, 255, 255))
        self.audio_ctrl.InsertColumn(0, _('References'), width=200)
        self.audio_ctrl.InsertColumn(1, _('Parameters'), width=450)
        # self.video_ctrl.SetBackgroundColour(wx.Colour(217, 255, 255))
        self.subtitle_ctrl.InsertColumn(0, _('References'), width=200)
        self.subtitle_ctrl.InsertColumn(1, _('Parameters'), width=450)
        if OS == 'Darwin':
            self.file_select.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL,
                                             wx.NORMAL))
            self.format_ctrl.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL,
                                             wx.NORMAL))
            self.video_ctrl.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL,
                                            wx.NORMAL))
            self.audio_ctrl.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL,
                                            wx.NORMAL))
            self.subtitle_ctrl.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL,
                                               wx.NORMAL))
        else:
            self.file_select.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,
                                             wx.NORMAL))
            self.video_ctrl.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,
                                            wx.NORMAL))
            self.format_ctrl.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,
                                             wx.NORMAL))
            self.audio_ctrl.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,
                                            wx.NORMAL))
            self.subtitle_ctrl.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,
                                               wx.NORMAL))
        # ----------------------Layout--------------------------#
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.file_select, 0, wx.ALL | wx.EXPAND, 5)
        grid_sizer_1 = wx.GridSizer(1, 1, 0, 0)
        grid_buttons = wx.GridSizer(1, 1, 0, 0)

        sizer_tab1 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab1.Add(self.format_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        nb_panel_1.SetSizer(sizer_tab1)

        sizer_tab2 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab2.Add(self.video_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        nb_panel_2.SetSizer(sizer_tab2)

        sizer_tab3 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab3.Add(self.audio_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        nb_panel_3.SetSizer(sizer_tab3)

        sizer_tab4 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab4.Add(self.subtitle_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        nb_panel_4.SetSizer(sizer_tab4)

        notebook.AddPage(nb_panel_1, (_("Data Format")))
        notebook.AddPage(nb_panel_2, (_("Video Stream")))
        notebook.AddPage(nb_panel_3, (_("Audio Streams")))
        notebook.AddPage(nb_panel_4, (_("Subtitle Streams")))
        grid_sizer_1.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        grid_buttons.Add(button_close, 1, wx.ALL, 5)

        sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        sizer_1.Add(grid_buttons, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=0)
        self.panel.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

        flist = [x['format']['filename'] for x in self.data
                 if x['format']['filename']]

        index = 0
        for f in flist:
            self.file_select.InsertItem(index, f)
            index += 1

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.file_select)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_desel, self.file_select)
        self.Bind(wx.EVT_BUTTON, self.on_close, button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)  # controlla la chiusura (x)

        self.file_select.Focus(0)  # make the line the current line
        self.file_select.Select(0, on=1)  # default event selection
    # ----------------------Event handler (callbacks)----------------------#

    def on_desel(self, event):
        """
        """
        pass
    # ------------------------------------------------------------------#

    def on_select(self, event):
        """
        show data during items selection

        """
        # delete previous append:
        self.format_ctrl.DeleteAllItems()
        self.video_ctrl.DeleteAllItems()
        self.audio_ctrl.DeleteAllItems()
        self.subtitle_ctrl.DeleteAllItems()

        index = self.file_select.GetFocusedItem()
        item = self.file_select.GetItemText(index)

        index = 0
        for x in self.data:
            if x.get('format').get('filename') == item:
                select = self.data[self.data.index(x)]
                num_items = self.format_ctrl.GetItemCount()
                self.format_ctrl.InsertItem(num_items, 'DATA FORMAT:')
                self.format_ctrl.SetItemBackgroundColour(index, "ORANGE")
                index += 1
                for k, v in x.get('format').items():
                    self.format_ctrl.InsertItem(index, str(k))
                    self.format_ctrl.SetItem(index, 1, str(v))
                    index += 1

        if select.get('streams'):
            index = 0
            for t in select.get('streams'):
                if t.get('codec_type') == 'video':
                    num_items = self.video_ctrl.GetItemCount()
                    n = 'VIDEO INDEX %d' % t.get('index')
                    self.video_ctrl.InsertItem(num_items, n)
                    self.video_ctrl.SetItemBackgroundColour(index,
                                                            "SLATE BLUE")
                    index += 1
                    for k, v in t.items():
                        self.video_ctrl.InsertItem(index, str(k))
                        self.video_ctrl.SetItem(index, 1, str(v))
                        index += 1
            index = 0
            for t in select.get('streams'):
                if t.get('codec_type') == 'audio':
                    num_items = self.audio_ctrl.GetItemCount()
                    n = 'AUDIO INDEX %d' % t.get('index')
                    self.audio_ctrl.InsertItem(num_items, n)
                    self.audio_ctrl.SetItemBackgroundColour(index, "GREEN")
                    index += 1
                    for k, v in t.items():
                        self.audio_ctrl.InsertItem(index, str(k))
                        self.audio_ctrl.SetItem(index, 1, str(v))
                        index += 1
            index = 0
            for t in select.get('streams'):
                if t.get('codec_type') == 'subtitle':
                    num_items = self.subtitle_ctrl.GetItemCount()
                    n = 'SUBTITLE INDEX %d' % t.get('index')
                    self.subtitle_ctrl.InsertItem(num_items, n)
                    self.subtitle_ctrl.SetItemBackgroundColour(index,
                                                               "GOLDENROD")
                    index += 1
                    for k, v in t.items():
                        self.subtitle_ctrl.InsertItem(index, str(k))
                        self.subtitle_ctrl.SetItem(index, 1, str(v))
                        index += 1
    # ------------------------------------------------------------------#

    def on_close(self, event):
        self.Destroy()
