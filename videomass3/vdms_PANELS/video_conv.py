# -*- coding: UTF-8 -*-

#########################################################
# FileName: video_conv.py
# Porpose: Intarface for video conversions
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Aug.02.2019, Sept.01.2019
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
from videomass3.vdms_IO.IO_tools import volumeDetectProcess
from videomass3.vdms_IO.IO_tools import stream_play
from videomass3.vdms_IO.filedir_control import inspect
from videomass3.vdms_DIALOGS.epilogue import Formula
from videomass3.vdms_DIALOGS import audiodialogs 
from videomass3.vdms_DIALOGS import presets_addnew
from videomass3.vdms_DIALOGS import dialog_tools
from videomass3.vdms_DIALOGS import shownormlist

"""
The following dictionaries are used for define the generated 
choices from the events. Some keys's values has not empty to 
accord with default parameters on program start. The cmd_opt 
contain all values need for ffmpeg command construction; the 
vcodec contain a tuple with two values (codec, container) and 
is useful to determine the video codec/container ratio and 
audio codec compatibility.
"""
cmd_opt = {"FormatChoice":"", "VideoFormat":"", "VideoCodec":"", 
           "ext_input":"", "Passing":"single", "InputDir":"", 
           "OutputDir":"",  "VideoSize":"", "VideoAspect":"", 
           "VideoRate":"", "Presets":"", "Profile":"", 
           "Tune":"", "Bitrate":"", "CRF":"", "Audio":"", 
           "AudioCodec":"", "AudioChannel":["",""], 
           "AudioRate":["",""], "AudioBitrate":["",""], 
           "AudioDepth":["",""], "Normalize":"", 
           "Deinterlace":"", "Interlace":"", "file":"", "Map":"-map 0", 
           "PixelFormat":"", "Orientation":["",""],"Crop":"",
           "Scale":"", "Setdar":"", "Setsar":"", "Denoiser":"", 
           "Filters":""
           }
vcodec = {
"AVI (XVID mpeg4)":("-vcodec mpeg4 -vtag xvid","avi"), 
"AVI (FFmpeg mpeg4)":("-vcodec mpeg4","avi"), 
"AVI (ITU h264)":("-vcodec libx264","avi"),
"MP4 (mpeg4)":("-vcodec mpeg4","mp4"), 
"MP4 (HQ h264/AVC)":("-vcodec libx264","mp4"), 
"M4V (HQ h264/AVC)":("-vcodec libx264","m4v"), 
"MKV (h264)":("-vcodec libx264","mkv"),
"OGG theora":("-vcodec libtheora","ogg"), 
"WebM (HTML5)":("-vcodec libvpx","webm"), 
"FLV (HQ h264/AVC)":("-vcodec libx264","flv"),
_("Copy Video Codec"):("","-c:v copy"),
_("Save Images From Video"):("save images",""),
            }
# set widget colours in some case with html rappresentetion:
azure = '#15a6a6' # rgb form (wx.Colour(217,255,255))
yellow = '#a29500'
red = '#ea312d'
orange = '#f28924'
greenolive = '#6aaf23'
ciano = '#61ccc7' # rgb 97, 204, 199

