# -*- coding: UTF-8 -*-

#########################################################
# Name: audio_conv
# Porpose: choose topic
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: October.25.2019
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
import wx.lib.agw.hyperlink as hpl

# get videomass wx.App attribute
get = wx.GetApp()
OS = get.OS
ydl = get.ydl

class Choose_Topic(wx.Panel):
    """
    Helps to choose the appropriate contextual panel
    """
    def __init__(self, parent, OS, videoconv_icn, audioconv_icn, 
                 storepictures_icn, slideshow_icn, audioextract_icn, 
                 merging_icn, youtube_icn, audionorm_icn, prstmng_icn):

        self.parent = parent
        self.OS = OS

        wx.Panel.__init__(self, parent, -1)
        
        welcome = wx.StaticText(self, wx.ID_ANY, (_("Welcome to Videomass")))
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(welcome, 0, wx.TOP|
                                   wx.ALIGN_CENTER_VERTICAL|
                                   wx.ALIGN_CENTER_HORIZONTAL, 15)
        #sizer_base.Add(vers, 0, wx.ALL|
                                #wx.ALIGN_CENTER_VERTICAL|
                                #wx.ALIGN_CENTER_HORIZONTAL, 15)
        grid_buttons = wx.FlexGridSizer(1, 4, 20, 20)
        grid_base = wx.GridSizer(1, 1, 0, 0)

        video_lab = _('    Video Conversions     ')
        audio_lab = _('    Audio Conversions     ')
        pict_lab = _('Pictures from Video')
        audgr_lab = _('Extract Audio from Video')
        slide_lab = _('Picture Slideshow Maker')
        audmer_lab = _('Merging Audio and Video')
        youtube_lab =  _('Download from YouTube')
        anorm_lab =  _('Audio Normalization')
        prst_mng =  _('      Presets Manager      ')
        
        self.presets_mng = wx.Button(self, wx.ID_ANY, prst_mng, size=(-1,-1))
        self.presets_mng.SetBitmap(wx.Bitmap(prstmng_icn),wx.TOP)
        self.video = wx.Button(self, wx.ID_ANY, video_lab, size=(-1,-1))
        self.video.SetBitmap(wx.Bitmap(videoconv_icn), wx.TOP)
        self.audio = wx.Button(self, wx.ID_ANY, audio_lab, size=(-1,-1))
        self.audio.SetBitmap(wx.Bitmap(audioconv_icn),wx.TOP)
        
        #self.save_pict = wx.Button(self, wx.ID_ANY, pict_lab, size=(-1,-1))
        #self.save_pict.SetBitmap(wx.Bitmap(storepictures_icn),wx.TOP)
        #self.audio_extract = wx.Button(self, wx.ID_ANY, audgr_lab, size=(-1,-1))
        #self.audio_extract.SetBitmap(wx.Bitmap(audioextract_icn),wx.TOP)
        #self.slideshow = wx.Button(self, wx.ID_ANY, slide_lab, size=(-1,-1))
        #self.slideshow.SetBitmap(wx.Bitmap(slideshow_icn),wx.TOP)
        #self.audio_merge = wx.Button(self, wx.ID_ANY, audmer_lab, size=(-1,-1))
        #self.audio_merge.SetBitmap(wx.Bitmap(merging_icn),wx.TOP)
        self.youtube = wx.Button(self, wx.ID_ANY, youtube_lab, size=(-1,-1))
        self.youtube.SetBitmap(wx.Bitmap(youtube_icn),wx.TOP)
        #self.anorm = wx.Button(self, wx.ID_ANY, anorm_lab, size=(-1,-1))
        #self.anorm.SetBitmap(wx.Bitmap(audionorm_icn),wx.TOP)

        grid_buttons.AddMany([(self.presets_mng, 0, wx.EXPAND, 5),
                              (self.video, 0, wx.EXPAND, 5),
                              (self.audio, 0, wx.EXPAND, 5),
                              #(self.save_pict, 0, wx.EXPAND, 5),
                              #(self.audio_merge, 0, wx.EXPAND, 5),
                              #(self.slideshow, 0, wx.EXPAND, 5),
                              (self.youtube, 0, wx.EXPAND, 5),
                              #(self.anorm, 0, wx.EXPAND, 5),
                              ])
        grid_base.Add(grid_buttons, 0, wx.ALIGN_CENTER_VERTICAL|
                                       wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer_base.Add(grid_base, 1, wx.EXPAND|
                                        wx.ALIGN_CENTER_VERTICAL|
                                        wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        sizer_hpl = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(sizer_hpl, 0, wx.ALL|
                                   wx.ALIGN_CENTER_VERTICAL|
                                   wx.ALIGN_CENTER_HORIZONTAL, 15)
        
        txt_link = wx.StaticText(self, label='Download additional presets or '
                                             'contribute to making new ones ')
        link = hpl.HyperLinkCtrl(self, -1, "Additional Presets",
                        URL="https://github.com/jeanslack/Videomass-presets")
        sizer_hpl.Add(txt_link)
        sizer_hpl.Add(link)
        self.SetSizerAndFit(sizer_base)
        
        
        if OS == 'Darwin':
            welcome.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        else:
            welcome.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        
        self.Bind(wx.EVT_BUTTON, self.on_Video, self.video)
        self.Bind(wx.EVT_BUTTON, self.on_Audio, self.audio)
        self.Bind(wx.EVT_BUTTON, self.on_Prst_mng, self.presets_mng)
        #self.Bind(wx.EVT_BUTTON, self.on_Pictures, self.save_pict)
        #self.Bind(wx.EVT_BUTTON, self.on_AudioFromVideo, self.audio_extract)
       # self.Bind(wx.EVT_BUTTON, self.on_AudioMerging, self.audio_merge)
        #self.Bind(wx.EVT_BUTTON, self.on_Slideshow, self.slideshow)
        self.Bind(wx.EVT_BUTTON, self.on_YoutubeDL, self.youtube)
    #------------------------------------------------------------------#    
    def on_Video(self, event):
        self.parent.File_import(self, 'Video Conversions')
    #------------------------------------------------------------------#
    def on_Audio(self, event):
        self.parent.File_import(self, 'Audio Conversions')
    
    #def on_Pictures(self, event):
        #print('pictures from video')
        
    #def on_AudioFromVideo(self, event):
        #print('audio from video')
    
    #def on_AudioMerging(self, event):
        #print('audio merging')
    
    #def on_Slideshow(self, event):
        #self.parent.File_import(self,'Pictures Slideshow Maker')
    #------------------------------------------------------------------#
    def on_YoutubeDL(self, event):
        if not ydl[0]:
            wx.MessageBox('ERROR: %s\n\nTo use this feature '
                          'please install youtube-dl.' % ydl[1],
                          'Videomass', wx.ICON_ERROR)
            return

        self.parent.Text_import(self, 'Youtube Downloader')
    #------------------------------------------------------------------#
    def on_Prst_mng(self, event):
        self.parent.File_import(self, 'Presets Manager')
