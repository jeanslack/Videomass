# -*- coding: UTF-8 -*-
"""
Name: ydl_mediainfo.py
Porpose: show media streams information through youtube-dl.extract_info
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.25.2021
Code checker:
    - flake8: --ignore F821, W504, F401
    - pylint: --ignore E0602, E1101, C0415, E0401, C0103

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


class YdlMediaInfo(wx.Dialog):
    """
    Display streams information from youtube-dl data.

    """
    def __init__(self, data, opsys):
        """
        NOTE constructor:: with 'None' not depend from videomass.
        With 'parent, -1' if close videomass also close mediainfo window
        """
        self.data = data
        get = wx.GetApp()  # get data from bootstrap
        colorscheme = get.appset['icontheme'][1]
        wx.Dialog.__init__(self, None,
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
                           )
        # Add widget controls
        self.url_select = wx.ListCtrl(self,
                                      wx.ID_ANY,
                                      style=wx.LC_REPORT |
                                      wx.SUNKEN_BORDER |
                                      wx.LC_SINGLE_SEL
                                      )
        self.textctrl = wx.TextCtrl(self,
                                    wx.ID_ANY, "",
                                    style=wx.TE_MULTILINE |
                                    wx.TE_READONLY |
                                    wx.TE_RICH2
                                    )
        self.textctrl.SetBackgroundColour(colorscheme['BACKGRD'])
        self.textctrl.SetDefaultStyle(wx.TextAttr(colorscheme['TXT3']))
        button_close = wx.Button(self, wx.ID_CLOSE, "")

        # ----------------------Properties----------------------#
        self.SetTitle(_('Statistics viewer'))
        self.SetMinSize((640, 400))
        self.url_select.SetMinSize((640, 200))
        self.url_select.InsertColumn(0, _('TITLE SELECTION'), width=250)
        self.url_select.InsertColumn(1, _('URL'), width=500)
        self.textctrl.SetMinSize((640, 300))

        if opsys == 'Darwin':
            self.url_select.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL,
                                            wx.NORMAL))
            self.textctrl.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL,
                                          wx.BOLD))
        else:
            self.url_select.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,
                                            wx.NORMAL))
            self.textctrl.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,
                                          wx.NORMAL))
        # ----------------------Layout--------------------------#
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.url_select, 0, wx.ALL | wx.EXPAND, 5)
        grid_sizer_1 = wx.GridSizer(1, 1, 0, 0)
        sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)

        grid_sizer_1.Add(self.textctrl, 0, wx.ALL | wx.EXPAND, 5)
        grid_buttons = wx.GridSizer(1, 1, 0, 0)
        grid_buttons.Add(button_close, 1, wx.ALL, 5)
        sizer_1.Add(grid_buttons, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

        index = 0
        for url in self.data:
            self.url_select.InsertItem(index, str(url['title']))
            self.url_select.SetItem(index, 1, url['url'])
            index += 1

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.url_select)
        self.Bind(wx.EVT_BUTTON, self.on_close, button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.url_select.Focus(0)  # make first line the current line selected
        self.url_select.Select(0, on=1)  # default event selection

    # ----------------------Event handler (callback)----------------------#

    def on_select(self, event):
        """
        show data during items selection

        """
        self.textctrl.Clear()  # delete previous append:

        index = self.url_select.GetFocusedItem()
        item = self.url_select.GetItemText(index)
        text = ('An error has occurred.\n'
                'Unable to parse data from provided URL.')

        for info in self.data:
            if info['title'] == item:
                text = (f"Categories:      {info.get('categories', 'N/A')}\n"
                        f"License:         {info.get('license', 'N/A')}\n"
                        f"Upload Date:     {info.get('upload_date', 'N/A')}\n"
                        f"Uploader:        {info.get('uploader', 'N/A')}\n"
                        f"View Count:      {info.get('view', 'N/A')}\n"
                        f"Like Count:      {info.get('like', 'N/A')}\n"
                        f"Dislike Count:   {info.get('dislike', 'N/A')}\n"
                        f"Average Rating:  {info.get('avr_rat', 'N/A')}\n"
                        f"ID:              {info.get('id', 'N/A')}\n"
                        f"Duration:        {info.get('duration', 'N/A')}\n"
                        f"Description:     {info.get('description', 'N/A')}\n"
                        )
        self.textctrl.AppendText(text)
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        Destroy mini frame
        """
        self.Destroy()
