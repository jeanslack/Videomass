# -*- coding: UTF-8 -*-

#########################################################
# Name: choose_topic.py
# Porpose: shows the topics available in the program
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: October.25.2019
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
import wx.lib.agw.hyperlink as hpl

# get videomass wx.App attribute
get = wx.GetApp()
OS = get.OS
ydl = get.ydl


class Choose_Topic(wx.Panel):
    """
    Helps to choose the appropriate contextual panel
    """
    def __init__(self, parent, OS, videoconv_icn, youtube_icn, prstmng_icn):
        self.parent = parent
        self.OS = OS

        wx.Panel.__init__(self, parent, -1)

        welcome = wx.StaticText(self, wx.ID_ANY, (_("Welcome to Videomass")))
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(welcome, 0, wx.TOP |
                       wx.ALIGN_CENTER_VERTICAL |
                       wx.ALIGN_CENTER_HORIZONTAL, 15
                       )
        grid_buttons = wx.FlexGridSizer(1, 4, 20, 20)
        grid_base = wx.GridSizer(1, 1, 0, 0)

        video_lab = _('Audio/Video Conversions')
        youtube_lab = _('Download from YouTube')
        prst_mng = _('Presets Manager')

        self.presets_mng = wx.Button(self, wx.ID_ANY, prst_mng, size=(-1, -1))
        self.presets_mng.SetBitmap(wx.Bitmap(prstmng_icn), wx.TOP)
        self.video = wx.Button(self, wx.ID_ANY, video_lab, size=(-1, -1))
        self.video.SetBitmap(wx.Bitmap(videoconv_icn), wx.TOP)
        self.youtube = wx.Button(self, wx.ID_ANY, youtube_lab, size=(-1, -1))
        self.youtube.SetBitmap(wx.Bitmap(youtube_icn), wx.TOP)

        grid_buttons.AddMany([(self.presets_mng, 0, wx.EXPAND, 5),
                              (self.video, 0, wx.EXPAND, 5),
                              (self.youtube, 0, wx.EXPAND, 5),
                              ])
        grid_base.Add(grid_buttons, 0, wx.ALIGN_CENTER_VERTICAL |
                      wx.ALIGN_CENTER_HORIZONTAL, 5
                      )
        sizer_base.Add(grid_base, 1, wx.EXPAND |
                       wx.ALIGN_CENTER_VERTICAL |
                       wx.ALIGN_CENTER_HORIZONTAL, 5
                       )
        sizer_hpl = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(sizer_hpl, 0, wx.ALL |
                       wx.ALIGN_CENTER_VERTICAL |
                       wx.ALIGN_CENTER_HORIZONTAL, 15
                       )
        txt_link = wx.StaticText(self, label=_('Download additional presets '
                                               'or contribute to making new '
                                               'ones '))
        link = hpl.HyperLinkCtrl(self, -1, _("Additional Presets"),
                                 URL="https://github.com/jeanslack/"
                                     "Videomass-presets")
        sizer_hpl.Add(txt_link)
        sizer_hpl.Add(link)
        self.SetSizerAndFit(sizer_base)

        if OS == 'Darwin':
            welcome.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        else:
            welcome.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.Bind(wx.EVT_BUTTON, self.on_Video, self.video)
        self.Bind(wx.EVT_BUTTON, self.on_Prst_mng, self.presets_mng)
        self.Bind(wx.EVT_BUTTON, self.on_YoutubeDL, self.youtube)
    # ------------------------------------------------------------------#

    def on_Video(self, event):
        self.parent.File_import(self, 'Audio/Video Conversions')
    # ------------------------------------------------------------------#

    def on_YoutubeDL(self, event):
        if not ydl[0]:
            wx.MessageBox(_('ERROR: {0}\n\nTo use this feature '
                          'please install youtube-dl.').format(ydl[1]),
                          'Videomass', wx.ICON_ERROR)
            return

        self.parent.Text_import(self, 'Youtube Downloader')
    # ------------------------------------------------------------------#

    def on_Prst_mng(self, event):
        self.parent.File_import(self, 'Presets Manager')
