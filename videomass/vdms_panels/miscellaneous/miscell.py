# -*- coding: UTF-8 -*-
"""
FileName: miscell.py
Porpose: Contains various functionalities for A/V Conversions
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.13.2024
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
        self.labinfo = wx.StaticText(self, wx.ID_ANY, label="",
                                     style=wx.ALIGN_CENTRE_HORIZONTAL)
        sizerbase.Add(self.labinfo, 0, wx.EXPAND | wx.ALL, 2)
        if self.appdata['ostype'] == 'Darwin':
            self.labinfo.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        else:
            self.labinfo.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        sizerbase.Add((0, 15), 0)
        gridsub = wx.BoxSizer(wx.HORIZONTAL)
        sizerbase.Add(gridsub, 0, wx.ALL | wx.CENTRE, 5)

        msg = _('Subtitle Mapping')
        txtSubmap = wx.StaticText(self, wx.ID_ANY, (msg))
        gridsub.Add(txtSubmap, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_Submap = wx.ComboBox(self, wx.ID_ANY,
                                      choices=[('None'),
                                               ('All'),
                                               ],
                                      size=(120, -1), style=wx.CB_DROPDOWN
                                      | wx.CB_READONLY,
                                      )
        gridsub.Add(self.cmb_Submap, 0, wx.ALL, 5)

        boxmetad = wx.BoxSizer(wx.HORIZONTAL)
        sizerbase.Add(boxmetad, 0, wx.ALL | wx.CENTRE, 5)
        self.ckbx_chap = wx.CheckBox(self, wx.ID_ANY, (_('Copy Chapters')))
        boxmetad.Add(self.ckbx_chap, 0, wx.LEFT, 5)
        msg = _('Copy Metadata')
        self.ckbx_metad = wx.CheckBox(self, wx.ID_ANY, (msg))
        boxmetad.Add(self.ckbx_metad, 0, wx.LEFT, 20)

        self.SetSizerAndFit(sizerbase)

        tip = (_('Select "All" to include any source file subtitles in the '
                 'output video.\n\nSelect "None" to exclude any subtitles '
                 'stream in the output video.\n\nThis option is '
                 'automatically ignored for output audio files.'))
        self.cmb_Submap.SetToolTip(tip)
        tip = (_('Copy the chapter markers as is from source file. This '
                 'option is automatically ignored for output audio files.'))
        self.ckbx_chap.SetToolTip(tip)
        tip = (_('Copy all incoming metadata from source file, such as '
                 'audio/video tags, titles, unique marks, and so on.'))
        self.ckbx_metad.SetToolTip(tip)

        self.Bind(wx.EVT_CHECKBOX, self.on_chapters, self.ckbx_chap)
        self.Bind(wx.EVT_COMBOBOX, self.on_subtitles, self.cmb_Submap)
        self.Bind(wx.EVT_CHECKBOX, self.on_metadata, self.ckbx_metad)

        self.default()

    def default(self):
        """
        Reset all controls to default
        """

        msg = _("Additional options")
        self.labinfo.SetLabel(msg)

        self.cmb_Submap.SetSelection(1), self.on_subtitles(None)
        self.ckbx_chap.SetValue(True), self.on_chapters(None)
        self.ckbx_metad.SetValue(True), self.on_metadata(None)
    # ------------------------------------------------------------------#

    def on_subtitles(self, event):
        """
        Event on combobox list for subtitles
        """
        smap = self.cmb_Submap.GetValue()
        if smap == 'None':
            self.opt["SubtitleMap"] = '-sn'
        elif smap == 'All':
            self.opt["SubtitleMap"] = '-map 0:s?'
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
