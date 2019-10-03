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
from videomass3.vdms_IO.IO_tools import FFProbe
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
           "AudioDepth": ["",""], "NormPEAK": "", "NormEBU": "",
           "Deinterlace": "", "Interlace": "", "Map": "-map 0", 
           "PixelFormat": "", "Orientation": ["",""],"Crop": "",
           "Scale": "", "Setdar": "", "Setsar": "", "Denoiser": "", 
           "Filters": "", "Shortest": [False,""], "AddAudioStream": "",
           "PicturesFormat": "", "YUV": "", "A_Copied": [],
           "A_exportExt": [], "A_CodecCopied": [],
           }
# Namings in the video container selection combo box:
vcodecs = {("AVI (XVID mpeg4)"): ("-vcodec mpeg4 -vtag xvid","avi"), 
            ("AVI (FFmpeg mpeg4)"): ("-vcodec mpeg4","avi"), 
            ("AVI (ITU h264)"): ("-vcodec libx264","avi"),
            ("MP4 (mpeg4)"): ("-vcodec mpeg4","mp4"), 
            ("MP4 (HQ h264/AVC)"): ("-vcodec libx264","mp4"), 
            ("M4V (HQ h264/AVC)"): ("-vcodec libx264","m4v"), 
            ("MKV (h264)"): ("-vcodec libx264","mkv"),
            ("OGG theora"): ("-vcodec libtheora","ogg"), 
            ("WebM (HTML5)"): ("-vcodec libvpx","webm"), 
            ("FLV (HQ h264/AVC)"): ("-vcodec libx264","flv"),
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
           ('copy'): (_("Try to copy audio source"), "-c:a copy"),
           ('silent'): (_("No audio stream (silent)"), "-an")
           }
# compatibility between video formats and related audio codecs:
av_formats = {('avi'): ('default','wav',None,None,None,'ac3',None,'mp3',
                       'copy','silent'),
              ('flv'): ('default',None,None,'aac',None,'ac3',None,'mp3',
                       'copy','silent'),
              ('mp4'): ('default',None,None,'aac',None,'ac3',None,'mp3',
                       'copy','silent'),
              ('m4v'): ('default',None,None,'aac','alac',None,None,None,
                       'copy','silent'),
              ('mkv'): ('default','wav','flac','aac',None,'ac3','ogg','mp3',
                       'copy','silent'),
              ('webm'): ('default',None,None,None,None,None,'ogg',None,
                        'copy','silent'),
              ('ogg'): ('default',None,'flac',None,None,None,'ogg',None,
                       'copy','silent')
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
                    "stillimage","psnr","ssim","fastecode",
                    "zerolatency"
                    )
            }
# set widget colours in some case with html rappresentetion:
azure = '#15a6a6' # rgb form (wx.Colour(217,255,255))
yellow = '#a29500'
red = '#ea312d'
orange = '#f28924'
greenolive = '#6aaf23'
ciano = '#61ccc7' # rgb 97, 204, 199
violet = '#D64E93'

