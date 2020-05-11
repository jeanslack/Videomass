# -*- coding: UTF-8 -*-

#########################################################
# FileName: av_conversions.py
# Porpose: audio/video conversions interface
# Compatibility: Python3, wxPython4 Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Aug.02.2019, Sept.24.2019, Dic.04.2019
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
import os
import wx.lib.agw.floatspin as FS
import wx.lib.agw.gradientbutton as GB
from videomass3.vdms_io.IO_tools import volumeDetectProcess
from videomass3.vdms_io.IO_tools import stream_play
from videomass3.vdms_io.filenames_check import inspect
from videomass3.vdms_dialogs.epilogue import Formula
from videomass3.vdms_dialogs import audiodialogs
from videomass3.vdms_dialogs import presets_addnew
from videomass3.vdms_dialogs import video_filters
from videomass3.vdms_frames import shownormlist
from videomass3.vdms_utils import optimizations
# # colour rappresentetion in rgb
GREY_DISABLED = 165, 165, 165
GREY_DARK = 28, 28, 28
AZURE_NEON = 158, 201, 232
YELLOW_LMN = 255, 255, 0
# colour rappresentetion in html
AZURE = '#15a6a6'
YELLOW = '#a29500'
RED = '#ea312d'
ORANGE = '#f28924'
GREENOLIVE = '#6aaf23'
GREEN = '#268826'
CIANO = '#61ccc7'  # rgb form (wx.Colour(97, 204, 199)
VIOLET = '#D64E93'
LIMEGREEN = '#87A615'
TROPGREEN = '#15A660'

# setting the path to the configuration directory:
get = wx.GetApp()
DIR_CONF = get.DIRconf

# Dictionary definition for command settings:
cmd_opt = {"VidCmbxStr": "x264", "OutputFormat": "mkv",
           "VideoCodec": "-c:v libx264", "ext_input": "",
           "Passing": "1 pass", "InputDir": "", "OutputDir": "",
           "VideoSize": "", "AspectRatio": "", "FPS": "", "Presets": "",
           "Profile": "", "Level": "", "Tune": "", "VideoBitrate": "",
           "CRF": "", "WebOptim": "",
           "MinRate": "", "MaxRate": "", "Bufsize": "", "AudioCodStr": "",
           "AudioInMap": ["", ""], "AudioOutMap": ["-map 0:a?", ""],
           "SubtitleMap": "-map 0:s?", "AudioCodec": ["", ""],
           "AudioChannel": ["", ""], "AudioRate": ["", ""],
           "AudioBitrate": ["", ""], "AudioDepth": ["", ""], "PEAK": "",
           "EBU": "", "RMS": "", "Deinterlace": "", "Interlace": "",
           "PixelFormat": "", "Orientation": ["", ""], "Crop": "",
           "Scale": "", "Setdar": "", "Setsar": "", "Denoiser": "",
           "VFilters": "", "PixFmt": "-pix_fmt yuv420p", "Deadline": "",
           "CpuUsed": "", "RowMthreading": "",
           }
# MUXERS dictionary:
MUXERS = {'mkv': 'matroska', 'avi': 'avi', 'flv': 'flv', 'mp4': 'mp4',
          'm4v': 'null', 'ogg': 'ogg', 'webm': 'webm',
          }
# Namings in the video container selection combo box:
VCODECS = ({"Mpeg4": {"-c:v mpeg4": ["avi"]},
            "x264": {"-c:v libx264": ["mkv", "mp4", "avi", "flv", "m4v"]},
            "x265": {"-c:v libx265": ["mkv", "mp4", "avi", "m4v"]},
            "Theora": {"-c:v libtheora": ["ogv"]},
            # "AV1": {"-c:v libaom-av1 -strict -2",["mkv"]},
            "Vp8": {"-c:v libvpx": ["webm"]},
            "Vp9": {"-c:v libvpx-vp9": ["webm"]},
            "Copy": {"-c:v copy": ["mkv", "mp4", "avi", "flv",
                                   "m4v", "ogv", "webm", "Copy"]}
            })
# Namings in the audio codec selection on audio radio box:
ACODECS = {('Auto'): (""),
           ('PCM'): ("pcm_s16le"),
           ('FLAC'): ("flac"),
           ('AAC'): ("aac"),
           ('ALAC'): ("alac"),
           ('AC3'): ("ac3"),
           ('VORBIS'): ("libvorbis"),
           ('LAME'): ("libmp3lame"),
           ('OPUS'): ("libopus"),
           ('Copy'): ("copy"),
           ('No Audio'): ("-an")
           }
# Namings in the audio format selection on Container combobox:
A_FORMATS = ('wav', 'mp3', 'ac3', 'ogg', 'flac', 'm4a', 'aac'
             )
# compatibility between video formats and related audio codecs:
AV_FORMATS = {('avi'): ('default', 'wav', None, None, None, 'ac3', None,
                        'mp3', None, 'copy', 'mute'),
              ('flv'): ('default', None, None, 'aac', None, 'ac3', None,
                        'mp3', None, 'copy', 'mute'),
              ('mp4'): ('default', None, None, 'aac', None, 'ac3', None,
                        'mp3', None, 'copy', 'mute'),
              ('m4v'): ('default', None, None, 'aac', 'alac', None, None,
                        None, None, 'copy', 'mute'),
              ('mkv'): ('default', 'wav', 'flac', 'aac', None, 'ac3', 'ogg',
                        'mp3', 'opus', 'copy', 'mute'),
              ('webm'): ('default', None, None, None, None, None, 'ogg',
                         None, 'opus', 'copy', 'mute'),
              ('ogv'): ('default', None, 'flac', None, None, None, 'ogg',
                        None, 'opus', 'copy', 'mute'),
              ('wav'): (None, 'wav', None, None, None, None, None, None,
                        None, 'copy', None),
              ('mp3'): (None, None, None, None, None, None, None, 'mp3',
                        None, 'copy', None),
              ('ac3'): (None, None, None, None, None, 'ac3', None, None,
                        None, 'copy', None),
              ('ogg'): (None, None, None, None, None, None, 'ogg', None,
                        None, 'copy', None),
              ('flac'): (None, None, 'flac', None, None, None, None, None,
                         None, 'copy', None),
              ('m4a'): (None, None, None, None, 'alac', None, None, None,
                        None, 'copy', None),
              ('aac'): (None, None, None, 'aac', None, None, None, None,
                        None, 'copy', None),
              }
