# -*- coding: UTF-8 -*-
"""
FileName: hevc_avc.py
Porpose: Contains h.264/h.265 functionality for A/V Conversions
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.04.2023
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
import wx.lib.scrolledpanel as scrolled


class Hevc_Avc(scrolled.ScrolledPanel):
    """
    This scroll panel implements controls for extra options
    of the `HEVC/AVC` aka h.264/h.265 encoders.
    """
    # presets used by h264 and h265:
    H264_OPT = {("Presets"): ("None", "ultrafast", "superfast",
                              "veryfast", "faster", "fast", "medium",
                              "slow", "slower", "veryslow", "placebo"
                              ),
                ("Profiles"): ("None", "baseline", "main", "high",
                               "high10", "high444"
                               ),
                ("Tunes"): ("None", "film", "animation", "grain",
                            "stillimage", "psnr", "ssim", "fastdecode",
                            "zerolatency"
                            )
                }
    # Used by h265 only
    H265_OPT = {("Presets"): ("None", "ultrafast", "superfast",
                              "veryfast", "faster", "fast", "medium",
                              "slow", "slower", "veryslow", "placebo"
                              ),
                ("Profiles"): ("None", "main", "main10", "mainstillpicture",
                               "msp", "main-intra", "main10-intra",
                               "main444-8", "main444-intra",
                               "main444-stillpicture", "main422-10",
                               "main422-10-intra", "main444-10",
                               "main444-10-intra", "main12", "main12-intra",
                               "main422-12", "main422-12-intra", "main444-12",
                               "main444-12-intra", "main444-16-intra",
                               "main444-16-stillpicture"
                               ),
                ("Tunes"): ("None", "grain", "psnr", "ssim", "fastdecode",
                            "zerolatency"
                            )
                }
    # profile level for profiles x264/x265
    LEVELS = ('None', '1', '2', '2.1', '3', '3.1', '4', '4.1',
              '5', '5.1', '5.2', '6', '6.1', '6.2', '8.5'
              )

    def __init__(self, parent, opt, osplat):
        """
        This is a child of `AV_Conv` class-panel (parent) and the `opt`
        attribute is a dict owned by that class.
        """
        self.parent = parent
        self.opt = opt
        scrolled.ScrolledPanel.__init__(self, parent, -1,
                                        size=(300, 700),
                                        style=wx.TAB_TRAVERSAL
                                        | wx.BORDER_NONE,
                                        name="HEVC scrolledpanel",
                                        )
        sizerbase = wx.BoxSizer(wx.VERTICAL)
        sizerbase.Add((10, 10), 0)
        infomsg = "H.264/H.265"
        self.lbl_info = wx.StaticText(self, wx.ID_ANY, label=infomsg)
        sizerbase.Add(self.lbl_info, 0, wx.ALL | wx.CENTER, 5)
        if osplat == 'Darwin':
            self.lbl_info.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        else:
            self.lbl_info.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerbase.Add((10, 10), 0)
        gridctrl = wx.FlexGridSizer(4, 2, 0, 0)
        sizerbase.Add(gridctrl, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 0)
        txtpresets = wx.StaticText(self, wx.ID_ANY, 'Preset')
        gridctrl.Add(txtpresets, 0, wx.ALL
                     | wx.ALIGN_CENTER_HORIZONTAL
                     | wx.ALIGN_CENTER_VERTICAL, 5,
                     )
        self.cmb_preset = wx.ComboBox(self, wx.ID_ANY,
                                      choices=Hevc_Avc.H264_OPT["Presets"],
                                      size=(170, -1), style=wx.CB_DROPDOWN
                                      | wx.CB_READONLY,
                                      )
        gridctrl.Add(self.cmb_preset, 0, wx.ALL
                     | wx.ALIGN_CENTER_HORIZONTAL
                     | wx.ALIGN_CENTER_VERTICAL, 5,
                     )
        txtprofile = wx.StaticText(self, wx.ID_ANY, 'Profile')
        gridctrl.Add(txtprofile, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_profile = wx.ComboBox(self, wx.ID_ANY,
                                       choices=Hevc_Avc.H264_OPT["Profiles"],
                                       size=(170, -1), style=wx.CB_DROPDOWN
                                       | wx.CB_READONLY,
                                       )
        gridctrl.Add(self.cmb_profile, 0, wx.ALL
                     | wx.ALIGN_CENTER_VERTICAL, 5,
                     )
        txtlevel = wx.StaticText(self, wx.ID_ANY, 'Level')
        gridctrl.Add(txtlevel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_level = wx.ComboBox(self, wx.ID_ANY,
                                     choices=Hevc_Avc.LEVELS, size=(100, -1),
                                     style=wx.CB_DROPDOWN | wx.CB_READONLY
                                     )
        gridctrl.Add(self.cmb_level, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        txttune = wx.StaticText(self, wx.ID_ANY, 'Tune')
        gridctrl.Add(txttune, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_tune = wx.ComboBox(self, wx.ID_ANY,
                                    choices=Hevc_Avc.H264_OPT["Tunes"],
                                    size=(170, -1), style=wx.CB_DROPDOWN
                                    | wx.CB_READONLY,
                                    )
        gridctrl.Add(self.cmb_tune, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        lab_gop = wx.StaticText(self, wx.ID_ANY, ("Group of picture (GOP):"))
        sizerbase.Add(lab_gop, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.spin_gop = wx.SpinCtrl(self, wx.ID_ANY,
                                    "10", min=-1,
                                    max=1000, size=(-1, -1),
                                    style=wx.TE_PROCESS_ENTER,
                                    )
        sizerbase.Add(self.spin_gop, 0, wx.TOP | wx.CENTRE, 5)

        self.SetSizer(sizerbase)  # set panel
        self.SetAutoLayout(1)
        self.SetupScrolling()

        tip = _('Set the encoding preset (default "medium")')
        self.cmb_preset.SetToolTip(tip)
        tip = _('Set profile restrictions')
        self.cmb_profile.SetToolTip(tip)
        tip = _('Specify level for a selected profile')
        self.cmb_level.SetToolTip(tip)
        tip = _('Tune the encoding params')
        self.cmb_tune.SetToolTip(tip)
        tip = (_('Set the group of picture (GOP) size '
                 '(default 12 for H.264, 1 for H.265). '
                 'Set to -1 to disable this control.'))
        self.spin_gop.SetToolTip(tip)

        self.Bind(wx.EVT_COMBOBOX, self.on_preset, self.cmb_preset)
        self.Bind(wx.EVT_COMBOBOX, self.on_profile, self.cmb_profile)
        self.Bind(wx.EVT_COMBOBOX, self.on_level, self.cmb_level)
        self.Bind(wx.EVT_COMBOBOX, self.on_tune, self.cmb_tune)
        self.Bind(wx.EVT_SPINCTRL, self.on_gop, self.spin_gop)

    def default(self):
        """
        Set to default when video codec changes
        """
        self.cmb_tune.Clear(), self.cmb_profile.Clear()
        if self.opt["VideoCodec"] == "-c:v libx264":
            for tune in Hevc_Avc.H264_OPT['Tunes']:
                self.cmb_tune.Append((tune),)
            for prof in Hevc_Avc.H264_OPT["Profiles"]:
                self.cmb_profile.Append((prof),)
            self.spin_gop.SetValue(12)
            self.opt["GOP"] = '-g 12'
            self.lbl_info.SetLabel("H.264 / AVC - libx264")

        elif self.opt["VideoCodec"] == "-c:v libx265":
            for tune in Hevc_Avc.H265_OPT["Tunes"]:
                self.cmb_tune.Append((tune),)
            for prof in Hevc_Avc.H265_OPT["Profiles"]:
                self.cmb_profile.Append((prof),)
            self.spin_gop.SetValue(1)
            self.opt["GOP"] = '-g 1'
            self.lbl_info.SetLabel("H.265 / HEVC - libx265")

        self.opt["Preset"] = '-preset:v medium'
        self.opt["Profile"] = ''
        self.opt["Level"] = ''
        self.opt["Tune"] = ''
        self.opt["Usage"] = ''
        self.opt["Deadline"] = ''
        self.opt["CpuUsed"] = ''
        self.opt["RowMthreading"] = ''

        self.cmb_preset.SetSelection(6)
        self.cmb_profile.SetSelection(0)
        self.cmb_tune.SetSelection(0)
        self.cmb_level.SetSelection(0)

    def on_preset(self, event):
        """
        Set h264/h265 only
        """
        sel = self.cmb_preset.GetStringSelection()
        self.opt["Preset"] = '' if sel == 'None' else f'-preset:v {sel}'
    # ------------------------------------------------------------------#

    def on_profile(self, event):
        """
        Set h264/h265 only
        """
        sel = self.cmb_profile.GetStringSelection()
        self.opt["Profile"] = '' if sel == 'None' else f'-profile:v {sel}'
    # ------------------------------------------------------------------#

    def on_level(self, event):
        """
        Set profile level for h264/h265. This flag must be insert
        after -profile:v parameter.
        """
        sel = self.cmb_level.GetStringSelection()
        self.opt["Level"] = '' if sel == 'None' else f'-level {sel}'
    # ------------------------------------------------------------------#

    def on_tune(self, event):
        """
        Set h264/h265 only
        """
        sel = self.cmb_tune.GetStringSelection()
        self.opt["Tune"] = '' if sel == 'None' else f'-tune:v {sel}'
    # -------------------------------------------------------------------#

    def on_gop(self, event):
        """
        Set group of pictures (GOP)
        """
        val = self.spin_gop.GetValue()
        if val == -1:
            self.opt["GOP"] = ''
        else:
            self.opt["GOP"] = f'-g {val}'
    # ------------------------------------------------------------------#
