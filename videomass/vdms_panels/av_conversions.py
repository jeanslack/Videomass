# -*- coding: UTF-8 -*-
"""
FileName: av_conversions.py
Porpose: audio/video conversions interface
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Aug.07.2025
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
import sys
import wx
import wx.lib.scrolledpanel as scrolled
from pubsub import pub
from videomass.vdms_utils.utils import update_timeseq_duration
from videomass.vdms_utils.get_bmpfromsvg import get_bmp
from videomass.vdms_threads.ffplay_file import FilePlay
from videomass.vdms_io.checkup import check_files
from videomass.vdms_dialogs.epilogue import Formula
from videomass.vdms_dialogs import setting_profiles
from videomass.vdms_dialogs.filter_crop import Crop
from videomass.vdms_dialogs.filter_transpose import Transpose
from videomass.vdms_dialogs.filter_denoisers import Denoisers
from videomass.vdms_dialogs.filter_deinterlace import Deinterlace
from videomass.vdms_dialogs.filter_scale import Scale
from videomass.vdms_dialogs.filter_stab import VidstabSet
from videomass.vdms_dialogs.filter_colorcorrection import ColorEQ
from videomass.vdms_dialogs.singlechoicedlg import SingleChoice
from videomass.vdms_dialogs.avconv_cmd_line import Raw_Cmd_Line
from videomass.vdms_threads.ffmpeg import get_raw_cmdline_args
from . video_encoders.video_no_enc import Video_No_Enc
from . video_encoders.mpeg4 import Mpeg_4
from . video_encoders.av1_aom import AV1_Aom
from . video_encoders.av1_svt import AV1_Svt
from . video_encoders.vp9_webm import Vp9_WebM
from . video_encoders.avc_x264 import Avc_X264
from . video_encoders.hevc_x265 import Hevc_X265
from . video_encoders.video_encodercopy import Copy_Vcodec
from . audio_encoders.acodecs import AudioEncoders
from . miscellaneous.miscell import Miscellaneous


class AV_Conv(wx.Panel):
    """
    Panel GUI for audio and video conversions
    """
    # colour rappresentetion in html
    AZURE = '#15a6a6'
    YELLOW = '#bd9f00'
    RED = '#ea312d'
    ORANGE = '#f28924'
    GREENOLIVE = '#6aaf23'
    GREEN = '#268826'
    CYAN = '#61ccc7'  # rgb form (wx.Colour(97, 204, 199)
    VIOLET = '#D64E93'
    LIMEGREEN = '#87A615'
    TROPGREEN = '#15A660'
    WHITE = '#fbf4f4'
    BLACK = '#060505'

    # MUXERS dictionary:
    MUXERS = {'mkv': 'matroska', 'avi': 'avi', 'mp4': 'mp4',
              'm4v': 'null', 'ogg': 'ogg', 'webm': 'webm',
              }
    # Namings in the video container selection combo box:
    VCODECS = ({"MPEG-4": {"-c:v mpeg4": ["avi"]},
                "XVID MPEG-4": {"-c:v libxvid": ["avi"]},
                "H.264": {"-c:v libx264": ["mkv", "mp4", "avi", "m4v"]},
                "H.264 10-bit": {"-c:v libx264": ["mkv", "mp4", "avi", "m4v"]},
                "H.265": {"-c:v libx265": ["mkv", "mp4", "avi", "m4v"]},
                "H.265 10-bit": {"-c:v libx265": ["mkv", "mp4", "avi", "m4v"]},
                "AOM-AV1": {"-c:v libaom-av1": ["mkv", "webm", "mp4"]},
                "SVT-AV1": {"-c:v libsvtav1": ["mkv", "webm"]},
                "SVT-AV1 10-bit": {"-c:v libsvtav1": ["mkv", "webm"]},
                "VP9": {"-c:v libvpx-vp9": ["webm", "mkv"]},
                "Copy": {"-c:v copy": ["mkv", "mp4", "avi", "m4v",
                                       "webm", "Copy"]}
                })
    # Namings in the audio format selection on Container combobox:
    A_FORMATS = ('wav', 'mp3', 'ac3', 'ogg', 'flac', 'm4a', 'aac', 'opus')
    # ------------------------------------------------------------------#

    def __init__(self, parent):
        """
        Collects all the values of the
        GUI controls used in this panel
        """
        self.parent = parent  # parent is the MainFrame
        get = wx.GetApp()  # get data from bootstrap
        self.appdata = get.appset
        icons = get.iconset
        self.videopanel = None

        if 'wx.svg' in sys.modules:  # only available in wx version 4.1 to up
            bmpplay = get_bmp(icons['preview'], ((16, 16)))
            self.bmpreset = get_bmp(icons['clear'], ((16, 16)))
            bmpresize = get_bmp(icons['scale'], ((16, 16)))
            bmpcrop = get_bmp(icons['crop'], ((16, 16)))
            bmprotate = get_bmp(icons['rotate'], ((16, 16)))
            bmpdeinterlace = get_bmp(icons['deinterlace'], ((16, 16)))
            bmpdenoiser = get_bmp(icons['denoiser'], ((16, 16)))
            bmpstab = get_bmp(icons['stabilizer'], ((16, 16)))
            bmpsaveprf = get_bmp(icons['addtoprst'], ((16, 16)))
            bmpcoloreq = get_bmp(icons['coloreq'], ((16, 16)))
            bmpcmd = get_bmp(icons['cmdshow'], ((16, 16)))
        else:
            bmpplay = wx.Bitmap(icons['preview'], wx.BITMAP_TYPE_ANY)
            self.bmpreset = wx.Bitmap(icons['clear'], wx.BITMAP_TYPE_ANY)
            bmpresize = wx.Bitmap(icons['scale'], wx.BITMAP_TYPE_ANY)
            bmpcrop = wx.Bitmap(icons['crop'], wx.BITMAP_TYPE_ANY)
            bmprotate = wx.Bitmap(icons['rotate'], wx.BITMAP_TYPE_ANY)
            bmpdeinterlace = wx.Bitmap(icons['deinterlace'],
                                       wx.BITMAP_TYPE_ANY)
            bmpdenoiser = wx.Bitmap(icons['denoiser'], wx.BITMAP_TYPE_ANY)
            bmpstab = wx.Bitmap(icons['stabilizer'], wx.BITMAP_TYPE_ANY)
            bmpsaveprf = wx.Bitmap(icons['addtoprst'], wx.BITMAP_TYPE_ANY)
            bmpcoloreq = wx.Bitmap(icons['coloreq'], wx.BITMAP_TYPE_ANY)
            bmpcmd = wx.Bitmap(icons['cmdshow'], wx.BITMAP_TYPE_ANY)

        # Default keys:values dictionary definition in this class
        self.opt = {"Media": "Video", "VidCmbxStr": "H.264",
                    "OutputFormat": "mkv", "VideoCodec": "-c:v libx264",
                    "ext_input": "", "Passes": "Auto", "InputDir": "",
                    "OutputDir": "", "SubtitleMap": "-map 0:s?",
                    "SubtitleEnc": "",
                    "Deinterlace": "", "Interlace": "", "ColorEQ": "",
                    "PixelFormat": "", "Orientation": ["", ""], "Crop": "",
                    "CropColor": "", "Scale": "", "Setdar": "", "Setsar": "",
                    "Denoiser": "", "Vidstabtransform": "",
                    "Vidstabdetect": "", "Unsharp": "", "Makeduo": False,
                    "VFilters": "", "CmdVideoParams": "", "CmdAudioParams": "",
                    "VideoMap": "-map 0:v?",

                    }
        wx.Panel.__init__(self, parent, -1)
        # ------------ widgets
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        # ------------------ BEGIN BOX top
        sizer_base.Add(10, 10)
        sizer_convin = wx.BoxSizer(wx.HORIZONTAL)
        txtmedia = wx.StaticText(self, wx.ID_ANY, _('Media:'))
        sizer_convin.Add(txtmedia, 0, wx.LEFT | wx.CENTRE, 5)
        self.cmb_Media = wx.ComboBox(self, wx.ID_ANY,
                                     choices=['Video', 'Audio'],
                                     size=(100, -1), style=wx.CB_DROPDOWN
                                     | wx.CB_READONLY
                                     )
        sizer_convin.Add(self.cmb_Media, 0, wx.LEFT | wx.CENTRE, 5)
        txtVcod = wx.StaticText(self, wx.ID_ANY, 'Video Encoder:')
        sizer_convin.Add(txtVcod, 0, wx.LEFT | wx.CENTRE, 20)
        self.cmb_vencoder = wx.ComboBox(self, wx.ID_ANY,
                                        choices=list(AV_Conv.VCODECS.keys()),
                                        size=(120, -1),
                                        style=wx.CB_DROPDOWN | wx.CB_READONLY
                                        )
        sizer_convin.Add(self.cmb_vencoder, 0, wx.LEFT | wx.CENTRE, 5)
        txtFormat = wx.StaticText(self, wx.ID_ANY, _('Container:'))
        sizer_convin.Add(txtFormat, 0, wx.LEFT | wx.CENTRE, 20)
        choices = list(AV_Conv.VCODECS['H.264'].values())[0]
        self.cmb_cont = wx.ComboBox(self, wx.ID_ANY,
                                    choices=choices,
                                    size=(100, -1),
                                    style=wx.CB_DROPDOWN
                                    | wx.CB_READONLY,
                                    )
        sizer_convin.Add(self.cmb_cont, 0, wx.LEFT | wx.CENTRE, 5)
        self.btn_saveprst = wx.Button(self, wx.ID_ANY, "", size=(40, -1))
        self.btn_saveprst.SetBitmap(bmpsaveprf, wx.LEFT)
        sizer_convin.Add(self.btn_saveprst, 0, wx.LEFT | wx.CENTRE, 20)
        self.btn_cmd = wx.Button(self, wx.ID_ANY, "", size=(40, -1))
        self.btn_cmd.SetBitmap(bmpcmd, wx.LEFT)
        sizer_convin.Add(self.btn_cmd, 0, wx.LEFT | wx.CENTRE, 5)
        msg = _("Target")
        box1 = wx.StaticBox(self, wx.ID_ANY, msg)
        box_convin = wx.StaticBoxSizer(box1, wx.HORIZONTAL)
        box_convin.Add(sizer_convin, 0, wx.ALL | wx.CENTRE, 5)
        sizer_base.Add(box_convin, 0, wx.BOTTOM | wx.CENTRE, 5)
        # END BOX top Media and Format

        # ------------------ BEGIN NOTEBOOK CONSTRUCTOR
        self.notebook = wx.Notebook(self, wx.ID_ANY,
                                    style=wx.NB_NOPAGETHEME | wx.NB_TOP
                                    )
        sizer_base.Add(self.notebook, 1, wx.ALL | wx.EXPAND, 5)
        # -------------- BEGIN NOTEBOOK PANEL 1
        self.nb_Video = wx.Panel(self.notebook, wx.ID_ANY)
        sizer_nbVideo = wx.BoxSizer(wx.HORIZONTAL)
        # VIDEO BOX video encoders central box
        box3 = wx.StaticBox(self.nb_Video, wx.ID_ANY, "")
        box_opt = wx.StaticBoxSizer(box3, wx.VERTICAL)
        sizer_nbVideo.Add(box_opt, 1, wx.ALL | wx.EXPAND, 5)

        # Inizializing VIDEO panels
        self.mpeg4panel = Mpeg_4(self.nb_Video, self.opt)
        self.aompanel = AV1_Aom(self.nb_Video, self.opt)
        self.svtpanel = AV1_Svt(self.nb_Video, self.opt)
        self.vp9panel = Vp9_WebM(self.nb_Video, self.opt)
        self.h264panel = Avc_X264(self.nb_Video, self.opt)
        self.h265panel = Hevc_X265(self.nb_Video, self.opt)
        self.vcopypanel = Copy_Vcodec(self.nb_Video, self.opt)
        self.disablevidpanels = Video_No_Enc(self.nb_Video)

        for vpan in (self.aompanel, self.svtpanel, self.vp9panel,
                     self.mpeg4panel, self.h264panel, self.h265panel,
                     self.vcopypanel, self.disablevidpanels,
                     ):
            box_opt.Add(vpan, 0, wx.ALL | wx.EXPAND, 5)

        self.vp9panel.Hide(), self.h265panel.Hide()
        self.aompanel.Hide(), self.svtpanel.Hide()
        self.vcopypanel.Hide(), self.mpeg4panel.Hide()
        self.disablevidpanels.Hide()
        self.videopanel = self.h264panel
        self.videopanel.Show()

        # BOX Video filters
        box4 = wx.StaticBox(self.nb_Video, wx.ID_ANY, "")
        self.box_Vfilters = wx.StaticBoxSizer(box4, wx.VERTICAL)
        sizer_nbVideo.Add(self.box_Vfilters, 0, wx.ALL | wx.EXPAND, 5)
        self.filterVpanel = scrolled.ScrolledPanel(self.nb_Video, -1,
                                                   size=(70, 700),
                                                   style=wx.TAB_TRAVERSAL
                                                   | wx.BORDER_NONE,
                                                   name="panelscroll",
                                                   )
        sizer_Vfilter = wx.BoxSizer(wx.VERTICAL)

        self.btn_preview = wx.Button(self.filterVpanel, wx.ID_ANY,
                                     "", size=(40, -1))
        self.btn_preview.SetBitmap(bmpplay, wx.LEFT)
        sizer_Vfilter.Add(self.btn_preview, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_preview.Disable()
        self.btn_reset = wx.Button(self.filterVpanel, wx.ID_ANY,
                                   "", size=(40, -1))
        self.btn_reset.SetBitmap(self.bmpreset, wx.LEFT)
        sizer_Vfilter.Add(self.btn_reset, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_reset.Disable()
        lineflt = wx.StaticLine(self.filterVpanel,
                                wx.ID_ANY,
                                pos=wx.DefaultPosition,
                                size=wx.DefaultSize,
                                style=wx.LI_HORIZONTAL,
                                name=wx.StaticLineNameStr,
                                )
        sizer_Vfilter.Add(lineflt, 0, wx.ALL | wx.EXPAND, 10)
        self.btn_videosize = wx.Button(self.filterVpanel, wx.ID_ANY,
                                       "", size=(40, -1))
        self.btn_videosize.SetBitmap(bmpresize, wx.LEFT)
        sizer_Vfilter.Add(self.btn_videosize, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_crop = wx.Button(self.filterVpanel, wx.ID_ANY,
                                  "", size=(40, -1))
        self.btn_crop.SetBitmap(bmpcrop, wx.LEFT)
        sizer_Vfilter.Add(self.btn_crop, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_rotate = wx.Button(self.filterVpanel, wx.ID_ANY,
                                    "", size=(40, -1))
        self.btn_rotate.SetBitmap(bmprotate, wx.LEFT)

        sizer_Vfilter.Add(self.btn_rotate, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_lacing = wx.Button(self.filterVpanel, wx.ID_ANY,
                                    "", size=(40, -1))
        self.btn_lacing.SetBitmap(bmpdeinterlace, wx.LEFT)
        sizer_Vfilter.Add(self.btn_lacing, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_denois = wx.Button(self.filterVpanel, wx.ID_ANY,
                                    "", size=(40, -1))
        self.btn_denois.SetBitmap(bmpdenoiser, wx.LEFT)
        sizer_Vfilter.Add(self.btn_denois, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_vidstab = wx.Button(self.filterVpanel, wx.ID_ANY,
                                     "", size=(40, -1))
        self.btn_vidstab.SetBitmap(bmpstab, wx.LEFT)
        sizer_Vfilter.Add(self.btn_vidstab, 0, wx.ALL | wx.CENTRE, 5)

        self.btn_coloreq = wx.Button(self.filterVpanel, wx.ID_ANY,
                                     "", size=(40, -1))
        self.btn_coloreq.SetBitmap(bmpcoloreq, wx.LEFT)
        sizer_Vfilter.Add(self.btn_coloreq, 0, wx.ALL | wx.CENTRE, 5)

        self.box_Vfilters.Add(self.filterVpanel, 1, wx.EXPAND)
        self.filterVpanel.SetSizer(sizer_Vfilter)  # set panel
        self.filterVpanel.SetAutoLayout(1)
        self.filterVpanel.SetupScrolling()

        self.nb_Video.SetSizer(sizer_nbVideo)
        self.notebook.AddPage(self.nb_Video, _("Video"))
        #  END NOTEBOOK PANEL 1 Video

        # -------------- BEGIN NOTEBOOK PANEL 2 Audio:
        self.nb_Audio = wx.Panel(self.notebook, wx.ID_ANY)
        sizer_nbAudio = wx.BoxSizer(wx.HORIZONTAL)
        box5 = wx.StaticBox(self.nb_Audio, wx.ID_ANY, "")
        box_audio = wx.StaticBoxSizer(box5, wx.VERTICAL)
        sizer_nbAudio.Add(box_audio, 1, wx.ALL | wx.EXPAND, 5)
        self.audioenc = AudioEncoders(self.nb_Audio, self.opt, self.parent)
        box_audio.Add(self.audioenc, 1, wx.ALL | wx.EXPAND, 5)
        self.nb_Audio.SetSizer(sizer_nbAudio)
        self.notebook.AddPage(self.nb_Audio, _("Audio"))

        # -------------- BEGIN NOTEBOOK PANEL 3 Miscellaneous:
        self.nb_misc = wx.Panel(self.notebook, wx.ID_ANY)
        sizer_nbmisc = wx.BoxSizer(wx.HORIZONTAL)
        box6 = wx.StaticBox(self.nb_misc, wx.ID_ANY, "")
        box_misc = wx.StaticBoxSizer(box6, wx.VERTICAL)
        sizer_nbmisc.Add(box_misc, 1, wx.ALL | wx.EXPAND, 5)
        self.miscfunc = Miscellaneous(self.nb_misc, self.opt)
        box_misc.Add(self.miscfunc, 1, wx.ALL | wx.EXPAND, 5)
        self.nb_misc.SetSizer(sizer_nbmisc)
        self.notebook.AddPage(self.nb_misc, _("Miscellaneous"))

        # ------------------ set layout
        self.SetSizer(sizer_base)
        self.Fit()
        self.Layout()
        # ---------------------- Tooltips
        tip = _('Save as a new profile of the Presets Manager.')
        self.btn_saveprst.SetToolTip(tip)
        tip = _('Displays the RAW commands of the selected file.')
        self.btn_cmd.SetToolTip(tip)
        tip = (_('Available video encoders. "Copy" means that the video '
                 'stream will not be re-encoded and will allow you (depending '
                 'on the encoder) to change the container, audio codec and a '
                 'few other parameters.'))
        self.cmb_vencoder.SetToolTip(tip)
        tip = (_('Container format. It is usually represented by the file '
                 'extension (output format).\n\nIf the Media target is set '
                 'to "Video" and the Video Encoder to "Copy", optionally you '
                 'can set this control to "Copy" the same container as '
                 'source file.\n\nIf the media target is set to "Audio", you '
                 'can extract only the audio streams from videos, or simply '
                 'convert audio source files.'))
        self.cmb_cont.SetToolTip(tip)
        tip = (_('Set output files target: "Video" to save output files as '
                 'video files; "Audio" to save files using an audio encoder '
                 'and format.\n\nNote that by using "Audio" as the target, '
                 'you will still be able to work on the video source files '
                 'but you will only be able to extract the audio streams, '
                 'convert them and apply audio filters such as '
                 'normalization.'))
        self.cmb_Media.SetToolTip(tip)
        self.btn_preview.SetToolTip(_('Preview video filters'))
        self.btn_reset.SetToolTip(_('Disable active filters'))
        self.btn_videosize.SetToolTip(_("Resize"))
        self.btn_crop.SetToolTip(_("Crop"))
        self.btn_rotate.SetToolTip(_("Transpose"))
        self.btn_lacing.SetToolTip(_("Deinterlace"))
        self.btn_denois.SetToolTip(_("Denoise"))
        self.btn_vidstab.SetToolTip(_("Stabilize"))
        self.btn_coloreq.SetToolTip(_("Equalize"))

        # ----------------------Binding (EVT)----------------------#

        # Note: wx.EVT_TEXT_ENTER é diverso da wx.EVT_TEXT: Il primo
        # é responsivo agli input di tastiera, il secondo é responsivo
        # agli input di tastiera ma anche agli "append"

        self.Bind(wx.EVT_COMBOBOX, self.videoCodec, self.cmb_vencoder)
        self.Bind(wx.EVT_COMBOBOX, self.on_Container, self.cmb_cont)
        self.Bind(wx.EVT_COMBOBOX, self.on_Media, self.cmb_Media)
        self.Bind(wx.EVT_BUTTON, self.on_saveprst, self.btn_saveprst)
        self.Bind(wx.EVT_BUTTON, self.on_Set_scale, self.btn_videosize)
        self.Bind(wx.EVT_BUTTON, self.on_Set_crop, self.btn_crop)
        self.Bind(wx.EVT_BUTTON, self.on_Set_transpose, self.btn_rotate)
        self.Bind(wx.EVT_BUTTON, self.on_Set_deinterlace, self.btn_lacing)
        self.Bind(wx.EVT_BUTTON, self.on_Set_denoiser, self.btn_denois)
        self.Bind(wx.EVT_BUTTON, self.on_Set_stabilizer, self.btn_vidstab)
        self.Bind(wx.EVT_BUTTON, self.on_Set_coloreq, self.btn_coloreq)
        self.Bind(wx.EVT_BUTTON, self.on_video_preview, self.btn_preview)
        self.Bind(wx.EVT_BUTTON, self.on_vfilters_clear, self.btn_reset)
        self.Bind(wx.EVT_BUTTON, self.on_audio_preview,
                  self.audioenc.btn_audio_preview)

        self.Bind(wx.EVT_BUTTON, self.on_cmd_line, self.btn_cmd)

        #  initialize default layout:
        self.cmb_vencoder.SetSelection(2)
        self.cmb_Media.SetSelection(0), self.cmb_cont.SetSelection(0)
        self.vencoder_panel_set(default=True)
        self.audioenc.startup_one_time(), self.audioenc.normalize_default()
        pub.subscribe(self.reset_on_changed_data, "RESET_ON_CHANGED_LIST")
    # -------------------------------------------------------------------#

    def reset_on_changed_data(self, msg):
        """
        Called using pub/sub protocol.
        Be sure to call this method at the end of the `init` code
        above to allow the `AudioEncoders` class to set the
        required objects, e.g. some `opt` dictionary keys.
        """
        if self.opt["PEAK"] or self.opt["RMS"]:
            self.audioenc.normalize_default()
        if self.opt["VFilters"]:
            self.on_vfilters_clear(self)
    # -------------------------------------------------------------------#

    def vencoder_panel_set(self, default=False):
        """
        Show/Hide and Reset the correspondig panel of the specified
        encoder. Inizializing this class make sure to pass the
        `default=True` argument to this method.
        """
        if self.cmb_Media.GetValue() == 'Audio':
            self.videopanel.default(), self.videopanel.Hide()
            self.filterVpanel.Disable(), self.on_vfilters_clear(self)
            self.videopanel = self.disablevidpanels
            self.videopanel.Show(), self.videopanel.default()
            self.opt["CmdVideoParams"] = ''

        elif self.opt["VideoCodec"] == "-c:v libx264":  # default
            if not default:
                self.filterVpanel.Enable(), self.videopanel.Hide()
                self.videopanel = self.h264panel
                self.videopanel.Show()
            self.videopanel.default()

        elif self.opt["VideoCodec"] == "-c:v libx265":
            self.filterVpanel.Enable(), self.videopanel.Hide()
            self.videopanel = self.h265panel
            self.videopanel.Show(), self.videopanel.default()

        elif self.opt["VideoCodec"] == "-c:v libvpx-vp9":
            self.filterVpanel.Enable(), self.videopanel.Hide()
            self.videopanel = self.vp9panel
            self.videopanel.Show(), self.videopanel.on_reset_args(None)

        elif self.opt["VideoCodec"] == "-c:v libaom-av1":
            self.filterVpanel.Enable(), self.videopanel.Hide()
            self.videopanel = self.aompanel
            self.videopanel.Show(), self.videopanel.default()

        elif self.opt["VideoCodec"] == "-c:v libsvtav1":
            self.filterVpanel.Enable(), self.videopanel.Hide()
            self.videopanel = self.svtpanel
            self.videopanel.Show(), self.videopanel.on_reset_args(None)

        elif self.opt["VideoCodec"] in ("-c:v mpeg4", "-c:v libxvid"):
            self.filterVpanel.Enable(), self.videopanel.Hide()
            self.videopanel = self.mpeg4panel
            self.videopanel.Show(), self.videopanel.default()

        elif self.opt["VideoCodec"] == "-c:v copy":
            self.filterVpanel.Disable(), self.on_vfilters_clear(self)
            self.videopanel.Hide()
            self.videopanel = self.vcopypanel
            self.videopanel.Show(), self.videopanel.default()

        self.nb_Video.Layout()  # force Layout

    # ----------------------Event handler (callback)----------------------#

    def videoCodec(self, event):
        """
        This event triggers the setting to the default values.
        """
        selected = AV_Conv.VCODECS.get(self.cmb_vencoder.GetValue())
        libcodec = list(selected.keys())[0]
        self.cmb_cont.Clear()
        for f in selected.values():
            self.cmb_cont.Append((f),)
        self.cmb_cont.SetSelection(0)
        self.opt["VideoCodec"] = libcodec
        self.opt["VidCmbxStr"] = self.cmb_vencoder.GetValue()
        self.opt["OutputFormat"] = self.cmb_cont.GetValue()
        self.vencoder_panel_set()
        self.audioenc.audio_default()
        self.audioenc.set_audio_radiobox(None)
        self.miscfunc.set_subt_radiobox()
    # ------------------------------------------------------------------#

    def on_Media(self, event):
        """
        Combobox Media Sets layout to Audio or Video formats
        """
        if self.cmb_Media.GetValue() == 'Audio':
            self.opt["Media"] = 'Audio'
            self.cmb_vencoder.Disable()
            self.opt["VideoCodec"] = ''
            self.opt["VidCmbxStr"] = ''
            self.audioenc.audio_default()
            self.cmb_cont.Clear()
            for f in AV_Conv.A_FORMATS:
                self.cmb_cont.Append((f),)
            self.cmb_cont.SetSelection(0)
            self.opt["OutputFormat"] = self.cmb_cont.GetValue()
            self.vencoder_panel_set()
            self.audioenc.set_audio_radiobox(None)
            self.miscfunc.set_subt_radiobox()

        elif self.cmb_Media.GetValue() == 'Video':
            self.opt["Media"] = 'Video'
            self.cmb_vencoder.Enable()
            self.cmb_vencoder.SetSelection(2)
            self.videoCodec(self)
            self.miscfunc.set_subt_radiobox()
    # ------------------------------------------------------------------#

    def on_Container(self, event):
        """
        Appends on container combobox according to audio and video formats
        """
        if self.cmb_cont.GetValue() == "Copy":
            self.opt["OutputFormat"] = ''
        else:
            self.opt["OutputFormat"] = self.cmb_cont.GetValue()
        self.audioenc.set_audio_radiobox(None)
        self.miscfunc.set_subt_radiobox()
    # ------------------------------------------------------------------#

    def on_video_preview(self, event):
        """
        Showing selected video preview with applied filters.
        Note that libstab filter is not possible to preview.
        """
        fget = self.file_selection()
        if not fget or not self.opt["VFilters"]:
            return
        if self.opt["Vidstabtransform"]:
            wx.MessageBox(_("To preview Stabilize filter, please click "
                            "Preview button on Video Stabilizer Tool"),
                          "Videomass", wx.ICON_INFORMATION, self)
            return

        flt = self.opt["VFilters"]
        autoexit = '-autoexit' if self.parent.autoexit else ''

        if self.parent.checktimestamp:
            args = (f'{autoexit} -i "{self.parent.file_src[fget[1]]}" '
                    f'{self.parent.time_seq} '
                    f'{flt},"{self.parent.cmdtimestamp}"')
        else:
            args = f'{autoexit} -i "{self.parent.file_src[fget[1]]}" {flt}'
        try:
            with open(self.parent.file_src[fget[1]], encoding='utf-8'):
                FilePlay(args)
        except IOError:
            wx.MessageBox(_("Invalid or unsupported file:  %s") % (filepath),
                          "Videomass", wx.ICON_EXCLAMATION, self)
            return
    # ------------------------------------------------------------------#

    def on_audio_preview(self, event):
        """
        Button event for button preview on `self.audioenc`.
        Only Bind it in this class.
        """
        fget = self.file_selection()
        self.audioenc.on_audio_preview(fget)
    # ------------------------------------------------------------------#

    def on_vfilters_clear(self, event):
        """
        Reset all enabled filters. If default disablevidstab
        arg is True, it disable only vidstab filter values.
        """
        if self.opt["VFilters"]:
            self.opt['Crop'], self.opt["Orientation"] = "", ["", ""]
            self.opt['Scale'], self.opt['Setdar'] = "", ""
            self.opt['Setsar'], self.opt['Deinterlace'] = "", ""
            self.opt['Interlace'], self.opt['Denoiser'] = "", ""
            self.opt["Vidstabtransform"], self.opt["Unsharp"] = "", ""
            self.opt["Vidstabdetect"], self.opt["Makeduo"] = "", False
            self.opt["VFilters"], self.opt["ColorEQ"] = "", ""

            self.btn_videosize.SetBackgroundColour(wx.NullColour)
            self.btn_crop.SetBackgroundColour(wx.NullColour)
            self.btn_denois.SetBackgroundColour(wx.NullColour)
            self.btn_lacing.SetBackgroundColour(wx.NullColour)
            self.btn_rotate.SetBackgroundColour(wx.NullColour)
            self.btn_vidstab.SetBackgroundColour(wx.NullColour)
            self.btn_coloreq.SetBackgroundColour(wx.NullColour)
            self.btn_preview.Disable()
            self.btn_reset.Disable()
    # ------------------------------------------------------------------#

    def file_selection(self):
        """
        Gets the selected file on files list and returns an object
        of type list [str('selected file name'), int(index)].
        Returns None if no files are selected.

        """
        if len(self.parent.file_src) == 1:
            return (self.parent.file_src[0], 0)

        if not self.parent.filedropselected:
            wx.MessageBox(_("Have to select an item in the file list first"),
                          'Videomass', wx.ICON_INFORMATION, self)
            return None

        clicked = self.parent.filedropselected
        return (clicked, self.parent.file_src.index(clicked))
    # ------------------------------------------------------------------#

    def get_video_stream(self):
        """
        Given a frame or a video file, it returns a dict object
        containing required video parameters as width, height, etc.
        """
        fget = self.file_selection()
        if not fget:
            return None

        index = self.parent.data_files[fget[1]]

        if 'video' in index.get('streams')[0]['codec_type']:
            width = int(index['streams'][0]['width'])
            height = int(index['streams'][0]['height'])
            filename = index['format']['filename']
            duration = index['format'].get('time', '00:00:00.000')
            if not width or not height:
                wx.MessageBox(_('Unsupported file:\n'
                                'Missing decoder or library? '
                                'Check FFmpeg configuration.'),
                              _('Videomass - Warning!'), wx.ICON_WARNING, self)
                self.on_vfilters_clear(self)
                return None
            return dict(zip(['width', 'height', 'filename', 'duration'],
                            [width, height, filename, duration]))

        wx.MessageBox(_('The file is not a frame or a video file'),
                      _('Videomass - Warning!'), wx.ICON_WARNING, self)
        self.on_vfilters_clear(self)
        return None
    # ------------------------------------------------------------------#

    def chain_all_video_filters(self):
        """
        Concatenate all video filters enabled and sorts
        them according to an consistance ffmpeg syntax.
        """
        orderf = (self.opt['Deinterlace'], self.opt['Interlace'],
                  self.opt["Denoiser"], self.opt["Vidstabtransform"],
                  self.opt["Unsharp"], self.opt['Crop'], self.opt['Scale'],
                  self.opt["Setdar"], self.opt["Setsar"],
                  self.opt['Orientation'][0], self.opt["ColorEQ"],
                  )  # do not change the order of the filters on this tuple
        filters = ''.join([f'{x},' for x in orderf if x])[:-1]

        if filters:
            self.opt["VFilters"] = f"-vf {filters}"
            self.btn_preview.Enable(), self.btn_reset.Enable()
        else:
            self.opt["VFilters"] = ""
            self.btn_preview.Disable(), self.btn_reset.Disable()
    # ------------------------------------------------------------------#

    def on_Set_scale(self, event):
        """
        Enable or disable scale, setdar and setsar filters
        """
        kwa = self.get_video_stream()
        if not kwa:
            return
        with Scale(self,
                   self.opt["Scale"],
                   self.opt["Setdar"],
                   self.opt["Setsar"],
                   self.bmpreset,
                   **kwa,
                   ) as sizing:
            if sizing.ShowModal() == wx.ID_OK:
                data = sizing.getvalue()
                if not [x for x in data.values() if x]:
                    self.btn_videosize.SetBackgroundColour(wx.NullColour)
                    self.opt["Setdar"] = ""
                    self.opt["Setsar"] = ""
                    self.opt["Scale"] = ""
                else:
                    self.btn_videosize.SetBackgroundColour(
                        wx.Colour(AV_Conv.VIOLET))
                    self.opt["Scale"] = data['scale']
                    self.opt['Setdar'] = data['setdar']
                    self.opt['Setsar'] = data['setsar']

                self.chain_all_video_filters()
    # -----------------------------------------------------------------#

    def on_Set_transpose(self, event):
        """
        Enable or disable transpose filter for frame rotations
        """
        kwa = self.get_video_stream()
        if not kwa:
            return
        with Transpose(self,
                       self.opt["Orientation"][0],
                       self.opt["Orientation"][1],
                       self.bmpreset,
                       **kwa,
                       ) as rotate:
            if rotate.ShowModal() == wx.ID_OK:
                data = rotate.getvalue()
                self.opt["Orientation"][0] = data[0]  # cmd option
                self.opt["Orientation"][1] = data[1]  # msg
                if not data[0]:
                    self.btn_rotate.SetBackgroundColour(wx.NullColour)
                else:
                    self.btn_rotate.SetBackgroundColour(
                        wx.Colour(AV_Conv.VIOLET))
                self.chain_all_video_filters()
    # ------------------------------------------------------------------#

    def on_Set_crop(self, event):
        """
        Enable or disable crop filter
        """
        kwa = self.get_video_stream()
        if not kwa:
            return
        with Crop(self, self.opt["Crop"], self.opt["CropColor"],
                  self.bmpreset, **kwa) as crop:
            if crop.ShowModal() == wx.ID_OK:
                data = crop.getvalue()
                if not data:
                    self.btn_crop.SetBackgroundColour(wx.NullColour)
                    self.opt["Crop"] = ''
                    self.opt["CropColor"] = ''
                else:
                    self.btn_crop.SetBackgroundColour(
                        wx.Colour(AV_Conv.VIOLET))
                    self.opt["Crop"] = f'crop={data[0]}'
                    self.opt["CropColor"] = data[1]
                self.chain_all_video_filters()
    # ------------------------------------------------------------------#

    def on_Set_deinterlace(self, event):
        """
        Enable or disable filter for deinterlacing
        (w3fdif and yadif) and interlace filter.
        """
        sdf = self.get_video_stream()
        if not sdf:
            return
        with Deinterlace(self,
                         self.opt["Deinterlace"],
                         self.opt["Interlace"],
                         self.bmpreset,
                         ) as lacing:
            if lacing.ShowModal() == wx.ID_OK:
                data = lacing.getvalue()
                if not data:
                    self.btn_lacing.SetBackgroundColour(wx.NullColour)
                    self.opt["Deinterlace"] = ''
                    self.opt["Interlace"] = ''
                else:
                    self.btn_lacing.SetBackgroundColour(
                        wx.Colour(AV_Conv.VIOLET))
                    if 'deinterlace' in data:
                        self.opt["Deinterlace"] = data["deinterlace"]
                        self.opt["Interlace"] = ''
                    elif 'interlace' in data:
                        self.opt["Interlace"] = data["interlace"]
                        self.opt["Deinterlace"] = ''
                self.chain_all_video_filters()
    # ------------------------------------------------------------------#

    def on_Set_denoiser(self, event):
        """
        Enable or disable denoiser filters (nlmeans and hqdn3d)
        useful in some case, i.e. when apply a deinterlace filter.
        <https://askubuntu.com/questions/866186/how-to-get-good-quality-when-
        converting-digital-video>
        """
        sdf = self.get_video_stream()
        if not sdf:
            return
        with Denoisers(self, self.opt["Denoiser"], self.bmpreset) as den:
            if den.ShowModal() == wx.ID_OK:
                data = den.getvalue()
                if not data:
                    self.btn_denois.SetBackgroundColour(wx.NullColour)
                    self.opt["Denoiser"] = ''
                else:
                    self.btn_denois.SetBackgroundColour(
                        wx.Colour(AV_Conv.VIOLET))
                    self.opt["Denoiser"] = data
                self.chain_all_video_filters()
    # ------------------------------------------------------------------#

    def on_Set_stabilizer(self, event):
        """
        Enable or disable libvidstab filter for video stabilization.
        Note, this filter is incompatible with two-pass encoding that
        includes `-pass 1` and` -pass 2` ffmpeg args/options.
        """
        sdf = self.get_video_stream()
        if not sdf:
            return
        with VidstabSet(self,
                        self.opt["Vidstabdetect"],
                        self.opt["Vidstabtransform"],
                        self.opt["Unsharp"],
                        self.opt["Makeduo"],
                        self.bmpreset,
                        **sdf,
                        ) as stab:
            if stab.ShowModal() == wx.ID_OK:
                data = stab.getvalue()
                if not data:
                    self.btn_vidstab.SetBackgroundColour(wx.NullColour)
                    self.opt["Vidstabdetect"] = ""
                    self.opt["Vidstabtransform"] = ""
                    self.opt["Unsharp"] = ""
                    self.opt["Makeduo"] = False
                else:
                    self.btn_vidstab.SetBackgroundColour(
                        wx.Colour(AV_Conv.VIOLET))
                    self.opt["Vidstabdetect"] = data[0]
                    self.opt['Vidstabtransform'] = data[1]
                    self.opt['Unsharp'] = data[2]
                    self.opt["Makeduo"] = data[3]
                self.chain_all_video_filters()
    # ------------------------------------------------------------------#

    def on_Set_coloreq(self, event):
        """
        Enable or disable color correction filter like
        contrast, brightness, saturation, gamma.
        """
        kwa = self.get_video_stream()
        if not kwa:
            return
        with ColorEQ(self, self.opt["ColorEQ"], self.bmpreset, **kwa,
                     ) as coloreq:
            if coloreq.ShowModal() == wx.ID_OK:
                data = coloreq.getvalue()
                if not data:
                    self.btn_coloreq.SetBackgroundColour(wx.NullColour)
                    self.opt["ColorEQ"] = ''
                else:
                    self.btn_coloreq.SetBackgroundColour(
                        wx.Colour(AV_Conv.VIOLET))
                    self.opt["ColorEQ"] = data
                self.chain_all_video_filters()
    # ------------------------------------------------------------------#

    def get_codec_args(self):
        """
        Get data from encoder panels and set ffmpeg
        command arguments
        """
        self.opt["CmdVideoParams"] = self.videopanel.video_options()
        self.opt["CmdAudioParams"] = self.audioenc.audio_options()

        if self.opt["Media"] == 'Video':

            if self.opt["Vidstabdetect"]:
                kwargs = self.video_stabilizer()

            elif self.opt["EBU"][0] == 'EBU R128 (High-Quality)':
                kwargs = self.video_ebu()
            else:
                kwargs = self.video_std()

            return kwargs

        # self.opt["Media"] == 'Audio':
        if self.opt["EBU"][0] == 'EBU R128 (High-Quality)':
            kwargs = self.audio_ebu()
        else:
            kwargs = self.audio_std()

        return kwargs
    # ------------------------------------------------------------------#

    def check_options(self, index=None, checkexists=True):
        """
        Update entries and file check.
        """
        if self.audioenc.btn_voldect.IsEnabled():
            wx.MessageBox(_('Undetected volume values! Click the '
                            '"Volume detect" button to analyze '
                            'audio volume data.'),
                          'Videomass', wx.ICON_INFORMATION, self)
            return None

        if index is not None:
            infile = [self.parent.file_src[index]]
            outfilenames = [self.parent.outputnames[index]]
        else:
            infile = self.parent.file_src
            outfilenames = self.parent.outputnames

        filecheck = check_files(infile,
                                self.appdata['outputdir'],
                                self.appdata['outputdir_asinput'],
                                self.appdata['filesuffix'],
                                self.opt["OutputFormat"],
                                outfilenames,
                                checkexists=checkexists,
                                )
        if not filecheck:  # User changing idea or not such files exist
            return None
        return filecheck
    # ------------------------------------------------------------------#

    def queue_mode(self):
        """
        build queue mode arguments. This method is
        called by `parent.on_add_to_queue`.
        Return a dictionary of data.
        """
        logname = 'Queue Processing.log'
        index = self.parent.file_src.index(self.parent.filedropselected)

        check = self.check_options(index)
        if not check:
            return None

        f_src, f_dest = check[0][0], check[1][0]
        kwargs = self.get_codec_args()
        dur, ss, et = update_timeseq_duration(self.parent.time_seq,
                                              self.parent.duration
                                              )
        kwargs['extension'] = self.opt["OutputFormat"]
        kwargs['pre-input-1'], kwargs['pre-input-2'] = '', ''
        kwargs['logname'] = logname
        kwargs['source'] = f_src
        kwargs['destination'] = f_dest
        kwargs["duration"] = dur[index]
        kwargs['start-time'], kwargs['end-time'] = ss, et
        if kwargs.get("volume"):
            kwargs["volume"] = kwargs["volume"][index]
        else:
            kwargs["volume"] = ''

        return kwargs
    # ------------------------------------------------------------------#

    def batch_mode(self):
        """
        build batch mode arguments. This method is called
        by `parent.click_start`
        """
        logname = 'AV Conversions.log'

        check = self.check_options()
        if not check:
            return None

        f_src, f_dest = check
        kwargs = self.get_codec_args()
        dur, ss, et = update_timeseq_duration(self.parent.time_seq,
                                              self.parent.duration
                                              )
        kwargs['extension'] = self.opt["OutputFormat"]
        kwargs['pre-input-1'], kwargs['pre-input-2'] = '', ''
        kwargs['logname'] = logname
        kwargs['start-time'], kwargs['end-time'] = ss, et
        batchlist = []
        for index in enumerate(self.parent.file_src):
            kw = kwargs.copy()
            kw['source'] = f_src[index[0]]
            kw['destination'] = f_dest[index[0]]
            kw['duration'] = dur[index[0]]
            if kw.get("volume"):
                kw["volume"] = kw["volume"][index[0]]
            else:
                kw["volume"] = ''
            batchlist.append(kw)

        keyval = self.update_dict(len(f_src), **kwargs)
        ending = Formula(self, (700, 250),
                         self.parent.movetotrash,
                         self.parent.emptylist,
                         **keyval,
                         )
        if ending.ShowModal() == wx.ID_OK:
            (self.parent.movetotrash,
             self.parent.emptylist) = ending.getvalue()
            self.parent.switch_to_processing(kwargs["type"],
                                             logname,
                                             datalist=batchlist
                                             )
        return None
    # ------------------------------------------------------------------#

    def video_stabilizer(self):
        """
        Build ffmpeg command strings for two pass
        video stabilizations process.

        """
        if self.opt["EBU"][0] == 'EBU R128 (High-Quality)':

            if self.opt["Passes"] == '2':
                cmd1 = (f'{self.opt["CmdVideoParams"]} '
                        f'-filter:v {self.opt["Vidstabdetect"]} '
                        f'{self.opt["passlogfile1"]} {self.opt["AudioIndex"]} '
                        f'-filter:a: {self.opt["EBU"][1]} -sn -dn '
                        f'-f {AV_Conv.MUXERS[self.opt["OutputFormat"]]}'
                        )
                cmd2 = (f'{self.opt["CmdVideoParams"]} {self.opt["VFilters"]} '
                        f'{self.opt["passlogfile2"]} '
                        f'{self.opt["CmdAudioParams"]} '
                        f'{self.opt["SubtitleEnc"]} {self.opt["SubtitleMap"]} '
                        f'{self.opt["Chapters"]} {self.opt["MetaData"]}'
                        )
            else:  # single pass
                cmd1 = (f'-filter:v {self.opt["Vidstabdetect"]} '
                        f'{self.opt["AudioIndex"]} '
                        f'-filter:a: {self.opt["EBU"][1]} -sn -dn -f null'
                        )
                cmd2 = (f'{self.opt["CmdVideoParams"]} '
                        f'{self.opt["VFilters"]} {self.opt["CmdAudioParams"]} '
                        f'{self.opt["SubtitleEnc"]} {self.opt["SubtitleMap"]} '
                        f'{self.opt["Chapters"]} {self.opt["MetaData"]}'
                        )
            pass1, pass2 = " ".join(cmd1.split()), " ".join(cmd2.split())
            kwargs = {'type': 'Two pass EBU', 'args': [pass1, pass2],
                      'EBU': self.opt["EBU"][1],
                      'audiomap': self.opt["AudioMap"],
                      'preset name':
                          'A/V Conversions - Video VIDSTAB/EBU Norm.',
                      }
        else:
            audnorm = (self.opt["RMS"] if not self.opt["PEAK"]
                       else self.opt["PEAK"])

            cmd1 = (f'-filter:v {self.opt["Vidstabdetect"]} '
                    f'-an -sn -dn -f null'
                    )
            cmd2 = (f'{self.opt["CmdVideoParams"]} {self.opt["VFilters"]} '
                    f'{self.opt["CmdAudioParams"]} {self.opt["EBU"][1]} '
                    f'{self.opt["SubtitleEnc"]} {self.opt["SubtitleMap"]} '
                    f'{self.opt["Chapters"]} {self.opt["MetaData"]}'
                    )
            pass1, pass2 = " ".join(cmd1.split()), " ".join(cmd2.split())
            kwargs = {'type': 'Two pass VIDSTAB', 'args': [pass1, pass2],
                      'volume': [vol[5] for vol in audnorm],
                      'preset name': 'A/V Conversions - Video VIDSTAB.',
                      }
        return kwargs
        # ------------------------------------------------------------------#

    def video_std(self):
        """
        Build the ffmpeg args strings for standard
        video conversions.
        """
        audnorm = self.opt["RMS"] if not self.opt["PEAK"] else self.opt["PEAK"]

        if self.cmb_vencoder.GetValue() == "Copy":

            args = (f'{self.opt["CmdVideoParams"]} '
                    f'{self.opt["CmdAudioParams"]} {self.opt["EBU"][1]} '
                    f'{self.opt["SubtitleEnc"]} {self.opt["SubtitleMap"]} '
                    f'{self.opt["Chapters"]} {self.opt["MetaData"]}'
                    )
            pass1, pass2 = " ".join(args.split()), ''
            kwargs = {'type': 'One pass', 'args': [pass1, pass2],
                      'volume': [vol[5] for vol in audnorm],
                      'preset name': 'A/V Conversions - Video standard',
                      }
        elif self.opt["Passes"] == "2":

            cmd1 = (f'{self.opt["CmdVideoParams"]} {self.opt["VFilters"]} '
                    f'{self.opt["passlogfile1"]} -an -sn -dn -f rawvideo'
                    )
            cmd2 = (f'{self.opt["CmdVideoParams"]} {self.opt["VFilters"]} '
                    f'{self.opt["passlogfile2"]} {self.opt["CmdAudioParams"]} '
                    f'{self.opt["EBU"][1]} {self.opt["SubtitleEnc"]} '
                    f'{self.opt["SubtitleMap"]} {self.opt["Chapters"]} '
                    f'{self.opt["MetaData"]}'
                    )
            pass1, pass2 = " ".join(cmd1.split()), " ".join(cmd2.split())
            kwargs = {'type': 'Two pass', 'args': [pass1, pass2],
                      'volume': [vol[5] for vol in audnorm],
                      'preset name': 'A/V Conversions - Video standard.',
                      }
        elif self.opt["Passes"] == "Auto":
            args = (f'{self.opt["CmdVideoParams"]} {self.opt["VFilters"]} '
                    f'{self.opt["CmdAudioParams"]} {self.opt["EBU"][1]} '
                    f'{self.opt["SubtitleEnc"]} {self.opt["SubtitleMap"]} '
                    f'{self.opt["Chapters"]} {self.opt["MetaData"]}'
                    )
            pass1, pass2 = " ".join(args.split()), ''
            kwargs = {'type': 'One pass', 'args': [pass1, pass2],
                      'volume': [vol[5] for vol in audnorm],
                      'preset name': 'A/V Conversions - Video standard',
                      }
        else:
            return None
        return kwargs
    # ------------------------------------------------------------------#

    def video_ebu(self):
        """
        Build the ffmpeg args strings for video conversions
        with two-pass EBU.
        NOTE If you want leave same indexes and process a selected Input Audio
             Index use same Output Audio Index on Audio Streams Mapping box

        """
        if self.cmb_vencoder.GetValue() == "Copy":
            cmd_1 = (f'{self.opt["AudioIndex"]} '
                     f'-filter:a: {self.opt["EBU"][1]} -vn -sn -dn  -f null'
                     )
            cmd_2 = (f'{self.opt["CmdVideoParams"]} {self.opt["VFilters"]} '
                     f'{self.opt["CmdAudioParams"]} {self.opt["SubtitleEnc"]} '
                     f'{self.opt["SubtitleMap"]} {self.opt["Chapters"]} '
                     f'{self.opt["MetaData"]}'
                     )
            pass1 = " ".join(cmd_1.split())
            pass2 = " ".join(cmd_2.split())
            kwargs = {'type': 'Two pass EBU', 'args': [pass1, pass2],
                      'EBU': self.opt["EBU"][1],
                      'audiomap': self.opt["AudioMap"],
                      'preset name': 'A/V Conversions - copy Video/EBU Norm.',
                      }
        elif self.opt["Passes"] == "2":

            cmd_1 = (f'{self.opt["CmdVideoParams"]} {self.opt["VFilters"]} '
                     f'{self.opt["passlogfile1"]} {self.opt["AudioIndex"]} '
                     f'-filter:a: {self.opt["EBU"][1]} '
                     f'-sn -dn -f {AV_Conv.MUXERS[self.opt["OutputFormat"]]}'
                     )
            cmd_2 = (f'{self.opt["CmdVideoParams"]} {self.opt["VFilters"]} '
                     f'{self.opt["passlogfile2"]} '
                     f'{self.opt["CmdAudioParams"]} {self.opt["SubtitleEnc"]} '
                     f'{self.opt["SubtitleMap"]} {self.opt["Chapters"]} '
                     f'{self.opt["MetaData"]}'
                     )
            pass1 = " ".join(cmd_1.split())
            pass2 = " ".join(cmd_2.split())
            kwargs = {'type': 'Two pass EBU', 'args': [pass1, pass2],
                      'EBU': self.opt["EBU"][1],
                      'audiomap': self.opt["AudioMap"],
                      'preset name': 'A/V Conversions - Video/EBU Norm.',
                      }
        else:
            cmd_1 = (f'{self.opt["AudioIndex"]} '
                     f'-filter:a: {self.opt["EBU"][1]} -vn -sn -dn -f null'
                     )
            cmd_2 = (f'{self.opt["CmdVideoParams"]} {self.opt["VFilters"]} '
                     f'{self.opt["CmdAudioParams"]} {self.opt["SubtitleEnc"]} '
                     f'{self.opt["SubtitleMap"]} {self.opt["Chapters"]} '
                     f'{self.opt["MetaData"]}'
                     )
            pass1 = " ".join(cmd_1.split())
            pass2 = " ".join(cmd_2.split())
            kwargs = {'type': 'Two pass EBU', 'args': [pass1, pass2],
                      'EBU': self.opt["EBU"][1],
                      'audiomap': self.opt["AudioMap"],
                      'preset name': 'A/V Conversions - Video/EBU Norm.',
                      }
        return kwargs
    # ------------------------------------------------------------------#

    def audio_std(self):
        """
        Build the ffmpeg args strings for standard
        audio conversions.

        """
        audnorm = self.opt["RMS"] if not self.opt["PEAK"] else self.opt["PEAK"]

        args = (f'{self.opt["CmdAudioParams"]} '
                f'{self.opt["EBU"][1]} -vn -sn {self.opt["MetaData"]}'
                )
        pass1, pass2 = " ".join(args.split()), ''
        kwargs = {'type': 'One pass', 'args': [pass1, pass2],
                  'volume': [vol[5] for vol in audnorm],
                  'preset name': 'A/V Conversions - Audio standard',
                  }
        return kwargs
    # ------------------------------------------------------------------#

    def audio_ebu(self):
        """
        Build the ffmpeg args strings for audio conversions
        and EBU R128 normalization.
        WARNING do not map output audio file index on filter:a: , -c:a:
        and not send self.opt["AudioMap"] to process because the files
        audio has not indexes
        """
        cmd_1 = (f'{self.opt["AudioMap"][0]} -filter:a: {self.opt["EBU"][1]} '
                 f'-vn -sn -dn -f null'
                 )
        cmd_2 = (f'{self.opt["CmdAudioParams"]} -vn -sn {self.opt["MetaData"]}'
                 )
        pass1 = " ".join(cmd_1.split())
        pass2 = " ".join(cmd_2.split())
        kwargs = {'type': 'Two pass EBU', 'args': [pass1, pass2],
                  'EBU': self.opt["EBU"][1], 'audiomap': self.opt["AudioMap"],
                  'preset name': 'A/V Conversions - Audio/EBU Norm.',
                  }
        return kwargs
    # ------------------------------------------------------------------#

    def update_dict(self, countmax, **kwa):
        """
        Update to epilogue
        """
        if self.opt["PEAK"]:
            normalize = 'PEAK'
        elif self.opt["RMS"]:
            normalize = 'RMS'
        elif self.opt["EBU"]:
            normalize = self.opt["EBU"][0]
        else:
            normalize = _('Off')
        if self.cmb_cont.GetValue() == "Copy":
            outputformat = "Copy"
        else:
            outputformat = self.opt["OutputFormat"]
        if not self.parent.time_seq:
            sst, endt = _('Same as source'), _('Same as source')
        else:
            sst = kwa["start-time"].split()[1]
            endt = kwa["end-time"].split()[1]
        if self.appdata['outputdir_asinput']:
            dest = _('Same destination paths as source files')
        else:
            dest = self.appdata['outputdir']

        if self.opt["Media"] == 'Audio':
            subtitles = _('Disabled')
        elif not self.opt["SubtitleEnc"]:
            subtitles = _('Auto')
        elif self.opt["SubtitleEnc"] == '-sn':
            subtitles = _('No Subtitles')
        else:
            subtitles = self.opt["SubtitleEnc"].split()[1]

        passes = '1' if kwa["args"][1] == '' else '2'

        keys = (_("Batch processing items\nDestination\nAutomation/Preset"
                  "\nEncoding passes\nOutput Format\nVideo Codec"
                  "\nSubtitle Stream\nAudio Codec\nAudio Normalization"
                  "\nOutput multimedia type\nStart of segment"
                  "\nClip duration"
                  ))
        vals = (f'{countmax}\n'
                f'{dest}\n'
                f'{kwa["preset name"]}\n'
                f'{passes}\n'
                f'{outputformat}\n'
                f'{self.opt["VidCmbxStr"]}\n'
                f'{subtitles}\n'
                f'{self.opt["AudioCodStr"]}\n'
                f'{normalize}\n'
                f'{self.opt["Media"]}\n'
                f'{sst}\n'
                f'{endt}'
                )
        return {'key': keys, 'val': vals}
    # ------------------------------------------------------------------#

    def on_cmd_line(self, event):
        """
        Displays the raw command line output.
        """
        try:
            index = self.parent.file_src.index(self.parent.filedropselected)
        except ValueError:
            wx.MessageBox(_("Have to select an item in the file list first"),
                          'Videomass', wx.ICON_INFORMATION, self)
            return None

        check = self.check_options(index=index, checkexists=False)
        if not check:
            return None
        f_src, f_dest = check[0][0], check[1][0]
        kwargs = self.get_codec_args()
        dur, ss, et = update_timeseq_duration(self.parent.time_seq,
                                              self.parent.duration
                                              )
        kwargs['extension'] = self.opt["OutputFormat"]
        kwargs['pre-input-1'], kwargs['pre-input-2'] = '', ''
        kwargs['source'] = f_src
        kwargs['destination'] = f_dest
        kwargs["duration"] = dur[index]
        kwargs['start-time'], kwargs['end-time'] = ss, et
        if kwargs.get("volume"):
            kwargs["volume"] = kwargs["volume"][index]
        else:
            kwargs["volume"] = ''

        cmd = get_raw_cmdline_args(**kwargs)

        displaycmd = Raw_Cmd_Line(self, *cmd)
        displaycmd.ShowModal()

        return None
    # ------------------------------------------------------------------#

    def save_to_preset(self, presetname):
        """
        Save the current profile in the Preset Manager
        """
        if self.cmb_Media.GetValue() == 'Video':
            self.opt["CmdVideoParams"] = self.videopanel.video_options()
            self.opt["CmdAudioParams"] = self.audioenc.audio_options()

            if self.opt["Vidstabdetect"]:
                kwargs = self.video_stabilizer()
            elif self.opt["EBU"][0] == 'EBU R128 (High-Quality)':
                kwargs = self.video_ebu()
            else:
                kwargs = self.video_std()

        else:  # self.cmb_Media.GetValue() == 'Audio'
            self.opt["CmdAudioParams"] = self.audioenc.audio_options()
            if self.opt["EBU"][0] == 'EBU R128 (High-Quality)':
                kwargs = self.audio_ebu()
            else:
                kwargs = self.audio_std()

        fname = os.path.basename(presetname)
        title = _('Write profile on «{0}»').format(fname)
        args = kwargs["args"][0], kwargs["args"][1], self.opt["OutputFormat"]
        with setting_profiles.SettingProfile(self, 'addprofile',
                                             presetname,
                                             args,
                                             title,
                                             ) as prstdialog:

            if prstdialog.ShowModal() == wx.ID_CANCEL:
                return
        self.parent.PrstsPanel.presets_refresh(self)
        return
    # ------------------------------------------------------------------#

    def preset_name(self, action):
        """
        Return the preset name
        """
        defaultdir = os.path.join(self.appdata['confdir'], 'presets')
        if action == 0:
            with wx.FileDialog(self, _("Enter name for new preset"),
                               defaultDir=defaultdir,
                               wildcard="Videomass preset (*.json;)|*.json;",
                               style=wx.FD_SAVE
                               | wx.FD_OVERWRITE_PROMPT) as fileDialog:
                fileDialog.SetFilename('New preset.json')
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return None
                filename = fileDialog.GetPath()
                if os.path.splitext(filename)[1].strip() != '.json':
                    wx.LogError(_('Invalid file name, make sure to provide a '
                                  'valid name including the «.json» '
                                  'extension'))
                    return None
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write('[]')
            except IOError:
                wx.LogError(_("Cannot save current "
                              "data in file «{}».").format(filename))
                return None

        elif action == 1:
            with wx.FileDialog(self, _("Open Videomass preset"),
                               defaultDir=defaultdir,
                               wildcard="Videomass preset (*.json;)|*.json;",
                               style=wx.FD_OPEN
                               | wx.FD_FILE_MUST_EXIST) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return None
                filename = fileDialog.GetPath()
        else:
            return None

        return filename
    # ------------------------------------------------------------------#

    def on_saveprst(self, event):
        """
        Asks to the user where add the new profile
        """
        caption = _('Videomass - Save new profile')
        message = _('Where do you want to save this profile?')
        choices = (_('Save the profile to a new preset'),
                   _('Save the profile to an existing preset'))
        with SingleChoice(self, caption, message, choices, 0) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                presetname = self.preset_name(dlg.getvalue())
            else:
                return
        if not presetname:
            return

        self.save_to_preset(presetname)
