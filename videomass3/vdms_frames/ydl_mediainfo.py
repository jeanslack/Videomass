# -*- coding: UTF-8 -*-
# Name: ydl_mediainfo.py
# Porpose: show media streams information through youtube-dl.extract_info
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


class YDL_Mediainfo(wx.MiniFrame):
    """
    Display streams information from youtube-dl data.
    """
    def __init__(self, data, OS):
        """
        NOTE constructor:: with 'None' not depend from videomass.
        With 'parent, -1' if close videomass also close mediainfo window
        """
        self.data = data
        wx.MiniFrame.__init__(self, None, style=wx.CAPTION | wx.CLOSE_BOX |
                              wx.RESIZE_BORDER | wx.SYSTEM_MENU
                              )
        '''constructor'''

        # add panel
        self.panel = wx.Panel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        # Add widget controls
        self.url_select = wx.ListCtrl(self.panel,
                                      wx.ID_ANY,
                                      style=wx.LC_REPORT |
                                      wx.SUNKEN_BORDER
                                      )
        self.textCtrl = wx.TextCtrl(self.panel,
                                    wx.ID_ANY, "",
                                    style=wx.TE_MULTILINE |
                                    wx.TE_DONTWRAP
                                    )
        button_close = wx.Button(self.panel, wx.ID_CLOSE, "")

        # ----------------------Properties----------------------#
        self.SetTitle(_('Videomass - youtube-dl show more'))
        self.SetMinSize((640, 400))
        self.url_select.SetMinSize((640, 200))
        self.url_select.InsertColumn(0, _('TITLE'), width=250)
        self.url_select.InsertColumn(1, _('URL'), width=500)
        self.textCtrl.SetMinSize((640, 300))

        # self.textCtrl.SetDefaultStyle(wx.TextAttr(wx.Colour(30, 62, 164)))
        if OS == 'Darwin':
            self.url_select.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL,
                                            wx.NORMAL))
            self.textCtrl.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL,
                                          wx.BOLD))
        else:
            self.url_select.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,
                                            wx.NORMAL))
            self.textCtrl.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,
                                          wx.BOLD))
        # ----------------------Layout--------------------------#
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.url_select, 0, wx.ALL | wx.EXPAND, 5)
        grid_sizer_1 = wx.GridSizer(1, 1, 0, 0)
        sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)

        grid_sizer_1.Add(self.textCtrl, 0, wx.ALL | wx.EXPAND, 5)
        grid_buttons = wx.GridSizer(1, 1, 0, 0)
        grid_buttons.Add(button_close, 1, wx.ALL, 5)
        sizer_1.Add(grid_buttons, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=0)
        self.panel.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

        index = 0
        for url in self.data:
            self.url_select.InsertItem(index, url['title'])
            self.url_select.SetItem(index, 1, url['url'])
            index += 1

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.url_select)
        self.Bind(wx.EVT_BUTTON, self.on_close, button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    # ----------------------Event handler (callback)----------------------#

    def on_select(self, event):
        """
        show data during items selection

        """
        # delete previous append:
        self.textCtrl.Clear()

        index = self.url_select.GetFocusedItem()
        item = self.url_select.GetItemText(index)

        for info in self.data:
            if info['title'] == item:
                text = ("Categories:      {}\n"
                        "License:         {}\n"
                        "Upload Date:     {}\n"
                        "Uploader:        {}\n"
                        "View Count:      {}\n"
                        "Like Count:      {}\n"
                        "Dislike Count:   {}\n"
                        "Average Rating:  {}\n"
                        "ID:              {}\n"
                        "Duration:        {}\n"
                        "Description:     {}\n".format(info['categories'],
                                                       info['license'],
                                                       info['upload_date'],
                                                       info['uploader'],
                                                       info['view'],
                                                       info['like'],
                                                       info['dislike'],
                                                       info['average_rating'],
                                                       info['id'],
                                                       info['duration'],
                                                       info['description'],
                                                       ))
        self.textCtrl.AppendText(text)
    # ------------------------------------------------------------------#

    def on_close(self, event):
        self.Destroy()
