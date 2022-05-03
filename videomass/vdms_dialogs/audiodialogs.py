# -*- coding: UTF-8 -*-
"""
Name: audiodialogs.py
Porpose: Audio dialog for settings audio parameters
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.14.2022
Code checker:
    flake8: --ignore F821, W504
    pylint: --ignore E0602, E1101

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


class AudioSettings(wx.Dialog):
    """
    Provides a dialog for settings audio codec parameters
    which includes bit-rate, sample-rate, audio-channels
    and bit-per-sample (bit depth).

    See ``av_conversions.py`` -> ``audio_dialog`` method for
    how to use this class.
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

        if self.bitrate is None:
            self.bitrate = {0: ('not applicable ', "")}

        if self.bitdepth is None:
            self.bitdepth = {0: ('not applicable ', "")}

        if self.sample_rate is None:
            self.sample_rate = {0: ('not applicable ', "")}

        samplerate_list = [a[0] for a in self.sample_rate.values()]
        channel_list = [a[0] for a in self.channels.values()]
        bitrate_list = [a[0] for a in self.bitrate.values()]
        bitdepth_list = [a[0] for a in self.bitdepth.values()]

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

        self.btn_cancel = wx.Button(self, wx.ID_CANCEL, "")
        self.btn_ok = wx.Button(self, wx.ID_OK, "")
        btn_reset = wx.Button(self, wx.ID_CLEAR, "")

        # ----------------------Properties----------------------
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

        # ----------------------Build layout----------------------
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(1, 4, 0, 0)  # radiobox
        sizerBase.Add(grid_sizer_1, 0, wx.ALL, 0)
        grid_sizer_1.Add(self.rdb_bitrate, 0, wx.ALL, 5)
        grid_sizer_1.Add(self.rdb_channels, 0, wx.ALL, 5)
        grid_sizer_1.Add(self.rdb_sample_r, 0, wx.ALL, 5)
        grid_sizer_1.Add(self.rdb_bitdepth, 0, wx.ALL, 5)

        gridBtn = wx.GridSizer(1, 2, 0, 0)  # buttons
        gridhelp = wx.GridSizer(1, 1, 0, 0)  # buttons
        gridhelp.Add(btn_reset, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridBtn.Add(gridhelp)

        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        gridexit.Add(self.btn_cancel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridexit.Add(self.btn_ok, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridBtn.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)
        sizerBase.Add(gridBtn, 0, wx.EXPAND)

        self.SetSizer(sizerBase)
        sizerBase.Fit(self)
        self.Layout()

        # --------------------Binders (EVT)----------------------
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_apply, self.btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)

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
        Cancel this dialog without saving anything
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def on_apply(self, event):
        """
        Don't use self.Destroy() in this dialog
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def getvalue(self):
        """
        This method return values via the interface getvalue()
        by the caller. See the caller for more info and usage.

        Returns:
            four tuples of audio parameters object in the form:
                (str(selected parameter), str(related value)) * 3
        """
        sel_ch = self.rdb_channels.GetStringSelection()
        sel_sr = self.rdb_sample_r.GetStringSelection()
        sel_br = self.rdb_bitrate.GetStringSelection()
        sel_bd = self.rdb_bitdepth.GetStringSelection()

        return ([v for v in self.channels.values() if sel_ch in v[0]][0],
                [v for v in self.sample_rate.values() if sel_sr in v[0]][0],
                [v for v in self.bitrate.values() if sel_br in v[0]][0],
                [v for v in self.bitdepth.values() if sel_bd in v[0]][0],
                )
#######################################################################


class TypeAudioParameters():
    """
    It provides an adequate representation of the adjustment
    parameters related to some audio codecs that need to be
    encoded and decoded by FFmpeg. For a list of supported audio
    formats and codecs, see the __init__ method docstring.

    Some aspects of the audio bitrate, sample rate, audio channels
    and bit depth are specified.

    """
    channel_tooltip = (_('Videomass supports mono and stereo audio channels. '
                         'If you are not sure set to "Auto" and source values '
                         'will be copied.'
                         ))
    sample_rate_tooltip = (_('The audio Rate (or sample-rate) is the sound '
                             'sampling frequency and is measured in Hertz. '
                             'The higher the frequency, the more true it '
                             'will be to the sound source and the more the '
                             'file will increase in size. For audio CD '
                             'playback, set a sampling frequency of 44100 '
                             'kHz. If you are not sure, set to "Auto" and '
                             'source values will be copied.'
                             ))
    bitrate_tooltip = (_('The audio bitrate affects the file compression and '
                         'thus the quality of listening. The higher the '
                         'value, the higher the quality.'
                         ))
    bitdepth_tooltip = (_('Bit depth is the number of bits of information in '
                          'each sample, and it directly corresponds to the '
                          'resolution of each sample. Bit depth is only '
                          'meaningful in reference to a PCM digital signal. '
                          'Non-PCM formats, such as lossy compression '
                          'formats, do not have associated bit depths.'
                          ))
    sample_rate = {0: ("Auto", ""),
                   1: ("44100 Hz ", "-ar 44100 "),
                   2: ("48000 Hz ", "-ar 48000"),
                   3: ("88200 Hz ", "-ar 88200"),
                   4: ("96000 Hz ", "-ar 96000 "),
                   5: ("192000 Hz ", "-ar 192000 ")
                   }
    # ----------------------------------------------------------------#

    def __init__(self, audio_format):
        """
        Accept a type string object representing the name
        of the audio format or/and audio codec name. The
        following audio formats are supported:

            ('PCM', 'wav', 'aiff', 'flac', 'alac', 'aac', 'ac3',
             'vorbis', 'ogg', 'oga', 'lame', 'mp3', 'opus)

        If any of the audio formats or codecs described above are
        passed as a string argument on 'audio_format`, this class sets
        all instance attributes with appropriate class method.
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
        pcm parameter data structures for
        wav and aiff audio formats

        """
        self.sample_rate = {0: ("Auto", ""),
                            1: ("44100 Hz ", "-ar 44100 "),
                            2: ("48000 Hz ", "-ar 48000"),
                            3: ("88200 Hz ", "-ar 88200"),
                            4: ("96000 Hz ", "-ar 96000 "),
                            5: ("192000 Hz ", "-ar 192000 ")
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
        defines parameter data structures for
        flac audio format

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
        defines parameter data structures for
        alac audio format

        """
        self.sample_rate = TypeAudioParameters.sample_rate
        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2")
                         }
    # -----------------------------------------------------------------#

    def opus(self):
        """
        defines parameter data structures for
        opus audio format

        """
        # self.sample_rate
        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2")
                         }
        self.bitrate = {0: ("Auto", ""),
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
                        11: ("highest quality 10 (default)",
                             "-compression_level 10")
                        }
    # -----------------------------------------------------------------#

    def aac(self):
        """
        defines parameter data structures for
        aac audio format

        """
        self.sample_rate = TypeAudioParameters.sample_rate
        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2"),
                         3: ("MultiChannel 5.1", "-ac 6")
                         }
        self.bitrate = {0: ("Auto", ""),
                        1: ("low quality", "-b:a 128k"),
                        2: ("medium/low quality", "-b:a 160k"),
                        3: ("medium quality", "-b:a 192k"),
                        4: ("good quality", "-b:a 260k"),
                        5: ("very good quality", "-b:a 320k")
                        }
    # -----------------------------------------------------------------#

    def ac3(self):
        """
        defines parameter data structures for
        ac3 audio format

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
        vorbis parameter data structures for
        vorbis, ogg and oga audio formats.

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
        defines parameter data structures for
        mp3 audio format

        """
        self.sample_rate = TypeAudioParameters.sample_rate

        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2")
                         }
        self.bitrate = {0: ("Auto", ""),
                        1: ("VBR 128 kbit/s (low quality)", "-b:a 128k"),
                        2: ("VBR 160 kbit/s", "-b:a 160k"),
                        3: ("VBR 192 kbit/s", "-b:a 192k"),
                        4: ("VBR 260 kbit/s", "-b:a 260k"),
                        5: ("CBR 320 kbit/s (very good quality)", "-b:a 320k")
                        }
