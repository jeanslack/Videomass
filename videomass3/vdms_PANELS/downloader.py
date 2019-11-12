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
from __future__ import unicode_literals
import wx

vquality = {'Best quality video': 'bestvideo',
            'Worst quality video': 'worstvideo'}

aformats = {("Default format"): ("--extract-audio --audio-format bestaudio"),
            ("wav"): ("--extract-audio --audio-format wav"),
            ("mp3"): ("--extract-audio --audio-format mp3"),
            ("aac"): ("--extract-audio --audio-format aac"),
            ("m4a"): ("--extract-audio --audio-format m4a"),
            ("vorbis"): ("--extract-audio --audio-format vorbis"),
            ("opus"): ("--extract-audio --audio-format opus"),
            ("flac"): ("--extract-audio --audio-format flac"),
            }

aquality = {'Best quality audio': 'bestaudio',
            'Worst quality audio': 'worstaudio'}

opt = {"PLAYLIST": "--no-playlist", "WARNINGS": "", "THUMB": "",
       "METADATA": "", "V_QUALITY": "bestvideo",
       "A_FORMAT": "--extract-audio --audio-format best", 
       "A_QUALITY": "bestaudio", 
       }

yellow = '#a29500'
red = '#ea312d'

#####################################################################
def sizeof_fmt(num, suffix='B'):
    num = int(num)
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
######################################################################

