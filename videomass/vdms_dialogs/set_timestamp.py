# -*- coding: UTF-8 -*-

"""
Name: set_timestamp.py
Porpose: timestamp setting on FFplay
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Aug.20.2025
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


class Set_Timestamp(wx.Dialog):
    """
    Customize drawtext filter to display current play time
    (timestamp) during playback with FFplay.
    See ``main_frame.py`` -> ``timestampCustomize`` method for
    how to use this class.
    """

    def __init__(self, parent, tscurrent):
        """
        Attributes defined here

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
        get = wx.GetApp()  # get videomass wx.App attribute
        self.appdata = get.appset

        items = tscurrent.split(':')
        for i in items:
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
        grid1 = wx.FlexGridSizer(cols=2, rows=4, vgap=0, hgap=0)
        sbox.Add(grid1, 0)
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
        stfontcolor = wx.StaticText(self, label=_("Font Color"))
        grid1.Add(stfontcolor, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmbx_fontcolor = wx.ComboBox(self, wx.ID_ANY,
                                          choices=colours,
                                          size=(-1, -1),
                                          style=wx.CB_DROPDOWN
                                          | wx.CB_READONLY,
                                          )
        self.cmbx_fontcolor.SetSelection(colours.index(self.fontcolor))
        grid1.Add(self.cmbx_fontcolor, 0, wx.ALL, 5)
        stshadowcolor = wx.StaticText(self, label=_("Shadow Color"))
        grid1.Add(stshadowcolor, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmbx_shadowcolor = wx.ComboBox(self, wx.ID_ANY,
                                            choices=colours,
                                            size=(-1, -1),
                                            style=wx.CB_DROPDOWN
                                            | wx.CB_READONLY,
                                            )
        self.cmbx_shadowcolor.SetSelection(colours.index(self.shadowcolor))
        grid1.Add(self.cmbx_shadowcolor, 0, wx.ALL, 5)
        self.check_enablebox = wx.CheckBox(self, wx.ID_ANY,
                                           (_("Show text box"))
                                           )
        grid1.Add(self.check_enablebox, 0, wx.ALL, 5)
        grid1.Add((5, 5))
        self.stboxcolor = wx.StaticText(self, label=_("Box Color"))
        grid1.Add(self.stboxcolor, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmbx_boxcolor = wx.ComboBox(self, wx.ID_ANY,
                                         choices=colours,
                                         size=(-1, -1),
                                         style=wx.CB_DROPDOWN
                                         | wx.CB_READONLY,
                                         )
        self.cmbx_boxcolor.SetSelection(colours.index(self.boxcolor))
        grid1.Add(self.cmbx_boxcolor, 0, wx.ALL, 5)
        # confirm buttons:
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        self.btn_ok = wx.Button(self, wx.ID_OK)
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        gridexit.Add(btn_close, 0)
        gridexit.Add(self.btn_ok, 1, wx.LEFT, 5)
        sizer_base.Add(gridexit, 0, wx.ALL | wx.EXPAND, 5)

        # final settings:
        self.SetTitle(_("Timestamp settings"))
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        # ----------------------Binding (EVT)--------------------------#
        self.Bind(wx.EVT_CHECKBOX, self.on_Box, self.check_enablebox)
        self.Bind(wx.EVT_COMBOBOX, self.on_Fontcolor, self.cmbx_fontcolor)
        self.Bind(wx.EVT_COMBOBOX, self.on_Shadowcolor, self.cmbx_shadowcolor)
        self.Bind(wx.EVT_COMBOBOX, self.on_Boxcolor, self.cmbx_boxcolor)

        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)

        if self.boxenabled == '1':
            self.check_enablebox.SetValue(True)
            self.cmbx_boxcolor.Enable()
            self.stboxcolor.Enable()
        else:
            self.check_enablebox.SetValue(False)
            self.cmbx_boxcolor.Disable()
            self.stboxcolor.Disable()

    # ----------------------Event handler (callback)----------------------#

    def on_Box(self, event):
        """
        enable or disable box around text
        enable = '1'
        disable = '0'
        """
        if self.check_enablebox.IsChecked():
            self.cmbx_boxcolor.Enable()
            self.stboxcolor.Enable()
            self.boxenabled = '1'
        else:
            self.cmbx_boxcolor.Disable()
            self.stboxcolor.Disable()
            self.boxenabled = '0'
    # ------------------------------------------------------------------#

    def on_Fontcolor(self, event):
        """
        get font color
        """
        self.fontcolor = self.cmbx_fontcolor.GetStringSelection()
    # ------------------------------------------------------------------#

    def on_Boxcolor(self, event):
        """
        Get box color
        """
        self.boxcolor = self.cmbx_boxcolor.GetStringSelection()
    # ------------------------------------------------------------------#

    def on_Shadowcolor(self, event):
        """
        Get shadow color
        """
        self.shadowcolor = self.cmbx_shadowcolor.GetStringSelection()
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        Close this dialog without saving anything
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Don't use self.Destroy() in this dialog
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def getvalue(self):
        """
        This method return values via a getvalue() interface by
        the caller. See the caller for more infos and usage.
        """
        ptshms = r"%{pts\:hms}"

        if self.appdata['ostype'] == 'Darwin':
            tsfont = '/Library/Fonts/Arial.ttf'
        elif self.appdata['ostype'] == 'Windows':
            tsfont = 'C\\:/Windows/Fonts/Arial.ttf'
        else:
            tsfont = 'Arial'
        fontsize = "fontsize=h/10:x=(w-text_w)/2:y=(h-text_h*2)"  # adaptative

        timestamp = (
            f"drawtext=fontfile='{tsfont}':text='{ptshms}':"
            f"fontcolor={self.fontcolor}:shadowcolor={self.shadowcolor}:"
            f"shadowx=1:shadowy=1:{fontsize}:"
            f"box={self.boxenabled}:boxcolor={self.boxcolor}:"
            f"x=(w-tw)/2:y=h-(2*lh)")

        return timestamp