class Video_Conv(wx.Panel):
    """
    Interface panel for video conversions
    """
    def __init__(self, parent, ffmpeg_link, ffplay_link, threads, 
                 cpu_used, ffmpeg_loglev, ffplay_loglev, OS, iconplay,
                 iconreset, iconresize, iconcrop, iconrotate, icondeinterlace,
                 icondenoiser, iconanalyzes, iconsettings):

        wx.Panel.__init__(self, parent)

        # set attributes:
        self.parent = parent
        self.ffmpeg_link = ffmpeg_link
        self.ffplay_link = ffplay_link
        self.threads = threads
        self.cpu_used = cpu_used if not cpu_used == 'Disabled' else ''
        self.ffmpeg_loglev = ffmpeg_loglev
        self.ffplay_loglev = ffplay_loglev
        # set others attributes;
        self.file_sources = []
        self.file_destin = ''
        self.normdetails = []
        self.OS = OS
        
        self.panel_base = wx.Panel(self, wx.ID_ANY)
        self.notebook_1 = wx.Notebook(self.panel_base, wx.ID_ANY, style=0)
        self.notebook_1_pane_1 = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.cmbx_vidContainers = wx.ComboBox(self.notebook_1_pane_1, wx.ID_ANY,
                                  choices=[("AVI (XVID mpeg4)"), 
                                           ("AVI (FFmpeg mpeg4)"), 
                                           ("AVI (ITU h264)"), 
                                           ("MP4 (mpeg4)"), 
                                           ("MP4 (HQ h264/AVC)"), 
                                           ("M4V (HQ h264/AVC)"), 
                                           ("MKV (h264)"), 
                                           ("OGG theora"), 
                                           ("WebM (HTML5)"), 
                                           ("FLV (HQ h264/AVC)"),
                                           (_("Copy Video Codec")),
                                           (_("Save Images From Video"))], 
                            size=(200,-1),style=wx.CB_DROPDOWN | wx.CB_READONLY
                                               )
        self.sizer_combobox_formatv_staticbox = wx.StaticBox(
                                             self.notebook_1_pane_1, wx.ID_ANY, 
                                            (_("Video Container Selection"))
                                                             )
        self.sizer_dir_staticbox = wx.StaticBox(self.notebook_1_pane_1, 
                                   wx.ID_ANY, 
                                   (_('Improves low-quality export'))
                                                )
        self.ckbx_pass = wx.CheckBox(self.notebook_1_pane_1, wx.ID_ANY, 
                                     (_("2-pass encoding"))
                                     )
        self.ckbx_pass.SetValue(False) # setto in modo spento

        self.sizer_automations_staticbox = wx.StaticBox(self.notebook_1_pane_1, 
                                                        wx.ID_ANY, ("")
                                                        )
        self.spin_ctrl_bitrate = wx.SpinCtrl(self.notebook_1_pane_1, wx.ID_ANY, 
        "1500", min=0, max=25000, style=wx.TE_PROCESS_ENTER
        )
        self.sizer_bitrate_staticbox = wx.StaticBox(self.notebook_1_pane_1, 
        wx.ID_ANY, (_("Video Bit-Rate Value"))
        )
        self.slider_CRF = wx.Slider(self.notebook_1_pane_1, wx.ID_ANY, 1, 0, 51, 
        style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
        )
        self.sizer_crf_staticbox = wx.StaticBox(self.notebook_1_pane_1, 
        wx.ID_ANY, (_("Video CRF Value"))
        )
        self.notebook_1_pane_2 = wx.Panel(self.notebook_1, wx.ID_ANY)
        resizebmp = wx.Bitmap(iconresize, wx.BITMAP_TYPE_ANY)
        self.btn_videosize = GB.GradientButton(self.notebook_1_pane_2,
                                               size=(-1,25),
                                               bitmap=resizebmp,
                                               label=_("Resize"))
        self.btn_videosize.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                        foregroundcolour=wx.Colour(28,28,28))
        self.btn_videosize.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_videosize.SetBottomStartColour(wx.Colour(205, 235, 222))
        self.btn_videosize.SetTopStartColour(wx.Colour(205, 235, 222))
        self.btn_videosize.SetTopEndColour(wx.Colour(205, 235, 222))
        cropbmp = wx.Bitmap(iconcrop, wx.BITMAP_TYPE_ANY)
        self.btn_crop = GB.GradientButton(self.notebook_1_pane_2,
                                          size=(-1,25),
                                          bitmap=cropbmp,
                                          label=_("Crop Dimension"))
        self.btn_crop.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                        foregroundcolour=wx.Colour(28,28,28))
        self.btn_crop.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_crop.SetBottomStartColour(wx.Colour(205, 235, 222))
        self.btn_crop.SetTopStartColour(wx.Colour(205, 235, 222))
        self.btn_crop.SetTopEndColour(wx.Colour(205, 235, 222))
        rotatebmp = wx.Bitmap(iconrotate, wx.BITMAP_TYPE_ANY)
        self.btn_rotate = GB.GradientButton(self.notebook_1_pane_2,
                                            size=(-1,25),
                                            bitmap=rotatebmp,
                                            label=_("Rotation"))
        self.btn_rotate.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                        foregroundcolour=wx.Colour(28,28,28))
        self.btn_rotate.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_rotate.SetBottomStartColour(wx.Colour(205, 235, 222))
        self.btn_rotate.SetTopStartColour(wx.Colour(205, 235, 222))
        self.btn_rotate.SetTopEndColour(wx.Colour(205, 235, 222))
        deintbmp = wx.Bitmap(icondeinterlace, wx.BITMAP_TYPE_ANY)
        self.btn_lacing = GB.GradientButton(self.notebook_1_pane_2,
                                            size=(-1,25),
                                            bitmap=deintbmp,
                                            label=_("De/Interlace"))
        self.btn_lacing.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                        foregroundcolour=wx.Colour(28,28,28))
        self.btn_lacing.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_lacing.SetBottomStartColour(wx.Colour(205, 235, 222))
        self.btn_lacing.SetTopStartColour(wx.Colour(205, 235, 222))
        self.btn_lacing.SetTopEndColour(wx.Colour(205, 235, 222))
        denoiserbmp = wx.Bitmap(icondenoiser, wx.BITMAP_TYPE_ANY)
        self.btn_denois = GB.GradientButton(self.notebook_1_pane_2,
                                            size=(-1,25),
                                            bitmap=denoiserbmp,
                                            label="Denoisers")
        self.btn_denois.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                        foregroundcolour=wx.Colour(28,28,28))
        self.btn_denois.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_denois.SetBottomStartColour(wx.Colour(205, 235, 222))
        self.btn_denois.SetTopStartColour(wx.Colour(205, 235, 222))
        self.btn_denois.SetTopEndColour(wx.Colour(205, 235, 222))
        playbmp = wx.Bitmap(iconplay, wx.BITMAP_TYPE_ANY)
        self.btn_preview = GB.GradientButton(self.notebook_1_pane_2,
                                             size=(-1,25),
                                             bitmap=playbmp, 
                                             )
        self.btn_preview.SetBaseColours(startcolour=wx.Colour(158,201,232))
        self.btn_preview.SetBottomEndColour(wx.Colour(97, 204, 153))
        self.btn_preview.SetBottomStartColour(wx.Colour(97, 204, 153))
        self.btn_preview.SetTopStartColour(wx.Colour(97, 204, 153))
        self.btn_preview.SetTopEndColour(wx.Colour(97, 204, 153))
        resetbmp = wx.Bitmap(iconreset, wx.BITMAP_TYPE_ANY)
        self.btn_reset = GB.GradientButton(self.notebook_1_pane_2,
                                             size=(-1,25),
                                             bitmap=resetbmp, 
                                             )
        self.btn_reset.SetBaseColours(startcolour=wx.Colour(158,201,232))
        self.btn_reset.SetBottomEndColour(wx.Colour(97, 204, 153))
        self.btn_reset.SetBottomStartColour(wx.Colour(97, 204, 153))
        self.btn_reset.SetTopStartColour(wx.Colour(97, 204, 153))
        self.btn_reset.SetTopEndColour(wx.Colour(97, 204, 153))
        
        self.sizer_videosize_staticbox = wx.StaticBox(self.notebook_1_pane_2, 
                                         wx.ID_ANY, (_("Filters Section"))
                                                      )
        self.cmbx_Vaspect = wx.ComboBox(self.notebook_1_pane_2, wx.ID_ANY,
        size=(200, -1), choices=[("Default "), ("4:3"), ("16:9")], 
        style=wx.CB_DROPDOWN | wx.CB_READONLY
                                        )
        self.sizer_videoaspect_staticbox = wx.StaticBox(self.notebook_1_pane_2, 
                                        wx.ID_ANY, (_("Video Aspect"))
                                        )
        self.cmbx_vrate = wx.ComboBox(self.notebook_1_pane_2, wx.ID_ANY, 
        choices=[("Default "), ("25 fps (50i) PAL"), ("29.97 fps (60i) NTSC"),
        ("30 fps (30p) Progessive"),("0.2 fps for images"), ("0.5 fps for images"),
        ("1 fps for images"), ("1.5 fps for images"), ("2 fps for images")], 
                                      style=wx.CB_DROPDOWN | wx.CB_READONLY
                                      )
        self.sizer_videorate_staticbox = wx.StaticBox(self.notebook_1_pane_2, 
                                        wx.ID_ANY, (_("Video Rate"))
                                                    )
        self.notebook_1_pane_3 = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.rdb_a = wx.RadioBox(self.notebook_1_pane_3, wx.ID_ANY, (
                                 _("Audio Codec Selecting")), 
                            choices=[(_("Default (managed by FFmpeg)")), 
                                    ("Wav (Raw, No_MultiChannel)"), 
                                    ("Flac (Lossless, No_MultiChannel)"), 
                                    ("Aac (Lossy, MultiChannel)"), 
                                    ("Alac (Lossless, m4v, No_MultiChannel)"),
                                    ("Ac3 (Lossy, MultiChannel)"), 
                                    ("Ogg (Lossy, No_MultiChannel)"),
                                    ("Mp3 (Lossy, No_MultiChannel)"), 
                                    (_("Try to copy audio source")),
                                    (_("No audio stream (silent)"))], 
                                    majorDimension=2, style=wx.RA_SPECIFY_COLS
                                    )
        self.rdb_a.EnableItem(0,enable=True),self.rdb_a.EnableItem(1,enable=True)
        self.rdb_a.EnableItem(2,enable=True),self.rdb_a.EnableItem(3,enable=True)
        self.rdb_a.EnableItem(4,enable=False),self.rdb_a.EnableItem(5,enable=True)
        self.rdb_a.EnableItem(6,enable=True),self.rdb_a.EnableItem(7,enable=True)
        self.rdb_a.EnableItem(8,enable=True),self.rdb_a.EnableItem(9,enable=True)
        self.rdb_a.SetSelection(0)
        self.ckbx_a_normalize = wx.CheckBox(self.notebook_1_pane_3, 
                      wx.ID_ANY, (_("Audio Normalization"))
                                )
        analyzebmp = wx.Bitmap(iconanalyzes, wx.BITMAP_TYPE_ANY)
        self.btn_analyzes = GB.GradientButton(self.notebook_1_pane_3,
                                            size=(-1,25),
                                            bitmap=analyzebmp,
                                            label=_("Volumedetect"))
        self.btn_analyzes.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(165,165, 165))
        self.btn_analyzes.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_analyzes.SetBottomStartColour(wx.Colour(205, 235, 222))
        self.btn_analyzes.SetTopStartColour(wx.Colour(205, 235, 222))
        self.btn_analyzes.SetTopEndColour(wx.Colour(205, 235, 222))
        
        self.btn_details = GB.GradientButton(self.notebook_1_pane_3,
                                            #size=(-1,25),
                                            #bitmap=analyzebmp,
                                            label=_("Details list"))
        self.btn_details.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(165,165, 165))
        self.btn_details.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_details.SetBottomStartColour(wx.Colour(205, 235, 222))
        self.btn_details.SetTopStartColour(wx.Colour(205, 235, 222))
        self.btn_details.SetTopEndColour(wx.Colour(205, 235, 222))
        
        self.label_normalize = wx.StaticText(self.notebook_1_pane_3, wx.ID_ANY, 
                                    (_("Max peak level threshold  "))
                                    )
        self.spin_ctrl_audionormalize = FS.FloatSpin(self.notebook_1_pane_3, 
            wx.ID_ANY, min_val=-99.0, max_val=0.0, increment=1.0, value=-1.0, 
                        agwStyle=FS.FS_LEFT, size=(-1,-1)
                        )
        self.spin_ctrl_audionormalize.SetFormat("%f")
        self.spin_ctrl_audionormalize.SetDigits(1)
        
        setbmp = wx.Bitmap(iconsettings, wx.BITMAP_TYPE_ANY)
        self.btn_aparam = GB.GradientButton(self.notebook_1_pane_3,
                                           size=(-1,25),
                                           bitmap=setbmp,
                                           label=_("Audio Options"))
        self.btn_aparam.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(165,165, 165))
        self.btn_aparam.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_aparam.SetBottomStartColour(wx.Colour(205, 235, 222))
        self.btn_aparam.SetTopStartColour(wx.Colour(205, 235, 222))
        self.btn_aparam.SetTopEndColour(wx.Colour(205, 235, 222))
        self.txt_audio_options = wx.TextCtrl(self.notebook_1_pane_3, wx.ID_ANY, 
                                       size=(300,-1), style=wx.TE_READONLY)
        
        self.notebook_1_pane_4 = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.rdb_h264preset = wx.RadioBox(self.notebook_1_pane_4, wx.ID_ANY, (
                                    "presets"), choices=[("Disabled"), 
                                                ("ultrafast"), ("superfast"), 
                                                ("veryfast"), ("faster"), 
                                                ("fast"), ("medium"), 
                                                ("slow"), ("slower"), 
                                                ("veryslow"), ("placebo")],  
                                majorDimension=0, style=wx.RA_SPECIFY_ROWS
                                            )
        self.rdb_h264profile = wx.RadioBox(self.notebook_1_pane_4, wx.ID_ANY, (
                                    "Profile"), choices=[("Disabled"), 
                                                    ("baseline"), ("main"), 
                                                    ("high"), ("high10"), 
                                                    ("high444")], 
                                majorDimension=0, style=wx.RA_SPECIFY_ROWS
                                            )
        self.rdb_h264tune = wx.RadioBox(self.notebook_1_pane_4, wx.ID_ANY, (
                                        "Tune"), choices=[("Disabled"), 
                                                ("film"), ("animation"),
                                                ("grain"), ("stillimage"), 
                                                ("psnr"), ("ssim"), 
                                                ("fastecode"), ("zerolatency")], 
                                    majorDimension=0, style=wx.RA_SPECIFY_ROWS
                                         )
        #----------------------Build Layout----------------------#
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(2, 1, 0, 0)
        sizer_pane4_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_pane4_base = wx.GridSizer(1, 3, 0, 0)
        sizer_pane3_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_pane3_base = wx.FlexGridSizer(2, 2, 0, 0)
        sizer_pane3_audio_column2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_in_column2 = wx.FlexGridSizer(4, 2, 0, 0)
        #sizer_pane3_audio_column1 = wx.BoxSizer(wx.VERTICAL)
        sizer_pane2_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_pane2_base = wx.GridSizer(1, 2, 0, 0)
        grid_sizer_1 = wx.GridSizer(2, 1, 0, 0)
        self.sizer_videorate_staticbox.Lower()
        sizer_videorate = wx.StaticBoxSizer(self.sizer_videorate_staticbox, 
                                            wx.VERTICAL)
        self.sizer_videoaspect_staticbox.Lower()
        sizer_videoaspect = wx.StaticBoxSizer(self.sizer_videoaspect_staticbox, 
                                              wx.VERTICAL)
        self.sizer_videosize_staticbox.Lower()
        sizer_2 = wx.StaticBoxSizer(self.sizer_videosize_staticbox, wx.VERTICAL)
        grid_sizer_2 = wx.GridSizer(6, 2, 0, 0)
        grid_sizer_pane1_base = wx.GridSizer(1, 3, 0, 0)
        grid_sizer_pane1_right = wx.GridSizer(2, 1, 0, 0)
        self.sizer_crf_staticbox.Lower()
        sizer_crf = wx.StaticBoxSizer(self.sizer_crf_staticbox, wx.VERTICAL)
        self.sizer_bitrate_staticbox.Lower()
        sizer_bitrate = wx.StaticBoxSizer(self.sizer_bitrate_staticbox, wx.VERTICAL)
        self.sizer_automations_staticbox.Lower()
        sizer_automations = wx.StaticBoxSizer(self.sizer_automations_staticbox, 
                                              wx.VERTICAL)
        grid_sizer_automations = wx.GridSizer(3, 1, 0, 0)

        grid_sizer_pane1_left = wx.GridSizer(2, 1, 0, 0)
        self.sizer_dir_staticbox.Lower()
        sizer_dir = wx.StaticBoxSizer(self.sizer_dir_staticbox, wx.VERTICAL)
        grid_sizer_dir = wx.GridSizer(1, 1, 0, 0)# vuoto
        self.sizer_combobox_formatv_staticbox.Lower()
        sizer_combobox_formatv = wx.StaticBoxSizer(
                                        self.sizer_combobox_formatv_staticbox, 
                                        wx.VERTICAL)
        sizer_combobox_formatv.Add(self.cmbx_vidContainers, 0, 
                                   wx.ALL |
                                   wx.ALIGN_CENTER_HORIZONTAL | 
                                   wx.ALIGN_CENTER_VERTICAL, 20
                                   )
        grid_sizer_pane1_left.Add(sizer_combobox_formatv, 1, wx.ALL | 
                                                             wx.EXPAND, 15
                                                             )
        grid_sizer_dir.Add(self.ckbx_pass, 0, wx.ALL | 
                                              wx.ALIGN_CENTER_HORIZONTAL | 
                                              wx.ALIGN_CENTER_VERTICAL, 20
                                              )
        sizer_dir.Add(grid_sizer_dir, 1, wx.EXPAND, 0)
        grid_sizer_pane1_left.Add(sizer_dir, 1, wx.ALL | wx.EXPAND, 15)
        grid_sizer_pane1_base.Add(grid_sizer_pane1_left, 1, wx.EXPAND, 0)

        sizer_automations.Add(grid_sizer_automations, 1, wx.EXPAND, 0)
        grid_sizer_pane1_base.Add(sizer_automations, 1, wx.ALL | wx.EXPAND, 15)
        sizer_bitrate.Add(self.spin_ctrl_bitrate, 0, wx.ALL| 
                                                     wx.ALIGN_CENTER_HORIZONTAL| 
                                                     wx.ALIGN_CENTER_VERTICAL, 
                                                     20
                                                     )
        grid_sizer_pane1_right.Add(sizer_bitrate, 1, wx.ALL | wx.EXPAND, 15)
        sizer_crf.Add(self.slider_CRF, 0, wx.ALL | 
                                          wx.ALIGN_CENTER_HORIZONTAL | 
                                          wx.ALIGN_CENTER_VERTICAL, 20
                                          )
        grid_sizer_pane1_right.Add(sizer_crf, 1, wx.ALL | wx.EXPAND, 15)
        grid_sizer_pane1_base.Add(grid_sizer_pane1_right, 1, wx.EXPAND, 0)
        self.notebook_1_pane_1.SetSizer(grid_sizer_pane1_base)
        grid_sizer_2.Add(self.btn_videosize, 0, wx.ALL |
                                                wx.ALIGN_CENTER_HORIZONTAL, 5
                                                )
        grid_sizer_2.Add(self.btn_crop, 0, wx.ALL |
                                           wx.ALIGN_CENTER_HORIZONTAL, 5
                                           )
        grid_sizer_2.Add(self.btn_rotate, 0, wx.ALL | 
                                             wx.ALIGN_CENTER_HORIZONTAL, 5
                                             )
        grid_sizer_2.Add(self.btn_lacing, 0, wx.ALL | 
                                             wx.ALIGN_CENTER_HORIZONTAL, 5
                                             )
        grid_sizer_2.Add(self.btn_denois, 0, wx.ALL | 
                                             wx.ALIGN_CENTER_HORIZONTAL, 5
                                             )
        grid_sizer_2.Add((20, 20), 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        grid_sizer_2.Add(self.btn_preview, 0, wx.ALL | 
                                              wx.ALIGN_CENTER_HORIZONTAL, 5
                                              )
        grid_sizer_2.Add(self.btn_reset, 0, wx.ALL | 
                                            wx.ALIGN_CENTER_HORIZONTAL, 5
                                            )
        sizer_2.Add(grid_sizer_2, 1, wx.EXPAND, 0)
        grid_sizer_pane2_base.Add(sizer_2, 1, wx.ALL | wx.EXPAND, 15)
        #----------------

        sizer_videoaspect.Add(self.cmbx_Vaspect, 0, wx.ALL | 
                                                    wx.ALIGN_CENTER_HORIZONTAL, 
                                                    15
                                                    )
        grid_sizer_1.Add(sizer_videoaspect, 1, wx.ALL | wx.EXPAND, 15)
        sizer_videorate.Add(self.cmbx_vrate, 0, wx.ALL | 
                                                wx.ALIGN_CENTER_HORIZONTAL, 15
                                                )
        grid_sizer_1.Add(sizer_videorate, 1, wx.ALL | wx.EXPAND, 15)
        grid_sizer_pane2_base.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        sizer_pane2_base.Add(grid_sizer_pane2_base, 1, wx.EXPAND, 0)
        self.notebook_1_pane_2.SetSizer(sizer_pane2_base)
        
        grid_sizer_pane3_base.Add(self.rdb_a, 0, wx.ALL | wx.EXPAND, 15)
        grid_sizer_in_column2.Add(self.ckbx_a_normalize, 0, wx.TOP, 5)
        grid_sizer_in_column2.Add((20, 20), 0, wx.EXPAND | wx.TOP, 5)
        grid_sizer_in_column2.Add(self.btn_analyzes, 0, wx.TOP, 10)
        grid_sizer_in_column2.Add((20, 20), 0, wx.EXPAND | wx.TOP, 5)
        grid_sizer_in_column2.Add(self.btn_details, 0, wx.TOP, 10)
        grid_sizer_in_column2.Add((20, 20), 0, wx.EXPAND | wx.TOP, 5)
        grid_sizer_in_column2.Add(self.label_normalize, 0, wx.TOP, 10)
        grid_sizer_in_column2.Add(self.spin_ctrl_audionormalize, 0, wx.TOP, 5)
        sizer_pane3_audio_column2.Add(grid_sizer_in_column2, 1, wx.ALL, 15)
        grid_sizer_pane3_base.Add(sizer_pane3_audio_column2, 1, wx.ALL, 0)
        grid_a_param = wx.FlexGridSizer(1, 2, 0, 0)
        grid_a_param.Add(self.btn_aparam, 0, wx.ALL|
                                             wx.ALIGN_CENTER_VERTICAL, 5
                                             )
        grid_a_param.Add(self.txt_audio_options, 0, wx.ALL|
                                                    wx.ALIGN_CENTER_VERTICAL, 5
                                                    )
        grid_sizer_pane3_base.Add(grid_a_param, 0, wx.ALL, 10)
        sizer_pane3_base.Add(grid_sizer_pane3_base, 1, 
                                        wx.ALL | 
                                        wx.ALIGN_CENTER_HORIZONTAL | 
                                        wx.ALIGN_CENTER_VERTICAL, 15
                                        )
        self.notebook_1_pane_3.SetSizer(sizer_pane3_base)
        
        
        grid_sizer_pane4_base.Add(self.rdb_h264preset, 0, 
                                  wx.ALL | 
                                  wx.ALIGN_CENTER_HORIZONTAL | 
                                  wx.ALIGN_CENTER_VERTICAL, 15
                                  )
        grid_sizer_pane4_base.Add(self.rdb_h264profile, 0, 
                                  wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | 
                                  wx.ALIGN_CENTER_VERTICAL, 15
                                  )
        grid_sizer_pane4_base.Add(self.rdb_h264tune, 0, 
                                  wx.ALL | 
                                  wx.ALIGN_CENTER_HORIZONTAL | 
                                  wx.ALIGN_CENTER_VERTICAL, 15
                                  )
        sizer_pane4_base.Add(grid_sizer_pane4_base, 1, wx.EXPAND, 0)
        self.notebook_1_pane_4.SetSizer(sizer_pane4_base)
        self.notebook_1.AddPage(self.notebook_1_pane_1, (_("Video Container")))
        self.notebook_1.AddPage(self.notebook_1_pane_2, (_("Video Settings")))
        self.notebook_1.AddPage(self.notebook_1_pane_3, (_("Audio Settings")))
        self.notebook_1.AddPage(self.notebook_1_pane_4, (_("H.264/X.264 Options")))
        grid_sizer_base.Add(self.notebook_1, 1, wx.ALL | wx.EXPAND, 5)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()
        
        #----------------------Set Properties----------------------#
        self.cmbx_vidContainers.SetToolTip(_("Video container that will " 
                                             "be used in the conversion. "
                                             "When the container is changed, " 
                                             "all settings are restored."))
        self.cmbx_vidContainers.SetSelection(6)


        self.ckbx_pass.SetToolTip(_("It can improve the video quality, "
                                    "but takes longer. Use it with high "
                                    "video compression.")
                                                 )
        self.spin_ctrl_bitrate.SetToolTip(_("The bit rate determines the "
                                            "quality and the final video "
                                            "size. A larger value correspond "
                                            "to greater quality and size of "
                                            "the file.")
                                                 )
        self.slider_CRF.SetValue(23)# this is a default rate
        self.slider_CRF.SetMinSize((230, -1))
        self.slider_CRF.SetToolTip(_("CRF (constant rate factor) Affects "
                                 "the quality of the final video. Used for "
                                 "h264 codec on single pass only, 2-pass "
                                 "encoding swich to bitrate. With lower "
                                 "values the quality is higher and a larger "
                                 "file size.")
                                          )
        self.btn_preview.SetToolTip(_("Try the filters you've enabled "
                                          "by playing a video preview")
                                          )
        self.btn_reset.SetToolTip(_("Clear all enabled filters "))
        self.cmbx_Vaspect.SetSelection(0)
        self.cmbx_Vaspect.SetToolTip(_("Video aspect (Aspect Ratio) "
                        "is the video width and video height ratio. "
                        "Leave on 'Default' to copy the original settings."
                                                ))
        self.cmbx_vrate.SetSelection(0)
        self.cmbx_vrate.SetToolTip(_("Video Rate: A any video consists "
                    "of images displayed as frames, repeated a given number "
                    "of times per second. In countries are 30 NTSC, PAL "
                    "countries (like Italy) are 25. Leave on 'Default' "
                    "to copy the original settings.")
                                            )
        
        self.ckbx_a_normalize.SetToolTip(_("Performs audio normalization "
                                           "on the video audio stream"))
        self.btn_analyzes.SetToolTip(_("Calculates the maximum and average "
                                       "peak level of audio streams expressed "
                                       "in dB values"))
        #self.spin_ctrl_audionormalize.SetMinSize((70, -1))
        self.spin_ctrl_audionormalize.SetToolTip(_("Threshold for the "
                                "maximum peak level in dB values. The default " 
                                "setting is -1.0 dB and is good for most of "
                                "the processes"))
        
        self.rdb_a.SetToolTip(_("Choose an audio codec. Some audio codecs "
                                "are disabled for certain video containers"))
        self.rdb_h264preset.SetToolTip("presets h.264")
        self.rdb_h264preset.SetSelection(0)
        self.rdb_h264profile.SetToolTip("profile h.264")
        self.rdb_h264profile.SetSelection(0)
        self.rdb_h264tune.SetToolTip("tune h.264")
        self.rdb_h264tune.SetSelection(0)
        self.notebook_1_pane_4.SetToolTip(_("The parameters on this tab "
                        "are enabled only for the video-codec h.264."))

        #----------------------Binding (EVT)----------------------#
        """
        Note: wx.EVT_TEXT_ENTER é diverso da wx.EVT_TEXT . Il primo é sensibile
        agli input di tastiera, il secondo é sensibile agli input di tastiera
        ma anche agli "append"
        """
        #self.Bind(wx.EVT_COMBOBOX, self.vidContainers, self.cmbx_vidContainers)
        self.cmbx_vidContainers.Bind(wx.EVT_COMBOBOX, self.vidContainers)
        self.Bind(wx.EVT_CHECKBOX, self.on_Pass, self.ckbx_pass)
        self.Bind(wx.EVT_SPINCTRL, self.on_Bitrate, self.spin_ctrl_bitrate)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.on_Crf, self.slider_CRF)
        self.Bind(wx.EVT_BUTTON, self.on_Enable_vsize, self.btn_videosize)
        self.Bind(wx.EVT_BUTTON, self.on_Enable_crop, self.btn_crop)
        self.Bind(wx.EVT_BUTTON, self.on_Enable_rotate, self.btn_rotate)
        self.Bind(wx.EVT_BUTTON, self.on_Enable_lacing, self.btn_lacing)
        self.Bind(wx.EVT_BUTTON, self.on_Enable_denoiser, self.btn_denois)
        self.Bind(wx.EVT_BUTTON, self.on_FiltersPreview, self.btn_preview)
        self.Bind(wx.EVT_BUTTON, self.on_FiltersClear, self.btn_reset)
        self.Bind(wx.EVT_COMBOBOX, self.on_Vaspect, self.cmbx_Vaspect)
        self.Bind(wx.EVT_COMBOBOX, self.on_Vrate, self.cmbx_vrate)
        self.Bind(wx.EVT_RADIOBOX, self.on_AudioFormats, self.rdb_a)
        self.Bind(wx.EVT_BUTTON, self.on_AudioParam, self.btn_aparam)
        self.Bind(wx.EVT_CHECKBOX, self.onNormalize, self.ckbx_a_normalize)
        self.Bind(wx.EVT_BUTTON, self.on_Audio_analyzes, self.btn_analyzes)
        self.Bind(wx.EVT_RADIOBOX, self.on_h264Presets, self.rdb_h264preset)
        self.Bind(wx.EVT_RADIOBOX, self.on_h264Profiles, self.rdb_h264profile)
        self.Bind(wx.EVT_RADIOBOX, self.on_h264Tunes, self.rdb_h264tune)
        self.Bind(wx.EVT_BUTTON, self.on_Show_normlist, self.btn_details)
        #self.Bind(wx.EVT_CLOSE, self.Quiet) # controlla la x di chiusura

    #----------------------used methods----------------------#
        # initialize default layout:
        cmd_opt["FormatChoice"] = "MKV (h264)"
        cmd_opt["VideoFormat"] = "mkv"
        cmd_opt["VideoCodec"] = "-vcodec libx264"
        self.default_videosettings()
        self.UI_set()
        self.audio_default()
        self.normalize_default()

    def default_videosettings(self):
        self.cmbx_vrate.SetSelection(0),self.cmbx_Vaspect.SetSelection(0)
        self.cmbx_Vaspect.Enable()
        cmd_opt["VideoAspect"] = ""
        cmd_opt["VideoRate"] = ""
        #self.rdbx_interlace.Hide() # TODO QUESTO E' IN SVILUPPO
        
    #-------------------------------------------------------------------#
    def UI_set(self):
        """
        Update all the GUI widgets based on the choices made by the user.
        """
        if cmd_opt["VideoCodec"] == "-vcodec libx264":
            self.notebook_1_pane_4.Enable(), self.btn_videosize.Enable(), 
            self.btn_crop.Enable(), self.btn_rotate.Enable(), 
            self.btn_lacing.Enable(), self.btn_denois.Enable(), 
            self.btn_preview.Enable(), self.ckbx_pass.Enable(),
            self.on_Pass(self)
            
        elif cmd_opt["VideoCodec"] == "-c:v copy":
            self.spin_ctrl_bitrate.Disable(), self.btn_videosize.Disable(), 
            self.btn_crop.Disable(), self.btn_rotate.Disable(), 
            self.btn_lacing.Disable(), self.btn_denois.Disable(), 
            self.btn_preview.Disable(), self.notebook_1_pane_4.Disable(), 
            self.ckbx_pass.Disable(), self.ckbx_pass.SetValue(False)
            self.rdb_a.EnableItem(4,enable=True)# se disable lo abilita
            self.slider_CRF.Disable(), self.rdb_h264preset.SetSelection(0)
            self.rdb_h264profile.SetSelection(0)
            self.rdb_h264tune.SetSelection(0)
            self.on_h264Presets(self), self.on_h264Profiles(self)
            self.on_h264Tunes(self)
        else: # all others containers that not use h264
            self.notebook_1_pane_4.Disable()
            self.rdb_h264preset.SetSelection(0)
            self.rdb_h264profile.SetSelection(0)
            self.rdb_h264tune.SetSelection(0)
            self.on_h264Presets(self), self.on_h264Profiles(self)
            self.on_h264Tunes(self), self.btn_videosize.Enable(), 
            self.btn_crop.Enable(), self.btn_rotate.Enable(), 
            self.btn_lacing.Enable(), self.btn_denois.Enable(), 
            self.btn_preview.Enable(), self.ckbx_pass.Enable(),
            self.on_Pass(self)
    #-------------------------------------------------------------------#
    def audio_default(self):
        """
        Set default audio parameters. This method is called on first run and
        if there is a change inthe  video container selection on the combobox
        """
        self.rdb_a.SetStringSelection(_("Default (managed by FFmpeg)"))
        cmd_opt["Audio"] = _("Default (managed by FFmpeg)")
        cmd_opt["AudioCodec"] = ""
        cmd_opt["AudioBitrate"] = ["",""]
        cmd_opt["AudioChannel"] = ["",""]
        cmd_opt["AudioRate"] = ["",""]
        cmd_opt["AudioDepth"] = ["",""]
        self.btn_aparam.Disable()
        self.btn_aparam.SetForegroundColour(wx.Colour(165,165, 165))
        self.btn_aparam.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.txt_audio_options.SetValue('')
        self.ckbx_a_normalize.Enable()
    #-------------------------------------------------------------------#
    def normalize_default(self):
        """
        Set default normalization parameters of the audio panel. This method 
        is called by preset_manager.switch_video_conv() on first run and
        switch in this panel, or if there are changing on dragNdrop panel,
        (when make a clear file list or append new file), or if change video 
        container in the combobox.
        """
        self.ckbx_a_normalize.SetValue(False)
        self.btn_analyzes.Disable() 
        self.btn_analyzes.SetForegroundColour(wx.Colour(165,165, 165))
        self.spin_ctrl_audionormalize.Disable()
        self.spin_ctrl_audionormalize.SetValue(-1.0)
        self.btn_details.Disable()
        self.btn_details.SetForegroundColour(wx.Colour(165,165, 165))
        self.label_normalize.Disable()
        cmd_opt["Normalize"] = ""
        del self.normdetails[:]
    
    #----------------------Event handler (callback)----------------------#
    #------------------------------------------------------------------#
    def vidContainers(self, event):
        """
        L'evento scelta nella combobox dei formati video scatena
        il setting ai valori predefiniti. Questo determina lo stato 
        di default ogni volta che si cambia codec video. Inoltre
        vengono abilitate o disabilitate funzioni dipendentemente
        dal tipo di codec scelto.
        """
        #### Audio settings panel
        self.audio_default() # reset audio radiobox and dict

        selected = self.cmbx_vidContainers.GetValue()
        print (vcodec[selected][0])
        
        if vcodec[selected][0] == "-vcodec libx264":
            cmd_opt["FormatChoice"] = "%s" % (selected)
            # avi,mkv,mp4,flv,etc.:
            cmd_opt['VideoFormat'] = "%s" % (vcodec[selected][1])
            cmd_opt["VideoCodec"] = "-vcodec libx264"
            cmd_opt["Bitrate"] = ""
            cmd_opt["CRF"] = ""
            self.parent.statusbar_msg("Output format: %s" % (
                                      cmd_opt['VideoFormat']),None)
            self.UI_set()
            
        elif vcodec[selected][0] == "":# copy video codec
            cmd_opt["Passing"] = "single"
            cmd_opt["FormatChoice"] = "%s" % (selected)
            # avi,mkv,mp4,flv,etc.:
            cmd_opt['VideoFormat'] = "%s" % ( vcodec[selected][1])
            cmd_opt["VideoCodec"] = "-c:v copy"
            self.parent.statusbar_msg("Output format: %s" % (
                                      cmd_opt['VideoFormat']),None)
            self.UI_set()
            
        elif vcodec[selected][0] == "save images":
            msg = (_('Tip: use the "Duration" tool, then try setting '
                     'the "Video Rate" to low values ​​0.2 fps / 0.5 fps'))
            self.parent.statusbar_msg(msg, greenolive)

            self.ckbx_pass.SetValue(False)
            self.UI_set()

        else:
            cmd_opt["FormatChoice"] = "%s" % (selected)
            # avi,mkv,mp4,flv,etc.:
            cmd_opt['VideoFormat'] = "%s" % (vcodec[selected][1])
            # -vcodec libx264 o altro:
            cmd_opt["VideoCodec"] = "%s" %(vcodec[selected][0])
            cmd_opt["Bitrate"] = ""
            cmd_opt["CRF"] = ""
            self.parent.statusbar_msg(_("Output format: %s") % (
                                    cmd_opt['VideoFormat']),None)
            self.UI_set()
            
        self.setAudioRadiobox(self)

    #------------------------------------------------------------------#
    def on_Pass(self, event):
        """
        enable or disable functionality for two pass encoding
        """
        if self.ckbx_pass.IsChecked():
            cmd_opt["Passing"] = "double"
            self.slider_CRF.Disable()
            self.spin_ctrl_bitrate.Enable()
            
        elif not self.ckbx_pass.IsChecked():
            cmd_opt["Passing"] = "single"
            if cmd_opt["VideoCodec"] == "-vcodec libx264":
                self.slider_CRF.Enable()
                self.spin_ctrl_bitrate.Disable()
            else:
                self.slider_CRF.Disable()
                self.spin_ctrl_bitrate.Enable()

        #self.parent.statusbar_msg("%s pass ready" % (
                                    #cmd_opt["Passing"]),None)

    #------------------------------------------------------------------#
    def on_Bitrate(self, event):
        """
        Reset CRF at empty (this depend if is h264 two-pass encoding
        or if not codec h264)
        """
        cmd_opt["CRF"] = ""
        cmd_opt["Bitrate"] = "-b:v %sk" % (self.spin_ctrl_bitrate.GetValue())

        
    #------------------------------------------------------------------#
    def on_Crf(self, event):
        """
        Reset bitrate at empty (this depend if is h264 codec)
        """
        cmd_opt["Bitrate"] = ""
        cmd_opt["CRF"] = "-crf %s" % self.slider_CRF.GetValue()
        
    #------------------------------------------------------------------#
    def on_FiltersPreview(self, event):
        """
        Showing a preview with applied filters only and Only the first 
        file in the list `self.file_sources` will be displayed
        """
        if not cmd_opt["Filters"]:
            wx.MessageBox(_("No filter enabled"), "Videomass: Info", 
                          wx.ICON_INFORMATION)
            return
        
        self.time_seq = self.parent.time_seq
        first_path = self.file_sources[0]
        
        stream_play(first_path, 
                    self.time_seq, 
                    self.ffplay_link, 
                    cmd_opt["Filters"], 
                    self.ffplay_loglev,
                    )
    #------------------------------------------------------------------#
    def on_FiltersClear(self, event):
        """
        Reset all enabled filters
        """
        if not cmd_opt["Filters"]:
            wx.MessageBox(_("No filter enabled"), "Videomass: Info", 
                          wx.ICON_INFORMATION)
            return
        else:
            cmd_opt['Crop'], cmd_opt["Orientation"] = "", ["",""]
            cmd_opt['Scale'], cmd_opt['Setdar'] = "",""
            cmd_opt['Setsar'], cmd_opt['Deinterlace'] = "",""
            cmd_opt['Interlace'], cmd_opt['Denoiser'] = "",""
            cmd_opt["Filters"] = ""
            self.btn_videosize.SetBottomEndColour(wx.Colour(205, 235, 222))
            self.btn_crop.SetBottomEndColour(wx.Colour(205, 235, 222))
            self.btn_denois.SetBottomEndColour(wx.Colour(205, 235, 222))
            self.btn_lacing.SetBottomEndColour(wx.Colour(205, 235, 222))
            self.btn_rotate.SetBottomEndColour(wx.Colour(205, 235, 222))
    #------------------------------------------------------------------#
    def video_filter_checker(self):
        """
        evaluates whether video filters (-vf) are enabled or not and 
        sorts them according to an appropriate syntax. If not filters strings,
        the -vf option will be removed
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
            cmd_opt['Filters'] = "-vf %s" % filters
        else:
            cmd_opt['Filters'] = ""
            
        print (cmd_opt["Filters"])
    #------------------------------------------------------------------#
    def on_Enable_vsize(self, event):
        """
        Enable or disable video/image resolution functionalities
        """
        sizing = dialog_tools.VideoResolution(self, 
                                              cmd_opt["Scale"],
                                              cmd_opt["Setdar"], 
                                              cmd_opt["Setsar"],
                                              )
        retcode = sizing.ShowModal()
        if retcode == wx.ID_OK:
            data = sizing.GetValue()
            if not data:
               self.btn_videosize.SetBottomEndColour(wx.Colour(205, 235, 222))
               cmd_opt["Setdar"] = ""
               cmd_opt["Setsar"] = ""
               cmd_opt["Scale"] = ""
            else:
                self.btn_videosize.SetBottomEndColour(wx.Colour(0, 240, 0))
                if 'scale' in data:
                    cmd_opt["Scale"] = data['scale']
                else:
                    cmd_opt["Scale"] = ""
                if 'setdar' in data:
                    cmd_opt['Setdar'] =  data['setdar']
                else:
                    cmd_opt['Setdar'] = ""
                if 'setsar' in data:
                    cmd_opt['Setsar'] =  data['setsar']
                else:
                    cmd_opt['Setsar'] = ""
            self.video_filter_checker()
        else:
            sizing.Destroy()
            return
    #-----------------------------------------------------------------#
    def on_Enable_rotate(self, event):
        """
        Show a setting dialog for video/image rotate
        """
        rotate = dialog_tools.VideoRotate(self, 
                                          cmd_opt["Orientation"][0],
                                          cmd_opt["Orientation"][1],
                                          )
        retcode = rotate.ShowModal()
        if retcode == wx.ID_OK:
            data = rotate.GetValue()
            cmd_opt["Orientation"][0] = data[0]# cmd option
            cmd_opt["Orientation"][1] = data[1]#msg
            if not data[0]:
                self.btn_rotate.SetBottomEndColour(wx.Colour(205, 235, 222))
            else:
                self.btn_rotate.SetBottomEndColour(wx.Colour(0, 240, 0))
            self.video_filter_checker()
        else:
            rotate.Destroy()
            return
    #------------------------------------------------------------------#
    def on_Enable_crop(self, event):
        """
        Show a setting dialog for video crop functionalities
        """
        crop = dialog_tools.VideoCrop(self, cmd_opt["Crop"])
        retcode = crop.ShowModal()
        if retcode == wx.ID_OK:
            data = crop.GetValue()
            if not data:
                self.btn_crop.SetBottomEndColour(wx.Colour(205, 235, 222))
                cmd_opt["Crop"] = ''
            else:
                self.btn_crop.SetBottomEndColour(wx.Colour(0, 240, 0))
                cmd_opt["Crop"] = 'crop=%s' % data
            self.video_filter_checker()
        else:
            crop.Destroy()
            return
    
    #------------------------------------------------------------------#
    def on_Enable_lacing(self, event):
        """
        Show a setting dialog for settings Deinterlace/Interlace filters
        """
        lacing = dialog_tools.Lacing(self, 
                                     cmd_opt["Deinterlace"],
                                     cmd_opt["Interlace"],
                                     )
        retcode = lacing.ShowModal()
        if retcode == wx.ID_OK:
            data = lacing.GetValue()
            if not data:
                self.btn_lacing.SetBottomEndColour(wx.Colour(205, 235, 222))
                cmd_opt["Deinterlace"] = ''
                cmd_opt["Interlace"] = ''
            else:
                self.btn_lacing.SetBottomEndColour(wx.Colour(0, 240, 0))
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
    #------------------------------------------------------------------#
    def on_Enable_denoiser(self, event):
        """
        Enable filters denoiser useful in some case, example when apply
        a deinterlace filter
        <https://askubuntu.com/questions/866186/how-to-get-good-quality-when-
        converting-digital-video>
        """
        den = dialog_tools.Denoisers(self, cmd_opt["Denoiser"])
        retcode = den.ShowModal()
        if retcode == wx.ID_OK:
            data = den.GetValue()
            if not data:
                self.btn_denois.SetBottomEndColour(wx.Colour(205, 235, 222))
                cmd_opt["Denoiser"] = ''
            else:
                self.btn_denois.SetBottomEndColour(wx.Colour(0, 240, 0))
                cmd_opt["Denoiser"] = data
            self.video_filter_checker()
        else:
            den.Destroy()
            return
    #------------------------------------------------------------------#
    def on_Vaspect(self, event):
        """
        Set aspect parameter (16:9, 4:3)
        """
        if self.cmbx_Vaspect.GetValue() == "Default ":
            cmd_opt["VideoAspect"] = ""
            
        else:
            cmd_opt["VideoAspect"] = '-aspect %s' % self.cmbx_Vaspect.GetValue()
            
    #------------------------------------------------------------------#
    def on_Vrate(self, event):
        """
        Set video rate parameter with fps values
        """
        val = self.cmbx_vrate.GetValue()
        if val == "Default ":
            cmd_opt["VideoRate"] = ""
        else:
            cmd_opt["VideoRate"] = "-r %s" % val.split(' ')[0]
            
    #------------------------------------------------------------------#
    def setAudioRadiobox(self, event):
        """
        set audio radiobox selection with compatible audio codec
        """
        cmb_value = self.cmbx_vidContainers.GetValue()
        
        if vcodec[cmb_value][1] == "avi":
            self.rdb_a.EnableItem(0,enable=True)## dafault
            self.rdb_a.EnableItem(1,enable=True)## wav
            self.rdb_a.EnableItem(2,enable=False)# flac
            self.rdb_a.EnableItem(3,enable=False)# aac
            self.rdb_a.EnableItem(4,enable=False) # alac
            self.rdb_a.EnableItem(5,enable=True) ## ac3
            self.rdb_a.EnableItem(6,enable=False) # ogg
            self.rdb_a.EnableItem(7,enable=True) ## mp3
            self.rdb_a.EnableItem(8,enable=True)# copy
            self.rdb_a.EnableItem(9,enable=True) # no audio
            self.rdb_a.SetSelection(0)
        elif vcodec[cmb_value][1] == "flv" or \
                                    vcodec[cmb_value][1] == "mp4":
            self.rdb_a.EnableItem(0,enable=True)## dafault #
            self.rdb_a.EnableItem(1,enable=False)## wav
            self.rdb_a.EnableItem(2,enable=False)# flac
            self.rdb_a.EnableItem(3,enable=True)# aac #
            self.rdb_a.EnableItem(4,enable=False) # alac
            self.rdb_a.EnableItem(5,enable=True) ## ac3 #
            self.rdb_a.EnableItem(6,enable=False) # ogg
            self.rdb_a.EnableItem(7,enable=True) ## mp3 #
            self.rdb_a.EnableItem(8,enable=True)# copy
            self.rdb_a.EnableItem(9,enable=True) # no audio
            self.rdb_a.SetSelection(0)
        elif vcodec[cmb_value][1] == "m4v":
            self.rdb_a.EnableItem(0,enable=True)# dafault #
            self.rdb_a.EnableItem(1,enable=False)# wav
            self.rdb_a.EnableItem(2,enable=False)# flac
            self.rdb_a.EnableItem(3,enable=True)# aac #
            self.rdb_a.EnableItem(4,enable=True)# alac #
            self.rdb_a.EnableItem(5,enable=False)# ac3
            self.rdb_a.EnableItem(6,enable=False)# ogg
            self.rdb_a.EnableItem(7,enable=False)# mp3
            self.rdb_a.EnableItem(8,enable=True)# copy
            self.rdb_a.EnableItem(9,enable=True) # no audio
            self.rdb_a.SetSelection(0)
        elif vcodec[cmb_value][1] == "mkv":
            self.rdb_a.EnableItem(0,enable=True)# dafault #
            self.rdb_a.EnableItem(1,enable=True)# wav
            self.rdb_a.EnableItem(2,enable=True)# flac
            self.rdb_a.EnableItem(3,enable=True)# aac #
            self.rdb_a.EnableItem(4,enable=False)# alac #
            self.rdb_a.EnableItem(5,enable=True)# ac3
            self.rdb_a.EnableItem(6,enable=True)# ogg
            self.rdb_a.EnableItem(7,enable=True)# mp3
            self.rdb_a.EnableItem(8,enable=True)# copy
            self.rdb_a.EnableItem(9,enable=True) # no audio
            self.rdb_a.SetSelection(0)
        elif vcodec[cmb_value][1] == "webm":
            self.rdb_a.EnableItem(0,enable=True)# dafault #
            self.rdb_a.EnableItem(1,enable=False)# wav
            self.rdb_a.EnableItem(2,enable=False)# flac
            self.rdb_a.EnableItem(3,enable=False)# aac #
            self.rdb_a.EnableItem(4,enable=False)# alac #
            self.rdb_a.EnableItem(5,enable=False)# ac3
            self.rdb_a.EnableItem(6,enable=True)# ogg
            self.rdb_a.EnableItem(7,enable=False)# mp3
            self.rdb_a.EnableItem(8,enable=True)# copy
            self.rdb_a.EnableItem(9,enable=True) # no audio
            self.rdb_a.SetSelection(0)
        elif vcodec[cmb_value][1] == "ogg":
            self.rdb_a.EnableItem(0,enable=True)# dafault #
            self.rdb_a.EnableItem(1,enable=False)# wav
            self.rdb_a.EnableItem(2,enable=True)# flac
            self.rdb_a.EnableItem(3,enable=False)# aac #
            self.rdb_a.EnableItem(4,enable=False)# alac #
            self.rdb_a.EnableItem(5,enable=False)# ac3
            self.rdb_a.EnableItem(6,enable=True)# ogg
            self.rdb_a.EnableItem(7,enable=False)# mp3
            self.rdb_a.EnableItem(8,enable=True)# copy
            self.rdb_a.EnableItem(9,enable=True) # no audio
            self.rdb_a.SetSelection(0)
            
    #------------------------------------------------------------------#
    def on_AudioFormats(self, event):
        """
        Qualche formato video supporta una limitata scelta di codec audio,
        quindi imposto le liste dei formati audio supportati in base al 
        formato video scelto
        """
        audioformat = self.rdb_a.GetStringSelection()

        def param(enablenormalization, enablebuttonparameters):
            cmd_opt["AudioBitrate"] = ["",""]
            cmd_opt["AudioChannel"] = ["",""]
            cmd_opt["AudioRate"] = ["",""]
            cmd_opt["AudioDepth"] = ["",""]

            if enablenormalization == 'yes':
                self.ckbx_a_normalize.Enable()
            else:
                self.ckbx_a_normalize.Disable()
            if enablebuttonparameters == 'yes':
                self.btn_aparam.Enable()
                self.txt_audio_options.SetValue('')
                self.btn_aparam.SetForegroundColour(wx.Colour(28,28,28))
                self.btn_aparam.SetBottomEndColour(wx.Colour(205, 235, 222))
            else:
                self.btn_aparam.Disable(), 
                self.txt_audio_options.SetValue('')
                self.btn_aparam.SetForegroundColour(wx.Colour(165,165,165))
                self.btn_aparam.SetBottomEndColour(wx.Colour(205, 235, 222))
            
        if audioformat == _("Default (managed by FFmpeg)"):
            self.audio_default()
            # reset parametrs
            self.ckbx_a_normalize.Enable()
        #--------------------------------------------#
        elif audioformat == "Wav (Raw, No_MultiChannel)":
            cmd_opt["AudioCodec"] = "-c:a pcm_s16le"
            cmd_opt["Audio"] = audioformat
            param('yes', 'yes')
            
        elif audioformat == "Flac (Lossless, No_MultiChannel)":
            cmd_opt["AudioCodec"] = "-c:a flac"
            cmd_opt["Audio"] = audioformat
            param('yes', 'yes')
            
        elif audioformat == "Aac (Lossy, MultiChannel)":
            cmd_opt["AudioCodec"] = "-c:a aac"
            cmd_opt["Audio"] = audioformat
            param('yes', 'yes')
            
        elif audioformat == "Alac (Lossless, m4v, No_MultiChannel)":
            cmd_opt["AudioCodec"] = "-c:a alac"
            cmd_opt["Audio"] = audioformat
            param('yes', 'yes')
            
        elif audioformat == "Ac3 (Lossy, MultiChannel)":
            cmd_opt["AudioCodec"] = "-c:a ac3"
            cmd_opt["Audio"] = audioformat
            param('yes', 'yes')
        
        elif audioformat == "Ogg (Lossy, No_MultiChannel)":
            cmd_opt["AudioCodec"] = "-c:a libvorbis"
            cmd_opt["Audio"] = audioformat
            param('yes', 'yes')
        
        elif audioformat == "Mp3 (Lossy, No_MultiChannel)":
            cmd_opt["AudioCodec"] = "-c:a libmp3lame"
            cmd_opt["Audio"] = audioformat
            param('yes', 'yes')

        elif audioformat == _("Try to copy audio source"):
            # reset parametrs
            self.normalize_default()
            self.rdb_a.SetSelection(8)
            param('no', 'no')
            cmd_opt["Audio"] = audioformat
            cmd_opt["AudioCodec"] = "-c:a copy"

        elif audioformat == _("No audio stream (silent)"):
            # reset parametrs
            self.normalize_default()
            self.rdb_a.SetSelection(9)
            param('no', 'no')
            cmd_opt["Audio"] = audioformat
            cmd_opt["AudioCodec"] = "-an"
            
    #-------------------------------------------------------------------#
    def on_AudioParam(self, event):
        """
        Check which audio codec has been set before starting the 
        corresponding dialog box
        """ 
        pcm = ["-c:a pcm_s16le","-c:a pcm_s24le","-c:a pcm_s32le",]

        if cmd_opt["AudioCodec"] in pcm:
            self.audio_dialog("wav", "Audio WAV Codec Parameters")
            
        elif cmd_opt["AudioCodec"] == "-c:a flac":
            self.audio_dialog("flac", "Audio FLAC Codec Parameters")
            
        elif cmd_opt["AudioCodec"] == "-c:a aac":
            self.audio_dialog("aac", "Audio AAC Codec Parameters")
            
        elif cmd_opt["AudioCodec"] == "-c:a alac":
            self.audio_dialog("alac", "Audio ALAC Codec Parameters")
            
        elif cmd_opt["AudioCodec"] == "-c:a ac3":
            self.audio_dialog("ac3", "Audio AC3 Codec Parameters")
            
        elif cmd_opt["AudioCodec"] == "-c:a libvorbis":
            self.audio_dialog("ogg", "Audio OGG Codec Parameters")
            
        elif cmd_opt["AudioCodec"] == "-c:a libmp3lame":
            self.audio_dialog("mp3", "Audio MP3 Codec Parameters")
        
        print (cmd_opt["AudioCodec"])
            
    #-------------------------------------------------------------------#
    def audio_dialog(self, audio_type, title):
        """
        Run a dialogs to choices audio parameters then set dictionary 
        at proper values.
        NOTE: The data[X] tuple contains the command parameters on the index [1] 
              and the descriptive parameters on the index [0].
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
            if audio_type in  ('wav','aiff'):
                if 'Default' in data[3][0]:
                    cmd_opt["AudioCodec"] = "-c:a pcm_s16le"
                else:
                    cmd_opt["AudioCodec"] = data[3][1]
                cmd_opt["AudioDepth"] = ("%s" % (data[3][0]),
                                         "%s" % (data[3][1])
                                         )
            else:# entra su tutti tranne wav aiff
                cmd_opt["AudioDepth"] = data[3]
        else:
            data = None
            audiodialog.Destroy()
            return
        
        self.txt_audio_options.SetValue("")
        count = 0
        for d in [cmd_opt["AudioRate"],cmd_opt["AudioDepth"],
                 cmd_opt["AudioBitrate"], cmd_opt["AudioChannel"]
                 ]:
            if d[1]:
                count += 1
                self.txt_audio_options.AppendText(" %s | " % d[0])

        if count == 0:
            self.btn_aparam.SetBottomEndColour(wx.Colour(205, 235, 222))
        else:
            self.btn_aparam.SetBottomEndColour(wx.Colour(0, 240, 0))
            
        audiodialog.Destroy()

    #------------------------------------------------------------------#
    def onNormalize(self, event):  # check box
        """
        Enable or disable functionality for volume normalization of
        the video.
        """
        msg = (_('Tip: set the maximum peak level threshold or accept default '
                 'dB value (-1.0); then check peak level by pressing the '
                 '"Volumedetect" button'))
        if self.ckbx_a_normalize.GetValue():# is checked
            self.parent.statusbar_msg(msg, azure)
            self.btn_analyzes.SetForegroundColour(wx.Colour(28,28,28))
            self.btn_analyzes.Enable(), self.spin_ctrl_audionormalize.Enable()
            self.label_normalize.Enable()
            #cmd_opt["Map"] = '-map 0'

        elif not self.ckbx_a_normalize.GetValue():# is not checked
            self.parent.statusbar_msg(_("Disable audio normalization"), None)
            self.spin_ctrl_audionormalize.SetValue(-1.0)
            self.label_normalize.Disable()
            self.btn_analyzes.SetForegroundColour(wx.Colour(165,165, 165))
            self.btn_analyzes.Disable(), self.spin_ctrl_audionormalize.Disable()
            self.btn_details.SetForegroundColour(wx.Colour(165,165, 165))
            self.btn_details.Disable()

            #cmd_opt["Map"] = ''
        cmd_opt["Normalize"] = ""
        del self.normdetails[:]
        
    #------------------------------------------------------------------#
    def on_Audio_analyzes(self, event):  # analyzes button
        """
        If check, send to audio_analyzes.
        """
        file_sources = self.parent.file_sources[:]
        self.audio_analyzes(file_sources)

    #------------------------------------------------------------------#
    def audio_analyzes(self, file_sources):  # analyzes button
        """
        Get audio peak level analyzes data for the offset calculation 
        need to normalization process.
        """
        msg1 = (_("Audio normalization will be applied"))
        msg2 = (_("Audio normalization is required only for some files"))
        msg3 = (_("Audio normalization is not required in relation to "
                  "the set threshold"))
        
        self.parent.statusbar_msg("",None)
        self.time_seq = self.parent.time_seq #from -ss to -t will be analyzed
        normalize = self.spin_ctrl_audionormalize.GetValue()

        data = volumeDetectProcess(self.ffmpeg_link, 
                                   file_sources, 
                                   self.time_seq)
        if data[1]:
            wx.MessageBox(data[1], "ERROR! -Videomass", wx.ICON_ERROR)
            return
        else:
            volume = list()

            for f, v in zip(file_sources, data[0]):
                maxvol = v[0].split(' ')[0]
                meanvol = v[1].split(' ')[0]
                offset = float(maxvol) - float(normalize)
                if float(maxvol) >= float(normalize):
                    volume.append('  ')
                    self.normdetails.append((f, 
                                             maxvol, 
                                             meanvol,
                                             ' ',
                                             _('Not Required')
                                             ))
                else:
                    volume.append("-af volume=%sdB" % (str(offset)[1:]))
                    self.normdetails.append((f, 
                                             maxvol,
                                             meanvol,
                                             str(offset)[1:],
                                             _('Required')
                                             ))
                    
        if [a for a in volume if not '  ' in a] == []:
             self.parent.statusbar_msg(msg3, orange)
        else:
            if len(volume) == 1 or not '  ' in volume:
                 self.parent.statusbar_msg(msg1, greenolive)
            else:
                self.parent.statusbar_msg(msg2, yellow)
                
        cmd_opt["Normalize"] = volume
        self.btn_analyzes.Disable()
        self.btn_analyzes.SetForegroundColour(wx.Colour(165,165, 165))
        self.btn_details.Enable()
        self.btn_details.SetForegroundColour(wx.Colour(28,28,28))

    #------------------------------------------------------------------#
    def on_Show_normlist(self, event):
        """
        Show a wx.ListCtrl dialog to list data of peak levels
        """
        title = _('Audio normalization details list')
        audionormlist = shownormlist.NormalizationList(title, 
                                                       self.normdetails, 
                                                       self.OS)
        audionormlist.Show()
        
    #------------------------------------------------------------------#
    def on_h264Presets(self, event):
        """
        Set only for h264 (non ha il default)
        """
        select = self.rdb_h264preset.GetStringSelection()
        
        if select == "Disabled":
            cmd_opt["Presets"] = ""
        else:
            cmd_opt["Presets"] = "-preset:v %s" % (select)
    #------------------------------------------------------------------#
    def on_h264Profiles(self, event):
        """
        Set only for h264
        """
        select = self.rdb_h264profile.GetStringSelection()
        
        if select == "Disabled":
            cmd_opt["Profile"] = ""
        else:
            cmd_opt["Profile"] = "-profile:v %s" % (select)
    #------------------------------------------------------------------#
    def on_h264Tunes(self, event):
        """
        Set only for h264
        """
        select = self.rdb_h264tune.GetStringSelection()
        
        if select == "Disabled":
            cmd_opt["Tune"] = ""
        else:
            cmd_opt["Tune"] = "-tune:v %s" % (select)
    #-----------------------------------------------------------------------#
    def disableParent(self):
        """
        disabling the main fraim also automatically disables this panel.
        Used on batch mode only with ProgressDialog gauge. 
        """
        self.parent.Disable()
    #-----------------------------------------------------------------------#
    def enableParent(self):
        """
        Enabling the main fraim also automatically enable this panel
        """
        self.parent.Enable()
    #------------------------------------------------------------------#
    def exportStreams(self, exported):
        """
        Set the parent.post_process attribute for communicate it the
        file disponibilities for play or metadata functionalities.
        """
        if not exported:
            return
        else:
            self.parent.post_process = exported
            self.parent.postExported_enable()
    #-------------------------------------------------------------------#
    def update_allentries(self):
        """
        Last step for set definitively all values before to proceed
        with std_conv or batch_conv methods.
        Update _allentries is callaed by on_ok method.
        """
        self.time_seq = self.parent.time_seq
        #self.on_Vrate(self), self.on_Vaspect(self)
        
        if self.spin_ctrl_bitrate.IsEnabled():
            self.on_Bitrate(self)
        elif self.slider_CRF.IsEnabled():
            self.on_Crf(self)
        else:
            cmd_opt["CRF"] = ''
            cmd_opt["Bitrate"] = ''
    #------------------------------------------------------------------#
    def on_ok(self):
        """
        Involves the files existence verification procedures and
        overwriting control, return:
        - typeproc: batch or single process
        - filename: nome file senza ext.
        - base_name: nome file con ext.
        - countmax: count processing cicles for batch mode

        """
        # check normalization data offset, if enable
        if self.ckbx_a_normalize.IsChecked():
            if self.btn_analyzes.IsEnabled():
                wx.MessageBox(_("Missing volume dectect!\n"
                                "Press the Volumedected button before "
                                "proceeding."),
                                "Videomass", wx.ICON_INFORMATION)
                return
        # make a different id need to avoid attribute overwrite:
        file_sources = self.parent.file_sources[:]
        # make a different id need to avoid attribute overwrite:
        dir_destin = self.file_destin
        # used for file log name
        logname = 'Videomass_VideoConversion.log'

        # CHECKING:
        if self.cmbx_vidContainers.GetValue() == _("Copy Video Codec"):
            self.time_seq = self.parent.time_seq
            checking = inspect(file_sources, dir_destin, '')
            
        elif self.cmbx_vidContainers.GetValue() == _("Save Images From Video"):
            self.time_seq = self.parent.time_seq
            checking = inspect(file_sources, dir_destin, 'jpg')
            
        else:
            self.update_allentries()# last update of all setting interface
            checking = inspect(file_sources, dir_destin, 
                            cmd_opt["VideoFormat"])
        if not checking[0]:
            # the user does not want to continue or not such files exist
            return
        
        typeproc, file_sources, dir_destin,\
        filename, base_name, countmax = checking
    
        if self.cmbx_vidContainers.GetValue() == _("Save Images From Video"):
            self.saveimages(file_sources, dir_destin, logname)
        else:
            self.stdProc(file_sources, dir_destin, countmax, logname)

        return

    #------------------------------------------------------------------#
    def stdProc(self, file_sources, dir_destin, countmax, logname):
        """
        Composes the ffmpeg command strings for batch process. 
        In double pass mode, split command in two part (see  
        os_processing.py at proc_batch_thread Class(Thread) ).
        
        """
        title = _('Start video conversion')
        if self.cmbx_vidContainers.GetValue() == _("Copy Video Codec"):
            command = ('-loglevel %s %s %s %s %s %s %s %s %s %s %s %s -y' % (
                       self.ffmpeg_loglev, 
                       cmd_opt["VideoCodec"], 
                       cmd_opt["VideoAspect"],
                       cmd_opt["VideoRate"],
                       cmd_opt["AudioCodec"], 
                       cmd_opt["AudioBitrate"][1], 
                       cmd_opt["AudioRate"][1], 
                       cmd_opt["AudioChannel"][1], 
                       cmd_opt["AudioDepth"][1], 
                       self.threads, 
                       self.cpu_used,
                       cmd_opt["Map"])
                        )
            command = " ".join(command.split())# mi formatta la stringa
            valupdate = self.update_dict(countmax, ["Copy Video Codec"] )
            ending = Formula(self, valupdate[0], valupdate[1], title)
            
            if ending.ShowModal() == wx.ID_OK:
                self.parent.switch_Process('normal',
                                           file_sources, 
                                           '', 
                                           dir_destin, 
                                           command, 
                                           None, 
                                           self.ffmpeg_link,
                                           cmd_opt["Normalize"], 
                                           logname, 
                                           countmax, 
                                           )
                #used for play preview and mediainfo:
                f = '%s/%s' % (dir_destin[0], os.path.basename(file_sources[0]))
                self.exportStreams(f)#call function more above
                
        elif cmd_opt["Passing"] == "double":
            cmd1 = ('-loglevel %s -an %s %s %s %s '
                     '%s %s %s %s %s %s -f rawvideo' % (
                      self.ffmpeg_loglev,
                      cmd_opt["VideoCodec"], cmd_opt["Bitrate"], 
                      cmd_opt["Presets"], cmd_opt["Profile"],
                      cmd_opt["Tune"], cmd_opt["VideoAspect"], 
                      cmd_opt["VideoRate"], cmd_opt["Filters"],
                      self.threads, self.cpu_used),
                    )
            pass1 = " ".join(cmd1[0].split())# mi formatta la stringa
            cmd2= ('-loglevel %s %s %s %s %s %s '
                     '%s %s %s %s %s %s %s %s %s %s %s' % (
                     self.ffmpeg_loglev, 
                     cmd_opt["VideoCodec"], cmd_opt["Bitrate"], 
                     cmd_opt["Presets"], cmd_opt["Profile"],
                     cmd_opt["Tune"], cmd_opt["VideoAspect"], 
                     cmd_opt["VideoRate"], cmd_opt["Filters"],
                     cmd_opt["AudioCodec"], cmd_opt["AudioBitrate"][1], 
                     cmd_opt["AudioRate"][1], cmd_opt["AudioChannel"][1], 
                     cmd_opt["AudioDepth"][1], self.threads, 
                     self.cpu_used, cmd_opt["Map"])
                    )
            pass2 =  " ".join(cmd2.split())# mi formatta la stringa
            valupdate = self.update_dict(countmax, [''])
            ending = Formula(self, valupdate[0], valupdate[1], title)
            
            if ending.ShowModal() == wx.ID_OK:
                self.parent.switch_Process('doublepass',
                                           file_sources, 
                                           cmd_opt['VideoFormat'], 
                                           dir_destin, 
                                           None, 
                                           [pass1, pass2], 
                                           self.ffmpeg_link,
                                           cmd_opt["Normalize"], 
                                           logname, 
                                           countmax, 
                                           )
                #used for play preview and mediainfo:
                f = os.path.basename(file_sources[0]).rsplit('.', 1)[0]
                self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                              cmd_opt["VideoFormat"]))
            #ending.Destroy() # con ID_OK e ID_CANCEL non serve Destroy()

        elif cmd_opt["Passing"] == "single": # Batch-Mode / h264 Codec
            command = ("-loglevel %s %s %s %s %s %s %s "
                       "%s %s %s %s %s %s %s %s %s %s -y" % (
                        self.ffmpeg_loglev, 
                        cmd_opt["VideoCodec"], cmd_opt["CRF"], 
                        cmd_opt["Presets"], cmd_opt["Profile"],
                        cmd_opt["Tune"], cmd_opt["VideoAspect"], 
                        cmd_opt["VideoRate"], cmd_opt["Filters"],
                        cmd_opt["AudioCodec"], cmd_opt["AudioBitrate"][1], 
                        cmd_opt["AudioRate"][1], cmd_opt["AudioChannel"][1], 
                        cmd_opt["AudioDepth"][1], self.threads, 
                        self.cpu_used, cmd_opt["Map"])
                        )
            command = " ".join(command.split())# mi formatta la stringa
            valupdate = self.update_dict(countmax, [''])
            ending = Formula(self, valupdate[0], valupdate[1], title)
            
            if ending.ShowModal() == wx.ID_OK:
                self.parent.switch_Process('normal',
                                           file_sources, 
                                           cmd_opt['VideoFormat'], 
                                           dir_destin, 
                                           command, 
                                           None, 
                                           self.ffmpeg_link,
                                           cmd_opt["Normalize"], 
                                           logname, 
                                           countmax, 
                                           )
                #used for play preview and mediainfo:
                f = os.path.basename(file_sources[0]).rsplit('.', 1)[0]
                self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                                 cmd_opt["VideoFormat"]))
    #--------------------------------------------------------------------#
    def saveimages(self, file_sources, dest, logname):
        """
        Save as files image the selected video input. The saved 
        images are named as file name + a progressive number + .jpg 
        and placed in a folder with the same file name + a progressive 
        number in the chosen output path.
        
        """
        if not self.parent.import_clicked:
            wx.MessageBox(_('To export images, select one of the files '
                            'in the "Add files" panel'), 'Videomass', 
                            wx.ICON_INFORMATION, self)
            return
        
        title = _('Start save as images')
        valupdate = self.update_dict('1', ["Save as images"])
        ending = Formula(self, valupdate[0],valupdate[1], title)
        
        if ending.ShowModal() == wx.ID_OK:
            clicked = self.parent.import_clicked
            fname = os.path.basename(clicked.rsplit('.', 1)[0])
            dir_destin = dest[file_sources.index(clicked)]# specified dest
            
            try: 
                outputdir = "%s/%s-IMAGES_1" % (dir_destin, fname)
                os.mkdir(outputdir)
                
            except FileExistsError:
                lista = []
                for dir_ in os.listdir(dir_destin):
                    if "%s-IMAGES_" % fname in dir_:
                        lista.append(int(dir_.split('IMAGES_')[1]))
                        
                prog = max(lista) +1
                outputdir = "%s/%s-IMAGES_%d" % (dir_destin, fname, prog)
                os.mkdir(outputdir)

            fileout = "{0}-%d.{1}".format(fname,'jpg')
            cmd = ('%s %s -i "%s" -loglevel %s -an %s %s %s %s -y "%s/%s"' % (
                                                    self.ffmpeg_link, 
                                                    self.parent.time_seq,
                                                    clicked, 
                                                    self.ffmpeg_loglev,
                                                    cmd_opt["VideoRate"],
                                                    cmd_opt["Filters"],
                                                    self.threads, 
                                                    self.cpu_used,
                                                    outputdir, 
                                                    fileout)
                                                    )
            command = " ".join(cmd.split())# compact string
            self.parent.switch_Process('saveimages',
                                        clicked, 
                                        None, 
                                        None, 
                                        command, 
                                        None, 
                                        None, 
                                        None, 
                                        logname, 
                                        '1', 
                                        )
    #------------------------------------------------------------------#
    #------------------------------------------------------------------#
    def update_dict(self, countmax, prof):
        """
        This method is required for update all cmd_opt
        dictionary values before send to epilogue
        """
        numfile = _("%s file in pending") % str(countmax)
        if cmd_opt["Normalize"]:
            normalize = _('Enable')
        else:
            normalize = _('Disable')
        
        if prof[0] == "Copy Video Codec":
            formula = (_("SUMMARY:\n\nFile to Queue\
                \nVideo Format:\nVideo codec:\nVideo aspect:\nVideo rate:\
                \nAudio Format:\nAudio codec:\nAudio channel:\
                \nAudio rate:\nAudio bit-rate:\nBit per Sample:\
                \nAudio Normalization:\nMap:\nTime selection:"))
            dictions = ("\n\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\
                        \n%s\n%s\n%s\n%s\n%s\n%s" % (
                numfile, cmd_opt["FormatChoice"], cmd_opt["VideoCodec"], 
                cmd_opt["VideoAspect"], cmd_opt["VideoRate"], cmd_opt["Audio"], 
                cmd_opt["AudioCodec"], cmd_opt["AudioChannel"][0], 
                cmd_opt["AudioRate"][0], cmd_opt["AudioBitrate"][0],
                cmd_opt["AudioDepth"][0], normalize, cmd_opt["Map"], 
                self.parent.time_seq))
                        
        elif prof[0] == "Save as images":
            formula = (_("SUMMARY:\n\nFile to Queue\
                         \nImages Format:\nVideo rate:\
                         \nFilters:\nTime selection:"
                        ))
            dictions = ("\n\n1\njpg\n%s\n%s\n%s" % (cmd_opt["VideoRate"],   
                                                    cmd_opt["Filters"],
                                                    self.parent.time_seq
                                                    ))
        
        else:
            formula = (_("SUMMARY:\n\nFile to Queue\
                    \nVideo Format:\nVideo codec:\nVideo bit-rate:\nCRF:\
                    \nDouble/Single Pass:\nDeinterlacing:\
                    \nInterlacing:\nApplied Filters:\
                    \nVideo aspect:\nVideo rate:\nPreset h264:\nProfile h264:\
                    \nTune h264:\nOrientation:\nAudio Format:\nAudio codec:\
                    \nAudio channel:\nAudio rate:\nAudio bit-rate:\
                    \nBit per Sample:\nAudio Normalization:\nMap:\
                    \nTime selection:"))
            dictions = ("\n\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\
                        \n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s" % (
                        numfile, cmd_opt["FormatChoice"], cmd_opt["VideoCodec"], 
                        cmd_opt["Bitrate"], cmd_opt["CRF"], cmd_opt["Passing"], 
                        cmd_opt["Deinterlace"], cmd_opt["Interlace"], 
                        cmd_opt["Filters"], cmd_opt["VideoAspect"], 
                        cmd_opt["VideoRate"], cmd_opt["Presets"], 
                        cmd_opt["Profile"], cmd_opt["Tune"], 
                        cmd_opt["Orientation"][1], cmd_opt["Audio"], 
                        cmd_opt["AudioCodec"], cmd_opt["AudioChannel"][0], 
                        cmd_opt["AudioRate"][0], cmd_opt["AudioBitrate"][0],
                        cmd_opt["AudioDepth"][0], normalize, cmd_opt["Map"], 
                        self.parent.time_seq)
                        )
        return formula, dictions

