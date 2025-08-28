# -*- coding: UTF-8 -*-
"""
Name: avconv_cmd_line.py
Porpose: Shows the output raw command lines.
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Aug.13.2025
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
import re
import wx
from videomass.vdms_dialogs.widget_utils import NormalTransientPopup


class Raw_Cmd_Line(wx.Dialog):
    """
    This class represents a modal dialog box
    to display output command lines.
    """
    get = wx.GetApp()
    APPDATA = get.appset
    PASS_1 = _("First pass command")
    PASS_2 = _("Second pass command")
    LGREEN = '#52ee7d'
    BLACK = '#1f1f1f'
    # ------------------------------------------------------------------

    def __init__(self, parent, *args):
        """
        `args` class tuple, contain from 0 to 1 items.
        """
        self.charsize = None
        self.cmd1 = args[0]
        self.cmd2 = args[1] if len(args) > 1 else ''

        wx.Dialog.__init__(self, parent, -1,
                           _("Videomass - RAW Commands"),
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        size_base = wx.BoxSizer(wx.VERTICAL)

        boxshow = wx.BoxSizer(wx.HORIZONTAL)
        size_base.Add(boxshow, 0, wx.ALL, 5)

        btn_readme = wx.Button(self, wx.ID_ANY, _("Read me"), size=(-1, -1))
        btn_readme.SetBackgroundColour(wx.Colour(Raw_Cmd_Line.LGREEN))
        btn_readme.SetForegroundColour(wx.Colour(Raw_Cmd_Line.BLACK))
        boxshow.Add(btn_readme, 0,)

        size_base.Add((0, 15), 0)
        labpass1 = wx.StaticText(self, wx.ID_ANY, Raw_Cmd_Line.PASS_1)
        size_base.Add(labpass1, 0, wx.ALL | wx.EXPAND, 5)
        self.pass_1_cmd = wx.TextCtrl(self, wx.ID_ANY, "",
                                      style=wx.TE_MULTILINE
                                      | wx.TE_READONLY
                                      | wx.TE_RICH2,
                                      )
        size_base.Add(self.pass_1_cmd, 1, wx.ALL | wx.EXPAND, 5)

        size_base.Add((0, 15), 0)
        labpass2 = wx.StaticText(self, wx.ID_ANY, Raw_Cmd_Line.PASS_2)
        size_base.Add(labpass2, 0, wx.ALL | wx.EXPAND, 5)
        self.pass_2_cmd = wx.TextCtrl(self, wx.ID_ANY, "",
                                      style=wx.TE_MULTILINE
                                      | wx.TE_READONLY
                                      | wx.TE_RICH2,
                                      )
        size_base.Add(self.pass_2_cmd, 1, wx.ALL | wx.EXPAND, 5)
        minsize = (800, 550)

        # ----- confirm buttons section
        btn_close = wx.Button(self, wx.ID_CLOSE, "")
        btngrid = wx.FlexGridSizer(1, 1, 0, 0)
        btngrid.Add(btn_close, 0, wx.LEFT, 5)
        size_base.Add(btngrid, flag=wx.ALL
                      | wx.ALIGN_RIGHT
                      | wx.RIGHT, border=5
                      )
        # ------ Set Layout
        self.SetMinSize(minsize)
        self.SetSizer(size_base)
        self.Fit()
        self.Layout()

        # ----------------------Binder (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_readme)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)  # for caption

        self.textstyle()
    # ------------------------------------------------------------------#

    def textstyle(self):
        """
        Populate TextCtrls
        """
        if Raw_Cmd_Line.APPDATA['ostype'] == 'Darwin':
            self.charsize = 12
        else:
            self.charsize = 10

        self.pass_1_cmd.SetFont(wx.Font(self.charsize, wx.FONTFAMILY_TELETYPE,
                                        wx.NORMAL, wx.NORMAL))
        self.pass_2_cmd.SetFont(wx.Font(self.charsize, wx.FONTFAMILY_TELETYPE,
                                        wx.NORMAL, wx.NORMAL))
        backgrnd = '#232424'  # DARK GREY
        foregrnd = '#cfcfc2'  # MATTE WHITE

        self.pass_1_cmd.SetBackgroundColour(backgrnd)
        self.pass_1_cmd.Clear()
        self.pass_1_cmd.SetDefaultStyle(wx.TextAttr(foregrnd))
        self.pass_1_cmd.AppendText(self.cmd1)  # command 1

        self.pass_2_cmd.SetBackgroundColour(backgrnd)
        self.pass_2_cmd.Clear()
        self.pass_2_cmd.SetDefaultStyle(wx.TextAttr(foregrnd))
        self.pass_2_cmd.AppendText(self.cmd2)  # command 2

        self.code_highlight()
    # --------------------------------------------------------------#

    def code_highlight(self):
        """
        event on button help
        """
        bold = wx.Font(self.charsize,
                       wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD)

        colours = {'green': wx.TextAttr('#49eb49', font=bold),
                   'blue': wx.TextAttr('#118db5', font=bold),
                   'azure': wx.TextAttr('#8AB8E6', font=bold),
                   'grey': wx.TextAttr('#7a7c7d', font=bold),
                   'yellow': wx.TextAttr('#fdbc4b', font=bold),
                   'violet': wx.TextAttr('#8e44ad', font=bold),
                   'orange': wx.TextAttr('#f67400', font=bold),
                   'red': wx.TextAttr(wx.RED, font=bold),
                   'white': wx.TextAttr(wx.WHITE, font=bold),
                   }
        keyflags = {(' -map', ' -map_chapters ',
                     ' -map_metadata ', ' verbose '): colours['azure'],
                    (' -c:v', ' -c:a', ' -c:s', ' -an', ' -vn',
                     ' -sn', ' -dn'): colours['orange'],
                    (' -i ',): colours['white'],
                    (' -filter:v', ' -filter:a', ' -vf'):
                        colours['violet'],
                    ('volume=', 'loudnorm=', 'eq=', 'vidstabdetect=',
                     'vidstabtransform=', 'nlmeans=', 'hqdn3d=', 'w3fdif=',
                     'yadif=', 'interlace=', 'transpose=', 'crop=', 'scale=',
                     'setdar=', 'setsar=', 'unsharp=',
                     ' info '): colours['green'],
                    (' -pass ', '.mkv', '.mp4', '.webm', '.avi',
                     '.m4v', '.ogg', '.wav', '.mp3', '.ac3',
                     '.flac', '.m4a', '.aac', '.opus', 'matroska',
                     'null', 'NUL', '-f null', ' warning '): colours['yellow'],
                    (' -aspect', ' -r', ' -movflags',
                     ' debug '): colours['blue'],
                    (' -y ', ' -stats ', ' -hide_banner ',
                     ' -loglevel '): colours['grey'],
                    (r'\<\?\>', ' error '): colours['red'],
                    }
        for key in keyflags:
            for flag in key:
                matches1 = re.finditer(flag, self.cmd1)  # iterator
                matches2 = re.finditer(flag, self.cmd2)  # iterator

                for idx in matches1:
                    self.pass_1_cmd.SetStyle(idx.start(),
                                             idx.end(),
                                             keyflags.get(key))
                for idx in matches2:
                    self.pass_2_cmd.SetStyle(idx.start(),
                                             idx.end(),
                                             keyflags.get(key))

    # ---------------------Callbacks (event handler)--------------------#

    def on_help(self, event):
        """
        event on button help
        """
        msg = (_("The RAW commands reflect the user settings made on\n"
                 "AV-Conversions interface and apply only to the individual\n"
                 "selected file.\n\n"
                 "Please note that using EBU R128 (High-Quality), any <?>\n"
                 "markers highlighted in red should be replaced with the\n"
                 "values given by the output of the first command."))
        win = NormalTransientPopup(self,
                                   wx.SIMPLE_BORDER,
                                   msg,
                                   Raw_Cmd_Line.LGREEN,
                                   Raw_Cmd_Line.BLACK)

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = event.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Popup()
    # --------------------------------------------------------------#

    def on_close(self, event):
        """
        Destroy this dialog
        """
        self.Destroy()
        # event.Skip()
