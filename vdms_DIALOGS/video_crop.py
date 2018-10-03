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
    
    def __init__(self, parent, fcrop):
        """
        Make sure you use the clear button when you finish the task.
        """
        self.w = ''
        self.h = ''
        self.y = ''
        self.x = ''
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        """ 
        """
        self.label_top = wx.StaticText(self, wx.ID_ANY, ("Top (Height)"))
        self.top = wx.SpinCtrl(self, wx.ID_ANY, "-1", min=-1,  max=10000,
                               size=(100,-1), style=wx.TE_PROCESS_ENTER
                                )
        self.label_right = wx.StaticText(self, wx.ID_ANY, ("Right (X)"))
        self.right = wx.SpinCtrl(self, wx.ID_ANY, "-1", min=-1, max=10000, 
                                 size=(100,-1), style=wx.TE_PROCESS_ENTER
                                 )
        self.label_bottom = wx.StaticText(self, wx.ID_ANY, ("Bottom (Y)"))
        self.bottom = wx.SpinCtrl(self, wx.ID_ANY, "-1", min=-1, max=10000, 
                                 size=(100,-1), style=wx.TE_PROCESS_ENTER
                                 )
        self.label_left = wx.StaticText(self, wx.ID_ANY, ("Left (Width)"))
        self.left = wx.SpinCtrl(self, wx.ID_ANY, "-1", min=-1, max=10000, 
                                 size=(100,-1), style=wx.TE_PROCESS_ENTER
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

        #----------------------Handle layout---------------------------------#
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        gridBase = wx.FlexGridSizer(2, 0, 0, 0)
        sizerBase.Add(gridBase, 0, wx.ALL, 0)
        gridBtnExit = wx.FlexGridSizer(1, 3, 0, 0)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
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
        
        #-------------- TOOLTIP
        height = (
        'Scale (resize) the input video or image, using the libswscale library. '
                  )
        self.top.SetToolTipString('Height:\n%s' % height)

        width = (
        'Set the frame (d)isplay (a)spect (r)atio. The setdar filter sets the ' 
                   )
        self.left.SetToolTipString(width)
        x = (
        'The setsar filter sets the Sample (aka Pixel) Aspect Ratio for the '
              )
        self.bottom.SetToolTipString(x)
        y = (
        'The setsar filter sets the Sample (aka Pixel) Aspect Ratio for the '
              )
        self.right.SetToolTipString(y)

        #----------------------Binding (EVT)---------------------------------#
        self.Bind(wx.EVT_SPINCTRL, self.on_top, self.top)
        self.Bind(wx.EVT_SPINCTRL, self.on_right, self.right)
        self.Bind(wx.EVT_SPINCTRL, self.on_bottom, self.bottom)
        self.Bind(wx.EVT_SPINCTRL, self.on_left, self.left)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)
        
        if fcrop: # set the previusly values
            s = fcrop.split(':')
            item1 = s[0][5:] # remove `crop=` word
            s[0] = item1 # replace first item
            for i in s:
                if i.startswith('w'):
                    self.w = i[2:]
                    self.left.SetValue(int(self.w))
                if i.startswith('h'):
                    self.h = i[2:]
                    self.top.SetValue(int(self.h))
                if i.startswith('y'):
                    self.y = i[2:]
                    self.bottom.SetValue(int(self.y))
                if i.startswith('x'):
                    self.x = i[2:]
                    self.right.SetValue(int(self.x))

    #----------------------Event handler (callback)--------------------------#
    def on_top(self, event):
        """
        Height
        """
        if self.top.GetValue() == '-1':
            self.h = ''
        else:
            self.h = 'h=%s:' % self.top.GetValue()
            
        
    #------------------------------------------------------------------#
    def on_right(self, event):
        """
        Y
        """
        if self.right.GetValue() == '-1':
            self.y = ''
        else:
            self.y = 'y=%s:' % self.right.GetValue()
        
    #------------------------------------------------------------------#
    def on_bottom(self, event):
        """
        X
        """
        if self.bottom.GetValue() == '-1':
            self.x = ''
        else:
            self.x = 'x=%s:' % self.bottom.GetValue()
    #------------------------------------------------------------------#
    def on_left(self, event):
        """
        Width
        """
        if self.left.GetValue() == '-1':
            self.w = ''
        else:
            self.w = 'w=%s:' % self.left.GetValue()
        
    #------------------------------------------------------------------#
    def on_reset(self, event):
        self.h, self.y, self.x, self.w = "", "", "", ""
        self.top.SetValue(-1), self.bottom.SetValue(-1)
        self.right.SetValue(-1), self.left.SetValue(-1)
        
    #------------------------------------------------------------------#
    def on_close(self, event):

        event.Skip()

    #------------------------------------------------------------------#
    def on_ok(self, event):
        """
        if you enable self.Destroy(), it delete from memory all data event and
        no return correctly. It has the right behavior if not used here, because 
        it is called in the main frame. 
        
        Event.Skip(), work correctly here. Sometimes needs to disable it for
        needs to maintain the view of the window (for exemple).
        """
        self.GetValue()
        #self.Destroy()
        event.Skip()
    #------------------------------------------------------------------#
    def GetValue(self):
        """
        This method return values via the interface GetValue()
        """

        s = '%s%s%s%s' % (self.w, self.h, self.x, self.y)
        l = len(s)
        val = '%s' % s[:l - 1]
        return (val)
