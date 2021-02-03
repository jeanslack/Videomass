# -*- coding: UTF-8 -*-
# Name: mediainfo.py
# Porpose: show media streams information through ffprobe
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Feb.03.2021 *PEP8 compatible*
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
    get = wx.GetApp()  # get data from bootstrap

    if get.THEME in ('Breeze-Blues', 'Videomass-Colours'):
        BACKGROUND = '#11303eff'
        FOREGROUND = '#959595'

    elif get.THEME in ('Breeze-Blues', 'Breeze-Dark', 'Videomass-Dark'):
        BACKGROUND = '#1c2027ff'
        FOREGROUND = '#87ceebff'

    else:
        BACKGROUND = '#e6e6faff'
        FOREGROUND = '#191970ff'

    def __init__(self, data, OS):
        """
        self.data: list object containing ffprobe data. See FFprobe
        class on vdms_threads/ffprobe_parser.py and probeInfo on
        vdms_io/IO_tools.py
        """
        self.data = data
        msg = _('Display of selected items in text format')
        msg1 = _('Select items to view them in text format')

        wx.MiniFrame.__init__(self, None, style=wx.CAPTION | wx.CLOSE_BOX |
                              wx.RESIZE_BORDER | wx.SYSTEM_MENU
                              )
        '''NOTE constructor: with 'None' not depend from videomass.
        With 'parent, -1' if close videomass also close mediainfo window'''

        # add panel
        self.panel = wx.Panel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL |
                              wx.BORDER_THEME)
        self.sizerBase = wx.BoxSizer(wx.VERTICAL)
        self.file_select = wx.ListCtrl(self.panel,
                                       wx.ID_ANY,
                                       style=wx.LC_REPORT |
                                       wx.SUNKEN_BORDER |
                                       wx.LC_SINGLE_SEL
                                       )
        self.sizerBase.Add(self.file_select, 0, wx.ALL | wx.EXPAND, 5)

        notebook = wx.Notebook(self.panel, wx.ID_ANY)
        grid_notebook = wx.GridSizer(1, 1, 0, 0)
        grid_notebook.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        self.sizerBase.Add(grid_notebook, 1, wx.EXPAND, 0)
        #  tab format
        nb_panel_1 = wx.Panel(notebook, wx.ID_ANY)
        self.format_ctrl = wx.ListCtrl(nb_panel_1,
                                       wx.ID_ANY,
                                       style=wx.LC_REPORT |
                                       wx.SUNKEN_BORDER |
                                       wx.LC_SINGLE_SEL
                                       )
        self.format_stxt = wx.StaticText(nb_panel_1, wx.ID_ANY, msg)
        self.format_tags = wx.TextCtrl(nb_panel_1,
                                       wx.ID_ANY, "",
                                       style=wx.TE_MULTILINE |
                                       wx.TE_READONLY |
                                       wx.TE_RICH2
                                       )
        sizer_tab1 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab1.Add(self.format_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        sizer_tab1.Add(self.format_stxt, 0, wx.ALL, 5)
        sizer_tab1.Add(self.format_tags, 0, wx.ALL | wx.EXPAND, 5)
        nb_panel_1.SetSizer(sizer_tab1)
        notebook.AddPage(nb_panel_1, (_("Data Format")))
        #  tab video
        nb_panel_2 = wx.Panel(notebook, wx.ID_ANY)

        self.video_ctrl = wx.ListCtrl(nb_panel_2,
                                      wx.ID_ANY,
                                      style=wx.LC_REPORT |
                                      wx.SUNKEN_BORDER |
                                      wx.LC_SINGLE_SEL
                                      )
        self.video_stxt = wx.StaticText(nb_panel_2, wx.ID_ANY, msg)
        self.video_tags = wx.TextCtrl(nb_panel_2,
                                      wx.ID_ANY, "",
                                      style=wx.TE_MULTILINE |
                                      wx.TE_READONLY |
                                      wx.TE_RICH2
                                      )
        sizer_tab2 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab2.Add(self.video_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        sizer_tab2.Add(self.video_stxt, 0, wx.ALL, 5)
        sizer_tab2.Add(self.video_tags, 0, wx.ALL | wx.EXPAND, 5)
        nb_panel_2.SetSizer(sizer_tab2)
        notebook.AddPage(nb_panel_2, (_("Video Stream")))
        #  tab audio
        nb_panel_3 = wx.Panel(notebook, wx.ID_ANY)
        self.audio_ctrl = wx.ListCtrl(nb_panel_3,
                                      wx.ID_ANY,
                                      style=wx.LC_REPORT |
                                      wx.SUNKEN_BORDER |
                                      wx.LC_SINGLE_SEL
                                      )
        self.audio_stxt = wx.StaticText(nb_panel_3, wx.ID_ANY, msg)
        self.audio_tags = wx.TextCtrl(nb_panel_3,
                                      wx.ID_ANY, "",
                                      style=wx.TE_MULTILINE |
                                      wx.TE_READONLY |
                                      wx.TE_RICH2
                                      )
        sizer_tab3 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab3.Add(self.audio_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        sizer_tab3.Add(self.audio_stxt, 0, wx.ALL, 5)
        sizer_tab3.Add(self.audio_tags, 0, wx.ALL | wx.EXPAND, 5)
        nb_panel_3.SetSizer(sizer_tab3)
        notebook.AddPage(nb_panel_3, (_("Audio Streams")))
        #  tab subtitle
        nb_panel_4 = wx.Panel(notebook, wx.ID_ANY)
        self.subtitle_ctrl = wx.ListCtrl(nb_panel_4,
                                         wx.ID_ANY,
                                         style=wx.LC_REPORT |
                                         wx.SUNKEN_BORDER |
                                         wx.LC_SINGLE_SEL
                                         )
        self.sub_stxt = wx.StaticText(nb_panel_4, wx.ID_ANY, msg)
        self.sub_tags = wx.TextCtrl(nb_panel_4,
                                    wx.ID_ANY, "",
                                    style=wx.TE_MULTILINE |
                                    wx.TE_READONLY |
                                    wx.TE_RICH2
                                    )
        sizer_tab4 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab4.Add(self.subtitle_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        sizer_tab4.Add(self.sub_stxt, 0, wx.ALL, 5)
        sizer_tab4.Add(self.sub_tags, 0, wx.ALL | wx.EXPAND, 5)
        nb_panel_4.SetSizer(sizer_tab4)
        notebook.AddPage(nb_panel_4, (_("Subtitle Streams")))
        #  bottom
        button_close = wx.Button(self.panel, wx.ID_CLOSE, "")
        self.button_view = wx.ToggleButton(self.panel, wx.ID_ANY,
                                           _("Enable text format"))
        grid_btns = wx.GridSizer(1, 2, 0, 0)
        grid_btns.Add(self.button_view, 0, wx.ALL | wx.EXPAND, 5)
        grid_btns.Add(button_close, 0, wx.ALL | wx.EXPAND, 5)
        self.sizerBase.Add(grid_btns, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=0)

        # ----------------------Properties----------------------#
        self.format_tags.Hide(), self.format_stxt.Hide()
        self.video_tags.Hide(), self.video_stxt.Hide()
        self.audio_tags.Hide(), self.audio_stxt.Hide()
        self.sub_tags.Hide(), self.sub_stxt.Hide()

        self.file_select.InsertColumn(0, _('FILE SELECTION'), width=700)

        self.format_ctrl.InsertColumn(0, _('References'), width=200)
        self.format_ctrl.InsertColumn(1, _('Parameters'), width=500)

        self.video_ctrl.InsertColumn(0, _('References'), width=200)
        self.video_ctrl.InsertColumn(1, _('Parameters'), width=500)

        self.audio_ctrl.InsertColumn(0, _('References'), width=200)
        self.audio_ctrl.InsertColumn(1, _('Parameters'), width=500)

        self.subtitle_ctrl.InsertColumn(0, _('References'), width=200)
        self.subtitle_ctrl.InsertColumn(1, _('Parameters'), width=500)

        self.format_tags.SetBackgroundColour(Mediainfo.BACKGROUND)
        self.format_tags.SetDefaultStyle(wx.TextAttr(Mediainfo.FOREGROUND))
        self.video_tags.SetBackgroundColour(Mediainfo.BACKGROUND)
        self.video_tags.SetDefaultStyle(wx.TextAttr(Mediainfo.FOREGROUND))
        self.audio_tags.SetBackgroundColour(Mediainfo.BACKGROUND)
        self.audio_tags.SetDefaultStyle(wx.TextAttr(Mediainfo.FOREGROUND))
        self.sub_tags.SetBackgroundColour(Mediainfo.BACKGROUND)
        self.sub_tags.SetDefaultStyle(wx.TextAttr(Mediainfo.FOREGROUND))

        self.format_ctrl.SetToolTip(msg1)
        self.video_ctrl.SetToolTip(msg1)
        self.audio_ctrl.SetToolTip(msg1)
        self.subtitle_ctrl.SetToolTip(msg1)

        # set layout
        self.SetTitle(_('Multimedia streams analyzer'))
        self.SetMinSize((700, 500))
        self.file_select.SetMinSize((-1, 150))
        # self.format_ctrl.SetMinSize((-1, 300))
        # self.format_tags.SetMinSize((-1, 100))

        self.format_tags.SetMinSize((-1, 100))
        self.video_tags.SetMinSize((-1, 100))
        self.audio_tags.SetMinSize((-1, 100))
        self.sub_tags.SetMinSize((-1, 100))

        self.panel.SetSizer(self.sizerBase)
        # self.sizerBase.Fit(self)
        self.Fit()
        self.Layout()
        self.CentreOnScreen()

        flist = [x['format']['filename'] for x in self.data
                 if x['format']['filename']]

        index = 0
        for f in flist:
            self.file_select.InsertItem(index, f)
            index += 1

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.file_select)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_format, self.format_ctrl)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_video, self.video_ctrl)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_audio, self.audio_ctrl)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_sub, self.subtitle_ctrl)

        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.format_deselect,
                  self.format_ctrl)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.video_deselect,
                  self.video_ctrl)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.audio_deselect,
                  self.audio_ctrl)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.sub_deselect,
                  self.subtitle_ctrl)

        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_view, self.button_view)
        self.Bind(wx.EVT_BUTTON, self.on_close, button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)  # controlla la chiusura (x)

        self.file_select.Focus(0)  # make the line the current line
        self.file_select.Select(0, on=1)  # default event selection

    # ----------------------Event handler (callbacks)----------------------#

    def on_view(self, event):
        """
        Show or hide text boxes
        """
        if self.button_view.GetValue():
            self.format_tags.Show(), self.format_stxt.Show()
            self.video_tags.Show(), self.video_stxt.Show()
            self.audio_tags.Show(), self.audio_stxt.Show()
            self.sub_tags.Show(), self.sub_stxt.Show()
        else:
            self.format_tags.Hide(), self.format_stxt.Hide()
            self.video_tags.Hide(), self.video_stxt.Hide()
            self.audio_tags.Hide(), self.audio_stxt.Hide()
            self.sub_tags.Hide(), self.sub_stxt.Hide()

        self.format_tags.SetMinSize((-1, 100))
        self.video_tags.SetMinSize((-1, 100))
        self.audio_tags.SetMinSize((-1, 100))
        self.sub_tags.SetMinSize((-1, 100))
        # self.panel.SetSizer(self.sizerBase)
        self.sizerBase.Fit(self)
        self.Layout()
    # ------------------------------------------------------------------#

    def format_deselect(self, event):
        """
        Delete the text previously added on corresponding text boxes
        """
        self.format_tags.Clear()
    # ------------------------------------------------------------------#

    def video_deselect(self, event):
        """
        Delete the text previously added on corresponding text boxes
        """
        self.video_tags.Clear()
    # ------------------------------------------------------------------#

    def audio_deselect(self, event):
        """
        Delete the text previously added on corresponding text boxes
        """
        self.audio_tags.Clear()
    # ------------------------------------------------------------------#

    def sub_deselect(self, event):
        """
        Delete the text previously added on corresponding text boxes
        """
        self.sub_tags.Clear()
    # ------------------------------------------------------------------#

    def on_format(self, event):
        """
        Shows the data of the selected item in the 'format' text box
        """
        if not self.button_view.GetValue():
            self.button_view.SetValue(True)
            self.on_view(self)
        item = self.format_ctrl.GetFocusedItem()
        col0 = self.format_ctrl.GetItemText(item, col=0)
        col1 = self.format_ctrl.GetItemText(item, col=1)
        self.format_tags.Clear()
        if col0 == 'tags':
            tags = eval(col1)
            for k, v in tags.items():
                self.format_tags.AppendText('%s: %s\n' % (k, v))
        elif col0 == 'disposition':
            dispos = eval(col1)
            for k, v in dispos.items():
                self.format_tags.AppendText('%s: %s\n' % (k, v))

        else:
            self.format_tags.write('%s: %s' % (col0, col1))
    # ------------------------------------------------------------------#

    def on_video(self, event):
        """
        Shows the data of the selected item in the video text box
        """
        if not self.button_view.GetValue():
            self.button_view.SetValue(True)
            self.on_view(self)
        item = self.video_ctrl.GetFocusedItem()
        col0 = self.video_ctrl.GetItemText(item, col=0)
        col1 = self.video_ctrl.GetItemText(item, col=1)
        self.video_tags.Clear()
        if col0 == 'tags':
            tags = eval(col1)
            for k, v in tags.items():
                self.video_tags.AppendText('%s: %s\n' % (k, v))
        elif col0 == 'disposition':
            dispos = eval(col1)
            for k, v in dispos.items():
                self.video_tags.AppendText('%s: %s\n' % (k, v))
        else:
            self.video_tags.AppendText('%s: %s\n' % (col0, col1))
    # ------------------------------------------------------------------#

    def on_audio(self, event):
        """
        Shows the data of the selected item in the audio text box
        """
        if not self.button_view.GetValue():
            self.button_view.SetValue(True)
            self.on_view(self)
        item = self.audio_ctrl.GetFocusedItem()
        col0 = self.audio_ctrl.GetItemText(item, col=0)
        col1 = self.audio_ctrl.GetItemText(item, col=1)
        self.audio_tags.Clear()
        if col0 == 'tags':
            tags = eval(col1)
            for k, v in tags.items():
                self.audio_tags.AppendText('%s: %s\n' % (k, v))
        elif col0 == 'disposition':
            dispos = eval(col1)
            for k, v in dispos.items():
                self.audio_tags.AppendText('%s: %s\n' % (k, v))
        else:
            self.audio_tags.AppendText('%s: %s\n' % (col0, col1))
    # ------------------------------------------------------------------#

    def on_sub(self, event):
        """
        Shows the data of the selected item in the subtitle text box

        """
        if not self.button_view.GetValue():
            self.button_view.SetValue(True)
            self.on_view(self)
        item = self.subtitle_ctrl.GetFocusedItem()
        col0 = self.subtitle_ctrl.GetItemText(item, col=0)
        col1 = self.subtitle_ctrl.GetItemText(item, col=1)
        self.sub_tags.Clear()
        if col0 == 'tags':
            tags = eval(col1)
            for k, v in tags.items():
                self.sub_tags.AppendText('%s: %s\n' % (k, v))
        elif col0 == 'disposition':
            dispos = eval(col1)
            for k, v in dispos.items():
                self.sub_tags.AppendText('%s: %s\n' % (k, v))
        else:
            self.sub_tags.AppendText('%s: %s\n' % (col0, col1))
    # ------------------------------------------------------------------#

    def on_select(self, event):
        """
        Update and populate all checklists during items selection
        on self.file_select list control

        """
        # delete previous append:
        self.format_ctrl.DeleteAllItems()
        self.video_ctrl.DeleteAllItems()
        self.audio_ctrl.DeleteAllItems()
        self.subtitle_ctrl.DeleteAllItems()
        self.format_tags.Clear()
        self.video_tags.Clear()
        self.audio_tags.Clear()
        self.sub_tags.Clear()

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