class Downloader(wx.Panel):
    """
    
    """
    def __init__(self, parent, OS):
        """
        """
        self.parent = parent
        wx.Panel.__init__(self, parent, -1) 
        """constructor"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        #sizer.Add((20, 20), 0,)#wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 30)
        self.choice = wx.Choice(self, wx.ID_ANY, 
                                     choices=[_('Default'),
                                              _('Separated Video+Audio'),  
                                              _('Audio only'),
                                              _('By using format code')],
                                     size=(-1,-1),
                                     )
        box = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                    _(" Media streams to download "))), 
                                        wx.VERTICAL)
        box.Add(self.choice, 0, wx.ALIGN_CENTER | wx.ALL, 20)
        self.choice.SetSelection(0)
        sizer.Add(box, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        #sizer.Add((50, 50), 0,)#wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 30)
        self.txt_code = wx.TextCtrl(self, wx.ID_ANY, "", 
                                   style=wx.TE_PROCESS_ENTER, size=(50,-1)
                                   )
        self.txt_code.Disable()
        grid_fcode = wx.FlexGridSizer(1, 2, 0, 0)
        sizer.Add(grid_fcode, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.stext = wx.StaticText(self, wx.ID_ANY, (
                                        _('Enter `Format Code` number here:')))
        self.stext.Disable()
        grid_fcode.Add(self.stext, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        grid_fcode.Add(self.txt_code, 0, wx.ALL, 5)
        grid_v = wx.FlexGridSizer(1, 5, 0, 0)
        sizer.Add(grid_v, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        f = [x for x in vquality.keys()]
        self.cmbx_vq = wx.ComboBox(self, wx.ID_ANY, choices=f,
                                   size=(150,-1),style=wx.CB_DROPDOWN|
                                                      wx.CB_READONLY
                                                      )
        self.cmbx_vq.SetSelection(0)
        #grid_v.Add((20, 20), 0,)
        grid_v.Add(self.cmbx_vq, 0, wx.ALL, 5)
        self.cmbx_aq = wx.ComboBox(self, wx.ID_ANY, 
                                   choices=[x for x in aquality.keys()],
                                   size=(150,-1),style=wx.CB_DROPDOWN|
                                                       wx.CB_READONLY
                                                       )
        self.cmbx_aq.SetSelection(0)
        #grid_v.Add((20, 20), 0,)
        grid_v.Add(self.cmbx_aq, 0, wx.ALL, 5)
        self.cmbx_af = wx.ComboBox(self, wx.ID_ANY,
                                   choices=[x for x in aformats.keys()],
                                   size=(150,-1),style=wx.CB_DROPDOWN|
                                                       wx.CB_READONLY)
        self.cmbx_af.Disable()
        self.cmbx_af.SetSelection(0)
        #grid_a = wx.FlexGridSizer(1, 1, 0, 0)
        #sizer.Add(grid_a, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        grid_v.Add(self.cmbx_af, 0, wx.ALL, 5)
        #-------------opt
        #line_0 = wx.StaticLine(self, pos=(25, 50), size=(650, 2))
        #sizer.Add(line_0, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 10)
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
        #line_1 = wx.StaticLine(self, pos=(25, 50), size=(650, 2))
        #sizer.Add(line_1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 10)
        
        self.fcode = wx.ListCtrl(self, wx.ID_ANY,style=wx.LC_REPORT | 
                                                  wx.SUNKEN_BORDER
                                    )
        self.fcode.Disable()
        sizer.Add(self.fcode, 1, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        self.fcode.InsertColumn(0, (_('URL')), width=400)
        self.fcode.InsertColumn(1, (_('Format Code')), width=100)
        self.fcode.InsertColumn(2, (_('Extension')), width=80)
        self.fcode.InsertColumn(3, (_('Resolution')), width=150)
        self.fcode.InsertColumn(4, (_('Video Codec')), width=110)
        self.fcode.InsertColumn(5, (_('fps')), width=60)
        self.fcode.InsertColumn(6, (_('Audio Codec')), width=110)
        self.fcode.InsertColumn(7, (_('Size')), width=80)
        
        if OS == 'Darwin':
            self.fcode.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
        else:
            self.fcode.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))

        self.SetSizer(sizer)
        self.Layout()

        #----------------------Binder (EVT)----------------------#
        self.choice.Bind(wx.EVT_CHOICE, self.on_Choice)
        self.cmbx_vq.Bind(wx.EVT_COMBOBOX, self.on_Vq)
        self.cmbx_af.Bind(wx.EVT_COMBOBOX, self.on_Af)
        self.cmbx_aq.Bind(wx.EVT_COMBOBOX, self.on_Aq)
        self.ckbx_pl.Bind(wx.EVT_CHECKBOX, self.on_Playlist)
        self.ckbx_warn.Bind(wx.EVT_CHECKBOX, self.on_Warnings)
        self.ckbx_thumb.Bind(wx.EVT_CHECKBOX, self.on_Thumbnails)
        self.ckbx_meta.Bind(wx.EVT_CHECKBOX, self.on_Metadata)
    #-----------------------------------------------------------------#
    def infoParse(self):
        
        import youtube_dl
        
        index = 0
        self.parent.statusbar_msg("wait... I'm getting the data", 'YELLOW')
        for link in self.parent.data:
            #ydl_opts = {'listformats': True }
            ydl_opts = {'ignoreerrors' : True, 'noplaylist': True,}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                meta = ydl.extract_info(link, download=False)
                
                if meta:
                    if 'entries' in meta:
                        meta['entries'][0]
                    formats = meta.get('formats', [meta])
                    self.fcode.InsertItem(index, link)
                    self.fcode.SetItemBackgroundColour(index, 'GREEN')
                else:
                    self.fcode.InsertItem(index, 'ERROR: %s' % link)
                    self.fcode.SetItemBackgroundColour(index, red)
                    break
                
            for f in formats:
                index+=1
                if f['vcodec'] == 'none':
                    vcodec = ''
                    fps = ''
                else:
                    vcodec = f['vcodec']
                    fps = '%sfps' % f['fps']
                            
                if f['acodec'] == 'none':
                    acodec = 'Video only'
                else:
                    acodec = f['acodec']
                
                if f['filesize']:
                    size = sizeof_fmt(f['filesize'])
                else:
                    size = ''
                
                self.fcode.InsertItem(index, '' )
                self.fcode.SetItem(index, 1, f['format_id'] )
                self.fcode.SetItem(index, 2, f['ext'])
                self.fcode.SetItem(index, 3, f['format'].split('-')[1])
                self.fcode.SetItem(index, 4, vcodec)
                self.fcode.SetItem(index, 5, fps)
                self.fcode.SetItem(index, 6, acodec)
                self.fcode.SetItem(index, 7, size)
                
        self.parent.statusbar_msg('Youtube Downloader', None)

    #-----------------------------------------------------------------#
    def on_Choice(self, event):
        if self.choice.GetSelection() in [0,1]:
            self.cmbx_af.Disable(), self.cmbx_aq.Enable()
            self.cmbx_vq.Enable(), self.txt_code.Disable()
            self.fcode.Disable(), self.stext.Disable()
            
        elif self.choice.GetSelection() == 2:
            self.cmbx_vq.Disable(), self.cmbx_aq.Disable()
            self.cmbx_af.Enable(), self.txt_code.Disable()
            self.fcode.Disable(), self.stext.Disable()
            
        elif self.choice.GetSelection() == 3:
            self.cmbx_vq.Disable(), self.cmbx_aq.Disable()
            self.cmbx_af.Disable(), self.txt_code.Enable()
            self.fcode.Enable(), self.stext.Enable()
            self.infoParse()

    #-----------------------------------------------------------------#
    def on_Vq(self, event):
        opt["V_QUALITY"] = vquality[self.cmbx_vq.GetValue()]
        
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
            opt["THUMB"] = ""
    #-----------------------------------------------------------------#
    def on_Metadata(self, event):
        if self.ckbx_meta.IsChecked():
            opt["METADATA"] = "--add-metadata"
        else:
            opt["METADATA"] = ""
    #-----------------------------------------------------------------#
    def on_Start(self):

        logname = 'Youtube_downloader'
        urls = self.parent.data
        
        if self.choice.GetSelection() == 0:
            cmd = [('--format {}+{} {} {} {}'.format(opt["V_QUALITY"], 
                                                    opt["A_QUALITY"], 
                                                    opt["METADATA"], 
                                                    opt["PLAYLIST"], 
                                                    opt["WARNINGS"])),
                    ('%(title)s.%(ext)s')
                    ]
        if self.choice.GetSelection() == 1:
            cmd = [('--format {},{} {} {} {}'.format(opt["V_QUALITY"], 
                                                    opt["A_QUALITY"], 
                                                    opt["METADATA"], 
                                                    opt["PLAYLIST"], 
                                                    opt["WARNINGS"])),
                   ('%(title)s.f%(format_id)s.%(ext)s')
                   ]
        elif self.choice.GetSelection() == 2: # audio only
            cmd = [('{} {} {} {}'.format(opt["A_FORMAT"], 
                                        opt["THUMB"],
                                        opt["METADATA"], 
                                        opt["PLAYLIST"],
                                        opt["WARNINGS"])),
                    ('%(title)s.%(ext)s')
                    ]
        if self.choice.GetSelection() == 3:
            code = self.txt_code.GetValue().strip()
            if not code.isdigit() or not code:
                wx.MessageBox(_('Enter a `Format Code` number in the text '
                                'box, please'),'Videomass', wx.ICON_INFORMATION)
                self.txt_code.SetBackgroundColour((255,192,255))
                return
            
            cmd = [('--format {} {} {} {}'.format(code,
                                                 opt["METADATA"], 
                                                 opt["PLAYLIST"], 
                                                 opt["WARNINGS"])),
                    ('%(title)s.%(ext)s')]

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
