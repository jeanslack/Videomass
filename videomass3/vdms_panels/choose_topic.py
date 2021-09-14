# -*- coding: UTF-8 -*-
"""
Name: choose_topic.py
Porpose: shows the topics available in the program
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: May.09.2021 *-pycodestyle- compatible*
########################################################

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
import os
import sys
import wx
from videomass3.vdms_utils.get_bmpfromsvg import get_bmp
from videomass3.vdms_io import io_tools
from videomass3.vdms_sys.msg_info import current_release


def ydl_latest():
    """
    check for new releases of youtube-dl from
    """
    url = ("https://api.github.com/repos/ytdl-org/youtube-dl"
           "/releases/latest")
    latest = io_tools.get_github_releases(url, "tag_name")

    if latest[0] in ['request error:', 'response error:']:
        wx.MessageBox("%s %s" % (latest[0], latest[1]),
                      "%s" % latest[0], wx.ICON_ERROR, self)
        return None

    return latest
# -----------------------------------------------------------------#


class Choose_Topic(wx.Panel):
    """
    Helps to choose a topic.
    """
    def __init__(self, parent, OS):
        """
        This is a home panel shown when start Videomass to choose the
        appropriate contextual panel.
        """
        get = wx.GetApp()  # get videomass wx.App attribute
        self.appdata = get.appset
        self.icons = get.iconset
        # ----------------------
        self.parent = parent
        self.oS = OS
        version = current_release()

        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up
            bmpAVconv = get_bmp(self.icons['A/V-Conv'], ((48, 48)))
            bmpPrstmng = get_bmp(self.icons['presets_manager'], ((48, 48)))
            bmpYdl = get_bmp(self.icons['youtube'], ((48, 48)))
            bmpConcat = get_bmp(self.icons['concatenate'], ((48, 48)))
        else:
            bmpAVconv = wx.Bitmap(self.icons['A/V-Conv'], wx.BITMAP_TYPE_ANY)
            bmpPrstmng = wx.Bitmap(self.icons['presets_manager'],
                                   wx.BITMAP_TYPE_ANY)
            bmpYdl = wx.Bitmap(self.icons['youtube'], wx.BITMAP_TYPE_ANY)
            bmpConcat = wx.Bitmap(self.icons['concatenate'],
                                  wx.BITMAP_TYPE_ANY)

        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)

        welcome = wx.StaticText(self, wx.ID_ANY, (_("Welcome to Videomass")))
        version = wx.StaticText(self, wx.ID_ANY, (_('Version {}'
                                                    ).format(version[2])))
        sizer_base = wx.BoxSizer(wx.VERTICAL)

        sizer_base.Add(120, 120)
        sizer_base.Add(welcome, 0, wx.ALIGN_CENTER_VERTICAL |
                       wx.ALIGN_CENTER_HORIZONTAL, 0
                       )
        sizer_base.Add(20, 20)
        sizer_base.Add(version, 0, wx.BOTTOM |
                       wx.ALIGN_CENTER_VERTICAL |
                       wx.ALIGN_CENTER_HORIZONTAL, 0
                       )

        if self.oS == 'Windows':
            style = wx.BU_LEFT | wx.BORDER_NONE
        else:
            style = wx.BU_LEFT

        self.presets_mng = wx.Button(self, wx.ID_ANY, _('Presets Manager'),
                                     size=(300, -1), style=style)
        self.presets_mng.SetBitmap(bmpPrstmng, wx.LEFT)

        self.avconv = wx.Button(self, wx.ID_ANY, _('AV-Conversions'),
                                size=(300, -1), style=style)
        self.avconv.SetBitmap(bmpAVconv, wx.LEFT)

        self.conc = wx.Button(self, wx.ID_ANY, _('Concatenate media files'),
                              size=(300, -1), style=style)
        self.conc.SetBitmap(bmpConcat, wx.LEFT)

        self.youtube = wx.Button(self, wx.ID_ANY, _('YouTube Downloader'),
                                 size=(300, -1), style=style)
        self.youtube.SetBitmap(bmpYdl, wx.LEFT)

        grid_buttons = wx.FlexGridSizer(2, 2, 20, 20)
        grid_buttons.AddMany([(self.presets_mng, 0, wx.EXPAND, 5),
                              (self.avconv, 0, wx.EXPAND, 5),
                              (self.conc, 0, wx.EXPAND, 5),
                              (self.youtube, 0, wx.EXPAND, 5),
                              ])
        sizer_base.Add(80, 80)
        sizer_base.Add(grid_buttons, 1, wx.ALIGN_CENTER_VERTICAL |
                       wx.ALIGN_CENTER_HORIZONTAL, 5
                       )
        self.SetSizerAndFit(sizer_base)

        # ---------------------- Tooltips
        tip = (_('Create, edit and use quickly your favorite FFmpeg '
                 'presets and profiles with full formats support and '
                 'codecs.'))
        self.presets_mng.SetToolTip(tip)
        tip = (_('A set of useful tools for audio and video conversions. '
                 'Save your profiles and reuse them with Presets '
                 'Manager.'))
        self.avconv.SetToolTip(tip)
        tip = (_('Easily download videos and audio in different '
                 'formats and quality from YouTube, Facebook and '
                 'more sites.'))
        self.youtube.SetToolTip(tip)
        tip = (_('Concatenate multiple media files based on import '
                 'order without re-encoding'))
        self.conc.SetToolTip(tip)

        if self.oS == 'Darwin':
            welcome.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            version.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            welcome.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL))
            version.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.LIGHT))

        if hasattr(wx.SystemSettings, 'GetAppearance'):
            appear = wx.SystemSettings.GetAppearance()
            if appear.IsDark():
                self.SetBackgroundColour('#070b0e')  # blue darkness
                welcome.SetForegroundColour('#777072')  # grey
                version.SetForegroundColour('#777072')  # grey
            else:
                self.SetBackgroundColour('#f2efe6')  # light azure
                welcome.SetForegroundColour('#171b12')  # black
                version.SetForegroundColour('#171b12')  # black

        self.Bind(wx.EVT_BUTTON, self.on_Conv, self.avconv)
        self.Bind(wx.EVT_BUTTON, self.on_Prst_mng, self.presets_mng)
        self.Bind(wx.EVT_BUTTON, self.on_Conc, self.conc)
        self.Bind(wx.EVT_BUTTON, self.on_YoutubeDL, self.youtube)
    # ------------------------------------------------------------------#

    def on_Prst_mng(self, event):
        """
        Open drag N drop interface to switch on Presets Manager panel
        """
        self.parent.switch_file_import(self, 'Presets Manager')
    # ------------------------------------------------------------------#

    def on_Conv(self, event):
        """
        Open drag N drop interface to switch on AVconversions panel
        """
        self.parent.switch_file_import(self, 'Audio/Video Conversions')
    # ------------------------------------------------------------------#

    def on_Conc(self, event):
        """
        Open drag N drop interface to switch on Concatenate panel
        """
        self.parent.switch_file_import(self, 'Concatenate Demuxer')
    # ------------------------------------------------------------------#

    def on_YoutubeDL(self, event):
        """
        Check the existence of youtube-dl based on the set attributes
        of the bootstrap, then open the text interface, otherwise it
        requires installation.

        """
        msg_required = (_(
                 'To download videos from YouTube.com and other video sites, '
                 'you need an updated version of youtube-dl.\n\n'
                 '...Do you want to download youtube-dl locally now?'
                 ))

        msg_ready = (_(
                    'Successful! \n\n'
                    'youtube-dl is very often updated, make sure you always '
                    'use the latest version available: menu bar > Tools > '
                    'Update youtube-dl.'
                    ))

        if self.appdata['enable_youtubedl'] == 'disabled':
            wx.MessageBox(_("youtube-dl is disabled. Check your preferences."),
                          "Videomass", wx.ICON_INFORMATION, self)
            return

        elif self.appdata['app'] == 'pyinstaller':
            # elif self.appdata['app'] != 'pyinstaller':  # use for debug
            # EXECYDL: /path/youtube-dl if used else False
            if os.path.isfile(self.appdata['EXECYDL']):
                self.parent.switch_text_import(self, 'Youtube Downloader')
                return
            else:
                if wx.MessageBox(msg_required, _("Please confirm"),
                                 wx.ICON_QUESTION |
                                 wx.YES_NO, self) == wx.NO:
                    return

                latest = ydl_latest()
                if not latest:
                    return
                else:
                    upgrd = io_tools.youtubedl_upgrade(latest[0],
                                                       self.appdata['EXECYDL']
                                                       )
                if upgrd[1]:  # failed
                    wx.MessageBox("%s" % (upgrd[1]),
                                  "Videomass", wx.ICON_ERROR, self)
                    return
                else:
                    wx.MessageBox(msg_ready, "Videomass", wx.ICON_INFORMATION,
                                  self)
                    self.parent.ydlused.Enable(True)
                    self.parent.ydlupdate.Enable(True)
                    return
                return

        else:
            # PYLIBYDL: None if used else 'string error'
            if self.appdata['PYLIBYDL'] is None:
                self.parent.switch_text_import(self, 'Youtube Downloader')
                return
            else:
                if self.appdata['app'] == 'appimage':
                    wx.MessageBox(_("ERROR: {}\n\nyoutube-dl is not embedded "
                                    "in AppImage."
                                    ).format(self.appdata['PYLIBYDL']),
                                  "Videomass", wx.ICON_ERROR, self)
                    return
                else:
                    wx.MessageBox(_("ERROR: {}\n\nyoutube-dl is not "
                                    "installed, use your package manager "
                                    "to install it."
                                    ).format(self.appdata['PYLIBYDL']),
                                  "Videomass", wx.ICON_ERROR, self)
                    return
