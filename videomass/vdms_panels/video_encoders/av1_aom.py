# -*- coding: UTF-8 -*-
"""
FileName: av1_aom.py
Porpose: Contains AOM-AV1 functionalities for A/V Conversions
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.11.2024
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


def presets_aomav1(name):
    """
    Presets collection for AOM-AV1 encoder
    """
    if name == 'Default':
        return {"crf": 35, "cpu": 4, "usage": 0, "fps": 0,
                "vasp": 0, "rmt": True, "trows": 1, "tcols": 1,
                "vbit": -1, "web": False, "minr": -1, "maxr": -1,
                "bsize": -1, "pass": False, "gop": -1,
                }
    return None


class AV1_Aom(scrolled.ScrolledPanel):
    """
    This scroll panel implements video controls functions
    for AOM-AV1 encoder on A/V Conversions.

    """
    # supported libaom Bit Depths (pixel formats)
    PIXELFRMT = [('Auto'), ('yuv420p'), ('yuv422p'), ('yuv444p'), ('gbrp'),
                 ('yuv420p10le'), ('yuv422p10le'), ('yuv444p10le'),
                 ('yuv420p12le'), ('yuv422p12le'), ('yuv444p12le'),
                 ('gbrp10le'), ('gbrp12le'), ('gray'), ('gray10le'),
                 ('gray12le')
                 ]
    ASPECTRATIO = [("Auto"), ("1:1"), ("1.3333"), ("1.7777"), ("2.4:1"),
                   ("3:2"), ("4:3"), ("5:4"), ("8:7"), ("14:10"), ("16:9"),
                   ("16:10"), ("19:10"), ("21:9"), ("32:9"),
                   ]
    FPS = [("Auto"), ("ntsc"), ("pal"), ("film"), ("23.976"), ("24"),
           ("25"), ("29.97"), ("30"), ("48"), ("50"), ("59.94"), ("60"),
           ]
    PRESET = ('Default',)

    def __init__(self, parent, opt):
        """
        This is a child of `nb_Video` on `AV_Conv` class-panel (parent).
        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.parent = parent  # parent is the `nb_Video` here.
        self.opt = opt
        scrolled.ScrolledPanel.__init__(self, parent, -1,
                                        size=(1024, 1024),
                                        style=wx.TAB_TRAVERSAL
                                        | wx.BORDER_NONE,
                                        name="AVC x264 scrolledpanel",
                                        )
        sizerbase = wx.BoxSizer(wx.VERTICAL)
        self.labinfo = wx.StaticText(self, wx.ID_ANY, label="")
        sizerbase.Add(self.labinfo, 0, wx.ALL | wx.CENTER, 2)
        if self.appdata['ostype'] == 'Darwin':
            self.labinfo.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        else:
            self.labinfo.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        boxset = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_reset = wx.Button(self, wx.ID_ANY, _("Reload"), size=(-1, -1))
        boxset.Add(self.btn_reset, 0)
        self.cmb_defprst = wx.ComboBox(self, wx.ID_ANY,
                                       choices=AV1_Aom.PRESET,
                                       size=(-1, -1), style=wx.CB_DROPDOWN
                                       | wx.CB_READONLY,
                                       )
        self.cmb_defprst.SetSelection(0)
        self.cmb_defprst.Disable()

        boxset.Add(self.cmb_defprst, 0, wx.LEFT, 20)

        self.ckbx_web = wx.CheckBox(self, wx.ID_ANY, (_('Optimize for Web')))
        boxset.Add(self.ckbx_web, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        sizerbase.Add(boxset, 0, wx.TOP | wx.CENTRE, 10)
        sizerbase.Add((0, 15), 0)
        boxcrf = wx.BoxSizer(wx.HORIZONTAL)
        labqtz = wx.StaticText(self, wx.ID_ANY, 'CRF:')
        boxcrf.Add(labqtz, 0, wx.ALIGN_CENTER, 2)
        self.slider_crf = wx.Slider(self, wx.ID_ANY, 30, -1, 63,
                                    size=(250, -1), style=wx.SL_HORIZONTAL
                                    )
        boxcrf.Add(self.slider_crf, 0, wx.LEFT | wx.ALIGN_CENTER, 2)
        self.labqtzmt = wx.StaticText(self, wx.ID_ANY, '')
        boxcrf.Add(self.labqtzmt, 0, wx.LEFT | wx.ALIGN_CENTER, 2)
        # boxcrf.Add((20, 0), 0)
        sizerbase.Add(boxcrf, 0, wx.ALL | wx.CENTER, 0)
        sizerbase.Add((0, 15), 0)
        boxopt = wx.BoxSizer(wx.HORIZONTAL)
        labcpu = wx.StaticText(self, wx.ID_ANY, 'CPU Used:')
        boxopt.Add(labcpu, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.cmb_cpu = wx.ComboBox(self, wx.ID_ANY,
                                   choices=['0', '1', '2', '3',
                                            '4', '5', '6', '7', '8'],
                                   style=wx.CB_DROPDOWN | wx.CB_READONLY,
                                   )
        boxopt.Add(self.cmb_cpu, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        boxopt.Add((20, 0), 0)
        labusage = wx.StaticText(self, wx.ID_ANY, 'Usage:')
        boxopt.Add(labusage, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.cmb_usage = wx.ComboBox(self, wx.ID_ANY,
                                     choices=['good', 'realtime', 'allintra'],
                                     style=wx.CB_DROPDOWN | wx.CB_READONLY,
                                     )
        boxopt.Add(self.cmb_usage, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        boxopt.Add((20, 0), 0)
        self.ckbx_rmt = wx.CheckBox(self, wx.ID_ANY, "Row Multi-Threading")
        boxopt.Add(self.ckbx_rmt, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        sizerbase.Add(boxopt, 0, wx.ALL | wx.CENTER, 0)
        line1 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=(-1, -1), style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        sizerbase.Add(line1, 0, wx.ALL | wx.EXPAND, 15)
        gridcod = wx.FlexGridSizer(4, 5, 0, 0)
        labtrows = wx.StaticText(self, wx.ID_ANY, 'Tile Rows:')
        gridcod.Add(labtrows, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.cmb_trows = wx.ComboBox(self, wx.ID_ANY,
                                     choices=['-1', '0', '1', '2', '3',
                                              '4', '5', '6'],
                                     size=(-1, -1), style=wx.CB_DROPDOWN
                                     | wx.CB_READONLY,
                                     )
        gridcod.Add(self.cmb_trows, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        gridcod.Add((40, 0), 0)
        labtcol = wx.StaticText(self, wx.ID_ANY, 'Tile Columns:')
        gridcod.Add(labtcol, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.cmb_tcols = wx.ComboBox(self, wx.ID_ANY,
                                     choices=['-1', '0', '1', '2', '3',
                                              '4', '5', '6'],
                                     size=(-1, -1), style=wx.CB_DROPDOWN
                                     | wx.CB_READONLY,
                                     )
        gridcod.Add(self.cmb_tcols, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        labpass = wx.StaticText(self, wx.ID_ANY, 'Passes:')
        gridcod.Add(labpass, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.ckbx_pass = wx.CheckBox(self, wx.ID_ANY, "Two-Pass Encoding")
        gridcod.Add(self.ckbx_pass, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        gridcod.Add((40, 0), 0)
        labminr = wx.StaticText(self, wx.ID_ANY, 'Minrate (kbps):')
        gridcod.Add(labminr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.spin_minr = wx.SpinCtrl(self, wx.ID_ANY,
                                     "-1", min=-1, max=100000,
                                     style=wx.TE_PROCESS_ENTER
                                     )
        gridcod.Add(self.spin_minr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)

        stextbitr = wx.StaticText(self, wx.ID_ANY, 'Bitrate (kbps):')
        gridcod.Add(stextbitr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.spin_vbrate = wx.SpinCtrl(self, wx.ID_ANY,
                                       "-1", min=-1, max=100000,
                                       size=(150, -1),
                                       style=wx.TE_PROCESS_ENTER
                                       )
        gridcod.Add(self.spin_vbrate, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        gridcod.Add((40, 0), 0)
        labmaxr = wx.StaticText(self, wx.ID_ANY, 'Maxrate (kbps):')
        gridcod.Add(labmaxr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.spin_maxr = wx.SpinCtrl(self, wx.ID_ANY,
                                     "-1", min=-1, max=100000,
                                     style=wx.TE_PROCESS_ENTER
                                     )
        gridcod.Add(self.spin_maxr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        labpixfrm = wx.StaticText(self, wx.ID_ANY, 'Bit Depth:')
        gridcod.Add(labpixfrm, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.cmb_pixfrm = wx.ComboBox(self, wx.ID_ANY,
                                      choices=AV1_Aom.PIXELFRMT,
                                      size=(150, -1), style=wx.CB_DROPDOWN
                                      | wx.CB_READONLY,
                                      )
        gridcod.Add(self.cmb_pixfrm, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        gridcod.Add((40, 0), 0)
        labbuffer = wx.StaticText(self, wx.ID_ANY, 'Bufsize (kbps):')
        gridcod.Add(labbuffer, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.spin_bufsize = wx.SpinCtrl(self, wx.ID_ANY,
                                        "-1", min=-1, max=100000,
                                        style=wx.TE_PROCESS_ENTER
                                        )
        gridcod.Add(self.spin_bufsize, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        sizerbase.Add(gridcod, 0, wx.ALL | wx.CENTER, 0)
        line0 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=(-1, -1), style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        sizerbase.Add(line0, 0, wx.ALL | wx.EXPAND, 15)
        # Option -------------------------------------------
        gridopt = wx.FlexGridSizer(1, 6, 0, 0)
        labvaspect = wx.StaticText(self, wx.ID_ANY, 'Aspect Ratio:')
        gridopt.Add(labvaspect, 0, wx.ALIGN_CENTER_VERTICAL)
        self.cmb_vaspect = wx.ComboBox(self, wx.ID_ANY,
                                       choices=AV1_Aom.ASPECTRATIO,
                                       size=(120, -1), style=wx.CB_DROPDOWN
                                       | wx.CB_READONLY,
                                       )
        gridopt.Add(self.cmb_vaspect, 0, wx.LEFT | wx.CENTER, 5)
        labfps = wx.StaticText(self, wx.ID_ANY, 'FPS:')
        gridopt.Add(labfps, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        self.cmb_fps = wx.ComboBox(self, wx.ID_ANY,
                                   choices=AV1_Aom.FPS,
                                   size=(120, -1),
                                   style=wx.CB_DROPDOWN
                                   | wx.CB_READONLY,
                                   )
        gridopt.Add(self.cmb_fps, 0, wx.LEFT | wx.CENTER, 5)
        lab_gop = wx.StaticText(self, wx.ID_ANY, ("GOP:"))
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
        tip = (_('Constant rate factor. Lower values correspond to higher '
                 'quality and greater file size. Set to -1 to disable this '
                 'control.'))
        self.slider_crf.SetToolTip(tip)
        tip = _('Number of tile rows to use, default changes per resolution')
        self.cmb_trows.SetToolTip(tip)
        tip = (_('Number of tile columns to use, default changes per '
                 'resolution'))
        self.cmb_tcols.SetToolTip(tip)
        tip = (_('Set the Group Of Picture (GOP). Set to -1 to disable '
                 'this control.'))
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
        tip = (_('Specifies the target (average) bit rate for the encoder '
                 'to use. Higher value = higher quality. Set -1 to disable '
                 'this control.'))
        self.spin_vbrate.SetToolTip(tip)
        tip = _('Video width and video height ratio.')
        self.cmb_vaspect.SetToolTip(tip)
        tip = (_('Frame rate (frames per second). Frames repeat a given '
                 'number of times per second. In some countries this is 30 '
                 'for NTSC, other countries (like Italy) use 25 for PAL'))
        self.cmb_fps.SetToolTip(tip)
        tip = (_('Quality/Speed ratio modifier. CPU Used sets how efficient '
                 'the compression will be. Lower values mean slower encoding '
                 'with better quality, and vice-versa. Valid values are from '
                 '0 to 8 inclusive.'))
        self.cmb_cpu.SetToolTip(tip)
        tip = (_('Quality and compression efficiency vs speed trade-off. '
                 '"good" is the default and recommended for most '
                 'applications; "realtime" is recommended for live/fast '
                 'encoding (live streaming, video conferencing, etc); '
                 '"allintra" for All Intra encoding.'))
        self.cmb_usage.SetToolTip(tip)

        tip = (_('Row Multi-Threading enables row-based multi-threading which '
                 'maximizes CPU usage.\n\nTo enable fast decoding '
                 'performance, also set tiles (i.e. Tile Columns 4 and Tile '
                 'Rows 1 or Tile Columns 2 and Tile Rows 2 for 4 tiles).\n\n'
                 'Enabling Row Multi-Threading is only faster when the CPU '
                 'has more threads than the number of encoded tiles.'))
        self.ckbx_rmt.SetToolTip(tip)

        self.Bind(wx.EVT_COMBOBOX, self.on_default_preset, self.cmb_defprst)
        self.Bind(wx.EVT_BUTTON, self.on_reset_args, self.btn_reset)
        self.Bind(wx.EVT_CHECKBOX, self.on_web_optimize, self.ckbx_web)
        self.Bind(wx.EVT_COMBOBOX, self.on_cpu_used, self.cmb_cpu)
        self.Bind(wx.EVT_COMBOBOX, self.on_usage, self.cmb_usage)
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
        self.Bind(wx.EVT_COMBOBOX, self.on_tile_rows, self.cmb_trows)
        self.Bind(wx.EVT_COMBOBOX, self.on_tile_columns, self.cmb_tcols)
        self.Bind(wx.EVT_CHECKBOX, self.on_row_multi_thread, self.ckbx_rmt)
    # ------------------------------------------------------------------#

    def video_options(self):
        """
        Get all video encoder parameters
        """
        return (f'{self.opt["VideoMap"]} '
                f'{self.opt["VideoCodec"]} {self.opt["PixFmt"]} '
                f'{self.opt["CpuUsed"]} {self.opt["TileRows"]} '
                f'{self.opt["TileColumns"]} {self.opt["Usage"]} '
                f'{self.opt["RowMultiThred"]} {self.opt["MinRate"]} '
                f'{self.opt["VideoBitrate"]} {self.opt["CRF"]} '
                f'{self.opt["MaxRate"]} {self.opt["Bufsize"]} '
                f'{self.opt["GOP"]} {self.opt["AspectRatio"]} '
                f'{self.opt["FPS"]} {self.opt["WebOptim"]}'
                )
    # ------------------------------------------------------------------#

    def default(self):
        """
        Reset all controls to default
        """
        if self.opt["VidCmbxStr"] == 'AOM-AV1 10-bit':
            self.labinfo.SetLabel("AOM-AV1 (Alliance for Open Media) 10-bit")
            self.cmb_pixfrm.SetSelection(2), self.on_bit_depth(None, False)
        else:
            self.labinfo.SetLabel("AOM-AV1 (Alliance for Open Media)")
            self.cmb_pixfrm.SetSelection(1), self.on_bit_depth(None, False)

        prst = presets_aomav1('Default')

        self.slider_crf.SetValue(prst['crf']), self.on_crf(None, False)
        self.cmb_cpu.SetSelection(prst['cpu']), self.on_cpu_used(None, False)
        self.cmb_usage.SetSelection(prst['usage']), self.on_usage(None, False)
        self.cmb_fps.SetSelection(prst['fps']), self.on_rate_fps(None, False)
        self.cmb_vaspect.SetSelection(prst['vasp'])
        self.on_vaspect(None, False)
        self.ckbx_rmt.SetValue(prst['rmt'])
        self.on_row_multi_thread(None, False)
        self.cmb_trows.SetSelection(prst['trows'])
        self.on_tile_rows(None, False)
        self.cmb_tcols.SetSelection(prst['tcols'])
        self.on_tile_columns(None, False)
        self.spin_vbrate.SetValue(prst['vbit']), self.on_vbitrate(None, False)
        self.ckbx_web.SetValue(prst['web']), self.on_web_optimize(None, False)
        self.spin_minr.SetValue(prst['minr']), self.on_min_rate(None, False)
        self.spin_maxr.SetValue(prst['maxr']), self.on_max_rate(None, False)
        self.spin_bufsize.SetValue(prst['bsize'])
        self.on_buffer_size(None, False)
        self.ckbx_pass.SetValue(prst['pass']), self.on_pass(None, False)
        self.spin_gop.SetValue(prst['gop']), self.on_gop(None, False)
        self.btn_reset.Disable()
    # ------------------------------------------------------------------#

    def on_reset_args(self, event):
        """
        Reload button event.
        A `None event` argument is provided by the parent
        calling this method, so that the settings are fully reset
        """
        if not event:
            self.cmb_defprst.SetSelection(0)
        self.default()
    # ------------------------------------------------------------------#

    def on_default_preset(self, event):
        """
        This combobox event is triggered by selecting an argument
        in the list, then calling `default` ensures that a preset's
        settings are applied.
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
        self.opt["PixFmt"] = '' if val == 'Auto' else f'-pix_fmt {val}'
    # ------------------------------------------------------------------#

    def on_min_rate(self, event, btnreset=True):
        """
        Event on setting minimun rate kbps
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = self.spin_minr.GetValue()
        self.opt["MinRate"] = '' if val == -1 else f'-minrate {val}k'
    # ------------------------------------------------------------------#

    def on_max_rate(self, event, btnreset=True):
        """
        Event on setting maximun rate kbps
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = self.spin_maxr.GetValue()
        self.opt["MaxRate"] = '' if val == -1 else f'-maxrate {val}k'
    # ------------------------------------------------------------------#

    def on_buffer_size(self, event, btnreset=True):
        """
        Event on setting buffer size kbps
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
        Here the CRF/QP values are set.
        Some codec do not support setting both bitrate
        and CRF, especially if two-pass is enabled.
        Select the quality for constant quality mode
        (from -1 to 63) (default -1)
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = self.slider_crf.GetValue()
        self.labqtzmt.SetLabel(str(val))
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
            self.opt["passlogfile1"] = '-pass 1'
            self.opt["passlogfile2"] = '-pass 2'
        else:
            self.opt["Passes"] = "Auto"
            self.opt["passlogfile1"] = ""
            self.opt["passlogfile2"] = ""

        self.on_vbitrate(None, False)
        self.on_crf(None, False)
    # ------------------------------------------------------------------#

    def on_cpu_used(self, event, btnreset=True):
        """
        Set cpu used Quality/Speed ratio modifier
        (from 0 to 8) (default 1)
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        sel = self.cmb_cpu.GetStringSelection()
        self.opt["CpuUsed"] = f'-cpu-used {sel}'
    # ------------------------------------------------------------------#

    def on_usage(self, event, btnreset=True):
        """
        Set usage Quality and compression efficiency vs speed
        trade-off (from 0 to INT_MAX) (default good)
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        sel = self.cmb_usage.GetStringSelection()
        self.opt["Usage"] = f'-usage {sel}'
    # ------------------------------------------------------------------#

    def on_tile_rows(self, event, btnreset=True):
        """
        Set tile rows, Log2 of number of tile rows to use
        (from -1 to 6) (default -1)
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = self.cmb_trows.GetStringSelection()
        self.opt["TileRows"] = f'-tile-rows {val}'
    # -------------------------------------------------------------------#

    def on_tile_columns(self, event, btnreset=True):
        """
        Set tile columns, Log2 of number of tile columns to use
        (from -1 to 6) (default -1)
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = self.cmb_tcols.GetStringSelection()
        self.opt["TileColumns"] = f'-tile-columns {val}'
    # -------------------------------------------------------------------#

    def on_row_multi_thread(self, event, btnreset=True):
        """
        Enable row based multi-threading (default auto)
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = '-row-mt 1' if self.ckbx_rmt.GetValue() else ''
        self.opt["RowMultiThred"] = val
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
