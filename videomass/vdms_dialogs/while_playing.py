# -*- coding: UTF-8 -*-
"""
Name: while_playing.py
Porpose: Show box with shortcuts keyboard when playback with FFplay
Compatibility: Python3, wxPython4
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.13.2023
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


class WhilePlaying(wx.Dialog):
    """
    Display a dialog box resizable with shortcuts keyboard
    useful when you use playback function with FFplay

    """
    KEYS = (_("q, ESC\nf\np, SPC\nm\n9, 0\n/, *\na\nv\nt\nc\n"
              "w\ns\n\nleft/right\ndown/up\npage down/page up\n\n"
              "right mouse click\nleft mouse double-click"
              ))
    EXPLAN = (
        "Quiet.\nToggle full screen.\nPause.\nToggle mute.\n"
        "Decrease and increase volume respectively.\n"
        "Decrease and increase volume respectively.\n"
        "Cycle audio channel in the current program (see FFplay docs).\n"
        "Cycle video channel (see FFplay docs).\n"
        "Cycle subtitle channel in the current program (see FFplay docs).\n"
        "Cycle program (see FFplay docs)."
        "\nCycle video filters or show modes (see FFplay docs).\n"
        "Step to the next frame. Pause if the stream is not \n"
        "already paused, step to the next video frame, and pause.\n"
        "Seek backward/forward 10 seconds.\n"
        "Seek backward/forward 1 minute.\n"
        "Seek to the previous/next chapter. Or Seek backward/forward\n"
        "10 minutes if there are no chapters.\n"
        "Seek to percentage in file corresponding to fraction of width.\n"
        "Toggle full screen.")
    # ----------------------------------------------------------------------

    def __init__(self, OS):
        """
        with 'None' not depend from parent:
        wx.Frame.__init__(self, None)

        With parent, -1:
        wx.Frame.__init__(self, parent, -1)
        if close videomass also close parent window
        """
        get = wx.GetApp()  # get data from bootstrap
        colorscheme = get.appset['colorscheme']
        vidicon = get.iconset['videomass']

        wx.Dialog.__init__(self, None,
                           style=wx.DEFAULT_DIALOG_STYLE
                           | wx.DIALOG_NO_PARENT
                           )
        # -------------------- widget --------------------------#
        panel_base = wx.Panel(self, wx.ID_ANY,
                              style=wx.TAB_TRAVERSAL
                              | wx.BORDER_THEME,
                              )
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        # panel_base.SetBackgroundColour(wx.Colour('#008000'))
        # panel_base.SetBackgroundColour(wx.Colour('#101212'))
        panel = wx.Panel(panel_base, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        sizer_base.Add(panel, 0, wx.ALL | wx.EXPAND, 5)

        label1 = wx.StaticText(panel, wx.ID_ANY, WhilePlaying.KEYS)
        label2 = wx.StaticText(panel, wx.ID_ANY, WhilePlaying.EXPLAN)
        button_close = wx.Button(panel_base, wx.ID_CLOSE, "")
        # ----------------------Properties----------------------#
        self.SetTitle(_("Shortcut keys while playing with FFplay"))

        panel.SetBackgroundColour(wx.Colour(colorscheme['BACKGRD']))
        label2.SetForegroundColour(wx.Colour(colorscheme['INFO']))
        label1.SetForegroundColour(wx.Colour(colorscheme['TXT0']))
        # ---------------------- Layout ----------------------#
        gr_s1 = wx.FlexGridSizer(1, 2, 0, 0)
        gr_s1.Add(label1, 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 5)
        gr_s1.Add(label2, 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 5)
        btngrid = wx.FlexGridSizer(1, 1, 0, 0)
        btngrid.Add(button_close, 0, wx.ALL, 0)
        panel.SetSizer(gr_s1)
        sizer_base.Add(btngrid, flag=wx.ALL
                       | wx.ALIGN_RIGHT
                       | wx.RIGHT,
                       border=5,
                       )
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(vidicon, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        panel_base.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # binding
        self.Bind(wx.EVT_BUTTON, self.on_close, button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)  # controlla la chiusura (x)
    # --------------------------------------------------------------#

    def on_close(self, event):
        """
        Destroy this window
        """
        pub.sendMessage("DESTROY_ORPHANED_WINDOWS", msg='WhilePlaying')
