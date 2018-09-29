# -*- coding: UTF-8 -*-

#########################################################
# FileName: video_conv.py
# Porpose: Intarface for video conversions
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2014-2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3

# This file is part of Videomass2.

#    Videomass2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass2.  If not, see <http://www.gnu.org/licenses/>.

# Rev (08) 04/08/2014
# Rev (09) 14/01/2015
# Rev (10) 10/03/2015
# Rev (11) 29/04/2015
# Rev (12) 25/July/2018
#########################################################

import wx
import os
import wx.lib.agw.floatspin as FS
from vdms_IO.IO_tools import volumeDetectProcess
from vdms_IO.filedir_control import inspect
from vdms_DIALOGS.epilogue import Formula
from vdms_DIALOGS import audiodialogs, presets_addnew, dialog_tools

                    
dirname = os.path.expanduser('~') # /home/user

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
           "AudioDepth":["",""], "Normalize":"", "scale":"", 
           "deinterlace":"", "interlace":"", "file":"", "Map":"", 
           "PixelFormat":"", "Orientation":["",""],
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
"Copy Video Codec":("","-c:v copy")
            }
# set widget colours in some case with html rappresentetion:
azure = '#d9ffff' # rgb form (wx.Colour(217,255,255))
yellow = '#faff35'
red = '#ea312d'
orange = '#f28924'
greenolive = '#8aab3c'

