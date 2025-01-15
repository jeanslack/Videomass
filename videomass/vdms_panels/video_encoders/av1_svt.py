# -*- coding: UTF-8 -*-
"""
FileName: av1_svt.py
Porpose: Contains SVT-AV1 functionalities for A/V Conversions
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


def presets_svtav1(name):
    """
    Presets collection for svtav1 encoder
    from <https://gitlab.com/AOMediaCodec/SVT-AV1/-/blob/master/Docs/Ffmpeg.md>
    """
    if name == 'Default':
        return {"crf": 30, "prf": 0, "lev": 0, "tune": 0, "fps": 0,
                "vasp": 0, "fdec": False, "scd": False, "prs": 5,
                "fgr": -1, "fgrden": False, "trows": 0, "tcols": 0,
                "vbit": -1, "web": False, "minr": -1, "maxr": -1,
                "bsize": -1, "pass": False, "gop": -1,
                }
    if name == 'Fast/Realtime Encoding':
        return {"crf": 35, "prf": 0, "lev": 0, "tune": 0, "fps": 0,
                "vasp": 0, "fdec": False, "scd": False, "prs": 10,
                "fgr": -1, "fgrden": False, "trows": 0, "tcols": 0,
                "vbit": -1, "web": False, "minr": -1, "maxr": -1,
                "bsize": -1, "pass": False, "gop": -1,
                }
    if name == 'Encoding for Personal Use':
        return {"crf": 32, "prf": 0, "lev": 0, "tune": 0, "fps": 0,
                "vasp": 0, "fdec": False, "scd": False, "prs": 5,
                "fgr": 8, "fgrden": False, "trows": 0, "tcols": 0,
                "vbit": -1, "web": False, "minr": -1, "maxr": -1,
                "bsize": -1, "pass": False, "gop": 240,
                }
    if name == 'Encoding for Video On Demand':
        return {"crf": 25, "prf": 0, "lev": 0, "tune": 0, "fps": 0,
                "vasp": 0, "fdec": False, "scd": False, "prs": 2,
                "fgr": 8, "fgrden": False, "trows": 0, "tcols": 0,
                "vbit": -1, "web": False, "minr": -1, "maxr": -1,
                "bsize": -1, "pass": False, "gop": 24,
                }
    return None


class AV1_Svt(scrolled.ScrolledPanel):
    """
    This scroll panel implements video controls functions
    for SVT-AV1 encoder on A/V Conversions..

    """
    # profile/tunes used by libsvtav1
    SVT_OPT = {("Profiles"): ("Auto", "main", "high", "professional"),
               ("Tunes"): ("Auto", "psnr", "vq", "ssim")
               }
    # levels libsvtav1 (Auto = 0 as param)
    LEVELS = ('Auto', '2.0', '2.1', '2.2', '2.3', '3.0', '3.1', '3.2',
              '3.3', '4.0', '4.1', '4.2', '4.3', '5.0', '5.1', '5.2', '5.3',
              '6.0', '6.1', '6.2', '6.3', '7.0', '7.1', '7.2', '7.3',
              )
    # supported libsvtav1 Bit Depths
    PIXELFRMT = [('Auto'), ('yuv420p'), ('yuv420p10le')]
    ASPECTRATIO = [("Auto"), ("1:1"), ("1.3333"), ("1.7777"), ("2.4:1"),
                   ("3:2"), ("4:3"), ("5:4"), ("8:7"), ("14:10"), ("16:9"),
                   ("16:10"), ("19:10"), ("21:9"), ("32:9"),
                   ]
    FPS = [("Auto"), ("ntsc"), ("pal"), ("film"), ("23.976"), ("24"),
           ("25"), ("29.97"), ("30"), ("48"), ("50"), ("59.94"), ("60"),
           ]

    PRESET = ('Default',
              'Fast/Realtime Encoding',
              'Encoding for Personal Use',
              'Encoding for Video On Demand')

    def __init__(self, parent, opt):
        """
        This is a child of `nb_Video` of `AV_Conv` class-panel (parent).
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
                                       choices=AV1_Svt.PRESET,
                                       size=(-1, -1), style=wx.CB_DROPDOWN
                                       | wx.CB_READONLY,
                                       )
        self.cmb_defprst.SetSelection(0)
        boxset.Add(self.cmb_defprst, 0, wx.LEFT, 20)
        self.ckbx_web = wx.CheckBox(self, wx.ID_ANY, (_('Optimize for Web')))
        boxset.Add(self.ckbx_web, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)

        sizerbase.Add(boxset, 0, wx.TOP | wx.CENTRE, 10)
        sizerbase.Add((0, 15), 0)
        boxprst = wx.BoxSizer(wx.HORIZONTAL)
        labqtz = wx.StaticText(self, wx.ID_ANY, 'CRF:')
        boxprst.Add(labqtz, 0, wx.ALIGN_CENTER)
        self.slider_crf = wx.Slider(self, wx.ID_ANY, 30, -1, 63,
                                    size=(230, -1), style=wx.SL_HORIZONTAL
                                    )
        boxprst.Add(self.slider_crf, 0, wx.LEFT | wx.ALIGN_CENTER, 2)
        self.labcrfmt = wx.StaticText(self, wx.ID_ANY, '')
        boxprst.Add(self.labcrfmt, 0, wx.LEFT | wx.ALIGN_CENTER, 2)
        boxprst.Add((20, 0), 0)
        labpreset = wx.StaticText(self, wx.ID_ANY, 'Preset:')
        boxprst.Add(labpreset, 0, wx.LEFT | wx.ALIGN_CENTER, 20)
        self.slider_prs = wx.Slider(self, wx.ID_ANY, 5, 0, 13,
                                    size=(230, -1), style=wx.SL_HORIZONTAL
                                    )
        boxprst.Add(self.slider_prs, 0, wx.LEFT | wx.ALIGN_CENTER, 2)

        self.labprstmt = wx.StaticText(self, wx.ID_ANY, '')
        boxprst.Add(self.labprstmt, 0, wx.LEFT | wx.ALIGN_CENTER, 2)

        sizerbase.Add(boxprst, 0, wx.ALL | wx.CENTER, 0)
        sizerbase.Add((0, 15), 0)
        boxopt = wx.BoxSizer(wx.HORIZONTAL)
        self.ckbx_fastd = wx.CheckBox(self, wx.ID_ANY, "Fast Decode")
        boxopt.Add(self.ckbx_fastd, 0)
        self.ckbx_scd = wx.CheckBox(self, wx.ID_ANY, "Scene Detection")
        boxopt.Add(self.ckbx_scd, 0)
        sizerbase.Add(boxopt, 0, wx.ALL | wx.CENTER, 0)
        sizerbase.Add((0, 15), 0)

        boxsfgr = wx.BoxSizer(wx.HORIZONTAL)
        labpfgrain = wx.StaticText(self, wx.ID_ANY, 'Film Grain:')
        boxsfgr.Add(labpfgrain, 0, wx.ALIGN_CENTER_VERTICAL)
        boxsfgr.Add((10, 10), 0)
        self.slider_fgr = wx.Slider(self, wx.ID_ANY, 0, -1, 50,
                                    size=(230, -1), style=wx.SL_HORIZONTAL
                                    )
        boxsfgr.Add(self.slider_fgr, 0, wx.LEFT | wx.ALIGN_CENTER, 2)
        self.labpfgrainmt = wx.StaticText(self, wx.ID_ANY, '')
        boxsfgr.Add(self.labpfgrainmt, 0, wx.LEFT | wx.ALIGN_CENTER, 2)
        boxsfgr.Add((20, 20), 0)
        self.ckbx_fgrden = wx.CheckBox(self, wx.ID_ANY, "Film Grain Denoise")
        boxsfgr.Add(self.ckbx_fgrden, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        sizerbase.Add(boxsfgr, 0, wx.CENTER, 5)
        line1 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=(400, -1), style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        sizerbase.Add(line1, 0, wx.ALL | wx.EXPAND, 15)
        gridcod = wx.FlexGridSizer(5, 8, 0, 0)
        labtrows = wx.StaticText(self, wx.ID_ANY, 'Tile Rows:')
        gridcod.Add(labtrows, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.cmb_trows = wx.ComboBox(self, wx.ID_ANY,
                                     choices=['0', '1', '2', '3',
                                              '4', '5', '6'],
                                     size=(-1, -1), style=wx.CB_DROPDOWN
                                     | wx.CB_READONLY,
                                     )
        gridcod.Add(self.cmb_trows, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        gridcod.Add((40, 0), 0)
        labtcol = wx.StaticText(self, wx.ID_ANY, 'Tile Columns:')
        gridcod.Add(labtcol, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)

        self.cmb_tcols = wx.ComboBox(self, wx.ID_ANY,
                                     choices=['0', '1', '2', '3', '4'],
                                     size=(-1, -1), style=wx.CB_DROPDOWN
                                     | wx.CB_READONLY,
                                     )
        gridcod.Add(self.cmb_tcols, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        gridcod.Add((40, 0), 0)
        labminr = wx.StaticText(self, wx.ID_ANY, 'Minrate (kbps):')
        gridcod.Add(labminr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.spin_minr = wx.SpinCtrl(self, wx.ID_ANY,
                                     "-1", min=-1, max=100000,
                                     style=wx.TE_PROCESS_ENTER
                                     )
        gridcod.Add(self.spin_minr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        labprofile = wx.StaticText(self, wx.ID_ANY, 'Profile:')
        gridcod.Add(labprofile, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.cmb_profile = wx.ComboBox(self, wx.ID_ANY,
                                       choices=AV1_Svt.SVT_OPT["Profiles"],
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
                                     "-1", min=-1, max=100000,
                                     style=wx.TE_PROCESS_ENTER
                                     )
        gridcod.Add(self.spin_maxr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        lablevel = wx.StaticText(self, wx.ID_ANY, 'Level:')
        gridcod.Add(lablevel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.cmb_level = wx.ComboBox(self, wx.ID_ANY,
                                     choices=AV1_Svt.LEVELS, size=(100, -1),
                                     style=wx.CB_DROPDOWN | wx.CB_READONLY
                                     )
        gridcod.Add(self.cmb_level, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        gridcod.Add((40, 0), 0)
        stextbitr = wx.StaticText(self, wx.ID_ANY, 'Bitrate (kbps):')
        gridcod.Add(stextbitr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.spin_vbrate = wx.SpinCtrl(self, wx.ID_ANY,
                                       "-1", min=-1, max=100000,
                                       size=(150, -1),
                                       style=wx.TE_PROCESS_ENTER
                                       )
        gridcod.Add(self.spin_vbrate, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        gridcod.Add((40, 0), 0)
        labbuffer = wx.StaticText(self, wx.ID_ANY, 'Bufsize (kbps):')
        gridcod.Add(labbuffer, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.spin_bufsize = wx.SpinCtrl(self, wx.ID_ANY,
                                        "-1", min=-1, max=100000,
                                        style=wx.TE_PROCESS_ENTER
                                        )
        gridcod.Add(self.spin_bufsize, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        labtune = wx.StaticText(self, wx.ID_ANY, 'Tune:')
        gridcod.Add(labtune, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.cmb_tune = wx.ComboBox(self, wx.ID_ANY,
                                    choices=AV1_Svt.SVT_OPT["Tunes"],
                                    size=(-1, -1), style=wx.CB_DROPDOWN
                                    | wx.CB_READONLY,
                                    )
        gridcod.Add(self.cmb_tune, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        gridcod.Add((40, 0), 0)
        labpixfrm = wx.StaticText(self, wx.ID_ANY, 'Bit Depth:')
        gridcod.Add(labpixfrm, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.cmb_pixfrm = wx.ComboBox(self, wx.ID_ANY,
                                      choices=AV1_Svt.PIXELFRMT,
                                      size=(150, -1), style=wx.CB_DROPDOWN
                                      | wx.CB_READONLY,
                                      )
        gridcod.Add(self.cmb_pixfrm, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        sizerbase.Add(gridcod, 0, wx.ALL | wx.CENTER, 0)
        line0 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=(400, -1), style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        sizerbase.Add(line0, 0, wx.ALL | wx.EXPAND, 15)

        # Option -------------------------------------------
        gridopt = wx.FlexGridSizer(1, 6, 0, 0)
        labvaspect = wx.StaticText(self, wx.ID_ANY, 'Aspect Ratio:')
        gridopt.Add(labvaspect, 0, wx.ALIGN_CENTER_VERTICAL)
        self.cmb_vaspect = wx.ComboBox(self, wx.ID_ANY,
                                       choices=AV1_Svt.ASPECTRATIO,
                                       size=(120, -1), style=wx.CB_DROPDOWN
                                       | wx.CB_READONLY,
                                       )
        gridopt.Add(self.cmb_vaspect, 0, wx.LEFT | wx.CENTER, 5)
        labfps = wx.StaticText(self, wx.ID_ANY, 'FPS:')
        gridopt.Add(labfps, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        self.cmb_fps = wx.ComboBox(self, wx.ID_ANY,
                                   choices=AV1_Svt.FPS,
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
        tip = (_('presets 1-3 represent extremely high efficiency, for use '
                 'when encode time is not important and quality/size of the '
                 'resulting video file is critical.\n\nPresets 4-6 are '
                 'commonly used by home enthusiasts as they represent a '
                 'balance of efficiency and reasonable compute time.\n\n'
                 'Presets between 7 and 12 are used for fast and real-time '
                 'encoding.\n\nPreset 13 is even faster but not intended for '
                 'direct human consumption--it can be used, for example, as a '
                 'per-scene quality metric in VOD applications. One should '
                 'use the lowest preset that is tolerable.'))
        self.slider_prs.SetToolTip(tip)
        tip = (_('Constant rate factor. This parameter governs the '
                 'quality/size trade-off.\n\nHigher CRF values will result in '
                 'a final output that takes less space, but begins to lose '
                 'detail.\n\nLower CRF values retain more detail at the cost '
                 'of larger file sizes. A good starting point for 1080p video '
                 'is 30.\n\nSet to -1 to disable this control.'))
        self.slider_crf.SetToolTip(tip)
        tip = (_('The "Film Grain" parameter allows SVT-AV1 to detect and '
                 'delete film grain from the source video, and replace it '
                 'with synthetic grain of the same character, resulting in '
                 'significant bitrate savings.\n\nA value of 8 is a '
                 'reasonable starting point for live-action video with a '
                 'normal amount of grain.\n\nHigher values in the range of '
                 '10-15 enable more aggressive use of this technique for '
                 'video with lots of natural grain.\n\nFor 2D animation, '
                 'lower values in the range of 4-6 are often appropriate. '
                 '\n\nIf the source video does not have natural grain, this '
                 'parameter can be set to -1 to disable it or at least 0.'))
        self.slider_fgr.SetToolTip(tip)
        tip = (_('If enabled, the "Film Grain Denoiser" option can mitigate '
                 'the detail removal caused by high "Film Grain" values '
                 'required to preserve the look of very grainy films\n\n'
                 'By default, the denoised frames are passed to be '
                 'encoded as the final pictures, enabling this feature '
                 'will lead to the original frames to be used instead. '))
        self.ckbx_fgrden.SetToolTip(tip)
        tip = (_('Enables encoder optimization to produce faster (less CPU '
                 'intensive) bit streams to decode, similar to the fastdecode '
                 'tuning in x264 and x265.'))
        self.ckbx_fastd.SetToolTip(tip)
        tip = _('Number of tile rows to use, default changes per resolution')
        self.cmb_trows.SetToolTip(tip)
        tip = (_('Number of tile columns to use, '
                 'default changes per resolution'))
        self.cmb_tcols.SetToolTip(tip)
        tip = _('Set profile restrictions')
        self.cmb_profile.SetToolTip(tip)
        tip = _('Specify level for a selected profile')
        self.cmb_level.SetToolTip(tip)
        tip = _('Tune the encoding params')
        self.cmb_tune.SetToolTip(tip)
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

        self.Bind(wx.EVT_COMBOBOX, self.on_default_preset, self.cmb_defprst)
        self.Bind(wx.EVT_BUTTON, self.on_reset_args, self.btn_reset)
        self.Bind(wx.EVT_CHECKBOX, self.on_web_optimize, self.ckbx_web)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.on_preset, self.slider_prs)
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
        self.Bind(wx.EVT_COMBOBOX, self.on_tile_rows, self.cmb_trows)
        self.Bind(wx.EVT_COMBOBOX, self.on_tile_columns, self.cmb_tcols)
        self.Bind(wx.EVT_CHECKBOX, self.on_scene_detect, self.ckbx_scd)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.on_filmgrain, self.slider_fgr)
        self.Bind(wx.EVT_CHECKBOX, self.on_filmgrane_denoiser,
                  self.ckbx_fgrden)
        self.Bind(wx.EVT_CHECKBOX, self.on_fast_decode, self.ckbx_fastd)
    # ------------------------------------------------------------------#

    def video_options(self):
        """
        Get all video encoder parameters
        """
        args = (f'-svtav1-params "{self.opt["Tune"]}{self.opt["TileColumns"]}'
                f'{self.opt["TileRows"]}{self.opt["SceneDetect"]}'
                f'{self.opt["FilmGrain"]}{self.opt["FilmGrainDenoiser"]}'
                f'{self.opt["FastDecode"]}"')

        # remove last colon (:) character
        svtparams = ''.join(args.rsplit(sep=':', maxsplit=1))

        return (f'{self.opt["VideoMap"]} '
                f'{self.opt["VideoCodec"]} {self.opt["Preset"]} '
                f'{self.opt["Profile"]} {self.opt["Level"]} '
                f'{self.opt["CRF"]} {self.opt["VideoBitrate"]} '
                f'{self.opt["MinRate"]} {self.opt["MaxRate"]} '
                f'{self.opt["Bufsize"]} {self.opt["GOP"]} '
                f'{self.opt["PixFmt"]} {self.opt["AspectRatio"]} '
                f'{self.opt["FPS"]} {self.opt["WebOptim"]} {svtparams}'
                )
    # ------------------------------------------------------------------#

    def default(self):
        """
        Reset all controls to default
        """
        if self.opt["VidCmbxStr"] == 'SVT-AV1 10-bit':
            self.labinfo.SetLabel("SVT-AV1 (Scalable Video Technology) 10-bit")
            self.cmb_pixfrm.SetSelection(2), self.on_bit_depth(None, False)
        else:
            self.labinfo.SetLabel("SVT-AV1 (Scalable Video Technology)")
            self.cmb_pixfrm.SetSelection(1), self.on_bit_depth(None, False)

        prst = presets_svtav1(self.cmb_defprst.GetStringSelection())

        self.slider_crf.SetValue(prst['crf']), self.on_crf(None, False)
        self.cmb_profile.SetSelection(prst['prf'])
        self.on_profile(None, False)
        self.cmb_level.SetSelection(prst['lev']), self.on_level(None, False)
        self.cmb_tune.SetSelection(prst['tune']), self.on_tune(None, False)
        self.cmb_fps.SetSelection(prst['fps']), self.on_rate_fps(None, False)
        self.cmb_vaspect.SetSelection(prst['vasp'])
        self.on_vaspect(None, False)
        self.ckbx_fastd.SetValue(prst['fdec'])
        self.on_fast_decode(None, False)
        self.ckbx_scd.SetValue(prst['scd']), self.on_scene_detect(None, False)
        self.slider_prs.SetValue(prst['prs']), self.on_preset(None, False)
        self.slider_fgr.SetValue(prst['fgr']), self.on_filmgrain(None, False)
        self.ckbx_fgrden.SetValue(prst['fgrden'])
        self.on_filmgrane_denoiser(None, False)
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
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = self.slider_crf.GetValue()
        self.labcrfmt.SetLabel(str(val))

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

    def on_preset(self, event, btnreset=True):
        """
        Set svtav1 preset
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        sel = self.slider_prs.GetValue()
        self.labprstmt.SetLabel(str(sel))
        self.opt["Preset"] = f'-preset {sel}'
    # ------------------------------------------------------------------#

    def on_profile(self, event, btnreset=True):
        """
        Set svtav1 profile
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        sel = self.cmb_profile.GetStringSelection()
        self.opt["Profile"] = '' if sel == 'Auto' else f'-profile:v {sel}'
    # ------------------------------------------------------------------#

    def on_level(self, event, btnreset=True):
        """
        Set profile level for svtav1. This flag must be insert
        after -profile:v parameter.
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        sel = self.cmb_level.GetStringSelection()
        self.opt["Level"] = '' if sel == 'Auto' else f'-level:v {sel}'
    # ------------------------------------------------------------------#

    def on_tune(self, event, btnreset=True):
        """
        Set svtav1 tune
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = str(self.cmb_tune.GetSelection())
        self.opt["Tune"] = f'tune={val}:'
    # -------------------------------------------------------------------#

    def on_tile_rows(self, event, btnreset=True):
        """
        Set tile rows
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = self.cmb_trows.GetStringSelection()
        self.opt["TileRows"] = f'tile-rows={val}:'
    # -------------------------------------------------------------------#

    def on_tile_columns(self, event, btnreset=True):
        """
        Set tile columns
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = self.cmb_tcols.GetStringSelection()
        self.opt["TileColumns"] = f'tile-columns={val}:'
    # -------------------------------------------------------------------#

    def on_scene_detect(self, event, btnreset=True):
        """
        Set scene change detection `sc_detection=bool` or `scd=bool`
        (boolean)
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = '1' if self.ckbx_scd.GetValue() else '0'
        self.opt["SceneDetect"] = f'scd={val}:'
    # -------------------------------------------------------------------#

    def on_filmgrain(self, event, btnreset=True):
        """
        Get film grain value by moving slider.
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = self.slider_fgr.GetValue()
        self.labpfgrainmt.SetLabel(str(val))

        if val == -1:
            self.opt["FilmGrain"] = ""
            self.ckbx_fgrden.SetValue(False)
            self.ckbx_fgrden.Disable()
            self.on_filmgrane_denoiser(None, False)
        else:
            self.opt["FilmGrain"] = f"film-grain={val}:"
            if not self.ckbx_fgrden.IsEnabled():
                self.ckbx_fgrden.Enable()
    # ------------------------------------------------------------------#

    def on_filmgrane_denoiser(self, event, btnreset=True):
        """
        Set film grain denoiser
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = 'film-grain-denoise=0:' if self.ckbx_fgrden.GetValue() else ''
        self.opt["FilmGrainDenoiser"] = val
    # -------------------------------------------------------------------#

    def on_fast_decode(self, event, btnreset=True):
        """
        Set fast decode
        """
        if not self.btn_reset.IsEnabled() and btnreset:
            self.btn_reset.Enable()

        val = 'fast-decode=1:' if self.ckbx_fastd.GetValue() else ''
        self.opt["FastDecode"] = val
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
