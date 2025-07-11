# -*- coding: UTF-8 -*-
"""
Name: choose_topic.py
Porpose: shows the topics available in the program
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: July.10.2025
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
import sys
import wx
from videomass.vdms_utils.get_bmpfromsvg import get_bmp
from videomass.vdms_sys.about_app import VERSION


class Choose_Topic(wx.Panel):
    """
    Helps to choose a topic.
    """
    def __init__(self, parent):
        """
        This is a home panel shown when start Videomass to choose the
        appropriate contextual panel.
        """
        get = wx.GetApp()  # get data from bootstrap
        self.appdata = get.appset
        self.icons = parent.icons
        icontheme = self.appdata['icontheme']

        # ----------------------
        self.parent = parent

        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up
            bmpAVconv = get_bmp(self.icons['A/V-Conv'], ((48, 48)))
            bmpPrstmng = get_bmp(self.icons['presets_manager'], ((48, 48)))
            bmpConcat = get_bmp(self.icons['concatenate'], ((48, 48)))
            bmpSlideshow = get_bmp(self.icons['slideshow'], ((48, 48)))
            bmpTopictures = get_bmp(self.icons['videotopictures'], ((48, 48)))
        else:
            bmpAVconv = wx.Bitmap(self.icons['A/V-Conv'], wx.BITMAP_TYPE_ANY)
            bmpPrstmng = wx.Bitmap(self.icons['presets_manager'],
                                   wx.BITMAP_TYPE_ANY)
            bmpConcat = wx.Bitmap(self.icons['concatenate'],
                                  wx.BITMAP_TYPE_ANY)
            bmpSlideshow = wx.Bitmap(self.icons['slideshow'],
                                     wx.BITMAP_TYPE_ANY)
            bmpTopictures = wx.Bitmap(self.icons['videotopictures'],
                                      wx.BITMAP_TYPE_ANY)

        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)

        welcome = wx.StaticText(self, wx.ID_ANY, (_("Welcome to Videomass")),
                                style=wx.ALIGN_CENTER)
        version = wx.StaticText(self, wx.ID_ANY, (_('Version {}'
                                                    ).format(VERSION)))
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(50, 50)
        sizer_base.Add(welcome, 0, wx.EXPAND, 0)
        sizer_base.Add(20, 20)
        sizer_base.Add(version, 0, wx.BOTTOM | wx.ALIGN_CENTER, 0)
        if self.appdata['ostype'] == 'Windows':
            style = wx.BU_LEFT | wx.BORDER_NONE
        else:
            style = wx.BU_LEFT
        presets_mng = wx.Button(self, wx.ID_ANY, _('Presets Manager'),
                                size=(300, -1), style=style)
        presets_mng.SetBitmap(bmpPrstmng, wx.LEFT)
        avconv = wx.Button(self, wx.ID_ANY, _('AV-Conversions'),
                           size=(300, -1), style=style)
        avconv.SetBitmap(bmpAVconv, wx.LEFT)
        conc = wx.Button(self, wx.ID_ANY, _('Concatenate media files'),
                         size=(300, -1), style=style)
        conc.SetBitmap(bmpConcat, wx.LEFT)
        slideshow = wx.Button(self, wx.ID_ANY, _('Still Image Maker'),
                              size=(300, -1), style=style)
        slideshow.SetBitmap(bmpSlideshow, wx.LEFT)
        videotoimages = wx.Button(self, wx.ID_ANY, _('From Movie to Pictures'),
                                  size=(300, -1), style=style)
        videotoimages.SetBitmap(bmpTopictures, wx.LEFT)
        grid_btntop = wx.FlexGridSizer(1, 2, 20, 20)
        grid_btntop.AddMany([(presets_mng, 0, wx.EXPAND, 5),
                             (avconv, 0, wx.EXPAND, 5),
                             ])
        sizer_base.Add(80, 80)
        sizer_base.Add(grid_btntop, 0, wx.ALIGN_CENTER_VERTICAL
                       | wx.ALIGN_CENTER_HORIZONTAL, 5,
                       )

        grid_btncntr = wx.FlexGridSizer(1, 1, 20, 20)
        grid_btncntr.Add(conc, 0, wx.EXPAND, 5)
        sizer_base.Add(20, 20)
        sizer_base.Add(grid_btncntr, 0, wx.ALIGN_CENTER_VERTICAL
                       | wx.ALIGN_CENTER_HORIZONTAL, 5,
                       )
        sizer_base.Add(20, 20)
        grid_btnbot = wx.FlexGridSizer(2, 2, 20, 20)
        grid_btnbot.AddMany([(slideshow, 0, wx.EXPAND, 5),
                             (videotoimages, 0, wx.EXPAND, 5),
                             ])
        sizer_base.Add(grid_btnbot, 0, wx.ALIGN_CENTER_VERTICAL
                       | wx.ALIGN_CENTER_HORIZONTAL, 5,
                       )
        self.SetSizerAndFit(sizer_base)

        # ---------------------- Tooltips
        tip = (_('Create, edit and use quickly your favorite FFmpeg '
                 'presets and profiles with full formats support and '
                 'codecs.'))
        presets_mng.SetToolTip(tip)
        tip = (_('A set of useful tools for audio and video conversions. '
                 'Save your profiles and reuse them with Presets '
                 'Manager.'))
        avconv.SetToolTip(tip)
        tip = (_('Concatenate multiple media files based on import '
                 'order without re-encoding'))
        conc.SetToolTip(tip)
        tip = (_('Create video from a sequence of images, based on import '
                 'order, with the ability to add an audio file.'))
        slideshow.SetToolTip(tip)
        tip = (_('Extract images (frames) from your movies '
                 'in JPG, PNG, BMP, GIF formats.'))
        videotoimages.SetToolTip(tip)

        if self.appdata['ostype'] == 'Darwin':
            welcome.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.BOLD))
            version.SetFont(wx.Font(13, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            welcome.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.NORMAL))
            version.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.LIGHT))

        if self.appdata['IS_DARK_THEME'] is True:
            if icontheme in ('Videomass-Colours',
                             'Videomass-Dark',
                             'Videomass-Light'):
                self.SetBackgroundColour('#232424')  # Dark grey
            elif icontheme in ('Ubuntu-Dark-Aubergine',
                               'Ubuntu-Light-Aubergine'):
                self.SetBackgroundColour('#2C001E')  # Dark Aubergine
            welcome.SetForegroundColour('#E95420')  # Ubuntu orange
            version.SetForegroundColour('#E95420')  # Ubuntu orange
        elif self.appdata['IS_DARK_THEME'] is False:
            if icontheme in ('Videomass-Colours',
                             'Videomass-Dark',
                             'Videomass-Light'):
                self.SetBackgroundColour('#4eada5')  # blue
            elif icontheme in ('Ubuntu-Dark-Aubergine',
                               'Ubuntu-Light-Aubergine'):
                self.SetBackgroundColour('#2C001E')  # Dark Aubergine
                welcome.SetForegroundColour('#E95420')  # Ubuntu orange
                version.SetForegroundColour('#E95420')  # Ubuntu orange

        self.Bind(wx.EVT_BUTTON, self.on_avconversions, avconv)
        self.Bind(wx.EVT_BUTTON, self.on_prst_mng, presets_mng)
        self.Bind(wx.EVT_BUTTON, self.on_concatenate, conc)
        self.Bind(wx.EVT_BUTTON, self.on_slideshow, slideshow)
        self.Bind(wx.EVT_BUTTON, self.on_to_pictures, videotoimages)
    # ------------------------------------------------------------------#

    def on_prst_mng(self, event):
        """
        Open drag N drop interface to switch on Presets Manager panel
        """
        self.parent.topicname = 'Presets Manager'
        self.parent.switch_file_import(self)

    # ------------------------------------------------------------------#

    def on_avconversions(self, event):
        """
        Open drag N drop interface to switch on AVconversions panel
        """
        self.parent.topicname = 'Audio/Video Conversions'
        self.parent.switch_file_import(self)
    # ------------------------------------------------------------------#

    def on_concatenate(self, event):
        """
        Open drag N drop interface to switch on Concatenate panel
        """
        self.parent.topicname = 'Concatenate Demuxer'
        self.parent.switch_file_import(self)
    # ------------------------------------------------------------------#

    def on_slideshow(self, event):
        """
        Open drag N drop interface to switch on Image Sequence to Video panel
        """
        self.parent.topicname = 'Image Sequence to Video'
        self.parent.switch_file_import(self)
    # ------------------------------------------------------------------#

    def on_to_pictures(self, event):
        """
        Open drag N drop interface to switch on Video to Pictures panel
        """
        self.parent.topicname = 'Video to Pictures'
        self.parent.switch_file_import(self)
