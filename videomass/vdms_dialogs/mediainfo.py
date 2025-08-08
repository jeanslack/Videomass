# -*- coding: UTF-8 -*-
"""
Name: mediainfo.py
Porpose: show media streams information through ffprobe data
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: July.17.2023
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


class MediaStreams(wx.Dialog):
    """
    Display streams information using ffprobe json data.
    """

    def __init__(self, data, OS):
        """
        list(data):
            contains ffprobe data from `MainFrame.self.data_files`.
        """
        self.data = data
        get = wx.GetApp()  # get data from bootstrap
        if get.appset['IS_DARK_THEME'] is True:
            self.mark = '#174573'
        elif get.appset['IS_DARK_THEME'] is False:
            self.mark = '#3bbbe6'
        else:
            self.mark = '#808080'
        self.colorscheme = get.appset['colorscheme']
        vidicon = get.iconset['videomass']

        wx.Dialog.__init__(self, None,
                           style=wx.DEFAULT_DIALOG_STYLE
                           | wx.RESIZE_BORDER
                           | wx.DIALOG_NO_PARENT
                           )
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        self.file_select = wx.ListCtrl(self,
                                       wx.ID_ANY,
                                       style=wx.LC_REPORT
                                       | wx.SUNKEN_BORDER
                                       | wx.LC_SINGLE_SEL,
                                       )
        sizerBase.Add(self.file_select, 0, wx.ALL | wx.EXPAND, 5)

        notebook = wx.Notebook(self, wx.ID_ANY)
        grid_notebook = wx.GridSizer(1, 1, 0, 0)
        grid_notebook.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        sizerBase.Add(grid_notebook, 1, wx.EXPAND, 0)
        #  tab format
        nb_panel_1 = wx.Panel(notebook, wx.ID_ANY)
        self.format_ctrl = wx.ListCtrl(nb_panel_1,
                                       wx.ID_ANY,
                                       style=wx.LC_REPORT
                                       | wx.SUNKEN_BORDER
                                       | wx.LC_SINGLE_SEL,
                                       name='format',
                                       )
        sizer_tab1 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab1.Add(self.format_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        nb_panel_1.SetSizer(sizer_tab1)
        notebook.AddPage(nb_panel_1, (_("Format")))
        #  tab video
        nb_panel_2 = wx.Panel(notebook, wx.ID_ANY)

        self.video_ctrl = wx.ListCtrl(nb_panel_2,
                                      wx.ID_ANY,
                                      style=wx.LC_REPORT
                                      | wx.SUNKEN_BORDER
                                      | wx.LC_SINGLE_SEL,
                                      name='video'
                                      )
        sizer_tab2 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab2.Add(self.video_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        nb_panel_2.SetSizer(sizer_tab2)
        notebook.AddPage(nb_panel_2, (_("Video Stream")))
        #  tab audio
        nb_panel_3 = wx.Panel(notebook, wx.ID_ANY)
        self.audio_ctrl = wx.ListCtrl(nb_panel_3,
                                      wx.ID_ANY,
                                      style=wx.LC_REPORT
                                      | wx.SUNKEN_BORDER
                                      | wx.LC_SINGLE_SEL,
                                      name='audio'
                                      )
        sizer_tab3 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab3.Add(self.audio_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        nb_panel_3.SetSizer(sizer_tab3)
        notebook.AddPage(nb_panel_3, (_("Audio Streams")))
        #  tab subtitle
        nb_panel_4 = wx.Panel(notebook, wx.ID_ANY)
        self.subt_ctrl = wx.ListCtrl(nb_panel_4,
                                     wx.ID_ANY,
                                     style=wx.LC_REPORT
                                     | wx.SUNKEN_BORDER
                                     | wx.LC_SINGLE_SEL,
                                     name='subtitle'
                                     )
        sizer_tab4 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab4.Add(self.subt_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        nb_panel_4.SetSizer(sizer_tab4)
        notebook.AddPage(nb_panel_4, (_("Subtitle Streams")))
        # ----- confirm buttons section
        gridbtns = wx.GridSizer(1, 2, 0, 0)
        gridclip = wx.GridSizer(1, 1, 0, 0)
        self.btn_copyclip = wx.Button(self, wx.ID_ANY, _("Copy to clipboard"))
        self.btn_copyclip.Disable()
        gridclip.Add(self.btn_copyclip, 0, wx.ALL, 5)
        gridbtns.Add(gridclip)
        boxaff = wx.BoxSizer(wx.HORIZONTAL)
        btn_close = wx.Button(self, wx.ID_CLOSE, "")
        boxaff.Add(btn_close, 0)
        gridbtns.Add(boxaff, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=5)
        sizerBase.Add(gridbtns, 0, wx.EXPAND)

        # ----------------------Properties----------------------#
        self.file_select.InsertColumn(0, _('FILE SELECTION'), width=600)

        self.format_ctrl.InsertColumn(0, _('Properties'), width=200)
        self.format_ctrl.InsertColumn(1, _('Values'), width=400)

        self.video_ctrl.InsertColumn(0, _('Properties'), width=200)
        self.video_ctrl.InsertColumn(1, _('Values'), width=400)

        self.audio_ctrl.InsertColumn(0, _('Properties'), width=200)
        self.audio_ctrl.InsertColumn(1, _('Values'), width=400)

        self.subt_ctrl.InsertColumn(0, _('Properties'), width=200)
        self.subt_ctrl.InsertColumn(1, _('Values'), width=400)

        # set layout
        self.SetTitle(_('Source Stream Properties'))
        self.SetMinSize((700, 600))
        # self.file_select.SetMinSize((-1, 150))
        self.SetSizer(sizerBase)
        # sizerBase.Fit(self)
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(vidicon, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.Fit()
        self.Layout()
        self.CentreOnScreen()

        flist = [x['format']['filename'] for x in self.data
                 if x['format']['filename']]
        index = 0
        for files in flist:
            self.file_select.InsertItem(index, files)
            index += 1
        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.file_select)

        self.format_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selected)
        self.video_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selected)
        self.audio_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selected)
        self.subt_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selected)

        self.format_ctrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselected)
        self.video_ctrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselected)
        self.audio_ctrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselected)
        self.subt_ctrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselected)

        self.Bind(wx.EVT_BUTTON, self.on_copy_to_clipboard, self.btn_copyclip)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)  # controlla la chiusura (x)

        if data:
            self.file_select.Focus(0)  # make the line the current line
            self.file_select.Select(0, on=1)  # default event selection

        self.typelist = None

    # ----------------------Event handler (callbacks)----------------------#

    def on_deselected(self, event):
        """
        Event on deselecting an item on the list
        """
        self.btn_copyclip.Disable()
        self.typelist = None
    # ----------------------------------------------------------------------

    def on_selected(self, event):
        """
        Event on selecting an item on the list
        """
        if not event.GetText():
            self.typelist = None
            return
        self.typelist = event.GetEventObject().Name
        self.btn_copyclip.Enable()
    # ----------------------------------------------------------------------

    def on_copy_to_clipboard(self, event):
        """
        Click on copy to clipboard button, evaluate which
        checklist you are using, then call the appropriate method.
        """
        if self.typelist == 'format':
            self.on_format()
        elif self.typelist == 'video':
            self.on_video()
        elif self.typelist == 'audio':
            self.on_audio()
        elif self.typelist == 'subtitle':
            self.on_sub()
    # ----------------------------------------------------------------------

    def on_format(self):
        """
        Copy selected item to clipboard
        """
        item = self.format_ctrl.GetFocusedItem()
        if item == -1:
            return
        col0 = self.format_ctrl.GetItemText(item, col=0)
        col1 = self.format_ctrl.GetItemText(item, col=1)
        text = f'{col0}: {col1}'
        if wx.TheClipboard.Open():
            data_object = wx.TextDataObject(text)
            wx.TheClipboard.SetData(data_object)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox(_('Unable to open the clipboard on Format tab'),
                          _('Videomass - Error!'), wx.ICON_ERROR, self)
    # ----------------------------------------------------------------------

    def on_video(self):
        """
        Copy selected item to clipboard
        """
        item = self.video_ctrl.GetFocusedItem()
        if item == -1:
            return
        col0 = self.video_ctrl.GetItemText(item, col=0)
        col1 = self.video_ctrl.GetItemText(item, col=1)
        text = f'{col0}: {col1}'
        if wx.TheClipboard.Open():
            data_object = wx.TextDataObject(text)
            wx.TheClipboard.SetData(data_object)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox(_('Unable to open the clipboard on '
                            'Video Streams tab'),
                          _('Videomass - Error!'), wx.ICON_ERROR, self)
    # ----------------------------------------------------------------------

    def on_audio(self):
        """
        Copy selected item to clipboard
        """
        item = self.audio_ctrl.GetFocusedItem()
        if item == -1:
            return
        col0 = self.audio_ctrl.GetItemText(item, col=0)
        col1 = self.audio_ctrl.GetItemText(item, col=1)
        text = f'{col0}: {col1}'
        if wx.TheClipboard.Open():
            data_object = wx.TextDataObject(text)
            wx.TheClipboard.SetData(data_object)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox(_('Unable to open the clipboard on '
                            'Audio Streams tab'),
                          _('Videomass - Error!'), wx.ICON_ERROR, self)
    # ----------------------------------------------------------------------

    def on_sub(self):
        """
        Copy selected item to clipboard
        """
        item = self.subt_ctrl.GetFocusedItem()
        if item == -1:
            return
        col0 = self.subt_ctrl.GetItemText(item, col=0)
        col1 = self.subt_ctrl.GetItemText(item, col=1)
        text = f'{col0}: {col1}'
        if wx.TheClipboard.Open():
            data_object = wx.TextDataObject(text)
            wx.TheClipboard.SetData(data_object)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox(_('Unable to open the clipboard on '
                            'Subtitle Streams tab'),
                          _('Videomass - Error!'), wx.ICON_ERROR, self)
    # ----------------------------------------------------------------------

    def on_select(self, event):
        """
        Update and populate all listctrls during items selection
        on self.file_select list control
        """
        # delete previous append:
        self.format_ctrl.DeleteAllItems()
        self.video_ctrl.DeleteAllItems()
        self.audio_ctrl.DeleteAllItems()
        self.subt_ctrl.DeleteAllItems()

        index = self.file_select.GetFocusedItem()
        item = self.file_select.GetItemText(index)

        index = 0

        for x in self.data:
            if x.get('format').get('filename') == item:
                select = self.data[self.data.index(x)]
                for k, v in x.get('format').items():
                    self.format_ctrl.InsertItem(index, str(k))
                    self.format_ctrl.SetItem(index, 1, str(v))
                    index += 1

        if select.get('streams'):
            index = 0
            for t in select.get('streams'):
                if t.get('codec_type') == 'video':
                    for k, v in t.items():
                        self.video_ctrl.InsertItem(index, str(k))
                        self.video_ctrl.SetItem(index, 1, str(v))
                        if k == 'index':
                            self.video_ctrl.SetItemBackgroundColour(index,
                                                                    self.mark)
                        index += 1
            index = 0
            for t in select.get('streams'):
                if t.get('codec_type') == 'audio':
                    for k, v in t.items():
                        self.audio_ctrl.InsertItem(index, str(k))
                        self.audio_ctrl.SetItem(index, 1, str(v))
                        if k == 'index':
                            self.audio_ctrl.SetItemBackgroundColour(index,
                                                                    self.mark)
                        index += 1
            index = 0
            for t in select.get('streams'):
                if t.get('codec_type') == 'subtitle':
                    for k, v in t.items():
                        self.subt_ctrl.InsertItem(index, str(k))
                        self.subt_ctrl.SetItem(index, 1, str(v))
                        if k == 'index':
                            self.subt_ctrl.SetItemBackgroundColour(index,
                                                                   self.mark)
                        index += 1

        self.btn_copyclip.Disable()
        self.typelist = None
    # ----------------------------------------------------------------------

    def on_close(self, event):
        """
        Destroy this dialog
        """
        pub.sendMessage("DESTROY_ORPHANED_WINDOWS", msg='MediaStreams')
