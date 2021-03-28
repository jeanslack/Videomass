# -*- coding: UTF-8 -*-
# Name: filter_scale.py
# Porpose: Show dialog to get scale data based on FFmpeg syntax
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Mar.04.2021 *PEP8 compatible*
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
import webbrowser
# import wx.lib.masked as masked # not work on macOSX


class Scale(wx.Dialog):
    """
    A dialog tool to get scale, setdar and setsar video filters
    data based on FFmpeg syntax.

    """
    get = wx.GetApp()
    OS = get.OS
    GET_LANG = get.GETlang
    SUPPLANG = get.SUPP_langs

    def __init__(self, parent, scale, dar, sar, v_width, v_height):
        """
        setdar and setsar values only will be returned if `Constrain
        proportions` is not checked. All strings with "0" will disable
        any related filter even in reference to a single value.

        """
        self.width = "0"
        self.height = "0"
        self.darNum = "0"
        self.darDen = "0"
        self.sarNum = "0"
        self.sarDen = "0"

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        """constructor"""
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        # --- Scale section:
        box_scale = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                      _("New size in pixels"))), wx.VERTICAL)
        sizerBase.Add(box_scale, 0, wx.ALL | wx.EXPAND, 5)

        Flex_scale = wx.FlexGridSizer(1, 4, 0, 0)
        box_scale.Add(Flex_scale, 0, wx.ALL | wx.CENTER, 5)
        label_width = wx.StaticText(self, wx.ID_ANY, (_("Width:")))
        Flex_scale.Add(label_width, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_scale_width = wx.SpinCtrl(self, wx.ID_ANY, "0",
                                            min=0, max=9000,
                                            style=wx.TE_PROCESS_ENTER |
                                            wx.SP_ARROW_KEYS
                                            )
        Flex_scale.Add(self.spin_scale_width, 0, wx.ALL |
                       wx.ALIGN_CENTER_VERTICAL, 5
                       )
        label_height = wx.StaticText(self, wx.ID_ANY, (_("Height:")))
        Flex_scale.Add(label_height, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_scale_height = wx.SpinCtrl(self, wx.ID_ANY, "0",
                                             min=0, max=9000,
                                             style=wx.TE_PROCESS_ENTER |
                                             wx.SP_ARROW_KEYS
                                             )
        Flex_scale.Add(self.spin_scale_height, 0, wx.ALL |
                       wx.ALIGN_CENTER_VERTICAL, 5
                       )
        dim = _("Source size: {0} x {1} pixels").format(v_width, v_height)
        label_sdim = wx.StaticText(self, wx.ID_ANY, dim)
        box_scale.Add(label_sdim, 0, wx.BOTTOM | wx.CENTER, 10)
        # --- options
        msg = _(
            'If you want to keep the aspect ratio, select "Constrain '
            'proportions" below and\nspecify only one dimension, either '
            'width or height, and set the other dimension\nto -1 or -2 '
            '(some codecs require -2, so you should do some testing first).')

        label_msg = wx.StaticText(self, wx.ID_ANY, (msg))
        box_scale.Add(label_msg, 0, wx.ALL | wx.CENTER, 10)
        # grid_opt = wx.FlexGridSizer(1, 3, 0, 0)
        # box_scale.Add(grid_opt, 0, wx.ALL, 5)
        lab = _("Constrain proportions (keep aspect ratio)")
        self.ckbx_keep = wx.CheckBox(self, wx.ID_ANY, lab)
        box_scale.Add(self.ckbx_keep, 0, wx.CENTER, 5)
        # grid_opt.Add((30, 0), 0, wx.ALL, 5)
        self.rdb_scale = wx.RadioBox(self, wx.ID_ANY,
                                     (_("Which dimension to adjust?")),
                                     choices=[_("Width"), _("Height")],
                                     majorDimension=1,
                                     style=wx.RA_SPECIFY_ROWS
                                     )
        self.rdb_scale.Disable()
        box_scale.Add(self.rdb_scale, 0, wx.ALL | wx.CENTER, 10)
        # --- setdar section:
        sizerBase.Add((15, 0), 0, wx.ALL, 5)
        box_ar = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                   _("Aspect Ratio"))), wx.VERTICAL)
        sizerBase.Add(box_ar, 1, wx.ALL | wx.EXPAND, 5)
        lab1 = _("Setdar filter (display aspect ratio) example 16/9, 4/3 ")
        self.lab_dar = wx.StaticText(self, wx.ID_ANY, (lab1))
        box_ar.Add(self.lab_dar, 0, wx.ALL | wx.CENTRE, 5)
        Flex_dar = wx.FlexGridSizer(1, 5, 0, 0)
        box_ar.Add(Flex_dar, 0, wx.ALL | wx.CENTRE, 5)
        self.label_num = wx.StaticText(self, wx.ID_ANY, (_("Numerator")))
        Flex_dar.Add(self.label_num, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_setdarNum = wx.SpinCtrl(self, wx.ID_ANY, "0", min=0,
                                          max=99, style=wx.TE_PROCESS_ENTER |
                                          wx.SP_ARROW_KEYS, size=(-1, -1)
                                          )
        Flex_dar.Add(self.spin_setdarNum, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5
                     )
        self.label_sepdar = wx.StaticText(self, wx.ID_ANY, ("/"))
        self.label_sepdar.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL,
                                  wx.BOLD, 0, ""))
        Flex_dar.Add(self.label_sepdar, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_setdarDen = wx.SpinCtrl(self, wx.ID_ANY, "0", min=0,
                                          max=99, style=wx.TE_PROCESS_ENTER |
                                          wx.SP_ARROW_KEYS, size=(-1, -1)
                                          )
        Flex_dar.Add(self.spin_setdarDen, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5
                     )
        self.label_den = wx.StaticText(self, wx.ID_ANY, (_("Denominator")))
        Flex_dar.Add(self.label_den, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        # --- setsar section:
        box_ar.Add((15, 0), 0, wx.ALL, 5)
        lab2 = _("Setsar filter (sample aspect ratio) example 1/1")
        self.lab_sar = wx.StaticText(self, wx.ID_ANY, (lab2))
        box_ar.Add(self.lab_sar, 0, wx.ALL | wx.CENTRE, 5)
        Flex_sar = wx.FlexGridSizer(1, 5, 0, 0)
        box_ar.Add(Flex_sar, 0, wx.ALL | wx.CENTRE, 5)
        self.label_num1 = wx.StaticText(self, wx.ID_ANY, (_("Numerator")))
        Flex_sar.Add(self.label_num1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_setsarNum = wx.SpinCtrl(self, wx.ID_ANY, "0", min=0,
                                          max=99, style=wx.TE_PROCESS_ENTER |
                                          wx.SP_ARROW_KEYS, size=(-1, -1)
                                          )
        Flex_sar.Add(self.spin_setsarNum, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5
                     )
        self.label_sepsar = wx.StaticText(self, wx.ID_ANY, ("/"))
        self.label_sepsar.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL,
                                  wx.BOLD, 0, ""))
        Flex_sar.Add(self.label_sepsar, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_setsarDen = wx.SpinCtrl(self, wx.ID_ANY, "0", min=0,
                                          max=99, style=wx.TE_PROCESS_ENTER |
                                          wx.SP_ARROW_KEYS, size=(-1, -1)
                                          )
        Flex_sar.Add(self.spin_setsarDen, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5
                     )
        self.label_den1 = wx.StaticText(self, wx.ID_ANY, (_("Denominator")))
        Flex_sar.Add(self.label_den1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        # --- confirm buttons section
        gridBtn = wx.GridSizer(1, 2, 0, 0)
        gridhelp = wx.GridSizer(1, 1, 0, 0)
        btn_help = wx.Button(self, wx.ID_HELP, "")
        gridhelp.Add(btn_help, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridBtn.Add(gridhelp)
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        gridexit.Add(btn_close, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.btn_ok = wx.Button(self, wx.ID_OK, _("Apply"))
        gridexit.Add(self.btn_ok, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        btn_reset = wx.Button(self, wx.ID_CLEAR, _("Reset"))  # Reimposta
        gridexit.Add(btn_reset, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridBtn.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)
        sizerBase.Add(gridBtn, 0, wx.EXPAND)
        # final settings:
        self.SetSizer(sizerBase)
        sizerBase.Fit(self)
        self.Layout()

        # Properties
        self.SetTitle(_("Resizing filters"))
        scale_str = (_('Scale filter, set to 0 to disable'))
        self.spin_scale_width.SetToolTip(scale_str)
        self.spin_scale_height.SetToolTip(scale_str)
        setdar_str = (_('Display Aspect Ratio. Set to 0 to disable'))
        self.spin_setdarNum.SetToolTip(setdar_str)
        self.spin_setdarDen.SetToolTip(setdar_str)
        setsar_str = (_('Sample (aka Pixel) Aspect Ratio.\nSet to 0 '
                        'to disable'))
        self.spin_setsarNum.SetToolTip(setsar_str)
        self.spin_setsarDen.SetToolTip(setsar_str)

        if Scale.OS == 'Darwin':
            label_sdim.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            label_msg.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            label_sdim.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            label_msg.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            self.lab_dar.SetLabelMarkup("<b>%s</b>" % lab1)
            self.lab_sar.SetLabelMarkup("<b>%s</b>" % lab2)

        # ----------------------Binding (EVT)--------------------------#
        self.Bind(wx.EVT_CHECKBOX, self.on_Constrain, self.ckbx_keep)
        self.Bind(wx.EVT_RADIOBOX, self.on_Dimension, self.rdb_scale)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        # Set previous changes
        if scale:
            self.width = scale.split(':')[0][8:]
            self.height = scale.split(':')[1][2:]

            if self.width in ('-1', '-2'):
                self.ckbx_keep.SetValue(True)
                self.rdb_scale.Enable(), self.rdb_scale.SetSelection(1)
                self.keep_aspect_ratio_ON(), self.on_Dimension(self)
            elif self.height in ('-1', '-2'):
                self.ckbx_keep.SetValue(True)
                self.rdb_scale.Enable(), self.rdb_scale.SetSelection(0)
                self.keep_aspect_ratio_ON(), self.on_Dimension(self)

            self.spin_scale_width.SetValue(self.width)
            self.spin_scale_height.SetValue(self.height)

        if dar:
            self.darNum = dar.split('/')[0][7:]
            self.darDen = dar.split('/')[1]
            self.spin_setdarNum.SetValue(int(self.darNum))
            self.spin_setdarDen.SetValue(int(self.darDen))
        if sar:
            self.sarNum = sar.split('/')[0][7:]
            self.sarDen = sar.split('/')[1]
            self.spin_setsarNum.SetValue(int(self.sarNum))
            self.spin_setsarDen.SetValue(int(self.sarDen))

    def keep_aspect_ratio_ON(self):
        """
        Reset the setdar and setsar filters and disable them
        """
        self.spin_setdarNum.SetValue(0), self.spin_setdarDen.SetValue(0)
        self.spin_setdarNum.Disable(), self.spin_setdarDen.Disable()
        self.lab_dar.Disable(), self.label_num.Disable()
        self.label_sepdar.Disable(), self.label_den.Disable()
        self.spin_setsarNum.SetValue(0), self.spin_setsarDen.SetValue(0)
        self.spin_setsarNum.Disable(), self.spin_setsarDen.Disable()
        self.lab_sar.Disable(), self.label_num1.Disable()
        self.label_sepsar.Disable(), self.label_den1.Disable()

    def keep_aspect_ratio_OFF(self):
        """
        Re-enable the setdar and setsar filters
        """
        self.spin_setdarNum.Enable(), self.spin_setdarDen.Enable()
        self.lab_dar.Enable(), self.label_num.Enable()
        self.label_sepdar.Enable(), self.label_den.Enable()
        self.spin_setsarNum.Enable(), self.spin_setsarDen.Enable()
        self.lab_sar.Enable(), self.label_num1.Enable()
        self.label_sepsar.Enable(), self.label_den1.Enable()

    # ----------------------Event handler (callback)---------------------#

    def on_Constrain(self, event):
        """
        Evaluate CheckBox status
        """
        if self.ckbx_keep.IsChecked():
            self.keep_aspect_ratio_ON()
            self.rdb_scale.Enable()
        else:
            self.keep_aspect_ratio_OFF()
            self.rdb_scale.Disable()

        self.on_Dimension(self)
    # ------------------------------------------------------------------#

    def on_Dimension(self, event):
        """
        Set the scaling controls according to whether the
        RadioBox is enabled or disabled
        """
        if self.rdb_scale.IsEnabled():
            if self.rdb_scale.GetSelection() == 0:
                self.spin_scale_height.SetMin(-2)
                self.spin_scale_height.SetMax(-1)
                self.spin_scale_width.SetMin(0)
                self.spin_scale_width.SetMax(9000)

            elif self.rdb_scale.GetSelection() == 1:
                self.spin_scale_width.SetMin(-2)
                self.spin_scale_width.SetMax(-1)
                self.spin_scale_height.SetMax(9000)
                self.spin_scale_height.SetMin(0)
        else:
            self.spin_scale_width.SetMin(0)
            self.spin_scale_width.SetMax(9000)
            self.spin_scale_height.SetMin(0)
            self.spin_scale_height.SetMax(9000)
    # ------------------------------------------------------------------#

    def on_help(self, event):
        """
        Open default web browser via Python Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        if Scale.GET_LANG in Scale.SUPPLANG:
            lang = Scale.GET_LANG.split('_')[0]
            page = ('https://jeanslack.github.io/Videomass/Pages/User-guide-'
                    'languages/%s/4-Video_filters_%s.pdf' % (lang, lang))
        else:
            page = ('https://jeanslack.github.io/Videomass/Pages/User-guide-'
                    'languages/en/4-Video_filters_en.pdf')

        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def on_reset(self, event):
        """
        Revert all controls to default
        """
        self.width, self.height = "0", "0"
        self.darNum, self.darDen = "0", "0"
        self.sarNum, self.sarDen = "0", "0"
        self.ckbx_keep.SetValue(False), self.on_Constrain(self)
        self.spin_scale_width.SetValue(0), self.spin_scale_height.SetValue(0)
        self.spin_setdarNum.SetValue(0), self.spin_setdarDen.SetValue(0)
        self.spin_setsarNum.SetValue(0), self.spin_setsarDen.SetValue(0)
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
        diction = {}
        self.width = '%s' % self.spin_scale_width.GetValue()
        self.height = '%s' % self.spin_scale_height.GetValue()
        self.darNum = '%s' % self.spin_setdarNum.GetValue()
        self.darDen = '%s' % self.spin_setdarDen.GetValue()
        self.sarNum = '%s' % self.spin_setsarNum.GetValue()
        self.sarDen = '%s' % self.spin_setsarDen.GetValue()

        if self.width == '0' or self.height == '0':
            size = ''
        else:
            size = 'scale=w=%s:h=%s' % (self.width, self.height)
            diction['scale'] = size

        if self.darNum == '0' or self.darDen == '0':
            setdar = ''
        else:
            setdar = 'setdar=%s/%s' % (self.darNum, self.darDen)
            diction['setdar'] = setdar

        if self.sarNum == '0' or self.sarDen == '0':
            setsar = ''
        else:
            setsar = 'setsar=%s/%s' % (self.sarNum, self.sarDen)
            diction['setsar'] = setsar

        return (diction)
