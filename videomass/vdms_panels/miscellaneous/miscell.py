# -*- coding: UTF-8 -*-
"""
FileName: miscell.py
Porpose: Contains various functionalities for A/V Conversions
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
import wx


class Miscellaneous(wx.Panel):
    """
    This Panel implements various functionalities
    controls for A/V Conversions.
    """
    # Namings in the subtitle codec selection on subtitle radio box:
    SCODECS = {('Auto'): (""),
               ('MOV_TEXT'): ("mov_text"),
               ('SUBRIP'): ("subrip"),
               ('WEBVTT'): ("webvtt"),
               ('ASS'): ("alac"),
               ('SSA'): ("ac3"),
               ('SRT'): ("libvorbis"),
               ('Copy'): ("copy"),
               ('No Subtitles'): ("-sn")
               }
    # compatibility between video formats and related subtitle formats:
    S_FORMATS = {('avi'): ('default', None, None, None, None, None, None,
                           'copy', 'No Subtitles'),
                 ('mp4'): ('default', 'mov_text', None, None, None, None, None,
                           'copy', 'No Subtitles'),
                 ('m4v'): ('default', 'mov_text', None, None, None, None, None,
                           'copy', 'No Subtitles'),
                 ('mkv'): ('default', None, 'subrip', 'webvtt', 'ass', 'ssa',
                           'srt', 'copy', 'No Subtitles'),
                 ('webm'): ('default', None, None, 'webvtt', None, None, None,
                            'copy', 'No Subtitles'),
                 }

    def __init__(self, parent, opt):
        """
        This is a child of `nb_misc` of AV_Conv` class-panel (parent).
        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.parent = parent  # parent is the `nb_misc` here.
        self.opt = opt

        wx.Panel.__init__(self, parent, -1,
                          style=wx.TAB_TRAVERSAL
                          | wx.BORDER_NONE,
                          name="Miscellaneous panel",
                          )
        sizerbase = wx.BoxSizer(wx.VERTICAL)
        labsub = wx.StaticText(self, wx.ID_ANY, label="",
                               style=wx.ALIGN_CENTRE_HORIZONTAL)
        sizerbase.Add(labsub, 0, wx.EXPAND | wx.ALL, 2)
        if self.appdata['ostype'] == 'Darwin':
            labsub.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        else:
            labsub.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        labsub.SetLabel(_("Subtitle Properties"))
        self.rdb_s = wx.RadioBox(self, wx.ID_ANY,
                                 (_("Subtitle Encoder")), size=(-1, -1),
                                 choices=list(Miscellaneous.SCODECS.keys()),
                                 majorDimension=0, style=wx.RA_SPECIFY_COLS
                                 )
        for n, v in enumerate(Miscellaneous.S_FORMATS["mkv"]):
            if not v:  # disable only not compatible with mkv
                self.rdb_s.EnableItem(n, enable=False)
        sizerbase.Add(self.rdb_s, 0, wx.ALL | wx.CENTRE, 5)
        line1 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=(-1, -1), style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        sizerbase.Add(line1, 0, wx.ALL | wx.EXPAND, 15)
        gridsub = wx.BoxSizer(wx.HORIZONTAL)
        sizerbase.Add(gridsub, 0, wx.ALL | wx.CENTRE, 5)
        msg = _('Index Selection:')
        txtSubmap = wx.StaticText(self, wx.ID_ANY, (msg))
        gridsub.Add(txtSubmap, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.cmb_Submap = wx.ComboBox(self, wx.ID_ANY,
                                      choices=['All', '1', '2', '3',
                                               '4', '5', '6', '7', '8', '9',
                                               '10', '11', '12', '13', '14',
                                               '15', '16',],
                                      size=(120, -1), style=wx.CB_DROPDOWN
                                      | wx.CB_READONLY,
                                      )
        gridsub.Add(self.cmb_Submap, 0, wx.LEFT | wx.CENTRE, 5)
        line2 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=(-1, -1), style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        sizerbase.Add(line2, 0, wx.ALL | wx.EXPAND, 15)
        sizerbase.Add((0, 25), 0)
        labdata = wx.StaticText(self, wx.ID_ANY, label="",
                                style=wx.ALIGN_CENTRE_HORIZONTAL)
        sizerbase.Add(labdata, 0, wx.EXPAND | wx.ALL, 2)
        if self.appdata['ostype'] == 'Darwin':
            labdata.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        else:
            labdata.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        labdata.SetLabel(_("Chapters and Metadata"))
        boxmetad = wx.BoxSizer(wx.HORIZONTAL)
        sizerbase.Add(boxmetad, 0, wx.ALL | wx.CENTRE, 5)
        self.ckbx_chap = wx.CheckBox(self, wx.ID_ANY, (_('Copy Chapters')))
        boxmetad.Add(self.ckbx_chap, 0, wx.LEFT, 5)
        msg = _('Copy Metadata')
        self.ckbx_metad = wx.CheckBox(self, wx.ID_ANY, (msg))
        boxmetad.Add(self.ckbx_metad, 0, wx.LEFT, 20)
        self.SetSizerAndFit(sizerbase)
        tip = (_('Select "All" to include any possible subtitle stream in the '
                 'output video.\n\nSelect "1-16" to indexing the desired '
                 'subtitle stream and exclude all others, e.g "1" for the '
                 'first available subtitle stream, "2" for the second '
                 'subtitle stream, and so on.'))
        self.cmb_Submap.SetToolTip(tip)
        tip = (_('Copy the chapter markers as is from source file.'))
        self.ckbx_chap.SetToolTip(tip)
        tip = (_('Copy all incoming metadata from source file, such as '
                 'audio/video tags, titles, unique marks, and so on.'))
        self.ckbx_metad.SetToolTip(tip)

        self.Bind(wx.EVT_RADIOBOX, self.on_sub_enc, self.rdb_s)
        self.Bind(wx.EVT_CHECKBOX, self.on_chapters, self.ckbx_chap)
        self.Bind(wx.EVT_COMBOBOX, self.on_sub_map, self.cmb_Submap)
        self.Bind(wx.EVT_CHECKBOX, self.on_metadata, self.ckbx_metad)

        self.default()

    def default(self):
        """
        Reset all controls to default
        """
        self.cmb_Submap.SetSelection(0), self.on_sub_map(None)
        self.ckbx_chap.SetValue(True), self.on_chapters(None)
        self.ckbx_metad.SetValue(True), self.on_metadata(None)
    # ------------------------------------------------------------------#

    def set_subt_radiobox(self):
        """
        Sets compatible subtitle codec for the selected video format.
        See `S_FORMATS` dict on this class. This method is called
        changing video format (container)
        This method is called by av_conversion.py file only.
        """
        if self.opt["Media"] == 'Audio':
            self.rdb_s.Disable(), self.cmb_Submap.Disable(),
            self.ckbx_chap.Disable()
            return
        self.rdb_s.Enable(), self.cmb_Submap.Enable()
        self.ckbx_chap.Enable()

        if not self.opt["OutputFormat"]:  # in Copy, enable all audio enc
            for n in range(self.rdb_s.GetCount()):
                self.rdb_s.EnableItem(n, enable=True)
            self.cmb_Submap.Enable()
            self.cmb_Submap.SetSelection(0)
            self.rdb_s.SetSelection(0)
            self.opt["SubtitleMap"] = '-map 0:s?'
            self.opt["SubtitleEnc"] = ''
            return

        if not [k for k in Miscellaneous.S_FORMATS if
                self.opt["OutputFormat"] == k]:
            return

        for n, v in enumerate(Miscellaneous.S_FORMATS[
                self.opt["OutputFormat"]]):
            if v:
                self.rdb_s.EnableItem(n, enable=True)
            else:
                self.rdb_s.EnableItem(n, enable=False)

        if self.opt["OutputFormat"] in ('mp4', 'm4v'):
            self.cmb_Submap.SetSelection(0)
            self.cmb_Submap.Disable()
            self.opt["SubtitleMap"] = '-map 0:s?'
            self.rdb_s.SetSelection(1)
            subcodec = self.rdb_s.GetStringSelection()
            codec = Miscellaneous.SCODECS[subcodec]
            self.opt["SubtitleEnc"] = f'-c:s {codec}'

        elif self.opt["OutputFormat"] == 'avi':
            self.cmb_Submap.SetSelection(0)
            self.cmb_Submap.Disable()
            self.opt["SubtitleMap"] = ''
            self.rdb_s.SetSelection(8)
            self.opt["SubtitleEnc"] = '-sn'
        else:
            self.cmb_Submap.Enable()
            self.cmb_Submap.SetSelection(0)
            self.opt["SubtitleMap"] = '-map 0:s?'
            self.rdb_s.SetSelection(0)
            self.opt["SubtitleEnc"] = ''

        return
    # ------------------------------------------------------------------#

    def on_sub_enc(self, event):
        """
        Event on subtitle radiobox control
        """
        subcodec = self.rdb_s.GetStringSelection()
        if subcodec == 'No Subtitles':
            self.opt["SubtitleEnc"] = '-sn'
            self.opt["SubtitleMap"] = ''
            self.cmb_Submap.Disable()
            return
        if subcodec == 'MOV_TEXT':
            self.cmb_Submap.SetSelection(0)
            self.cmb_Submap.Disable()
            self.opt["SubtitleMap"] = '-map 0:s?'
            return
        if not self.cmb_Submap.IsEnabled():
            self.cmb_Submap.Enable()

        smap = self.cmb_Submap.GetValue()
        if smap.isdigit():
            idx = f':{str(int(smap) - 1)}'
        else:
            idx = ''

        if subcodec == 'Auto':
            self.opt["SubtitleEnc"] = ''
        elif subcodec == 'Copy':
            self.opt["SubtitleEnc"] = f'-c:s{idx} copy'
        else:
            codec = Miscellaneous.SCODECS[subcodec]
            self.opt["SubtitleEnc"] = f'-c:s{idx} {codec}'
    # ------------------------------------------------------------------#

    def on_sub_map(self, event):
        """
        Event on combobox list for subtitles
        """
        smap = self.cmb_Submap.GetValue()
        if smap == 'All':
            self.opt["SubtitleMap"] = '-map 0:s?'
        else:
            self.opt["SubtitleMap"] = f'-map 0:s:{str(int(smap) - 1)}'

        self.on_sub_enc(None)
    # ------------------------------------------------------------------#

    def on_chapters(self, event):
        """
        Event on enabling/disabling map chapters
        """
        val = self.ckbx_chap.GetValue()
        self.opt["Chapters"] = '-map_chapters 0' if val else '-map_chapters -1'
    # ------------------------------------------------------------------#

    def on_metadata(self, event):
        """
        Event on enabling/disabling metadata
        """
        val = self.ckbx_metad.GetValue()
        self.opt["MetaData"] = '-map_metadata 0' if val else '-map_metadata -1'
    # ------------------------------------------------------------------#
