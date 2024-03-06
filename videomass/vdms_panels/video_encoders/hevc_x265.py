# -*- coding: UTF-8 -*-
"""
FileName: hevc_x265.py
Porpose: Contains H.265 functionality for A/V Conversions
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
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
import os
import wx
import wx.lib.scrolledpanel as scrolled


class Hevc_X265(scrolled.ScrolledPanel):
    """
    This scroll panel implements controls for extra options
    of the `HEVC/AVC` aka h.264/h.265 encoders.
    """
    ASPECTRATIO = [("Auto"), ("1:1"), ("1.3333"), ("1.7777"), ("2.4:1"),
                   ("3:2"), ("4:3"), ("5:4"), ("8:7"), ("14:10"), ("16:9"),
                   ("16:10"), ("19:10"), ("21:9"), ("32:9"),
                   ]
    FPS = [("Auto"), ("ntsc"), ("pal"), ("film"), ("23.976"), ("24"),
           ("25"), ("29.97"), ("30"), ("48"), ("50"), ("59.94"), ("60"),
           ]
    PIXELFRMT = [('None'), ('yuv420p'), ('yuvj420p'), ('yuv422p'),
                 ('yuvj422p'), ('yuv444p'), ('yuvj444p'), ('gbrp'),
                 ('yuv420p10le'), ('yuv422p10le'), ('yuv444p10le'),
                 ('gbrp10le'), ('yuv420p12le'), ('yuv422p12le'),
                 ('yuv444p12le'), ('gbrp12le'), ('gray'), ('gray10le'),
                 ('gray12le')
                 ]
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
    # profile level for h265
    LEVELS = ('None', '1', '2', '2.1', '3', '3.1', '4', '4.1',
              '5', '5.1', '5.2', '6', '6.1', '6.2', '8.5'
              )

    def __init__(self, parent, opt):
        """
        This is a child of `AV_Conv` class-panel (parent) and the `opt`
        attribute is a dict owned by that class.

        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.parent = parent  # parent is the `nb_Video` here.
        self.opt = opt
        scrolled.ScrolledPanel.__init__(self, parent, -1,
                                        size=(1024, 1024),
                                        style=wx.TAB_TRAVERSAL
                                        | wx.BORDER_NONE,
                                        name="HEVC x265 scrolledpanel",
                                        )
        sizerbase = wx.BoxSizer(wx.VERTICAL)
        self.labinfo = wx.StaticText(self, wx.ID_ANY, label="")
        sizerbase.Add(self.labinfo, 0, wx.ALL | wx.CENTER, 2)
        if self.appdata['ostype'] == 'Darwin':
            self.labinfo.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        else:
            self.labinfo.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        self.btn_reset = wx.Button(self, wx.ID_ANY, _("Reload"), size=(-1, -1))
        sizerbase.Add(self.btn_reset, 0, wx.TOP | wx.CENTRE, 10)
        sizerbase.Add((0, 15), 0)

        gridcod = wx.FlexGridSizer(5, 8, 0, 0)
        labpresets = wx.StaticText(self, wx.ID_ANY, 'Preset:')
        gridcod.Add(labpresets, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.cmb_preset = wx.ComboBox(self, wx.ID_ANY,
                                      choices=Hevc_X265.H265_OPT["Presets"],
                                      size=(-1, -1), style=wx.CB_DROPDOWN
                                      | wx.CB_READONLY,
                                      )
        gridcod.Add(self.cmb_preset, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        gridcod.Add((40, 0), 0)
        labcrf = wx.StaticText(self, wx.ID_ANY, 'CRF:')
        gridcod.Add(labcrf, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.slider_crf = wx.Slider(self, wx.ID_ANY, 1, -1, 51,
                                    size=(150, -1), style=wx.SL_HORIZONTAL
                                    | wx.SL_AUTOTICKS
                                    | wx.SL_VALUE_LABEL
                                    | wx.SL_MIN_MAX_LABELS
                                    # | wx.SL_LABELS,
                                    )
        gridcod.Add(self.slider_crf, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        gridcod.Add((40, 0), 0)
        labminr = wx.StaticText(self, wx.ID_ANY, 'Minrate (kbps):')
        gridcod.Add(labminr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.spin_minr = wx.SpinCtrl(self, wx.ID_ANY,
                                     "-1", min=-1, max=900000,
                                     style=wx.TE_PROCESS_ENTER
                                     )
        gridcod.Add(self.spin_minr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        labprofile = wx.StaticText(self, wx.ID_ANY, 'Profile:')
        gridcod.Add(labprofile, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.cmb_profile = wx.ComboBox(self, wx.ID_ANY,
                                       choices=Hevc_X265.H265_OPT["Profiles"],
                                       size=(-1, -1), style=wx.CB_DROPDOWN
                                       | wx.CB_READONLY,
                                       )
        gridcod.Add(self.cmb_profile, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        gridcod.Add((40, 0), 0)
        labpass = wx.StaticText(self, wx.ID_ANY, 'Passes:')
        gridcod.Add(labpass, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.ckbx_pass = wx.CheckBox(self, wx.ID_ANY, "Two-Pass Encoding")
        gridcod.Add(self.ckbx_pass, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        gridcod.Add((40, 0), 0)
        labmaxr = wx.StaticText(self, wx.ID_ANY, 'Maxrate (kbps):')
        gridcod.Add(labmaxr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.spin_maxr = wx.SpinCtrl(self, wx.ID_ANY,
                                     "-1", min=-1, max=900000,
                                     style=wx.TE_PROCESS_ENTER
                                     )
        gridcod.Add(self.spin_maxr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        lablevel = wx.StaticText(self, wx.ID_ANY, 'Level:')
        gridcod.Add(lablevel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.cmb_level = wx.ComboBox(self, wx.ID_ANY,
                                     choices=Hevc_X265.LEVELS, size=(100, -1),
                                     style=wx.CB_DROPDOWN | wx.CB_READONLY
                                     )
        gridcod.Add(self.cmb_level, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        gridcod.Add((40, 0), 0)
        stextbitr = wx.StaticText(self, wx.ID_ANY, 'Bitrate (kbps):')
        gridcod.Add(stextbitr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.spin_vbrate = wx.SpinCtrl(self, wx.ID_ANY,
                                       "-1", min=-1, max=204800,
                                       size=(150, -1),
                                       style=wx.TE_PROCESS_ENTER
                                       )
        gridcod.Add(self.spin_vbrate, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        gridcod.Add((40, 0), 0)
        labbuffer = wx.StaticText(self, wx.ID_ANY, 'Bufsize (kbps):')
        gridcod.Add(labbuffer, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.spin_bufsize = wx.SpinCtrl(self, wx.ID_ANY,
                                        "-1", min=-1, max=900000,
                                        style=wx.TE_PROCESS_ENTER
                                        )
        gridcod.Add(self.spin_bufsize, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        labtune = wx.StaticText(self, wx.ID_ANY, 'Tune:')
        gridcod.Add(labtune, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.cmb_tune = wx.ComboBox(self, wx.ID_ANY,
                                    choices=Hevc_X265.H265_OPT["Tunes"],
                                    size=(-1, -1), style=wx.CB_DROPDOWN
                                    | wx.CB_READONLY,
                                    )
        gridcod.Add(self.cmb_tune, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        gridcod.Add((40, 0), 0)
        labpixfrm = wx.StaticText(self, wx.ID_ANY, 'Bit Depth:')
        gridcod.Add(labpixfrm, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.cmb_pixfrm = wx.ComboBox(self, wx.ID_ANY,
                                      choices=Hevc_X265.PIXELFRMT,
                                      size=(150, -1), style=wx.CB_DROPDOWN
                                      | wx.CB_READONLY,
                                      )
        gridcod.Add(self.cmb_pixfrm, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        sizerbase.Add(gridcod, 0, wx.ALL | wx.CENTER, 0)
        sizerbase.Add((0, 20), 0)
        line0 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=(400, -1), style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        sizerbase.Add(line0, 0, wx.ALL | wx.CENTER, 5)
        # sizerbase.Add((0, 10), 0)
        self.ckbx_web = wx.CheckBox(self, wx.ID_ANY, (_('Use for Web')))
        sizerbase.Add(self.ckbx_web, 0, wx.ALL | wx.CENTER, 2)
        line1 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=(400, -1), style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        sizerbase.Add(line1, 0, wx.ALL | wx.CENTER, 5)

        # Option -------------------------------------------
        sizerbase.Add((0, 10), 0)
        gridopt = wx.FlexGridSizer(1, 6, 0, 0)
        labvaspect = wx.StaticText(self, wx.ID_ANY, 'Aspect Ratio:')
        gridopt.Add(labvaspect, 0, wx.ALIGN_CENTER_VERTICAL)
        self.cmb_vaspect = wx.ComboBox(self, wx.ID_ANY,
                                       choices=Hevc_X265.ASPECTRATIO,
                                       size=(120, -1), style=wx.CB_DROPDOWN
                                       | wx.CB_READONLY,
                                       )
        gridopt.Add(self.cmb_vaspect, 0, wx.LEFT | wx.CENTER, 5)
        labfps = wx.StaticText(self, wx.ID_ANY, 'FPS (frame rate):')
        gridopt.Add(labfps, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        self.cmb_fps = wx.ComboBox(self, wx.ID_ANY,
                                   choices=Hevc_X265.FPS,
                                   size=(120, -1),
                                   style=wx.CB_DROPDOWN
                                   | wx.CB_READONLY,
                                   )
        gridopt.Add(self.cmb_fps, 0, wx.LEFT | wx.CENTER, 5)
        lab_gop = wx.StaticText(self, wx.ID_ANY, ("Group of picture (GOP):"))
        gridopt.Add(lab_gop, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        self.spin_gop = wx.SpinCtrl(self, wx.ID_ANY,
                                    "12", min=-1,
                                    max=1000, size=(-1, -1),
                                    style=wx.TE_PROCESS_ENTER,
                                    )
        gridopt.Add(self.spin_gop, 0, wx.LEFT | wx.CENTRE, 5)
        sizerbase.Add(gridopt, 0, wx.ALL | wx.CENTER, 0)

        self.SetSizer(sizerbase)  # set panel
        self.SetAutoLayout(1)
        self.SetupScrolling()

        tip = (_('Reloads the selected video encoder settings. '
                 'Changes will be discarded.'))
        self.btn_reset.SetToolTip(tip)
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
        tip = _('It can reduce the file size, but takes longer.')
        self.ckbx_pass.SetToolTip(tip)
        tip = (_('Set minimum bitrate tolerance. Most useful in setting up '
                 'a CBR encode. It is of little use otherwise. Set to -1 to '
                 'disable this control.'))
        self.spin_minr.SetToolTip(tip)
        tip = (_('Specifies a maximum tolerance. Requires bufsize to be set. '
                 'Set to -1 to disable this control.'))
        self.spin_maxr.SetToolTip(tip)
        tip = (_('Set ratecontrol buffer size, which determines the '
                 'variability of the output bitrate. '
                 'Set to -1 to disable this control.'))
        self.spin_bufsize.SetToolTip(tip)
        tip = (_('specifies the target (average) bit rate for the encoder '
                 'to use. Higher value = higher quality. Set -1 to disable '
                 'this control.'))
        self.spin_vbrate.SetToolTip(tip)
        tip = (_('Constant rate factor. Lower values = higher quality and '
                 'a larger file size. Set to -1 to disable this control.'))
        self.slider_crf.SetToolTip(tip)
        tip = _('Video width and video height ratio.')
        self.cmb_vaspect.SetToolTip(tip)
        tip = (_('Frames repeat a given number of times per second. In some '
                 'countries this is 30 for NTSC, other countries (like '
                 'Italy) use 25 for PAL'))
        self.cmb_fps.SetToolTip(tip)

        self.Bind(wx.EVT_BUTTON, self.reset_args, self.btn_reset)
        self.Bind(wx.EVT_CHECKBOX, self.on_web_optimize, self.ckbx_web)
        self.Bind(wx.EVT_COMBOBOX, self.on_preset, self.cmb_preset)
        self.Bind(wx.EVT_COMBOBOX, self.on_profile, self.cmb_profile)
        self.Bind(wx.EVT_COMBOBOX, self.on_level, self.cmb_level)
        self.Bind(wx.EVT_COMBOBOX, self.on_tune, self.cmb_tune)
        self.Bind(wx.EVT_SPINCTRL, self.on_gop, self.spin_gop)
        self.Bind(wx.EVT_CHECKBOX, self.on_pass, self.ckbx_pass)
        self.Bind(wx.EVT_SPINCTRL, self.on_vbitrate, self.spin_vbrate)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.on_crf, self.slider_crf)
        self.Bind(wx.EVT_COMBOBOX, self.on_vaspect, self.cmb_vaspect)
        self.Bind(wx.EVT_COMBOBOX, self.on_rate_fps, self.cmb_fps)
        self.Bind(wx.EVT_SPINCTRL, self.on_min_rate, self.spin_minr)
        self.Bind(wx.EVT_SPINCTRL, self.on_max_rate, self.spin_maxr)
        self.Bind(wx.EVT_SPINCTRL, self.on_buffer_size, self.spin_bufsize)
        self.Bind(wx.EVT_COMBOBOX, self.on_bit_depth, self.cmb_pixfrm)

        # self.default(None)
    # ------------------------------------------------------------------#

    def video_options(self):
        """
        Get all video parameters
        """
        return (f'{self.opt["VideoCodec"]} {self.opt["VideoBitrate"]} '
                f'{self.opt["MinRate"]} {self.opt["MaxRate"]} '
                f'{self.opt["Bufsize"]} {self.opt["CRF"]} '
                f'{self.opt["GOP"]} {self.opt["Preset"]} '
                f'{self.opt["Profile"]} {self.opt["Level"]} '
                f'{self.opt["Tune"]} {self.opt["AspectRatio"]} '
                f'{self.opt["FPS"]} {self.opt["VFilters"]} '
                f'{self.opt["PixFmt"]} {self.opt["WebOptim"]} '
                )
    # ------------------------------------------------------------------#

    def default(self):
        """
        Reset all controls to default
        """
        self.cmb_fps.SetSelection(0), self.on_rate_fps(None, False)
        self.cmb_vaspect.SetSelection(0), self.on_vaspect(None, False)
        self.slider_crf.SetMax(51)
        if self.opt["VidCmbxStr"] == 'H.265 10-bit':
            self.cmb_pixfrm.SetSelection(8), self.on_bit_depth(None, False)
            self.cmb_profile.SetSelection(0), self.on_profile(None, False)
            self.labinfo.SetLabel("H.265 HEVC (High Efficiency "
                                  "Video Coding) 10-bit")
            self.slider_crf.SetValue(22), self.on_crf(None, False)
        else:
            self.cmb_pixfrm.SetSelection(1), self.on_bit_depth(None, False)
            self.cmb_profile.SetSelection(0), self.on_profile(None, False)
            self.labinfo.SetLabel("H.265 HEVC (High Efficiency Video Coding)")
            self.slider_crf.SetValue(28), self.on_crf(None, False)

        self.cmb_preset.SetSelection(6), self.on_preset(None, False)
        self.cmb_tune.SetSelection(0), self.on_tune(None, False)
        self.spin_vbrate.SetValue(-1), self.on_vbitrate(None, False)
        self.spin_gop.SetValue(1), self.on_gop(None, False)
        self.cmb_level.SetSelection(0), self.on_level(None, False)
        self.ckbx_pass.SetValue(False), self.on_pass(None, False)
        self.ckbx_web.SetValue(False), self.on_web_optimize(None, False)
        self.spin_minr.SetValue(-1), self.on_min_rate(None, False)
        self.spin_maxr.SetValue(-1), self.on_max_rate(None, False)
        self.spin_bufsize.SetValue(-1), self.on_buffer_size(None, False)
        self.btn_reset.Disable()
    # ------------------------------------------------------------------#

    def reset_args(self, event):
        """
        Set default event
        """
        self.default()
    # ------------------------------------------------------------------#

    def on_bit_depth(self, event, btnreset=True):
        """
        Event on seting pixel format
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = self.cmb_pixfrm.GetValue()
        self.opt["PixFmt"] = '' if val == 'None' else f'-pix_fmt {val}'
    # ------------------------------------------------------------------#

    def on_min_rate(self, event, btnreset=True):
        """
        Event on seting minimun rate kbps
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = self.spin_minr.GetValue()
        self.opt["MinRate"] = '' if val == -1 else f'-minrate {val}k'
    # ------------------------------------------------------------------#

    def on_max_rate(self, event, btnreset=True):
        """
        Event on seting maximun rate kbps
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = self.spin_maxr.GetValue()
        self.opt["MaxRate"] = '' if val == -1 else f'-maxrate {val}k'
    # ------------------------------------------------------------------#

    def on_buffer_size(self, event, btnreset=True):
        """
        Event on seting buffer size kbps
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = self.spin_bufsize.GetValue()
        self.opt["Bufsize"] = '' if val == -1 else f'-bufsize {val}k'
    # ------------------------------------------------------------------#

    def on_web_optimize(self, event, btnreset=True):
        """
        Adds or removes -movflags faststart flag to maximize
        speed on video streaming.
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        check = self.ckbx_web.IsChecked()
        self.opt["WebOptim"] = '-movflags faststart' if check else ''
    # ------------------------------------------------------------------#

    def on_vbitrate(self, event, btnreset=True):
        """
        Here the bitrate values are set.
        Some codec do not support setting both bitrate
        and CRF, especially if two-pass is enabled.
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = self.spin_vbrate.GetValue()
        self.opt["VideoBitrate"] = "" if val == -1 else f"-b:v {val}k"
    # ------------------------------------------------------------------#

    def on_crf(self, event, btnreset=True):
        """
        Here the CRF values are set.
        Some codec do not support setting both bitrate
        and CRF, especially if two-pass is enabled.
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = self.slider_crf.GetValue()
        self.opt["CRF"] = "" if val == -1 else f"-crf {val}"

    # ------------------------------------------------------------------#

    def on_pass(self, event, btnreset=True):
        """
        enable or disable operations for two pass encoding
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        if self.ckbx_pass.IsChecked():
            self.opt["Passes"] = "2"
            tmp = os.path.join(self.appdata["cachedir"], 'tmp', 'passlogfile')
            self.opt["passlogfile1"] = (f'-x265-params "pass=1" '
                                        f'-passlogfile "{tmp}"')
            self.opt["passlogfile2"] = (f'-x265-params "pass=2" '
                                        f'-passlogfile "{tmp}"')
            self.slider_crf.SetValue(-1)
            self.slider_crf.Disable()
            self.spin_vbrate.SetValue(4000)
            self.spin_vbrate.Enable()
        else:
            self.opt["Passes"] = "Auto"
            self.opt["passlogfile1"] = ""
            self.opt["passlogfile2"] = ""
            if self.opt["VidCmbxStr"] == 'H.265 10-bit':
                self.slider_crf.SetValue(22)
            else:
                self.slider_crf.SetValue(28)
            self.slider_crf.Enable()
            self.spin_vbrate.SetValue(-1)
            self.spin_vbrate.Enable()

        self.on_vbitrate(None, False)
        self.on_crf(None, False)
    # ------------------------------------------------------------------#

    def on_preset(self, event, btnreset=True):
        """
        Set h264/h265 only
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        sel = self.cmb_preset.GetStringSelection()
        self.opt["Preset"] = '' if sel == 'None' else f'-preset:v {sel}'
    # ------------------------------------------------------------------#

    def on_profile(self, event, btnreset=True):
        """
        Set h264/h265 only
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        sel = self.cmb_profile.GetStringSelection()
        self.opt["Profile"] = '' if sel == 'None' else f'-profile:v {sel}'
    # ------------------------------------------------------------------#

    def on_level(self, event, btnreset=True):
        """
        Set profile level for h264/h265. This flag must be insert
        after -profile:v parameter.
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        sel = self.cmb_level.GetStringSelection()
        self.opt["Level"] = '' if sel == 'None' else f'-level {sel}'
    # ------------------------------------------------------------------#

    def on_tune(self, event, btnreset=True):
        """
        Set h264/h265 only
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        sel = self.cmb_tune.GetStringSelection()
        self.opt["Tune"] = '' if sel == 'None' else f'-tune:v {sel}'
    # -------------------------------------------------------------------#

    def on_gop(self, event, btnreset=True):
        """
        Set group of pictures (GOP)
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = self.spin_gop.GetValue()
        self.opt["GOP"] = '' if val == -1 else f'-g {val}'
    # ------------------------------------------------------------------#

    def on_vaspect(self, event, btnreset=True):
        """
        Set aspect parameter (16:9, 4:3)
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = self.cmb_vaspect.GetValue()
        self.opt["AspectRatio"] = '' if val == 'Auto' else f'-aspect {val}'
    # ------------------------------------------------------------------#

    def on_rate_fps(self, event, btnreset=True):
        """
        Set video rate parameter with fps values
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        fps = self.cmb_fps.GetValue()
        self.opt["FPS"] = '' if fps == 'Auto' else f'-r {fps}'
    # ------------------------------------------------------------------#
