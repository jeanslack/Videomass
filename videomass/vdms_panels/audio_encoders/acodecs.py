# -*- coding: UTF-8 -*-
"""
FileName: acodecs.py
Porpose: Contains audio functionality for A/V Conversions
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: July.26.2025
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
import sys
import wx
import wx.lib.scrolledpanel as scrolled
import wx.lib.agw.floatspin as FS
from videomass.vdms_utils.get_bmpfromsvg import get_bmp
from videomass.vdms_dialogs.audioproperties import AudioProperties
from videomass.vdms_utils.utils import get_volume_data
from videomass.vdms_io.io_tools import volume_detect_process
from videomass.vdms_dialogs.shownormlist import AudioVolNormal
from videomass.vdms_threads.ffplay_file import FilePlay


class AudioEncoders(scrolled.ScrolledPanel):
    """
    This scroll panel implements audio controls
    for A/V Conversions.
    """
    VIOLET = '#D64E93'
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
    # compatibility between video formats and related audio codecs:
    AV_FORMATS = {('avi'): ('default', 'wav', None, None, None, 'ac3', None,
                            'mp3', None, 'copy', 'mute'),
                  ('mp4'): ('default', None, None, 'aac', None, 'ac3', None,
                            'mp3', 'opus', 'copy', 'mute'),
                  ('m4v'): ('default', None, None, 'aac', 'alac', None, None,
                            None, None, 'copy', 'mute'),
                  ('mkv'): ('default', 'wav', 'flac', 'aac', None, 'ac3',
                            'ogg', 'mp3', 'opus', 'copy', 'mute'),
                  ('webm'): ('default', None, None, None, None, None, 'ogg',
                             None, 'opus', 'copy', 'mute'),
                  ('wav'): (None, 'wav', None, None, None, None, None, None,
                            None, 'copy', None),
                  ('mp3'): (None, None, None, None, None, None, None, 'mp3',
                            None, 'copy', None),
                  ('ac3'): (None, None, None, None, None, 'ac3', None, None,
                            None, 'copy', None),
                  ('ogg'): (None, None, None, None, None, None, 'ogg', None,
                            'opus', 'copy', None),
                  ('flac'): (None, None, 'flac', None, None, None, None, None,
                             None, 'copy', None),
                  ('m4a'): (None, None, None, None, 'alac', None, None, None,
                            None, 'copy', None),
                  ('aac'): (None, None, None, 'aac', None, None, None, None,
                            None, 'copy', None),
                  ('opus'): (None, None, None, None, None, None, None, None,
                             'opus', 'copy', None),
                  }

    def __init__(self, parent, opt, maindata):
        """
        This is a child of `nb_Audio` of `AV_Conv` class-panel (parent)
        """
        self.parent = parent  # parent is the `nb_Audio` here.
        self.maindata = maindata  # data on MainFrame
        self.appdata = self.maindata.appdata
        self.opt = opt
        icons = self.maindata.icons

        if 'wx.svg' in sys.modules:  # only available in wx version 4.1 to up
            bmpapreview = get_bmp(icons['preview_audio'], ((16, 16)))
            bmpanalyzes = get_bmp(icons['volanalyze'], ((16, 16)))
            bmpasettings = get_bmp(icons['settings'], ((16, 16)))
            bmppeaklevel = get_bmp(icons['audiovolume'], ((16, 16)))
        else:
            bmpapreview = wx.Bitmap(icons['preview_audio'], wx.BITMAP_TYPE_ANY)
            bmpanalyzes = wx.Bitmap(icons['volanalyze'], wx.BITMAP_TYPE_ANY)
            bmpasettings = wx.Bitmap(icons['settings'], wx.BITMAP_TYPE_ANY)
            bmppeaklevel = wx.Bitmap(icons['audiovolume'], wx.BITMAP_TYPE_ANY)

        scrolled.ScrolledPanel.__init__(self, parent, -1,
                                        size=(1024, 1024),
                                        style=wx.TAB_TRAVERSAL
                                        | wx.BORDER_NONE,
                                        name="Audio Codecs scrolledpanel",
                                        )
        sizerbase = wx.BoxSizer(wx.VERTICAL)
        self.labinfo = wx.StaticText(self, wx.ID_ANY,
                                     label=_('Audio encoder settings, '
                                             'mapping and filters'),
                                     style=wx.ALIGN_CENTRE_HORIZONTAL)
        sizerbase.Add(self.labinfo, 0, wx.EXPAND | wx.ALL, 2)
        if self.appdata['ostype'] == 'Darwin':
            self.labinfo.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        else:
            self.labinfo.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        # sizerbase.Add((0, 15), 0)
        self.rdb_a = wx.RadioBox(self, wx.ID_ANY,
                                 (_("Audio Encoder")), size=(-1, -1),
                                 choices=list(AudioEncoders.ACODECS.keys()),
                                 majorDimension=0, style=wx.RA_SPECIFY_COLS
                                 )
        for n, v in enumerate(AudioEncoders.AV_FORMATS["mkv"]):
            if not v:  # disable only not compatible with mkv
                self.rdb_a.EnableItem(n, enable=False)

        sizerbase.Add(self.rdb_a, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_set = wx.Button(self, wx.ID_ANY, _("Settings"),
                                 size=(-1, -1))
        self.btn_set.SetBitmap(bmpasettings, wx.LEFT)
        sizerbase.Add(self.btn_set, 0, wx.ALL | wx.CENTRE, 5)
        line1 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=(-1, -1), style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        sizerbase.Add(line1, 0, wx.ALL | wx.EXPAND, 15)
        sizproper = wx.BoxSizer(wx.HORIZONTAL)
        sizerbase.Add(sizproper, 0, wx.CENTRE)
        txtAinmap = wx.StaticText(self, wx.ID_ANY, _('Index Selection:'))
        sizproper.Add(txtAinmap, 0, wx.LEFT | wx.CENTRE, 20)
        self.cmb_A_inMap = wx.ComboBox(self, wx.ID_ANY,
                                       choices=['Auto', '1', '2', '3',
                                                '4', '5', '6', '7', '8', '9',
                                                '10', '11', '12', '13', '14',
                                                '15', '16',],
                                       size=(-1, -1), style=wx.CB_DROPDOWN
                                       | wx.CB_READONLY,
                                       )
        sizproper.Add(self.cmb_A_inMap, 0, wx.LEFT | wx.CENTRE, 5)
        txtAoutmap = wx.StaticText(self, wx.ID_ANY, _('Map:'))
        sizproper.Add(txtAoutmap, 0, wx.LEFT | wx.CENTRE, 20)
        self.cmb_A_outMap = wx.ComboBox(self, wx.ID_ANY,
                                        choices=['Auto', 'All', 'Index only'],
                                        size=(-1, -1),
                                        style=wx.CB_DROPDOWN
                                        | wx.CB_READONLY,
                                        )
        sizproper.Add(self.cmb_A_outMap, 0, wx.LEFT | wx.CENTRE, 5)
        self.btn_audio_preview = wx.Button(self, wx.ID_ANY,
                                           _("Preview"), size=(-1, -1))
        self.btn_audio_preview.SetBitmap(bmpapreview, wx.LEFT)
        sizproper.Add(self.btn_audio_preview, 0, wx.LEFT | wx.CENTRE, 20)
        line2 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=(-1, -1), style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        sizerbase.Add(line2, 0, wx.ALL | wx.EXPAND, 15)
        sizer_a_normaliz = wx.BoxSizer(wx.VERTICAL)
        sizerbase.Add(sizer_a_normaliz, 0, wx.EXPAND)
        normopt = [('Off'), ('PEAK'), ('RMS'), ('EBU R128 (Worst)'),
                   ('EBU R128 (High-Quality)')]
        self.rdbx_normalize = wx.RadioBox(self, wx.ID_ANY,
                                          (_("Normalization")), size=(-1, -1),
                                          choices=normopt,
                                          majorDimension=1,
                                          style=wx.RA_SPECIFY_ROWS,
                                          )
        sizer_a_normaliz.Add(self.rdbx_normalize, 0, wx.ALL | wx.CENTRE, 5)
        sizer_a_normaliz.Add((0, 10), 0)

        grid_peak = wx.FlexGridSizer(1, 4, 15, 4)
        sizer_a_normaliz.Add(grid_peak, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_voldect = wx.Button(self, wx.ID_ANY,
                                     _("Volume detect"), size=(-1, -1))
        self.btn_voldect.SetBitmap(bmppeaklevel, wx.LEFT)
        grid_peak.Add(self.btn_voldect, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.btn_stat = wx.Button(self, wx.ID_ANY,
                                  _("Volume Statistics"), size=(-1, -1))
        self.btn_stat.SetBitmap(bmpanalyzes, wx.LEFT)
        grid_peak.Add(self.btn_stat, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.lab_amplitude = wx.StaticText(self, wx.ID_ANY, _("Target level:"))
        grid_peak.Add(self.lab_amplitude, 0, wx.LEFT
                      | wx.ALIGN_CENTER_VERTICAL, 20)
        self.spin_target = FS.FloatSpin(self, wx.ID_ANY,
                                        min_val=-99.0, max_val=0.0,
                                        increment=0.5, value=-1.0,
                                        agwStyle=FS.FS_LEFT, size=(120, -1)
                                        )
        self.spin_target.SetFormat("%f"), self.spin_target.SetDigits(1)
        grid_peak.Add(self.spin_target, 0, wx.LEFT | wx.CENTRE, 2)

        self.lab_help_norm = wx.StaticText(self, wx.ID_ANY, (""),
                                           style=wx.ALIGN_CENTRE_HORIZONTAL)
        sizer_a_normaliz.Add(self.lab_help_norm, 0, wx.ALL | wx.CENTRE, 5)

        sizer_a_normaliz.Add((0, 15), 0)
        grid_ebu = wx.FlexGridSizer(1, 6, 0, 0)
        sizer_a_normaliz.Add(grid_ebu, 0, wx.ALL | wx.CENTRE, 5)
        lab_i = wx.StaticText(self, wx.ID_ANY, ("IL:"))
        grid_ebu.Add(lab_i, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.spin_i = FS.FloatSpin(self, wx.ID_ANY,
                                   min_val=-70.0, max_val=-5.0,
                                   increment=0.5, value=-16.0,
                                   agwStyle=FS.FS_LEFT, size=(120, -1)
                                   )
        self.spin_i.SetFormat("%f"), self.spin_i.SetDigits(1)
        grid_ebu.Add(self.spin_i, 0, wx.LEFT | wx.CENTRE, 5)

        lab_tp = wx.StaticText(self, wx.ID_ANY, ("TP:"))
        grid_ebu.Add(lab_tp, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        self.spin_tp = FS.FloatSpin(self, wx.ID_ANY,
                                    min_val=-9.0, max_val=0.0,
                                    increment=0.5, value=-1.5,
                                    agwStyle=FS.FS_LEFT, size=(120, -1)
                                    )
        self.spin_tp.SetFormat("%f"), self.spin_tp.SetDigits(1)
        grid_ebu.Add(self.spin_tp, 0, wx.LEFT | wx.CENTRE, 5)

        lab_lra = wx.StaticText(self, wx.ID_ANY, ("LRA:"))
        grid_ebu.Add(lab_lra, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        self.spin_lra = FS.FloatSpin(self, wx.ID_ANY,
                                     min_val=1.0, max_val=20.0,
                                     increment=0.5, value=11.0,
                                     agwStyle=FS.FS_LEFT, size=(120, -1)
                                     )
        self.spin_lra.SetFormat("%f"), self.spin_lra.SetDigits(1)
        grid_ebu.Add(self.spin_lra, 0, wx.LEFT | wx.CENTRE, 5)
        self.lab_help_ebu = wx.StaticText(self, wx.ID_ANY, (""),
                                          style=wx.ALIGN_CENTRE_HORIZONTAL)
        sizer_a_normaliz.Add(self.lab_help_ebu, 0, wx.ALL | wx.CENTRE, 5)

        if self.appdata['ostype'] == 'Darwin':
            self.lab_help_norm.SetFont(wx.Font(11, wx.DEFAULT,
                                               wx.NORMAL, wx.NORMAL))
            self.lab_help_ebu.SetFont(wx.Font(11, wx.DEFAULT,
                                              wx.NORMAL, wx.NORMAL))
        else:
            self.lab_help_norm.SetFont(wx.Font(8, wx.DEFAULT,
                                               wx.NORMAL, wx.NORMAL))
            self.lab_help_ebu.SetFont(wx.Font(8, wx.DEFAULT,
                                              wx.NORMAL, wx.NORMAL))
        self.SetSizer(sizerbase)  # set panel
        self.SetAutoLayout(1)
        self.SetupScrolling()

        tip = (_('Gets maximum volume and average volume data in dBFS, then '
                 'calculates the offset amount for audio normalization.'))
        self.btn_voldect.SetToolTip(tip)
        tip = (_('Limiter for the maximum peak level or the mean level '
                 '(when switch to RMS) in dBFS. From -99.0 to +0.0; default '
                 'for PEAK level is -1.0; default for RMS is -20.0'))
        self.spin_target.SetToolTip(tip)
        tip = (_('"Auto", lets FFmpeg select the audio stream to process '
                 '(usually the first audio stream). If the source file(s) '
                 'is just an audio track, it\'s recommend to always set this '
                 'control to "Auto."\n\n"1-16", if a video file contains '
                 'more than one audio stream, you can select a specific '
                 'one, e.g "1" for the first available audio stream, '
                 '"2" for the second audio stream, and so on.'))
        self.cmb_A_inMap.SetToolTip(tip)
        tip = (_('"Auto" keeps all audio streams and processes only the one '
                 'selected by the "Index Selection" control.\n\n'
                 '"All" processes all audio streams with the properties '
                 'of the one selected by the "Index Selection" control. '
                 'Don\'t use "All" to export audio files from videos.\n\n'
                 '"Index Only" processes only the audio stream selected by '
                 'the "Index Selection" control and removes all others '
                 'from the output video.'))
        self.cmb_A_outMap.SetToolTip(tip)
        tip = (_('Integrated Loudness Target in LUFS. '
                 'From -70.0 to -5.0, default is -16.0'))
        self.spin_i.SetToolTip(tip)
        tip = (_('Maximum True Peak in dBTP. From -1.5 '
                 'to +0.0, default is -2.0'))
        self.spin_tp.SetToolTip(tip)
        tip = (_('Loudness Range Target in LUFS. '
                 'From +1.0 to +20.0, default is +11.0'))
        self.spin_lra.SetToolTip(tip)
        tip = (_('Play the audio stream selected in the "Index Selection" '
                 'control. Using this function you can test the result of '
                 'audio normalization.'))
        self.btn_audio_preview.SetToolTip(tip)

        self.Bind(wx.EVT_RADIOBOX, self.on_getting_acodec, self.rdb_a)
        self.Bind(wx.EVT_BUTTON, self.on_setting_acodec, self.btn_set)
        self.Bind(wx.EVT_COMBOBOX, self.on_audio_index, self.cmb_A_inMap)
        self.Bind(wx.EVT_COMBOBOX, self.on_audio_mapping, self.cmb_A_outMap)
        self.Bind(wx.EVT_RADIOBOX, self.on_normalize, self.rdbx_normalize)
        self.Bind(wx.EVT_SPINCTRL, self.on_enter_gain, self.spin_target)
        self.Bind(wx.EVT_BUTTON, self.on_analyzes, self.btn_voldect)
        self.Bind(wx.EVT_BUTTON, self.on_show_vol_statistics, self.btn_stat)
    # ------------------------------------------------------------------#

    def audio_options(self):
        """
        Get audio parameters
        """
        if self.rdbx_normalize.GetSelection() == 0:
            del self.opt["PEAK"][:]
            del self.opt["RMS"][:]
            self.opt["EBU"] = ["", ""]

        if self.rdbx_normalize.GetSelection() == 1:  # is checked
            del self.opt["RMS"][:]
            self.opt["EBU"] = ["", ""]

        elif self.rdbx_normalize.GetSelection() == 2:
            del self.opt["PEAK"][:]
            self.opt["EBU"] = ["", ""]

        elif self.rdbx_normalize.GetSelection() == 3:
            del self.opt["PEAK"][:]
            del self.opt["RMS"][:]
            loud = (f'-filter:a: loudnorm=I={str(self.spin_i.GetValue())}'
                    f':LRA={str(self.spin_lra.GetValue())}'
                    f':TP={str(self.spin_tp.GetValue())}')
            self.opt["EBU"][1] = loud

        elif self.rdbx_normalize.GetSelection() == 4:
            del self.opt["PEAK"][:]
            del self.opt["RMS"][:]
            loud = (f'loudnorm=I={str(self.spin_i.GetValue())}:'
                    f'TP={str(self.spin_tp.GetValue())}:'
                    f'LRA={str(self.spin_lra.GetValue())}:'
                    f'print_format=summary'
                    )
            self.opt["EBU"][1] = loud

        return (f'{self.opt["AudioMap"][0]} '
                f'{self.opt["AudioCodec"][0]} '
                f'{self.opt["AudioCodec"][1]} '
                f'{self.opt["AudioBitrate"][1]} '
                f'{self.opt["AudioRate"][1]} '
                f'{self.opt["AudioChannel"][1]} '
                f'{self.opt["AudioDepth"][1]}'
                )
    # ------------------------------------------------------------------#

    def startup_one_time(self):
        """
        This method needs to be called only once when the
        parent `init` method is started, to create the
        required default dict keys.
        """
        self.opt["AudioIndex"] = ""
        self.opt["AudioMap"] = ["-map 0:a:?", ""]
        self.opt["PEAK"] = []
        self.opt["RMS"] = []
        self.opt["EBU"] = ["", ""]
        self.audio_default()
    # ------------------------------------------------------------------#

    def audio_default(self):
        """
        Set default audio parameters. This method is called
        whenever changes the video container selection.
        """
        self.rdb_a.SetStringSelection("Auto")
        self.opt["AudioCodStr"] = "Auto"
        self.opt["AudioCodec"] = ["", ""]
        self.opt["AudioBitrate"] = ["", ""]
        self.opt["AudioChannel"] = ["", ""]
        self.opt["AudioRate"] = ["", ""]
        self.opt["AudioDepth"] = ["", ""]
        self.btn_set.Disable()
        self.btn_set.SetBackgroundColour(wx.NullColour)
        # self.rdbx_normalize.Enable()
        self.cmb_A_outMap.SetSelection(0)
        self.cmb_A_inMap.SetSelection(0)
        self.cmb_A_outMap.Disable()
    # -------------------------------------------------------------------#

    def normalize_default(self, setoff='all'):
        """
        Reset normalization parameters on the audio properties.
        This method even is called by `MainFrame.switch_video_conv()`
        on start-up and when there are changing on `dragNdrop` panel.
        """
        del self.opt["PEAK"][:]
        del self.opt["RMS"][:]
        self.opt["EBU"] = ["", ""]

        if setoff == 'all':
            self.rdbx_normalize.SetSelection(0)
            self.spin_i.Disable(), self.spin_lra.Disable()
            self.spin_tp.Disable(), self.btn_voldect.Disable()
            self.spin_target.Disable(), self.btn_stat.Disable()
            self.spin_target.SetValue(-1.0)

        elif setoff == 'ebu':
            self.btn_voldect.Disable(), self.spin_target.Disable()
            self.btn_stat.Disable(), self.spin_i.Enable()
            self.spin_lra.Enable(), self.spin_tp.Enable()
            self.opt["EBU"][0] = self.rdbx_normalize.GetStringSelection()

        elif setoff == 'rms':
            self.spin_i.Disable(), self.spin_lra.Disable()
            self.spin_tp.Disable(), self.btn_voldect.Enable()
            self.spin_target.Enable(), self.btn_stat.Disable()
            self.spin_target.SetValue(-20.0)

        elif setoff == 'peak':
            self.spin_i.Disable(), self.spin_lra.Disable()
            self.spin_tp.Disable(), self.btn_voldect.Enable()
            self.spin_target.Enable(), self.btn_stat.Disable()
            self.spin_target.SetValue(-1.0)
    # ------------------------------------------------------------------#

    def on_audio_preview(self, fileget):
        """
        It allows a direct evaluation of the sound results given
        by the audio filters with the ability to playback even the
        selected audio streams through audio index mapping.
        """
        def _undetect():
            wx.MessageBox(_('Undetected volume values! Click the '
                            '"Volume detect" button to analyze '
                            'audio volume data.'),
                          'Videomass', wx.ICON_INFORMATION, self
                          )

        # fileget = self.parent.file_selection()
        if not fileget or not self.get_audio_stream(fileget):
            return None

        if self.cmb_A_inMap.GetValue() == 'Auto':
            idx = ''
        else:
            idx = f'-ast a:{str(int(self.cmb_A_inMap.GetValue()) - 1)}'

        if self.rdbx_normalize.GetSelection() == 0:
            afilter = ''

        elif self.rdbx_normalize.GetSelection() == 1:
            if self.btn_voldect.IsEnabled():
                return _undetect()
            afilter = f'-af {self.opt["PEAK"][fileget[1]][5].split()[1]}'

        elif self.rdbx_normalize.GetSelection() == 2:
            if self.btn_voldect.IsEnabled():
                return _undetect()
            afilter = f'-af {self.opt["RMS"][fileget[1]][5].split()[1]}'

        elif self.rdbx_normalize.GetSelection() in (3, 4):
            afilter = (f'-af loudnorm=I={str(self.spin_i.GetValue())}'
                       f':LRA={str(self.spin_lra.GetValue())}'
                       f':TP={str(self.spin_tp.GetValue())}')
        else:
            return None

        self.build_playfile_command(afilter,
                                    idx,
                                    self.maindata.file_src[fileget[1]]
                                    )
        return None
    # ------------------------------------------------------------------#

    def build_playfile_command(self, afilter, index, filepath):
        """
        Build ffplay command for playback
        """
        autoexit = '-autoexit' if self.maindata.autoexit else ''

        if self.maindata.checktimestamp:
            args = (f'-showmode waves {autoexit} -i "{filepath}" '
                    f'{self.maindata.time_seq} '
                    f'-vf "{self.maindata.cmdtimestamp}" {afilter} {index}')
        else:
            args = (f'-showmode waves {autoexit} -i "{filepath}" '
                    f'{self.maindata.time_seq} '
                    f'{afilter} {index}')
        try:
            with open(filepath, encoding='utf-8'):
                FilePlay(args)
        except IOError:
            wx.MessageBox(_("Invalid or unsupported file:  %s") % (filepath),
                          "Videomass", wx.ICON_EXCLAMATION, self)
    # ------------------------------------------------------------------#

    def get_audio_stream(self, fileselected):
        """
        Given a selected media file (object of type `file_selection()`),
        it evaluates whether it contains any audio streams and any
        indexes based on selected index (audio map).
        If no audio streams or no audio index it Returns None,
        True otherwise.
        See `on_audio_preview()` method for usage.

        """
        selected = self.maindata.data_files[fileselected[1]].get('streams')
        isaudio = [a for a in selected if 'audio' in a.get('codec_type')]
        idx = self.cmb_A_inMap.GetValue()

        if isaudio:
            if idx.isdigit():  # not Auto
                if not len(isaudio) - 1 == int(idx) - 1:
                    wx.MessageBox(_('Selected index does not exist or '
                                    'does not contain any audio streams'),
                                  'Videomass', wx.ICON_INFORMATION, self)
                    return None
        else:
            wx.MessageBox(_('ERROR: Missing audio stream:\n"{}"'
                            ).format(fileselected[0]),
                          _('Videomass - Error!'), wx.ICON_ERROR, self)
            return None

        return True
    # ------------------------------------------------------------------#

    def set_audio_radiobox(self, event):
        """
        Container combobox sets compatible audio codecs
        for the selected format. See AV_FORMATS dict

        """
        if self.opt["Media"] == 'Video':
            if not self.opt["OutputFormat"]:  # Copy, enable all audio enc
                for n in range(self.rdb_a.GetCount()):
                    self.rdb_a.EnableItem(n, enable=True)
            else:
                for n, v in enumerate(AudioEncoders.AV_FORMATS[
                        self.opt["OutputFormat"]]):
                    if v:
                        self.rdb_a.EnableItem(n, enable=True)
                    else:
                        self.rdb_a.EnableItem(n, enable=False)
            self.rdb_a.SetSelection(0)

        if self.opt["Media"] == 'Audio':
            for n, v in enumerate(AudioEncoders.AV_FORMATS[
                    self.opt["OutputFormat"]]):
                if v:
                    self.rdb_a.EnableItem(n, enable=True)
                    # self.rdb_a.SetSelection(n)
                else:
                    self.rdb_a.EnableItem(n, enable=False)
            for x in range(self.rdb_a.GetCount()):
                if self.rdb_a.IsItemEnabled(x):
                    self.rdb_a.SetSelection(x)
                    break
            self.on_getting_acodec(self)
    # ------------------------------------------------------------------#

    def on_getting_acodec(self, event):
        """
        choosing an item on audio radiobox list, sets the
        audio format name and the appropriate command arg,
        (see ACODECS dict), resets the audio normalize and
        some `self.opt` keys.
        """
        audiocodec = self.rdb_a.GetStringSelection()

        def _param(enablenormalization, enablebuttonparameters):
            self.opt["AudioBitrate"] = ["", ""]
            self.opt["AudioChannel"] = ["", ""]
            self.opt["AudioRate"] = ["", ""]
            self.opt["AudioDepth"] = ["", ""]

            if enablenormalization:
                self.rdbx_normalize.Enable()
            else:
                self.rdbx_normalize.Disable()
            if enablebuttonparameters:
                self.btn_set.Enable()
                self.btn_set.SetBackgroundColour(wx.NullColour)
            else:
                self.btn_set.Disable()
                self.btn_set.SetBackgroundColour(wx.NullColour)

        # --------------------------------------------------------
        for k, v in AudioEncoders.ACODECS.items():
            if audiocodec in k:
                if audiocodec == "Auto":
                    self.audio_default()
                    self.rdbx_normalize.Enable()
                    self.opt["AudioCodec"] = ["", ""]

                elif audiocodec == "Copy":
                    self.rdbx_normalize.SetSelection(0)
                    self.on_normalize(self)
                    _param(False, False)
                    amap = f'-c:a:{self.opt["AudioMap"][1]}'
                    self.opt["AudioCodec"] = [amap, v]

                elif audiocodec == "No Audio":
                    self.rdbx_normalize.SetSelection(0)
                    self.on_normalize(self)
                    self.opt["AudioCodec"] = ["", v]
                    _param(False, False)
                    # break
                else:
                    _param(True, True)
                    amap = f'-c:a:{self.opt["AudioMap"][1]}'
                    self.opt["AudioCodec"] = [amap, v]

                self.opt["AudioCodStr"] = audiocodec

        if audiocodec == 'No Audio':  # audio Mapping disable
            self.cmb_A_inMap.Disable()
            self.cmb_A_outMap.Disable()
            self.opt["AudioMap"] = ["", ""]
            self.opt["AudioIndex"] = ""
        else:
            self.cmb_A_inMap.Enable()
            self.on_audio_index(self)
    # -------------------------------------------------------------------#

    def on_setting_acodec(self, event):
        """
        Event by Audio options button. Set audio codec string and audio
        command string and pass it to audio_dialogs method.
        """
        pcm = ["pcm_s16le", "pcm_s24le", "pcm_s32le"]

        if self.opt["AudioCodec"][1] in pcm:
            self.audio_dialog(self.opt["AudioCodStr"],
                              f'{self.opt["AudioCodStr"]} Audio Settings')
        else:
            self.audio_dialog(self.opt["AudioCodStr"],
                              f'{self.opt["AudioCodStr"]} Audio Settings')
    # -------------------------------------------------------------------#

    def audio_dialog(self, codecname, caption):
        """
        Given an audio codec specified by `codecname`,
        show a dialog for setting audio parameters
        related to the codec.
        """
        with AudioProperties(self,
                             codecname,
                             caption,
                             self.opt["AudioRate"],
                             self.opt["AudioDepth"],
                             self.opt["AudioBitrate"],
                             self.opt["AudioChannel"],
                             ) as properties:
            if properties.ShowModal() == wx.ID_OK:
                aparam = properties.getvalue()
            else:
                return

        self.opt["AudioChannel"] = aparam[0]
        self.opt["AudioRate"] = aparam[1]
        self.opt["AudioBitrate"] = aparam[2]
        if codecname == 'PCM':  # wav, aiff, etc
            amap = f'-c:a:{self.opt["AudioMap"][1]}'
            if 'Auto' in aparam[3][0]:  # [3] bit depth tuple
                self.opt["AudioCodec"] = [amap, "pcm_s16le"]
            else:
                self.opt["AudioCodec"] = [amap, aparam[3][1]]
            self.opt["AudioDepth"] = (f"{aparam[3][0]}", '')  # none
        else:  # all, except PCM
            self.opt["AudioDepth"] = aparam[3]

        count = 0
        for descr in (self.opt["AudioRate"],
                      aparam[3],
                      self.opt["AudioBitrate"],
                      self.opt["AudioChannel"],
                      ):
            if descr[1]:
                count += 1

        if count == 0:
            self.btn_set.SetBackgroundColour(wx.NullColour)
        else:
            self.btn_set.SetBackgroundColour(wx.Colour(AudioEncoders.VIOLET))
        return
    # ------------------------------------------------------------------#

    def on_audio_index(self, event):
        """
        Set a specific index from audio streams.
        See: <http://ffmpeg.org/ffmpeg.html#Advanced-options>
        """
        if self.cmb_A_inMap.GetValue() == 'Auto':
            self.cmb_A_outMap.Disable()
            self.opt["AudioIndex"] = ''
        else:
            self.cmb_A_outMap.Enable()
            idx = str(int(self.cmb_A_inMap.GetValue()) - 1)
            self.opt["AudioIndex"] = f'-map 0:a:{idx}'

        if self.rdbx_normalize.GetSelection() in [1, 2]:
            if not self.btn_voldect.IsEnabled():
                self.btn_voldect.Enable()

        self.on_audio_mapping(None)
    # ------------------------------------------------------------------#

    def on_audio_mapping(self, event):
        """
        Set the mapping of the audio streams.
        """
        index = self.cmb_A_inMap.GetValue()
        sel = self.cmb_A_outMap.GetValue()
        idx = '' if index == 'Auto' else str(int(index) - 1)

        if sel == 'Auto':
            if self.opt["Media"] == 'Video':
                self.opt["AudioMap"] = ['-map 0:a:?', idx]

            elif self.opt["Media"] == 'Audio':
                self.opt["AudioMap"] = [f'-map 0:a:{idx}?', '']

        elif sel == 'All':
            self.opt["AudioMap"] = ['-map 0:a:?', '']

        elif sel == 'Index only':
            self.opt["AudioMap"] = [f'-map 0:a:{idx}?', '']

        if self.opt["AudioCodec"][0]:
            self.opt["AudioCodec"][0] = f"-c:a:{self.opt['AudioMap'][1]}"
    # ------------------------------------------------------------------#

    def on_normalize(self, event):
        """
        Enable or disable functionality for volume normalization.
        """
        msg_1 = (_('PEAK level normalization, which will produce '
                   'a maximum peak level equal to the set target level.'
                   ))
        msg_2 = (_('RMS-based normalization, which according to '
                   'mean volume calculates the amount of gain to reach same '
                   'average power signal.'
                   ))
        msg_3 = (_('Loudnorm normalization. Normalizes '
                   'the perceived loudness using the \"loudnorm\" filter, '
                   'which implements the EBU R128 algorithm.\n'
                   'Ideal for live normalization. It produces worse results '
                   'than the High-quality two-pass Loudnorm normalization, '
                   'but is faster.'
                   ))
        msg_4 = (_('High-quality two-pass Loudnorm normalization. '
                   'Normalizes the perceived loudness using the '
                   '\"loudnorm\" filter, which implements\nthe EBU R128 '
                   'algorithm. Ideal for postprocessing.'
                   ))
        if self.rdbx_normalize.GetSelection() == 0:
            self.normalize_default('all')
            self.lab_help_norm.SetLabel(''), self.lab_help_ebu.SetLabel('')

        if self.rdbx_normalize.GetSelection() == 1:  # is checked
            self.normalize_default('peak')
            self.lab_help_norm.SetLabel(msg_1), self.lab_help_ebu.SetLabel('')

        elif self.rdbx_normalize.GetSelection() == 2:
            self.normalize_default('rms')
            self.lab_help_norm.SetLabel(msg_2), self.lab_help_ebu.SetLabel('')

        elif self.rdbx_normalize.GetSelection() == 3:
            self.lab_help_ebu.SetLabel(msg_3), self.lab_help_norm.SetLabel('')
            self.normalize_default('ebu')

        elif self.rdbx_normalize.GetSelection() == 4:
            self.lab_help_ebu.SetLabel(msg_4), self.lab_help_norm.SetLabel('')
            self.normalize_default('ebu')
        self.Layout()
    # ------------------------------------------------------------------#

    def on_enter_gain(self, event):
        """
        when spin_amplitude is changed enable 'Volumedetect' to
        update new incomming

        """
        if not self.btn_voldect.IsEnabled():
            self.btn_voldect.Enable()
    # ------------------------------------------------------------------#

    def on_analyzes(self, event):
        """
        Clicking on the "Detect Volume" button performs the
        PEAK/RMS-based volume detection and analysis process
        required to calculate the offset for audio volume
        normalization in dBFS:
            - PEAK-based Analyzes, get the MAXIMUM peak level data.
            - RMS-based Analyzes, get the MEAN peak level data.
        <https://superuser.com/questions/323119/how-can-i-normalize-audio-
        using-ffmpeg?utm_medium=organic>
        """
        if not self.maindata.data_files:
            wx.MessageBox(_("You need to import at least one file"),
                          'Videomass', wx.ICON_INFORMATION, self)
            return

        data = volume_detect_process(self.maindata.file_src,
                                     self.maindata.time_seq,  # from -ss to -t
                                     self.opt["AudioIndex"],
                                     parent=self.GetParent(),
                                     )
        if data[1]:
            if data[1][0] == 'ERROR':
                caption, ico = _('Videomass - Error!'), wx.ICON_ERROR
            elif data[1][0] == 'INFO':
                caption, ico = 'Videomass', wx.ICON_INFORMATION
            wx.MessageBox(f"{data[1][1]}", caption, ico, self)
            return

        if self.rdbx_normalize.GetSelection() == 1:  # PEAK
            target = "PEAK"
        elif self.rdbx_normalize.GetSelection() == 2:  # RMS
            target = "RMS"
        else:
            return

        del self.opt["PEAK"][:]
        del self.opt["RMS"][:]

        gain = self.spin_target.GetValue()
        for filename, vol in zip(self.maindata.file_src, data[0]):
            dataref = get_volume_data(filename,
                                      vol,
                                      gain=gain,
                                      target=target,
                                      audiomap=self.opt["AudioMap"][1],
                                      )
            self.opt[target].append(dataref)

        self.btn_voldect.Disable()
        self.btn_stat.Enable()
    # ------------------------------------------------------------------#

    def on_show_vol_statistics(self, event):
        """
        Show a wx.ListCtrl dialog with volumedetect data
        """
        if self.maindata.audivolnormalize:
            self.maindata.audivolnormalize.Raise()
            return

        if self.rdbx_normalize.GetSelection() == 1:  # PEAK
            title = _('PEAK-based volume statistics')
        elif self.rdbx_normalize.GetSelection() == 2:  # RMS
            title = _('RMS-based volume statistics')
        else:
            return

        if self.btn_voldect.IsEnabled():
            self.on_analyzes(self)

        lev = self.opt["RMS"] if not self.opt["PEAK"] else self.opt["PEAK"]
        self.maindata.audivolnormalize = AudioVolNormal(title,
                                                        lev,
                                                        self.appdata['ostype'],
                                                        )
        self.maindata.audivolnormalize.Show()
    # ------------------------------------------------------------------#
