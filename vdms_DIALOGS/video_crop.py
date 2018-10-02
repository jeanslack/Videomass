# -*- coding: UTF-8 -*-

#########################################################
# Name: video_crop.py
# Porpose: a module for video crop on video_conv panel
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2015-2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3

# This file is part of Videomass2.

#    Videomass2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass2.  If not, see <http://www.gnu.org/licenses/>.

# Rev (00) October 2 2018
#########################################################

import wx
#import wx.lib.masked as masked # not work on macOSX

class VideoCrop(wx.Dialog):
    """
    Show a dialog with buttons for movie image orientation.
    TODO: make rotate button with images 
    """
    
    def __init__(self, parent, orientation, msg):
        """
        Make sure you use the clear button when you finish the task.
        """
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.label_top = wx.StaticText(self, wx.ID_ANY, ("Top"))
        self.top = wx.SpinCtrl(self, wx.ID_ANY, "0", min=0,  max=10000,
                               size=(100,-1), style=wx.TE_PROCESS_ENTER
                                )
        self.label_right = wx.StaticText(self, wx.ID_ANY, ("Right"))
        self.right = wx.SpinCtrl(self, wx.ID_ANY, "0", min=0, max=10000, 
                                 size=(100,-1), style=wx.TE_PROCESS_ENTER
                                 )
        self.label_bottom = wx.StaticText(self, wx.ID_ANY, ("Bottom"))
        self.bottom = wx.SpinCtrl(self, wx.ID_ANY, "0", min=0, max=10000, 
                                 size=(100,-1), style=wx.TE_PROCESS_ENTER
                                 )
        self.label_left = wx.StaticText(self, wx.ID_ANY, ("Left"))
        self.left = wx.SpinCtrl(self, wx.ID_ANY, "0", min=0, max=10000, 
                                 size=(100,-1), style=wx.TE_PROCESS_ENTER
                                 )
        self.text_crop = wx.TextCtrl(self, wx.ID_ANY, "", 
                                    style=wx.TE_PROCESS_ENTER | wx.TE_READONLY
                                    )
        sizerLabel = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                    "Crop Dimensions")), wx.VERTICAL)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        self.btn_ok = wx.Button(self, wx.ID_OK, "")
        btn_reset = wx.Button(self, wx.ID_CLEAR, "")
        #----------------------Properties------------------------------------#

        self.SetTitle("Video Crop - Videomass2")
        self.top.SetBackgroundColour(wx.Colour(122, 239, 255))
        self.top.SetToolTipString("Reverses visual movie from bottom to top")
        self.right.SetBackgroundColour(wx.Colour(122, 239, 255))
        self.right.SetToolTipString("Rotate view movie to left")
        self.bottom.SetBackgroundColour(wx.Colour(122, 239, 255))
        self.bottom.SetToolTipString("Rotate view movie to Right")
        self.left.SetBackgroundColour(wx.Colour(122, 239, 255))
        self.left.SetToolTipString("Reverses visual movie from top to bottom")
        self.text_crop.SetMinSize((200, -1))
        self.text_crop.SetToolTipString("Display show settings")

        #----------------------Handle layout---------------------------------#

        sizerBase = wx.BoxSizer(wx.VERTICAL)
        gridBase = wx.FlexGridSizer(2, 0, 0, 0)
        sizerBase.Add(gridBase, 0, wx.ALL, 0)
        gridBtnExit = wx.FlexGridSizer(1, 3, 0, 0)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        grid_sizerLabel = wx.GridSizer(1, 1, 0, 0)
        grid_sizerBase = wx.FlexGridSizer(1, 5, 0, 0)

        sizer_3.Add(self.label_top, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer_3.Add(self.top, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        grid_sizerBase.Add(self.label_left, 0, wx.ALL 
                                                | wx.ALIGN_CENTER_HORIZONTAL 
                                                | wx.ALIGN_CENTER_VERTICAL, 5
                                                )
        grid_sizerBase.Add(self.left, 0, wx.ALL 
                                                | wx.ALIGN_CENTER_HORIZONTAL 
                                                | wx.ALIGN_CENTER_VERTICAL, 5
                                                )
        grid_sizerBase.Add((50, 50), 0, wx.ALL 
                                            | wx.ALIGN_CENTER_HORIZONTAL 
                                            | wx.ALIGN_CENTER_VERTICAL, 5
                                            )
        grid_sizerBase.Add(self.right, 0, wx.ALL 
                                            | wx.ALIGN_CENTER_HORIZONTAL 
                                            | wx.ALIGN_CENTER_VERTICAL, 5
                                            )
        grid_sizerBase.Add(self.label_right, 0, wx.ALL 
                                                | wx.ALIGN_CENTER_HORIZONTAL 
                                                | wx.ALIGN_CENTER_VERTICAL, 5
                                                )
        
        sizer_3.Add(grid_sizerBase, 1, wx.EXPAND, 0)
        sizer_3.Add(self.bottom, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL 
                                                | wx.ALIGN_CENTER_VERTICAL,5
                                                )
        sizer_3.Add(self.label_bottom, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL 
                                                | wx.ALIGN_CENTER_VERTICAL,5
                                                )
        grid_sizerLabel.Add(self.text_crop, 0, wx.ALL 
                                        | wx.ALIGN_CENTER_HORIZONTAL 
                                        | wx.ALIGN_CENTER_VERTICAL,5
                                        )
        sizer_3.Add(grid_sizerLabel, 1, wx.EXPAND, 0)
        sizerLabel.Add(sizer_3, 1, wx.EXPAND, 0)
        gridBase.Add(sizerLabel, 1, wx.ALL | 
                                    wx.ALIGN_CENTER_HORIZONTAL | 
                                    wx.ALIGN_CENTER_VERTICAL,15)
        gridBase.Add(gridBtnExit, 1, wx.ALL,5)
        
        gridBtnExit.Add(btn_close, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL 
                                              | wx.ALIGN_CENTER_VERTICAL,5
                                               )
        gridBtnExit.Add(self.btn_ok, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL 
                                                | wx.ALIGN_CENTER_VERTICAL,5
                                                )
        gridBtnExit.Add(btn_reset, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL 
                                                | wx.ALIGN_CENTER_VERTICAL,5
                                                )
        self.SetSizer(sizerBase)
        sizerBase.Fit(self)
        self.Layout()

        #----------------------Binding (EVT)---------------------------------#
        #self.Bind(wx.EVT_BUTTON, self.on_up, self.button_up)
        #self.Bind(wx.EVT_BUTTON, self.on_left, self.button_left)
        #self.Bind(wx.EVT_BUTTON, self.on_right, self.button_right)
        #self.Bind(wx.EVT_BUTTON, self.on_down, self.button_down)
        ##self.Bind(wx.EVT_BUTTON, self.on_reset, self.button_reset)
        #self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        #self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
        #self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)
        
        #if orientation == '':
            #self.orientation = ''
        #else:
            #self.orientation = orientation
            #self.text_crop.SetValue(msg)

    ##----------------------Event handler (callback)--------------------------#
    #def on_up(self, event):
        #self.orientation = "-vf 'vflip, hflip' -metadata:s:v rotate=0"
        #self.text_crop.SetValue("180° from bottom to top")
        
    ##------------------------------------------------------------------#
    #def on_left(self, event):
        #opt = "-vf 'transpose=1,transpose=1,transpose=1' -metadata:s:v rotate=0"
        #self.orientation = opt
        #self.text_crop.SetValue("Rotate 90° Left")
        
    ##------------------------------------------------------------------#
    #def on_right(self, event):
        #self.orientation = "-vf 'transpose=1' -metadata:s:v rotate=0"
        #self.text_crop.SetValue("Rotate 90° Right")
        
    ##------------------------------------------------------------------#
    #def on_down(self, event):
        #self.orientation = "-vf 'hflip, vflip' -metadata:s:v rotate=0"
        #self.text_crop.SetValue("180° from top to bottom")
        
    ##------------------------------------------------------------------#
    #def on_reset(self, event):
        #self.orientation = ""
        #self.text_crop.SetValue("")
        
    ##------------------------------------------------------------------#
    #def on_close(self, event):

        #event.Skip()

    ##------------------------------------------------------------------#
    #def on_ok(self, event):
        #"""
        #if you enable self.Destroy(), it delete from memory all data event and
        #no return correctly. It has the right behavior if not used here, because 
        #it is called in the main frame. 
        
        #Event.Skip(), work correctly here. Sometimes needs to disable it for
        #needs to maintain the view of the window (for exemple).
        #"""
        #self.GetValue()
        ##self.Destroy()
        #event.Skip()
    ##------------------------------------------------------------------#
    #def GetValue(self):
        #"""
        #This method return values via the interface GetValue()
        #"""
        #msg = self.text_crop.GetValue()
        #return (self.orientation, msg)
