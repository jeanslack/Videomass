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
from videomass3.vdms_io import IO_tools
from videomass3.vdms_sys.msg_info import current_release
import os


class Choose_Topic(wx.Panel):
    """
    Helps to choose a topic.
    """
    def __init__(self, parent, OS, videoconv_icn, youtube_icn, prstmng_icn):
        """
        This is a home panel shown when start Videomass to choose the
        appropriate contextual panel.
        """
        self.parent = parent
        self.oS = OS
        version = current_release()

        get = wx.GetApp()  # get videomass wx.App attribute
        self.PYLIB_YDL = get.pylibYdl
        self.EXEC_YDL = get.execYdl

        if self.oS == 'Windows':
            MSGWIN = (_('- Requires: Microsoft Visual C++ 2010 '
                        'Redistributable Package (x86)\n\nfor major '
                        'information visit: <http://ytdl-org.github.io'
                        '/youtube-dl/download.html>'))

        if self.oS == 'Darwin':
            MSGWIN = ''

        else:
            MSGWIN = ''
            self.MSG_ERR = _('{}\n\nyoutube-dl: no library or executable '
                             'found .').format(self.PYLIB_YDL)

        self.MSG = (_(
                 'An updated version of youtube-dl is required to download '
                 'videos from YouTube.com and other video sites. Videomass '
                 'can download an updated copy of youtube-dl locally.\n\n'
                 '- Web site: <https://github.com/ytdl-org/youtube-dl/'
                 'releases>\n{}\n\n'
                 '...Do you wish to continue?'
                 )).format(MSGWIN)

        self.MSGREADY = (_(
                      'Successful! \n\n'
                      'Important: youtube-dl is very often updated, be sure '
                      'to always use the latest version available.\nUse the '
                      'dedicated functions on menu bar > Tools > '
                      'youtube-dl.\n\n'
                      'Re-start is required. Do you want to close Videomass '
                      'now?'
                      ))

        PRST_MNG = _('  Presets Manager - Create, edit and use quickly your '
                     'favorite\n  FFmpeg presets and profiles with full '
                     'formats support and codecs. ')

        AV_CONV = _('  A set of useful tools for audio and video conversions.'
                    '\n  Save your profiles and reuse them with Presets '
                    'Manager. ')

        YOUTUBE_DL = _('  Easily download videos and audio in different '
                       'formats\n  and quality from YouTube, Facebook and '
                       'more sites. ')

        wx.Panel.__init__(self, parent, -1,)

        welcome = wx.StaticText(self, wx.ID_ANY, (_("Welcome to Videomass")))
        version = wx.StaticText(self, wx.ID_ANY, (_('Version {}'
                                                    ).format(version[2])))
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_buttons = wx.FlexGridSizer(5, 0, 20, 20)
        grid_base = wx.GridSizer(1, 1, 0, 0)
        if self.oS == 'Windows':
            style = wx.BU_LEFT | wx.BORDER_NONE
        else:
            style = wx.BU_LEFT

        self.presets_mng = wx.Button(self, wx.ID_ANY, PRST_MNG, size=(-1, -1),
                                     style=style
                                     )
        self.presets_mng.SetBitmap(wx.Bitmap(prstmng_icn), wx.LEFT)
        self.avconv = wx.Button(self, wx.ID_ANY, AV_CONV,
                                size=(-1, -1), style=style
                                )
        self.avconv.SetBitmap(wx.Bitmap(videoconv_icn), wx.LEFT)
        self.youtube = wx.Button(self, wx.ID_ANY, YOUTUBE_DL,
                                 size=(-1, -1), style=style
                                 )
        self.youtube.SetBitmap(wx.Bitmap(youtube_icn), wx.LEFT)

        grid_buttons.AddMany([(welcome, 0, wx.ALIGN_CENTER_VERTICAL |
                               wx.ALIGN_CENTER_HORIZONTAL, 0),
                              (version, 0, wx.BOTTOM |
                               wx.ALIGN_CENTER_VERTICAL |
                               wx.ALIGN_CENTER_HORIZONTAL, 20),
                              (self.presets_mng, 0, wx.EXPAND, 5),
                              (self.avconv, 0, wx.EXPAND, 5),
                              (self.youtube, 0, wx.EXPAND, 5),
                              ])
        grid_base.Add(grid_buttons, 0, wx.ALIGN_CENTER_VERTICAL |
                      wx.ALIGN_CENTER_HORIZONTAL, 5
                      )
        sizer_base.Add(grid_base, 1, wx.EXPAND, 5)
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

        if self.oS == 'Darwin':
            welcome.SetFont(wx.Font(13, wx.SWISS, wx.NORMAL, wx.BOLD))
            version.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            welcome.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            version.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.LIGHT))

        self.Bind(wx.EVT_BUTTON, self.on_Video, self.avconv)
        self.Bind(wx.EVT_BUTTON, self.on_Prst_mng, self.presets_mng)
        self.Bind(wx.EVT_BUTTON, self.on_YoutubeDL, self.youtube)
    # ------------------------------------------------------------------#

    def on_Video(self, event):
        self.parent.switch_file_import(self, 'Audio/Video Conversions')
    # ------------------------------------------------------------------#

    def on_YoutubeDL(self, event):
        """
        Check the installation of youtube-dl depending on the OS in use.
        """
        if self.PYLIB_YDL is None:
            self.parent.switch_text_import(self, 'Youtube Downloader')
            return
        elif self.EXEC_YDL:
            if os.path.isfile(self.EXEC_YDL):
                self.parent.switch_text_import(self, 'Youtube Downloader')
                return
            else:
                if wx.MessageBox(self.MSG, _("Videomass confirmation"),
                                 wx.ICON_QUESTION |
                                 wx.YES_NO, self) == wx.NO:
                    return

                latest = self.parent.ydl_latest(self, msgbox=False)
                if latest[1]:
                    return
                else:
                    upgrade = IO_tools.youtubedl_upgrade(latest[0],
                                                         self.EXEC_YDL)
                if upgrade[1]:  # failed
                    wx.MessageBox("%s" % (upgrade[1]),
                                  "Videomass error", wx.ICON_ERROR, self)
                    return
                else:
                    if wx.MessageBox(self.MSGREADY, "Videomass",
                                     wx.ICON_QUESTION |
                                     wx.YES_NO, self) == wx.NO:
                        return
                    self.parent.on_Kill()
                return

        elif self.EXEC_YDL is False:
            wx.MessageBox(self.MSG_ERR, 'Videomass error', wx.ICON_ERROR)
            return
    # ------------------------------------------------------------------#

    def on_Prst_mng(self, event):
        self.parent.switch_file_import(self, 'Presets Manager')