# presets used by x264 and h265:
X264_OPT = {("Presets"): ("None", "ultrafast", "superfast",
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
# Used by x265 only
X265_OPT = {("Presets"): ("None", "ultrafast", "superfast",
                          "veryfast", "faster", "fast", "medium",
                          "slow", "slower", "veryslow", "placebo"
                          ),
            ("Profiles"): ("None", "main", "main10", "mainstillpicture",
                           "msp", "main-intra", "main10-intra", "main444-8",
                           "main444-intra", "main444-stillpicture",
                           "main422-10", "main422-10-intra", "main444-10",
                           "main444-10-intra", "main12", "main12-intra",
                           "main422-12", "main422-12-intra", "main444-12",
                           "main444-12-intra", "main444-16-intra",
                           "main444-16-stillpicture"
                           ),
            ("Tunes"): ("None", "grain", "psnr", "ssim", "fastdecode",
                        "zerolatency")
            }
# profile level for profiles x264/x265
LEVELS = ('None', '1', '2', '2.1', '3', '3.1', '4', '4.1',
          '5', '5.1', '5.2', '6', '6.1', '6.2', '8.5'
          )
# optimization list for vp8/vp9
OPTIMIZ_VP9 = ('Default',
               'Vp9 best for Archive',
               'Vp9 CBR Web streaming',
               'Vp9 Constrained ABR-VBV live streaming')
# optimization list for x264/x265
OPTIMIZ_HEVC_AVC = ('Default',
                    'x264 best for Archive',
                    'x265 best for Archive',
                    'x264 ABR for devices',
                    'x265 ABR for devices',
                    'x264 ABR-VBV live streaming',
                    'x265 ABR-VBV live streaming')


class AV_Conv(wx.Panel):
    """
    Interface panel for video conversions
    """
    def __init__(self, parent, OS, iconplay, iconreset, iconresize,
                 iconcrop, iconrotate, icondeinterlace, icondenoiser,
                 iconanalyzes, iconsettings, iconpeaklevel, iconatrack,
                 btn_color, fontBtncolor,):
        # set attributes:
        self.parent = parent
        self.normdetails = []
        self.oS = OS
        self.btn_color = btn_color
        self.fBtnC = fontBtncolor

        wx.Panel.__init__(self, parent, -1)
        # ------------ base
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        self.notebook = wx.Notebook(self, wx.ID_ANY,
                                    style=wx.NB_NOPAGETHEME |
                                    wx.NB_BOTTOM
                                    )
        sizer_base.Add(self.notebook, 1, wx.ALL | wx.EXPAND, 5)
        # -------------- notebook panel 1:
        self.nb_Video = wx.Panel(self.notebook, wx.ID_ANY)
        sizer_nbVideo = wx.BoxSizer(wx.HORIZONTAL)
        # box Sx
        self.codVpanel = wx.Panel(self.nb_Video, wx.ID_ANY,
                                  style=wx.TAB_TRAVERSAL
                                  )
        sizer_nbVideo.Add(self.codVpanel, 1, wx.ALL | wx.EXPAND, 10)
        grid_sx_Vcod = wx.FlexGridSizer(11, 2, 0, 0)
        self.box_Vcod = wx.StaticBoxSizer(wx.StaticBox(self.codVpanel,
                                          wx.ID_ANY, _("Video Encoder")),
                                          wx.VERTICAL
                                          )
        self.box_Vcod.Add(grid_sx_Vcod, 0, wx.ALL |
                          wx.ALIGN_CENTER_HORIZONTAL |
                          wx.ALIGN_CENTER_VERTICAL, 5
                          )
        txtVcod = wx.StaticText(self.codVpanel, wx.ID_ANY, _('Codec'))
        grid_sx_Vcod.Add(txtVcod, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_Vcod = wx.ComboBox(self.codVpanel, wx.ID_ANY,
                                    choices=[x for x in VCODECS.keys()],
                                    size=(160, -1), style=wx.CB_DROPDOWN |
                                    wx.CB_READONLY
                                    )
        grid_sx_Vcod.Add(self.cmb_Vcod, 0, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        txtpass = wx.StaticText(self.codVpanel, wx.ID_ANY, _('Pass'))
        grid_sx_Vcod.Add(txtpass, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.ckbx_pass = wx.CheckBox(self.codVpanel, wx.ID_ANY,
                                     _("2-pass encoding")
                                     )
        grid_sx_Vcod.Add(self.ckbx_pass, 0, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        txtCRF = wx.StaticText(self.codVpanel, wx.ID_ANY, _('CRF'))
        grid_sx_Vcod.Add(txtCRF, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.slider_CRF = wx.Slider(self.codVpanel, wx.ID_ANY, 1, -1, 51,
                                    size=(160, -1), style=wx.SL_HORIZONTAL |
                                    wx.SL_AUTOTICKS | wx.SL_LABELS
                                    )
        grid_sx_Vcod.Add(self.slider_CRF, 0, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        txtVbrate = wx.StaticText(self.codVpanel, wx.ID_ANY,
                                  _('Bit Rate (kb)')
                                  )
        grid_sx_Vcod.Add(txtVbrate, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.spin_Vbrate = wx.SpinCtrl(self.codVpanel, wx.ID_ANY,
                                       "-1", min=-1, max=204800,
                                       style=wx.TE_PROCESS_ENTER
                                       )
        grid_sx_Vcod.Add(self.spin_Vbrate, 0, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        txtMinr = wx.StaticText(self.codVpanel, wx.ID_ANY, _('Min Rate (kb)'))
        grid_sx_Vcod.Add(txtMinr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.spinMinr = wx.SpinCtrl(self.codVpanel, wx.ID_ANY,
                                    "0", min=0, max=900000,
                                    style=wx.TE_PROCESS_ENTER
                                    )
        grid_sx_Vcod.Add(self.spinMinr, 0, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        txtMaxr = wx.StaticText(self.codVpanel, wx.ID_ANY, _('Max Rate (kb)'))
        grid_sx_Vcod.Add(txtMaxr, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spinMaxr = wx.SpinCtrl(self.codVpanel, wx.ID_ANY,
                                    "0", min=0, max=900000,
                                    style=wx.TE_PROCESS_ENTER
                                    )
        grid_sx_Vcod.Add(self.spinMaxr, 0, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        txtBuffer = wx.StaticText(self.codVpanel, wx.ID_ANY,
                                  _('Buffer Size (kb)')
                                  )
        grid_sx_Vcod.Add(txtBuffer, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.spinBufsize = wx.SpinCtrl(self.codVpanel, wx.ID_ANY,
                                       "0", min=0, max=900000,
                                       style=wx.TE_PROCESS_ENTER
                                       )
        grid_sx_Vcod.Add(self.spinBufsize, 0, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        txtVaspect = wx.StaticText(self.codVpanel, wx.ID_ANY,
                                   _('Aspect Ratio')
                                   )
        grid_sx_Vcod.Add(txtVaspect, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_Vaspect = wx.ComboBox(self.codVpanel, wx.ID_ANY,
                                       choices=[("Auto"),
                                                ("4:3"),
                                                ("16:9"),
                                                ("1.3333"),
                                                ("1.7777")],
                                       size=(160, -1), style=wx.CB_DROPDOWN |
                                       wx.CB_READONLY
                                       )
        grid_sx_Vcod.Add(self.cmb_Vaspect, 0, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        txtFps = wx.StaticText(self.codVpanel, wx.ID_ANY, ('FPS'))
        grid_sx_Vcod.Add(txtFps, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_Fps = wx.ComboBox(self.codVpanel, wx.ID_ANY,
                                   choices=[("Auto"),
                                            ("ntsc"),
                                            ("pal"),
                                            ("film"),
                                            ("23.976"),
                                            ("24"),
                                            ("25"),
                                            ("29.97"),
                                            ("30"),
                                            ("48"),
                                            ("50"),
                                            ("59.94"),
                                            ("60")
                                            ],
                                   size=(160, -1),
                                   style=wx.CB_DROPDOWN | wx.CB_READONLY
                                   )
        grid_sx_Vcod.Add(self.cmb_Fps, 0, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        txtPixfrm = wx.StaticText(self.codVpanel, wx.ID_ANY, _('Pixel Format'))
        grid_sx_Vcod.Add(txtPixfrm, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_Pixfrm = wx.ComboBox(self.codVpanel, wx.ID_ANY,
                                      choices=['None', 'yuv420p', 'yuv444p'],
                                      size=(160, -1), style=wx.CB_DROPDOWN |
                                      wx.CB_READONLY
                                      )
        grid_sx_Vcod.Add(self.cmb_Pixfrm, 0, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        txtSubmap = wx.StaticText(self.codVpanel, wx.ID_ANY,
                                  _('Subtitle Stream')
                                  )
        grid_sx_Vcod.Add(txtSubmap, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_Submap = wx.ComboBox(self.codVpanel, wx.ID_ANY,
                                      choices=['None', 'All'],
                                      size=(160, -1), style=wx.CB_DROPDOWN |
                                      wx.CB_READONLY
                                      )
        grid_sx_Vcod.Add(self.cmb_Submap, 0, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        self.codVpanel.SetSizer(self.box_Vcod)  # set panel
        # central box
        self.box_opt = wx.StaticBoxSizer(wx.StaticBox(self.nb_Video,
                                         wx.ID_ANY, _("Optimizations")),
                                         wx.VERTICAL
                                         )
        sizer_nbVideo.Add(self.box_opt, 1, wx.ALL | wx.EXPAND, 10)
        # panel vp8 vp9
        self.ckbx_web = wx.CheckBox(self.nb_Video,
                                    wx.ID_ANY, (_('Use for Web'))
                                    )
        self.box_opt.Add(self.ckbx_web, 0, wx.ALL |
                         wx.ALIGN_CENTER_HORIZONTAL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        self.vp9panel = wx.Panel(self.nb_Video, wx.ID_ANY,
                                 style=wx.TAB_TRAVERSAL
                                 )
        self.box_opt.Add(self.vp9panel, 0, wx.ALL |
                         wx.ALIGN_CENTER_HORIZONTAL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        sizer_vp9panel = wx.FlexGridSizer(6, 1, 5, 5)
        grid_vp9panelprst = wx.FlexGridSizer(1, 2, 0, 0)
        sizer_vp9panel.Add(grid_vp9panelprst, 0, wx.ALL |
                           wx.ALIGN_CENTER_HORIZONTAL, 5
                           )
        txtvp9prst = wx.StaticText(self.vp9panel, wx.ID_ANY, _('Optimize for'))
        grid_vp9panelprst.Add(txtvp9prst, 0, wx.ALL |
                              wx.ALIGN_CENTER_HORIZONTAL |
                              wx.ALIGN_CENTER_VERTICAL, 5
                              )
        self.cmb_vp9opti = wx.ComboBox(self.vp9panel, wx.ID_ANY,
                                       choices=OPTIMIZ_VP9,
                                       size=(180, -1), style=wx.CB_DROPDOWN |
                                       wx.CB_READONLY
                                       )
        grid_vp9panelprst.Add(self.cmb_vp9opti, 0, wx.ALL |
                              wx.ALIGN_CENTER_HORIZONTAL |
                              wx.ALIGN_CENTER_VERTICAL, 5
                              )
        line1 = wx.StaticLine(self.vp9panel, pos=(0, 0), size=(-1, -1))
        sizer_vp9panel.Add(line1, 0, wx.ALL | wx.EXPAND, 5)
        self.rdb_deadline = wx.RadioBox(self.vp9panel, wx.ID_ANY,
                                        (_("Deadline/Quality")),
                                        choices=[("best"), ("good"),
                                                 ("realtime")],
                                        majorDimension=0,
                                        style=wx.RA_SPECIFY_ROWS
                                        )
        sizer_vp9panel.Add(self.rdb_deadline, 0, wx.ALL |
                           wx.ALIGN_CENTER_HORIZONTAL, 5
                           )
        lab_cpu = wx.StaticText(self.vp9panel, wx.ID_ANY, (
                                        _("Quality/Speed ratio modifier:")))
        sizer_vp9panel.Add(lab_cpu, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.spin_cpu = wx.SpinCtrl(self.vp9panel, wx.ID_ANY, "0", min=-16,
                                    max=16, size=(-1, -1),
                                    style=wx.TE_PROCESS_ENTER
                                    )
        sizer_vp9panel.Add(self.spin_cpu, 0, wx.ALL |
                           wx.ALIGN_CENTER_HORIZONTAL, 5
                           )
        self.ckbx_rowMt1 = wx.CheckBox(self.vp9panel,
                                       wx.ID_ANY,
                                       (_('Activates row-mt 1'))
                                       )
        sizer_vp9panel.Add(self.ckbx_rowMt1, 0, wx.ALL |
                           wx.ALIGN_CENTER_HORIZONTAL, 5
                           )
        self.vp9panel.SetSizer(sizer_vp9panel)  # set panel
        # panel x/h 264 265
        self.h264panel = wx.Panel(self.nb_Video, wx.ID_ANY,
                                  style=wx.TAB_TRAVERSAL)
        self.box_opt.Add(self.h264panel, 0, wx.ALL |
                         wx.ALIGN_CENTER_HORIZONTAL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        sizer_h264panel = wx.BoxSizer(wx.VERTICAL)

        grid_h264panelprst = wx.FlexGridSizer(1, 2, 0, 0)
        sizer_h264panel.Add(grid_h264panelprst, 0, wx.ALL |
                            wx.ALIGN_CENTER_HORIZONTAL, 5
                            )
        txt264prst = wx.StaticText(self.h264panel, wx.ID_ANY,
                                   _('Optimize for')
                                   )
        grid_h264panelprst.Add(txt264prst, 0, wx.ALL |
                               wx.ALIGN_CENTER_HORIZONTAL |
                               wx.ALIGN_CENTER_VERTICAL, 5
                               )
        self.cmb_x26opti = wx.ComboBox(self.h264panel, wx.ID_ANY,
                                       choices=OPTIMIZ_HEVC_AVC,
                                       size=(180, -1), style=wx.CB_DROPDOWN |
                                       wx.CB_READONLY
                                       )
        grid_h264panelprst.Add(self.cmb_x26opti, 0, wx.ALL |
                               wx.ALIGN_CENTER_HORIZONTAL |
                               wx.ALIGN_CENTER_VERTICAL, 5
                               )
        line2 = wx.StaticLine(self.h264panel, pos=(0, 0), size=(-1, -1))
        sizer_h264panel.Add(line2, 0, wx.ALL | wx.EXPAND, 10)
        grid_h264panel = wx.FlexGridSizer(4, 2, 0, 0)
        sizer_h264panel.Add(grid_h264panel, 0, wx.ALL |
                            wx.ALIGN_CENTER_HORIZONTAL, 5
                            )
        txtpresets = wx.StaticText(self.h264panel, wx.ID_ANY, _('Preset'))
        grid_h264panel.Add(txtpresets, 0, wx.ALL |
                           wx.ALIGN_CENTER_HORIZONTAL |
                           wx.ALIGN_CENTER_VERTICAL, 5
                           )
        self.cmb_preset = wx.ComboBox(self.h264panel, wx.ID_ANY,
                                      choices=[p for p in X264_OPT["Presets"]],
                                      size=(120, -1), style=wx.CB_DROPDOWN |
                                      wx.CB_READONLY
                                      )
        grid_h264panel.Add(self.cmb_preset, 0, wx.ALL |
                           wx.ALIGN_CENTER_HORIZONTAL |
                           wx.ALIGN_CENTER_VERTICAL, 5)
        txtprofile = wx.StaticText(self.h264panel, wx.ID_ANY, _('Profile'))
        grid_h264panel.Add(txtprofile, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_profile = wx.ComboBox(self.h264panel, wx.ID_ANY,
                                       choices=[p for p in
                                                X264_OPT["Profiles"]],
                                       size=(120, -1), style=wx.CB_DROPDOWN |
                                       wx.CB_READONLY
                                       )
        grid_h264panel.Add(self.cmb_profile, 0, wx.ALL |
                           wx.ALIGN_CENTER_VERTICAL, 5
                           )
        txtlevel = wx.StaticText(self.h264panel, wx.ID_ANY, _('Level'))
        grid_h264panel.Add(txtlevel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_level = wx.ComboBox(self.h264panel, wx.ID_ANY,
                                     choices=LEVELS, size=(80, -1),
                                     style=wx.CB_DROPDOWN | wx.CB_READONLY
                                     )
        grid_h264panel.Add(self.cmb_level, 0, wx.ALL |
                           wx.ALIGN_CENTER_VERTICAL, 5
                           )
        txttune = wx.StaticText(self.h264panel, wx.ID_ANY, _('Tune'))
        grid_h264panel.Add(txttune, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_tune = wx.ComboBox(self.h264panel, wx.ID_ANY,
                                    choices=[p for p in X264_OPT["Tunes"]],
                                    size=(120, -1), style=wx.CB_DROPDOWN |
                                    wx.CB_READONLY)
        grid_h264panel.Add(self.cmb_tune, 0, wx.ALL |
                           wx.ALIGN_CENTER_VERTICAL, 5
                           )
        self.h264panel.SetSizer(sizer_h264panel)  # set panel
        sizer_dx_format = wx.BoxSizer(wx.HORIZONTAL)
        sizer_nbVideo.Add(sizer_dx_format, 1, wx.ALL | wx.EXPAND, 5)
        self.box_format = wx.StaticBoxSizer(wx.StaticBox(self.nb_Video,
                                            wx.ID_ANY, _("Format")),
                                            wx.VERTICAL
                                            )
        sizer_dx_format.Add(self.box_format, 1, wx.ALL | wx.EXPAND, 5)
        grid_dx_frmt = wx.FlexGridSizer(4, 2, 0, 0)
        self.box_format.Add(grid_dx_frmt, 1, wx.ALL |
                            wx.ALIGN_CENTER_HORIZONTAL |
                            wx.ALIGN_CENTER_VERTICAL, 5
                            )
        txtMedia = wx.StaticText(self.nb_Video, wx.ID_ANY, _('Media'))
        grid_dx_frmt.Add(txtMedia, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_Media = wx.ComboBox(self.nb_Video, wx.ID_ANY,
                                     choices=['Video', 'Audio'],
                                     size=(160, -1), style=wx.CB_DROPDOWN |
                                     wx.CB_READONLY
                                     )
        grid_dx_frmt.Add(self.cmb_Media, 0, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        txtFormat = wx.StaticText(self.nb_Video, wx.ID_ANY, _('Container'))
        grid_dx_frmt.Add(txtFormat, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_Vcont = wx.ComboBox(self.nb_Video, wx.ID_ANY,
                                     choices=[f for f in
                                              VCODECS.get('x264').values()][0],
                                     size=(160, -1), style=wx.CB_DROPDOWN |
                                     wx.CB_READONLY
                                     )
        grid_dx_frmt.Add(self.cmb_Vcont, 0, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        self.nb_Video.SetSizer(sizer_nbVideo)
        self.notebook.AddPage(self.nb_Video, _("AV Media"))
        # -------------- notebook panel 2:
        self.nb_Audio = wx.Panel(self.notebook, wx.ID_ANY)
        sizer_nbAudio = wx.BoxSizer(wx.VERTICAL)
        self.rdb_a = wx.RadioBox(self.nb_Audio, wx.ID_ANY, (
                                 _("Audio Encoder")),
                                 choices=[x for x in ACODECS.keys()],
                                 majorDimension=5, style=wx.RA_SPECIFY_COLS
                                 )
        for n, v in enumerate(AV_FORMATS["mkv"]):
            if not v:  # disable only not compatible with mkv
                self.rdb_a.EnableItem(n, enable=False)
        sizer_nbAudio.Add(self.rdb_a, 1, wx.ALL | wx.EXPAND, 10)
        self.box_audioProper = wx.StaticBoxSizer(wx.StaticBox(
                                                 self.nb_Audio, wx.ID_ANY,
                                                 _("Audio Properties")),
                                                 wx.VERTICAL
                                                 )
        sizer_nbAudio.Add(self.box_audioProper, 1, wx.ALL | wx.EXPAND, 10)
        grid_a_ctrl = wx.BoxSizer(wx.HORIZONTAL)
        self.box_audioProper.Add(grid_a_ctrl, 0, wx.ALL | wx.EXPAND, 15)
        setbmp = wx.Bitmap(iconsettings, wx.BITMAP_TYPE_ANY)
        self.btn_aparam = GB.GradientButton(self.nb_Audio,
                                            size=(-1, 25),
                                            bitmap=setbmp,
                                            label=_("Settings"))
        self.btn_aparam.SetBaseColours(startcolour=wx.Colour(AZURE_NEON),
                                       foregroundcolour=wx.Colour(GREY_DISABLED
                                                                  ))
        self.btn_aparam.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_aparam.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_aparam.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_aparam.SetTopEndColour(wx.Colour(self.btn_color))
        grid_a_ctrl.Add(self.btn_aparam, 0, wx.ALL |
                        wx.ALIGN_CENTER_VERTICAL, 5
                        )
        self.txt_audio_options = wx.TextCtrl(self.nb_Audio, wx.ID_ANY,
                                             size=(-1, -1),
                                             style=wx.TE_READONLY
                                             )
        grid_a_ctrl.Add(self.txt_audio_options, 1, wx.ALL | wx.EXPAND, 5)
        self.box_audioMap = wx.StaticBoxSizer(wx.StaticBox(self.nb_Audio,
                                              wx.ID_ANY,
                                              _("Audio Streams Mapping")),
                                              wx.VERTICAL
                                              )
        sizer_nbAudio.Add(self.box_audioMap, 1, wx.ALL | wx.EXPAND, 10)
        grid_Amap = wx.FlexGridSizer(2, 2, 0, 0)
        self.box_audioMap.Add(grid_Amap, 0, wx.ALL | wx.EXPAND, 15)
        txtAinmap = wx.StaticText(self.nb_Audio, wx.ID_ANY,
                                  _('Input Audio Index')
                                  )
        grid_Amap.Add(txtAinmap, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_A_inMap = wx.ComboBox(self.nb_Audio, wx.ID_ANY,
                                       choices=['Auto', '1', '2', '3',
                                                '4', '5', '6', '7', '8'],
                                       size=(160, -1), style=wx.CB_DROPDOWN |
                                       wx.CB_READONLY
                                       )
        grid_Amap.Add(self.cmb_A_inMap, 0, wx.ALL |
                      wx.ALIGN_CENTER_VERTICAL, 5
                      )
        txtAoutmap = wx.StaticText(self.nb_Audio, wx.ID_ANY,
                                   _('Output Audio Index')
                                   )
        grid_Amap.Add(txtAoutmap, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_A_outMap = wx.ComboBox(self.nb_Audio, wx.ID_ANY,
                                        choices=['Auto', 'All', '1', '2', '3',
                                                 '4', '5', '6', '7', '8'],
                                        size=(160, -1), style=wx.CB_DROPDOWN |
                                        wx.CB_READONLY
                                        )
        grid_Amap.Add(self.cmb_A_outMap, 0, wx.ALL |
                      wx.ALIGN_CENTER_VERTICAL, 5
                      )
        self.nb_Audio.SetSizer(sizer_nbAudio)
        self.notebook.AddPage(self.nb_Audio, _("Audio"))
        # -------------- notebook panel 3:
        self.nb_filters = wx.Panel(self.notebook, wx.ID_ANY)
        sizer_nbFilters = wx.BoxSizer(wx.VERTICAL)
        # box video Filters
        self.box_vFilters = wx.StaticBoxSizer(wx.StaticBox(self.nb_filters,
                                              wx.ID_ANY,  _("Video Filters")),
                                              wx.VERTICAL
                                              )
        sizer_nbFilters.Add(self.box_vFilters, 1, wx.ALL | wx.EXPAND, 10)
        self.filterVpanel = wx.Panel(self.nb_filters, wx.ID_ANY,
                                     style=wx.TAB_TRAVERSAL
                                     )
        self.box_vFilters.Add(self.filterVpanel, 0, wx.ALL |
                              wx.ALIGN_CENTER_HORIZONTAL |
                              wx.ALIGN_CENTER_VERTICAL, 5
                              )
        grid_vfilters = wx.FlexGridSizer(3, 5, 20, 20)
        resizebmp = wx.Bitmap(iconresize, wx.BITMAP_TYPE_ANY)
        self.btn_videosize = GB.GradientButton(self.filterVpanel,
                                               size=(-1, 25),
                                               bitmap=resizebmp,
                                               label=_("Resize"))
        self.btn_videosize.SetBaseColours(startcolour=wx.Colour(AZURE_NEON),
                                          foregroundcolour=wx.Colour(
                                              self.fBtnC
                                              ))
        self.btn_videosize.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_videosize.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_videosize.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_videosize.SetTopEndColour(wx.Colour(self.btn_color))
        grid_vfilters.Add(self.btn_videosize)
        cropbmp = wx.Bitmap(iconcrop, wx.BITMAP_TYPE_ANY)
        self.btn_crop = GB.GradientButton(self.filterVpanel,
                                          size=(-1, 25),
                                          bitmap=cropbmp,
                                          label=_("Crop Dimension"))
        self.btn_crop.SetBaseColours(startcolour=wx.Colour(AZURE_NEON),
                                     foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_crop.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_crop.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_crop.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_crop.SetTopEndColour(wx.Colour(self.btn_color))
        grid_vfilters.Add(self.btn_crop)
        rotatebmp = wx.Bitmap(iconrotate, wx.BITMAP_TYPE_ANY)
        self.btn_rotate = GB.GradientButton(self.filterVpanel,
                                            size=(-1, 25),
                                            bitmap=rotatebmp,
                                            label=_("Rotation"))
        self.btn_rotate.SetBaseColours(startcolour=wx.Colour(AZURE_NEON),
                                       foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_rotate.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_rotate.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_rotate.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_rotate.SetTopEndColour(wx.Colour(self.btn_color))
        grid_vfilters.Add(self.btn_rotate)
        deintbmp = wx.Bitmap(icondeinterlace, wx.BITMAP_TYPE_ANY)
        self.btn_lacing = GB.GradientButton(self.filterVpanel,
                                            size=(-1, 25),
                                            bitmap=deintbmp,
                                            label=_("De/Interlace")
                                            )
        self.btn_lacing.SetBaseColours(startcolour=wx.Colour(AZURE_NEON),
                                       foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_lacing.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_lacing.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_lacing.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_lacing.SetTopEndColour(wx.Colour(self.btn_color))
        grid_vfilters.Add(self.btn_lacing)
        denoiserbmp = wx.Bitmap(icondenoiser, wx.BITMAP_TYPE_ANY)
        self.btn_denois = GB.GradientButton(self.filterVpanel,
                                            size=(-1, 25),
                                            bitmap=denoiserbmp,
                                            label="Denoisers")
        self.btn_denois.SetBaseColours(startcolour=wx.Colour(AZURE_NEON),
                                       foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_denois.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_denois.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_denois.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_denois.SetTopEndColour(wx.Colour(self.btn_color))
        grid_vfilters.Add(self.btn_denois)

        playbmp = wx.Bitmap(iconplay, wx.BITMAP_TYPE_ANY)
        self.btn_preview = GB.GradientButton(self.filterVpanel,
                                             size=(-1, 25),
                                             bitmap=playbmp,
                                             )
        self.btn_preview.SetBaseColours(startcolour=wx.Colour(AZURE_NEON))
        self.btn_preview.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_preview.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_preview.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_preview.SetTopEndColour(wx.Colour(self.btn_color))
        grid_vfilters.Add(self.btn_preview)
        resetbmp = wx.Bitmap(iconreset, wx.BITMAP_TYPE_ANY)
        self.btn_reset = GB.GradientButton(self.filterVpanel,
                                           size=(-1, 25),
                                           bitmap=resetbmp,
                                           )
        self.btn_reset.SetBaseColours(startcolour=wx.Colour(AZURE_NEON))
        self.btn_reset.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_reset.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_reset.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_reset.SetTopEndColour(wx.Colour(self.btn_color))
        grid_vfilters.Add(self.btn_reset)
        self.filterVpanel.SetSizer(grid_vfilters)  # set panel
        self.box_aFilters = wx.StaticBoxSizer(wx.StaticBox(self.nb_filters,
                                              wx.ID_ANY, _("Audio Filters")),
                                              wx.VERTICAL
                                              )
        sizer_nbFilters.Add(self.box_aFilters, 1, wx.ALL | wx.EXPAND, 10)
        sizer_Anormalization = wx.BoxSizer(wx.VERTICAL)
        self.box_aFilters.Add(sizer_Anormalization, 0, wx.ALL | wx.EXPAND, 0)
        self.rdbx_normalize = wx.RadioBox(self.nb_filters, wx.ID_ANY,
                                          (_("Audio Normalization")),
                                          choices=[('Off'),
                                                   ('PEAK'),
                                                   ('RMS'),
                                                   ('EBU R128'),
                                                   ],
                                          majorDimension=1,
                                          style=wx.RA_SPECIFY_ROWS,
                                          )
        sizer_Anormalization.Add(self.rdbx_normalize, 0, wx.ALL |
                                 wx.EXPAND, 20
                                 )
        self.peakpanel = wx.Panel(self.nb_filters, wx.ID_ANY,
                                  style=wx.TAB_TRAVERSAL
                                  )
        sizer_peak = wx.FlexGridSizer(1, 4, 15, 15)
        sizer_Anormalization.Add(self.peakpanel, 0, wx.ALL | wx.EXPAND, 20)
        analyzebmp = wx.Bitmap(iconanalyzes, wx.BITMAP_TYPE_ANY)
        self.btn_voldect = GB.GradientButton(self.peakpanel,
                                             size=(-1, 25),
                                             bitmap=analyzebmp,
                                             label=_("Volumedetect")
                                             )
        self.btn_voldect.SetBaseColours(startcolour=wx.Colour(AZURE_NEON),
                                        foregroundcolour=wx.Colour(GREY_DARK))
        self.btn_voldect.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_voldect.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_voldect.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_voldect.SetTopEndColour(wx.Colour(self.btn_color))
        sizer_peak.Add(self.btn_voldect, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        peaklevelbmp = wx.Bitmap(iconpeaklevel, wx.BITMAP_TYPE_ANY)
        self.btn_details = GB.GradientButton(self.peakpanel,
                                             size=(-1, 25),
                                             bitmap=peaklevelbmp,
                                             label=_("Volume Statistics")
                                             )
        self.btn_details.SetBaseColours(startcolour=wx.Colour(AZURE_NEON),
                                        foregroundcolour=wx.Colour(GREY_DARK))
        self.btn_details.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_details.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_details.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_details.SetTopEndColour(wx.Colour(self.btn_color))
        sizer_peak.Add(self.btn_details, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.lab_amplitude = wx.StaticText(self.peakpanel, wx.ID_ANY,
                                           (_("Target level:"))
                                           )
        sizer_peak.Add(self.lab_amplitude, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.spin_target = FS.FloatSpin(self.peakpanel, wx.ID_ANY,
                                        min_val=-99.0,
                                        max_val=0.0,
                                        increment=0.5, value=-1.0,
                                        agwStyle=FS.FS_LEFT, size=(-1, -1)
                                        )
        self.spin_target.SetFormat("%f"), self.spin_target.SetDigits(1)
        sizer_peak.Add(self.spin_target, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.peakpanel.SetSizer(sizer_peak)  # set panel
        sizer_nbAudio.Add(self.peakpanel, 0, wx.ALL, 20)
        self.ebupanel = wx.Panel(self.nb_filters,
                                 wx.ID_ANY, style=wx.TAB_TRAVERSAL
                                 )
        sizer_ebu = wx.FlexGridSizer(3, 2, 5, 5)
        sizer_Anormalization.Add(self.ebupanel, 0, wx.ALL | wx.EXPAND, 20)
        self.lab_i = wx.StaticText(self.ebupanel, wx.ID_ANY, (
                             _("Set integrated loudness target:  ")))
        sizer_ebu.Add(self.lab_i, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.spin_i = FS.FloatSpin(self.ebupanel, wx.ID_ANY,
                                   min_val=-70.0, max_val=-5.0,
                                   increment=0.5, value=-24.0,
                                   agwStyle=FS.FS_LEFT, size=(-1, -1)
                                   )
        self.spin_i.SetFormat("%f"), self.spin_i.SetDigits(1)
        sizer_ebu.Add(self.spin_i, 0, wx.ALL, 0)

        self.lab_tp = wx.StaticText(self.ebupanel, wx.ID_ANY, (
                                    _("Set maximum true peak:")))
        sizer_ebu.Add(self.lab_tp, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.spin_tp = FS.FloatSpin(self.ebupanel, wx.ID_ANY,
                                    min_val=-9.0, max_val=0.0,
                                    increment=0.5, value=-2.0,
                                    agwStyle=FS.FS_LEFT, size=(-1, -1)
                                    )
        self.spin_tp.SetFormat("%f"), self.spin_tp.SetDigits(1)
        sizer_ebu.Add(self.spin_tp, 0, wx.ALL, 0)

        self.lab_lra = wx.StaticText(self.ebupanel, wx.ID_ANY, (
                                     _("Set loudness range target:")))
        sizer_ebu.Add(self.lab_lra, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.spin_lra = FS.FloatSpin(self.ebupanel, wx.ID_ANY,
                                     min_val=1.0, max_val=20.0,
                                     increment=0.5, value=7.0,
                                     agwStyle=FS.FS_LEFT, size=(-1, -1)
                                     )
        self.spin_lra.SetFormat("%f"), self.spin_lra.SetDigits(1)
        sizer_ebu.Add(self.spin_lra, 0, wx.ALL, 0)
        self.ebupanel.SetSizer(sizer_ebu)  # set panel
        sizer_nbAudio.Add(self.ebupanel, 0, wx.ALL, 20)
        self.nb_filters.SetSizer(sizer_nbFilters)
        self.notebook.AddPage(self.nb_filters, _("Filters"))
        # -------------- notebook panel 4:
        # self.nb_Subt = wx.Panel(self.notebook, wx.ID_ANY)
        # sizer_nbSubt = wx.BoxSizer(wx.VERTICAL)

        # self.nb_Subt.SetSizer(sizer_nbSubt)
        # self.notebook.AddPage(self.nb_Subt, _("Subtitles"))
        # ------------------ set layout
        self.SetSizer(sizer_base)
        self.Layout()
        # ---------------------- Tooltip
        tip = (_('Available video codecs. "Copy" is not a codec but indicate '
                 'that the video stream is not to be re-encoded and allows '
                 'changing the format or other parameters'))
        self.cmb_Vcod.SetToolTip(tip)
        tip = (_('Output format and file extension. the '
                 'content may change based on the codec and media'))
        self.cmb_Vcont.SetToolTip(tip)
        tip = (_('"Video" to save the output file as a '
                 'video; "Audio" to save as an audio track'))
        self.cmb_Media.SetToolTip(tip)
        tip = (_('It can reduce the file size, but takes longer.'))
        self.ckbx_pass.SetToolTip(tip)
        tip = (_('Specifies a minimum tolerance to be used'))
        self.spinMinr.SetToolTip(tip)
        tip = (_('Specifies a maximum tolerance. this is '
                 'only used in conjunction with buffer size'))
        self.spinMaxr.SetToolTip(tip)
        tip = (_('Specifies the decoder buffer size, which determines the '
                 'variability of the output bitrate '))
        self.spinBufsize.SetToolTip(tip)
        tip = (_('"good" is the default and recommended for most '
                 'applications; "best" is recommended if you have lots of '
                 'time and want the best compression efficiency; "realtime" '
                 'is recommended for live/fast encoding'))
        self.rdb_deadline.SetToolTip(tip)
        tip = (_('"cpu-used" sets how efficient the compression will be. '
                 'The meaning depends on the mode above.'))
        self.spin_cpu.SetToolTip(tip)
        tip = (_('specifies the target (average) bit rate for the encoder '
                 'to use. Higher value = higher quality. Set -1 to disable '
                 'this control.'))
        self.spin_Vbrate.SetToolTip(tip)
        tip = (_('Constant rate factor. Lower values = higher quality and '
                 'a larger file size. Set -1 to disable this control.'))
        self.slider_CRF.SetToolTip(tip)
        tip = (_('Try filters by playing a preview'))
        self.btn_preview.SetToolTip(tip)
        tip = (_("Clear all enabled filters "))
        self.btn_reset.SetToolTip(tip)
        tip = (_('Video width and video height ratio.'))
        self.cmb_Vaspect.SetToolTip(tip)
        tip = (_('Frames repeat a given number of times per second. In some '
                 'countries are 30 NTSC, in PAL countries like Italy are 25.'))
        self.cmb_Fps.SetToolTip(tip)
        tip = (_('Gets maximum volume and average volume data in dBFS, then '
                 'calculates the offset amount for audio normalization.'))
        self.btn_voldect.SetToolTip(tip)
        tip = (_('Limiter for the maximum peak level or the mean level '
                 '(when switch to RMS) in dBFS. From -99.0 to +0.0; default '
                 'for PEAK level is -1.0; default for RMS is -20.0'))
        self.spin_target.SetToolTip(tip)
        tip = (_('Choose from video a specific input '
                 'audio stream to work out.'))
        self.cmb_A_inMap.SetToolTip(tip)
        tip = (_('Map on the output index. Keep same input map if saving '
                 'as video; to save as audio select to "all" or "Auto"'))
        self.cmb_A_outMap.SetToolTip(tip)
        tip = (_('Integrated Loudness Target in LUFS. '
                 'From -70.0 to -5.0, default is -24.0'))
        self.spin_i.SetToolTip(tip)
        tip = (_('Maximum True Peak in dBTP. From -9.0 '
                 'to +0.0, default is -2.0'))
        self.spin_tp.SetToolTip(tip)
        tip = (_('Loudness Range Target in LUFS. '
                 'From +1.0 to +20.0, default is +7.0'))
        self.spin_lra.SetToolTip(tip)

        # ----------------------Binding (EVT)----------------------#
        """
        Note: wx.EVT_TEXT_ENTER é diverso da wx.EVT_TEXT . Il primo é sensibile
        agli input di tastiera, il secondo é sensibile agli input di tastiera
        ma anche agli "append"
        """
        self.Bind(wx.EVT_COMBOBOX, self.videoCodec, self.cmb_Vcod)
        self.Bind(wx.EVT_COMBOBOX, self.on_Container, self.cmb_Vcont)
        self.Bind(wx.EVT_COMBOBOX, self.on_Media, self.cmb_Media)
        self.Bind(wx.EVT_RADIOBOX, self.on_Deadline, self.rdb_deadline)
        self.Bind(wx.EVT_CHECKBOX, self.on_Pass, self.ckbx_pass)
        self.Bind(wx.EVT_CHECKBOX, self.on_WebOptimize, self.ckbx_web)
        self.Bind(wx.EVT_SPINCTRL, self.on_Vbitrate, self.spin_Vbrate)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.on_Crf, self.slider_CRF)
        self.Bind(wx.EVT_BUTTON, self.on_Enable_vsize, self.btn_videosize)
        self.Bind(wx.EVT_BUTTON, self.on_Enable_crop, self.btn_crop)
        self.Bind(wx.EVT_BUTTON, self.on_Enable_rotate, self.btn_rotate)
        self.Bind(wx.EVT_BUTTON, self.on_Enable_lacing, self.btn_lacing)
        self.Bind(wx.EVT_BUTTON, self.on_Enable_denoiser, self.btn_denois)
        self.Bind(wx.EVT_BUTTON, self.on_FiltersPreview, self.btn_preview)
        self.Bind(wx.EVT_BUTTON, self.on_FiltersClear, self.btn_reset)
        self.Bind(wx.EVT_COMBOBOX, self.on_Vaspect, self.cmb_Vaspect)
        self.Bind(wx.EVT_COMBOBOX, self.on_Vrate, self.cmb_Fps)
        self.Bind(wx.EVT_RADIOBOX, self.on_AudioCodecs, self.rdb_a)
        self.Bind(wx.EVT_BUTTON, self.on_AudioParam, self.btn_aparam)
        self.Bind(wx.EVT_COMBOBOX, self.on_audioINstream, self.cmb_A_inMap)
        self.Bind(wx.EVT_COMBOBOX, self.on_audioOUTstream, self.cmb_A_outMap)
        self.Bind(wx.EVT_RADIOBOX, self.onNormalize, self.rdbx_normalize)
        self.Bind(wx.EVT_SPINCTRL, self.on_enter_Ampl, self.spin_target)
        self.Bind(wx.EVT_BUTTON, self.on_Audio_analyzes, self.btn_voldect)
        self.Bind(wx.EVT_COMBOBOX, self.on_xOptimize, self.cmb_x26opti)
        self.Bind(wx.EVT_COMBOBOX, self.on_vpOptimize, self.cmb_vp9opti)
        self.Bind(wx.EVT_COMBOBOX, self.on_xPreset, self.cmb_preset)
        self.Bind(wx.EVT_COMBOBOX, self.on_xProfile, self.cmb_profile)
        self.Bind(wx.EVT_COMBOBOX, self.on_Level, self.cmb_level)
        self.Bind(wx.EVT_COMBOBOX, self.on_xTune, self.cmb_tune)
        self.Bind(wx.EVT_BUTTON, self.on_Show_normlist, self.btn_details)

        # -------------------------------------- initialize default layout:
        self.rdb_a.SetSelection(0), self.cmb_Vcod.SetSelection(1)
        self.cmb_Media.SetSelection(0), self.cmb_Vcont.SetSelection(0)
        self.cmb_Fps.SetSelection(0), self.cmb_Vaspect.SetSelection(0)
        self.cmb_Pixfrm.SetSelection(1), self.cmb_Submap.SetSelection(1)
        self.cmb_A_outMap.SetSelection(1), self.cmb_A_inMap.SetSelection(0)
        self.cmb_x26opti.SetSelection(0), self.cmb_vp9opti.SetSelection(0)
        self.UI_set()
        self.audio_default()
        self.normalize_default()

    # -------------------------------------------------------------------#
    def UI_set(self):
        """
        Update all the GUI widgets based on the choices made by the user.
        """
        if cmd_opt["VideoCodec"] in ["-c:v libx264", "-c:v libx265"]:
            self.vp9panel.Hide(), self.h264panel.Show()
            self.cmb_tune.Clear(), self.cmb_profile.Clear()
            if cmd_opt["VideoCodec"] == "-c:v libx264":
                self.slider_CRF.SetValue(23), self.spin_Vbrate.SetValue(1500)
                for tune in X264_OPT['Tunes']:
                    self.cmb_tune.Append((tune),)
                for prof in X264_OPT["Profiles"]:
                    self.cmb_profile.Append((prof),)
            elif cmd_opt["VideoCodec"] == "-c:v libx265":
                self.slider_CRF.SetValue(28), self.spin_Vbrate.SetValue(1500)
                for tune in X265_OPT["Tunes"]:
                    self.cmb_tune.Append((tune),)
                for prof in X265_OPT["Profiles"]:
                    self.cmb_profile.Append((prof),)
            self.filterVpanel.Show(), self.slider_CRF.SetMax(51)
            self.cmb_preset.SetSelection(0), self.cmb_profile.SetSelection(0)
            self.cmb_tune.SetSelection(0), self.cmb_level.SetSelection(0)

        elif cmd_opt["VideoCodec"] in ["-c:v libvpx", "-c:v libvpx-vp9",
                                       "-c:v libaom-av1 -strict -2"]:
            self.vp9panel.Show(), self.h264panel.Hide()
            self.ckbx_rowMt1.SetValue(True), self.rdb_deadline.SetSelection(1)
            self.spin_cpu.SetRange(0, 5), self.slider_CRF.SetMax(63)
            self.slider_CRF.SetValue(31), self.spin_Vbrate.SetValue(1500)
            self.filterVpanel.Show(), self.nb_Video.Layout()

        elif cmd_opt["VideoCodec"] == "-c:v copy":
            self.slider_CRF.SetValue(-1), self.spin_Vbrate.SetValue(-1)
            self.vp9panel.Hide(), self.h264panel.Hide()
            self.filterVpanel.Hide()

        else:  # all others containers that not use h264
            self.slider_CRF.SetValue(-1), self.spin_Vbrate.SetValue(1500)
            self.vp9panel.Hide(), self.h264panel.Hide()
            self.filterVpanel.Show()

        cmd_opt["Preset"], cmd_opt["Profile"], cmd_opt["Tune"] = '', '', ''

        if self.rdbx_normalize.GetSelection() == 3:
            self.ckbx_pass.SetValue(True)
            self.ckbx_pass.Disable()
        else:
            if cmd_opt["VideoCodec"] == "-c:v copy":
                self.ckbx_pass.SetValue(False)
                self.ckbx_pass.Disable()
            else:
                self.ckbx_pass.Enable()
        self.on_Pass(self)
    # -------------------------------------------------------------------#

    def audio_default(self):
        """
        Set default audio parameters. This method is called on first run and
        when change the video container selection
        """
        self.rdb_a.SetStringSelection("Auto")
        cmd_opt["AudioCodStr"] = "Auto"
        cmd_opt["AudioCodec"] = ["", ""]
        cmd_opt["AudioBitrate"] = ["", ""]
        cmd_opt["AudioChannel"] = ["", ""]
        cmd_opt["AudioRate"] = ["", ""]
        cmd_opt["AudioDepth"] = ["", ""]
        self.btn_aparam.Disable()
        self.btn_aparam.SetForegroundColour(wx.Colour(GREY_DISABLED))
        self.btn_aparam.SetBottomEndColour(wx.Colour(self.btn_color))
        self.txt_audio_options.Clear()
        # self.rdbx_normalize.Enable()
    # -------------------------------------------------------------------#

    def normalize_default(self, setoff=True):
        """
        Set default normalization parameters of the audio panel. This method
        is called by main_frame module on MainFrame.switch_video_conv()
        during first run and when there are changing on dragNdrop panel,
        (like make a clear file list or append new file, etc)
        """
        if setoff:
            self.rdbx_normalize.SetSelection(0)
        if not self.btn_voldect.IsEnabled():
            self.btn_voldect.Enable()
        self.spin_target.SetValue(-1.0)
        self.peakpanel.Hide(), self.ebupanel.Hide(), self.btn_details.Hide()
        self.btn_voldect.SetForegroundColour(wx.Colour(self.fBtnC))
        cmd_opt["PEAK"], cmd_opt["EBU"], cmd_opt["RMS"] = "", "", ""
        del self.normdetails[:]

    # ----------------------Event handler (callback)----------------------#

    def videoCodec(self, event):
        """
        The event chosen in the video format combobox triggers the
        setting to the default values. The selection of a new format
        determines the default status, enabling or disabling some
        functions depending on the type of video format chosen.
        """
        selected = VCODECS.get(self.cmb_Vcod.GetValue())
        libcodec = list(selected.keys())[0]
        self.cmb_Vcont.Clear()
        for f in selected.values():
            self.cmb_Vcont.Append((f),)
        self.cmb_Vcont.SetSelection(0)

        cmd_opt["VideoCodec"] = libcodec
        cmd_opt["VidCmbxStr"] = self.cmb_Vcod.GetValue()
        cmd_opt["OutputFormat"] = self.cmb_Vcont.GetValue()
        cmd_opt["VideoBitrate"] = ""
        cmd_opt["CRF"] = ""

        if self.cmb_Vcod.GetValue() == "Copy":
            self.spinMinr.Disable(), self.spinMaxr.Disable()
            self.spinBufsize.Disable()
            cmd_opt["Passing"] = "1 pass"
        else:
            self.spinMinr.Enable(), self.spinMaxr.Enable()
            self.spinBufsize.Enable()

        self.UI_set()
        self.audio_default()  # reset audio radiobox and dict
        self.setAudioRadiobox(self)
    # ------------------------------------------------------------------#

    def on_Media(self, event):
        """
        Combobox Media Sets layout to Audio or Video formats
        """
        if self.cmb_Media.GetValue() == 'Audio':
            self.cmb_Vcod.SetSelection(6)
            cmd_opt["VideoCodec"] = "-c:v copy"
            self.audio_default()
            self.codVpanel.Disable()
            self.cmb_Vcont.Clear()
            for f in A_FORMATS:
                self.cmb_Vcont.Append((f),)
            self.cmb_Vcont.SetSelection(0)
            self.UI_set()
            self.setAudioRadiobox(self)

        elif self.cmb_Media.GetValue() == 'Video':
            self.codVpanel.Enable()
            self.cmb_Vcod.SetSelection(1)
            self.videoCodec(self)

        cmd_opt["OutputFormat"] = self.cmb_Vcont.GetValue()
    # ------------------------------------------------------------------#

    def on_Container(self, event):
        """
        Appends on container combobox according to audio and video formats
        """
        if self.cmb_Vcont.GetValue() == "Copy":
            cmd_opt["OutputFormat"] = ''
        else:
            cmd_opt["OutputFormat"] = self.cmb_Vcont.GetValue()
        self.setAudioRadiobox(self)
    # ------------------------------------------------------------------#

    def on_WebOptimize(self, event):
        """
        Add movflags faststart to output media to maximize speed when
        playback
        """
        check = self.ckbx_web.IsChecked()
        cmd_opt["WebOptim"] = '-movflags faststart' if check else ''
    # ------------------------------------------------------------------#

    def on_xOptimize(self, event):
        """
        Sets widgets and parameters to a choosen presets for x264/x265
        encoders

        """
        name = self.cmb_x26opti.GetValue()
        data = optimizations.hevc_avc(name)
        eval(data)
    # -------------------------------------------------------------------#

    def on_vpOptimize(self, event):
        """
        Sets widgets and parameters to a choosen presets for vp8/vp9
        encoders

        """
        name = self.cmb_vp9opti.GetValue()
        data = optimizations.vp9(name)
        eval(data)
    # -------------------------------------------------------------------#

    def on_Pass(self, event):
        """
        enable or disable functionality for two pass encoding
        """
        if self.ckbx_pass.IsChecked():
            cmd_opt["Passing"] = "2 pass"
            if cmd_opt["VideoCodec"] in ["-c:v libvpx", "-c:v libvpx-vp9"]:
                self.slider_CRF.Enable()
                self.spin_Vbrate.Enable()

            elif cmd_opt["VideoCodec"] == "-c:v copy":
                self.slider_CRF.Disable()
                self.spin_Vbrate.Disable()
            else:
                self.slider_CRF.Disable()
                self.spin_Vbrate.Enable()
        else:
            cmd_opt["Passing"] = "1 pass"
            if cmd_opt["VideoCodec"] in ["-c:v libx264", "-c:v libx265"]:
                self.slider_CRF.Enable()
                self.spin_Vbrate.Disable()

            elif cmd_opt["VideoCodec"] in ["-c:v libvpx", "-c:v libvpx-vp9",
                                           "-c:v libaom-av1 -strict -2"]:
                self.slider_CRF.Enable()
                self.spin_Vbrate.Enable()

            elif cmd_opt["VideoCodec"] == "-c:v copy":
                self.slider_CRF.Disable()
                self.spin_Vbrate.Disable()
            else:
                self.slider_CRF.Disable()
                self.spin_Vbrate.Enable()
    # ------------------------------------------------------------------#

    def on_Vbitrate(self, event):
        """
        Reset a empty CRF (this depend if is h264 two-pass encoding
        or if not codec h264)
        """
        val = self.spin_Vbrate.GetValue()
        if cmd_opt["VideoCodec"] == "-c:v libaom-av1 -strict -2":
            if self.ckbx_pass.IsChecked():
                cmd_opt["CRF"] = ""

        if not cmd_opt["VideoCodec"] in ["-c:v libvpx", "-c:v libvpx-vp9",
                                         "-c:v libaom-av1 -strict -2"]:
            cmd_opt["CRF"] = ""

        cmd_opt["VideoBitrate"] = "" if val == -1 else "-b:v %sk" % val
    # ------------------------------------------------------------------#

    def on_Crf(self, event):
        """
        Reset bitrate at empty (this depend if is h264 codec)
        """
        val = self.slider_CRF.GetValue()
        if not cmd_opt["VideoCodec"] in ["-c:v libvpx", "-c:v libvpx-vp9",
                                         "-c:v libaom-av1 -strict -2"]:
            cmd_opt["VideoBitrate"] = ""

        cmd_opt["CRF"] = "" if val == -1 else "-crf %s" % val

    # ------------------------------------------------------------------#

    def on_Deadline(self, event):
        """
        Sets range according to spin_cpu used

        """
        if self.rdb_deadline.GetSelection() in [0, 1]:
            self.spin_cpu.SetRange(0, 5), self.spin_cpu.SetValue(0)
        else:
            self.spin_cpu.SetRange(0, 15), self.spin_cpu.SetValue(0)

    # ------------------------------------------------------------------#

    def on_FiltersPreview(self, event):
        """
        Showing a preview with applied filters only and Only the first
        file in the list `self.file_src` will be displayed
        """
        if not cmd_opt["VFilters"]:
            wx.MessageBox(_("No filter enabled"), "Videomass: Info",
                          wx.ICON_INFORMATION)
            return
        self.time_seq = self.parent.time_seq

        stream_play(self.parent.file_src[0],
                    self.time_seq, cmd_opt["VFilters"]
                    )
    # ------------------------------------------------------------------#

    def on_FiltersClear(self, event):
        """
        Reset all enabled filters
        """
        if not cmd_opt["VFilters"]:
            wx.MessageBox(_("No filter enabled"), "Videomass: Info",
                          wx.ICON_INFORMATION)
            return
        else:
            cmd_opt['Crop'], cmd_opt["Orientation"] = "", ["", ""]
            cmd_opt['Scale'], cmd_opt['Setdar'] = "", ""
            cmd_opt['Setsar'], cmd_opt['Deinterlace'] = "", ""
            cmd_opt['Interlace'], cmd_opt['Denoiser'] = "", ""
            cmd_opt["VFilters"] = ""
            self.btn_videosize.SetBottomEndColour(wx.Colour(self.btn_color))
            self.btn_crop.SetBottomEndColour(wx.Colour(self.btn_color))
            self.btn_denois.SetBottomEndColour(wx.Colour(self.btn_color))
            self.btn_lacing.SetBottomEndColour(wx.Colour(self.btn_color))
            self.btn_rotate.SetBottomEndColour(wx.Colour(self.btn_color))
    # ------------------------------------------------------------------#

    def video_filter_checker(self):
        """
        evaluates whether video filters (-vf) are enabled or not and
        sorts them according to an appropriate syntax. If not filters
        strings, the -vf option will be removed
        """
        if cmd_opt['Crop']:
            crop = '%s,' % cmd_opt['Crop']
        else:
            crop = ''
        if cmd_opt['Scale']:
            size = '%s,' % cmd_opt['Scale']
        else:
            size = ''
        if cmd_opt["Setdar"]:
            dar = '%s,' % cmd_opt['Setdar']
        else:
            dar = ''
        if cmd_opt["Setsar"]:
            sar = '%s,' % cmd_opt['Setsar']
        else:
            sar = ''
        if cmd_opt['Orientation'][0]:
            rotate = '%s,' % cmd_opt['Orientation'][0]
        else:
            rotate = ''
        if cmd_opt['Deinterlace']:
            lacing = '%s,' % cmd_opt['Deinterlace']
        elif cmd_opt['Interlace']:
            lacing = '%s,' % cmd_opt['Interlace']
        else:
            lacing = ''
        if cmd_opt["Denoiser"]:
            denoiser = '%s,' % cmd_opt['Denoiser']
        else:
            denoiser = ''

        f = crop + size + dar + sar + rotate + lacing + denoiser
        if f:
            lengh = len(f)
            filters = '%s' % f[:lengh - 1]
            cmd_opt["VFilters"] = "-vf %s" % filters
        else:
            cmd_opt["VFilters"] = ""

        # print (cmd_opt["VFilters"])
    # ------------------------------------------------------------------#

    def on_Enable_vsize(self, event):
        """
        Enable or disable video/image resolution functionalities
        """
        sizing = video_filters.VideoResolution(self,
                                               cmd_opt["Scale"],
                                               cmd_opt["Setdar"],
                                               cmd_opt["Setsar"],
                                               )
        retcode = sizing.ShowModal()
        if retcode == wx.ID_OK:
            data = sizing.GetValue()
            if not data:
                self.btn_videosize.SetBottomEndColour(
                    wx.Colour(self.btn_color)
                    )
                cmd_opt["Setdar"] = ""
                cmd_opt["Setsar"] = ""
                cmd_opt["Scale"] = ""
            else:
                self.btn_videosize.SetBottomEndColour(wx.Colour(YELLOW_LMN))
                if 'scale' in data:
                    cmd_opt["Scale"] = data['scale']
                else:
                    cmd_opt["Scale"] = ""
                if 'setdar' in data:
                    cmd_opt['Setdar'] = data['setdar']
                else:
                    cmd_opt['Setdar'] = ""
                if 'setsar' in data:
                    cmd_opt['Setsar'] = data['setsar']
                else:
                    cmd_opt['Setsar'] = ""
            self.video_filter_checker()
        else:
            sizing.Destroy()
            return
    # -----------------------------------------------------------------#

    def on_Enable_rotate(self, event):
        """
        Show a setting dialog for video/image rotate
        """
        rotate = video_filters.VideoRotate(self,
                                           cmd_opt["Orientation"][0],
                                           cmd_opt["Orientation"][1],
                                           )
        retcode = rotate.ShowModal()
        if retcode == wx.ID_OK:
            data = rotate.GetValue()
            cmd_opt["Orientation"][0] = data[0]  # cmd option
            cmd_opt["Orientation"][1] = data[1]  # msg
            if not data[0]:
                self.btn_rotate.SetBottomEndColour(wx.Colour(self.btn_color))
            else:
                self.btn_rotate.SetBottomEndColour(wx.Colour(YELLOW_LMN))
            self.video_filter_checker()
        else:
            rotate.Destroy()
            return
    # ------------------------------------------------------------------#

    def on_Enable_crop(self, event):
        """
        Show a setting dialog for video crop functionalities
        """
        crop = video_filters.VideoCrop(self, cmd_opt["Crop"])
        retcode = crop.ShowModal()
        if retcode == wx.ID_OK:
            data = crop.GetValue()
            if not data:
                self.btn_crop.SetBottomEndColour(wx.Colour(self.btn_color))
                cmd_opt["Crop"] = ''
            else:
                self.btn_crop.SetBottomEndColour(wx.Colour(YELLOW_LMN))
                cmd_opt["Crop"] = 'crop=%s' % data
            self.video_filter_checker()
        else:
            crop.Destroy()
            return
    # ------------------------------------------------------------------#

    def on_Enable_lacing(self, event):
        """
        Show a setting dialog for settings Deinterlace/Interlace filters
        """
        lacing = video_filters.Lacing(self,
                                      cmd_opt["Deinterlace"],
                                      cmd_opt["Interlace"],
                                      )
        retcode = lacing.ShowModal()
        if retcode == wx.ID_OK:
            data = lacing.GetValue()
            if not data:
                self.btn_lacing.SetBottomEndColour(wx.Colour(self.btn_color))
                cmd_opt["Deinterlace"] = ''
                cmd_opt["Interlace"] = ''
            else:
                self.btn_lacing.SetBottomEndColour(wx.Colour(YELLOW_LMN))
                if 'deinterlace' in data:
                    cmd_opt["Deinterlace"] = data["deinterlace"]
                    cmd_opt["Interlace"] = ''
                elif 'interlace' in data:
                    cmd_opt["Interlace"] = data["interlace"]
                    cmd_opt["Deinterlace"] = ''
            self.video_filter_checker()
        else:
            lacing.Destroy()
            return
    # ------------------------------------------------------------------#

    def on_Enable_denoiser(self, event):
        """
        Enable filters denoiser useful in some case, example when apply
        a deinterlace filter
        <https://askubuntu.com/questions/866186/how-to-get-good-quality-when-
        converting-digital-video>
        """
        den = video_filters.Denoisers(self, cmd_opt["Denoiser"])
        retcode = den.ShowModal()
        if retcode == wx.ID_OK:
            data = den.GetValue()
            if not data:
                self.btn_denois.SetBottomEndColour(wx.Colour(self.btn_color))
                cmd_opt["Denoiser"] = ''
            else:
                self.btn_denois.SetBottomEndColour(wx.Colour(YELLOW_LMN))
                cmd_opt["Denoiser"] = data
            self.video_filter_checker()
        else:
            den.Destroy()
            return
    # ------------------------------------------------------------------#

    def on_Vaspect(self, event):
        """
        Set aspect parameter (16:9, 4:3)
        """
        if self.cmb_Vaspect.GetValue() == "Auto":
            cmd_opt["AspectRatio"] = ""

        else:
            cmd_opt["AspectRatio"] = '-aspect %s' % self.cmb_Vaspect.GetValue()
    # ------------------------------------------------------------------#

    def on_Vrate(self, event):
        """
        Set video rate parameter with fps values
        """
        fps = self.cmb_Fps.GetValue()
        if fps == "Auto":
            cmd_opt["FPS"] = ""
        else:
            cmd_opt["FPS"] = "-r %s" % fps
    # ------------------------------------------------------------------#

    def setAudioRadiobox(self, event):
        """
        Container combobox sets compatible audio codecs to selected format.
        see AV_FORMATS dict

        """
        if self.cmb_Media.GetValue() == 'Video':
            if self.cmb_Vcod.GetValue() == 'Copy':  # enable all codec
                for n in range(self.rdb_a.GetCount()):
                    self.rdb_a.EnableItem(n, enable=True)
            else:
                for n, v in enumerate(AV_FORMATS[self.cmb_Vcont.GetValue()]):
                    if v:
                        self.rdb_a.EnableItem(n, enable=True)
                    else:
                        self.rdb_a.EnableItem(n, enable=False)
            self.rdb_a.SetSelection(0)

        if self.cmb_Media.GetValue() == 'Audio':
            for n, v in enumerate(AV_FORMATS[self.cmb_Vcont.GetValue()]):
                if v:
                    self.rdb_a.EnableItem(n, enable=True)
                    # self.rdb_a.SetSelection(n)
                else:
                    self.rdb_a.EnableItem(n, enable=False)
            for x in range(self.rdb_a.GetCount()):
                if self.rdb_a.IsItemEnabled(x):
                    self.rdb_a.SetSelection(x)
                    break
            self.on_AudioCodecs(self)
    # ------------------------------------------------------------------#

    def on_AudioCodecs(self, event):
        """
        When choose an item on audio radiobox list, set the audio format
        name and audio codec command (see ACODECS dict.). Also  set the
        view of the audio normalize widgets and reset values some cmd_opt
        keys.
        """
        audiocodec = self.rdb_a.GetStringSelection()

        def _param(enablenormalization, enablebuttonparameters):
            cmd_opt["AudioBitrate"] = ["", ""]
            cmd_opt["AudioChannel"] = ["", ""]
            cmd_opt["AudioRate"] = ["", ""]
            cmd_opt["AudioDepth"] = ["", ""]

            if enablenormalization:
                self.rdbx_normalize.Enable()
            else:
                self.rdbx_normalize.Disable()
            if enablebuttonparameters:
                self.btn_aparam.Enable()
                self.txt_audio_options.SetValue('')
                self.btn_aparam.SetForegroundColour(wx.Colour(self.fBtnC))
                self.btn_aparam.SetBottomEndColour(wx.Colour(self.btn_color))
            else:
                self.btn_aparam.Disable(),
                self.txt_audio_options.SetValue('')
                self.btn_aparam.SetForegroundColour(wx.Colour(GREY_DISABLED))
                self.btn_aparam.SetBottomEndColour(wx.Colour(self.btn_color))
        # --------------------------------------------------------
        for k, v in ACODECS.items():
            if audiocodec in k:
                if audiocodec == "Auto":
                    self.audio_default()
                    self.rdbx_normalize.Enable()
                    cmd_opt["AudioCodec"] = ["", ""]

                elif audiocodec == "Copy":
                    self.normalize_default()
                    _param(False, False)
                    cmd_opt["AudioCodec"] = ["-c:a:%s" %
                                             cmd_opt["AudioOutMap"][1], v]

                elif audiocodec == _("No Audio"):
                    self.normalize_default()
                    cmd_opt["AudioCodec"] = ["", v]
                    _param(False, False)

                    # break
                else:
                    _param(True, True)
                    cmd_opt["AudioCodec"] = ["-c:a:%s" %
                                             cmd_opt["AudioOutMap"][1], v]

                cmd_opt["AudioCodStr"] = audiocodec

        if audiocodec == 'No Audio':  # audio Mapping disable
            self.cmb_A_inMap.SetSelection(0), self.cmb_A_inMap.Disable()
            self.cmb_A_outMap.Disable(), self.on_audioINstream(self)
        else:
            self.cmb_A_inMap.Enable(), self.cmb_A_outMap.Enable()
    # -------------------------------------------------------------------#

    def on_AudioParam(self, event):
        """
        Event by Audio options button. Set audio codec string and audio
        command string and pass it to audio_dialogs method.
        """
        pcm = ["pcm_s16le", "pcm_s24le", "pcm_s32le"]

        if cmd_opt["AudioCodec"][1] in pcm:
            self.audio_dialog(cmd_opt["AudioCodStr"],
                              "%s Audio Settings" % cmd_opt["AudioCodStr"])
        else:
            self.audio_dialog(cmd_opt["AudioCodStr"],
                              "%s Audio Settings" % cmd_opt["AudioCodStr"])
    # -------------------------------------------------------------------#

    def audio_dialog(self, audio_type, title):
        """
        Run audio dialog on specified audio codec to get additionals
        audio options.

        NOTE: The data[X] tuple contains the command parameters on the
              index [1] and the descriptive parameters on the index [0].
              exemple: data[0] contains parameters for channel then
              data[0][1] is ffmpeg option command for audio channels and
              data[0][0] is a simple description for view.
        """
        audiodialog = audiodialogs.AudioSettings(self,
                                                 audio_type,
                                                 cmd_opt["AudioRate"],
                                                 cmd_opt["AudioDepth"],
                                                 cmd_opt["AudioBitrate"],
                                                 cmd_opt["AudioChannel"],
                                                 title,
                                                 )
        retcode = audiodialog.ShowModal()

        if retcode == wx.ID_OK:
            data = audiodialog.GetValue()
            cmd_opt["AudioChannel"] = data[0]
            cmd_opt["AudioRate"] = data[1]
            cmd_opt["AudioBitrate"] = data[2]
            if audio_type in ('wav', 'aiff', 'PCM'):
                if 'Auto' in data[3][0]:  # [3] is the bit depth tupla
                    cmd_opt["AudioCodec"] = ["-c:a:%s" %
                                             cmd_opt["AudioOutMap"][1],
                                             "pcm_s16le"
                                             ]
                else:
                    cmd_opt["AudioCodec"] = ["-c:a:%s" %
                                             cmd_opt["AudioOutMap"][1],
                                             data[3][1]
                                             ]
                cmd_opt["AudioDepth"] = ("%s" % (data[3][0]), '')  # null
            else:  # entra su tutti tranne wav aiff
                cmd_opt["AudioDepth"] = data[3]
        else:
            data = None
            audiodialog.Destroy()
            return

        self.txt_audio_options.Clear()
        count = 0
        for d in [cmd_opt["AudioRate"], data[3],
                  cmd_opt["AudioBitrate"], cmd_opt["AudioChannel"]
                  ]:
            if d[1]:
                count += 1
                self.txt_audio_options.AppendText(" %s | " % d[0])

        if count == 0:
            self.btn_aparam.SetBottomEndColour(wx.Colour(self.btn_color))
        else:
            self.btn_aparam.SetBottomEndColour(wx.Colour(YELLOW_LMN))

        audiodialog.Destroy()
    # ------------------------------------------------------------------#

    def on_audioINstream(self, event):
        """
        sets the specified audio input stream as index to process,
        e.g. for filters volumedected and loudnorm will map 0:N
        where N is digit from 0 to available audio index up to 8.
        See: http://ffmpeg.org/ffmpeg.html#Advanced-options
        When changes this feature affect audio filter peak and rms analyzers
        and then re-enable volume dected button .
        """
        sel = self.cmb_A_inMap.GetValue()
        if sel == 'Auto':
            cmd_opt["AudioInMap"] = ['', '']
            self.cmb_A_outMap.SetSelection(1)
            self.on_audioOUTstream(self)
        else:
            cmd_opt["AudioInMap"] = ['-map 0:%s' % sel, sel]
            self.cmb_A_outMap.SetStringSelection(self.cmb_A_inMap.GetValue())
            self.on_audioOUTstream(self)

        if self.rdbx_normalize.GetSelection() in [1, 2]:
            if not self.btn_voldect.IsEnabled():
                self.btn_voldect.Enable()
                self.btn_voldect.SetForegroundColour(wx.Colour(self.fBtnC))
    # ------------------------------------------------------------------#

    def on_audioOUTstream(self, event):
        """
        Sets the audio stream index for the output file and sets
        audio codec to specified map.

        """
        sel = self.cmb_A_outMap.GetValue()
        if sel == 'Auto':
            cmd_opt["AudioOutMap"] = ['', '']
        elif sel == 'All':
            cmd_opt["AudioOutMap"] = ['-map 0:a?', '']
        else:
            sel = int(sel) - 1
            cmd_opt["AudioOutMap"] = ['-map 0:a%s?' % str(sel),
                                      '%s' % str(sel)]
        if cmd_opt["AudioCodec"][0]:
            cmd_opt["AudioCodec"][0] = "-c:a:%s" % cmd_opt["AudioOutMap"][1]
    # ------------------------------------------------------------------#

    def onNormalize(self, event):
        """
        Enable or disable functionality for volume normalization of
        the video.

        """
        msg_1 = (_('Activate peak level normalization, which will produce '
                   'a maximum peak level equal to the set target level.'
                   ))
        msg_2 = (_('Activate RMS-based normalization, which according to '
                   'mean volume calculates the amount of gain to reach same '
                   'average power signal.'
                   ))
        msg_3 = (_('Activate two passes normalization. It Normalizes the '
                   'perceived loudness using the "​loudnorm" filter, which '
                   'implements the EBU R128 algorithm.'
                   ))
        if self.rdbx_normalize.GetSelection() == 1:  # is checked
            self.normalize_default(False)
            self.parent.statusbar_msg(msg_1, AZURE)
            self.peakpanel.Show()

        elif self.rdbx_normalize.GetSelection() == 2:
            self.normalize_default(False)
            self.parent.statusbar_msg(msg_2, TROPGREEN)
            self.peakpanel.Show(), self.spin_target.SetValue(-20)

        elif self.rdbx_normalize.GetSelection() == 3:
            self.parent.statusbar_msg(msg_3, LIMEGREEN)
            self.normalize_default(False)
            self.ebupanel.Show()
            self.ckbx_pass.SetValue(True), self.ckbx_pass.Disable()
            cmd_opt["Passing"] = "2 pass"
            if not self.cmb_Vcod.GetSelection() == 6:  # copycodec
                self.on_Pass(self)
        else:
            self.parent.statusbar_msg(_("Audio normalization off"), None)
            self.normalize_default(False)

        self.nb_filters.Layout()

        if not self.rdbx_normalize.GetSelection() == 3:
            if not self.cmb_Vcod.GetSelection() == 6:  # copycodec
                self.ckbx_pass.Enable()

        if self.cmb_Vcod.GetSelection() == 6:  # copycodec
            if not self.rdbx_normalize.GetSelection() == 3:
                self.ckbx_pass.SetValue(False)
    # ------------------------------------------------------------------#

    def on_enter_Ampl(self, event):
        """
        when spin_amplitude is changed enable 'Volumedected' to
        update new incomming

        """
        if not self.btn_voldect.IsEnabled():
            self.btn_voldect.Enable()
            self.btn_voldect.SetForegroundColour(wx.Colour(self.fBtnC))
    # ------------------------------------------------------------------#

    def on_Audio_analyzes(self, event):  # Volumedetect button
        """
        - normalizations based on PEAK Analyzes to get MAXIMUM peak levels
          data to calculates offset in dBFS need for audio normalization
          process.
        - normalizations based on RMS Analyzes to get MEAN peak levels data to
          calculates RMS offset in dBFS need for audio normalization process.

        <https://superuser.com/questions/323119/how-can-i-normalize-audio-
        using-ffmpeg?utm_medium=organic>

        """
        msg2 = (_('Audio normalization is required only for some files'))
        msg3 = (_('Audio normalization is not required based to '
                  'set target level'))
        if self.normdetails:
            del self.normdetails[:]

        self.parent.statusbar_msg("", None)
        self.time_seq = self.parent.time_seq  # from -ss to -t will be analyzed
        target = self.spin_target.GetValue()

        data = volumeDetectProcess(self.parent.file_src,
                                   self.time_seq,
                                   cmd_opt["AudioInMap"][0]
                                   )
        if data[1]:
            wx.MessageBox(data[1], "ERROR! -Videomass", wx.ICON_ERROR)
            return
        else:
            volume = list()
            if self.rdbx_normalize.GetSelection() == 1:  # RMS
                for f, v in zip(self.parent.file_src, data[0]):
                    maxvol = v[0].split(' ')[0]
                    meanvol = v[1].split(' ')[0]
                    offset = float(maxvol) - float(target)
                    result = float(maxvol) - offset
                    if float(maxvol) == float(target):
                        volume.append('  ')
                    else:
                        volume.append("-filter:a:%s volume=%fdB" %
                                      (cmd_opt["AudioOutMap"][1],
                                       -offset)
                                      )
                    self.normdetails.append((f,
                                             maxvol,
                                             meanvol,
                                             str(offset),
                                             str(result),
                                             ))
            elif self.rdbx_normalize.GetSelection() == 2:  # ebu
                for f, v in zip(self.parent.file_src, data[0]):
                    maxvol = v[0].split(' ')[0]
                    meanvol = v[1].split(' ')[0]
                    offset = float(meanvol) - float(target)
                    result = float(maxvol) - offset
                    if offset == 0.0:
                        volume.append('  ')
                    else:
                        volume.append("-filter:a:%s volume=%fdB" % (
                                                    cmd_opt["AudioOutMap"][1],
                                                    -offset))
                    self.normdetails.append((f,
                                             maxvol,
                                             meanvol,
                                             str(offset),
                                             str(result),
                                             ))
        if [a for a in volume if '  ' not in a] == []:
            self.parent.statusbar_msg(msg3, ORANGE)
        else:
            if len(volume) == 1 or '  ' not in volume:
                pass
            else:
                self.parent.statusbar_msg(msg2, YELLOW)
        if self.rdbx_normalize.GetSelection() == 1:  # PEAK
            cmd_opt["PEAK"] = volume
        elif self.rdbx_normalize.GetSelection() == 2:  # RMS
            cmd_opt["RMS"] = volume
        self.btn_voldect.Disable()
        self.btn_voldect.SetForegroundColour(wx.Colour(GREY_DISABLED))
        self.btn_details.Show()
        self.nb_filters.Layout()
    # ------------------------------------------------------------------#

    def on_Show_normlist(self, event):
        """
        Show a wx.ListCtrl dialog with volumedected data
        """
        if self.rdbx_normalize.GetSelection() == 1:  # PEAK
            title = _('PEAK-based volume statistics')
        elif self.rdbx_normalize.GetSelection() == 2:  # RMS
            title = _('RMS-based volume statistics')

        audionormlist = shownormlist.NormalizationList(title,
                                                       self.normdetails,
                                                       self.oS)
        audionormlist.Show()
    # ------------------------------------------------------------------#

    def on_xPreset(self, event):
        """
        Set h264/h265 only
        """
        sel = self.cmb_preset.GetStringSelection()
        cmd_opt["Preset"] = '' if sel == 'None' else '-preset:v %s' % sel
    # ------------------------------------------------------------------#

    def on_xProfile(self, event):
        """
        Set h264/h265 only
        """
        sel = self.cmb_profile.GetStringSelection()
        cmd_opt["Profile"] = '' if sel == 'None' else '-profile:v %s' % sel
    # ------------------------------------------------------------------#

    def on_Level(self, event):
        """
        Set profile level for h264/h265. This flag must be insert
        after -profile:v parameter.
        """
        sel = self.cmb_level.GetStringSelection()
        cmd_opt["Level"] = '' if sel == 'None' else '-level %s' % sel
    # ------------------------------------------------------------------#

    def on_xTune(self, event):
        """
        Set h264/h265 only
        """
        sel = self.cmb_tune.GetStringSelection()
        cmd_opt["Tune"] = '' if sel == 'None' else '-tune:v %s' % sel
    # -------------------------------------------------------------------#

    def update_allentries(self):
        """
        Update entries.
        """
        if self.spin_Vbrate.IsEnabled() and not self.slider_CRF.IsEnabled():
            self.on_Vbitrate(self)

        elif self.slider_CRF.IsEnabled() and not self.spin_Vbrate.IsEnabled():
            self.on_Crf(self)

        elif self.slider_CRF.IsEnabled() and self.spin_Vbrate.IsEnabled():
            self.on_Vbitrate(self), self.on_Crf(self)
        else:
            cmd_opt["CRF"] = ''
            cmd_opt["VideoBitrate"] = ''

        if self.vp9panel.IsShown():
            deadline = self.rdb_deadline.GetStringSelection()
            cmd_opt["CpuUsed"] = '-cpu-used %s' % self.spin_cpu.GetValue()
            cmd_opt["Deadline"] = '-deadline %s' % deadline
            if self.ckbx_rowMt1.IsChecked():
                cmd_opt["RowMthreading"] = '-row-mt 1'
            else:
                cmd_opt["RowMthreading"] = ''
        else:
            cmd_opt["CpuUsed"] = ''
            cmd_opt["Deadline"] = ''
            cmd_opt["RowMthreading"] = ''

        if self.spinMinr.GetValue() > 0:
            cmd_opt["MinRate"] = '-minrate %sk' % self.spinMinr.GetValue()
        else:
            cmd_opt["MinRate"] = ''
        if self.spinMaxr.GetValue() > 0:
            cmd_opt["MaxRate"] = '-maxrate %sk' % self.spinMaxr.GetValue()
        else:
            cmd_opt["MaxRate"] = ''
        if self.spinBufsize.GetValue() > 0:
            cmd_opt["Bufsize"] = '-bufsize %sk' % self.spinBufsize.GetValue()
        else:
            cmd_opt["Bufsize"] = ''

        if self.cmb_Pixfrm.GetValue() == 'None':
            cmd_opt["PixFmt"] = ''
        else:
            cmd_opt["PixFmt"] = '-pix_fmt %s' % self.cmb_Pixfrm.GetValue()

        smap = self.cmb_Submap.GetValue()
        if smap == 'None':
            cmd_opt["SubtitleMap"] = '-sn'
        elif smap == 'All':
            cmd_opt["SubtitleMap"] = '-map 0:s?'

        if self.rdb_a.GetStringSelection() == "No Audio":
            self.cmb_A_inMap.SetSelection(0), self.on_audioINstream(self)
            self.cmb_A_outMap.SetSelection(1), self.on_audioOUTstream(self)
    # ------------------------------------------------------------------#

    def on_start(self):
        """
        Check the settings and files before redirecting
        to the build command.

        typeproc      : batch or single process
        filename      : file name without extension
        base_name     : file name with extension
        countmax      : count processing cicles for batch mode
        """

        # check normalization data offset, if enable
        logname = 'Videomass_AVconversions.log'
        if self.rdbx_normalize.GetSelection() in [1, 2]:
            if self.btn_voldect.IsEnabled():
                wx.MessageBox(_('Undetected volume values! use the '
                                '"Volumedetect" control button to analyze '
                                'the data on the audio volume.'),
                              'Videomass', wx.ICON_INFORMATION
                              )
                return

        self.update_allentries()  # update

        if self.cmb_Media.GetValue() == 'Video':  # CHECKING
            checking = inspect(self.parent.file_src,
                               self.parent.file_destin,
                               cmd_opt["OutputFormat"]
                               )
            if not checking[0]:  # User changing idea or not such files exist
                return
            (typeproc, f_src, destin, filename, base_name, countmax) = checking
            if self.rdbx_normalize.GetSelection() == 3:  # EBU
                self.video_ebu_2pass(f_src, destin, countmax, logname)
            else:
                self.video_stdProc(f_src, destin, countmax, logname)

        elif self.cmb_Media.GetValue() == 'Audio':  # CHECKING
            checking = inspect(self.parent.file_src,
                               self.parent.file_destin,
                               cmd_opt["OutputFormat"])
            if not checking[0]:  # User changing idea or not such files exist
                return
            (typeproc, f_src, destin, filename, base_name, countmax) = checking
            if self.rdbx_normalize.GetSelection() == 3:
                self.audio_ebu_2pass(f_src, destin, countmax, logname)
            else:
                self.audio_stdProc(f_src, destin, countmax, logname)
        return
    # ------------------------------------------------------------------#

    def video_stdProc(self, f_src, destin, countmax, logname):
        """
        Build the ffmpeg command strings for video conversions.
        """
        audnorm = cmd_opt["RMS"] if not cmd_opt["PEAK"] else cmd_opt["PEAK"]

        if self.cmb_Vcod.GetValue() == "Copy":
            command = (
                    f'{cmd_opt["VideoCodec"]} {cmd_opt["PixFmt"]} '
                    f'{cmd_opt["WebOptim"]} {cmd_opt["AspectRatio"]} '
                    f'{cmd_opt["FPS"]}  -map 0:v? -map_chapters 0 '
                    f'{cmd_opt["SubtitleMap"]} {cmd_opt["AudioCodec"][0]} '
                    f'{cmd_opt["AudioCodec"][1]} {cmd_opt["AudioBitrate"][1]} '
                    f'{cmd_opt["AudioRate"][1]} {cmd_opt["AudioChannel"][1]} '
                    f'{cmd_opt["AudioDepth"][1]} {cmd_opt["AudioOutMap"][0]} '
                    f'-map_metadata 0'
                      )
            command = " ".join(command.split())  # mi formatta la stringa
            if logname == 'save as profile':
                return command, '', cmd_opt["OutputFormat"]
            valupdate = self.update_dict(countmax, ["Copy"])
            ending = Formula(self, valupdate[0], valupdate[1], 'Copy')

            if ending.ShowModal() == wx.ID_OK:
                # ending.Destroy() # con ID_OK e ID_CANCEL non serve Destroy()
                self.parent.switch_to_processing('onepass',
                                                 f_src,
                                                 cmd_opt["OutputFormat"],
                                                 destin,
                                                 command,
                                                 None,
                                                 '',
                                                 audnorm,
                                                 logname,
                                                 countmax,
                                                 )
        elif cmd_opt["Passing"] == "2 pass":
            if cmd_opt["VideoCodec"] == "-c:v libx265":
                opt1, opt2 = '-x265-params pass=1', '-x265-params pass=2'
            else:
                opt1, opt2 = '-pass 1', '-pass 2'

            cmd1 = (f'-an -sn {cmd_opt["VideoCodec"]} '
                    f'{cmd_opt["VideoBitrate"]} {cmd_opt["MinRate"]} '
                    f'{cmd_opt["MaxRate"]} {cmd_opt["Bufsize"]} '
                    f'{cmd_opt["CRF"]} {cmd_opt["Deadline"]} '
                    f'{cmd_opt["CpuUsed"]} {cmd_opt["RowMthreading"]} '
                    f'{cmd_opt["Preset"]} {cmd_opt["Profile"]} '
                    f'{cmd_opt["Level"]} {cmd_opt["Tune"]} '
                    f'{cmd_opt["AspectRatio"]} {cmd_opt["FPS"]} '
                    f'{cmd_opt["VFilters"]} {cmd_opt["PixFmt"]} '
                    f'{cmd_opt["WebOptim"]} {opt1} -f rawvideo'
                    )
            cmd2 = (f'{cmd_opt["VideoCodec"]} {cmd_opt["VideoBitrate"]} '
                    f'{cmd_opt["MinRate"]} {cmd_opt["MaxRate"]} '
                    f'{cmd_opt["Bufsize"]} {cmd_opt["CRF"]} '
                    f'{cmd_opt["Deadline"]} {cmd_opt["CpuUsed"]} '
                    f'{cmd_opt["RowMthreading"]} {cmd_opt["Preset"]} '
                    f'{cmd_opt["Profile"]} {cmd_opt["Level"]} '
                    f'{cmd_opt["Tune"]} {cmd_opt["AspectRatio"]} '
                    f'{cmd_opt["FPS"]} {cmd_opt["VFilters"]} '
                    f'{cmd_opt["PixFmt"]} {cmd_opt["WebOptim"]} '
                    f'-map 0:v? -map_chapters 0 {opt2} '
                    f'{cmd_opt["SubtitleMap"]} {cmd_opt["AudioCodec"][0]} '
                    f'{cmd_opt["AudioCodec"][1]} {cmd_opt["AudioBitrate"][1]} '
                    f'{cmd_opt["AudioRate"][1]} {cmd_opt["AudioChannel"][1]} '
                    f'{cmd_opt["AudioDepth"][1]} {cmd_opt["AudioOutMap"][0]} '
                    f'-map_metadata 0'
                    )
            pass1 = " ".join(cmd1.split())
            pass2 = " ".join(cmd2.split())
            if logname == 'save as profile':
                return pass1, pass2, cmd_opt["OutputFormat"]
            valupdate = self.update_dict(countmax, [''])
            title = 'Two pass Video Encoding'
            ending = Formula(self, valupdate[0], valupdate[1], title)

            if ending.ShowModal() == wx.ID_OK:
                self.parent.switch_to_processing('twopass',
                                                 f_src,
                                                 cmd_opt["OutputFormat"],
                                                 destin,
                                                 None,
                                                 [pass1, pass2],
                                                 '',
                                                 audnorm,
                                                 logname,
                                                 countmax,
                                                 )
        elif cmd_opt["Passing"] == "1 pass":  # Batch-Mode / h264 Codec
            command = (
                    f'{cmd_opt["VideoCodec"]} {cmd_opt["VideoBitrate"]} '
                    f'{cmd_opt["MinRate"]} {cmd_opt["MaxRate"]} '
                    f'{cmd_opt["Bufsize"]} {cmd_opt["CRF"]} '
                    f'{cmd_opt["Deadline"]} {cmd_opt["CpuUsed"]} '
                    f'{cmd_opt["RowMthreading"]} {cmd_opt["Preset"]} '
                    f'{cmd_opt["Profile"]} {cmd_opt["Level"]} '
                    f'{cmd_opt["Tune"]} {cmd_opt["AspectRatio"]} '
                    f'{cmd_opt["FPS"]} {cmd_opt["VFilters"]} '
                    f'{cmd_opt["PixFmt"]} {cmd_opt["WebOptim"]} '
                    f'-map 0:v? -map_chapters 0 '
                    f'{cmd_opt["SubtitleMap"]} {cmd_opt["AudioCodec"][0]} '
                    f'{cmd_opt["AudioCodec"][1]} {cmd_opt["AudioBitrate"][1]} '
                    f'{cmd_opt["AudioRate"][1]} {cmd_opt["AudioChannel"][1]} '
                    f'{cmd_opt["AudioDepth"][1]} {cmd_opt["AudioOutMap"][0]} '
                    f'-map_metadata 0'
                        )
            command = " ".join(command.split())  # mi formatta la stringa
            if logname == 'save as profile':
                return command, '', cmd_opt["OutputFormat"]
            valupdate = self.update_dict(countmax, [''])
            title = 'One pass Video Encoding'
            ending = Formula(self, valupdate[0], valupdate[1], title)

            if ending.ShowModal() == wx.ID_OK:
                self.parent.switch_to_processing('onepass',
                                                 f_src,
                                                 cmd_opt["OutputFormat"],
                                                 destin,
                                                 command,
                                                 None,
                                                 '',
                                                 audnorm,
                                                 logname,
                                                 countmax,
                                                 )
    # ------------------------------------------------------------------#

    def video_ebu_2pass(self, f_src, destin, countmax, logname):
        """
        Define the ffmpeg command strings for batch process with
        EBU two-passes conversion.
        NOTE If you want leave same indexes and process a selected Input Audio
             Index use same Output Audio Index on Audio Streams Mapping box

        """
        title = _('Audio/Video EBU normalization')
        cmd_opt["EBU"] = 'EBU R128'
        loudfilter = ('loudnorm=I=%s:TP=%s:LRA=%s:print_format=summary' %
                      (str(self.spin_i.GetValue()),
                       str(self.spin_tp.GetValue()),
                       str(self.spin_lra.GetValue()),
                       ))
        if cmd_opt["VideoCodec"] == "-c:v libx265":
            opt1, opt2 = '-x265-params pass=1', '-x265-params pass=2'
        else:
            opt1, opt2 = '-pass 1', '-pass 2'

        if self.cmb_Vcod.GetValue() == "Copy":
            cmd_1 = (f'-map 0:v? {cmd_opt["AudioInMap"][0]} '
                     f'-filter:a: {loudfilter} '
                     f'-vn -sn {opt1} {cmd_opt["AspectRatio"]} '
                     f'{cmd_opt["FPS"]} -f null'
                     )
            cmd_2 = (f'{cmd_opt["VideoCodec"]} {opt2} {cmd_opt["AspectRatio"]} '
                     f'{cmd_opt["FPS"]} {cmd_opt["PixFmt"]} '
                     f'{cmd_opt["WebOptim"]} -map 0:v? -map_chapters 0 '
                     f'{cmd_opt["SubtitleMap"]} {cmd_opt["AudioCodec"][0]} '
                     f'{cmd_opt["AudioCodec"][1]} {cmd_opt["AudioBitrate"][1]} '
                     f'{cmd_opt["AudioRate"][1]} {cmd_opt["AudioChannel"][1]} '
                     f'{cmd_opt["AudioDepth"][1]} {cmd_opt["AudioOutMap"][0]} '
                     f'-map_metadata 0'
                     )
            pass1 = " ".join(cmd_1.split())
            pass2 = " ".join(cmd_2.split())
            if logname == 'save as profile':
                return pass1, pass2, cmd_opt["OutputFormat"]
            valupdate = self.update_dict(countmax, ["Copy"])
            ending = Formula(self, valupdate[0], valupdate[1], title)

            if ending.ShowModal() == wx.ID_OK:
                self.parent.switch_to_processing('two pass EBU',
                                                 f_src,
                                                 cmd_opt["OutputFormat"],
                                                 destin,
                                                 None,
                                                 [pass1, pass2, loudfilter],
                                                 cmd_opt["AudioOutMap"],
                                                 None,
                                                 logname,
                                                 countmax,
                                                 )
        else:
            cmd_1 = (f'{cmd_opt["VideoCodec"]} {cmd_opt["VideoBitrate"]} '
                     f'{cmd_opt["MinRate"]} {cmd_opt["MaxRate"]} '
                     f'{cmd_opt["Bufsize"]} {cmd_opt["CRF"]} '
                     f'{cmd_opt["Deadline"]} {cmd_opt["CpuUsed"]} '
                     f'{cmd_opt["RowMthreading"]} {cmd_opt["Preset"]} '
                     f'{cmd_opt["Profile"]} {cmd_opt["Level"]} '
                     f'{cmd_opt["Tune"]} {cmd_opt["AspectRatio"]} '
                     f'{cmd_opt["FPS"]} {cmd_opt["VFilters"]} '
                     f'{cmd_opt["PixFmt"]} {cmd_opt["WebOptim"]} '
                     f'-map 0:v? {cmd_opt["AudioInMap"][0]}  '
                     f'{opt1} -sn -filter:a: {loudfilter} '
                     f'-f {MUXERS[cmd_opt["OutputFormat"]]}'
                     )
            cmd_2 = (f'{cmd_opt["VideoCodec"]} {cmd_opt["VideoBitrate"]} '
                     f'{cmd_opt["MinRate"]} {cmd_opt["MaxRate"]} '
                     f'{cmd_opt["Bufsize"]} {cmd_opt["CRF"]} '
                     f'{cmd_opt["Deadline"]} {cmd_opt["CpuUsed"]} '
                     f'{cmd_opt["RowMthreading"]} {cmd_opt["Preset"]} '
                     f'{cmd_opt["Profile"]} {cmd_opt["Level"]} '
                     f'{cmd_opt["Tune"]} {cmd_opt["AspectRatio"]} '
                     f'{cmd_opt["FPS"]} {cmd_opt["VFilters"]} '
                     f'{cmd_opt["PixFmt"]} {cmd_opt["WebOptim"]} '
                     f'-map 0:v? -map_chapters 0 {opt2} '
                     f'{cmd_opt["SubtitleMap"]} {cmd_opt["AudioCodec"][0]} '
                     f'{cmd_opt["AudioCodec"][1]} {cmd_opt["AudioBitrate"][1]} '
                     f'{cmd_opt["AudioRate"][1]} {cmd_opt["AudioChannel"][1]} '
                     f'{cmd_opt["AudioDepth"][1]} {cmd_opt["AudioOutMap"][0]} '
                     f'-map_metadata 0'
                     )
            pass1 = " ".join(cmd_1.split())
            pass2 = " ".join(cmd_2.split())  # mi formatta la stringa
            if logname == 'save as profile':
                return pass1, pass2, cmd_opt["OutputFormat"]
            valupdate = self.update_dict(countmax, [''])
            ending = Formula(self, valupdate[0], valupdate[1], title)

            if ending.ShowModal() == wx.ID_OK:
                self.parent.switch_to_processing('two pass EBU',
                                                 f_src,
                                                 cmd_opt["OutputFormat"],
                                                 destin,
                                                 None,
                                                 [pass1, pass2, loudfilter],
                                                 cmd_opt["AudioOutMap"],
                                                 None,
                                                 logname,
                                                 countmax,
                                                 )
            # ending.Destroy() # con ID_OK e ID_CANCEL non serve Destroy()
    # ------------------------------------------------------------------#

    def audio_stdProc(self, f_src, destin, countmax, logname):
        """
        Build the ffmpeg command strings for audio conversion.

        """
        audnorm = cmd_opt["RMS"] if not cmd_opt["PEAK"] else cmd_opt["PEAK"]
        title = _('Audio conversions')
        command = (f'-vn -sn {cmd_opt["WebOptim"]} {cmd_opt["AudioInMap"][0]} '
                   f'{cmd_opt["AudioCodec"][0]} {cmd_opt["AudioCodec"][1]} '
                   f'{cmd_opt["AudioBitrate"][1]} {cmd_opt["AudioDepth"][1]} '
                   f'{cmd_opt["AudioRate"][1]} {cmd_opt["AudioChannel"][1]} '
                   f'-map_metadata 0'
                   )
        command = " ".join(command.split())  # mi formatta la stringa
        if logname == 'save as profile':
            return command, '', cmd_opt["OutputFormat"]
        valupdate = self.update_dict(countmax, [''])
        ending = Formula(self, valupdate[0], valupdate[1], title)

        if ending.ShowModal() == wx.ID_OK:
            self.parent.switch_to_processing('onepass',
                                             f_src,
                                             cmd_opt["OutputFormat"],
                                             destin,
                                             command,
                                             None,
                                             '',
                                             audnorm,
                                             logname,
                                             countmax,
                                             )
    # ------------------------------------------------------------------#

    def audio_ebu_2pass(self, f_src, destin, countmax, logname):
        """
        Perform EBU R128 normalization on audio conversion
        WARNING do not map output audio file index on filter:a: , -c:a:
        and not send cmd_opt["AudioOutMap"] to process because the files
        audio has not indexes
        """
        cmd_opt["EBU"] = True
        loudfilter = ('loudnorm=I=%s:TP=%s:LRA=%s:print_format=summary' %
                      (str(self.spin_i.GetValue()),
                       str(self.spin_tp.GetValue()),
                       str(self.spin_lra.GetValue())
                       ))
        title = _('Audio EBU normalization')

        cmd_1 = (f'{cmd_opt["WebOptim"]} {cmd_opt["AudioInMap"][0]} '
                 f'-filter:a: {loudfilter} -vn -sn -pass 1 -f null'
                 )
        cmd_2 = (f'-vn -sn {cmd_opt["WebOptim"]} {cmd_opt["AudioInMap"][0]} '
                 f'-pass 2 {cmd_opt["AudioCodec"][0]} '
                 f'{cmd_opt["AudioCodec"][1]} {cmd_opt["AudioBitrate"][1]} '
                 f'{cmd_opt["AudioDepth"][1]} {cmd_opt["AudioRate"][1]} '
                 f'{cmd_opt["AudioChannel"][1]} -map_metadata 0'
                 )
        pass1 = " ".join(cmd_1.split())
        pass2 = " ".join(cmd_2.split())
        if logname == 'save as profile':
            return pass1, pass2, cmd_opt["OutputFormat"]
        valupdate = self.update_dict(countmax, [''])
        ending = Formula(self, valupdate[0], valupdate[1], title)

        if ending.ShowModal() == wx.ID_OK:
            self.parent.switch_to_processing('two pass EBU',
                                             f_src,
                                             cmd_opt["OutputFormat"],
                                             destin,
                                             None,
                                             [pass1, pass2, loudfilter],
                                             ['', ''],  # do not map audio file
                                             None,
                                             logname,
                                             countmax,
                                             )
    # ------------------------------------------------------------------#

    def update_dict(self, countmax, prof):
        """
        Update all settings before send to epilogue
        """
        numfile = _("%s file in pending") % str(countmax)
        if cmd_opt["PEAK"]:
            normalize = 'PEAK'
        elif cmd_opt["RMS"]:
            normalize = 'RMS'
        elif cmd_opt["EBU"]:
            normalize = 'EBU R128'
        else:
            normalize = _('Off')
        if self.cmb_Vcont.GetValue() == "Copy":
            outputformat = "Copy"
        else:
            outputformat = cmd_opt["OutputFormat"]
        if not self.parent.time_seq:
            time = _('Off')
        else:
            t = list(self.parent.time_read.items())
            time = '{0}: {1} | {2}: {3}'.format(t[0][0], t[0][1][0],
                                                t[1][0], t[1][1][0])
        # ------------------
        if self.cmb_Media.GetValue() == 'Audio':
            formula = (_("SUMMARY\n\nFile Queue\nOutput Format\
                        \nWeb Optimize\nAudio Codec\nAudio bit-rate\
                        \nAudio Channels\nAudio Rate\nBit per Sample\
                        \nAudio Normalization\nTime selection\
                        \nSelected Input Audio index"))
            dictions = ("\n\n%s\n%s\n%s\n%s\n%s\n%s"
                        "\n%s\n%s\n%s\n%s\n%s" % (numfile,
                                                  outputformat,
                                                  cmd_opt["WebOptim"],
                                                  cmd_opt["AudioCodStr"],
                                                  cmd_opt["AudioBitrate"][0],
                                                  cmd_opt["AudioChannel"][0],
                                                  cmd_opt["AudioRate"][0],
                                                  cmd_opt["AudioDepth"][0],
                                                  normalize,
                                                  time,
                                                  self.cmb_A_outMap.GetValue(),
                                                  )
                        )
        elif prof[0] == "Copy":
            formula = (_("SUMMARY\n\nFile to Queue\nWeb Optimize\nOutput Format\
                        \nVideo Codec\nAspect Ratio\nFPS\nAudio Codec\
                        \nAudio Channels\nAudio Rate\nAudio bit-rate\
                        \nBit per Sample\nAudio Normalization\
                        \nSelected Input Audio index\nAudio Output Map index\
                        \nSubtitle stream index\nTime selection"))
            dictions = ("\n\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\
                         \n%s\n%s\n%s\n%s" % (numfile,
                                              cmd_opt["WebOptim"],
                                              outputformat,
                                              cmd_opt["VidCmbxStr"],
                                              cmd_opt["AspectRatio"],
                                              cmd_opt["FPS"],
                                              cmd_opt["AudioCodStr"],
                                              cmd_opt["AudioChannel"][0],
                                              cmd_opt["AudioRate"][0],
                                              cmd_opt["AudioBitrate"][0],
                                              cmd_opt["AudioDepth"][0],
                                              normalize,
                                              self.cmb_A_inMap.GetValue(),
                                              self.cmb_A_outMap.GetValue(),
                                              self.cmb_Submap.GetValue(),
                                              time,
                                              ))
        # --------------------
        else:
            formula = (_("SUMMARY\n\nFile to Queue\nWeb Optimize\nPass Encoding\
                         \nOutput Format\nVideo Codec\nVideo bit-rate\
                         \nCRF\nMin Rate\nMax Rate\nBuffer size\
                         \nVP8/VP9 Options\nVideo Filters\nAspect Ratio\nFPS\
                         \nPreset\nProfile\nTune\nAudio Codec\
                         \nAudio Channels\nAudio Rate\nAudio bit-rate\
                         \nBit per Sample\nAudio Normalization\
                         \nSelected Input Audio index\nAudio Output Map index\
                         \nSubtitles streams index\nTime selection"
                         ))
            dictions = ("\n\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\
                        \n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\
                        \n%s\n%s" % (numfile,
                                     cmd_opt["WebOptim"],
                                     cmd_opt["Passing"],
                                     outputformat,
                                     cmd_opt["VidCmbxStr"],
                                     cmd_opt["VideoBitrate"],
                                     cmd_opt["CRF"],
                                     cmd_opt["MinRate"],
                                     cmd_opt["MaxRate"],
                                     cmd_opt["Bufsize"],
                                     '%s %s %s' % (cmd_opt["Deadline"],
                                                   cmd_opt["CpuUsed"],
                                                   cmd_opt["RowMthreading"],
                                                   ),
                                     cmd_opt["VFilters"],
                                     cmd_opt["AspectRatio"],
                                     cmd_opt["FPS"],
                                     cmd_opt["Preset"],
                                     '%s %s' % (cmd_opt["Profile"],
                                                cmd_opt["Level"],
                                                ),
                                     cmd_opt["Tune"],
                                     cmd_opt["AudioCodStr"],
                                     cmd_opt["AudioChannel"][0],
                                     cmd_opt["AudioRate"][0],
                                     cmd_opt["AudioBitrate"][0],
                                     cmd_opt["AudioDepth"][0],
                                     normalize,
                                     self.cmb_A_inMap.GetValue(),
                                     self.cmb_A_outMap.GetValue(),
                                     self.cmb_Submap.GetValue(),
                                     time,
                                     ))
        return formula, dictions
# ------------------------------------------------------------------#

    def Addprof(self):
        """
        Storing profile or save new preset for vinc application
        with the same current setting.

        """
        self.update_allentries()
        if self.cmb_Media.GetValue() == 'Video':
            if self.rdbx_normalize.GetSelection() == 3:  # EBU
                parameters = self.video_ebu_2pass([], [], 0, 'save as profile')
            else:
                parameters = self.video_stdProc([], [], 0, 'save as profile')

        elif self.cmb_Media.GetValue() == 'Audio':
            if self.rdbx_normalize.GetSelection() == 3:  # EBU
                parameters = self.audio_ebu_2pass([], [], 0, 'save as profile')
            else:
                parameters = self.audio_stdProc([], [], 0, 'save as profile')

        with wx.FileDialog(None, _("Videomass: Choose a preset to "
                                   "storing new profile"),
                           defaultDir=os.path.join(DIR_CONF, 'presets'),
                           wildcard="Videomass presets (*.prst;)|*.prst;",
                           style=wx.FD_OPEN |
                           wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            filename = os.path.splitext(fileDialog.GetPath())[0]

            t = _('Videomass: Create a new profile')

        prstdialog = presets_addnew.MemPresets(self,
                                               'addprofile',
                                               os.path.basename(filename),
                                               parameters,
                                               t
                                               )
        ret = prstdialog.ShowModal()