class Video_Conv(wx.Panel):
    """
    Interface panel for video conversions with audio volume normalizations
    and preset storing feature
    """
    def __init__(self, parent, helping, ffmpeg_link, 
                 threads, cpu_used, loglevel_type, OS):

        wx.Panel.__init__(self, parent)
        """ constructor """
        # passed attributes:
        self.parent = parent
        self.ffmpeg_link = ffmpeg_link
        self.helping = helping
        self.threads = threads
        self.cpu_used = cpu_used
        self.loglevel_type = loglevel_type
        # others attributes;
        self.file_sources = []
        self.file_destin = ''
        self.OS = OS
        
        self.panel_base = wx.Panel(self, wx.ID_ANY)
        self.notebook_1 = wx.Notebook(self.panel_base, wx.ID_ANY, style=0)
        self.notebook_1_pane_1 = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.cmbx_vidContainers = wx.ComboBox(self.notebook_1_pane_1, wx.ID_ANY,
        choices=[("AVI (XVID mpeg4)"), ("AVI (FFmpeg mpeg4)"), 
        ("AVI (ITU h264)"), ("MP4 (mpeg4)"), ("MP4 (HQ h264/AVC)"), 
        ("M4V (HQ h264/AVC)"), ("MKV (h264)"), ("OGG theora"), ("WebM (HTML5)"), 
        ("FLV (HQ h264/AVC)"),("Copy Video Codec")], style=wx.CB_DROPDOWN | wx.CB_READONLY
        )
        self.sizer_combobox_formatv_staticbox = wx.StaticBox(self.notebook_1_pane_1, 
        wx.ID_ANY, ("Video Container Selection")
        )
        self.sizer_dir_staticbox = wx.StaticBox(self.notebook_1_pane_1, 
        wx.ID_ANY, ('Export Preferences')
        )
        self.ckbx_pass = wx.CheckBox(self.notebook_1_pane_1, wx.ID_ANY, 
        ("2-pass encoding.")
        )
        self.ckbx_pass.SetValue(False) # setto in modo spento

        self.sizer_automations_staticbox = wx.StaticBox(self.notebook_1_pane_1, 
        wx.ID_ANY, ("Automations and Filters")
        )
        self.rdb_automations = wx.RadioBox(self.notebook_1_pane_1, wx.ID_ANY, "", 
                            choices=[("Disabled"),
                                     ("Save images from Video"),
                                     ("Set visual Rotation")], 
                            majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        self.spin_ctrl_bitrate = wx.SpinCtrl(self.notebook_1_pane_1, wx.ID_ANY, 
        "1500", min=0, max=25000, style=wx.TE_PROCESS_ENTER
        )
        self.sizer_bitrate_staticbox = wx.StaticBox(self.notebook_1_pane_1, 
        wx.ID_ANY, ("Video Bit-Rate Value")
        )
        self.slider_CRF = wx.Slider(self.notebook_1_pane_1, wx.ID_ANY, 1, 0, 51, 
        style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
        )
        self.sizer_crf_staticbox = wx.StaticBox(self.notebook_1_pane_1, 
        wx.ID_ANY, ("Video CRF Value")
        )
        self.notebook_1_pane_2 = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.ckbx_videosize = wx.CheckBox(self.notebook_1_pane_2, 
                                    wx.ID_ANY, ("Set Video Size"))
        self.label_width_1 = wx.StaticText(self.notebook_1_pane_2, wx.ID_ANY, 
                                    ("Width"))
        #self.label_sep = wx.StaticText(self.notebook_1_pane_2, wx.ID_ANY, 
                                    #("/"))
        self.label_height = wx.StaticText(self.notebook_1_pane_2, wx.ID_ANY, 
                    ("Heigth"))
        
        self.spin_size_width = wx.SpinCtrl(self.notebook_1_pane_2, wx.ID_ANY, 
        "0", min=0, max=10000, style=wx.TE_PROCESS_ENTER
        )
        self.label_x = wx.StaticText(self.notebook_1_pane_2, wx.ID_ANY, ("X"))
        self.spin_size_height = wx.SpinCtrl(self.notebook_1_pane_2, wx.ID_ANY,
        "0", min=0, max=10000, style=wx.TE_PROCESS_ENTER
        )
        self.ckbx_scale = wx.CheckBox(self.notebook_1_pane_2, 
                            wx.ID_ANY, ("Enable Scaling (Resizing)"))##
        self.ckbx_scale.SetValue(False)##
        self.label_width_2 = wx.StaticText(self.notebook_1_pane_2, wx.ID_ANY, 
                                        ("Width"), style=wx.ALIGN_CENTRE)###
        
        self.spin_ctrl_scale = wx.SpinCtrl(self.notebook_1_pane_2, wx.ID_ANY,
                        "0", min=0, max=10000, style=wx.TE_PROCESS_ENTER)##
        self.sizer_videosize_staticbox = wx.StaticBox(self.notebook_1_pane_2, 
        wx.ID_ANY, ("Video Size (Optional)")
        )
        self.ckbx_deinterlace = wx.CheckBox(self.notebook_1_pane_2, 
                                        wx.ID_ANY, (u"Deinterlaces")
                                        )
        self.rdbx_deinterlace = wx.RadioBox(self.notebook_1_pane_2, 
                            wx.ID_ANY, (u"Modality"), choices=[("complex"), 
                            ("simple")], majorDimension=0, 
                            style=wx.RA_SPECIFY_ROWS
                            )
        self.ckbx_interlace = wx.CheckBox(self.notebook_1_pane_2, 
                                        wx.ID_ANY, ("Interlaces   ")
                                        )
        self.rdbx_interlace = wx.RadioBox(self.notebook_1_pane_2, 
                                    wx.ID_ANY, ("Parameters interlacc."), 
                                    choices=[("Default"), ("Scan"), ("Lowpass")], 
                                    majorDimension=0, style=wx.RA_SPECIFY_ROWS
                                    )
        self.sizer_1_staticbox = wx.StaticBox(self.notebook_1_pane_2, 
                            wx.ID_ANY, (u"De-interlaced/Progressive video"))
        self.cmbx_Vaspect = wx.ComboBox(self.notebook_1_pane_2, wx.ID_ANY,
        choices=[("Set default "), ("4:3"), ("16:9")], style=wx.CB_DROPDOWN | 
        wx.CB_READONLY
        )
        self.sizer_videoaspect_staticbox = wx.StaticBox(self.notebook_1_pane_2, 
                                        wx.ID_ANY, ("Video Aspect (Optional)")
                                        )
        self.cmbx_vrate = wx.ComboBox(self.notebook_1_pane_2, wx.ID_ANY, 
        choices=[("Set default "), ("25 fps (50i) PAL"), ("29.97 fps (60i) NTSC"),
        ("30 fps (30p) Progessive")], style=wx.CB_DROPDOWN | wx.CB_READONLY
        )
        self.sizer_videorate_staticbox = wx.StaticBox(self.notebook_1_pane_2, 
                                        wx.ID_ANY, ("Video Rate (Optional)")
                                                    )
        self.notebook_1_pane_3 = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.rdb_a = wx.RadioBox(self.notebook_1_pane_3, wx.ID_ANY, (
        "Audio Codec Selecting"), choices=[("Default"), 
        ("Wav (Raw, No_MultiChannel)"), ("Flac (Lossless, No_MultiChannel)"), 
        ("Aac (Lossy, MultiChannel)"), ("Alac (Lossless, m4v, No_MultiChannel)"),
        ("Ac3 (Lossy, MultiChannel)"), ("Ogg (Lossy, No_MultiChannel)"),
        ("Mp3 (Lossy, No_MultiChannel)"), ("Try to copy audio source"),
        ("No audio stream (silent)")], 
                                    majorDimension=0, style=wx.RA_SPECIFY_ROWS
                                    )
        self.rdb_a.EnableItem(0,enable=True),self.rdb_a.EnableItem(1,enable=True)
        self.rdb_a.EnableItem(2,enable=True),self.rdb_a.EnableItem(3,enable=True)
        self.rdb_a.EnableItem(4,enable=False),self.rdb_a.EnableItem(5,enable=True)
        self.rdb_a.EnableItem(6,enable=True),self.rdb_a.EnableItem(7,enable=True)
        self.rdb_a.EnableItem(8,enable=True),self.rdb_a.EnableItem(9,enable=True)
        self.rdb_a.SetSelection(0)
        self.ckbx_a_normalize = wx.CheckBox(self.notebook_1_pane_3, 
                      wx.ID_ANY, ("Audio Normalization Stream")
                                )
        self.btn_analyzes = wx.Button(self.notebook_1_pane_3, wx.ID_ANY, 
                                ("Analyzes")
                                )
        self.label_dbMax = wx.StaticText(self.notebook_1_pane_3, wx.ID_ANY, 
                                ("dB Maximum audio level: ")
                                )
        self.text_dbMax = wx.TextCtrl(self.notebook_1_pane_3, wx.ID_ANY, "", 
                                style=wx.TE_READONLY)
        self.label_dbMedium = wx.StaticText(self.notebook_1_pane_3, wx.ID_ANY, 
                                    ("dB Middle audio level:")
                                    )
        self.text_dbMedium = wx.TextCtrl(self.notebook_1_pane_3, wx.ID_ANY, "", 
                                style=wx.TE_READONLY)
        self.label_normalize = wx.StaticText(self.notebook_1_pane_3, wx.ID_ANY, 
                                    ("Max Peak Level Threshold:")
                                    )
        self.spin_ctrl_audionormalize = FS.FloatSpin(self.notebook_1_pane_3, 
            wx.ID_ANY, min_val=-99.0, max_val=0.0, increment=1.0, value=-1.0, 
                        agwStyle=FS.FS_LEFT
                        )
        self.spin_ctrl_audionormalize.SetFormat("%f")
        self.spin_ctrl_audionormalize.SetDigits(1)
        #self.button_info = wx.Button(self.notebook_1_pane_3, wx.ID_ANY, ("?"), 
                            #style=wx.BU_BOTTOM)
        #self.bitmap_1 = wx.StaticBitmap(self.notebook_1_pane_3, wx.ID_ANY, 
            #wx.Bitmap(icon_eyes, wx.BITMAP_TYPE_ANY))
        
        self.notebook_1_pane_4 = wx.Panel(self.notebook_1, wx.ID_ANY)
        self.rdb_h264preset = wx.RadioBox(self.notebook_1_pane_4, wx.ID_ANY, (
        "presets h264 (optional)"), choices=[("Disabled"), ("ultrafast"), 
        ("superfast"), ("veryfast"), ("faster"), ("fast"), ("medium"), 
        ("slow"), ("slower"), ("veryslow"), ("placebo")],  majorDimension=0, 
                                                    style=wx.RA_SPECIFY_ROWS
                                                    )
        self.rdb_h264profile = wx.RadioBox(self.notebook_1_pane_4, wx.ID_ANY, (
        "Profilo h264 (optional)"), choices=[("Disabled"), ("baseline"), 
        ("main"), ("high"), ("high10"), ("high444")], majorDimension=0, 
                                                    style=wx.RA_SPECIFY_ROWS
                                                    )
        self.rdb_h264tune = wx.RadioBox(self.notebook_1_pane_4, wx.ID_ANY, (
        "Tune h264 (optional)"), choices=[("Disabled"), ("film"), ("animation"),
        ("grain"), ("stillimage"), ("psnr"), ("ssim"), ("fastecode"), 
                ("zerolatency")], majorDimension=0, style=wx.RA_SPECIFY_ROWS
                )
        # Set default layout of the widget in the window:
        self.label_width_2.Disable(), self.spin_ctrl_scale.Disable()

        #----------------------Set Properties----------------------#
        self.cmbx_vidContainers.SetToolTipString("Video container that will "
                                        "be used in the conversion. NOTE: for "
                                        "any container change, all settings "
                                        "there be reset.")
        self.cmbx_vidContainers.SetSelection(6)


        self.ckbx_pass.SetToolTipString("If use double pass, can improve "
                                            "the video quality, but it take "
                                            "more time. We recommend using "
                                            "it in high video compression."
                                                 )
        self.spin_ctrl_bitrate.SetToolTipString("The bit rate determines the "
                                            "quality and the final video "
                                            "size. A larger value correspond "
                                            "to greater quality and size of "
                                            "the file."
                                                 )
        self.slider_CRF.SetValue(23)# this is a default rate
        self.slider_CRF.SetMinSize((230, -1))
        self.slider_CRF.SetToolTipString("CRF (constant rate factor) Affects "
                                 "the quality of the final video. Used for "
                                 "h264 codec on single pass only, 2-pass "
                                 "encoding swich to bitrate. With lower "
                                 "values the quality is higher and a larger "
                                 "file size."
                                          )
        self.ckbx_videosize.SetToolTipString(u"Enables manual setting of "
                                                 "sizing (width x height)"
                                                 )
        sizestr = (u"The video size is the size of the final video in pixels. "
                "Example for youtube:: 640X480\nExample for Ipod/Iphone: "
                "320x180\nVideo per PSP: 320x240"
                )
        self.spin_size_height.SetToolTipString("Video height:\n%s" %(sizestr))
        #self.spin_size_height.SetMinSize((70, -1))
        self.spin_size_width.SetToolTipString("Video width:\n%s" %(sizestr))##
        #self.spin_size_width.SetMinSize((70, -1))
        self.ckbx_scale.SetToolTipString("Enable automatic scaling "
                            "proportionate videos. Scaling is any resizing "
                            "operation without changing the appearance of "
                            "the original movie")##
        #self.spin_ctrl_scale.SetMinSize((70, -1))
        self.spin_ctrl_scale.SetToolTipString("Enter only the video width in "
                                "pixels. The video height will be calculated"
                                "automatically")##
        self.ckbx_deinterlace.SetToolTipString(u'Deinterlace the input video '
                u'("w3fdif" stands for "Weston 3 Field Deinterlacing Filter. '
                u'Based on the process described by Martin Weston for BBC R&D, '
                u'and implemented based on the de-interlace algorithm written '
                u'by Jim Easterbrook for BBC R&D, the Weston 3 field '
                u'deinterlacing filter uses filter coefficients calculated '
                u'by BBC R&D.")'
                                                   )
        self.rdbx_deinterlace.SetToolTipString('Set the interlacing filter '
                        'coefficients. Accepts one of the following values:\n'
                        'simple: Simple filter coefficient set.\n'
                        'complex: More-complex filter coefficient set. '
                        'Default value is complex.'
                                                    )
        self.ckbx_interlace.SetToolTipString('Simple interlacing filter from '
                'progressive contents. This interleaves upper (or lower) '
                'lines from odd frames with lower (or upper) lines from even '
                'frames, halving the frame rate and preserving image height.'
                                                 )
        self.rdbx_interlace.SetToolTipString('It accepts the following '
        'optional parameters;\nscan: determines whether the interlaced frame '
        'is taken from the even (tff - default) or odd (bff) lines of the '
        'progressive frame.\nlowpas: Enable (default) or disable the vertical '
        'lowpass filter to avoid twitter interlacing and reduce moire '
        'patterns. Default is no setting.'
                                                  )
        self.cmbx_Vaspect.SetSelection(0)
        self.cmbx_Vaspect.SetToolTipString(u"Video aspect (Aspect Ratio) "
                        "is the video width and video height ratio. "
                        "Leave on 'Set default' to copy the original settings."
                                                )
        self.cmbx_vrate.SetSelection(0)
        self.cmbx_vrate.SetToolTipString(u"Video Rate: A any video consists "
                       "of images displayed as frames, repeated a given number "
                       "of times per second. In countries are 30 NTSC, PAL "
                       "countries (like Italy) are 25. Leave on 'Set default' "
                       "to copy the original settings."
                                              )
        
        self.ckbx_a_normalize.SetToolTipString("Performs audio "
                    "normalization in the video audio stream. "
                    "NOTE: this feature is disabled for "
                    "'Try to copy audio source' and 'No audio stream (silent)' "
                    "selections." )
        self.btn_analyzes.SetToolTipString(u"Calculate the maximum and "
                                    "average peak in dB values, of the audio "
                                    "stream on the video imported.")
        #self.spin_ctrl_audionormalize.SetMinSize((70, -1))
        self.spin_ctrl_audionormalize.SetToolTipString("Threshold for the "
                                "maximum peak level in dB values. The default " 
                                "setting is -1.0 dB and is good for most of "
                                "the processes")
        
        self.rdb_a.SetToolTipString("Choose the appropriate Audio Codec. "
                                    "Some Audio Codecs are disabled for "
                                    "certain Video Containers. " )
        self.rdb_h264preset.SetToolTipString("preset h264")
        self.rdb_h264preset.SetSelection(0)
        self.rdb_h264profile.SetToolTipString("profili h264")
        self.rdb_h264profile.SetSelection(0)
        self.rdb_h264tune.SetToolTipString("tune h264")
        self.rdb_h264tune.SetSelection(0)
        self.notebook_1_pane_4.SetToolTipString("The parameters on this tab "
                        "are enabled only for the video-codec h264. Although "
                        "optional, is set to 'preset medium' as default "
                        "parameter.")
        
        #----------------------Build Layout----------------------#
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(2, 1, 0, 0)
        sizer_pane4_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_pane4_base = wx.GridSizer(1, 3, 0, 0)
        sizer_pane3_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_pane3_base = wx.GridSizer(1, 2, 0, 0)
        sizer_pane3_audio_column2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_in_column2 = wx.FlexGridSizer(3, 1, 0, 0)
        grid_sizer_audionormalize = wx.GridSizer(3, 1, 0, 0)
        grid_sizer_slider_normalize = wx.FlexGridSizer(1, 2, 0, 0)
        grid_sizer_text_normalize = wx.FlexGridSizer(2, 2, 0, 0)
        sizer_pane3_audio_column1 = wx.BoxSizer(wx.VERTICAL)
        sizer_pane2_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_pane2_base = wx.GridSizer(1, 3, 0, 0)
        grid_sizer_1 = wx.GridSizer(2, 1, 0, 0)
        self.sizer_videorate_staticbox.Lower()
        sizer_videorate = wx.StaticBoxSizer(self.sizer_videorate_staticbox, wx.VERTICAL)
        self.sizer_videoaspect_staticbox.Lower()
        sizer_videoaspect = wx.StaticBoxSizer(self.sizer_videoaspect_staticbox, wx.VERTICAL)
        self.sizer_1_staticbox.Lower()
        sizer_1 = wx.StaticBoxSizer(self.sizer_1_staticbox, wx.VERTICAL)
        grid_sizer_3 = wx.GridSizer(2, 2, 0, 0)
        self.sizer_videosize_staticbox.Lower()
        sizer_2 = wx.StaticBoxSizer(self.sizer_videosize_staticbox, wx.VERTICAL)
        grid_sizer_2 = wx.GridSizer(6, 1, 0, 0)
        grid_sizer_5 = wx.GridSizer(1, 3, 0, 0)
        grid_sizer_4 = wx.GridSizer(1, 3, 0, 0)
        grid_sizer_pane1_base = wx.GridSizer(1, 3, 0, 0)
        grid_sizer_pane1_right = wx.GridSizer(2, 1, 0, 0)
        self.sizer_crf_staticbox.Lower()
        sizer_crf = wx.StaticBoxSizer(self.sizer_crf_staticbox, wx.VERTICAL)
        self.sizer_bitrate_staticbox.Lower()
        sizer_bitrate = wx.StaticBoxSizer(self.sizer_bitrate_staticbox, wx.VERTICAL)
        self.sizer_automations_staticbox.Lower()
        sizer_automations = wx.StaticBoxSizer(self.sizer_automations_staticbox, wx.VERTICAL)
        grid_sizer_automations = wx.GridSizer(3, 1, 0, 0)

        grid_sizer_pane1_left = wx.GridSizer(2, 1, 0, 0)
        self.sizer_dir_staticbox.Lower()
        sizer_dir = wx.StaticBoxSizer(self.sizer_dir_staticbox, wx.VERTICAL)
        grid_sizer_dir = wx.GridSizer(1, 1, 0, 0)# vuoto
        self.sizer_combobox_formatv_staticbox.Lower()
        sizer_combobox_formatv = wx.StaticBoxSizer(self.sizer_combobox_formatv_staticbox, wx.VERTICAL)
        sizer_combobox_formatv.Add(self.cmbx_vidContainers, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 20)
        grid_sizer_pane1_left.Add(sizer_combobox_formatv, 1, wx.ALL | wx.EXPAND, 15)
        grid_sizer_dir.Add(self.ckbx_pass, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 20)
        sizer_dir.Add(grid_sizer_dir, 1, wx.EXPAND, 0)
        grid_sizer_pane1_left.Add(sizer_dir, 1, wx.ALL | wx.EXPAND, 15)
        grid_sizer_pane1_base.Add(grid_sizer_pane1_left, 1, wx.EXPAND, 0)

        grid_sizer_automations.Add(self.rdb_automations, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer_automations.Add(grid_sizer_automations, 1, wx.EXPAND, 0)
        grid_sizer_pane1_base.Add(sizer_automations, 1, wx.ALL | wx.EXPAND, 15)
        sizer_bitrate.Add(self.spin_ctrl_bitrate, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 20)
        grid_sizer_pane1_right.Add(sizer_bitrate, 1, wx.ALL | wx.EXPAND, 15)
        sizer_crf.Add(self.slider_CRF, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 20)
        grid_sizer_pane1_right.Add(sizer_crf, 1, wx.ALL | wx.EXPAND, 15)
        grid_sizer_pane1_base.Add(grid_sizer_pane1_right, 1, wx.EXPAND, 0)
        self.notebook_1_pane_1.SetSizer(grid_sizer_pane1_base)
        grid_sizer_2.Add(self.ckbx_videosize, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_4.Add(self.label_width_1, 0, wx.LEFT | wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_4.Add((0, 0), 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_4.Add(self.label_height, 0, wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_2.Add(grid_sizer_4, 1, wx.EXPAND, 0)
        grid_sizer_5.Add(self.spin_size_width, 0, wx.LEFT | wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_5.Add(self.label_x, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_5.Add(self.spin_size_height, 0, wx.RIGHT | wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_2.Add(grid_sizer_5, 1, wx.EXPAND, 0)
        grid_sizer_2.Add(self.ckbx_scale, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 30)
        grid_sizer_2.Add(self.label_width_2, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 20)
        grid_sizer_2.Add(self.spin_ctrl_scale, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_2.Add(grid_sizer_2, 1, wx.EXPAND, 0)
        grid_sizer_pane2_base.Add(sizer_2, 1, wx.ALL | wx.EXPAND, 15)
        grid_sizer_3.Add(self.ckbx_deinterlace, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_3.Add(self.rdbx_deinterlace, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_3.Add(self.ckbx_interlace, 0, wx.ALL, 5)
        grid_sizer_3.Add(self.rdbx_interlace, 0, 0, 0)
        sizer_1.Add(grid_sizer_3, 1, wx.EXPAND, 0)
        grid_sizer_pane2_base.Add(sizer_1, 1, wx.ALL | wx.EXPAND, 15)
        sizer_videoaspect.Add(self.cmbx_Vaspect, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 15)
        grid_sizer_1.Add(sizer_videoaspect, 1, wx.ALL | wx.EXPAND, 15)
        sizer_videorate.Add(self.cmbx_vrate, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 15)
        grid_sizer_1.Add(sizer_videorate, 1, wx.ALL | wx.EXPAND, 15)
        grid_sizer_pane2_base.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        sizer_pane2_base.Add(grid_sizer_pane2_base, 1, wx.EXPAND, 0)
        self.notebook_1_pane_2.SetSizer(sizer_pane2_base)
        sizer_pane3_audio_column1.Add(self.rdb_a, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_pane3_base.Add(sizer_pane3_audio_column1, 1, wx.EXPAND, 0)
        grid_sizer_in_column2.Add(self.ckbx_a_normalize, 0, wx.TOP, 15)
        grid_sizer_audionormalize.Add(self.btn_analyzes, 0, wx.TOP, 15)
        grid_sizer_text_normalize.Add(self.label_dbMax, 0, wx.TOP|wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_text_normalize.Add(self.text_dbMax, 0, wx.TOP|wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_text_normalize.Add(self.label_dbMedium, 0, wx.TOP|wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_text_normalize.Add(self.text_dbMedium, 0, wx.TOP|wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_audionormalize.Add(grid_sizer_text_normalize, 1, wx.EXPAND, 0)
        grid_sizer_slider_normalize.Add(self.label_normalize, 0, wx.TOP|wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_slider_normalize.Add(self.spin_ctrl_audionormalize, 0, wx.TOP|wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_audionormalize.Add(grid_sizer_slider_normalize, 1, wx.ALL, 5)
        grid_sizer_in_column2.Add(grid_sizer_audionormalize, 1, wx.ALL, 5)
        sizer_pane3_audio_column2.Add(grid_sizer_in_column2, 1, wx.EXPAND, 0)
        grid_sizer_pane3_base.Add(sizer_pane3_audio_column2, 1, wx.EXPAND, 0)
        sizer_pane3_base.Add(grid_sizer_pane3_base, 1, wx.EXPAND, 0)
        self.notebook_1_pane_3.SetSizer(sizer_pane3_base)
        grid_sizer_pane4_base.Add(self.rdb_h264preset, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_pane4_base.Add(self.rdb_h264profile, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        grid_sizer_pane4_base.Add(self.rdb_h264tune, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 15)
        sizer_pane4_base.Add(grid_sizer_pane4_base, 1, wx.EXPAND, 0)
        self.notebook_1_pane_4.SetSizer(sizer_pane4_base)
        self.notebook_1.AddPage(self.notebook_1_pane_1, ("Video Container"))
        self.notebook_1.AddPage(self.notebook_1_pane_2, ("Video Settings"))
        self.notebook_1.AddPage(self.notebook_1_pane_3, ("Audio Settings"))
        self.notebook_1.AddPage(self.notebook_1_pane_4, ("Codec H264 Options"))
        grid_sizer_base.Add(self.notebook_1, 1, wx.ALL | wx.EXPAND, 5)
        self.panel_base.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(self.panel_base, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()

        #----------------------Binding (EVT)----------------------#
        """
        Note: wx.EVT_TEXT_ENTER é diverso da wx.EVT_TEXT . Il primo é sensibile
        agli input di tastiera, il secondo é sensibile agli input di tastiera
        ma anche agli "append"
        """
        #self.Bind(wx.EVT_COMBOBOX, self.vidContainers, self.cmbx_vidContainers)
        self.cmbx_vidContainers.Bind(wx.EVT_COMBOBOX, self.vidContainers)
        self.Bind(wx.EVT_CHECKBOX, self.on_Pass, self.ckbx_pass)
        self.Bind(wx.EVT_RADIOBOX, self.on_Automations, self.rdb_automations)
        self.Bind(wx.EVT_SPINCTRL, self.on_Bitrate, self.spin_ctrl_bitrate)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.on_Crf, self.slider_CRF)
        self.Bind(wx.EVT_CHECKBOX, self.on_Enable_vsize, self.ckbx_videosize)
        self.Bind(wx.EVT_CHECKBOX, self.on_Enable_scale, self.ckbx_scale)
        #self.Bind(wx.EVT_SPINCTRL, self.set_Scaling, self.spin_ctrl_scale)
        self.Bind(wx.EVT_CHECKBOX, self.on_Deinterlace, self.ckbx_deinterlace)
        self.Bind(wx.EVT_RADIOBOX, self.mod_Deinterlace, self.rdbx_deinterlace)
        self.Bind(wx.EVT_CHECKBOX, self.on_Interlace, self.ckbx_interlace)
        self.Bind(wx.EVT_RADIOBOX, self.mod_Interlace, self.rdbx_interlace)
        self.Bind(wx.EVT_COMBOBOX, self.on_Vaspect, self.cmbx_Vaspect)
        self.Bind(wx.EVT_COMBOBOX, self.on_Vrate, self.cmbx_vrate)
        self.Bind(wx.EVT_RADIOBOX, self.on_Audio, self.rdb_a)
        self.Bind(wx.EVT_CHECKBOX, self.onNormalize, self.ckbx_a_normalize)
        self.Bind(wx.EVT_BUTTON, self.on_Audio_analyzes, self.btn_analyzes)
        self.Bind(wx.EVT_RADIOBOX, self.on_h264Presets, self.rdb_h264preset)
        self.Bind(wx.EVT_RADIOBOX, self.on_h264Profiles, self.rdb_h264profile)
        self.Bind(wx.EVT_RADIOBOX, self.on_h264Tunes, self.rdb_h264tune)
        #self.Bind(wx.EVT_CLOSE, self.Quiet) # controlla la chiusura dalla x di chiusura

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
        self.ckbx_videosize.SetValue(False), self.ckbx_videosize.Enable()
        self.spin_size_height.Disable(), self.spin_size_width.Disable()
        self.spin_ctrl_scale.Disable(), self.spin_ctrl_scale.SetValue(0)
        self.spin_size_height.SetValue(0), self.spin_size_width.SetValue(0)
        self.cmbx_Vaspect.Enable(), self.ckbx_scale.SetValue(False)
        self.ckbx_scale.Enable()
        self.label_width_1.Disable(), self.label_height.Disable()
        self.label_x.Disable(), self.label_width_2.Disable()
        self.rdbx_deinterlace.SetSelection(0), 
        self.ckbx_deinterlace.SetValue(False)
        self.rdbx_deinterlace.Disable()
        #self.rdbx_interlace.SetSelection(0), 
        self.ckbx_interlace.SetValue(False)
        #self.rdbx_interlace.Disable()
        cmd_opt["VideoAspect"] = ""
        cmd_opt["VideoRate"] = ""
        cmd_opt["VideoSize"] = ""
        self.rdbx_interlace.Hide() # TODO QUESTO E' IN SVILUPPO
        
    #-------------------------------------------------------------------#
    def UI_set(self):
        """
        Update all the GUI widgets based on the choices made by the user.
        """
        if cmd_opt["VideoCodec"] == "-vcodec libx264":
            self.notebook_1_pane_4.Enable()
            if not self.notebook_1_pane_2.IsEnabled():
                self.notebook_1_pane_2.Enable()
                self.ckbx_pass.Enable()
                self.rdb_automations.Enable()
            self.on_Pass(self)
        elif cmd_opt["VideoCodec"] == "-c:v copy":
            self.spin_ctrl_bitrate.Disable(), self.notebook_1_pane_2.Disable(),
            self.notebook_1_pane_4.Disable(), self.ckbx_pass.Disable(), 
            self.ckbx_pass.SetValue(False)
            self.rdb_a.EnableItem(4,enable=True)# se disable lo abilita
            self.slider_CRF.Disable(), self.rdb_h264preset.SetSelection(0)
            self.rdb_h264profile.SetSelection(0)
            self.rdb_h264tune.SetSelection(0)
            self.rdb_automations.Disable(),self.rdb_automations.SetSelection(0)
            self.on_h264Presets(self), self.on_h264Profiles(self)
            self.on_h264Tunes(self)
        else: # all others containers that not use h264
            self.notebook_1_pane_4.Disable()
            self.rdb_h264preset.SetSelection(0)
            self.rdb_h264profile.SetSelection(0)
            self.rdb_h264tune.SetSelection(0)
            self.on_h264Presets(self), self.on_h264Profiles(self)
            self.on_h264Tunes(self)
            
            if not self.notebook_1_pane_2.IsEnabled():
                self.notebook_1_pane_2.Enable()
                self.ckbx_pass.Enable()
                self.rdb_automations.Enable()
            self.on_Pass(self)
    #-------------------------------------------------------------------#
    def audio_default(self):
        """
        Set default audio parameters. This method is called on first run and
        if there is a change inthe  video container selection on the combobox
        """
        self.rdb_a.SetStringSelection("Default") # scheda param.audio
        cmd_opt["Audio"] = ""
        cmd_opt["AudioCodec"] = ""
        cmd_opt["AudioBitrate"] = ["",""]
        cmd_opt["AudioChannel"] = ["",""]
        cmd_opt["AudioRate"] = ["",""]
        cmd_opt["AudioDepth"] = ["",""]
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
        self.btn_analyzes.Disable(), self.spin_ctrl_audionormalize.Disable()
        self.spin_ctrl_audionormalize.SetValue(-1.0)
        self.text_dbMax.SetValue(""), self.text_dbMedium.SetValue("")
        self.text_dbMax.Disable(), self.text_dbMedium.Disable()
        self.label_dbMax.Disable(), self.label_dbMedium.Disable()
        self.label_normalize.Disable()
        cmd_opt["Normalize"] = ""
    
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
        
        if vcodec[selected][0] == "-vcodec libx264":
            cmd_opt["FormatChoice"] = "%s" % (selected)
            # avi,mkv,mp4,flv,etc.:
            cmd_opt['VideoFormat'] = "%s" % (vcodec[selected][1])
            cmd_opt["VideoCodec"] = "-vcodec libx264"
            cmd_opt["Bitrate"] = ""
            cmd_opt["CRF"] = ""
            self.UI_set()
        elif vcodec[selected][0] == "":# copy video codec
            cmd_opt["ext_input"], cmd_opt["InputDir"], cmd_opt["OutputDir"],\
            cmd_opt["VideoSize"], cmd_opt["VideoAspect"], cmd_opt["VideoRate"],\
            cmd_opt["Presets"], cmd_opt["Profile"], cmd_opt["Tune"],\
            cmd_opt["Bitrate"], cmd_opt["CRF"], cmd_opt["scale"],\
            cmd_opt["deinterlace"], cmd_opt["interlace"], cmd_opt["file"],\
            cmd_opt["PixelFormat"], cmd_opt["Orientation"] = '','','','','',\
            '','','','','','','','','','','',['','']
            cmd_opt["Passing"] = "single"
            cmd_opt["FormatChoice"] = "%s" % (selected)
            # avi,mkv,mp4,flv,etc.:
            cmd_opt['VideoFormat'] = "%s" % ( vcodec[selected][1])
            cmd_opt["VideoCodec"] = "-c:v copy"
            cmd_opt["Bitrate"] = ""
            cmd_opt["CRF"] = ""
            self.UI_set()
        else:
            cmd_opt["FormatChoice"] = "%s" % (selected)
            # avi,mkv,mp4,flv,etc.:
            cmd_opt['VideoFormat'] = "%s" % (vcodec[selected][1])
            # -vcodec libx264 o altro:
            cmd_opt["VideoCodec"] = "%s" %(vcodec[selected][0])
            cmd_opt["Bitrate"] = ""
            cmd_opt["CRF"] = ""
            self.UI_set()
            
        self.setAudioRadiobox(self)
        self.parent.statusbar_msg("Output format: %s" % (
                                    cmd_opt['VideoFormat']),None)

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
    def on_Automations(self, event):
        """
        FIXME sistema meglio il blocco di codice in questa funzione
        """
        
        data = ''
        selected = self.rdb_automations.GetStringSelection()

        if selected == "Save images from Video":
            time_seq = self.parent.time_seq
            dialog = dialog_tools.SaveImages(self, time_seq, 
                                             cmd_opt["VideoRate"])
            retcode = dialog.ShowModal()
            if retcode == wx.ID_OK:
                self.cmbx_vrate.Disable()
                self.rdb_automations.EnableItem(2,enable=False)
                data = dialog.GetValue()
                if data[0] == '-ss 00:00:00 -t 00:00:00':
                    cmd_opt["VideoRate"] = ""
                    self.parent.time_seq = ''
                    if not self.cmbx_vrate.IsEnabled():
                        self.cmbx_vrate.Enable()
                        self.rdb_automations.EnableItem(2,enable=True)
                        
                else:
                    self.parent.time_seq = data[0]
                    cmd_opt["VideoRate"] = data[1]
            else:
                dialog.Destroy()
                return
            
        elif selected == "Set visual Rotation":
            dialog = dialog_tools.VideoRotate(self, cmd_opt["Orientation"][0],
                                              cmd_opt["Orientation"][1])
            retcode = dialog.ShowModal()
            if retcode == wx.ID_OK:
                self.rdb_automations.EnableItem(1,enable=False)
                data = dialog.GetValue()
                cmd_opt["Orientation"][0] = data[0]# cmd option
                cmd_opt["Orientation"][1] = data[1]#msg
                if data[0] == '':
                    self.rdb_automations.EnableItem(1,enable=True)
            else:
                dialog.Destroy()
                return
            
        elif selected == "Disabled":
            self.on_Vrate(self)

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
    def on_Enable_vsize(self, event):
        """
        Enable or disable functionality for sizing video
        """
        ## TODO è meglio usare il filtro scale anzichè -s ???
        
        if self.ckbx_videosize.IsChecked():
            
            self.spin_size_height.Enable(), self.spin_size_width.Enable()
            self.label_width_1.Enable(), self.label_height.Enable()
            self.label_x.Enable(), self.ckbx_scale.Disable()
            self.set_Sizing()

        elif not self.ckbx_videosize.IsChecked():

            self.spin_size_height.Disable(), self.spin_size_width.Disable()
            self.label_width_1.Disable(), self.label_height.Disable()
            self.label_x.Disable(), self.ckbx_scale.Enable()
    #------------------------------------------------------------------#
    def set_Sizing(self):
        """
        NOTE 0): Sometimes the spinctlr don't get the values immediately 
                 using the keyboard if you do not press the 'Enter' key, 
                 then they are updated again in the on_ok method.
        NOTE 1): The spinctrls gives an integear values only .
        """
        if self.ckbx_videosize.IsChecked():
            size = "-s %sx%s" % (self.spin_size_width.GetValue(), 
                                 self.spin_size_height.GetValue())
            cmd_opt["VideoSize"] = size
        elif self.ckbx_scale.IsChecked():
            scale = self.spin_ctrl_scale.GetValue()
            cmd_opt["VideoSize"] = "-vf scale=%s:-1" % (scale)
        else:
            cmd_opt["VideoSize"] = ''

    #------------------------------------------------------------------#
    def on_Enable_scale(self, event):
        """
        Enable or disable functionality for scale. Scale is a parameter 
        that not work if 'Video Aspect' combobox is enabled, than disable it. 
        If checked, also call set_Scaling method below for automate the entries.
        """
        if self.ckbx_scale.IsChecked():
            self.cmbx_Vaspect.Disable(), self.cmbx_Vaspect.SetSelection(0)
            self.label_width_2.Enable(), self.spin_ctrl_scale.Enable()
            self.ckbx_videosize.Disable()
            self.set_Sizing()

        elif not self.ckbx_scale.IsChecked():
            self.spin_ctrl_scale.Disable(), self.spin_ctrl_scale.SetValue(0)
            self.cmbx_Vaspect.Enable(), self.label_width_2.Disable()
            self.ckbx_videosize.Enable()
    #------------------------------------------------------------------#
    def on_Deinterlace(self, event):
        """
        Enable or disable functionality 
        """
        if self.ckbx_deinterlace.IsChecked():
            self.rdbx_deinterlace.Enable()
            self.ckbx_interlace.Disable()
            cmd_opt["deinterlace"] = "-vf w3fdif"
            
        elif not self.ckbx_deinterlace.IsChecked():
            self.rdbx_deinterlace.Disable()
            self.ckbx_interlace.Enable()
            cmd_opt["deinterlace"] = ""
            
    #------------------------------------------------------------------#
    def mod_Deinterlace(self, event):
        """
        Set parameter with string value 
        """
        cmd_opt["deinterlace"] = "-vf w3fdif=%s" % (
                             self.rdbx_deinterlace.GetStringSelection())
    #------------------------------------------------------------------#

    def on_Interlace(self, event):
        """
        Enable or disable functionality 
        """
        if self.ckbx_interlace.IsChecked():
            self.ckbx_deinterlace.Disable()
            cmd_opt["interlace"] = "-vf interlace"
            
        elif not self.ckbx_interlace.IsChecked():
            self.ckbx_deinterlace.Enable()
            cmd_opt["interlace"] = ""
            
    #------------------------------------------------------------------#
    def mod_Interlace(self, event):
        # TODO this is work in progress
        
        print "'mod_Interlace' not implemented!"
        
    #------------------------------------------------------------------#
    def on_Vaspect(self, event):
        """
        Set parameter with choice and put in dict value 
        """
        if self.cmbx_Vaspect.GetValue() == "Set default":
            cmd_opt["VideoAspect"] = ""
            
        else:
            cmd_opt["VideoAspect"] = self.cmbx_Vaspect.GetValue()
            
    #------------------------------------------------------------------#
    def on_Vrate(self, event):
        """
        Set parameter with choice and put in dict value 
        """
        if self.cmbx_vrate.GetValue() == "Set default":
            cmd_opt["VideoRate"] = ""
            
        elif self.cmbx_vrate.GetValue() == "25 fps (50i) PAL":
            cmd_opt["VideoRate"] = "-r 25"
            
        elif self.cmbx_vrate.GetValue() == "29,97 fps (60i) NTSC":
            cmd_opt["VideoRate"] = "-r 29,97"
            
        elif self.cmbx_vrate.GetValue() == "30 fps (30p) Progessive":
            cmd_opt["VideoRate"] = "-r 30"
            
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
    def on_Audio(self, event):
        """
        Qualche formato video supporta una limitata scelta di codec audio,
        quindi imposto le liste dei formati audio supportati in base al 
        formato video scelto
        """
        audioformat = self.rdb_a.GetStringSelection()

        normlz = lambda: self.ckbx_a_normalize.Enable()

        if audioformat == "Default":
            self.audio_default()
            # reset parametrs
            normlz()
        #--------------------------------------------#
        elif audioformat == "Wav (Raw, No_MultiChannel)":
            cmd_opt["AudioCodec"] = "-c:a pcm_s16le"
            self.audio_("wav", "Audio WAV Codec Parameters"), normlz()
            
        elif audioformat == "Flac (Lossless, No_MultiChannel)":
            cmd_opt["AudioCodec"] = "-c:a flac"
            self.audio_("flac", "Audio FLAC Codec Parameters"), normlz()
            
        elif audioformat == "Aac (Lossy, MultiChannel)":
            cmd_opt["AudioCodec"] = "-c:a libfaac"
            self.audio_("aac", "Audio AAC Codec Parameters"), normlz()
            
        elif audioformat == "Alac (Lossless, m4v, No_MultiChannel)":
            cmd_opt["AudioCodec"] = "-c:a alac"
            self.audio_("alac", "Audio ALAC Codec Parameters"), normlz()
            
        elif audioformat == "Ac3 (Lossy, MultiChannel)":
            cmd_opt["AudioCodec"] = "-c:a ac3"
            self.audio_("ac3", "Audio AC3 Codec Parameters"), normlz()
        
        elif audioformat == "Ogg (Lossy, No_MultiChannel)":
            cmd_opt["AudioCodec"] = "-c:a libvorbis"
            self.audio_("ogg", "Audio OGG Codec Parameters"), normlz()
        
        elif audioformat == "Mp3 (Lossy, No_MultiChannel)":
            cmd_opt["AudioCodec"] = "-c:a libmp3lame"
            self.audio_("mp3", "Audio MP3 Codec Parameters"), normlz()

        elif audioformat == "Try to copy audio source":
            # reset parametrs
            self.ckbx_a_normalize.Disable()
            self.normalize_default()
            self.rdb_a.SetSelection(8)
            cmd_opt["AudioBitrate"] = ["",""]
            cmd_opt["AudioChannel"] = ["",""]
            cmd_opt["AudioRate"] = ["",""]
            cmd_opt["AudioDepth"] = ["",""]
            cmd_opt["Audio"] = audioformat
            cmd_opt["AudioCodec"] = "-c:a copy"

        elif audioformat == "No audio stream (silent)":
            # reset parametrs
            self.ckbx_a_normalize.Disable()
            self.normalize_default()
            self.rdb_a.SetSelection(9)
            cmd_opt["AudioBitrate"] = ["",""]
            cmd_opt["AudioChannel"] = ["",""]
            cmd_opt["AudioRate"] = ["",""]
            cmd_opt["AudioDepth"] = ["",""]
            cmd_opt["AudioCodec"] = "-an"
            cmd_opt["Audio"] = audioformat
            
    #-------------------------------------------------------------------#
    def audio_(self, audio_type, title):
        """
        Run a dialogs to choices audio parameters then set dictionary 
        at proper values.
        NOTE: The data[X] tuple contains the command parameters on the index [1] 
              and the descriptive parameters on the index [0].
              exemple: data[0] contains parameters for channel then
              data[0][1] is ffmpeg option command for audio channels and
              data[0][0] is a simple description for view.
        """ 
        audiodialog = audiodialogs.AudioSettings(self,audio_type,title)
        retcode = audiodialog.ShowModal()
        
        if retcode == wx.ID_OK:
            data = audiodialog.GetValue()
            cmd_opt["AudioChannel"] = data[0]
            cmd_opt["AudioRate"] = data[1]
            cmd_opt["AudioBitrate"] = data[2]
            if audio_type in  ('wav','aiff'):
                if 'Not set' in data[3][0]:
                    cmd_opt["AudioCodec"] = "-c:a pcm_s16le"
                else:
                    cmd_opt["AudioCodec"] = data[3][1]
                cmd_opt["AudioDepth"] = ["%s" % (data[3][0]),""]
            else:# entra su tutti tranne wav aiff
                cmd_opt["AudioDepth"] = data[3]
        else:
            data = None
            audiodialog.Destroy()
            return
        audiodialog.Destroy()

    #------------------------------------------------------------------#
    def onNormalize(self, event):  # check box
        """
        Enable or disable functionality for volume normalization of
        the video. Not enable if batch mode is enable
        """
        msg = ("Tip: check the volume peak by pressing the Analyzess button; "
               "set the normalize maximum amplitude or accept "
               "default dB value (-1.0)")
        if self.ckbx_a_normalize.GetValue():# is checked
            self.parent.statusbar_msg(msg, greenolive)
            self.btn_analyzes.Enable(), self.spin_ctrl_audionormalize.Enable()
            self.label_normalize.Enable()
            cmd_opt["Map"] = '-map 0'
            
            if len(self.parent.file_sources) == 1:# se solo un file
                self.text_dbMax.Enable(), self.text_dbMedium.Enable()
                self.label_dbMax.Enable(), self.label_dbMedium.Enable()

        elif not self.ckbx_a_normalize.GetValue():# is not checked
            self.parent.statusbar_msg("Disable audio normalization inside video", None)
            self.spin_ctrl_audionormalize.SetValue(-1.0), self.label_normalize.Disable()
            self.btn_analyzes.Disable(), self.spin_ctrl_audionormalize.Disable()
            self.text_dbMax.SetValue(""), self.text_dbMedium.SetValue("")
            self.text_dbMax.Disable(), self.text_dbMedium.Disable()
            self.label_dbMax.Disable(), self.label_dbMedium.Disable()
            cmd_opt["Map"] = ''
        cmd_opt["Normalize"] = ""
        
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
        msg = ("The audio stream peak level is equal to or higher " 
               "than the level set on the threshold. If you proceed, "
               "there will be no changes.")
        self.parent.statusbar_msg("",None)
        normalize = self.spin_ctrl_audionormalize.GetValue()

        data = volumeDetectProcess(self.ffmpeg_link, file_sources)

        if data[1]:
            wx.MessageBox(data[1], "ERROR! -Videomass2", wx.ICON_ERROR)
            return
        else:
            volume = list()

            for v in data[0]:
                maxvol = v[0].split(' ')[0]
                meanvol = v[1].split(' ')[0]
                offset = float(maxvol) - float(normalize)
                if float(maxvol) >= float(normalize):
                    # non processa se è superiore o uguale a norm.
                    self.parent.statusbar_msg(msg, yellow)
                    volume.append('')
                else:
                    volume.append("-af volume=%sdB" % (str(offset)[1:]))
                    
                if len(data[0]) == 1:# append in textctrl
                    self.text_dbMax.SetValue(""), 
                    self.text_dbMedium.SetValue("")
                    self.text_dbMax.AppendText(v[0])
                    self.text_dbMedium.AppendText(v[1])
                    
        cmd_opt["Normalize"] = volume
        self.btn_analyzes.Disable()
        
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
        wildcard = None
        if not exported:
            return
        
        elif len(exported) > 1:#if batch
            wildcard = "Source (*.%s)|*.%s| All files (*.*)|*.*" % (
                cmd_opt["VideoFormat"], cmd_opt["VideoFormat"])
            self.parent.post_process = [exported[0],wildcard]
            self.parent.postExported_enable()#enable menu items

        else:
            self.parent.post_process = [exported[0], wildcard]
            self.parent.postExported_enable()
    #-------------------------------------------------------------------#
    def update_allentries(self):
        """
        Last step for set definitively all values before to proceed
        with std_conv or batch_conv methods.
        Update _allentries is callaed by on_ok method.
        """
        self.time_seq = self.parent.time_seq
        self.set_Sizing()
        self.on_Vrate(self), self.on_Vaspect(self)
        
        if self.spin_ctrl_bitrate.IsEnabled():
            self.on_Bitrate(self)
        elif self.slider_CRF.IsEnabled():
            self.on_Crf(self)
        else:
            cmd_opt["CRF"] = ''
            cmd_opt["Bitrate"] = ''
        
        if self.ckbx_deinterlace.IsChecked():
            self.on_Deinterlace(self), self.mod_Deinterlace(self)
        elif self.ckbx_interlace.IsChecked():
            self.on_Interlace(self)

    #------------------------------------------------------------------#
    def on_ok(self):
        """
        Involves the files existence verification procedures and
        overwriting control.
        TODO: fare dizionario anche per map 0 da usare con normalization
        o aggiungi widget che lo spunti.
        """
        # check normalization data offset, if enable
        if self.ckbx_a_normalize.IsChecked():
            if self.btn_analyzes.IsEnabled():
                wx.MessageBox("Press the analyze button before proceeding.",
                              "Missing volume dectect -Videomass2")
                return
        # make a different id need to avoid attribute overwrite:
        file_sources = self.parent.file_sources[:]
        # make a different id need to avoid attribute overwrite:
        dir_destin = self.file_destin
        # used for file log name
        logname = 'Videomass_VideoConversion.log'

        ######## ------------ VALIDAZIONI: --------------
        if self.cmbx_vidContainers.GetValue() == "Copy Video Codec":
            self.time_seq = self.parent.time_seq
            checking = inspect(file_sources, dir_destin, '')
        else:
            self.update_allentries()# last update of all setting interface
            checking = inspect(file_sources, dir_destin, 
                            cmd_opt["VideoFormat"])
        if not checking[0]:# l'utente non vuole continuare o files assenti
            return
        # typeproc: batch or single process
        # filename: nome file senza ext.
        # base_name: nome file con ext.
        # lenghmax: count processing cicles for batch mode
        typeproc, file_sources, dir_destin,\
        filename, base_name, lenghmax = checking
    
        if self.rdb_automations.GetStringSelection() == "Save images from Video":
            self.saveimages(file_sources, dir_destin, filename, 
                            logname, lenghmax)
        else:
            if self.OS == 'Windows':
                null = 'NUL'
            else:
                null = '/dev/null'
            self.stdProc(file_sources, dir_destin, lenghmax, logname, null)

        return

    #------------------------------------------------------------------#
    def stdProc(self, file_sources, dir_destin, lenghmax, logname, null):
        """
        Composes the ffmpeg command strings for batch process. 
        In double pass mode, split command in two part (see  os_processing.py 
        at proc_batch_thread Class(Thread).
        """
        if self.cmbx_vidContainers.GetValue() == "Copy Video Codec":
            command = ('-loglevel %s %s %s %s %s %s %s %s %s %s %s -y' % (
                       self.loglevel_type, 
                       self.time_seq, 
                       cmd_opt["VideoCodec"], 
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
            valupdate = self.update_dict(lenghmax)
            ending = Formula(self, valupdate[0], valupdate[1])
            
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
                                           lenghmax, 
                                           )
                #used for play preview and mediainfo:
                self.exportStreams(dir_destin)#call function more above
                
        elif cmd_opt["Passing"] == "double":
            cmd1 = ('-loglevel %s %s -pass 1 -an %s %s %s %s %s %s '
                     '%s %s %s %s %s %s %s -f rawvideo -y %s' % (
                      self.loglevel_type, self.time_seq, 
                      cmd_opt["VideoCodec"], cmd_opt["Bitrate"], 
                      cmd_opt["Presets"], cmd_opt["Profile"],
                      cmd_opt["Tune"], cmd_opt["interlace"], 
                      cmd_opt["deinterlace"], cmd_opt["VideoSize"], 
                      cmd_opt["VideoAspect"], cmd_opt["VideoRate"],
                      cmd_opt["Orientation"][0], self.threads,
                      self.cpu_used, null),
                    )
            pass1 = " ".join(cmd1[0].split())# mi formatta la stringa
            cmd2= ('-loglevel %s %s -pass 2 %s %s %s %s %s %s '
                     '%s %s %s %s %s %s %s %s %s %s %s %s %s -y' % (
                     self.loglevel_type, self.time_seq, 
                     cmd_opt["VideoCodec"], cmd_opt["Bitrate"], 
                     cmd_opt["Presets"], cmd_opt["Profile"],
                     cmd_opt["Tune"], cmd_opt["interlace"], 
                     cmd_opt["deinterlace"], cmd_opt["VideoSize"], 
                     cmd_opt["VideoAspect"], cmd_opt["VideoRate"],
                     cmd_opt["Orientation"][0], cmd_opt["AudioCodec"], 
                     cmd_opt["AudioBitrate"][1], cmd_opt["AudioRate"][1], 
                     cmd_opt["AudioChannel"][1], cmd_opt["AudioDepth"][1], 
                     self.threads, self.cpu_used, cmd_opt["Map"])
                    )
            pass2 =  " ".join(cmd2.split())# mi formatta la stringa
            valupdate = self.update_dict(lenghmax)
            ending = Formula(self, valupdate[0], valupdate[1])
            
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
                                           lenghmax, 
                                           )
                #used for play preview and mediainfo:
                self.exportStreams(dir_destin)#call function more above
            #ending.Destroy() # con ID_OK e ID_CANCEL non serve Destroy()

        elif cmd_opt["Passing"] == "single": # Batch-Mode / h264 Codec
            command = ("-loglevel %s %s %s %s %s %s %s %s %s "
                       "%s %s %s %s %s %s %s %s %s %s %s %s -y" % (
                        self.loglevel_type, self.time_seq, 
                        cmd_opt["VideoCodec"], cmd_opt["CRF"], 
                        cmd_opt["Presets"], cmd_opt["Profile"],
                        cmd_opt["Tune"], cmd_opt["interlace"], 
                        cmd_opt["deinterlace"], cmd_opt["VideoSize"], 
                        cmd_opt["VideoAspect"], cmd_opt["VideoRate"],
                        cmd_opt["Orientation"][0], cmd_opt["AudioCodec"], 
                        cmd_opt["AudioBitrate"][1], cmd_opt["AudioRate"][1], 
                        cmd_opt["AudioChannel"][1], cmd_opt["AudioDepth"][1], 
                        self.threads, self.cpu_used, cmd_opt["Map"])
                        )
            command = " ".join(command.split())# mi formatta la stringa
            valupdate = self.update_dict(lenghmax)
            ending = Formula(self, valupdate[0], valupdate[1])
            
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
                                           lenghmax, 
                                           )
                self.exportStreams(dir_destin)#call function more above
    #--------------------------------------------------------------------#
    def saveimages(self, file_sources, dir_destin, 
                   filename, logname, lenghmax):
        """
        Save file (jpg) image from any video input. The saved images 
        are named image1.jpg, image2.jpg, image3...
        NOTE: non imposto 'loglevel_type' con l'opzione -stats sul loglevel 
              perchè non serve la lettura dell'output in real time e inoltre 
              voglio controllare solo l'uscita degli errori, se ci sono.
        """
        fileout = "image%d.jpg"
        cmd = ('%s -i "%s" -loglevel %s %s %s -an %s %s -y "%s/%s"' % (
               self.ffmpeg_link, 
               file_sources[0], 
               'error', # non imposto l'opzione -stats
               self.time_seq, 
               cmd_opt["VideoRate"], 
               self.threads, 
               self.cpu_used,
               dir_destin[0], 
               fileout)
               )
        command = " ".join(cmd.split())# mi formatta la stringa
        self.parent.switch_Process('saveimages',
                                   None, 
                                   None, 
                                   None, 
                                   command, 
                                   None, 
                                   None, 
                                   None, 
                                   logname, 
                                   lenghmax, 
                                   )
    #------------------------------------------------------------------#
    #------------------------------------------------------------------#
    def update_dict(self, lenghmax):
        """
        This method is required for update all cmd_opt
        dictionary values before send at epilogue
        """
        numfile = "%s file in pending" % str(lenghmax)
        if cmd_opt["Normalize"]:
            normalize = 'Enable'
        else:
            normalize = 'Disable'
        
        formula = (u"FORMULATIONS:\n\nFile to Queue\
                \nVideo Format:\nVideo codec:\nVideo bit-rate:\nCRF:\
                \nDouble/Single Pass:\nDeinterlacing:\
                \nInterlacing (progressive content)\nVideo size:\
                \nVideo aspect:\nVideo rate:\nPreset h264:\nProfile h264:\
                \nTune h264:\nOrientation:\nAudio Format:\nAudio codec:\nAudio channel:\
                \nAudio rate:\nAudio bit-rate:\nBit per Sample:\
                \nAudio Normalization:\nMap:\nTime selection:")
        dictions = ("\n\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\
                \n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s" % (
                numfile, cmd_opt["FormatChoice"], 
                cmd_opt["VideoCodec"], cmd_opt["Bitrate"], cmd_opt["CRF"], 
                cmd_opt["Passing"], cmd_opt["deinterlace"], cmd_opt["interlace"], 
                cmd_opt["VideoSize"], cmd_opt["VideoAspect"], 
                cmd_opt["VideoRate"], cmd_opt["Presets"], cmd_opt["Profile"], 
                cmd_opt["Tune"], cmd_opt["Orientation"][1], cmd_opt["Audio"], 
                cmd_opt["AudioCodec"], cmd_opt["AudioChannel"][0], 
                cmd_opt["AudioRate"][0], cmd_opt["AudioBitrate"][0],
                cmd_opt["AudioDepth"][0], normalize, cmd_opt["Map"], 
                self.time_seq))
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
        
        #if cmd_opt["VideoCodec"] == "-vcodec libx264":
        if cmd_opt["Passing"] == "double":
            command = ("-pass 1 -an %s %s %s %s %s %s %s %s %s %s %s %s "
                       "DOUBLE_PASS -pass 2 %s %s %s %s %s %s %s %s %s "
                       "%s %s %s %s %s %s %s %s %s %s" % (
            cmd_opt["VideoCodec"], cmd_opt["Bitrate"], cmd_opt["CRF"], 
            cmd_opt["interlace"], cmd_opt["deinterlace"], cmd_opt["Presets"], 
            cmd_opt["Profile"], cmd_opt["Tune"], cmd_opt["VideoSize"], 
            cmd_opt["VideoAspect"], cmd_opt["VideoRate"], cmd_opt["Orientation"][0],
            cmd_opt["VideoCodec"], cmd_opt["Bitrate"], cmd_opt["CRF"], 
            cmd_opt["interlace"], cmd_opt["deinterlace"], cmd_opt["Presets"], 
            cmd_opt["Profile"], cmd_opt["Tune"], cmd_opt["VideoSize"], 
            cmd_opt["VideoAspect"], cmd_opt["VideoRate"], cmd_opt["Orientation"][0], 
            cmd_opt["AudioCodec"], cmd_opt["AudioBitrate"][1],
            cmd_opt["AudioRate"][1], cmd_opt["AudioChannel"][1], 
            cmd_opt["AudioDepth"][1], cmd_opt["Normalize"], cmd_opt["Map"])
                        )

        elif cmd_opt["Passing"] == "single":
            command = ("%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s "
                       "%s %s %s %s" % (
            cmd_opt["VideoCodec"], cmd_opt["Bitrate"], cmd_opt["CRF"], 
            cmd_opt["Presets"], cmd_opt["Profile"], cmd_opt["Tune"], 
            cmd_opt["interlace"], cmd_opt["deinterlace"],cmd_opt["VideoSize"], 
            cmd_opt["VideoAspect"], cmd_opt["VideoRate"], cmd_opt["Orientation"][0],
            cmd_opt["AudioCodec"], cmd_opt["AudioBitrate"][1], 
            cmd_opt["AudioRate"][1], cmd_opt["AudioChannel"][1], 
            cmd_opt["AudioDepth"][1], cmd_opt["Normalize"], cmd_opt["Map"])
                        )
        command = ' '.join(command.split())# sitemo meglio gli spazi in stringa
        list = [command, cmd_opt["VideoFormat"]]

        filename = 'preset-v1-Personal'# nome del file preset senza ext
        name_preset = 'User Profiles'
        full_pathname = '%s/.videomass2/preset-v1-Personal.vdms' % dirname
        
        prstdlg = presets_addnew.MemPresets(self, 'addprofile', full_pathname, 
                                 filename, list, 'Create a new profile on '
                                 '"%s" preset - Videomass2' % (
                                 name_preset))
        prstdlg.ShowModal()
