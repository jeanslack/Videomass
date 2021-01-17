# -*- coding: UTF-8 -*-
# Name: set_timestamp.py
# Porpose: set viewing attribute timestamp for FFplay
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Gen.01.2020 *PEP8 compatible*
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


class Set_Timestamp(wx.Dialog):
    """
    Customize drawtext filter to display current play time
    (timestamp) during playback with FFplay.

    """
    # get videomass wx.App attribute
    get = wx.GetApp()
    OS = get.OS  # ID of the operative system:

    def __init__(self, parent, tscurrent):
        """
        Attributes defined here

            self.fontsize:
                The font size to be used for drawing text.
            self.box:
                Used to draw a box around text using the background color.
                The value must be either 1 (enable) or 0 (disable).
            boxcolor:
                The color to be used for drawing box around text.
            fontcolor:
                The color to be used for drawing fonts.
            shadowcolor:
                The color to be used for drawing a shadow behind the drawn
                text.

        For all details:  https://ffmpeg.org/ffmpeg-filters.html#drawtext

        For the syntax of the colors, check the
        https://ffmpeg.org/ffmpeg-utils.html#color-syntax

        """
        items = tscurrent.split(':')
        for i in items:
            if 'fontsize=' in i:
                self.fontsize = i.split('=')[1]
            if 'box=' in i:
                self.boxenabled = i.split('=')[1]
            if 'fontcolor=' in i:
                self.fontcolor = i.split('=')[1]
            if 'boxcolor' in i:
                self.boxcolor = i.split('=')[1]
            if 'shadowcolor' in i:
                self.shadowcolor = i.split('=')[1]

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)

        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sbox = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, ("")),
                                 wx.VERTICAL)
        sizer_base.Add(sbox, 1, wx.ALL | wx.EXPAND, 5)
        grid1 = wx.FlexGridSizer(cols=3, vgap=0, hgap=0)
        sbox.Add(grid1, 0, wx.ALL | wx.CENTER, 10)
        stfont = wx.StaticText(self, label=_('Timestamp Size'))
        grid1.Add(stfont, 0, wx.ALL |
                  wx.ALIGN_CENTER_VERTICAL |
                  wx.ALIGN_CENTER_HORIZONTAL,
                  5)

        size = ['16', '20', '28', '32', '40', '48', '56', '64']
        self.cmbx_fontsize = wx.ComboBox(self, wx.ID_ANY,
                                         choices=size,
                                         size=(90, -1),
                                         style=wx.CB_DROPDOWN |
                                         wx.CB_READONLY
                                         )
        fsize = self.cmbx_fontsize.FindString(self.fontsize,
                                              caseSensitive=False)
        self.cmbx_fontsize.SetSelection(fsize)
        grid1.Add(self.cmbx_fontsize, 0, wx.ALL |
                  wx.ALIGN_CENTER_VERTICAL |
                  wx.ALIGN_CENTER_HORIZONTAL,
                  5)
        self.check_enablebox = wx.CheckBox(self, wx.ID_ANY,
                                           (_("Enable box around text"))
                                           )
        grid1.Add(self.check_enablebox, 0, wx.ALL |
                  wx.ALIGN_CENTER_VERTICAL |
                  wx.ALIGN_CENTER_HORIZONTAL,
                  5)
        grid2 = wx.FlexGridSizer(cols=3, vgap=0, hgap=20)
        sbox.Add(grid2, 0, wx.ALL | wx.CENTER, 10)
        colours = [("Azure"),
                   ("DeepPink"),
                   ("ForestGreen"),
                   ("Gold"),
                   ("Orange"),
                   ("Red"),
                   ("Pink"),
                   ("White"),
                   ("Black"),
                   ("Yellow"),
                   ]
        sel = colours.index(self.fontcolor)
        self.rdbx_fontcolor = wx.RadioBox(self, wx.ID_ANY, (_("Font Color")),
                                          choices=colours, majorDimension=0,
                                          style=wx.RA_SPECIFY_ROWS
                                          )
        self.rdbx_fontcolor.SetSelection(sel)
        grid2.Add(self.rdbx_fontcolor, 0, wx.ALL | wx.CENTER, 5)

        sel = colours.index(self.boxcolor)
        self.rdbx_boxcolor = wx.RadioBox(self, wx.ID_ANY, (_("Box Color")),
                                         choices=colours, majorDimension=0,
                                         style=wx.RA_SPECIFY_ROWS
                                         )
        self.rdbx_boxcolor.SetSelection(sel)
        grid2.Add(self.rdbx_boxcolor, 0, wx.ALL | wx.CENTER, 5)

        sel = colours.index(self.shadowcolor)
        self.rdbx_shadowcolor = wx.RadioBox(self, wx.ID_ANY,
                                            (_("Shadow Color")),
                                            choices=colours, majorDimension=0,
                                            style=wx.RA_SPECIFY_ROWS
                                            )
        self.rdbx_shadowcolor.SetSelection(sel)
        grid2.Add(self.rdbx_shadowcolor, 0, wx.ALL | wx.CENTER, 5)
        # confirm buttons:
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        self.btn_ok = wx.Button(self, wx.ID_OK, _("Apply"))
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        gridexit.Add(btn_close, 0, wx.ALL | wx.EXPAND, 5)
        gridexit.Add(self.btn_ok, 0, wx.ALL | wx.EXPAND, 5)
        sizer_base.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)

        # tooltips:
        tip = _('The timestamp size does not auto-adjust to the video size, '
                'you have to set the size here')
        self.cmbx_fontsize.SetToolTip(tip)
        # final settings:
        self.SetTitle(_("Timestamp settings"))
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # ----------------------Binding (EVT)--------------------------#
        self.Bind(wx.EVT_COMBOBOX, self.on_Fontsize, self.cmbx_fontsize)
        self.Bind(wx.EVT_CHECKBOX, self.on_Box, self.check_enablebox)
        self.Bind(wx.EVT_RADIOBOX, self.on_Fontcolor, self.rdbx_fontcolor)
        self.Bind(wx.EVT_RADIOBOX, self.on_Shadowcolor, self.rdbx_shadowcolor)
        self.Bind(wx.EVT_RADIOBOX, self.on_Boxcolor, self.rdbx_boxcolor)

        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)

        if self.boxenabled == '1':
            self.check_enablebox.SetValue(True)
            self.rdbx_boxcolor.Enable()
        else:
            self.check_enablebox.SetValue(False)
            self.rdbx_boxcolor.Disable()

    # ----------------------Event handler (callback)----------------------#

    def on_Fontsize(self, event):
        """
        Get font size str on combobox

        """
        self.fontsize = self.cmbx_fontsize.GetStringSelection()
    # ------------------------------------------------------------------#

    def on_Box(self, event):
        """
        enable or disable box around text
        enable = '1'
        disable = '0'
        """
        if self.check_enablebox.IsChecked():
            self.rdbx_boxcolor.Enable()
            self.boxenabled = '1'
        else:
            self.rdbx_boxcolor.Disable()
            self.boxenabled = '0'
    # ------------------------------------------------------------------#

    def on_Fontcolor(self, event):
        """
        get font color
        """
        self.fontcolor = self.rdbx_fontcolor.GetStringSelection()
    # ------------------------------------------------------------------#

    def on_Boxcolor(self, event):
        """
        Get box color
        """
        self.boxcolor = self.rdbx_boxcolor.GetStringSelection()
    # ------------------------------------------------------------------#

    def on_Shadowcolor(self, event):
        """
        Get shadow color
        """
        self.shadowcolor = self.rdbx_shadowcolor.GetStringSelection()
    # ------------------------------------------------------------------#

    def on_close(self, event):

        event.Skip()
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        if you enable self.Destroy(), it delete from memory all data
        event and no return correctly. It has the right behavior if
        not used here, because it is called in the main frame.

        Event.Skip(), work correctly here. Sometimes needs to disable
        it for needs to maintain the view of the window (for exemple).
        """
        self.GetValue()
        # self.Destroy()
        event.Skip()
    # ------------------------------------------------------------------#

    def GetValue(self):
        """
        This method return values via the interface GetValue()

        """
        ptshms = r"%{pts\:hms}"

        if Set_Timestamp.OS == 'Darwin':
            tsfont = '/Library/Fonts/Arial.ttf'
        elif Set_Timestamp.OS == 'Windows':
            tsfont = 'C:\\Windows\\Fonts\\Arial.ttf'
        else:
            tsfont = 'Arial'

        timestamp = (
            f"drawtext=fontfile={tsfont}:text='{ptshms}':"
            f"fontcolor={self.fontcolor}:shadowcolor={self.shadowcolor}:"
            f"shadowx=1:shadowy=1:fontsize={self.fontsize}:"
            f"box={self.boxenabled}:boxcolor={self.boxcolor}:"
            f"x=(w-tw)/2:y=h-(2*lh)")

        return timestamp