#------------------------------------------------------------------#
    def Addprof(self):
        """
        Storing new profile in the 'Preset Manager' panel with the same 
        current setting. All profiles saved in this way will also be stored 
        in the preset 'User Presets'
        
        FIXME have any problem with xml escapes in special character
        (like && for ffmpeg double pass), so there is some to get around it 
        (escamotage), but work .
        """
        self.update_allentries()# aggiorno gli imput
        get = wx.GetApp()
        dirconf = os.path.join(get.DIRconf, 'vdms')
        
        if cmd_opt["Normalize"]:
            normalize = cmd_opt["Normalize"][0]
        else:
            normalize = ''
        
        if not self.ckbx_pass.IsChecked():
            if self.cmbx_vidContainers.GetValue() == _("Copy Video Codec"):
                outext = cmd_opt["VideoFormat"]
                command = ('%s %s %s %s %s %s %s %s %s %s' % (
                            normalize,
                            cmd_opt["VideoCodec"], 
                            cmd_opt["VideoAspect"],
                            cmd_opt["VideoRate"],
                            cmd_opt["AudioCodec"], 
                            cmd_opt["AudioBitrate"][1], 
                            cmd_opt["AudioRate"][1], 
                            cmd_opt["AudioChannel"][1], 
                            cmd_opt["AudioDepth"][1], 
                            cmd_opt["Map"])
                                )
            elif self.cmbx_vidContainers.GetValue() == _("Save Images From Video"):
                outext = "jpg"
                command = ('%s %s -an' % (
                           cmd_opt["VideoRate"],
                           cmd_opt["Filters"],)
                           )
            else:
                outext = cmd_opt["VideoFormat"]
                command = ("%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s" % (
                            normalize,
                            cmd_opt["VideoCodec"], cmd_opt["CRF"], 
                            cmd_opt["Presets"], cmd_opt["Profile"],
                            cmd_opt["Tune"], cmd_opt["VideoAspect"], 
                            cmd_opt["VideoRate"], cmd_opt["Filters"],
                            cmd_opt["AudioCodec"], cmd_opt["AudioBitrate"][1], 
                            cmd_opt["AudioRate"][1], cmd_opt["AudioChannel"][1], 
                            cmd_opt["AudioDepth"][1], cmd_opt["Map"])
                            )
        else:
            outext = cmd_opt["VideoFormat"]
            cmd1 = ('-an %s %s %s %s %s %s %s %s -f rawvideo' % (
                      cmd_opt["VideoCodec"], cmd_opt["Bitrate"], 
                      cmd_opt["Presets"], cmd_opt["Profile"],
                      cmd_opt["Tune"], cmd_opt["VideoAspect"], 
                      cmd_opt["VideoRate"], cmd_opt["Filters"])
                    )
            cmd2= ('%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s' % (
                     normalize,
                     cmd_opt["VideoCodec"], cmd_opt["Bitrate"], 
                     cmd_opt["Presets"], cmd_opt["Profile"],
                     cmd_opt["Tune"], cmd_opt["VideoAspect"], 
                     cmd_opt["VideoRate"], cmd_opt["Filters"],
                     cmd_opt["AudioCodec"], cmd_opt["AudioBitrate"][1], 
                     cmd_opt["AudioRate"][1], cmd_opt["AudioChannel"][1], 
                     cmd_opt["AudioDepth"][1], cmd_opt["Map"])
                    )
            command = ("%s DOUBLE_PASS %s" % (cmd1,cmd2))
                       
        command = ' '.join(command.split())# sitemo meglio gli spazi in stringa
        list = [command, outext]

        filename = 'preset-v1-Personal'# nome del file preset senza ext
        name_preset = 'User Profiles'
        full_pathname = os.path.join(dirconf, 'preset-v1-Personal.vdms')
        
        prstdlg = presets_addnew.MemPresets(self, 'addprofile', full_pathname, 
                                            filename, list, 
                    _('Videomass: Create a new profile on "%s" preset') % (
                                 name_preset))
        prstdlg.ShowModal()
