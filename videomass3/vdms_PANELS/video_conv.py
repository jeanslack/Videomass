# -*- coding: UTF-8 -*-

#########################################################
# FileName: video_conv.py
# Porpose: Intarface for video conversions
# Compatibility: Python3, wxPython4 Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Aug.02.2019, Sept.24.2019
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

# Dictionary definition for command settings:
cmd_opt = {"VidCmbxStr": "", "VideoFormat": "", "VideoCodec": "", 
           "ext_input": "", "Passing": "single", "InputDir": "", 
           "OutputDir": "",  "VideoSize": "", "VideoAspect": "", 
           "VideoRate": "", "Presets": "", "Profile": "", 
           "Tune": "", "Bitrate": "", "CRF": "", "Audio": "", 
           "AudioCodec": "", "AudioChannel": ["",""], 
           "AudioRate": ["",""], "AudioBitrate": ["",""], 
           "AudioDepth": ["",""], "PEAK": "", "EBU": "","RMS": "", 
           "Deinterlace": "", "Interlace": "", "Map": "-map 0", 
           "PixelFormat": "", "Orientation": ["",""],"Crop": "",
           "Scale": "", "Setdar": "", "Setsar": "", "Denoiser": "", 
           "Filters": "", "YUV": "", "Deadline": "", "CpuUsed": "",
           "RowMthreading": "",
           }
# Namings in the video container selection combo box:
vcodecs = {("AVI (XVID mpeg4)"): ("-c:v mpeg4 -vtag xvid","avi"), 
            ("AVI (FFmpeg mpeg4)"): ("-c:v mpeg4","avi"), 
            ("AVI (h.264/AVC)"): ("-c:v libx264","avi"),
            ("AVI (h.265/HEVC)"): ("-c:v libx265","avi"),
            ("MP4 (mpeg4)"): ("-c:v mpeg4","mp4"), 
            ("MP4 (h.264/AVC)"): ("-c:v libx264","mp4"), 
            ("MP4 (h.265/HEVC)"): ("-c:v libx265","mp4"), 
            ("M4V (h.264/AVC)"): ("-c:v libx264","m4v"), 
            ("M4V (h.265/HEVC)"): ("-c:v libx265","m4v"),
            ("MKV (h.264/AVC)"): ("-c:v libx264","mkv"),
            ("MKV (h.265/HEVC)"): ("-c:v libx265","mkv"),
            #("MKV (AV1/libaom)"): ("-c:v libaom-av1 -strict -2","mkv"),
            ("OGG theora"): ("-c:v libtheora","ogg"), 
            ("WebM vp8 (HTML5)"): ("-c:v libvpx","webm"), 
            ("WebM vp9 (HTML5)"): ("-c:v libvpx-vp9","webm"),
            ("FLV (h.264/AVC)"): ("-c:v libx264","flv"),
            (_("Copy video codec")): ("-c:v copy",""),
            }
# Namings in the audio format selection on audio radio box:
acodecs = {('default'): (_("Default (managed by FFmpeg)"),''),
           ('wav'): ("Wav (Raw, No_MultiChannel)", "-c:a pcm_s16le"), 
           ('flac'): ("Flac (Lossless, No_MultiChannel)", "-c:a flac"), 
           ('aac'): ("Aac (Lossy, MultiChannel)", "-c:a aac"), 
           ('m4v'): ("Alac (Lossless, m4v, No_MultiChannel)", "-c:a alac"),
           ('ac3'): ("Ac3 (Lossy, MultiChannel)", "-c:a ac3"), 
           ('ogg'): ("Ogg (Lossy, No_MultiChannel)", "-c:a libvorbis"),
           ('mp3'): ("Mp3 (Lossy, No_MultiChannel)", "-c:a libmp3lame"),
           ('opus'): ("Opus (Lossy, No_MultiChannel)", "-c:a libopus"),
           ('copy'): (_("Try to copy audio source"), "-c:a copy"),
           ('silent'): (_("No audio stream (silent)"), "-an")
           }
# compatibility between video formats and related audio codecs:
av_formats = {('avi'): ('default','wav',None,None,None,'ac3',None,'mp3',
                        None,'copy','silent'),
              ('flv'): ('default',None,None,'aac',None,'ac3',None,'mp3',
                        None,'copy','silent'),
              ('mp4'): ('default',None,None,'aac',None,'ac3',None,'mp3',
                        None,'copy','silent'),
              ('m4v'): ('default',None,None,'aac','alac',None,None,None,
                        None,'copy','silent'),
              ('mkv'): ('default','wav','flac','aac',None,'ac3','ogg','mp3',
                        'opus','copy','silent'),
              ('webm'): ('default',None,None,None,None,None,'ogg',None,
                         'opus','copy','silent'),
              ('ogg'): ('default',None,'flac',None,None,None,'ogg',None,
                        'opus','copy','silent')
              }
# presets used by x264 an h264:
x264_opt = {("Presets"): ("Disabled","ultrafast","superfast",
                          "veryfast","faster","fast","medium",
                          "slow","slower","veryslow","placebo"
                          ), 
            ("Profiles"): ("Disabled","baseline","main","high",
                           "high10","high444"
                           ),
            ("Tunes"): ("Disabled","film","animation","grain",
                        "stillimage","psnr","ssim","fastedecode",
                        "zerolatency"
                        )
            }
# set widget colours in some case with html rappresentetion:
azure = '#15a6a6' # rgb form (wx.Colour(217,255,255))
yellow = '#a29500'
red = '#ea312d'
orange = '#f28924'
greenolive = '#6aaf23'
green = '#268826'
ciano = '#61ccc7' # rgb 97, 204, 199
violet = '#D64E93'

