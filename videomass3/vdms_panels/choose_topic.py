# -*- coding: UTF-8 -*-
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
        self.YOUTUBE_DL = 'youtube-dl.exe' if OS == 'Windows' else 'youtube-dl'
        self.oS = OS
        self.store_ydl_on_cache = True  # show it again the next time
        version = current_release()

        get = wx.GetApp()  # get videomass wx.App attribute
        self.PYLIB_YDL = get.pylibYdl  # None if used else 'string error'
        self.EXEC_YDL = get.execYdl  # /path/youtube-dl if used else False
        self.CACHEDIR = get.CACHEdir

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

    def on_Prst_mng(self, event):
        """
        Open drag N drop interface to switch on Presets Manager panel
        """
        self.parent.switch_file_import(self, 'Presets Manager')
    # ------------------------------------------------------------------#

    def on_Video(self, event):
        """
        Open drag N drop interface to switch on AVconversions panel
        """
        self.parent.switch_file_import(self, 'Audio/Video Conversions')
    # ------------------------------------------------------------------#

    def on_YoutubeDL(self, event):
        """
        Check the existence of youtube-dl based on the set attributes
        of the bootstrap, then open the text interface, otherwise it
        requires installation.

        """
        if self.oS == 'Windows':
            msg_windows = (_(
                        '- Requires: Microsoft Visual C++ 2010 '
                        'Redistributable Package (x86)\n\nfor major '
                        'information visit: <http://ytdl-org.github.io'
                        '/youtube-dl/download.html>'
                        ))

        if self.oS == 'Darwin':
            msg_windows = ''

        else:
            msg_windows = ''
            msg_error = _('{}\n\nyoutube-dl: no library or executable '
                          'found .').format(self.PYLIB_YDL)

        msg_required = (_(
                 'An updated version of youtube-dl is required to download '
                 'videos from YouTube.com and other video sites. Videomass '
                 'can download an updated copy of youtube-dl locally.\n\n'
                 '- Web site: <https://github.com/ytdl-org/youtube-dl/'
                 'releases>\n{}\n\n'
                 '...Do you wish to continue?'
                 )).format(msg_windows)

        msg_ready = (_(
                    'Successful! \n\n'
                    'Important: youtube-dl is very often updated, be sure '
                    'to always use the latest version available. Use the '
                    'dedicated functions on menu bar > Tools > youtube-dl.\n\n'
                    'Re-start is required. Do you want to close Videomass now?'
                    ))

        msg_system_used = (_(
                  'Notice: the youtube-dl executable previously downloaded '
                  'with Videomass is no longer in use, since the one '
                  'installed in the system that has priority is now used.\n\n'
                  'Do you want to remove the one no longer in use?'
                  ))

        if self.PYLIB_YDL is None:
            fydl = os.path.join(self.CACHEDIR, self.YOUTUBE_DL)
            if not self.EXEC_YDL and os.path.isfile(fydl):
                if self.store_ydl_on_cache:
                    dlg = wx.RichMessageDialog(self, msg_system_used,
                                               _("Videomass confirmation"),
                                               wx.ICON_QUESTION |
                                               wx.YES_NO
                                               )
                    dlg.ShowCheckBox(_("Don't show this dialog again"))

                    if dlg.ShowModal() == wx.ID_NO:
                        if dlg.IsCheckBoxChecked():
                            # make sure we won't show it again the next time
                            self.store_ydl_on_cache = False
                    else:
                        os.remove(fydl)
                        if dlg.IsCheckBoxChecked():
                            self.store_ydl_on_cache = False

            self.parent.switch_text_import(self, 'Youtube Downloader')
            return

        elif self.EXEC_YDL:
            if os.path.isfile(self.EXEC_YDL):
                self.parent.switch_text_import(self, 'Youtube Downloader')
                return
            else:
                if wx.MessageBox(msg_required, _("Videomass confirmation"),
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
                    if wx.MessageBox(msg_ready, "Videomass",
                                     wx.ICON_QUESTION |
                                     wx.YES_NO, self) == wx.NO:
                        return
                    self.parent.on_Kill()
                return

        elif self.EXEC_YDL is False:
            wx.MessageBox(msg_error, 'Videomass error', wx.ICON_ERROR)
            return
