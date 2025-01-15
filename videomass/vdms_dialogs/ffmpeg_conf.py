# -*- coding: UTF-8 -*-
"""
Name: ffmpeg_conf.py
Porpose: Shows the features of the FFmpeg build configuration
Compatibility: Python3, wxPython4
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.12.2023
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
import os
from shutil import which
import wx
from pubsub import pub


class FFmpegConf(wx.Dialog):
    """
    Shows a graphical representation of the FFmpeg configuration
    sorted by topic

    """
    def __init__(self, out, FFMPEG_LINK, FFPROBE_LINK, FFPLAY_LINK, OS):
        """
        with 'None' not depend from parent:
        wx.Dialog.__init__(self, None, style=wx.DEFAULT_DIALOG_STYLE)

        With parent, -1:
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        if close videomass also close parent window:

        """
        get = wx.GetApp()  # get data from bootstrap
        vidicon = get.iconset['videomass']
        wx.Dialog.__init__(self, None,
                           style=wx.DEFAULT_DIALOG_STYLE
                           | wx.RESIZE_BORDER
                           | wx.DIALOG_NO_PARENT
                           )
        # add panel
        self.panel = wx.Panel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL
                              | wx.BORDER_THEME,
                              )
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(self.panel, wx.ID_ANY)
        sizer_base.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        # -- nb 1
        nb_panel_1 = wx.Panel(notebook, wx.ID_ANY,)
        txtinfo = wx.StaticText(nb_panel_1, wx.ID_ANY,
                                )
        sizer_tab1 = wx.BoxSizer(wx.HORIZONTAL)
        grid_tab1 = wx.FlexGridSizer(1, 1, 10, 10)
        sizer_tab1.Add(grid_tab1, 0, wx.ALL | wx.EXPAND, 5)
        grid_tab1.Add(txtinfo, 0, wx.ALL | wx.EXPAND, 5)
        nb_panel_1.SetSizer(sizer_tab1)
        notebook.AddPage(nb_panel_1, (_("Informations")))
        # -- nb 2
        nb_panel_2 = wx.Panel(notebook, wx.ID_ANY)
        others_opt = wx.ListCtrl(nb_panel_2,
                                 wx.ID_ANY,
                                 style=wx.LC_REPORT
                                 | wx.SUNKEN_BORDER,
                                 )
        sizer_tab2 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab2.Add(others_opt, 1, wx.ALL | wx.EXPAND, 5)
        nb_panel_2.SetSizer(sizer_tab2)
        notebook.AddPage(nb_panel_2, (_("Flags settings")))
        # -- nb 3
        nb_panel_3 = wx.Panel(notebook, wx.ID_ANY)
        enable_opt = wx.ListCtrl(nb_panel_3, wx.ID_ANY,
                                 style=wx.LC_REPORT
                                 | wx.SUNKEN_BORDER,
                                 )
        sizer_tab3 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab3.Add(enable_opt, 1, wx.ALL | wx.EXPAND, 5)
        nb_panel_3.SetSizer(sizer_tab3)
        notebook.AddPage(nb_panel_3, (_("Flags enabled")))
        # -- nb 4
        nb_panel_4 = wx.Panel(notebook, wx.ID_ANY)
        disabled_opt = wx.ListCtrl(nb_panel_4, wx.ID_ANY,
                                   style=wx.LC_REPORT
                                   | wx.SUNKEN_BORDER,
                                   )
        sizer_tab4 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab4.Add(disabled_opt, 1, wx.ALL | wx.EXPAND, 5)
        nb_panel_4.SetSizer(sizer_tab4)
        notebook.AddPage(nb_panel_4, (_("Flags disabled"))
                         )
        # -- btns
        # button_help = wx.Button(self, wx.ID_HELP, "")
        button_close = wx.Button(self.panel, wx.ID_CLOSE, "")

        grid_buttons = wx.FlexGridSizer(1, 1, 0, 0)
        grid_buttons.Add(button_close, 0, wx.ALL, 5)
        sizer_base.Add(grid_buttons, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=0)
        # -- set layout
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(vidicon, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetTitle(_("FFmpeg configuration"))
        self.SetMinSize((700, 500))
        others_opt.SetMinSize((700, 400))
        self.panel.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # ----------------------Properties----------------------#
        others_opt.InsertColumn(0, _('flags'), width=300)
        others_opt.InsertColumn(1, _('options'), width=450)
        # others_opt.SetBackgroundColour(wx.Colour(217, 255, 255))
        enable_opt.SetMinSize((700, 400))
        enable_opt.InsertColumn(0, _('status'), width=300)
        enable_opt.InsertColumn(1, _('options'), width=450)
        # enable_opt.SetBackgroundColour(wx.Colour(217, 255, 255))
        disabled_opt.SetMinSize((700, 400))
        disabled_opt.InsertColumn(0, _('status'), width=300)
        disabled_opt.InsertColumn(1, _('options'), width=450)
        # disabled_opt.SetBackgroundColour(wx.Colour(217, 255, 255))

        if OS == 'Darwin':
            txtinfo.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL))
            others_opt.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
            enable_opt.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
            disabled_opt.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
        else:
            txtinfo.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.NORMAL))
            others_opt.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            enable_opt.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            disabled_opt.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))

        # create lists by out:
        info, others, enable, disable = out
        # ---------
        if OS == 'Windows':
            biname = ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']
        else:
            biname = ['ffmpeg', 'ffprobe', 'ffplay']
        # ---------
        if which(biname[0]):
            ffmpeg = f"FFmpeg:  {FFMPEG_LINK}"
        else:
            if os.path.exists(FFMPEG_LINK):
                ffmpeg = f"FFmpeg:  {FFMPEG_LINK}"

        if which(biname[1]):
            ffprobe = f"FFprobe:  {FFPROBE_LINK}"
        else:
            if os.path.exists(FFPROBE_LINK):
                ffprobe = f"FFprobe:  {FFPROBE_LINK}"
            else:
                ffprobe = _("FFprobe   ...not found !")

        if which(biname[2]):
            ffplay = f"FFplay:  {FFPLAY_LINK}"
        else:
            if os.path.exists(FFPLAY_LINK):
                ffplay = f"FFplay:  {FFPLAY_LINK}"
            else:
                ffplay = _("FFplay   ...not found !")

        # populate txtinfo TextCtrl output:
        txtinfo.SetLabel(f"\n\n\n\n"
                         f"{info[0].strip()}\n\n"
                         f"{info[1].strip()}\n"
                         f"\n\nPath to executables:\n"
                         f"- {ffmpeg}\n"
                         f"- {ffprobe}\n"
                         f"- {ffplay}\n")
        txtinfo.Wrap(600)
        # populate others_opt listctrl output:
        index = 0
        if others:
            n = len(others)
            for a in range(n):
                if '=' in others[a]:
                    oth = others[a].strip().split('=')
                    (key, value) = oth[0], oth[1]
                    # (key, value) = others[a][0].strip().split('=')
                    # num_items = others_opt.GetItemCount()
                    others_opt.InsertItem(index, key)
                    others_opt.SetItem(index, 1, value)
                    index += 1

        # populate enable_opt listctrl output:
        index = 0
        if enable:
            n = len(enable)
            for a in range(n):
                (key, value) = _('Enabled'), enable[a]
                # num_items = enable_opt.GetItemCount()
                enable_opt.InsertItem(index, key)
                enable_opt.SetItem(index, 1, value)
                index += 1

        # populate disabled_opt listctrl output:
        index = 0
        if disable:
            n = len(disable)
            for a in range(n):
                (key, value) = _('Disabled'), disable[a]
                # num_items = disabled_opt.GetItemCount()
                disabled_opt.InsertItem(index, key)
                disabled_opt.SetItem(index, 1, value)
                index += 1

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    # ----------------------Event handler (callback)----------------------#

    def on_close(self, event):
        """
        Destroy this window
        """
        pub.sendMessage("DESTROY_ORPHANED_WINDOWS", msg='FFmpegConf')
