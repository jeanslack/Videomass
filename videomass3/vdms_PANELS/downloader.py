# -*- coding: UTF-8 -*-

#########################################################
# Name: downloader.py
# Porpose: sets youtube-dl options
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Nov.08.2019
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

vformats = ("All best", "mp4", "webm", "flv", "3gp", "m4a", "mkv")
vquality = {"All best": {"default": "bestvideo+bestaudio/best"},
            "mp4": {"mp4 maximum quality": "--format mp4",
                    "mp4 [360p] (3D)": "--format 82",
                    "mp4 [480p] (3D)": "--format 83",
                    "mp4 [720p] (3D)": "-format 84",
                    "mp4 [1080p] (3D)": "--format 85",
                    "mp4 [360p]": "--format 18",
                    "mp4 [720p]": "--format 22",
                    "mp4 [1080p]": "--format 37",
                    "mp4 [4K]": "--format 38",
                    "mp4 [144p] (DASH Video)": "--format 160",
                    "mp4 [240p] (DASH Video)": "--format 133",
                    "mp4 [360p] (DASH Video)": "--format 134",
                    "mp4 [480p] (DASH Video)": "--format 135",
                    "mp4 [720p] (DASH Video)": "--format136",
                    "mp4 [1080p] (DASH Video)": "--format 137",
                    "mp4 [1440p] (DASH Video)": "--format 264",
                    "mp4 [2160p] (DASH Video)": "--format 138"},
            "webm": {"webm maximum quality": "--format webm",
                    "webm [360p]": "--format 43",
                    "webm [480p]": "--format 44",
                    "webm [720p]": "--format 45",
                    "webm [1080p]": "--format 46",
                    "webm [240p] DASH Video": "--format 242",
                    "webm [360p] DASH Video": "--format 243",
                    "webm [480p] DASH Video": "--format 244",
                    "webm [720p] DASH Video": "--format 247",
                    "webm [1080p] DASH Video": "--format 248",
                    "webm [1440p] DASH Video": "--format 271",
                    "webm [2160p] DASH Video": "--format 272",
                    "webm [360p] 3D": "--format 100",
                    "webm [480p] 3D": "--format 101",
                    "webm [720p] 3D": "--format 102",
                    "webm 48k DASH Audio": "--format 171",
                    "webm 256k DASH Audio": "--format 172"},
            "flv": {"flv maximum quality": "--format flv",
                    "flv [240p]": "--format 5",
                    "flv [360p]": "--format 34",
                    "flv [480p]": "--format 35"},
            "3gp": {"3gp maximum quality": "--format 3gp",
                    "3gp [144p]": "--format 17",
                    "3gp [240p]": "--format 36"},
            "m4a": {"m4a maximum quality": "--format m4a",
                    "m4a 48k DASH Audio": "--format 139",
                    "m4a 128k DASH Audio": "--format 140",
                    "m4a 256k DASH Audio": "--format 141"},
            "mkv": {"mkv maximum quality": "--format mkv",}
                }

aformats = {("Best audio)"): ("--extract-audio --audio-format best"),
            ("wav"): ("--extract-audio --audio-format wav"),
            ("mp3"): ("--extract-audio --audio-format mp3"),
            ("aac"): ("--extract-audio --audio-format aac"),
            ("m4a"): ("--extract-audio --audio-format m4a"),
            ("vorbis"): ("--extract-audio --audio-format vorbis"),
            ("opus"): ("--extract-audio --audio-format opus"),
            ("flac"): ("--extract-audio --audio-format flac"),
            }

aquality = {("Maximum quality"): ("--audio-quality 0"),
            ("Audio quality 1"): ("--audio-quality 1"),
            ("Audio quality 2"): ("--audio-quality 2"),
            ("Audio quality 3"): ("--audio-quality 3"),
            ("Audio qualit 4"): ("--audio-quality 4"),
            ("Mid audio quality"): ("--audio-quality 5"),
            ("Audio quality 6"): ("--audio-quality 6"),
            ("Audio quality 7"): ("--audio-quality 7"),
            ("Audio quality 8"): ("--audio-quality 8"),
            ("Worse audio quality 9"): ("--audio-quality 9"),
            }

