# -*- coding: UTF-8 -*-
# Name: audiodialogs.py
# Porpose: Dialog for choice and settings audio parameters
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.06.2020 *PEP8 compatible*
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
import webbrowser


class AudioSettings(wx.Dialog):
    """
    Provides a dialog for codec audio settings which bit-rate,
    sample-rate, audio-channels and bit-per-sample (bit depth).

    """
    def __init__(self, parent, audio_type, arate,
                 adepth, abitrate, achannel, title):
        """
        The given 'audio_type' parameter represents the audio codec
        string, which will passed to the instance `data`.
        This class has the same attributes as the TypeAudioParameters class
        but here they are assigned by reference with the instance-object.

        """
        data = TypeAudioParameters(audio_type)  # instance for audio param
        # set attributes:
        self.sample_rate = data.sample_rate
        self.channels = data.channels
        self.bitrate = data.bitrate
        self.bitdepth = data.bitdepth
        samplerate_list = []
        channel_list = []
        bitrate_list = []
        bitdepth_list = []

        if self.bitrate is None:
            self.bitrate = {0: ('not applicable ', "")}

        if self.bitdepth is None:
            self.bitdepth = {0: ('not applicable ', "")}

        if self.sample_rate is None:
            self.sample_rate = {0: ('not applicable ', "")}

        for a in self.sample_rate.values():
            samplerate_list.append(a[0])

        for b in self.channels.values():
            channel_list.append(b[0])

        for c in self.bitrate.values():
            bitrate_list.append(c[0])

        for d in self.bitdepth.values():
            bitdepth_list.append(d[0])

        wx.Dialog.__init__(self, parent, -1, title=title,
                           style=wx.DEFAULT_DIALOG_STYLE
                           )
        self.rdb_bitrate = wx.RadioBox(self, wx.ID_ANY,
                                       ("Audio Bit-Rate"),
                                       choices=bitrate_list,
                                       majorDimension=0,
                                       style=wx.RA_SPECIFY_ROWS
                                       )

        self.rdb_channels = wx.RadioBox(self, wx.ID_ANY,
                                        ("Audio Channels"),
                                        choices=channel_list,
                                        majorDimension=0,
                                        style=wx.RA_SPECIFY_ROWS
                                        )
        self.rdb_sample_r = wx.RadioBox(self, wx.ID_ANY,
                                        ("Audio Rate (sample rate)"),
                                        choices=samplerate_list,
                                        majorDimension=0,
                                        style=wx.RA_SPECIFY_ROWS
                                        )
        self.rdb_bitdepth = wx.RadioBox(self, wx.ID_ANY,
                                        ("Bit per Sample (bit depth)"),
                                        choices=bitdepth_list,
                                        majorDimension=0,
                                        style=wx.RA_SPECIFY_ROWS
                                        )
        if self.rdb_bitrate.GetStringSelection() == 'not applicable ':
            self.rdb_bitrate.Disable()

        if self.rdb_bitdepth.GetStringSelection() == 'not applicable ':
            self.rdb_bitdepth.Disable()

        if self.rdb_sample_r.GetStringSelection() == 'not applicable ':
            self.rdb_sample_r.Disable()

        btn_help = wx.Button(self, wx.ID_HELP, "", size=(-1, -1))
        self.btn_cancel = wx.Button(self, wx.ID_CANCEL, "")
        self.btn_ok = wx.Button(self, wx.ID_OK, "")
        btn_reset = wx.Button(self, wx.ID_CLEAR, "")

        """----------------------Properties----------------------"""
        self.rdb_bitrate.SetSelection(0)
        self.rdb_bitrate.SetToolTip(data.bitrate_tooltip)
        self.rdb_channels.SetSelection(0)
        self.rdb_channels.SetToolTip(data.channel_tooltip)
        self.rdb_sample_r.SetSelection(0)
        self.rdb_sample_r.SetToolTip(data.sample_rate_tooltip)
        self.rdb_bitdepth.SetSelection(0)
        self.rdb_bitdepth.SetToolTip(data.bitdepth_tooltip)
        # Set previusly settings:
        if arate[0]:
            self.rdb_sample_r.SetSelection(samplerate_list.index(arate[0]))
        if adepth[0]:
            self.rdb_bitdepth.SetSelection(bitdepth_list.index(adepth[0]))
        if abitrate[0]:
            self.rdb_bitrate.SetSelection(bitrate_list.index(abitrate[0]))
        if achannel[0]:
            self.rdb_channels.SetSelection(channel_list.index(achannel[0]))

        """----------------------Build layout----------------------"""
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(1, 4, 0, 0)  # radiobox
        sizerBase.Add(grid_sizer_1, 0, wx.ALL, 0)
        grid_sizer_1.Add(self.rdb_bitrate, 0, wx.ALL, 10)
        grid_sizer_1.Add(self.rdb_channels, 0, wx.ALL, 10)
        grid_sizer_1.Add(self.rdb_sample_r, 0, wx.ALL, 10)
        grid_sizer_1.Add(self.rdb_bitdepth, 0, wx.ALL, 10)

        gridBtn = wx.GridSizer(1, 2, 0, 0)  # buttons
        gridhelp = wx.GridSizer(1, 1, 0, 0)  # buttons
        gridhelp.Add(btn_help, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridBtn.Add(gridhelp)

        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        gridexit.Add(self.btn_cancel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridexit.Add(self.btn_ok, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridexit.Add(btn_reset, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridBtn.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)
        sizerBase.Add(gridBtn, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(sizerBase)
        sizerBase.Fit(self)
        self.Layout()

        """--------------------Binders (EVT)----------------------"""
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_apply, self.btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)

    # ------------------------------------------------------------------#
    def on_help(self, event):
        """
        """
        page = ('https://jeanslack.github.io/Videomass/Pages/'
                'Audio_Parameters/Audio_parameters.html')
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def on_reset(self, event):
        """
        Reset all option and values
        """
        self.rdb_sample_r.SetSelection(0)
        self.rdb_bitdepth.SetSelection(0)
        self.rdb_bitrate.SetSelection(0)
        self.rdb_channels.SetSelection(0)
    # ------------------------------------------------------------------#

    def on_cancel(self, event):
        """
        if you enable self.Destroy(), it delete from memory all data
        event and no return correctly. It has the right behavior if
        not used here, because it is called in the main frame.

        Event.Skip(), work correctly here.

        """
        # self.Destroy()
        event.Skip()
    # ------------------------------------------------------------------#

    def on_apply(self, event):
        """
        as on_cancel for destroy.

        Event.Skip(), work correctly here. Sometimes needs to disable
        it for needs to maintain the view of the window (for exemple).

        """
        self.GetValue()
        # self.Destroy()
        event.Skip()
    # ------------------------------------------------------------------#

    def GetValue(self):
        """
        This method return values via the interface GetValue()
        """
        for k, v in self.channels.items():
            if self.rdb_channels.GetStringSelection() in v[0]:
                channel = v

        for k, v in self.sample_rate.items():
            if self.rdb_sample_r.GetStringSelection() in v[0]:
                samplerate = v

        for k, v in self.bitrate.items():
            if self.rdb_bitrate.GetStringSelection() in v[0]:
                bitrate = v

        for k, v in self.bitdepth.items():
            if self.rdb_bitdepth.GetStringSelection() in v[0]:
                bitdepth = v

        return (channel, samplerate, bitrate, bitdepth)
#######################################################################


class TypeAudioParameters(object):
    """
    The class provides an adequate representation of the different
    audio parameters that need to be encoded or decoded by FFmpeg.
    These parameters relate to some aspects of quality and technical:
    audio bitrates, sample rate, audio channels and bitdepth and also
    include messages tooltip.
    """
    channel_tooltip = (_('Support to mono or stereo audio channels. If you '
                         'are not sure set to "Auto" and source values '
                         'will be copied.'))
    sample_rate_tooltip = (_("""\
The audio Rate (or sample-rate) is the sound sampling
frequency and is measured in hertz. The higher the frequency,
plus the audio signal will be true to the sound source, but
the file will increase its size. For normal playback with
audio CD set a sample rate of 44100kHz. If you are not sure
set to "Auto" and source values will be copied.\
"""))
    bitrate_tooltip = (_("""\
The audio bitrate affects on file compression
and on the quality of listening. The higher
the value and more higher quality.\
"""))
    bitdepth_tooltip = (_("""\
bit depth is the number of bits of information in each
sample, and it directly corresponds to the resolution
of each sample. Bit depth is only meaningful in reference
to a PCM digital signal. Non-PCM formats, such as lossy
compression formats, do not have associated bit depths.\
"""))
    sample_rate = {0: ("Auto", ""),
                   1: ("44100 Hz ", "-ar 44100 "),
                   2: ("48000 Hz ", "-ar 48000"),
                   3: ("88200 Hz ", "-ar 88200"),
                   4: ("96000 Hz ", "-ar 96000 ")
                   }
    # ----------------------------------------------------------------#

    def __init__(self, audio_format):
        """
        Accept a type string object representing the name of the audio
        format or/and audio codec name. For now there is support for these
        audio formats e.g. 'PCM' or 'wav' or 'aiff'
        Each attribute is instantiable with this class and returns the
        data object for each dictionary.
        """
        self.sample_rate = None
        self.channels = None
        self.bitrate = None
        self.bitdepth = None

        if audio_format in ('PCM', 'wav', 'aiff'):
            self.pcm()
        elif audio_format in ('FLAC', 'flac'):
            self.flac()
        elif audio_format in ('ALAC', 'alac', 'm4a'):
            self.alac()
        elif audio_format in ('AAC', 'aac'):
            self.aac()
        elif audio_format in ('AC3', 'ac3'):
            self.ac3()
        elif audio_format in ('VORBIS', 'ogg', 'oga'):
            self.vorbis()
        elif audio_format in ('LAME', 'mp3'):
            self.lame()
        elif audio_format in ('OPUS', 'opus'):
            self.opus()
    # -----------------------------------------------------------------#

    def pcm(self):
        """
        NOTE: the wav and aiff bitdepth is used implicitly on the
              codec name and not as separated -sample_fmts option.

        """
        self.sample_rate = {0: ("Auto", ""),
                            1: ("44100 Hz ", "-ar 44100 "),
                            2: ("48000 Hz ", "-ar 48000"),
                            3: ("88200 Hz ", "-ar 88200"),
                            4: ("96000 Hz ", "-ar 96000 ")
                            }
        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2")
                         }
        self.bitdepth = {0: ("Auto", ""),
                         1: ("16 bit", "pcm_s16le"),
                         2: ("24 bit", "pcm_s24le"),
                         4: ("32 bit", "pcm_s32le")
                         }
    # -----------------------------------------------------------------#

    def flac(self):
        """
        """
        self.sample_rate = TypeAudioParameters.sample_rate
        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2")
                         }
        self.bitrate = {0: ("Auto", ""),
                        1: ("very high quality", "-compression_level 0"),
                        2: ("quality 1", "-compression_level 1"),
                        3: ("quality 2", "-compression_level 2"),
                        4: ("quality 3", "-compression_level 3"),
                        5: ("quality 4", "-compression_level 4"),
                        6: ("Standard quality", "-compression_level 5"),
                        7: ("quality 6", "-compression_level 6"),
                        8: ("quality 7", "-compression_level 7"),
                        9: ("low quality", "-compression_level 8")
                        }
    # -----------------------------------------------------------------#

    def alac(self):
        """
        """
        self.sample_rate = TypeAudioParameters.sample_rate
        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2")
                         }
    # -----------------------------------------------------------------#

    def opus(self):
        """
        """
        # self.sample_rate
        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2")
                         }
        self.bitrate = {
                0: ("Auto", ""),
                1: ("low quality 0", "-compression_level 0"),
                2: ("low quality 1", "-compression_level 1"),
                3: ("quality 2", "-compression_level 2"),
                4: ("quality 3", "-compression_level 3"),
                5: ("quality 4", "-compression_level 4"),
                6: ("medium quality 5", "-compression_level 5"),
                7: ("quality 6", "-compression_level 6"),
                8: ("quality 7", "-compression_level 7"),
                9: ("quality 8", "-compression_level 8"),
                10: ("high quality 9", "-compression_level 9"),
                11: ("highest quality 10 (default)", "-compression_level 10")
                        }
    # -----------------------------------------------------------------#

    def aac(self):
        """
        """
        self.sample_rate = TypeAudioParameters.sample_rate
        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2"),
                         3: ("MultiChannel 5.1", "-ac 6")
                         }
        self.bitrate = {
            0: ("Auto", ""),
            1: ("low quality", "-b:a 128k"),
            2: ("medium/low quality", "-b:a 160k"),
            3: ("medium quality", "-b:a 192k"),
            4: ("good quality", "-b:a 260k"),
            5: ("very good quality", "-b:a 320k")
            }
    # -----------------------------------------------------------------#

    def ac3(self):
        """
        """
        self.sample_rate = TypeAudioParameters.sample_rate
        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2"),
                         3: ("MultiChannel 5.1", "-ac 6")
                         }
        self.bitrate = {0: ("Auto", ""),
                        1: ("low quality", "-b:a 192k"),
                        2: ("224 kbit/s", "-b:a 224k"),
                        3: ("256 kbit/s", "-b:a 256k"),
                        4: ("320 kbit/s", "-b:a 320k"),
                        5: ("384 kbit/s", "-b:a 384k"),
                        6: ("448 kbit/s", "-b:a 448k"),
                        7: ("512 kbit/s", "-b:a 512k"),
                        8: ("576 kbit/s", "-b:a 576k"),
                        9: ("very good quality", "-b:a 640k")
                        }
    # -----------------------------------------------------------------#

    def vorbis(self):
        """
        """
        self.sample_rate = TypeAudioParameters.sample_rate

        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2")
                         }
        self.bitrate = {0: ("Auto", ""),
                        1: ("very poor quality", "-aq 1"),
                        2: ("VBR 92 kbit/s", "-aq 2"),
                        3: ("VBR 128 kbit/s", "-aq 3"),
                        4: ("VBR 160 kbit/s", "-aq 4"),
                        5: ("VBR 175 kbit/s", "-aq 5"),
                        6: ("VBR 192 kbit/s", "-aq 6"),
                        7: ("VBR 220 kbit/s", "-aq 7"),
                        8: ("VBR 260 kbit/s", "-aq 8"),
                        9: ("VBR 320 kbit/s", "-aq 9"),
                        10: ("very good quality", "-aq 10")
                        }
    # -----------------------------------------------------------------#

    def lame(self):
        """
        """
        self.sample_rate = TypeAudioParameters.sample_rate

        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2")
                         }
        self.bitrate = {
            0: ("Auto", ""),
            1: ("VBR 128 kbit/s (low quality)", "-b:a 128k"),
            2: ("VBR 160 kbit/s", "-b:a 160k"),
            3: ("VBR 192 kbit/s", "-b:a 192k"),
            4: ("VBR 260 kbit/s", "-b:a 260k"),
            5: ("CBR 320 kbit/s (very good quality)", "-b:a 320k")
                        }