class Video_Conv(wx.Panel):
    """
    Interface panel for video conversions
    """
    def __init__(self, parent, ffmpeg_link, ffplay_link, ffprobe_link, 
                 threads, cpu_used, ffmpeg_loglev, ffplay_loglev, OS, 
                 iconplay, iconreset, iconresize, iconcrop, iconrotate, 
                 icondeinterlace, icondenoiser, iconanalyzes, iconsettings,
                 iconpeaklevel, iconatrack):

        wx.Panel.__init__(self, parent)

        # set attributes:
        self.parent = parent
        self.ffmpeg_link = ffmpeg_link
        self.ffplay_link = ffplay_link
        self.ffprobe_link = ffprobe_link
        self.threads = threads
        self.cpu_used = cpu_used if not cpu_used == 'Disabled' else ''
        self.ffmpeg_loglev = ffmpeg_loglev
        self.ffplay_loglev = ffplay_loglev
        self.file_sources = []
        self.file_destin = ''
        self.normdetails = []
        self.OS = OS
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
        self.rdb_auto = wx.RadioBox(self.notebook_1_pane_1, wx.ID_ANY, 
                                   (_("Automations")), choices=[
                                            (_("Disable")), 
                                            (_("Pictures from Video")), 
                                            (_("Merging Audio and Video ")), 
                                            (_("Picture slideshow maker")),
                                            (_("Extract Audio from Video")),
                                                                ], 
                                    majorDimension=0, 
                                    style=wx.RA_SPECIFY_ROWS
                                            )
        self.shortest = wx.CheckBox(self.notebook_1_pane_1, wx.ID_ANY, 
                                     (_("Shortest"))
                                     )
        audiotrack = wx.Bitmap(iconatrack, wx.BITMAP_TYPE_ANY)
        self.btn_audioAdd = GB.GradientButton(self.notebook_1_pane_1,
                                              wx.ID_OPEN,
                                            size=(-1,25),
                                            bitmap=audiotrack,
                                            label=_("Add audio track"))
        self.btn_audioAdd.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(28,28, 28))
        self.btn_audioAdd.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_audioAdd.SetBottomStartColour(wx.Colour(205, 235, 222))
        self.btn_audioAdd.SetTopStartColour(wx.Colour(205, 235, 222))
        self.btn_audioAdd.SetTopEndColour(wx.Colour(205, 235, 222))
        
        self.cmbx_pictformat = wx.ComboBox(self.notebook_1_pane_1, wx.ID_ANY,
                                           choices=[("jpg"),("png"),("bmp"),], 
                                           size=(100,-1),
                                           style=wx.CB_DROPDOWN | 
                                           wx.CB_READONLY
                                           )
        self.spin_ctrl_bitrate = wx.SpinCtrl(self.notebook_1_pane_1, wx.ID_ANY, 
                                             "1500", min=0, max=25000, 
                                             style=wx.TE_PROCESS_ENTER
                                             )
        self.sizer_bitrate_staticbox = wx.StaticBox(self.notebook_1_pane_1, 
                                                    wx.ID_ANY, 
                                                 (_("Video Bit-Rate Value"))
                                                    )
        self.slider_CRF = wx.Slider(self.notebook_1_pane_1, wx.ID_ANY, 
                                    1, 0, 51, size=(230, -1),style=wx.SL_HORIZONTAL | 
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
                                                      wx.ID_ANY, 
                                                      (_("Video Filters"))
                                                      )
        self.cmbx_Vaspect = wx.ComboBox(self.notebook_1_pane_2, wx.ID_ANY,
                                        size=(200, -1), choices=[
                                                        ("Default "), 
                                                        ("4:3"), 
                                                        ("16:9")], 
                                        style=wx.CB_DROPDOWN | 
                                        wx.CB_READONLY
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
                                               ("0.2 fps for images"), 
                                               ("0.5 fps for images"),
                                               ("1 fps for images"), 
                                               ("1.5 fps for images"), 
                                               ("2 fps for images")
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
                                     (_('Disable')), 
                                     (_('Peak Level-based')), 
                                     (_('Loudness using EBU R128')),
                                              ], 
                                     majorDimension=0, 
                                     style=wx.RA_SPECIFY_ROWS,
                                            )
        analyzebmp = wx.Bitmap(iconanalyzes, wx.BITMAP_TYPE_ANY)
        self.btn_analyzes = GB.GradientButton(self.notebook_1_pane_3,
                                            size=(-1,25),
                                            bitmap=analyzebmp,
                                            label=_("Volumedetect"))
        self.btn_analyzes.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(28,28, 28))
        self.btn_analyzes.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_analyzes.SetBottomStartColour(wx.Colour(205, 235, 222))
        self.btn_analyzes.SetTopStartColour(wx.Colour(205, 235, 222))
        self.btn_analyzes.SetTopEndColour(wx.Colour(205, 235, 222))
        
        peaklevelbmp = wx.Bitmap(iconpeaklevel, wx.BITMAP_TYPE_ANY)
        self.btn_details = GB.GradientButton(self.notebook_1_pane_3,
                                            size=(-1,25),
                                            bitmap=peaklevelbmp,
                                            label=_("Peak levels index"))
        self.btn_details.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(28,28, 28))
        self.btn_details.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_details.SetBottomStartColour(wx.Colour(205, 235, 222))
        self.btn_details.SetTopStartColour(wx.Colour(205, 235, 222))
        self.btn_details.SetTopEndColour(wx.Colour(205, 235, 222))
        
        self.lab_amplitude = wx.StaticText(self.notebook_1_pane_3, wx.ID_ANY, 
                                    (_("Target level (dB level limiter)"))
                                    )
        self.spin_amplitude = FS.FloatSpin(self.notebook_1_pane_3, 
                                                     wx.ID_ANY, 
                                                     min_val=-99.0, 
                                                     max_val=0.0, 
                                                     increment=1.0, value=-1.0, 
                                            agwStyle=FS.FS_LEFT, size=(-1,-1)
                                            )
        self.spin_amplitude.SetFormat("%f"), self.spin_amplitude.SetDigits(1)
        self.lab_i = wx.StaticText(self.notebook_1_pane_3, wx.ID_ANY, (
                             _("Set integrated loudness target:")))
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
        self.btn_aparam.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_aparam.SetBottomStartColour(wx.Colour(205, 235, 222))
        self.btn_aparam.SetTopStartColour(wx.Colour(205, 235, 222))
        self.btn_aparam.SetTopEndColour(wx.Colour(205, 235, 222))
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
        grid_sizer_automations = wx.GridSizer(6, 1, 0, 0)
        grid_sizer_automations.Add((20, 20), 0, wx.EXPAND | wx.ALL, 5)
        grid_sizer_automations.Add(self.rdb_auto, 0, wx.ALL| 
                                                    wx.ALIGN_CENTER_HORIZONTAL| 
                                                    wx.ALIGN_CENTER_VERTICAL, 
                                                    20
                                                    )
        grid_sizer_automations.Add((20, 20), 0, wx.EXPAND | wx.ALL, 5)
        grid_sizer_automations.Add(self.btn_audioAdd, 0, wx.ALL| 
                                                     wx.ALIGN_CENTER_HORIZONTAL| 
                                                     wx.ALIGN_CENTER_VERTICAL, 
                                                     20
                                                     )
        grid_sizer_automations.Add(self.shortest, 0, wx.ALL| 
                                                     wx.ALIGN_CENTER_HORIZONTAL| 
                                                     wx.ALIGN_CENTER_VERTICAL, 
                                                     20
                                                     )
        grid_sizer_automations.Add(self.cmbx_pictformat, 0, wx.ALL| 
                                                     wx.ALIGN_CENTER_HORIZONTAL| 
                                                     wx.ALIGN_CENTER_VERTICAL, 
                                                     20
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
        grid_sizer_in_column2.Add(self.btn_analyzes, 0, wx.TOP, 10)
        grid_sizer_in_column2.Add((20, 20), 0, wx.EXPAND | wx.TOP, 5)
        grid_sizer_in_column2.Add(self.btn_details, 0, wx.TOP, 10)
        grid_sizer_in_column2.Add((20, 20), 0, wx.EXPAND | wx.TOP, 5)
        grid_sizer_in_column2.Add(self.lab_amplitude, 0, wx.TOP, 10)
        grid_sizer_in_column2.Add(self.spin_amplitude, 0, wx.TOP, 5)
        
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
                                (_("H.264/X.264 Options")))
        grid_sizer_base.Add(self.notebook_1, 1, wx.ALL | wx.EXPAND, 5)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(self.sizer_base)
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
        self.shortest.SetToolTip(_('Selecting "Shortest" option, the audio '
                                   'will be cut to the video duration')
                                 )
        self.cmbx_pictformat.SetToolTip(_('Output format of the extracted '
                                        'pictures'))
        self.spin_ctrl_bitrate.SetToolTip(_("The bit rate determines the "
                                            "quality and the final video "
                                            "size. A larger value correspond "
                                            "to greater quality and size of "
                                            "the file.")
                                                 )
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
        
        self.cmbx_Vaspect.SetToolTip(_("Video aspect (Aspect Ratio) "
                        "is the video width and video height ratio. "
                        "Leave on 'Default' to copy the original settings."
                                                ))
        
        self.cmbx_Vrate.SetToolTip(_("Video Rate: A any video consists "
                    "of images displayed as frames, repeated a given number "
                    "of times per second. In countries are 30 NTSC, PAL "
                    "countries (like Italy) are 25. Leave on 'Default' "
                    "to copy the original settings."
                                   ))
        #self.rdbx_normalize.SetToolTip(_('Performs peak level audio '
                                    #'normalization on the audio stream'
                                           #))
        self.btn_analyzes.SetToolTip(_("Find the maximum and average peak "
                                       "levels in dB values and calculates "
                                       "the normalization data offset"
                                       ))
        self.spin_amplitude.SetToolTip(_("Limiter for the maximum "
                                        "peak level in dB. From -99.0 "
                                        "to +0.0 dB, default is -1.0"
                                                 ))
        self.spin_i.SetToolTip(_('Integrated Loudness Target in LUFS. '
                                 'From -70.0 to -5.0, default is -24.0'
                                 ))
        self.spin_tp.SetToolTip(_('Maximum True Peak in dBTP. From -9.0 '
                                  'to +0.0, default is -2.0'
                                  ))
        self.spin_lra.SetToolTip(_('Loudness Range Target in LUFS. '
                                   'From +1.0 to +20.0, default is +7.0'
                                   ))
        self.rdb_a.SetToolTip(_("Choose an audio codec. Some audio codecs "
                                "are disabled for certain video containers"
                                ))
        self.notebook_1_pane_4.SetToolTip(_('These parameters are enabled '
                                            'for the codecs h.264/x.264'))

        #----------------------Binding (EVT)----------------------#
        """
        Note: wx.EVT_TEXT_ENTER é diverso da wx.EVT_TEXT . Il primo é sensibile
        agli input di tastiera, il secondo é sensibile agli input di tastiera
        ma anche agli "append"
        """
        #self.Bind(wx.EVT_COMBOBOX, self.vidContainers, self.cmbx_vidContainers)
        self.cmbx_vidContainers.Bind(wx.EVT_COMBOBOX, self.vidContainers)
        self.Bind(wx.EVT_CHECKBOX, self.on_Pass, self.ckbx_pass)
        self.Bind(wx.EVT_RADIOBOX, self.on_Automation, self.rdb_auto)
        self.Bind(wx.EVT_CHECKBOX, self.on_Shortest, self.shortest)
        self.Bind(wx.EVT_BUTTON, self.on_AddaudioStr, self.btn_audioAdd)
        self.Bind(wx.EVT_COMBOBOX, self.on_PicturesFormat, self.cmbx_pictformat)
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
        self.Bind(wx.EVT_COMBOBOX, self.on_Vrate, self.cmbx_Vrate)
        self.Bind(wx.EVT_RADIOBOX, self.on_AudioFormats, self.rdb_a)
        self.Bind(wx.EVT_BUTTON, self.on_AudioParam, self.btn_aparam)
        self.Bind(wx.EVT_RADIOBOX, self.onNormalize, self.rdbx_normalize)
        self.Bind(wx.EVT_BUTTON, self.on_Audio_analyzes, self.btn_analyzes)
        self.Bind(wx.EVT_RADIOBOX, self.on_h264Presets, self.rdb_h264preset)
        self.Bind(wx.EVT_RADIOBOX, self.on_h264Profiles, self.rdb_h264profile)
        self.Bind(wx.EVT_RADIOBOX, self.on_h264Tunes, self.rdb_h264tune)
        self.Bind(wx.EVT_BUTTON, self.on_Show_normlist, self.btn_details)
        #self.Bind(wx.EVT_CLOSE, self.Quiet) # controlla la x di chiusura

        #-------------------------------------- initialize default layout:
        cmd_opt["VidCmbxStr"] = "MKV (h264)"
        cmd_opt["VideoFormat"] = "mkv"
        cmd_opt["VideoCodec"] = "-vcodec libx264"
        cmd_opt["YUV"] = "-pix_fmt yuv420p"
        cmd_opt["VideoAspect"] = ""
        cmd_opt["VideoRate"] = ""
        self.rdb_a.SetSelection(0)
        self.ckbx_pass.SetValue(False), self.slider_CRF.SetValue(23)
        self.rdb_h264preset.SetSelection(0), self.rdb_h264profile.SetSelection(0)
        self.rdb_h264tune.SetSelection(0), self.cmbx_Vrate.SetSelection(0)
        self.cmbx_Vaspect.SetSelection(0), self.rdb_auto.SetSelection(0)
        self.shortest.Hide(), self.btn_audioAdd.Hide()
        self.cmbx_pictformat.Hide(), self.cmbx_Vaspect.Enable()
        self.UI_set()
        self.audio_default()
        self.normalize_default()

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
        #self.rdbx_normalize.Enable()
    #-------------------------------------------------------------------#
    def normalize_default(self, setoff=True):
        """
        Set default normalization parameters of the audio panel. This method 
        is called by preset_manager.switch_video_conv() on first run and
        switch in this panel, or if there are changing on dragNdrop panel,
        (when make a clear file list or append new file), or if change video 
        container in the combobox.
        
        """
        if setoff:
            self.rdbx_normalize.SetSelection(0)
        if not self.btn_analyzes.IsEnabled():
                self.btn_analyzes.Enable()
        
        self.btn_analyzes.Hide()
        self.spin_amplitude.Hide(), self.spin_amplitude.SetValue(-1.0)
        self.btn_details.Hide(), self.lab_amplitude.Hide() 
        self.lab_i.Hide(), self.lab_tp.Hide(), self.lab_lra.Hide() 
        self.spin_i.Hide(), self.spin_tp.Hide(), self.spin_lra.Hide()
        self.btn_analyzes.SetForegroundColour(wx.Colour(28,28,28))
        cmd_opt["NormPEAK"], cmd_opt["NormEBU"] = "", ""
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
        self.audio_default() # reset audio radiobox and dict
        selected = self.cmbx_vidContainers.GetValue()
        #print (vcodecs[selected][0])
        
        if vcodecs[selected][0] == "-vcodec libx264":
            cmd_opt["VidCmbxStr"] = "%s" % (selected)# output form.
            cmd_opt['VideoFormat'] = "%s" % (vcodecs[selected][1])# format
            cmd_opt["VideoCodec"] = "-vcodec libx264"
            cmd_opt["Bitrate"] = ""
            cmd_opt["CRF"] = ""
            cmd_opt["YUV"] = "-pix_fmt yuv420p"
            self.parent.statusbar_msg("Output format: %s" % (
                                      cmd_opt['VideoFormat']),None)
            self.UI_set()
            
        elif vcodecs[selected][0] == "":# copy video codec
            cmd_opt["Passing"] = "single"
            cmd_opt["VidCmbxStr"] = "%s" % (selected)
            cmd_opt['VideoFormat'] = "%s" % ( vcodecs[selected][1])
            cmd_opt["VideoCodec"] = "-c:v copy"
            cmd_opt["YUV"] = ""
            self.parent.statusbar_msg("Output format: %s" % (
                                      cmd_opt['VideoFormat']),None)
            self.UI_set()

        else: # not x264/h264
            cmd_opt["VidCmbxStr"] = "%s" % (selected)
            cmd_opt['VideoFormat'] = "%s" % (vcodecs[selected][1])
            cmd_opt["VideoCodec"] = "%s" %(vcodecs[selected][0])
            cmd_opt["Bitrate"] = ""
            cmd_opt["CRF"] = ""
            cmd_opt["YUV"] = ""
            self.parent.statusbar_msg(_("Output format: %s") % (
                                    cmd_opt['VideoFormat']),None)
            self.UI_set()
            
        self.setAudioRadiobox(self)
        
    #------------------------------------------------------------------#
    def on_Automation(self, event):
        """
        This event allows you to select some functional automations, 
        sometimes with independent features and modes.
        
        """
        msg_1 = (_('Automations disabled'
                   ))
        msg_2 = (_('Tip: use the "Duration" tool, then try setting '
                   'the "Video Rate" to low values ​​0.2 fps / 0.5 fps'
                   ))
        msg_3 = (_('Tip: If audio format is supported by video format, use '
                   'audio and video copy options to speed up the process '
                   'without re-encoding'
                   ))
        msg_4 = (_('Tip: Import pictures ONLY (preferably in the same format), '
                   'then use the "Duration" tool to set pictures duration. '
                   'Use the "Resize > Scale" filter to resize same resolution'
                   ))
        msg_5 = (_('Tip: Import only video files that contain at least one '
                   'audio stream'
                   ))
        #-------------- On ACCESS first revert to default ----------------#
        self.ckbx_pass.Show(), self.ckbx_pass.SetValue(False),
        self.cmbx_pictformat.Hide(), self.cmbx_vidContainers.Show(),
        self.ckbx_pass.Show(), self.spin_ctrl_bitrate.Show(),
        self.slider_CRF.Show(),self.cmbx_Vaspect.Show(),
        self.shortest.Hide(), self.shortest.SetValue(True), 
        self.btn_audioAdd.Hide(), self.rdb_h264tune.SetSelection(0)
        self.notebook_1_pane_2.Enable(), 
        self.rdbx_normalize.EnableItem(2,enable=True)
        self.cmbx_vidContainers.Clear()
        for n in vcodecs.keys():
            self.cmbx_vidContainers.Append((n),)
        self.cmbx_vidContainers.SetStringSelection(cmd_opt["VidCmbxStr"])
        
        #------------------- start widgets settings ------------------#
        ####----------- Default
        if self.rdb_auto.GetSelection() == 0:
            self.parent.statusbar_msg(msg_1, '')
            
        ####-----------  Pictures from Video
        elif self.rdb_auto.GetSelection() == 1:
            if self.cmbx_vidContainers.GetValue() == _('Copy video codec'):
                self.cmbx_vidContainers.SetSelection(6)
                self.vidContainers(self)
            self.cmbx_pictformat.Show(), self.cmbx_pictformat.SetSelection(0)
            self.cmbx_vidContainers.Hide(),self.ckbx_pass.Hide(),
            self.spin_ctrl_bitrate.Hide(), self.slider_CRF.Hide(),
            self.cmbx_Vaspect.Hide(), self.notebook_1_pane_3.Disable(),
            self.notebook_1_pane_4.Disable()
            self.cmbx_Vrate.SetSelection(4), self.on_Vrate(self)

            cmd_opt["PicturesFormat"] = "jpg"
            self.parent.statusbar_msg(msg_2, greenolive)
            self.Layout()
            
            return
        ####----------- Add audio stream to a movie
        elif self.rdb_auto.GetSelection() == 2:
            self.vidContainers(self)####
            self.parent.statusbar_msg(msg_3, azure)
            self.btn_audioAdd.Show()
            self.cmbx_Vrate.SetSelection(0), self.on_Vrate(self)
            self.rdbx_normalize.EnableItem(2,enable=True)
            
            if cmd_opt["AddAudioStream"]:
                self.notebook_1_pane_3.Enable()
                cmd_opt["Shortest"] = [False,'-shortest']
            else:
                self.notebook_1_pane_3.Disable()
                cmd_opt["Shortest"] = [False,'']
            self.Layout()
            
            return
        ####----------- Picture slideshow maker
        elif self.rdb_auto.GetSelection() == 3:
            self.ckbx_pass.SetValue(False), self.ckbx_pass.Hide(),
            self.cmbx_vidContainers.Clear()
            for n in vcodecs.keys():
                if 'h264' in n:
                    self.cmbx_vidContainers.Append((n),)
            self.cmbx_vidContainers.SetSelection(1)
            self.vidContainers(self)#### 
            self.spin_ctrl_bitrate.Hide()
            self.rdb_h264tune.SetSelection(4)
            self.cmbx_Vaspect.Hide()
            cmd_opt["Tune"] = "-tune:v stillimage"
            self.shortest.Show(), self.btn_audioAdd.Show()
            self.cmbx_Vrate.SetSelection(1), self.on_Vrate(self)
            if cmd_opt["AddAudioStream"]:
                self.notebook_1_pane_3.Enable()
            else:
                self.notebook_1_pane_3.Disable()
            self.rdbx_normalize.EnableItem(2,enable=False)
            self.parent.statusbar_msg(msg_4, violet)
            self.Layout()
            
            return
        ####----------- Extract audio from video
        elif self.rdb_auto.GetSelection() == 4:
            self.cmbx_vidContainers.Hide(), self.ckbx_pass.Hide(),
            self.slider_CRF.Hide(), self.spin_ctrl_bitrate.Hide(),
            self.notebook_1_pane_2.Disable(), self.notebook_1_pane_3.Disable(), 
            self.notebook_1_pane_4.Disable()
            self.parent.statusbar_msg(msg_5,wx.Colour('CORAL'))
            
            return
        #-------------- on EXIT first revert to default --------------#
        self.btn_audioAdd.SetBottomEndColour(wx.Colour(205, 235, 222))
        self.btn_audioAdd.SetLabel(_("Add audio track"))
        cmd_opt["Shortest"], cmd_opt["Map"] = [False,''], "-map 0"
        cmd_opt["PicturesFormat"], cmd_opt["AddAudioStream"] = "", ""
        cmd_opt["Tune"] = ""
        if not self.notebook_1_pane_3.IsEnabled():
            self.notebook_1_pane_3.Enable()
        self.vidContainers(self)
        self.cmbx_Vrate.SetSelection(0), self.on_Vrate(self)
        self.normalize_default()
        self.Layout()
        
    #------------------------------------------------------------------#
    def on_Shortest(self, event):
        """
        Enable or disable shortest option.  If checked, will take the 
        video stream duration. If un-checked, will take the audio track
        duration.
        
        """
        if not cmd_opt["AddAudioStream"]:
            return
        if self.shortest.IsChecked():
            cmd_opt["Shortest"] = [False, '-shortest']
        else:
            from videomass3.vdms_IO import IO_tools
            path = cmd_opt["AddAudioStream"].replace('-i ', '').replace('"','')
            s = IO_tools.probeDuration(path, self.ffprobe_link)
            cmd_opt["Shortest"] = [s[0], '']
            
    #------------------------------------------------------------------#
            
    def on_AddaudioStr(self, event):
        """
        Add audio track on video or to slideshow and sets the 
        `cmd_opt["AddAudioStream"]` value with audio pathname, the
        `cmd_opt["Map"]` value with new mapping. With slideshow
        option selected it also calls the `on_Shortest` method.
        
        """
        frmt = ["*.%s;" % (a) for a in ['wav','aiff','flac','oga',
                                        'ogg','m4a','aac','ac3','mp3']
                   ]
        f = ''.join(frmt)
        
        with wx.FileDialog(self, "Videomass: Open an audio file", 
                           wildcard="Audio source (%s)|%s" % (f, f),
                           style=wx.FD_OPEN | 
                           wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            cmd_opt["AddAudioStream"] = '-i "%s"' % pathname
        
        self.btn_audioAdd.SetBottomEndColour(wx.Colour(0, 240, 0))
        
        self.btn_audioAdd.SetLabel(_("%s audio") %(
                                        pathname.rsplit('.', 1)[1]).upper())
        self.notebook_1_pane_3.Enable()
        cmd_opt["Map"] = "-map 0:v:0 -map 1:a:0"
        self.normalize_default()
        
        if self.rdb_auto.GetStringSelection() == _("Merging Audio and Video "):
            cmd_opt["Shortest"] = [False,'-shortest']
            
        elif self.rdb_auto.GetStringSelection() == _("Picture slideshow maker"):
            #self.rdbx_normalize.EnableItem(1,enable=False)
            self.on_Shortest(self)

    #------------------------------------------------------------------#
    def on_PicturesFormat(self, event):
        """
        Set output format to save images fro movie. Values are jpg,
        png and bmp
        
        """
        cmd_opt["PicturesFormat"] = self.cmbx_pictformat.GetValue()
        self.rdb_h264tune.SetSelection(4)
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
        Reset a empty CRF (this depend if is h264 two-pass encoding
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
                self.btn_aparam.SetForegroundColour(wx.Colour(28,28,28))
                self.btn_aparam.SetBottomEndColour(wx.Colour(205, 235, 222))
            else:
                self.btn_aparam.Disable(), 
                self.txt_audio_options.SetValue('')
                self.btn_aparam.SetForegroundColour(wx.Colour(165,165,165))
                self.btn_aparam.SetBottomEndColour(wx.Colour(205, 235, 222))
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
        msg_1 = (_('Performs the Peak level normalization to a certain '
                   'target level by analyzing the audio stream to get the '
                   'maximum volume data.'
                   ))
        msg_2 = (_('Performs two passes normalization. It Normalizes the '
                   'perceived loudness using the "​loudnorm" filter, which '
                   'implements the EBU R128 algorithm.'
                   ))
        if self.rdbx_normalize.GetSelection() == 1:# is checked
            self.normalize_default(False)
            self.parent.statusbar_msg(msg_1, azure)
            self.btn_analyzes.Show(), self.spin_amplitude.Show()
            self.lab_amplitude.Show()
        
        elif self.rdbx_normalize.GetSelection() == 2:
            self.parent.statusbar_msg(msg_2, '#268826')
            self.normalize_default(False)
            self.lab_i.Show(), self.lab_tp.Show(), self.lab_lra.Show(),
            self.spin_i.Show(), self.spin_tp.Show(), self.spin_lra.Show()

        else:
            self.parent.statusbar_msg(_("Disable audio normalization"), None)
            self.normalize_default(False)

        self.notebook_1_pane_3.Layout()
        
    #------------------------------------------------------------------#
    def on_Audio_analyzes(self, event):  # analyzes button
        """
        If check, send to audio_analyzes.
        """
        if self.rdb_auto.GetSelection() in [2,3] and cmd_opt["AddAudioStream"]:
            path = cmd_opt["AddAudioStream"].replace('-i ', '').replace('"','')
            self.audio_analyzes([path])
        else:
            file_sources = self.parent.file_sources[:]
            self.audio_analyzes(file_sources)

    #------------------------------------------------------------------#
    def audio_analyzes(self, file_sources):  # analyzes button
        """
        Get audio peak level analyzes data for the offset calculation 
        need to normalization process.
        """
        msg1 = (_('Audio normalization will be applied'))
        msg2 = (_('Audio normalization is required only for some files'))
        msg3 = (_('Audio normalization is not required in according to '
                  'set target level'))
        
        self.parent.statusbar_msg("",None)
        self.time_seq = self.parent.time_seq #from -ss to -t will be analyzed
        normalize = self.spin_amplitude.GetValue()

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
                
        cmd_opt["NormPEAK"] = volume
        self.btn_analyzes.Disable()
        self.btn_analyzes.SetForegroundColour(wx.Colour(165,165, 165))
        self.btn_details.Show()
        self.notebook_1_pane_3.Layout()
        #self.btn_details.SetForegroundColour(wx.Colour(28,28,28))

    #------------------------------------------------------------------#
    def on_Show_normlist(self, event):
        """
        Show a wx.ListCtrl dialog to list data of peak levels
        """
        title = _('peak levels details index')
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
    #------------------------------------------------------------------#
    def audiocopy_extract(self, file_sources):
        """
        Try copying and saving the audio stream on a video by 
        recognizing the codec and then assigning a container/format. 
        If there is more than one audio stream in a video, a choice 
        is made to the user.
        """
        cmd_opt["A_exportExt"] = []
        cmd_opt["A_CodecCopied"] = []
        cmd_opt["A_Copied"] = []

        for files in file_sources:
            metadata = FFProbe(files, self.ffprobe_link, '-pretty') 
            # first execute a control for errors:
            if metadata.ERROR():
                wx.MessageBox("[FFprobe] Error:  %s" % (metadata.error), 
                              "ERROR - Videomass",
                wx.ICON_ERROR, self)
                return
            # Proceed with the istance method call:
            datastream = metadata.get_audio_codec_name()
            audio_list = datastream[0]

            if audio_list == None:
                wx.MessageBox(_("There are no audio streams:\n%s ") % (files), 
                                'Videomass', wx.ICON_INFORMATION, self)
                return

            elif len(audio_list) > 1:
                title = datastream[1]
                
                dlg = wx.SingleChoiceDialog(self, 
                        _("{0}\n\n"
                          "Contains multiple audio streams. " 
                          "Select which audio stream you want to "
                          "export between these:").format(title), 
                        _("Videomass: Stream choice"),
                        audio_list, wx.CHOICEDLG_STYLE
                                            )
                if dlg.ShowModal() == wx.ID_OK:
                    if dlg.GetStringSelection() in audio_list:
                        cn = ''.join(dlg.GetStringSelection()).split()[4]
                        indx = ''.join(dlg.GetStringSelection()).split()[1]
                        cmd_opt["A_CodecCopied"].append(
                                            "-map 0:%s -c copy" % indx)
                        cmd_opt["A_Copied"].append(cn)#used for epilogue
                        if cn in ('aac','alac'): cn = 'm4a'
                        if cn in ('ogg','vorbis'): cn = 'oga'
                        if cn.startswith('pcm_'): cn = 'wav'
                        cmd_opt["A_exportExt"].append(cn)
                    else:
                        wx.MessageBox(_("Nothing choice:\n%s ") % (files), 
                                        'Videomass: Error', wx.ICON_ERROR, 
                                        self)
                        return
                else: # there must be some choice (default first item list)
                    cn = ''.join(audio_list[0]).split()[4]
                    indx = ''.join(audio_list[0]).split()[1]
                    cmd_opt["A_CodecCopied"].append("-map 0:%s -c copy" % indx)
                    cmd_opt["A_Copied"].append(cn)#used for epilogue
                    if cn in ('aac','alac'): cn = 'm4a'
                    if cn in ('ogg','vorbis'): cn = 'oga'
                    if cn.startswith('pcm_'): cn = 'wav'
                    cmd_opt["A_exportExt"].append(cn)
                dlg.Destroy()
            else:
                cn = ''.join(audio_list[0]).split()[4]
                indx = ''.join(audio_list[0]).split()[1]
                cmd_opt["A_CodecCopied"].append("-map 0:%s -c copy" % indx)
                cmd_opt["A_Copied"].append(cn)#used for epilogue
                if cn in ('aac','alac'): cn = 'm4a'
                if cn in ('ogg','vorbis'): cn = 'oga'
                if cn.startswith('pcm_'): cn = 'wav'
                cmd_opt["A_exportExt"].append(cn)
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
        if self.rdbx_normalize.GetSelection() == 1:
            if self.btn_analyzes.IsEnabled():
                wx.MessageBox(_('Peak values not detected! use the '
                                '"Volumedetect" button before proceeding, '
                                'otherwise disable audio normalization.'),
                                'Videomass', wx.ICON_INFORMATION)
                return
        if self.rdb_auto.GetSelection() == 2:
            if not cmd_opt["AddAudioStream"]:
                wx.MessageBox(_('To add audio stream to a movie please '
                                'import an audio track with "Add audio track" '
                                'button.'), 'Videomass', wx.ICON_INFORMATION)
                return
        # make a different id need to avoid attribute overwrite:
        file_sources = self.parent.file_sources[:]
        # make a different id need to avoid attribute overwrite:
        dir_destin = self.file_destin
        # used for file log name
        logname = 'Videomass_VideoConversion.log'

        # CHECKING:
        if self.rdb_auto.GetSelection() == 4:
            file_sources = self.parent.file_sources[:]
            self.audiocopy_extract(file_sources)
            checking = inspect(file_sources, dir_destin, cmd_opt["A_exportExt"])
            
        elif self.cmbx_vidContainers.GetValue() == _("Copy video codec"):
            self.time_seq = self.parent.time_seq
            checking = inspect(file_sources, dir_destin, '')
            
        elif self.rdb_auto.GetSelection() == 1:# video to pictures
            self.time_seq = self.parent.time_seq
            checking = inspect(file_sources, dir_destin, 
                               cmd_opt["PicturesFormat"])
        else:
            self.update_allentries()# last update of all setting interface
            checking = inspect(file_sources, dir_destin, 
                            cmd_opt["VideoFormat"])
        if not checking[0]:
            # the user does not want to continue or not such files exist
            return
        
        (typeproc, file_sources, dir_destin,
        filename, base_name, countmax) = checking
    
        if self.rdb_auto.GetSelection() ==  1:
            self.saveimages(file_sources, dir_destin, logname)
    
        elif self.rdb_auto.GetSelection() == 3:
            self.slideShow(file_sources, dir_destin, logname)
        
        elif self.rdb_auto.GetSelection() == 4:
            self.audio_extract(file_sources, dir_destin, countmax, logname)
            
        elif self.rdbx_normalize.GetSelection() == 2: # EBU
            self.ebu_2pass(file_sources, dir_destin, countmax, logname)
            
        else:
            self.stdProc(file_sources, dir_destin, countmax, logname)
        
        return

    #------------------------------------------------------------------#
    def stdProc(self, file_sources, dir_destin, countmax, logname):
        """
        Define the ffmpeg command strings for batch process.
        
        """
        if self.cmbx_vidContainers.GetValue() == _("Copy video codec"):
            command = ('%s -loglevel %s %s %s %s %s %s %s %s %s %s %s %s '
                       '%s -y' %(
                       cmd_opt["AddAudioStream"],
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
                       cmd_opt["Map"],
                       cmd_opt["Shortest"][1])
                        )
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
                                           cmd_opt["NormPEAK"], 
                                           logname, 
                                           countmax,
                                           cmd_opt["Shortest"][0],
                                           )
                #used for play preview and mediainfo:
                f = '%s/%s' % (dir_destin[0], os.path.basename(file_sources[0]))
                self.exportStreams(f)#call function more above
                
        elif cmd_opt["Passing"] == "double":
            cmd1 = ('-an %s %s %s %s %s %s %s %s %s %s %s '
                    '-f rawvideo' %(cmd_opt["VideoCodec"], 
                                    cmd_opt["Bitrate"], 
                                    cmd_opt["Presets"], 
                                    cmd_opt["Profile"], 
                                    cmd_opt["Tune"], 
                                    cmd_opt["VideoAspect"], 
                                    cmd_opt["VideoRate"], 
                                    cmd_opt["Filters"], 
                                    cmd_opt["YUV"], 
                                    self.threads,
                                    self.cpu_used,
                                    ))
            cmd2= ('%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s '
                   '%s %s' % (cmd_opt["AddAudioStream"], 
                              cmd_opt["VideoCodec"], 
                              cmd_opt["Bitrate"], 
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
                              self.cpu_used, 
                              cmd_opt["Map"], 
                              cmd_opt["Shortest"][1]
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
                                           cmd_opt["NormPEAK"], 
                                           logname, 
                                           countmax, 
                                           cmd_opt["Shortest"][0],
                                           )
                #used for play preview and mediainfo:
                f = os.path.basename(file_sources[0]).rsplit('.', 1)[0]
                self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                              cmd_opt["VideoFormat"]))
            #ending.Destroy() # con ID_OK e ID_CANCEL non serve Destroy()

        elif cmd_opt["Passing"] == "single": # Batch-Mode / h264 Codec
            command = ('%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s '
                       '%s %s %s -y' % (cmd_opt["AddAudioStream"],
                                        cmd_opt["VideoCodec"], 
                                        cmd_opt["CRF"],
                                        cmd_opt["Bitrate"],
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
                                        self.cpu_used, 
                                        cmd_opt["Map"], 
                                        cmd_opt["Shortest"][1]
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
                                           cmd_opt["NormPEAK"], 
                                           logname, 
                                           countmax, 
                                           cmd_opt["Shortest"][0],
                                           )
                #used for play preview and mediainfo:
                f = os.path.basename(file_sources[0]).rsplit('.', 1)[0]
                self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                                 cmd_opt["VideoFormat"]))

    #------------------------------------------------------------------#
    def ebu_2pass(self, file_sources, dir_destin, countmax, logname):
        """
        Composes the ffmpeg command strings for batch process. 
        In double pass mode, split command in two part (see  
        os_processing.py at proc_batch_thread Class(Thread) ).
        
        """
        title = _('Two pass AV Loudnorm')
        cmd_opt["NormEBU"] = 'EBU R128'
        loudfilter = ('loudnorm=I=%s:TP=%s:LRA=%s:print_format=summary' %( 
                                              str(self.spin_i.GetValue()),
                                              str(self.spin_tp.GetValue()),
                                              str(self.spin_lra.GetValue()),))
        
        if self.cmbx_vidContainers.GetValue() == _("Copy video codec"):
            cmd_1 = ('%s %s %s %s %s %s %s %s' %(cmd_opt["AddAudioStream"],
                                                 cmd_opt["VideoCodec"], 
                                                 cmd_opt["VideoAspect"],
                                                 cmd_opt["VideoRate"],
                                                 self.threads, 
                                                 self.cpu_used,
                                                 cmd_opt["Map"],
                                                 cmd_opt["Shortest"][1])
                                                 )
            cmd_2 = ('%s %s %s %s %s %s %s %s %s %s %s %s %s' %(
                                                    cmd_opt["AddAudioStream"],
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
                                                    cmd_opt["Map"],
                                                    cmd_opt["Shortest"][1]))
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
                                           [pass1,pass2,loudfilter,None], 
                                           '',
                                           '', 
                                           logname, 
                                           countmax,
                                           cmd_opt["Shortest"][0],
                                           )
                #used for play preview and mediainfo:
                f = '%s/%s' % (dir_destin[0], os.path.basename(file_sources[0]))
                self.exportStreams(f)#pass arg to function above
        
        else:

            Vpass = True if cmd_opt["Passing"] == "double" else False

            cmd_1 = ('%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s' % (
                                                    cmd_opt["AddAudioStream"], 
                                                    cmd_opt["VideoCodec"], 
                                                    cmd_opt["Bitrate"],
                                                    cmd_opt["CRF"],
                                                    cmd_opt["Presets"], 
                                                    cmd_opt["Profile"], 
                                                    cmd_opt["Tune"], 
                                                    cmd_opt["VideoAspect"], 
                                                    cmd_opt["VideoRate"], 
                                                    cmd_opt["Filters"], 
                                                    cmd_opt["YUV"], 
                                                    self.threads, 
                                                    self.cpu_used,
                                                    cmd_opt["Map"], 
                                                    cmd_opt["Shortest"][1])
                    )
            cmd_2= ('%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s'
                    '%s %s' % (cmd_opt["AddAudioStream"],
                               cmd_opt["VideoCodec"], 
                               cmd_opt["Bitrate"], 
                               cmd_opt["CRF"],
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
                               self.cpu_used, 
                               cmd_opt["Map"], 
                               cmd_opt["Shortest"][1])
                    )
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
                                           [pass1, pass2, loudfilter, Vpass], 
                                           '',
                                           '', 
                                           logname, 
                                           countmax, 
                                           cmd_opt["Shortest"][0],
                                           )
                #used for play preview and mediainfo:
                f = os.path.basename(file_sources[0]).rsplit('.', 1)[0]
                self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                                 cmd_opt["VideoFormat"]))
            #ending.Destroy() # con ID_OK e ID_CANCEL non serve Destroy()

    def saveimages(self, file_sources, dest, logname):
        """
        Save as files image the selected video input. The saved 
        images are named as file name + a progressive number + .format 
        and placed in a folder with the same file name + a progressive 
        number in the chosen output path.
        
        """
        if len(file_sources) == 1:
            clicked = file_sources[0]
            
        elif not self.parent.import_clicked:
            wx.MessageBox(_('To export images, select one of the files '
                            'in the "Add files" panel'), 'Videomass', 
                            wx.ICON_INFORMATION, self)
            return
        else:
            clicked = self.parent.import_clicked
        
        title = _('Pictures from Video')
        valupdate = self.update_dict('1', ["Save as images"])
        ending = Formula(self, valupdate[0],valupdate[1], title)
        
        if ending.ShowModal() == wx.ID_OK:
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
            
            YUV = {'jpg':'-pix_fmt yuvj420p', 'png': '-pix_fmt rgb24', 
                   'bmp': '-pix_fmt bgr24' 
                       }
            fileout = "{0}-%d.{1}".format(fname,cmd_opt["PicturesFormat"])
            cmd = ('%s %s -i "%s" -loglevel %s -an %s %s %s '
                   '%s %s -y "%s/%s"' %(self.ffmpeg_link, 
                                        self.parent.time_seq,
                                        clicked, 
                                        self.ffmpeg_loglev,
                                        cmd_opt["VideoRate"],
                                        cmd_opt["Filters"],
                                        #cmd_opt["YUV"],
                                        YUV[cmd_opt["PicturesFormat"]],
                                        self.threads, 
                                        self.cpu_used,
                                        outputdir, 
                                        fileout,
                                        ))
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
                                        cmd_opt["Shortest"][0],
                                        )
    #------------------------------------------------------------------#
    def slideShow(self, file_sources, dest, logname):
        """
        this method allows to form the parameters for the realization 
        of a simple presentation or a movie with a single image
        
        """
        nopict = [f for f in file_sources if os.path.splitext(f)[1] 
                  not in ['.jpg','.png','.bmp','.JPG','.PNG','.BMP']]
        if nopict:
            wx.MessageBox(_('Please import only pictures in JPG, PNG or '
                            'BMP formats.'), 
                            'Videomass', 
                             wx.ICON_INFORMATION, self)
            return

        if not self.time_seq:
            wx.MessageBox(_('You should set a time length for the pictures: '
                            'Use the "Duration" tool setting ONLY "Cut (end '
                            'point)" and NOT "Search (start point)".\n\nThe '
                            'final video will have that duration multiplied '
                            'by the number of loaded pictures.'), 
                            'Videomass', 
                            wx.ICON_INFORMATION, self)
            return
        else:# convert time seconds
            time = self.parent.time_read['time']
        
        if not cmd_opt["Scale"]:
            if not len(file_sources) == 1:
                if wx.MessageBox(_('Make sure all imported images have the '
                                   'same resolution, otherwise you should set '
                                   'it with the Resize filter.\n\n'
                                   'Do the slideshow images have the same '
                                   'resolution?'), 
                                    _('Videomass: Please confirm'), 
                                                    wx.ICON_QUESTION | 
                                                    wx.YES_NO, 
                                                    self) == wx.NO:
                    return
        li = []
        for dir_ in os.listdir(dest[0]):
            if "Slideshow_" in dir_:
                li.append(int(dir_.split('Slideshow_')[1].split('.')[0]))
        if li:
            prog = max(li) +1
            outputdir = "%s/Slideshow_%d.%s" % (dest[0], prog, 
                                                 cmd_opt["VideoFormat"],)
        else:
            outputdir = "%s/Slideshow_1.%s" % (dest[0],cmd_opt["VideoFormat"],)
            
        cmd_1 = ['-loglevel %s' %(self.ffmpeg_loglev),
                 cmd_opt["Filters"]
                 ]
        cmd_2 = ['-loglevel %s -framerate '
                 '1/%s' % (self.ffmpeg_loglev, 
                           str(time[1]),
                           ),
                 #'%s -c:v libx264 %s %s %s %s -vf fps=25,format=yuv420p %s %s '
                 '%s -c:v libx264 %s %s %s %s %s -vf format=yuv420p %s %s '
                 '%s %s %s %s %s %s %s -y "%s"' % (cmd_opt["AddAudioStream"],
                                                   cmd_opt["CRF"],
                                                   cmd_opt["Presets"],
                                                   cmd_opt["Profile"],
                                                   cmd_opt["Tune"],
                                                   cmd_opt["VideoRate"],
                                                   cmd_opt["AudioCodec"], 
                                                   cmd_opt["AudioBitrate"][1], 
                                                   cmd_opt["AudioRate"][1], 
                                                   cmd_opt["AudioChannel"][1], 
                                                   cmd_opt["AudioDepth"][1],
                                                   self.threads, 
                                                   self.cpu_used,
                                                   cmd_opt["Map"], 
                                                   cmd_opt["Shortest"][1],
                                                   outputdir,
                                                   )
                 ]
        valupdate = self.update_dict(1, ['Slideshow', ''])
        ending = Formula(self, 
                         valupdate[0], 
                         valupdate[1], 
                         'Slideshows Maker'
                         )
        if ending.ShowModal() == wx.ID_OK:
            self.parent.switch_Process('slideshow',
                                        file_sources, 
                                        cmd_opt["VideoFormat"], 
                                        cmd_1, 
                                        cmd_2, 
                                        cmd_opt["VideoFormat"], 
                                        '',
                                        cmd_opt["NormPEAK"], 
                                        logname, 
                                        '1', 
                                        cmd_opt["Shortest"][0],
                                        )
            #used for play preview and mediainfo:
            self.exportStreams("%s" % outputdir)
    
    #------------------------------------------------------------------#
    def audio_extract(self, file_sources, dir_destin, countmax, logname):
        """
        Define the ffmpeg command strings for audio tracks extract
        from video.
        """
        title = _('Audio extract from video')
        cmdsplit1 = ("-vn")
        cmdsplit2 = ("%s %s -y" % (self.threads, self.cpu_used,))

        valupdate = self.update_dict(countmax, ['audio extract', ''])
        ending = Formula(self, valupdate[0], valupdate[1], title)
        
        if ending.ShowModal() == wx.ID_OK:
            self.parent.switch_Process('audioextract',
                                       '', 
                                       file_sources, #list
                                       dir_destin, #list
                                       cmdsplit1, 
                                       cmd_opt["A_CodecCopied"],#list
                                       cmdsplit2, 
                                       cmd_opt["A_exportExt"],#list
                                       logname, 
                                       countmax, #list
                                       False,# do not use is reserved
                                       )
            # used for play preview and mediainfo:
            f = os.path.basename(file_sources[0]).rsplit('.', 1)[0]
            self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                             cmd_opt["A_exportExt"][0]))
            
    #------------------------------------------------------------------#
    #------------------------------------------------------------------#
    def update_dict(self, countmax, prof):
        """
        This method is required for update all cmd_opt
        dictionary values before send to epilogue
        """
        numfile = _("%s file in pending") % str(countmax)
        if cmd_opt["NormPEAK"]:
            normalize = _('Peak level Norm.')
        elif cmd_opt["NormEBU"]:
            normalize = _('EBU R128 Loudnorm')
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
                        \nAudio stream added\nAudio Format\
                        \nAudio Codec\nAudio Channels\nAudio Rate\
                        \nAudio bit-rate\nBit per Sample\
                        \nAudio Normalization\nMap\nTime selection\
                        \nEnable stopping to shortest"))
            dictions = ("\n\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\
                        \n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s" % (numfile,
                cmd_opt["VidCmbxStr"], cmd_opt["VideoCodec"],
                cmd_opt["VideoAspect"], cmd_opt["VideoRate"], 
                cmd_opt["AddAudioStream"], cmd_opt["Audio"], 
                cmd_opt["AudioCodec"], cmd_opt["AudioChannel"][0], 
                cmd_opt["AudioRate"][0], cmd_opt["AudioBitrate"][0],
                cmd_opt["AudioDepth"][0], normalize, cmd_opt["Map"], 
                time, cmd_opt["Shortest"][1]))
        #-------------------
        elif prof[0] == "Save as images":
            formula = (_("SUMMARY\n\nFile to Queue\
                         \nImages Format\nVideo Rate\
                         \nFilters\nTime selection"
                        ))
            dictions = ("\n\n1\n%s\n%s\n%s\n%s" % (cmd_opt["PicturesFormat"], 
                                                   cmd_opt["VideoRate"],   
                                                   cmd_opt["Filters"],
                                                   time))
        #--------------------
        elif prof[0] == 'audio extract':
            formula = (_("SUMMARY\n\nFile Queue\
                      \nAudio Container\nCodec copied\nTime selection"))
            dictions = ("\n\n%s\n%s\n%s\n%s" % (numfile, 
                                                cmd_opt["A_exportExt"],
                                                cmd_opt["A_Copied"], 
                                                time,)
                        )
        #-------------------
        elif prof[0] == "Slideshow":
            formula = (_("SUMMARY\n\nPictures imported\nVideo Format\
                        \nResolution (size)\nCFR\nPreset h/x 264\
                        \nProfile h/x 264\nTune h/x 264\nVideo Rate\
                        \nAudio stream added\nAudio Format\nAudio Codec\
                        \nAudio Channels\nAudio Rate\nAudio bit-rate\
                        \nBit per Sample\nAudio Normalization\nMap\
                        \nPictures Timing\nEnable stopping to shortest")
                        )
            if cmd_opt["Scale"]:
                res = cmd_opt["Scale"].split('=')
                size = '%s X %s' %(res[2].split(':')[0], res[3])
            else:
                size = _('As from source')
                
            dictions = ("\n\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s"
                        "\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s" %(
                                             len(self.file_sources),
                                             cmd_opt["VideoFormat"],
                                             size,
                                             cmd_opt["CRF"],
                                             cmd_opt["Presets"],
                                             cmd_opt["Profile"],
                                             cmd_opt["Tune"],
                                             cmd_opt["VideoRate"],
                                             cmd_opt["AddAudioStream"],
                                             cmd_opt["Audio"],
                                             cmd_opt["AudioCodec"],
                                             cmd_opt["AudioChannel"][1],
                                             cmd_opt["AudioRate"][1],
                                             cmd_opt["AudioBitrate"][1],
                                             cmd_opt["AudioDepth"][1],
                                             normalize,
                                             cmd_opt["Map"],
                                             time,
                                             cmd_opt["Shortest"][1],))
        #--------------------
        else:
            formula = (_("SUMMARY\n\nFile to Queue\
                         \nVideo Format\nVideo Codec\nVideo bit-rate\nCRF\
                         \nPass Encoding\nDeinterlacing\nInterlacing\
                         \nApplied Filters\nVideo Aspect\nVideo Rate\
                         \nPreset h/x 264\nProfile h/x 264\nTune h/x 264\
                         \nOrientation point\nAudio stream added\
                         \nAudio Format\nAudio codec\nAudio Channels\
                         \nAudio Rate\nAudio bit-rate\nBit per Sample\
                         \nAudio Normalization\nMap\nTime selection\
                         \nEnable stopping to shortest"))
            dictions = ("\n\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\
                        \n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\
                        \n%s\n%s\n%s" % (numfile, cmd_opt["VidCmbxStr"], 
                        cmd_opt["VideoCodec"], cmd_opt["Bitrate"], 
                        cmd_opt["CRF"], cmd_opt["Passing"], 
                        cmd_opt["Deinterlace"], cmd_opt["Interlace"], 
                        cmd_opt["Filters"], cmd_opt["VideoAspect"], 
                        cmd_opt["VideoRate"], cmd_opt["Presets"], 
                        cmd_opt["Profile"], cmd_opt["Tune"], 
                        cmd_opt["Orientation"][1], cmd_opt["AddAudioStream"],
                        cmd_opt["Audio"], cmd_opt["AudioCodec"], 
                        cmd_opt["AudioChannel"][0], cmd_opt["AudioRate"][0], 
                        cmd_opt["AudioBitrate"][0], cmd_opt["AudioDepth"][0],
                        normalize, cmd_opt["Map"], time, cmd_opt["Shortest"][1])
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
        
        if cmd_opt["NormPEAK"]:
            normalize = cmd_opt["NormPEAK"][0]
        else:
            normalize = ''
        
        if self.rdb_auto.GetSelection() == 4: # audio extract from video
            outext = ''
            command = ("-vn -map 0:1 -c copy")
        
        elif not self.ckbx_pass.IsChecked():
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
                            cmd_opt["Map"],
                            cmd_opt["Shortest"][1],)
                                )
            elif self.rdb_auto.GetSelection() == 1:# video to pictures
                outext = cmd_opt["PicturesFormat"]
                YUV = {'jpg':'-pix_fmt yuvj420p', 
                       'png': '-pix_fmt rgb24', 
                       'bmp': '-pix_fmt bgr24'}
                command = ('%s %s %s -an' % (
                           cmd_opt["VideoRate"],
                           cmd_opt["Filters"],
                           YUV[outext],)
                           )
            elif self.rdb_auto.GetSelection() ==  3:# slideshow maker
                outext = cmd_opt["VideoFormat"]
                #cmd_1 = [cmd_opt["Filters"]]
                #time = self.parent.time_read['time']
                #cmd_2 = ['-framerate 1/%s' % (str(time[1]),),
                         #'%s -c:v libx264 %s %s %s %s -vf '
                         #'fps=25,format=yuv420p %s %s %s %s %s %s %s' %(
                                                   #cmd_opt["AddAudioStream"],
                                                   #cmd_opt["CRF"],
                                                   #cmd_opt["Presets"],
                                                   #cmd_opt["Profile"],
                                                   #cmd_opt["Tune"],
                                                   #cmd_opt["AudioCodec"], 
                                                   #cmd_opt["AudioBitrate"][1], 
                                                   #cmd_opt["AudioRate"][1], 
                                                   #cmd_opt["AudioChannel"][1], 
                                                   #cmd_opt["AudioDepth"][1],
                                                   #cmd_opt["Map"], 
                                                   #cmd_opt["Shortest"][1],)]
                         
                #command = ("%s id_SLIDESHOW %s" % (cmd_1,cmd_2))
                command = ("NOT YET IMPLEMENTED")
            else:
                outext = cmd_opt["VideoFormat"]
                command = ("%s %s %s %s %s %s %s %s %s "
                           "%s %s %s %s %s %s %s %s %s" % (
                           normalize, cmd_opt["AddAudioStream"],
                           cmd_opt["VideoCodec"], cmd_opt["CRF"], 
                           cmd_opt["Presets"], cmd_opt["Profile"],
                           cmd_opt["Tune"], cmd_opt["VideoAspect"], 
                           cmd_opt["VideoRate"], cmd_opt["Filters"],
                           cmd_opt["YUV"], cmd_opt["AudioCodec"], 
                           cmd_opt["AudioBitrate"][1], cmd_opt["AudioRate"][1], 
                           cmd_opt["AudioChannel"][1], cmd_opt["AudioDepth"][1], 
                           cmd_opt["Map"], cmd_opt["Shortest"][1],)
                            )
        else:
            outext = cmd_opt["VideoFormat"]
            cmd1 = ('-an %s %s %s %s %s %s %s %s %s -f rawvideo' % (
                      cmd_opt["VideoCodec"], cmd_opt["Bitrate"], 
                      cmd_opt["Presets"], cmd_opt["Profile"],
                      cmd_opt["Tune"], cmd_opt["VideoAspect"], 
                      cmd_opt["VideoRate"], cmd_opt["Filters"],
                      cmd_opt["YUV"],)
                    )
            cmd2= ('%s %s %s %s %s %s %s %s %s '
                   '%s %s %s %s %s %s %s %s %s' % (
                    normalize, cmd_opt["AddAudioStream"],
                    cmd_opt["VideoCodec"], cmd_opt["Bitrate"], 
                    cmd_opt["Presets"], cmd_opt["Profile"],
                    cmd_opt["Tune"], cmd_opt["VideoAspect"], 
                    cmd_opt["VideoRate"], cmd_opt["Filters"],
                    cmd_opt["YUV"], cmd_opt["AudioCodec"], 
                    cmd_opt["AudioBitrate"][1], cmd_opt["AudioRate"][1], 
                    cmd_opt["AudioChannel"][1], cmd_opt["AudioDepth"][1], 
                    cmd_opt["Map"], cmd_opt["Shortest"][1],)
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
