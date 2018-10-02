# -*- coding: UTF-8 -*-

#########################################################
# Name: video_sizer.py
# Porpose: a module for video resizing on video_conv panel
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

# Rev (00) October 1 2018
#########################################################

import wx
#import wx.lib.masked as masked # not work on macOSX

class Video_Sizer(wx.Dialog):
    """
    This class show parameters for set custom video resizing. 
    Include a video size, video scaling with setdar and 
    setsar options.
    """
    def __init__(self, parent, hasSet):
        """
        See FFmpeg documents for more details..
        When this dialog is called, the values previously set are returned 
        for a complete reading (if there are preconfigured values)
        """
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        """constructor """
        ####----scaling static box section
        v_scalingbox = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                    "Set Video Scaling")), wx.VERTICAL)
        
        self.spin_scale_width = wx.SpinCtrl(self, wx.ID_ANY, "0", min=-2, 
                                            max=10000, style=wx.TE_PROCESS_ENTER
                                            )
        self.label_x1 = wx.StaticText(self, wx.ID_ANY, ("X")
                                      )
        self.label_x1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD,0, "")
                              )
        self.spin_scale_height = wx.SpinCtrl(self, wx.ID_ANY, "0", min=-2, 
                                             max=10000, style=wx.TE_PROCESS_ENTER
                                             )
        self.label_setdar = wx.StaticText(self, wx.ID_ANY, ("SetDar:")
                                          )
        self.spin_darN1 = wx.SpinCtrl(self, wx.ID_ANY, "16", min=0, 
                                      max=10000, style=wx.TE_PROCESS_ENTER,
                                      size=(90,-1))
        self.label_sepdar = wx.StaticText(self, wx.ID_ANY, (":")
                                          )
        self.label_sepdar.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, 
                                          wx.BOLD,0, "")
                                          )
        self.spin_darN2 = wx.SpinCtrl(self, wx.ID_ANY, "9", min=0, 
                                      max=10000, style=wx.TE_PROCESS_ENTER,
                                      size=(90,-1)
                                      )##
        self.label_setsar = wx.StaticText(self, wx.ID_ANY, ("SetSar:")
                                          )
        self.spin_sarN1 = wx.SpinCtrl(self, wx.ID_ANY, "1", min=0, 
                                      max=10000, style=wx.TE_PROCESS_ENTER,
                                      size=(90,-1))
        self.label_sepsar = wx.StaticText(self, wx.ID_ANY, (":")
                                          )
        self.label_sepsar.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, 
                                          wx.BOLD,0, "")
                                          )
        self.spin_sarN2 = wx.SpinCtrl(self, wx.ID_ANY, "1", min=0, 
                                      max=10000, style=wx.TE_PROCESS_ENTER,
                                      size=(90,-1))##
        ####----Button preview and CheckBox section
        #self.btn_preview = wx.Button(self, wx.ID_ANY, ("Preview"))
        #self.btn_preview.SetBackgroundColour(wx.Colour(122, 239, 255))
        self.ckb_enablesize = wx.CheckBox(self, wx.ID_ANY, (
                                               "Enable Video Size"))
        ####---videosize section
        v_sizerbox = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                    "Set Video Size")), wx.VERTICAL)
        self.spin_size_width = wx.SpinCtrl(self, wx.ID_ANY, 
        "0", min=0, max=10000, style=wx.TE_PROCESS_ENTER
                                           )
        self.label_x2 = wx.StaticText(self, wx.ID_ANY, ("X"))
        self.label_x2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD,0, "")
                              )
        self.spin_size_height = wx.SpinCtrl(self, wx.ID_ANY,
        "0", min=0, max=10000, style=wx.TE_PROCESS_ENTER
                                            )
        ####----- confirm buttons section
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        btn_ok = wx.Button(self, wx.ID_OK, "")
        btn_reset = wx.Button(self, wx.ID_CLEAR, "")
        
        self.SetTitle("Set Video Size - Videomass2")
        
        ####------Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(4, 1, 0, 0)
        
        # scaling section:
        grid_sizer_base.Add(v_scalingbox, 1, wx.ALL | wx.EXPAND, 5)
        Flex_scale_base = wx.FlexGridSizer(2, 1, 0, 0)
        Flex_scale = wx.FlexGridSizer(1, 3, 0, 0)
        Flex_scale_base.Add(Flex_scale)
        Flex_scale.Add(self.spin_scale_width, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_scale.Add(self.label_x1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_scale.Add(self.spin_scale_height, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_darsar = wx.FlexGridSizer(2, 4, 0, 0)
        Flex_scale_base.Add(Flex_darsar, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_darsar.Add(self.label_setdar, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_darsar.Add(self.spin_darN1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_darsar.Add(self.label_sepdar, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_darsar.Add(self.spin_darN2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_darsar.Add(self.label_setsar, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_darsar.Add(self.spin_sarN1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_darsar.Add(self.label_sepsar, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_darsar.Add(self.spin_sarN2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        v_scalingbox.Add(Flex_scale_base)
        
        # preview and CheckBox section
        #grid_sizer_base.Add(self.btn_preview, 0, wx.ALL|
                            #wx.ALIGN_CENTER_VERTICAL|
                            #wx.ALIGN_CENTER_HORIZONTAL|
                            #wx.EXPAND, 5
                            #)
        grid_sizer_base.Add(self.ckb_enablesize, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        
        # video size section:
        grid_sizer_base.Add(v_sizerbox, 1, wx.ALL | wx.EXPAND, 5)
        Flex_sizing = wx.FlexGridSizer(1, 3, 0, 0)
        Flex_sizing.Add(self.spin_size_width, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_sizing.Add(self.label_x2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_sizing.Add(self.spin_size_height, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        v_sizerbox.Add(Flex_sizing)
        
        # confirm btn section:
        gridBtn = wx.FlexGridSizer(1, 3, 0, 0)
        grid_sizer_base.Add(gridBtn)
        gridBtn.Add(btn_close,1, wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        gridBtn.Add(btn_ok,1, wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        gridBtn.Add(btn_reset,1, wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        
        # final settings:
        sizer_base.Add(grid_sizer_base, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        
        scale_str = (
        'Scale (resize) the input video or image, using the libswscale library. '
        " If we'd like to keep the aspect ratio, we need to specify only one "
        'component, either width or height, and set the other component to -1 '
        'or to -2')
        self.spin_scale_width.SetToolTipString('WIDTH:\n%s' % scale_str)
        self.spin_scale_height.SetToolTipString('HEIGHT:\n%s' % scale_str)
        setdar_str = (
        'Set the frame (d)isplay (a)spect (r)atio. The setdar filter sets the '
         'Display Aspect Ratio for the filter output video. This is done by ' 
         'changing the specified Sample (aka Pixel) Aspect Ratio, according to ' 
         'the following equation: \n'
             'DAR = HORIZONTAL_RESOLUTION / VERTICAL_RESOLUTION * SAR \n'
         'Keep in mind that the setdar filter does not modify the pixel '
         'dimensions of the video frame. Also, the display aspect ratio set by '
         'this filter may be changed by later filters in the filterchain, e.g. '
         'in case of scaling or if another "setdar" or a "setsar" filter is '
         'applied. ')
        self.spin_darN1.SetToolTipString(setdar_str)
        self.spin_darN2.SetToolTipString(setdar_str)
        setsar_str = (
        'The setsar filter sets the Sample (aka Pixel) Aspect Ratio for the '
        'filter output video. Note that as a consequence of the application '
        'of this filter, the output display aspect ratio will change according '
        'to the equation above. Keep in mind that the sample aspect ratio set '
        'by the setsar filter may be changed by later filters in the '
        'filterchain, e.g. if another "setsar" or a "setdar" filter is '
        'applied. ')
        self.spin_sarN1.SetToolTipString(setsar_str)
        self.spin_sarN2.SetToolTipString(setsar_str)
        
        
        
        
        