class Video_Conv(wx.Panel):
    """
    Interface panel for video conversions
    """
    def __init__(self, parent, ffmpeg_link, ffplay_link, ffprobe_link, 
                 threads, ffmpeg_loglev, ffplay_loglev, OS, iconplay,
                 iconreset, iconresize, iconcrop, iconrotate, 
                 icondeinterlace, icondenoiser, iconanalyzes, 
                 iconsettings, iconpeaklevel, iconatrack, btn_color,
                 fontBtncolor,
                 ):

        wx.Panel.__init__(self, parent)

        # set attributes:
        self.parent = parent
        self.ffmpeg_link = ffmpeg_link
        self.ffplay_link = ffplay_link
        self.ffprobe_link = ffprobe_link
        self.threads = threads
        self.ffmpeg_loglev = ffmpeg_loglev
        self.ffplay_loglev = ffplay_loglev
        self.file_sources = []
        self.file_destin = ''
        self.normdetails = []
        self.OS = OS
        self.btn_color = btn_color
        self.fBtnC = fontBtncolor
        #------------
        self.panel_base = wx.Panel(self, wx.ID_ANY)
        self.notebook_1 = wx.Notebook(self.panel_base, wx.ID_ANY, 
                                      style=wx.NB_NOPAGETHEME|wx.NB_BOTTOM)
        self.notebook_1_pane_1 = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.cmbx_vidContainers = wx.ComboBox(self.notebook_1_pane_1, 
                                              wx.ID_ANY,
                                             choices=[x for x in vcodecs.keys()],
                                             size=(200,-1),
                                             style=wx.CB_DROPDOWN | 
                                             wx.CB_READONLY
                                             )
        self.sizer_combobox_formatv_staticbox = wx.StaticBox(
                                                        self.notebook_1_pane_1, 
                                                        wx.ID_ANY, 
                                               (_("Video Container Selection"))
                                                             )
        self.sizer_dir_staticbox = wx.StaticBox(self.notebook_1_pane_1, 
                                                wx.ID_ANY, 
                                           (_('Improves low-quality export'))
                                                )
        self.ckbx_pass = wx.CheckBox(self.notebook_1_pane_1, 
                                     wx.ID_ANY, 
                                     (_("2-pass encoding"))
                                     )
        self.sizer_automations_staticbox = wx.StaticBox(self.notebook_1_pane_1, 
                                                        wx.ID_ANY, ("")
                                                        )
        self.rdb_deadline = wx.RadioBox(self.notebook_1_pane_1, wx.ID_ANY, 
                                   (_("Deadline/Quality")), choices=[
                                            ("best"), 
                                            ("good"), 
                                            ("realtime")], 
                                    majorDimension=0, 
                                    style=wx.RA_SPECIFY_ROWS
                                            )
        self.lab_cpu = wx.StaticText(self.notebook_1_pane_1, wx.ID_ANY, (
                            _("Quality/Speed ratio modifier:")))
        self.spin_cpu = wx.SpinCtrl(self.notebook_1_pane_1, wx.ID_ANY, 
                                        "0", min=-16, max=16, 
                                        size=(-1,-1), style=wx.TE_PROCESS_ENTER
                                             )
        self.ckbx_multithread = wx.CheckBox(self.notebook_1_pane_1, 
                                     wx.ID_ANY, 
                                     (_('Activates row-mt 1'))
                                     )
        self.spin_Vbrate = wx.SpinCtrl(self.notebook_1_pane_1, wx.ID_ANY, 
                                             "1500", min=0, max=204800, 
                                             style=wx.TE_PROCESS_ENTER
                                             )
        self.sizer_bitrate_staticbox = wx.StaticBox(self.notebook_1_pane_1, 
                                                    wx.ID_ANY, 
                                                 (_("Video Bit-Rate Value"))
                                                    )
        self.slider_CRF = wx.Slider(self.notebook_1_pane_1, wx.ID_ANY, 
                                    1, 0, 51, size=(230, -1),
                                    style=wx.SL_HORIZONTAL | 
                                          wx.SL_AUTOTICKS | 
                                          wx.SL_LABELS
                                    )
        self.sizer_crf_staticbox = wx.StaticBox(self.notebook_1_pane_1, 
                                                wx.ID_ANY, 
                                                (_("Video CRF Value"))
                                                )
        self.notebook_1_pane_2 = wx.Panel(self.notebook_1, wx.ID_ANY)
        resizebmp = wx.Bitmap(iconresize, wx.BITMAP_TYPE_ANY)
        self.btn_videosize = GB.GradientButton(self.notebook_1_pane_2,
                                               size=(-1,25),
                                               bitmap=resizebmp,
                                               label=_("Resize"))
        self.btn_videosize.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                        foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_videosize.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_videosize.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_videosize.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_videosize.SetTopEndColour(wx.Colour(self.btn_color))
        cropbmp = wx.Bitmap(iconcrop, wx.BITMAP_TYPE_ANY)
        self.btn_crop = GB.GradientButton(self.notebook_1_pane_2,
                                          size=(-1,25),
                                          bitmap=cropbmp,
                                          label=_("Crop Dimension"))
        self.btn_crop.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                        foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_crop.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_crop.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_crop.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_crop.SetTopEndColour(wx.Colour(self.btn_color))
        rotatebmp = wx.Bitmap(iconrotate, wx.BITMAP_TYPE_ANY)
        self.btn_rotate = GB.GradientButton(self.notebook_1_pane_2,
                                            size=(-1,25),
                                            bitmap=rotatebmp,
                                            label=_("Rotation"))
        self.btn_rotate.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                        foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_rotate.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_rotate.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_rotate.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_rotate.SetTopEndColour(wx.Colour(self.btn_color))
        deintbmp = wx.Bitmap(icondeinterlace, wx.BITMAP_TYPE_ANY)
        self.btn_lacing = GB.GradientButton(self.notebook_1_pane_2,
                                            size=(-1,25),
                                            bitmap=deintbmp,
                                            label=_("De/Interlace"))
        self.btn_lacing.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                        foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_lacing.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_lacing.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_lacing.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_lacing.SetTopEndColour(wx.Colour(self.btn_color))
        denoiserbmp = wx.Bitmap(icondenoiser, wx.BITMAP_TYPE_ANY)
        self.btn_denois = GB.GradientButton(self.notebook_1_pane_2,
                                            size=(-1,25),
                                            bitmap=denoiserbmp,
                                            label="Denoisers")
        self.btn_denois.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                        foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_denois.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_denois.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_denois.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_denois.SetTopEndColour(wx.Colour(self.btn_color))
        playbmp = wx.Bitmap(iconplay, wx.BITMAP_TYPE_ANY)
        self.btn_preview = GB.GradientButton(self.notebook_1_pane_2,
                                             size=(-1,25),
                                             bitmap=playbmp, 
                                             )
        self.btn_preview.SetBaseColours(startcolour=wx.Colour(158,201,232))
        self.btn_preview.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_preview.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_preview.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_preview.SetTopEndColour(wx.Colour(self.btn_color))
        resetbmp = wx.Bitmap(iconreset, wx.BITMAP_TYPE_ANY)
        self.btn_reset = GB.GradientButton(self.notebook_1_pane_2,
                                             size=(-1,25),
                                             bitmap=resetbmp, 
                                             )
        self.btn_reset.SetBaseColours(startcolour=wx.Colour(158,201,232))
        self.btn_reset.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_reset.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_reset.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_reset.SetTopEndColour(wx.Colour(self.btn_color))
        
        self.sizer_videosize_staticbox = wx.StaticBox(self.notebook_1_pane_2, 
                                                      wx.ID_ANY, 
                                                      (_("Video Filters"))
                                                      )
        self.cmbx_Vaspect = wx.ComboBox(self.notebook_1_pane_2, wx.ID_ANY,
                                        size=(200, -1), choices=[("Default "), 
                                                                 ("4:3"), 
                                                                 ("16:9"),
                                                                 ("1.3333"),
                                                                 ("1.7777")], 
                                        style=wx.CB_DROPDOWN | wx.CB_READONLY
                                        )
        self.sizer_videoaspect_staticbox = wx.StaticBox(self.notebook_1_pane_2, 
                                                        wx.ID_ANY, 
                                                        (_("Video Aspect"))
                                                        )
        self.cmbx_Vrate = wx.ComboBox(self.notebook_1_pane_2, wx.ID_ANY, 
                                      choices=[("Default "), 
                                               ("25 fps (50i) PAL"), 
                                               ("29.97 fps (60i) NTSC"),
                                               ("30 fps (30p) Progessive"),
                                               ("0.2 fps"), 
                                               ("0.5 fps"),
                                               ("1 fps"), 
                                               ("1.5 fps"), 
                                               ("2 fps")
                                               ], 
                                      style=wx.CB_DROPDOWN | 
                                      wx.CB_READONLY
                                      )
        self.sizer_videorate_staticbox = wx.StaticBox(self.notebook_1_pane_2, 
                                                      wx.ID_ANY, 
                                                      (_("Video Rate"))
                                                      )
        self.notebook_1_pane_3 = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.rdb_a = wx.RadioBox(self.notebook_1_pane_3, wx.ID_ANY, (
                                 _("Audio Codec Selecting")),
                                 choices=[x[0] for x in acodecs.values()],
                                 majorDimension=2, style=wx.RA_SPECIFY_COLS
                                    )
        for n,v in enumerate(av_formats["mkv"]):
            if not v:#disable only not compatible with mkv 
                self.rdb_a.EnableItem(n,enable=False
                                      )
        self.rdbx_normalize = wx.RadioBox(self.notebook_1_pane_3,wx.ID_ANY,
                                     (_("Audio Normalization")), 
                                     choices=[
                                       ('Off'), 
                                       ('PEAK'), 
                                       ('RMS'),
                                       ('EBU R128'),
                                              ], 
                                     majorDimension=0, 
                                     style=wx.RA_SPECIFY_ROWS,
                                            )
        analyzebmp = wx.Bitmap(iconanalyzes, wx.BITMAP_TYPE_ANY)
        self.btn_voldect = GB.GradientButton(self.notebook_1_pane_3,
                                            size=(-1,25),
                                            bitmap=analyzebmp,
                                            label=_("Volumedetect"))
        self.btn_voldect.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(28,28, 28))
        self.btn_voldect.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_voldect.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_voldect.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_voldect.SetTopEndColour(wx.Colour(self.btn_color))
        
        peaklevelbmp = wx.Bitmap(iconpeaklevel, wx.BITMAP_TYPE_ANY)
        self.btn_details = GB.GradientButton(self.notebook_1_pane_3,
                                            size=(-1,25),
                                            bitmap=peaklevelbmp,
                                            label=_("Volume Statistics"))
        self.btn_details.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(28,28, 28))
        self.btn_details.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_details.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_details.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_details.SetTopEndColour(wx.Colour(self.btn_color))
        
        self.lab_amplitude = wx.StaticText(self.notebook_1_pane_3, wx.ID_ANY, 
                                    (_("Target level:"))
                                    )
        self.spin_target = FS.FloatSpin(self.notebook_1_pane_3, 
                                                     wx.ID_ANY, 
                                                     min_val=-99.0, 
                                                     max_val=0.0, 
                                                     increment=0.5, value=-1.0, 
                                            agwStyle=FS.FS_LEFT, size=(-1,-1)
                                            )
        self.spin_target.SetFormat("%f"), self.spin_target.SetDigits(1)
        self.lab_i = wx.StaticText(self.notebook_1_pane_3, wx.ID_ANY, (
                             _("Set integrated loudness target:  ")))
        self.spin_i = FS.FloatSpin(self.notebook_1_pane_3, wx.ID_ANY, 
                                   min_val=-70.0, max_val=-5.0, 
                                   increment=0.5, value=-24.0, 
                                    agwStyle=FS.FS_LEFT,size=(-1,-1))
        self.spin_i.SetFormat("%f"), self.spin_i.SetDigits(1)
        
        self.lab_tp = wx.StaticText(self.notebook_1_pane_3, wx.ID_ANY, (
                                    _("Set maximum true peak:")))
        self.spin_tp = FS.FloatSpin(self.notebook_1_pane_3, wx.ID_ANY, 
                                    min_val=-9.0, max_val=0.0,
                                    increment=0.5, value=-2.0, 
                                    agwStyle=FS.FS_LEFT,size=(-1,-1))
        self.spin_tp.SetFormat("%f"), self.spin_tp.SetDigits(1)
        
        self.lab_lra = wx.StaticText(self.notebook_1_pane_3, wx.ID_ANY, (
                                    _("Set loudness range target:")))
        self.spin_lra = FS.FloatSpin(self.notebook_1_pane_3, wx.ID_ANY,
                                     min_val=1.0, max_val=20.0, 
                                     increment=0.5, value=7.0, 
                                    agwStyle=FS.FS_LEFT,size=(-1,-1))
        self.spin_lra.SetFormat("%f"), self.spin_lra.SetDigits(1)
        
        setbmp = wx.Bitmap(iconsettings, wx.BITMAP_TYPE_ANY)
        self.btn_aparam = GB.GradientButton(self.notebook_1_pane_3,
                                           size=(-1,25),
                                           bitmap=setbmp,
                                           label=_("Audio Options"))
        self.btn_aparam.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(165,165, 165))
        self.btn_aparam.SetBottomEndColour(wx.Colour(self.btn_color))
        self.btn_aparam.SetBottomStartColour(wx.Colour(self.btn_color))
        self.btn_aparam.SetTopStartColour(wx.Colour(self.btn_color))
        self.btn_aparam.SetTopEndColour(wx.Colour(self.btn_color))
        self.txt_audio_options = wx.TextCtrl(self.notebook_1_pane_3, wx.ID_ANY, 
                                             size=(300,-1), 
                                             style=wx.TE_READONLY
                                             )
        self.notebook_1_pane_4 = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.rdb_h264preset = wx.RadioBox(self.notebook_1_pane_4, wx.ID_ANY, 
                                          ("presets"),  
                                    choices=[p for p in x264_opt["Presets"]],
                                          majorDimension=0, 
                                          style=wx.RA_SPECIFY_ROWS
                                            )
        self.rdb_h264profile = wx.RadioBox(self.notebook_1_pane_4, wx.ID_ANY, 
                                           ("Profile"),  
                                    choices=[p for p in x264_opt["Profiles"]],
                                           majorDimension=0, 
                                           style=wx.RA_SPECIFY_ROWS
                                            )
        self.rdb_h264tune = wx.RadioBox(self.notebook_1_pane_4, wx.ID_ANY, 
                                        ("Tune"),
                                        choices=[p for p in x264_opt["Tunes"]],
                                        majorDimension=0, 
                                        style=wx.RA_SPECIFY_ROWS
                                         )
        #----------------------Build Layout----------------------#
        self.sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(2, 1, 0, 0)
        sizer_pane4_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_pane4_base = wx.GridSizer(1, 3, 0, 0)
        sizer_pane3_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_pane3_base = wx.FlexGridSizer(2, 2, 0, 0)
        sizer_pane3_audio_column2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_in_column2 = wx.FlexGridSizer(7, 2, 0, 0)
        #sizer_pane3_audio_column1 = wx.BoxSizer(wx.VERTICAL)
        sizer_pane2_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_pane2_base = wx.GridSizer(1, 2, 0, 0)
        grid_sizer_1 = wx.GridSizer(2, 1, 0, 0)
        self.sizer_videorate_staticbox.Lower()
        sizer_videorate = wx.StaticBoxSizer(self.sizer_videorate_staticbox, 
                                            wx.VERTICAL)
        self.sizer_videoaspect_staticbox.Lower()
        sizer_videoaspect = wx.StaticBoxSizer(self.sizer_videoaspect_staticbox, 
                                              wx.VERTICAL
                                              )
        self.sizer_videosize_staticbox.Lower()
        sizer_2 = wx.StaticBoxSizer(self.sizer_videosize_staticbox, wx.VERTICAL)
        grid_sizer_2 = wx.GridSizer(6, 2, 0, 0)
        grid_sizer_pane1_base = wx.GridSizer(1, 3, 0, 0)
        grid_sizer_pane1_right = wx.GridSizer(2, 1, 0, 0)
        self.sizer_crf_staticbox.Lower()
        sizer_crf = wx.StaticBoxSizer(self.sizer_crf_staticbox, wx.VERTICAL)
        self.sizer_bitrate_staticbox.Lower()
        sizer_bitrate = wx.StaticBoxSizer(self.sizer_bitrate_staticbox, 
                                          wx.VERTICAL
                                          )
        self.sizer_automations_staticbox.Lower()
        sizer_automations = wx.StaticBoxSizer(self.sizer_automations_staticbox, 
                                              wx.VERTICAL
                                              )
        grid_sizer_automations = wx.FlexGridSizer(6, 1, 0, 0)
        grid_sizer_automations.Add(self.rdb_deadline, 0, wx.ALL| 
                                                    wx.ALIGN_CENTER_HORIZONTAL| 
                                                    wx.ALIGN_CENTER_VERTICAL, 
                                                    15
                                                    )
        
        grid_sizer_automations.Add(self.lab_cpu, 0, wx.ALL, 5)
        grid_sizer_automations.Add(self.spin_cpu, 0, wx.ALL| 
                                                     wx.ALIGN_CENTER_HORIZONTAL| 
                                                     wx.ALIGN_CENTER_VERTICAL, 
                                                     5
                                                     )
        grid_sizer_automations.Add(self.ckbx_multithread, 0, wx.ALL| 
                                                     wx.ALIGN_CENTER_HORIZONTAL| 
                                                     wx.ALIGN_CENTER_VERTICAL, 
                                                     5
                                                     )
        grid_sizer_pane1_left = wx.GridSizer(2, 1, 0, 0)
        self.sizer_dir_staticbox.Lower()
        sizer_dir = wx.StaticBoxSizer(self.sizer_dir_staticbox, wx.VERTICAL)
        grid_sizer_dir = wx.GridSizer(1, 1, 0, 0)
        self.sizer_combobox_formatv_staticbox.Lower()
        sizer_combobox_formatv = wx.StaticBoxSizer(
                                        self.sizer_combobox_formatv_staticbox, 
                                        wx.VERTICAL
                                        )
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

        sizer_automations.Add(grid_sizer_automations, 0, wx.ALL| 
                                                     wx.ALIGN_CENTER_HORIZONTAL| 
                                                     wx.ALIGN_CENTER_VERTICAL, 
                                                     5)####
        grid_sizer_pane1_base.Add(sizer_automations, 1, wx.ALL | wx.EXPAND, 15)
        sizer_bitrate.Add(self.spin_Vbrate, 0, wx.ALL| 
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
        sizer_videorate.Add(self.cmbx_Vrate, 0, wx.ALL | 
                                                wx.ALIGN_CENTER_HORIZONTAL, 15
                                                )
        grid_sizer_1.Add(sizer_videorate, 1, wx.ALL | wx.EXPAND, 15)
        grid_sizer_pane2_base.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        sizer_pane2_base.Add(grid_sizer_pane2_base, 1, wx.EXPAND, 0)
        self.notebook_1_pane_2.SetSizer(sizer_pane2_base)
        
        grid_a_param = wx.FlexGridSizer(2, 1, 20, 20)
        grid_a_param.Add(self.rdb_a, 0, wx.ALL|
                                            wx.ALIGN_CENTER_VERTICAL|
                                            wx.ALIGN_CENTER_HORIZONTAL, 5
                                            )
        grid_a_ctrl = wx.FlexGridSizer(1, 2, 0, 0)
        grid_a_ctrl.Add(self.btn_aparam, 0, wx.ALL|
                                            wx.ALIGN_CENTER_VERTICAL|
                                            wx.ALIGN_CENTER_HORIZONTAL, 5
                        )
        grid_a_ctrl.Add(self.txt_audio_options, 0, wx.ALL|
                                                   wx.ALIGN_CENTER_VERTICAL|
                                                   wx.ALIGN_CENTER_HORIZONTAL,5
                        )
        grid_a_param.Add(grid_a_ctrl)
        grid_sizer_pane3_base.Add(grid_a_param, 1, wx.ALL, 15)
        grid_sizer_in_column2.Add(self.rdbx_normalize, 0, wx.TOP, 5)
        grid_sizer_in_column2.Add((20, 20), 0, wx.EXPAND | wx.TOP, 5)
        grid_sizer_in_column2.Add(self.btn_voldect, 0, wx.TOP, 10)
        grid_sizer_in_column2.Add((20, 20), 0, wx.EXPAND | wx.TOP, 5)
        grid_sizer_in_column2.Add(self.btn_details, 0, wx.TOP, 10)
        grid_sizer_in_column2.Add((20, 20), 0, wx.EXPAND | wx.TOP, 5)
        grid_sizer_in_column2.Add(self.lab_amplitude, 0, wx.TOP, 10)
        grid_sizer_in_column2.Add(self.spin_target, 0, wx.TOP, 5)
        
        grid_sizer_in_column2.Add(self.lab_i, 0, wx.TOP, 10)
        grid_sizer_in_column2.Add(self.spin_i, 0, wx.TOP, 5)
        grid_sizer_in_column2.Add(self.lab_tp, 0, wx.TOP, 10)
        grid_sizer_in_column2.Add(self.spin_tp, 0, wx.TOP, 5)
        grid_sizer_in_column2.Add(self.lab_lra, 0, wx.TOP, 10)
        grid_sizer_in_column2.Add(self.spin_lra, 0, wx.TOP, 5)
        
        sizer_pane3_audio_column2.Add(grid_sizer_in_column2, 1, wx.ALL, 15)
        grid_sizer_pane3_base.Add(sizer_pane3_audio_column2, 1, wx.ALL, 0)
        sizer_pane3_base.Add(grid_sizer_pane3_base, 0, 
                                        wx.ALL|
                                        wx.ALIGN_CENTER_HORIZONTAL|
                                        wx.ALIGN_CENTER_VERTICAL,
                                        20
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
        self.notebook_1.AddPage(self.notebook_1_pane_1, 
                                (_("Video Container")))
        self.notebook_1.AddPage(self.notebook_1_pane_2, 
                                (_("Video Settings")))
        self.notebook_1.AddPage(self.notebook_1_pane_3, 
                                (_("Audio Settings")))
        self.notebook_1.AddPage(self.notebook_1_pane_4, 
                                (_("h.264/h.265 Options")))
        grid_sizer_base.Add(self.notebook_1, 1, wx.ALL | wx.EXPAND, 5)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(self.sizer_base)
        self.Layout()
        
        #----------------------Set Properties----------------------#
        self.cmbx_vidContainers.SetToolTip(_('The output Video container'))
        
        self.ckbx_pass.SetToolTip(_('It can improve the video quality and '
                                    'reduce the file size, but takes longer.'))
        self.rdb_deadline.SetToolTip(_('"good" is the default and recommended '
                'for most applications; "best" is recommended if you have lots '
                'of time and want the best compression efficiency; "realtime" '
                'is recommended for live/fast encoding'))
        self.spin_cpu.SetToolTip(_('"cpu-used" sets how efficient the '
                'compression will be. The meaning depends on the mode above.'))
        self.spin_Vbrate.SetToolTip(_('The bit rate determines the quality and '
                'the final video size. A larger value correspond to greater '
                'quality and size of the file.'))
        self.slider_CRF.SetToolTip(_('CRF (constant rate factor) Affects the '
                'quality of the final video. Only used with x264/x265 encoders '
                'on one-pass (two-pass encoding switchs to bitrate). With '
                'lower values the quality is higher and a larger file size.'))
        self.btn_preview.SetToolTip(_('Try the filters by playing a '
                                      'video preview'))
        self.btn_reset.SetToolTip(_("Clear all enabled filters "))
        self.cmbx_Vaspect.SetToolTip(_('Video aspect (Aspect Ratio) is the '
                'video width and video height ratio. Leave on "Default" to '
                'copy the original settings.'))
        self.cmbx_Vrate.SetToolTip(_('Video Rate: A any video consists of'
                'of images displayed as frames, repeated a given number of '
                'times per second. In countries are 30 NTSC, PAL countries '
                '(like Italy) are 25. Leave on "Default" to copy the '
                'original settings.'))
        self.btn_voldect.SetToolTip(_('Gets maximum volume and average volume '
                'data in dBFS, then calculates the offset amount for audio '
                'normalization.'))
        self.spin_target.SetToolTip(_('Limiter for the maximum peak level or '
                'the mean level (when switch to RMS) in dBFS. From -99.0 to '
                '+0.0; default for PEAK level is -1.0; default for RMS is '
                '-20.0'))
        self.spin_i.SetToolTip(_('Integrated Loudness Target in LUFS. '
                                 'From -70.0 to -5.0, default is -24.0'))
        self.spin_tp.SetToolTip(_('Maximum True Peak in dBTP. From -9.0 '
                                  'to +0.0, default is -2.0'))
        self.spin_lra.SetToolTip(_('Loudness Range Target in LUFS. '
                                   'From +1.0 to +20.0, default is +7.0'))
        self.rdb_a.SetToolTip(_('Audio codecs compatible with the chosen '
                                'video container'))
        self.notebook_1_pane_4.SetToolTip(_('Options enabled for the codecs '
                                            'x.264/x.265'))

        #----------------------Binding (EVT)----------------------#
        """
        Note: wx.EVT_TEXT_ENTER é diverso da wx.EVT_TEXT . Il primo é sensibile
        agli input di tastiera, il secondo é sensibile agli input di tastiera
        ma anche agli "append"
        """
        #self.Bind(wx.EVT_COMBOBOX, self.vidContainers, self.cmbx_vidContainers)
        self.cmbx_vidContainers.Bind(wx.EVT_COMBOBOX, self.vidContainers)
        self.Bind(wx.EVT_RADIOBOX, self.on_Deadline, self.rdb_deadline)
        self.Bind(wx.EVT_CHECKBOX, self.on_Pass, self.ckbx_pass)
        self.Bind(wx.EVT_SPINCTRL, self.on_Bitrate, self.spin_Vbrate)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.on_Crf, self.slider_CRF)
        self.Bind(wx.EVT_BUTTON, self.on_Enable_vsize, self.btn_videosize)
        self.Bind(wx.EVT_BUTTON, self.on_Enable_crop, self.btn_crop)
        self.Bind(wx.EVT_BUTTON, self.on_Enable_rotate, self.btn_rotate)
        self.Bind(wx.EVT_BUTTON, self.on_Enable_lacing, self.btn_lacing)
        self.Bind(wx.EVT_BUTTON, self.on_Enable_denoiser, self.btn_denois)
        self.Bind(wx.EVT_BUTTON, self.on_FiltersPreview, self.btn_preview)
        self.Bind(wx.EVT_BUTTON, self.on_FiltersClear, self.btn_reset)
        self.Bind(wx.EVT_COMBOBOX, self.on_Vaspect, self.cmbx_Vaspect)
        self.Bind(wx.EVT_COMBOBOX, self.on_Vrate, self.cmbx_Vrate)
        self.Bind(wx.EVT_RADIOBOX, self.on_AudioFormats, self.rdb_a)
        self.Bind(wx.EVT_BUTTON, self.on_AudioParam, self.btn_aparam)
        self.Bind(wx.EVT_RADIOBOX, self.onNormalize, self.rdbx_normalize)
        self.Bind(wx.EVT_SPINCTRL, self.on_enter_Ampl, self.spin_target)
        self.Bind(wx.EVT_BUTTON, self.on_Audio_analyzes, self.btn_voldect)
        self.Bind(wx.EVT_RADIOBOX, self.on_h264Presets, self.rdb_h264preset)
        self.Bind(wx.EVT_RADIOBOX, self.on_h264Profiles, self.rdb_h264profile)
        self.Bind(wx.EVT_RADIOBOX, self.on_h264Tunes, self.rdb_h264tune)
        self.Bind(wx.EVT_BUTTON, self.on_Show_normlist, self.btn_details)
        #self.Bind(wx.EVT_CLOSE, self.Quiet) # controlla la x di chiusura

        #-------------------------------------- initialize default layout:
        cmd_opt["VidCmbxStr"] = "MKV (h.264/AVC)"
        cmd_opt["VideoFormat"] = "mkv"
        cmd_opt["VideoCodec"] = "-c:v libx264"
        cmd_opt["YUV"] = "-pix_fmt yuv420p"
        cmd_opt["VideoAspect"] = ""
        cmd_opt["VideoRate"] = ""
        self.rdb_a.SetSelection(0), self.cmbx_vidContainers.SetSelection(9)
        self.ckbx_pass.SetValue(False), self.slider_CRF.SetValue(23)
        self.cmbx_Vrate.SetSelection(0), self.cmbx_Vaspect.SetSelection(0), 
        self.UI_set()
        self.audio_default()
        self.normalize_default()

    #-------------------------------------------------------------------#
    def UI_set(self, opt265=False):
        """
        Update all the GUI widgets based on the choices made by the user.
        """
        if cmd_opt["VideoCodec"] in ["-c:v libx264", "-c:v libx265"]:
            self.sizer_automations_staticbox.SetLabel('')
            self.spin_cpu.Hide(), self.lab_cpu.Hide(), self.rdb_deadline.Hide()
            self.ckbx_multithread.Hide()
            if cmd_opt["VideoCodec"] == "-c:v libx264":
                self.slider_CRF.SetValue(23)
            elif cmd_opt["VideoCodec"] == "-c:v libx265":
                self.slider_CRF.SetValue(28)
            self.notebook_1_pane_4.Enable(), self.btn_videosize.Enable() 
            self.btn_crop.Enable(), self.btn_rotate.Enable() 
            self.btn_lacing.Enable(), self.btn_denois.Enable() 
            self.btn_preview.Enable(), self.slider_CRF.SetMax(51)
            self.ckbx_pass.Enable()
        
        elif cmd_opt["VideoCodec"] in ["-c:v libvpx","-c:v libvpx-vp9", 
                                       "-c:v libaom-av1 -strict -2"]:
            self.sizer_automations_staticbox.SetLabel(
                                        _('Controlling Speed and Quality'))
            self.spin_cpu.Show(), self.lab_cpu.Show(), self.rdb_deadline.Show()
            self.ckbx_multithread.Show(), self.ckbx_multithread.SetValue(True)
            self.rdb_deadline.SetSelection(1)
            self.spin_cpu.SetRange(0, 5)
            self.notebook_1_pane_1.Layout()
            self.slider_CRF.SetMax(63), self.slider_CRF.SetValue(31)
            self.notebook_1_pane_4.Disable(), self.btn_videosize.Enable()
            self.btn_crop.Enable(), self.btn_rotate.Enable()
            self.btn_lacing.Enable(), self.btn_denois.Enable()
            self.btn_preview.Enable(), self.ckbx_pass.Enable()
            
        elif cmd_opt["VideoCodec"] == "-c:v copy":
            self.sizer_automations_staticbox.SetLabel('')
            self.spin_cpu.Hide(), self.lab_cpu.Hide(), self.rdb_deadline.Hide()
            self.ckbx_multithread.Hide()
            self.spin_Vbrate.Disable(), self.btn_videosize.Disable() 
            self.btn_crop.Disable(), self.btn_rotate.Disable()
            self.btn_lacing.Disable(), self.btn_denois.Disable() 
            self.btn_preview.Disable(), self.notebook_1_pane_4.Disable() 
            self.ckbx_pass.Disable()
            
        else: # all others containers that not use h264
            self.sizer_automations_staticbox.SetLabel('')
            self.spin_cpu.Hide(), self.lab_cpu.Hide(), self.rdb_deadline.Hide()
            self.ckbx_multithread.Hide()
            self.notebook_1_pane_4.Disable()
            self.btn_videosize.Enable(), 
            self.btn_crop.Enable(), self.btn_rotate.Enable() 
            self.btn_lacing.Enable(), self.btn_denois.Enable()
            self.btn_preview.Enable(), self.ckbx_pass.Enable()
        
        if self.rdbx_normalize.GetSelection() == 3: 
            self.ckbx_pass.SetValue(True)
        else:
            self.ckbx_pass.SetValue(False)
        self.on_Pass(self) 
        
        if opt265:
            if cmd_opt["VideoCodec"] == "-c:v libx265":
                for n in [1,2,4]:
                    self.rdb_h264tune.EnableItem(n,enable=False)
            elif cmd_opt["VideoCodec"] == "-c:v libx264":
                for n in [1,2,4]:
                    self.rdb_h264tune.EnableItem(n,enable=True)
            
        self.rdb_h264preset.SetSelection(0), self.on_h264Presets(self)
        self.rdb_h264profile.SetSelection(0), self.on_h264Profiles(self)
        self.rdb_h264tune.SetSelection(0), self.on_h264Tunes(self)
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
        self.btn_aparam.SetBottomEndColour(wx.Colour(self.btn_color))
        self.txt_audio_options.SetValue('')
        #self.rdbx_normalize.Enable()
    #-------------------------------------------------------------------#
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
        
        self.btn_voldect.Hide()
        self.spin_target.Hide(), self.spin_target.SetValue(-1.0)
        self.btn_details.Hide(), self.lab_amplitude.Hide() 
        self.lab_i.Hide(), self.lab_tp.Hide(), self.lab_lra.Hide() 
        self.spin_i.Hide(), self.spin_tp.Hide(), self.spin_lra.Hide()
        self.btn_voldect.SetForegroundColour(wx.Colour(self.fBtnC))
        cmd_opt["PEAK"], cmd_opt["EBU"], cmd_opt["RMS"] = "", "", ""
        del self.normdetails[:]
    
    #----------------------Event handler (callback)----------------------#
    #------------------------------------------------------------------#
    def vidContainers(self, event):
        """
        The event chosen in the video format combobox triggers the 
        setting to the default values. The selection of a new format 
        determines the default status, enabling or disabling some 
        functions depending on the type of video format chosen.
        """
        selected = self.cmbx_vidContainers.GetValue()
        
        if vcodecs[selected][0] in ["-c:v libx264", "-c:v libx265", 
                                    "-c:v libaom-av1 -strict -2"]:
            if vcodecs[selected][0] == "-c:v libx264":
                cmd_opt["VideoCodec"] = "-c:v libx264"
                
            elif vcodecs[selected][0] == "-c:v libx265":
                cmd_opt["VideoCodec"] = "-c:v libx265"
                
            elif vcodecs[selected][0] == "-c:v libaom-av1 -strict -2":
                cmd_opt["VideoCodec"] = "-c:v libaom-av1 -strict -2"
        
            cmd_opt["VidCmbxStr"] = "%s" % (selected)# output form.
            cmd_opt['VideoFormat'] = "%s" % (vcodecs[selected][1])# format
            cmd_opt["Bitrate"] = ""
            cmd_opt["CRF"] = ""
            cmd_opt["YUV"] = "-pix_fmt yuv420p"
            
        elif vcodecs[selected][0] in ["-c:v libvpx","-c:v libvpx-vp9"]:
            if vcodecs[selected][0] == "-c:v libvpx":
                cmd_opt["VideoCodec"] = "-c:v libvpx"
            else:
                cmd_opt["VideoCodec"] = "-c:v libvpx-vp9"
            cmd_opt["VidCmbxStr"] = "%s" % (selected)# output form.
            cmd_opt['VideoFormat'] = "%s" % (vcodecs[selected][1])# format
            cmd_opt["Bitrate"] = ""
            cmd_opt["CRF"] = ""
            cmd_opt["YUV"] = "-pix_fmt yuv420p"
            
        elif vcodecs[selected][0] == "":# copy video codec
            cmd_opt["Passing"] = "single"
            cmd_opt["VidCmbxStr"] = "%s" % (selected)
            cmd_opt['VideoFormat'] = "%s" % ( vcodecs[selected][1])
            cmd_opt["VideoCodec"] = "-c:v copy"
            cmd_opt["YUV"] = ""

        else: # not h264/h265
            cmd_opt["VidCmbxStr"] = "%s" % (selected)
            cmd_opt['VideoFormat'] = "%s" % (vcodecs[selected][1])
            cmd_opt["VideoCodec"] = "%s" %(vcodecs[selected][0])
            cmd_opt["Bitrate"] = ""
            cmd_opt["CRF"] = ""
            cmd_opt["YUV"] = ""
        
        self.UI_set(True)
        self.audio_default() # reset audio radiobox and dict
        self.setAudioRadiobox(self)
        
    #------------------------------------------------------------------#

    def on_Pass(self, event):
        """
        enable or disable functionality for two pass encoding
        """
        if self.ckbx_pass.IsChecked():
            cmd_opt["Passing"] = "double"
            if cmd_opt["VideoCodec"] in ["-c:v libvpx","-c:v libvpx-vp9"]:
                self.slider_CRF.Enable()
                self.spin_Vbrate.Enable()
            else:   
                self.slider_CRF.Disable()
                self.spin_Vbrate.Enable()
        else:
            cmd_opt["Passing"] = "single"
            if cmd_opt["VideoCodec"] in ["-c:v libx264", "-c:v libx265"]:
                self.slider_CRF.Enable()
                self.spin_Vbrate.Disable()
                
            elif cmd_opt["VideoCodec"] in ["-c:v libvpx","-c:v libvpx-vp9",
                                           "-c:v libaom-av1 -strict -2"]:
                self.slider_CRF.Enable()
                self.spin_Vbrate.Enable()
                
            elif cmd_opt["VideoCodec"] == "-c:v copy":
                self.slider_CRF.Disable()
                self.spin_Vbrate.Disable()
            else:
                self.slider_CRF.Disable()
                self.spin_Vbrate.Enable()
    #------------------------------------------------------------------#
    def on_Bitrate(self, event):
        """
        Reset a empty CRF (this depend if is h264 two-pass encoding
        or if not codec h264)
        """
        if cmd_opt["VideoCodec"] == "-c:v libaom-av1 -strict -2":
            if self.ckbx_pass.IsChecked():
                cmd_opt["CRF"] = ""
                
        if not cmd_opt["VideoCodec"] in ["-c:v libvpx","-c:v libvpx-vp9", 
                                         "-c:v libaom-av1 -strict -2"]:
            cmd_opt["CRF"] = ""
            
        cmd_opt["Bitrate"] = "-b:v %sk" % (self.spin_Vbrate.GetValue())

        
    #------------------------------------------------------------------#
    def on_Crf(self, event):
        """
        Reset bitrate at empty (this depend if is h264 codec)
        """
        if not cmd_opt["VideoCodec"] in ["-c:v libvpx","-c:v libvpx-vp9", 
                                         "-c:v libaom-av1 -strict -2"]:
            cmd_opt["Bitrate"] = ""
        cmd_opt["CRF"] = "-crf %s" % self.slider_CRF.GetValue()
        
    #------------------------------------------------------------------#
    def on_Deadline(self, event):
        """
        Sets range according to spin_cpu used
        
        """
        if self.rdb_deadline.GetSelection() in [0,1]:
            self.spin_cpu.SetRange(0, 5), self.spin_cpu.SetValue(0)
        else:
            self.spin_cpu.SetRange(0, 15), self.spin_cpu.SetValue(0)
        
        
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
            self.btn_videosize.SetBottomEndColour(wx.Colour(self.btn_color))
            self.btn_crop.SetBottomEndColour(wx.Colour(self.btn_color))
            self.btn_denois.SetBottomEndColour(wx.Colour(self.btn_color))
            self.btn_lacing.SetBottomEndColour(wx.Colour(self.btn_color))
            self.btn_rotate.SetBottomEndColour(wx.Colour(self.btn_color))
    #------------------------------------------------------------------#
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
            cmd_opt['Filters'] = "-vf %s" % filters
        else:
            cmd_opt['Filters'] = ""
            
        #print (cmd_opt["Filters"])
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
               self.btn_videosize.SetBottomEndColour(wx.Colour(self.btn_color))
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
                self.btn_rotate.SetBottomEndColour(wx.Colour(self.btn_color))
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
                self.btn_crop.SetBottomEndColour(wx.Colour(self.btn_color))
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
                self.btn_lacing.SetBottomEndColour(wx.Colour(self.btn_color))
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
                self.btn_denois.SetBottomEndColour(wx.Colour(self.btn_color))
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
        val = self.cmbx_Vrate.GetValue()
        if val == "Default ":
            cmd_opt["VideoRate"] = ""
        else:
            cmd_opt["VideoRate"] = "-r %s" % val.split(' ')[0]
            
    #------------------------------------------------------------------#
    def setAudioRadiobox(self, event):
        """
        set the compatible audio formats with selected video format 
        on audio radiobox (see av_formats dict.) 
        * except when 'Copy video codec' is selected
        """
        cmb_str = self.cmbx_vidContainers.GetValue()
        
        if cmb_str == _('Copy video codec'):# enable all audio sel.
            for n,v in enumerate(av_formats.keys()):
                self.rdb_a.EnableItem(n,enable=True)
        else:
            for n,v in enumerate(av_formats[vcodecs[cmb_str][1]]):
                if v:
                    self.rdb_a.EnableItem(n,enable=True)
                else:
                    self.rdb_a.EnableItem(n,enable=False)
                    
        self.rdb_a.SetSelection(0)
        
    #------------------------------------------------------------------#
    def on_AudioFormats(self, event):
        """
        When choose an item on audio radiobox list, set the audio format 
        name and audio codec command (see acodecs dict.). Also  set the 
        view of the audio normalize widgets and reset values some cmd_opt 
        keys.
        """
        audioformat = self.rdb_a.GetStringSelection()
        #------------------------------------------------------
        def param(enablenormalization, enablebuttonparameters):
            cmd_opt["AudioBitrate"] = ["",""]
            cmd_opt["AudioChannel"] = ["",""]
            cmd_opt["AudioRate"] = ["",""]
            cmd_opt["AudioDepth"] = ["",""]

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
                self.btn_aparam.SetForegroundColour(wx.Colour(165,165,165))
                self.btn_aparam.SetBottomEndColour(wx.Colour(self.btn_color))
        #--------------------------------------------------------
        for n in acodecs.values():
            if audioformat in n[0]:
                if audioformat == _("Default (managed by FFmpeg)"):
                    self.audio_default()
                    self.rdbx_normalize.Enable()

                elif audioformat == _("Try to copy audio source"):
                    self.normalize_default()
                    param(False, False)

                elif audioformat == _("No audio stream (silent)"):
                    self.normalize_default()
                    param(False, False)
                    break
                else:
                    param(True, True)
                    
                cmd_opt["Audio"] = audioformat
                cmd_opt["AudioCodec"] = n[1]
            
    #-------------------------------------------------------------------#
    def on_AudioParam(self, event):
        """
        Call audio_dialog method and pass the respective parameters 
        of the selected audio codec 
        """ 
        pcm = ["-c:a pcm_s16le","-c:a pcm_s24le","-c:a pcm_s32le",]
        
        if cmd_opt["AudioCodec"] in pcm:
            self.audio_dialog("wav", "Audio wav parameter (%s)"
                              % cmd_opt["AudioCodec"])
        else:
            for k,v in acodecs.items():
                if cmd_opt["AudioCodec"] == v[1]:
                    self.audio_dialog(k, "%s encoding parameters (%s)" 
                                      % (k,v[1].split()[1]))
        
        #print (cmd_opt["AudioCodec"])
            
    #-------------------------------------------------------------------#
    def audio_dialog(self, audio_type, title):
        """
        Starts a dialog to select the audio parameters, then sets the values 
        on the cmd_opt dictionary.
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
            self.btn_aparam.SetBottomEndColour(wx.Colour(self.btn_color))
        else:
            self.btn_aparam.SetBottomEndColour(wx.Colour(0, 240, 0))
            
        audiodialog.Destroy()

    #------------------------------------------------------------------#
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
        if self.rdbx_normalize.GetSelection() == 1:# is checked
            self.normalize_default(False)
            self.parent.statusbar_msg(msg_1, azure)
            self.btn_voldect.Show(), self.spin_target.Show()
            self.lab_amplitude.Show()
        
        elif self.rdbx_normalize.GetSelection() == 2:
            self.normalize_default(False)
            self.parent.statusbar_msg(msg_2, '#15A660')
            self.btn_voldect.Show(), self.spin_target.Show()
            self.lab_amplitude.Show(), self.spin_target.SetValue(-20)
            
        elif self.rdbx_normalize.GetSelection() == 3:
            self.parent.statusbar_msg(msg_3, '#87A615')
            self.normalize_default(False)
            self.lab_i.Show(), self.lab_tp.Show(), self.lab_lra.Show(),
            self.spin_i.Show(), self.spin_tp.Show(), self.spin_lra.Show()
            self.ckbx_pass.SetValue(True), self.ckbx_pass.Disable()
            cmd_opt["Passing"] = "double"
            if not self.cmbx_vidContainers.GetSelection() == 16:#copycodec
                self.on_Pass(self)
        else:
            self.parent.statusbar_msg(_("Audio normalization off"), None)
            self.normalize_default(False)

        self.notebook_1_pane_3.Layout()
        
        if not self.rdbx_normalize.GetSelection() == 3: 
            if not self.cmbx_vidContainers.GetSelection() == 16:#copycodec
                self.ckbx_pass.Enable()
                
        if self.cmbx_vidContainers.GetSelection() == 16:#copycodec
            if not self.rdbx_normalize.GetSelection() == 3: 
                self.ckbx_pass.SetValue(False)
        
    #------------------------------------------------------------------#
    def on_enter_Ampl(self, event):
        """
        when spin_amplitude is changed enable 'Volumedected' to
        update new incomming
        
        """
        if not self.btn_voldect.IsEnabled():
            self.btn_voldect.Enable()
            self.btn_voldect.SetForegroundColour(wx.Colour(self.fBtnC))
        
    #------------------------------------------------------------------#
    def on_Audio_analyzes(self, event):  # Volumedetect button
        """
        Evaluates the user's choices and directs them to the references 
        for audio normalizations based on PEAK or RMS .
        """
        file_sources = self.parent.file_sources[:]
        
        if self.rdbx_normalize.GetSelection() == 1:
            self.max_volume_PEAK(file_sources)
            
        elif self.rdbx_normalize.GetSelection() == 2:
            self.mean_volume_RMS(file_sources)

    #------------------------------------------------------------------#
    def max_volume_PEAK(self, file_sources):  # Volumedetect button
        """
        Analyzes to get MAXIMUM peak levels data to calculates offset in
        dBFS values need for audio normalization process.
        
        """
        msg2 = (_('Audio normalization is required only for some files'))
        msg3 = (_('Audio normalization is not required based to '
                  'set target level'))
        if self.normdetails:
            del self.normdetails[:]
        
        self.parent.statusbar_msg("",None)
        self.time_seq = self.parent.time_seq #from -ss to -t will be analyzed
        target = self.spin_target.GetValue()

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
                offset = float(maxvol) - float(target)
                result = float(maxvol) - offset
                
                if float(maxvol) == float(target):
                    volume.append('  ')
                else:
                    volume.append("-af volume=%fdB" % -offset)
                    
                self.normdetails.append((f, 
                                         maxvol,
                                         meanvol,
                                         str(offset),
                                         str(result),
                                         ))
                    
        if [a for a in volume if not '  ' in a] == []:
             self.parent.statusbar_msg(msg3, orange)
        else:
            if len(volume) == 1 or not '  ' in volume:
                 pass
            else:
                self.parent.statusbar_msg(msg2, yellow)
                
        cmd_opt["PEAK"] = volume
        self.btn_voldect.Disable()
        self.btn_voldect.SetForegroundColour(wx.Colour(165,165, 165))
        self.btn_details.Show()
        self.notebook_1_pane_3.Layout()

    #------------------------------------------------------------------#
    def mean_volume_RMS(self, file_sources):  # Volumedetect button
        """
        Analyzes to get MEAN peak levels data to calculates RMS offset in dB
        need for audio normalization process.
        """
        msg2 = (_('Audio normalization is required only for some files'))
        msg3 = (_('Audio normalization is not required based to '
                  'set target level'))
        if self.normdetails:
            del self.normdetails[:]
        
        self.parent.statusbar_msg("",None)
        self.time_seq = self.parent.time_seq #from -ss to -t will be analyzed
        target = self.spin_target.GetValue()

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
                offset = float(meanvol) - float(target)
                result = float(maxvol) - offset
                
                if offset == 0.0:
                    volume.append('  ')
                else:
                    volume.append("-af volume=%fdB" % -offset)
                    
                self.normdetails.append((f, 
                                         maxvol,
                                         meanvol,
                                         str(offset),
                                         str(result),
                                         ))
                    
        if [a for a in volume if not '  ' in a] == []:
             self.parent.statusbar_msg(msg3, orange)
        else:
            if len(volume) == 1 or not '  ' in volume:
                 pass
            else:
                self.parent.statusbar_msg(msg2, yellow)
                
        cmd_opt["RMS"] = volume
        self.btn_voldect.Disable()
        self.btn_voldect.SetForegroundColour(wx.Colour(165,165, 165))
        self.btn_details.Show()
        self.notebook_1_pane_3.Layout()
        
    #------------------------------------------------------------------#
    def on_Show_normlist(self, event):
        """
        Show a wx.ListCtrl dialog with volumedected data
        """
        if cmd_opt["PEAK"]:
            title = _('PEAK-based volume statistics')
        elif cmd_opt["RMS"]:
            title = _('RMS-based volume statistics')
            
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

    def exportStreams(self, exported):
        """
        Set the parent.post_process attribute to communicate the
        file available for playback or display metadata.
        """
        if not exported:
            return
        else:
            self.parent.post_process = exported
            self.parent.postExported_enable()
    #-------------------------------------------------------------------#
    
    def update_allentries(self):
        """
        Update some entries, is callaed by on_ok method.
        
        """
        self.time_seq = self.parent.time_seq
        #self.on_Vrate(self), self.on_Vaspect(self)
        #if cmd_opt["VideoCodec"] in ["-c:v libvpx","-c:v libvpx-vp9"]:
            #self.on_Bitrate(self), self.on_Crf(self)
        #else:
        if self.spin_Vbrate.IsEnabled() and not self.slider_CRF.IsEnabled():
            self.on_Bitrate(self)
            
        elif self.slider_CRF.IsEnabled() and not self.spin_Vbrate.IsEnabled():
            self.on_Crf(self)
            
        elif self.slider_CRF.IsEnabled() and self.spin_Vbrate.IsEnabled():
            self.on_Bitrate(self), self.on_Crf(self)
        else:
            cmd_opt["CRF"] = ''
            cmd_opt["Bitrate"] = ''
        
        if self.rdb_deadline.IsShown():
            deadline = self.rdb_deadline.GetStringSelection()
            cmd_opt["CpuUsed"] = '-cpu-used %s' % self.spin_cpu.GetValue()
            cmd_opt["Deadline"] = '-deadline %s' % deadline
            if self.ckbx_multithread.IsChecked():
                cmd_opt["RowMthreading"] = '-row-mt 1'
            else:
                cmd_opt["RowMthreading"] = ''
        else:
            cmd_opt["CpuUsed"] = ''
            cmd_opt["Deadline"] = ''
            cmd_opt["RowMthreading"] = ''
            
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
        if self.rdbx_normalize.GetSelection() in [1,2]:
            if self.btn_voldect.IsEnabled():
                wx.MessageBox(_('Undetected volume values! use the '
                                '"Volumedetect" control button to analyze '
                                'the data on the audio volume.'),
                                'Videomass', wx.ICON_INFORMATION)
                return
            
        # make a different id need to avoid attribute overwrite:
        file_sources = self.parent.file_sources[:]
        # make a different id need to avoid attribute overwrite:
        dir_destin = self.file_destin
        # used for file log name
        logname = 'Videomass_VideoConversion.log'

        # CHECKING:
        if self.cmbx_vidContainers.GetValue() == _("Copy video codec"):
            self.time_seq = self.parent.time_seq
            checking = inspect(file_sources, dir_destin, '')
        else:
            self.update_allentries()# last update of all setting interface
            checking = inspect(file_sources, dir_destin, cmd_opt["VideoFormat"])
            
        if not checking[0]: # the user changing idea or not such files exist
            return
        
        (typeproc, file_sources, dir_destin,
        filename, base_name, countmax) = checking
    
        if self.rdbx_normalize.GetSelection() == 3: # EBU
            self.ebu_2pass(file_sources, dir_destin, countmax, logname)
            
        else:
            self.stdProc(file_sources, dir_destin, countmax, logname)
        
        return

    #------------------------------------------------------------------#
    def stdProc(self, file_sources, dir_destin, countmax, logname):
        """
        Define the ffmpeg command strings for batch process.
        
        """
        audnorm = cmd_opt["RMS"] if not cmd_opt["PEAK"] else cmd_opt["PEAK"]
            
        if self.cmbx_vidContainers.GetValue() == _("Copy video codec"):
            command = ('%s %s %s %s %s %s %s %s %s %s' %(
                                                    cmd_opt["VideoCodec"], 
                                                    cmd_opt["VideoAspect"],
                                                    cmd_opt["VideoRate"],
                                                    cmd_opt["AudioCodec"], 
                                                    cmd_opt["AudioBitrate"][1], 
                                                    cmd_opt["AudioRate"][1], 
                                                    cmd_opt["AudioChannel"][1], 
                                                    cmd_opt["AudioDepth"][1], 
                                                    self.threads,
                                                    cmd_opt["Map"],
                                                        ))
            command = " ".join(command.split())# mi formatta la stringa
            valupdate = self.update_dict(countmax, ["Copy video codec"] )
            ending = Formula(self,valupdate[0],valupdate[1],'Copy video codec')
            
            if ending.ShowModal() == wx.ID_OK:
                self.parent.switch_Process('common',
                                           file_sources, 
                                           '', 
                                           dir_destin, 
                                           command, 
                                           None, 
                                           '',
                                           audnorm, 
                                           logname, 
                                           countmax,
                                           )
                #used for play preview and mediainfo:
                f = '%s/%s' % (dir_destin[0], os.path.basename(file_sources[0]))
                self.exportStreams(f)#call function more above
                
        elif cmd_opt["Passing"] == "double":
            cmd1 = ('-an %s %s %s %s %s %s %s %s %s %s %s %s %s %s '
                    '-f rawvideo' %(cmd_opt["VideoCodec"],
                                    cmd_opt["CRF"],
                                    cmd_opt["Bitrate"], 
                                    cmd_opt["Deadline"],
                                    cmd_opt["CpuUsed"],
                                    cmd_opt["RowMthreading"],
                                    cmd_opt["Presets"], 
                                    cmd_opt["Profile"], 
                                    cmd_opt["Tune"], 
                                    cmd_opt["VideoAspect"], 
                                    cmd_opt["VideoRate"], 
                                    cmd_opt["Filters"], 
                                    cmd_opt["YUV"], 
                                    self.threads,
                                    ))
            cmd2= ('%s %s %s %s %s %s %s %s %s %s %s '
                   '%s %s %s %s %s %s %s %s %s' %(cmd_opt["VideoCodec"],
                                                  cmd_opt["CRF"],
                                                  cmd_opt["Bitrate"], 
                                                  cmd_opt["Deadline"],
                                                  cmd_opt["CpuUsed"],
                                                  cmd_opt["RowMthreading"],
                                                  cmd_opt["Presets"], 
                                                  cmd_opt["Profile"], 
                                                  cmd_opt["Tune"], 
                                                  cmd_opt["VideoAspect"], 
                                                  cmd_opt["VideoRate"], 
                                                  cmd_opt["Filters"], 
                                                  cmd_opt["YUV"], 
                                                  cmd_opt["AudioCodec"], 
                                                  cmd_opt["AudioBitrate"][1], 
                                                  cmd_opt["AudioRate"][1], 
                                                  cmd_opt["AudioChannel"][1], 
                                                  cmd_opt["AudioDepth"][1], 
                                                  self.threads, 
                                                  cmd_opt["Map"],
                                                  ))
            pass1 = " ".join(cmd1.split())
            pass2 =  " ".join(cmd2.split())
            valupdate = self.update_dict(countmax, [''])
            title = 'Two pass Video Encoding'
            ending = Formula(self, valupdate[0], valupdate[1], title)
            
            if ending.ShowModal() == wx.ID_OK:
                self.parent.switch_Process('doublepass',
                                           file_sources, 
                                           cmd_opt['VideoFormat'], 
                                           dir_destin, 
                                           None, 
                                           [pass1, pass2], 
                                           '',
                                           audnorm, 
                                           logname, 
                                           countmax,
                                           )
                #used for play preview and mediainfo:
                f = os.path.basename(file_sources[0]).rsplit('.', 1)[0]
                self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                              cmd_opt["VideoFormat"]))
            #ending.Destroy() # con ID_OK e ID_CANCEL non serve Destroy()

        elif cmd_opt["Passing"] == "single": # Batch-Mode / h264 Codec
            command = ('%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s '
                       '%s %s %s %s' % (cmd_opt["VideoCodec"], 
                                        cmd_opt["CRF"],
                                        cmd_opt["Bitrate"],
                                        cmd_opt["Deadline"],
                                        cmd_opt["CpuUsed"],
                                        cmd_opt["RowMthreading"],
                                        cmd_opt["Presets"], 
                                        cmd_opt["Profile"],
                                        cmd_opt["Tune"], 
                                        cmd_opt["VideoAspect"], 
                                        cmd_opt["VideoRate"], 
                                        cmd_opt["Filters"],
                                        cmd_opt["YUV"], 
                                        cmd_opt["AudioCodec"], 
                                        cmd_opt["AudioBitrate"][1], 
                                        cmd_opt["AudioRate"][1], 
                                        cmd_opt["AudioChannel"][1], 
                                        cmd_opt["AudioDepth"][1], 
                                        self.threads, 
                                        cmd_opt["Map"],
                                        ))
            command = " ".join(command.split())# mi formatta la stringa
            valupdate = self.update_dict(countmax, [''])
            title = 'Standard Video Encoding'
            ending = Formula(self, valupdate[0], valupdate[1], title)
            
            if ending.ShowModal() == wx.ID_OK:
                self.parent.switch_Process('common',
                                           file_sources, 
                                           cmd_opt['VideoFormat'], 
                                           dir_destin, 
                                           command, 
                                           None, 
                                           '',
                                           audnorm, 
                                           logname, 
                                           countmax, 
                                           )
                #used for play preview and mediainfo:
                f = os.path.basename(file_sources[0]).rsplit('.', 1)[0]
                self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                                 cmd_opt["VideoFormat"]))

    #------------------------------------------------------------------#
    def ebu_2pass(self, file_sources, dir_destin, countmax, logname):
        """
        Define the ffmpeg command strings for batch process with
        EBU two-passes conversion 
        
        """
        title = _('Audio/Video EBU normalization')
        cmd_opt["EBU"] = 'EBU R128'
        loudfilter = ('loudnorm=I=%s:TP=%s:LRA=%s:print_format=summary' %( 
                                              str(self.spin_i.GetValue()),
                                              str(self.spin_tp.GetValue()),
                                              str(self.spin_lra.GetValue()),))
        
        if self.cmbx_vidContainers.GetValue() == _("Copy video codec"):
            cmd_1 = ('%s %s %s %s %s' %(cmd_opt["VideoCodec"], 
                                        cmd_opt["VideoAspect"],
                                        cmd_opt["VideoRate"],
                                        self.threads,
                                        cmd_opt["Map"],
                                        ))
            cmd_2 = ('%s %s %s %s %s %s %s %s %s %s' %(cmd_opt["VideoCodec"], 
                                                       cmd_opt["VideoAspect"],
                                                       cmd_opt["VideoRate"],
                                                       cmd_opt["AudioCodec"], 
                                                       cmd_opt["AudioBitrate"][1], 
                                                       cmd_opt["AudioRate"][1], 
                                                       cmd_opt["AudioChannel"][1], 
                                                       cmd_opt["AudioDepth"][1], 
                                                       self.threads,
                                                       cmd_opt["Map"],
                                                       ))
            pass1 = " ".join(cmd_1.split())
            pass2 = " ".join(cmd_2.split())
            valupdate = self.update_dict(countmax, ["Copy video codec"])
            ending = Formula(self, valupdate[0], valupdate[1], title)
            
            if ending.ShowModal() == wx.ID_OK:
                self.parent.switch_Process('EBU normalization',
                                           file_sources, 
                                           '', 
                                           dir_destin, 
                                           cmd_opt["VideoFormat"], 
                                           [pass1, pass2, loudfilter, False], 
                                           '',
                                           '', 
                                           logname, 
                                           countmax,
                                           )
                #used for play preview and mediainfo:
                f = '%s/%s' % (dir_destin[0], os.path.basename(file_sources[0]))
                self.exportStreams(f)#pass arg to function above
        
        else:
            cmd_1 = ('%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s' % (
                                                    cmd_opt["VideoCodec"], 
                                                    cmd_opt["CRF"],
                                                    cmd_opt["Bitrate"],
                                                    cmd_opt["Deadline"],
                                                    cmd_opt["CpuUsed"],
                                                    cmd_opt["RowMthreading"],
                                                    cmd_opt["Presets"], 
                                                    cmd_opt["Profile"], 
                                                    cmd_opt["Tune"], 
                                                    cmd_opt["VideoAspect"], 
                                                    cmd_opt["VideoRate"], 
                                                    cmd_opt["Filters"], 
                                                    cmd_opt["YUV"], 
                                                    self.threads,
                                                    cmd_opt["Map"],
                                                    ))
                
            cmd_2= ('%s %s %s %s %s %s %s %s %s %s %s '
                    '%s %s %s %s %s %s %s %s %s' %(cmd_opt["VideoCodec"], 
                                                   cmd_opt["CRF"],
                                                   cmd_opt["Bitrate"], 
                                                   cmd_opt["Deadline"],
                                                   cmd_opt["CpuUsed"],
                                                   cmd_opt["RowMthreading"],
                                                   cmd_opt["Presets"], 
                                                   cmd_opt["Profile"],
                                                   cmd_opt["Tune"], 
                                                   cmd_opt["VideoAspect"], 
                                                   cmd_opt["VideoRate"], 
                                                   cmd_opt["Filters"],
                                                   cmd_opt["YUV"], 
                                                   cmd_opt["AudioCodec"], 
                                                   cmd_opt["AudioBitrate"][1], 
                                                   cmd_opt["AudioRate"][1], 
                                                   cmd_opt["AudioChannel"][1], 
                                                   cmd_opt["AudioDepth"][1], 
                                                   self.threads, 
                                                   cmd_opt["Map"],
                                                   ))
            pass1 = " ".join(cmd_1.split())
            pass2 =  " ".join(cmd_2.split())# mi formatta la stringa
            valupdate = self.update_dict(countmax, [''])
            ending = Formula(self, valupdate[0], valupdate[1], title)
            
            if ending.ShowModal() == wx.ID_OK:
                self.parent.switch_Process('EBU normalization',
                                           file_sources, 
                                           '', 
                                           dir_destin, 
                                           cmd_opt["VideoFormat"], 
                                           [pass1, pass2, loudfilter, True], 
                                           '',
                                           '', 
                                           logname, 
                                           countmax,
                                           )
                #used for play preview and mediainfo:
                f = os.path.basename(file_sources[0]).rsplit('.', 1)[0]
                self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                                 cmd_opt["VideoFormat"]))
            #ending.Destroy() # con ID_OK e ID_CANCEL non serve Destroy()
    #------------------------------------------------------------------#
    def update_dict(self, countmax, prof):
        """
        This method is required for update all cmd_opt
        dictionary values before send to epilogue
        """
        numfile = _("%s file in pending") % str(countmax)
        if cmd_opt["PEAK"]:
            normalize = 'PEAK'
        elif cmd_opt["RMS"]:
            normalize = 'RMS'
        elif cmd_opt["EBU"]:
            normalize = 'EBU R128'
        else:
            normalize = _('Disabled')
        if not self.parent.time_seq:
            time = _('Disabled')
        else:
            t = list(self.parent.time_read.items())
            time = '{0}: {1} | {2}: {3}'.format(t[0][0], t[0][1][0], 
                                                t[1][0], t[1][1][0])
        #------------------
        if prof[0] == "Copy video codec":
            formula = (_("SUMMARY\n\nFile to Queue\nVideo Format\
                        \nVideo Codec\nVideo Aspect\nVideo Rate\
                        \nAudio Format\nAudio Codec\nAudio Channels\
                        \nAudio Rate\nAudio bit-rate\nBit per Sample\
                        \nAudio Normalization\nMap\nTime selection\
                        \nThreads"))
            dictions = ("\n\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\
                         \n%s\n%s\n%s" %(numfile, 
                                         cmd_opt["VidCmbxStr"], 
                                         cmd_opt["VideoCodec"], 
                                         cmd_opt["VideoAspect"], 
                                         cmd_opt["VideoRate"], 
                                         cmd_opt["Audio"], 
                                         cmd_opt["AudioCodec"], 
                                         cmd_opt["AudioChannel"][0], 
                                         cmd_opt["AudioRate"][0], 
                                         cmd_opt["AudioBitrate"][0], 
                                         cmd_opt["AudioDepth"][0], 
                                         normalize, 
                                         cmd_opt["Map"], 
                                         time,
                                         self.threads.split()[1],
                                         ))
        #--------------------
        else:
            formula = (_("SUMMARY\n\nFile to Queue\
                         \nVideo Format\nPass Encoding\nVideo Codec\
                         \nVideo bit-rate\nCRF\nVP8/VP9 Options\
                         \nApplied Filters\nVideo Aspect\nVideo Rate\
                         \nPreset h.264/h.265\nProfile h.264/h.265\
                         \nTune h.264/h.265\nAudio Format\nAudio codec\
                         \nAudio Channels\nAudio Rate\nAudio bit-rate\
                         \nBit per Sample\nAudio Normalization\nMap\
                         \nTime selection\nThreads"
                         ))
            dictions = ("\n\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\
                        \n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\
                        \n%s" % (numfile, 
                                 cmd_opt["VidCmbxStr"], 
                                 cmd_opt["Passing"],
                                 cmd_opt["VideoCodec"], 
                                 cmd_opt["Bitrate"], 
                                 cmd_opt["CRF"],
                                '%s %s %s' %(cmd_opt["Deadline"], 
                                                cmd_opt["CpuUsed"],
                                                cmd_opt["RowMthreading"],
                                                ),
                                 cmd_opt["Filters"], 
                                 cmd_opt["VideoAspect"], 
                                 cmd_opt["VideoRate"], 
                                 cmd_opt["Presets"], 
                                 cmd_opt["Profile"], 
                                 cmd_opt["Tune"], 
                                 cmd_opt["Audio"], 
                                 cmd_opt["AudioCodec"], 
                                 cmd_opt["AudioChannel"][0], 
                                 cmd_opt["AudioRate"][0], 
                                 cmd_opt["AudioBitrate"][0], 
                                 cmd_opt["AudioDepth"][0],
                                 normalize, 
                                 cmd_opt["Map"], 
                                 time,
                                 self.threads.split()[1],
                                ))
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
        
        if cmd_opt["PEAK"]:
            normalize = cmd_opt["PEAK"][0]
        elif cmd_opt["RMS"]:
            normalize = cmd_opt["RMS"][0]# tengo il primo valore lista 
        else:
            normalize = ''
        
        if not self.ckbx_pass.IsChecked():
            if self.cmbx_vidContainers.GetValue() == _("Copy video codec"):
                outext = cmd_opt["VideoFormat"]
                command = ('%s %s %s %s %s %s %s %s %s %s %s' % (
                                                    normalize,
                                                    cmd_opt["VideoCodec"], 
                                                    cmd_opt["VideoAspect"],
                                                    cmd_opt["VideoRate"],
                                                    cmd_opt["AudioCodec"], 
                                                    cmd_opt["AudioBitrate"][1], 
                                                    cmd_opt["AudioRate"][1], 
                                                    cmd_opt["AudioChannel"][1], 
                                                    cmd_opt["AudioDepth"][1], 
                                                    self.threads,
                                                    cmd_opt["Map"],
                                                    ))
            else:
                outext = cmd_opt["VideoFormat"]
                command = ('%s %s %s %s %s %s %s %s %s %s %s %s %s %s '
                           '%s %s %s %s %s %s %s' %(normalize, 
                                                    cmd_opt["VideoCodec"], 
                                                    cmd_opt["CRF"], 
                                                    cmd_opt["Bitrate"], 
                                                    cmd_opt["Deadline"],
                                                    cmd_opt["CpuUsed"],
                                                    cmd_opt["RowMthreading"],
                                                    cmd_opt["Presets"], 
                                                    cmd_opt["Profile"], 
                                                    cmd_opt["Tune"], 
                                                    cmd_opt["VideoAspect"], 
                                                    cmd_opt["VideoRate"], 
                                                    cmd_opt["Filters"], 
                                                    cmd_opt["YUV"], 
                                                    cmd_opt["AudioCodec"], 
                                                    cmd_opt["AudioBitrate"][1], 
                                                    cmd_opt["AudioRate"][1], 
                                                    cmd_opt["AudioChannel"][1], 
                                                    cmd_opt["AudioDepth"][1], 
                                                    self.threads,
                                                    cmd_opt["Map"],
                                                    ))
        else:
            outext = cmd_opt["VideoFormat"]
            cmd1 = ('-an %s %s %s %s %s %s %s %s %s %s %s %s %s %s '
                    '-f rawvideo' %(cmd_opt["VideoCodec"],
                                    cmd_opt["CRF"],
                                    cmd_opt["Bitrate"], 
                                    cmd_opt["Deadline"],
                                    cmd_opt["CpuUsed"],
                                    cmd_opt["RowMthreading"],
                                    cmd_opt["Presets"], 
                                    cmd_opt["Profile"], 
                                    cmd_opt["Tune"], 
                                    cmd_opt["VideoAspect"], 
                                    cmd_opt["VideoRate"], 
                                    cmd_opt["Filters"], 
                                    cmd_opt["YUV"], 
                                    self.threads,
                                    ))
            cmd2= ('%s %s %s %s %s %s %s %s %s %s %s '
                   '%s %s %s %s %s %s %s %s %s' %(cmd_opt["VideoCodec"],
                                                  cmd_opt["CRF"],
                                                  cmd_opt["Bitrate"], 
                                                  cmd_opt["Deadline"],
                                                  cmd_opt["CpuUsed"],
                                                  cmd_opt["RowMthreading"],
                                                  cmd_opt["Presets"], 
                                                  cmd_opt["Profile"], 
                                                  cmd_opt["Tune"], 
                                                  cmd_opt["VideoAspect"], 
                                                  cmd_opt["VideoRate"], 
                                                  cmd_opt["Filters"], 
                                                  cmd_opt["YUV"], 
                                                  cmd_opt["AudioCodec"], 
                                                  cmd_opt["AudioBitrate"][1], 
                                                  cmd_opt["AudioRate"][1], 
                                                  cmd_opt["AudioChannel"][1], 
                                                  cmd_opt["AudioDepth"][1], 
                                                  self.threads, 
                                                  cmd_opt["Map"],
                                                  ))
            command = ("-pass 1 %s -pass 2 %s" % (cmd1,cmd2))
                       
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