opt = {"PLAYLIST": "--no-playlist", "WARNINGS": "", "THUMB": "",
       "METADATA": "", "V_FORMAT": "bestvideo+bestaudio/best",
       "A_FORMAT": "", "A_QUALITY": "--audio-quality 5", 
       }

class Downloader(wx.Panel):
    """
    
    """
    def __init__(self, parent):
        """
        """
        self.parent = parent
        wx.Panel.__init__(self, parent, -1) 
        """constructor"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.choice = wx.Choice(self, wx.ID_ANY, 
                                     choices=['Video+Audio',  
                                              'Audio only',],
                                     size=(-1,-1),
                                     )
        box = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                    _(" Media streams to download "))), 
                                        wx.VERTICAL)
        box.Add(self.choice, 0, wx.ALIGN_CENTER | wx.ALL, 20)
        self.choice.SetSelection(0)
        sizer.Add(box, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        self.cmbx_vf = wx.ComboBox(self, wx.ID_ANY,
                                   choices=[x for x in vformats],
                                   size=(110,-1),style=wx.CB_DROPDOWN|
                                                       wx.CB_READONLY
                                                       )
        self.cmbx_vf.SetSelection(0)
        grid_v = wx.FlexGridSizer(1, 5, 0, 0)
        sizer.Add(grid_v, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        grid_v.Add(self.cmbx_vf, 0, wx.ALL, 5)
        f = [x for x in vquality.get('All best')]
        self.cmbx_vq = wx.ComboBox(self, wx.ID_ANY, choices=f,
                                   size=(200,-1),style=wx.CB_DROPDOWN|
                                                      wx.CB_READONLY
                                                      )
        self.cmbx_vq.SetSelection(0)
        grid_v.Add((20, 20), 0,)
        grid_v.Add(self.cmbx_vq, 0, wx.ALL, 5)
        self.cmbx_aq = wx.ComboBox(self, wx.ID_ANY, 
                                   choices=[x for x in aquality.keys()],
                                   size=(200,-1),style=wx.CB_DROPDOWN|
                                                       wx.CB_READONLY
                                                       )
        self.cmbx_aq.SetSelection(5)
        grid_v.Add((20, 20), 0,)
        grid_v.Add(self.cmbx_aq, 0, wx.ALL, 5)
        self.cmbx_af = wx.ComboBox(self, wx.ID_ANY,
                                   choices=[x for x in aformats.keys()],
                                   size=(110,-1),style=wx.CB_DROPDOWN|
                                                       wx.CB_READONLY)
        self.cmbx_af.Disable()
        self.cmbx_af.SetSelection(0)
        grid_a = wx.FlexGridSizer(1, 1, 0, 0)
        sizer.Add(grid_a, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        grid_a.Add(self.cmbx_af, 0, wx.ALL, 5)
        #-------------opt
        line_0 = wx.StaticLine(self, pos=(25, 50), size=(650, 2))
        sizer.Add(line_0, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 10)
        grid_opt = wx.FlexGridSizer(1, 5, 0, 0)
        sizer.Add(grid_opt, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.ckbx_pl = wx.CheckBox(self, wx.ID_ANY,(
                                                  _('Download all playlist')))
        grid_opt.Add(self.ckbx_pl, 0, wx.ALL, 5)
        self.ckbx_warn = wx.CheckBox(self, wx.ID_ANY,(_('No warnings')))
        grid_opt.Add(self.ckbx_warn, 0, wx.ALL, 5)
        self.ckbx_thumb = wx.CheckBox(self, wx.ID_ANY,(
                                        _('Embed thumbnail in audio file')))
        grid_opt.Add(self.ckbx_thumb, 0, wx.ALL, 5)
        self.ckbx_meta = wx.CheckBox(self, wx.ID_ANY,(_('Add metadata to file')))
        grid_opt.Add(self.ckbx_meta, 0, wx.ALL, 5)
        line_1 = wx.StaticLine(self, pos=(25, 50), size=(650, 2))
        sizer.Add(line_1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 10)

        self.SetSizer(sizer)
        self.Layout()

        #----------------------Binder (EVT)----------------------#
        self.choice.Bind(wx.EVT_CHOICE, self.on_Choice)
        self.cmbx_vf.Bind(wx.EVT_COMBOBOX, self.on_Vf)
        self.cmbx_vq.Bind(wx.EVT_COMBOBOX, self.on_Vq)
        self.cmbx_af.Bind(wx.EVT_COMBOBOX, self.on_Af)
        self.cmbx_aq.Bind(wx.EVT_COMBOBOX, self.on_Aq)
        self.ckbx_pl.Bind(wx.EVT_CHECKBOX, self.on_Playlist)
        self.ckbx_warn.Bind(wx.EVT_CHECKBOX, self.on_Warnings)
        self.ckbx_thumb.Bind(wx.EVT_CHECKBOX, self.on_Thumbnails)
        self.ckbx_meta.Bind(wx.EVT_CHECKBOX, self.on_Metadata)
        
    #-----------------------------------------------------------------#
    def on_Choice(self, event):
        if self.choice.GetSelection() == 0:
            self.cmbx_af.Disable(), self.cmbx_vf.Enable()
            self.cmbx_aq.Enable(), self.cmbx_vq.Enable()
            self.cmbx_aq.Enable()
            
        elif self.choice.GetSelection() == 1:
            self.cmbx_vq.Disable(), self.cmbx_vf.Disable()
            self.cmbx_af.Enable(), self.cmbx_aq.Enable()
            self.cmbx_aq.Disable()

    #-----------------------------------------------------------------#
    def on_Vf(self, event): 
        self.cmbx_vq.Clear()
        fq = [x for x in vquality.get(self.cmbx_vf.GetValue())]
        self.cmbx_vq.Append((fq),)
        self.cmbx_vq.SetSelection(0)
        q = vquality[self.cmbx_vf.GetValue()].get(self.cmbx_vq.GetValue())
        opt["V_FORMAT"] = q
    #-----------------------------------------------------------------#
    def on_Vq(self, event):
        q = vquality[self.cmbx_vf.GetValue()].get(self.cmbx_vq.GetValue())
        opt["V_FORMAT"] = q
    #-----------------------------------------------------------------#
    def on_Af(self, event):
        opt["A_FORMAT"] = aformats.get(self.cmbx_af.GetValue())
    #-----------------------------------------------------------------#
    def on_Aq(self, event):
        opt["A_QUALITY"] = aquality.get(self.cmbx_aq.GetValue())
    #-----------------------------------------------------------------#
    def on_Playlist(self, event):
        if self.ckbx_pl.IsChecked():
            opt["PLAYLIST"] = "--yes-playlist"
        else:
            opt["PLAYLIST"] = "--no-playlist"
    #-----------------------------------------------------------------#
    def on_Warnings(self, event):
        if self.ckbx_warn.IsChecked():
            opt["WARNINGS"] = "--no-warnings"
        else:
            opt["WARNINGS"] = ""
    #-----------------------------------------------------------------#
    def on_Thumbnails(self, event):
        if self.ckbx_thumb.IsChecked():
            opt["THUMB"] = "--embed-thumbnail"
        else:
            opt["PLAYLIST"] = ""
    #-----------------------------------------------------------------#
    def on_Metadata(self, event):
        if self.ckbx_meta.IsChecked():
            opt["METADATA"] = "--add-metadata"
        else:
            opt["METADATA"] = ""
    #-----------------------------------------------------------------#
    def on_Start(self):
        # https://www.youtube.com/watch?v=R67nUHelLM4
        logname = 'Youtube_downloader'
        urls = self.parent.data
        
        if self.choice.GetSelection() == 0:
            cmd = ('{} {} {} {} {}'.format(opt["WARNINGS"], opt["METADATA"],
                                           opt["V_FORMAT"], opt["A_QUALITY"],
                                           opt["PLAYLIST"]))
        elif self.choice.GetSelection() == 1:
            cmd = ('{} {} {} {}'.format(opt["WARNINGS"], opt["METADATA"],
                                        opt["A_FORMAT"], opt["THUMB"],
                                        opt["PLAYLIST"]))

        self.parent.switch_Process('downloader',
                                        urls,
                                        '',
                                        self.parent.file_destin,
                                        cmd,
                                        None,
                                        '',
                                        '',
                                        logname, 
                                        len(urls),
                                        )
        
        
