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

class Choose_Topic(wx.Panel):
    """
    Helps to choose the appropriate contextual panel
    """
    def __init__(self, parent, OS):

        self.parent = parent
        self.OS = OS

        wx.Panel.__init__(self, parent, -1)
        
        welcome = wx.StaticText(self, wx.ID_ANY, (
                             _("Welcome to Videomass")))
        vers = wx.StaticText(self, wx.ID_ANY, (
                             _("Choose a Topic")))
        welcome.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))
        
        
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(welcome, 0, wx.TOP|
                                   wx.ALIGN_CENTER_VERTICAL|
                                   wx.ALIGN_CENTER_HORIZONTAL, 15)
        sizer_base.Add(vers, 0, wx.ALL|
                                wx.ALIGN_CENTER_VERTICAL|
                                wx.ALIGN_CENTER_HORIZONTAL, 15)
        grid_buttons = wx.GridSizer(3, 2, 20, 20)
        
        self.video = wx.Button(self, wx.ID_ANY, "Video Conversions", size=(-1,-1))
        self.audio = wx.Button(self, wx.ID_ANY, "Audio Conversions", size=(-1,-1))
        self.save_pict = wx.Button(self, wx.ID_ANY, "Pictures from Video", size=(-1,-1))
        self.audio_extract = wx.Button(self, wx.ID_ANY, "Extract Audio from Video", size=(-1,-1))
        
        self.slideshow = wx.Button(self, wx.ID_ANY, "Picture Slideshow Maker", size=(-1,-1))
        self.audio_merge = wx.Button(self, wx.ID_ANY, "Merging Audio and Video", size=(-1,-1))
        grid_buttons.AddMany([(self.video, 0, wx.EXPAND, 5),
                              (self.audio, 0, wx.EXPAND, 5),
                              (self.save_pict, 0, wx.EXPAND, 5),
                              (self.audio_extract, 0, wx.EXPAND, 5),
                              (self.audio_merge, 0, wx.EXPAND, 5),
                              (self.slideshow, 0, wx.EXPAND, 5)
                              ])
        
        sizer_base.Add(grid_buttons, 1, wx.EXPAND|
                                        wx.ALIGN_CENTER_VERTICAL|
                                        wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        self.SetSizerAndFit(sizer_base)
        
        self.Bind(wx.EVT_BUTTON, self.on_Choose, self.video)
        self.Bind(wx.EVT_BUTTON, self.on_Choose, self.audio)
        self.Bind(wx.EVT_BUTTON, self.on_Pictures, self.save_pict)
        self.Bind(wx.EVT_BUTTON, self.on_AudioFromVideo, self.audio_extract)
        self.Bind(wx.EVT_BUTTON, self.on_AudioMerging, self.audio_merge)
        self.Bind(wx.EVT_BUTTON, self.on_Slideshow, self.slideshow)
        
        
    def on_Choose(self, event):
        self.parent.File_import(self)
    
    def on_Pictures(self, event):
        print('pictures from video')
        
    def on_AudioFromVideo(self, event):
        print('audio from video')
    
    def on_AudioMerging(self, event):
        print('audio merging')
    
    def on_Slideshow(self, event):
        print('make a slideshow')
        
        

        
