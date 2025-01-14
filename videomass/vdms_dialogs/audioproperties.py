# -*- coding: UTF-8 -*-
"""
Name: audioproperties.py
Porpose: A dialog interface for audio parameter settings
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.03.2024
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


class AudioProperties(wx.Dialog):
    """
    Provides a dialog for settings audio codec parameters
    which includes bit-rate, sample-rate, audio-channels
    and bit-per-sample (bit depth).

    See ``av_conversions.py`` -> ``audio_dialog`` method for
    how to use this class.
    """
    def __init__(self, parent, *args):
        """
        The given 'codecname' parameter represents the
        audio codec string, which will passed to the
        instance `audiodata`. This class has the same
        attributes as the AudioParameters class but
        here they are assigned by reference with the
        instance-object.

        """
        audiodata = AudioParameters(args[0])  # get audio params
        self.sample_rate = audiodata.sample_rate
        self.channels = audiodata.channels
        self.bitrate = audiodata.bitrate
        self.bitdepth = audiodata.bitdepth

        wx.Dialog.__init__(self, parent, -1, title=args[1],
                           style=wx.DEFAULT_DIALOG_STYLE
                           )
        sizerbase = wx.BoxSizer(wx.VERTICAL)
        boxctrls = wx.BoxSizer(wx.HORIZONTAL)
        sizerbase.Add(boxctrls, 0, wx.ALL | wx.CENTRE, 0)

        bitrate_list = [a[0] for a in self.bitrate.values()]
        self.rdb_bitrate = wx.RadioBox(self, wx.ID_ANY,
                                       ("Compression level"),
                                       choices=bitrate_list,
                                       majorDimension=0,
                                       style=wx.RA_SPECIFY_ROWS,
                                       )
        boxctrls.Add(self.rdb_bitrate, 0, wx.ALL, 5)

        channel_list = [a[0] for a in self.channels.values()]
        self.rdb_channels = wx.RadioBox(self, wx.ID_ANY,
                                        ("Channels"),
                                        choices=channel_list,
                                        majorDimension=0,
                                        style=wx.RA_SPECIFY_ROWS,
                                        )
        boxctrls.Add(self.rdb_channels, 0, wx.ALL, 5)

        samplerate_list = [a[0] for a in self.sample_rate.values()]
        self.rdb_sample_r = wx.RadioBox(self, wx.ID_ANY,
                                        ("Sample rate"),
                                        choices=samplerate_list,
                                        majorDimension=0,
                                        style=wx.RA_SPECIFY_ROWS,
                                        )
        boxctrls.Add(self.rdb_sample_r, 0, wx.ALL, 5)

        bitdepth_list = [a[0] for a in self.bitdepth.values()]
        self.rdb_bitdepth = wx.RadioBox(self, wx.ID_ANY,
                                        ("Bit per Sample (bit depth)"),
                                        choices=bitdepth_list,
                                        majorDimension=0,
                                        style=wx.RA_SPECIFY_ROWS,
                                        )
        boxctrls.Add(self.rdb_bitdepth, 0, wx.ALL, 5)

        # ---------------------- Bottom buttons ----------------------
        grid_btn = wx.GridSizer(1, 2, 0, 0)
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_reset = wx.Button(self, wx.ID_CLEAR, "")
        grid_btn.Add(btn_reset, 0, wx.ALL, 5)
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "")
        gridexit.Add(btn_cancel, 0)
        btn_ok = wx.Button(self, wx.ID_OK)
        gridexit.Add(btn_ok, 0, wx.LEFT, 5)
        grid_btn.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 5)
        sizerbase.Add(grid_btn, 0, wx.EXPAND)
        # ---------------------- main layout ----------------------
        self.SetSizer(sizerbase)
        sizerbase.Fit(self)
        self.Layout()

        # ----------------------Properties----------------------
        if self.rdb_bitrate.GetStringSelection() == 'Not applicable ':
            self.rdb_bitrate.Hide()

        if self.rdb_bitdepth.GetStringSelection() == 'Not applicable ':
            self.rdb_bitdepth.Hide()

        if self.rdb_sample_r.GetStringSelection() == 'Not applicable ':
            self.rdb_sample_r.Hide()

        self.rdb_bitrate.SetToolTip(audiodata.BITRATE_TOOLTIP)
        self.rdb_channels.SetToolTip(audiodata.CHANNEL_TOOLTIP)
        self.rdb_sample_r.SetToolTip(audiodata.SAMPLE_RATE_TOOLTIP)
        self.rdb_bitdepth.SetToolTip(audiodata.BITDEPTH_TOOLTIP)

        # Set previusly settings:
        arate, adepth, abitrate, achannel = args[2], args[3], args[4], args[5]
        if arate[0]:
            self.rdb_sample_r.SetSelection(samplerate_list.index(arate[0]))
        else:
            self.rdb_sample_r.SetSelection(0)
        if adepth[0]:
            self.rdb_bitdepth.SetSelection(bitdepth_list.index(adepth[0]))
        else:
            self.rdb_bitdepth.SetSelection(0)
        if abitrate[0]:
            self.rdb_bitrate.SetSelection(bitrate_list.index(abitrate[0]))
        else:
            self.rdb_bitrate.SetSelection(0)
        if achannel[0]:
            self.rdb_channels.SetSelection(channel_list.index(achannel[0]))
        else:
            self.rdb_channels.SetSelection(0)

        # --------------------Binders (EVT)----------------------
        self.Bind(wx.EVT_BUTTON, self.on_cancel, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_apply, btn_ok)
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
        This method return values via the getvalue() interface
        from the caller. See the caller for more info and usage.

        Returns:
            A four items tuple with audio parameters:
                channel(str(description), str(ffmpeg flags))
                sample_rate(str(description), str(ffmpeg flags))
                bitrate(str(description), str(ffmpeg flags))
                bitdepth(str(description), str(ffmpeg flags))
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
# ----------------------------------------------------------------------#


class AudioParameters():
    """
    It provides an adequate representation of the adjustment
    parameters related to some audio codecs as bitrate, sample
    rate, channels and bit depth based on FFmpeg syntax.
    For a list of supported audio codecs, see the
    __init__ method docstring.

    USAGE:
        >>> adata = AudioParameters(str(codec))
        >>> if not adata.unsupported:
        >>>    sample_rate = adata.sample_rate
        >>>    channels = adata.channels
        >>>    bitrate = adata.bitrate
        >>>    bitdepth = adata.bitdepth
    EXAMPLES:
        >>>    descriptions = [a[0] for a in adata.sample_rate.values()]
        >>>    ffmpeg_flags = [a[1] for a in adata.sample_rate.values()]

    """
    CHANNEL_TOOLTIP = (_('Videomass supports mono and stereo audio channels. '
                         'If you are not sure set to "Auto" and source values '
                         'will be copied.'
                         ))
    SAMPLE_RATE_TOOLTIP = (_('The audio Rate (or sample-rate) is the sound '
                             'sampling frequency and is measured in Hertz. '
                             'The higher the frequency, the more true it '
                             'will be to the sound source and the more the '
                             'file will increase in size. For audio CD '
                             'playback, set a sampling frequency of 44100 '
                             'kHz. If you are not sure, set to "Auto" and '
                             'source values will be copied.'
                             ))
    BITRATE_TOOLTIP = (_('The audio bitrate affects the file compression and '
                         'thus the quality of listening. The higher the '
                         'value, the higher the quality.'
                         ))
    BITDEPTH_TOOLTIP = (_('Bit depth is the number of bits of information in '
                          'each sample, and it directly corresponds to the '
                          'resolution of each sample. Bit depth is only '
                          'meaningful in reference to a PCM digital signal. '
                          'Non-PCM formats, such as lossy compression '
                          'formats, do not have associated bit depths.'
                          ))
    SAMPLE_RATE = {0: ("Auto", ""),
                   1: ("44100 Hz ", "-ar 44100"),
                   2: ("48000 Hz ", "-ar 48000"),
                   3: ("88200 Hz ", "-ar 88200"),
                   4: ("96000 Hz ", "-ar 96000"),
                   5: ("192000 Hz ", "-ar 192000"),
                   }
    # ----------------------------------------------------------------#

    def __init__(self, acodecname: str):
        """
        Expects a type string object representing the audio
        codec name. The following audio codec are supported:

        'PCM', 'FLAC', 'ALAC', 'AAC', 'AC3', 'VORBIS', 'LAME', 'OPUS

        If any of the audio codecs described above are passed,
        this class sets all instance attributes with appropriate
        class method.
        """
        self.sample_rate = {0: ('Not applicable ', "")}
        self.channels = {0: ('Not applicable ', "")}
        self.bitrate = {0: ('Not applicable ', "")}
        self.bitdepth = {0: ('Not applicable ', "")}
        self.unsupported = None

        if acodecname in ('PCM', 'wav', 'aiff'):
            self.pcm()
        elif acodecname in ('FLAC', 'flac'):
            self.flac()
        elif acodecname in ('ALAC', 'alac', 'm4a'):
            self.alac()
        elif acodecname in ('AAC', 'aac'):
            self.aac()
        elif acodecname in ('AC3', 'ac3'):
            self.ac3()
        elif acodecname in ('VORBIS', 'ogg', 'oga'):
            self.vorbis()
        elif acodecname in ('LAME', 'mp3'):
            self.lame()
        elif acodecname in ('OPUS', 'opus'):
            self.opus()
        else:
            self.unsupported = f'Unsupported codec: {acodecname}'
    # -----------------------------------------------------------------#

    def pcm(self):
        """
        Set the PCM codec parameters
        """
        self.sample_rate = AudioParameters.SAMPLE_RATE
        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2"),
                         }
        self.bitdepth = {0: ("Auto", ""),
                         1: ("16 bit", "pcm_s16le"),
                         2: ("24 bit", "pcm_s24le"),
                         4: ("32 bit", "pcm_s32le"),
                         }
    # -----------------------------------------------------------------#

    def flac(self):
        """
        Set the FLAC codec parameters
        """
        self.sample_rate = AudioParameters.SAMPLE_RATE
        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2"),
                         }
        self.bitrate = {0: ("Auto", ""),
                        1: ("very high quality", "-compression_level 0"),
                        2: ("quality 1", "-compression_level 1"),
                        3: ("quality 2", "-compression_level 2"),
                        4: ("quality 3", "-compression_level 3"),
                        5: ("quality 4", "-compression_level 4"),
                        6: ("Default quality", "-compression_level 5"),
                        7: ("quality 6", "-compression_level 6"),
                        8: ("quality 7", "-compression_level 7"),
                        9: ("low quality", "-compression_level 8"),
                        }
    # -----------------------------------------------------------------#

    def alac(self):
        """
        Set the ALAC codec parameters
        """
        self.sample_rate = AudioParameters.SAMPLE_RATE
        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2"),
                         }
    # -----------------------------------------------------------------#

    def opus(self):
        """
        Set the OPUS codec parameters
        """
        # self.sample_rate
        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2"),
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
                             "-compression_level 10"),
                        }
    # -----------------------------------------------------------------#

    def aac(self):
        """
        Set the AAC codec parameters
        """
        self.sample_rate = AudioParameters.SAMPLE_RATE
        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2"),
                         3: ("MultiChannel 5.1", "-ac 6"),
                         }
        self.bitrate = {0: ("Auto", ""),
                        1: ("low quality", "-b:a 128k"),
                        2: ("medium/low quality", "-b:a 160k"),
                        3: ("medium quality", "-b:a 192k"),
                        4: ("good quality", "-b:a 260k"),
                        5: ("very good quality", "-b:a 320k"),
                        }
    # -----------------------------------------------------------------#

    def ac3(self):
        """
        Set the AC3 codec parameters
        """
        self.sample_rate = AudioParameters.SAMPLE_RATE
        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2"),
                         3: ("MultiChannel 5.1", "-ac 6"),
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
                        9: ("very good quality", "-b:a 640k"),
                        }
    # -----------------------------------------------------------------#

    def vorbis(self):
        """
        Set the VORBIS codec parameters
        """
        self.sample_rate = AudioParameters.SAMPLE_RATE
        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2"),
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
                        10: ("very good quality", "-aq 10"),
                        }
    # -----------------------------------------------------------------#

    def lame(self):
        """
        Set the LAME codec parameters
        """
        self.sample_rate = AudioParameters.SAMPLE_RATE
        self.channels = {0: ("Auto", ""),
                         1: ("Mono", "-ac 1"),
                         2: ("Stereo", "-ac 2"),
                         }
        self.bitrate = {0: ("Auto", ""),
                        1: ("VBR 128 kbit/s (low quality)", "-b:a 128k"),
                        2: ("VBR 160 kbit/s", "-b:a 160k"),
                        3: ("VBR 192 kbit/s", "-b:a 192k"),
                        4: ("VBR 260 kbit/s", "-b:a 260k"),
                        5: ("CBR 320 kbit/s (very good quality)", "-b:a 320k"),
                        }
