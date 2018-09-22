# -*- coding: UTF-8 -*-

#########################################################
# Name: dialog_tools.py
# Porpose: a module with multiple dialog tools
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

# Rev (05) 20/07/2014
# Rev (06) 12/03/2015
# Rev (07)  30/04/2015 (improved management audio with ffprobe)
# Rev (08)  04/Aug/2018 (improved management audio with ffprobe)
#########################################################

import wx
#import wx.lib.masked as masked # not work on macOSX


class Cut_Range(wx.Dialog):
    """
    This class show a simple dialog with a timer selection for
    cutting a time range of audio and video streams. 
    FIXME: replace spinctrl with a timer spin float ctrl if exist
    """
    def __init__(self, parent, title, hasSet):
        """
        FFmpeg use this format of a time range to specifier a media cutting
        range: "-ss 00:00:00 -t 00:00:00". The -ss flag is the initial
        start selection time; the -t flag is the duration time amount 
        starting from -ss. All this one is specified by hours, minutes and 
        seconds values.
        See FFmpeg documents for more details..
        When this dialog is called, the values previously set are returned 
        for a complete reading (if there are preconfigured values)
        """
        if hasSet == '':
            self.init_hour = '00'
            self.init_minute = '00'
            self.init_seconds = '00'
            self.cut_hour = '00'
            self.cut_minute = '00'
            self.cut_seconds = '00'
        else:#return a previus settings:
            self.init_hour = hasSet[4:6]
            self.init_minute = hasSet[7:9]
            self.init_seconds = hasSet[10:12]
            self.cut_hour = hasSet[16:18]
            self.cut_minute = hasSet[19:21]
            self.cut_seconds = hasSet[22:24]
        
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        """constructor """
        self.start_hour_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                  self.init_hour), min=0, max=23, style=wx.TE_PROCESS_ENTER)
        self.start_minute_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                self.init_minute), min=0, max=59, style=wx.TE_PROCESS_ENTER)
        self.start_second_ctrl = wx.SpinCtrl(self, wx.ID_ANY,"%s" % (
               self.init_seconds), min=0, max=59, style=wx.TE_PROCESS_ENTER)
        sizer_1_staticbox = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                            "Start time position (h:m:s)")), wx.VERTICAL)
        self.stop_hour_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                   self.cut_hour), min=0, max=23, style=wx.TE_PROCESS_ENTER)
        self.stop_minute_ctrl = wx.SpinCtrl(self, wx.ID_ANY,"%s" % (
                 self.cut_minute), min=0, max=59, style=wx.TE_PROCESS_ENTER)
        self.stop_second_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                self.cut_seconds), min=0, max=59, style=wx.TE_PROCESS_ENTER)
        sizer_2_staticbox = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                            "Time progress duration (h:m:s)")), wx.VERTICAL)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        btn_ok = wx.Button(self, wx.ID_OK, "")
        btn_reset = wx.Button(self, wx.ID_CLEAR, "")

        #----------------------Properties ----------------------#
        self.SetTitle(title)
        self.start_hour_ctrl.SetMinSize((45,30 ))
        self.start_minute_ctrl.SetMinSize((45, 30))
        self.start_second_ctrl.SetMinSize((45, 30))
        self.start_hour_ctrl.SetToolTipString("Hours time")
        self.start_minute_ctrl.SetToolTipString("Minutes Time")
        self.start_second_ctrl.SetToolTipString("Seconds time")
        self.stop_hour_ctrl.SetMinSize((45, 30))
        self.stop_minute_ctrl.SetMinSize((45, 30))
        self.stop_second_ctrl.SetMinSize((45, 30))
        self.stop_hour_ctrl.SetToolTipString("Hours amount duration")
        self.stop_second_ctrl.SetToolTipString("Minutes amount duration")
        self.stop_minute_ctrl.SetToolTipString("Seconds amount duration")
        #----------------------Layout----------------------#
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(2, 2, 0, 0)
        gridFlex1 = wx.FlexGridSizer(1, 3, 0, 0)
        gridFlex2 = wx.FlexGridSizer(1, 3, 0, 0)
        gridBtn = wx.FlexGridSizer(1, 3, 0, 0)
        
        grid_sizer_base.Add(sizer_1_staticbox,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_1_staticbox.Add(gridFlex1,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        gridFlex1.Add(self.start_hour_ctrl,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        gridFlex1.Add(self.start_minute_ctrl,0, wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        gridFlex1.Add(self.start_second_ctrl,0, wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        
        grid_sizer_base.Add(sizer_2_staticbox,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        sizer_2_staticbox.Add(gridFlex2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        gridFlex2.Add(self.stop_hour_ctrl,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        gridFlex2.Add(self.stop_minute_ctrl,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        gridFlex2.Add(self.stop_second_ctrl,0,wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        
        grid_sizer_base.Add(gridBtn,1,)
        gridBtn.Add(btn_close,1, wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        gridBtn.Add(btn_ok,1,wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        gridBtn.Add(btn_reset,1, wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        
        sizer_base.Add(grid_sizer_base, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        #----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_SPINCTRL, self.start_hour, self.start_hour_ctrl)
        self.Bind(wx.EVT_SPINCTRL, self.start_minute, self.start_minute_ctrl)
        self.Bind(wx.EVT_SPINCTRL, self.start_second, self.start_second_ctrl)
        self.Bind(wx.EVT_SPINCTRL, self.stop_hour, self.stop_hour_ctrl)
        self.Bind(wx.EVT_SPINCTRL, self.stop_minute, self.stop_minute_ctrl)
        self.Bind(wx.EVT_SPINCTRL, self.stop_second, self.stop_second_ctrl)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.resetValues, btn_reset)

    #----------------------Event handler (callback)----------------------#
    def start_hour(self, event):
        self.init_hour = '%s' % self.start_hour_ctrl.GetValue()
        if len(self.init_hour) == 1:
            self.init_hour = '0%s' % self.start_hour_ctrl.GetValue()
            
    #------------------------------------------------------------------#
    def start_minute(self, event):
        self.init_minute = '%s' % self.start_minute_ctrl.GetValue()
        if len(self.init_minute) == 1:
            self.init_minute = '0%s' % self.start_minute_ctrl.GetValue()
            
    #------------------------------------------------------------------#
    def start_second(self, event):
        self.init_seconds = '%s' % self.start_second_ctrl.GetValue()
        if len(self.init_seconds) == 1:
            self.init_seconds = '0%s' % self.start_second_ctrl.GetValue()
            
    #------------------------------------------------------------------#
    def stop_hour(self, event):
        self.cut_hour = '%s' % self.stop_hour_ctrl.GetValue()
        if len(self.cut_hour) == 1:
            self.cut_hour = '0%s' % self.stop_hour_ctrl.GetValue()
            
    #------------------------------------------------------------------#
    def stop_minute(self, event):
        self.cut_minute = '%s' % self.stop_minute_ctrl.GetValue()
        if len(self.cut_minute) == 1:
            self.cut_minute = '0%s' % self.stop_minute_ctrl.GetValue()
            
    #------------------------------------------------------------------#
    def stop_second(self, event):
        self.cut_seconds = '%s' % self.stop_second_ctrl.GetValue()
        if len(self.cut_seconds) == 1:
            self.cut_seconds = '0%s' % self.stop_second_ctrl.GetValue()
            
    #------------------------------------------------------------------#
    def resetValues(self, event):
        """
        Reset all values at initial state. Is need to confirm with
        ok Button for apply correctly.
        """
        self.start_hour_ctrl.SetValue(0), self.start_minute_ctrl.SetValue(0),
        self.start_second_ctrl.SetValue(0),self.stop_hour_ctrl.SetValue(0),
        self.stop_minute_ctrl.SetValue(0), self.stop_second_ctrl.SetValue(0)
        self.init_hour, self.init_minute, self.init_seconds = '00','00','00'
        self.cut_hour, self.cut_minute, self.cut_seconds = '00','00','00'
    #------------------------------------------------------------------#
    def on_close(self, event):

        event.Skip() # need if destroy from parent

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
        cut_range = "-ss %s:%s:%s -t %s:%s:%s" % (self.init_hour,
                                    self.init_minute, self.init_seconds,
                                    self.cut_hour, self.cut_minute, 
                                    self.cut_seconds)
        return cut_range
    
##########################################################################
class SaveImages(wx.Dialog):
    """
    Extract one range  of jpg images by setting the start time, 
    progress time and amount of frames of the movie. 
    """
    def __init__(self, parent, hasSet, vrate):
        """
        NOTE: The timer settings on the movie for managing the selection 
        and duration (see Cut_Range above), have global influence (such as the 
        Cut_Range dialog above). 
        Make sure you use the clear button when you finish the task.
        """
        if hasSet == '':
            self.init_hour = '00'
            self.init_minute = '00'
            self.init_seconds = '00'
            self.cut_hour = '00'
            self.cut_minute = '00'
            self.cut_seconds = '00'
            self.vrate = ''
        else:#return a previus settings:
            self.init_hour = hasSet[4:6]
            self.init_minute = hasSet[7:9]
            self.init_seconds = hasSet[10:12]
            self.cut_hour = hasSet[16:18]
            self.cut_minute = hasSet[19:21]
            self.cut_seconds = hasSet[22:24]
            self.vrate = vrate

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        """constructor """
        #self.time_start = masked.TimeCtrl(self, wx.ID_ANY, "0")
        #siz1_staticbox = wx.StaticBox(self, wx.ID_ANY, ("Tempo Inizio (h:m:s)"))
        #self.time_lengh = masked.TimeCtrl(self, wx.ID_ANY, "")
        #siz2_staticbox = wx.StaticBox(self, wx.ID_ANY, ("Tempo Avanzamento (h:m:s)"))
        self.start_hour_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                  self.init_hour), min=0, max=23, style=wx.TE_PROCESS_ENTER)
        self.start_minute_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                self.init_minute), min=0, max=59, style=wx.TE_PROCESS_ENTER)
        self.start_second_ctrl = wx.SpinCtrl(self, wx.ID_ANY,"%s" % (
               self.init_seconds), min=0, max=59, style=wx.TE_PROCESS_ENTER)
        siz1_staticbox = wx.StaticBox(self, wx.ID_ANY, (
                                            "Start time position (h:m:s)"))
        
        self.stop_hour_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                   self.cut_hour), min=0, max=23, style=wx.TE_PROCESS_ENTER)
        self.stop_minute_ctrl = wx.SpinCtrl(self, wx.ID_ANY,"%s" % (
                 self.cut_minute), min=0, max=59, style=wx.TE_PROCESS_ENTER)
        self.stop_second_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                self.cut_seconds), min=0, max=59, style=wx.TE_PROCESS_ENTER)
        siz2_staticbox = wx.StaticBox(self, wx.ID_ANY, (
                                        "Time progress duration (h:m:s)"))
        
        
        self.combo_box = wx.ComboBox(self, wx.ID_ANY, choices=[("0.2"), ("0.5"), 
                ("1"), ("1.5"), ("2")], style=wx.CB_DROPDOWN | wx.CB_READONLY
                )
        siz3_staticbox = wx.StaticBox(self, wx.ID_ANY, ("Frame-Rate "
                                "(frequency frames capture)"))
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        self.btn_ok = wx.Button(self, wx.ID_OK, "")
        btn_reset = wx.Button(self, wx.ID_CLEAR, "")

        #----------------------Properties----------------------#
        self.SetTitle("Saves Video Images")
        self.start_hour_ctrl.SetMinSize((45, 30))
        self.start_minute_ctrl.SetMinSize((45, 30))
        self.start_second_ctrl.SetMinSize((45, 30))
        self.start_hour_ctrl.SetToolTipString("Hours time")
        self.start_minute_ctrl.SetToolTipString("Minutes Time")
        self.start_second_ctrl.SetToolTipString("Seconds time")
        self.stop_hour_ctrl.SetMinSize((45, 30))
        self.stop_minute_ctrl.SetMinSize((45, 30))
        self.stop_second_ctrl.SetMinSize((45, 30))
        self.stop_hour_ctrl.SetToolTipString("Hours amount duration")
        self.stop_second_ctrl.SetToolTipString("Minutes amount duration")
        self.stop_minute_ctrl.SetToolTipString("Seconds amount duration")
        self.combo_box.SetSelection(0)
        self.combo_box.SetToolTipString("Choose from this list the frequency "
                                      "of the extracted images. More is low, "
                                      "the lower will be the extracted images."
                                        )
        #----------------------handle layout----------------------#
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(2, 1, 0, 0)
        grid_sizer_4 = wx.FlexGridSizer(2, 1, 0, 0)
        grid_sizer_6 = wx.FlexGridSizer(1, 3, 0, 0)
        grid_sizer_2 = wx.GridSizer(2, 1, 0, 0)
        siz3_staticbox.Lower()
        sizer_7 = wx.StaticBoxSizer(siz3_staticbox, wx.VERTICAL)
        grid_sizer_3 = wx.GridSizer(1, 2, 0, 0)
        siz2_staticbox.Lower()
        sizer_6 = wx.StaticBoxSizer(siz2_staticbox, wx.HORIZONTAL)
        siz1_staticbox.Lower()
        sizer_5 = wx.StaticBoxSizer(siz1_staticbox, wx.HORIZONTAL)
        sizer_5.Add(self.start_hour_ctrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_5.Add(self.start_minute_ctrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_5.Add(self.start_second_ctrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_3.Add(sizer_5, 1, wx.ALL | wx.EXPAND, 15)
        sizer_6.Add(self.stop_hour_ctrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_6.Add(self.stop_minute_ctrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_6.Add(self.stop_second_ctrl, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grid_sizer_3.Add(sizer_6, 1, wx.ALL | wx.EXPAND, 15)
        grid_sizer_2.Add(grid_sizer_3, 1, wx.EXPAND, 0)
        sizer_7.Add(self.combo_box, 0, wx.ALL| wx.CENTER, 5)
        grid_sizer_2.Add(sizer_7, 1, wx.ALL | wx.EXPAND, 15)
        grid_sizer_1.Add(grid_sizer_2, 1, wx.EXPAND, 0)
        grid_sizer_6.Add(btn_close, 0, wx.ALL, 5)
        grid_sizer_6.Add(self.btn_ok, 0, wx.ALL, 5)
        grid_sizer_6.Add(btn_reset, 0, wx.ALL, 5)
        grid_sizer_4.Add(grid_sizer_6, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(grid_sizer_4, 1, wx.EXPAND, 0)
        sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

        #----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_SPINCTRL, self.start_hour, self.start_hour_ctrl)
        self.Bind(wx.EVT_SPINCTRL, self.start_minute, self.start_minute_ctrl)
        self.Bind(wx.EVT_SPINCTRL, self.start_second, self.start_second_ctrl)
        self.Bind(wx.EVT_SPINCTRL, self.stop_hour, self.stop_hour_ctrl)
        self.Bind(wx.EVT_SPINCTRL, self.stop_minute, self.stop_minute_ctrl)
        self.Bind(wx.EVT_SPINCTRL, self.stop_second, self.stop_second_ctrl)
        #self.Bind(wx.EVT_SPINCTRL, self.on_time_init, self.time_start)
        #self.Bind(wx.EVT_SPINCTRL, self.on_time_finish, self.time_lengh)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
        self.Bind(wx.EVT_BUTTON, self.resetValues, btn_reset)
        
        if self.vrate:
            self.combo_box.SetValue("%s" % self.vrate[3:])

    #----------------------Event handler (callback)----------------------#
    def start_hour(self, event):
        self.init_hour = '%s' % self.start_hour_ctrl.GetValue()
        if len(self.init_hour) == 1:
            self.init_hour = '0%s' % self.start_hour_ctrl.GetValue()
            
    #------------------------------------------------------------------#
    def start_minute(self, event):
        self.init_minute = '%s' % self.start_minute_ctrl.GetValue()
        if len(self.init_minute) == 1:
            self.init_minute = '0%s' % self.start_minute_ctrl.GetValue()
            
    #------------------------------------------------------------------#
    def start_second(self, event):
        self.init_seconds = '%s' % self.start_second_ctrl.GetValue()
        if len(self.init_seconds) == 1:
            self.init_seconds = '0%s' % self.start_second_ctrl.GetValue()
            
    #------------------------------------------------------------------#
    def stop_hour(self, event):
        self.cut_hour = '%s' % self.stop_hour_ctrl.GetValue()
        if len(self.cut_hour) == 1:
            self.cut_hour = '0%s' % self.stop_hour_ctrl.GetValue()
            
    #------------------------------------------------------------------#
    def stop_minute(self, event):
        self.cut_minute = '%s' % self.stop_minute_ctrl.GetValue()
        if len(self.cut_minute) == 1:
            self.cut_minute = '0%s' % self.stop_minute_ctrl.GetValue()
            
    #------------------------------------------------------------------#
    def stop_second(self, event):
        self.cut_seconds = '%s' % self.stop_second_ctrl.GetValue()
        if len(self.cut_seconds) == 1:
            self.cut_seconds = '0%s' % self.stop_second_ctrl.GetValue()
    #------------------------------------------------------------------#
    def resetValues(self, event):
        """
        Reset all values at initial state. Is need to confirm with
        ok Button for apply correctly.
        """
        self.start_hour_ctrl.SetValue(0), self.start_minute_ctrl.SetValue(0),
        self.start_second_ctrl.SetValue(0),self.stop_hour_ctrl.SetValue(0),
        self.stop_minute_ctrl.SetValue(0), self.stop_second_ctrl.SetValue(0)
        self.init_hour, self.init_minute, self.init_seconds = '00','00','00'
        self.cut_hour, self.cut_minute, self.cut_seconds = '00','00','00'
        self.combo_box.SetSelection(0)
    #------------------------------------------------------------------#
    def on_close(self, event):

        event.Skip() # need if destroy from parent
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
        cut_range = "-ss %s:%s:%s -t %s:%s:%s" % (self.init_hour,
                                    self.init_minute, self.init_seconds,
                                    self.cut_hour, self.cut_minute, 
                                    self.cut_seconds)
        self.vrate = '-r %s' % self.combo_box.GetValue()
        return cut_range, self.vrate
    
#############################################################################

class VideoRotate(wx.Dialog):
    """
    Show a dialog with buttons for movie image orientation.
    TODO: make rotate button with images 
    """
    
    def __init__(self, parent, orientation, msg):
        """
        Make sure you use the clear button when you finish the task.
        """
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)

        
        self.button_up = wx.Button(self, wx.ID_ANY, ("Flip over")) # capovolgi Sopra
        self.button_left = wx.Button(self, wx.ID_ANY, ("Rotate Left")) # ruota sx
        self.button_right = wx.Button(self, wx.ID_ANY, ("Rotate Right")) # ruota a destra
        self.button_down = wx.Button(self, wx.ID_ANY, ("Flip below")) # capovolgi sotto
        #self.button_reset = wx.Button(self, wx.ID_ANY, ("RESET"))
        self.text_rotate = wx.TextCtrl(self, wx.ID_ANY, "", 
                                    style=wx.TE_PROCESS_ENTER | wx.TE_READONLY
                                    )
        sizerLabel = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                    "Orientation points")), wx.VERTICAL)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        self.btn_ok = wx.Button(self, wx.ID_OK, "")
        btn_reset = wx.Button(self, wx.ID_CLEAR, "")
        #----------------------Properties------------------------------------#

        self.SetTitle("Set Visual Rotation")
        self.button_up.SetBackgroundColour(wx.Colour(122, 239, 255))
        self.button_up.SetToolTipString("Reverses visual movie from bottom to top")
        self.button_left.SetBackgroundColour(wx.Colour(122, 239, 255))
        self.button_left.SetToolTipString("Rotate view movie to left")
        self.button_right.SetBackgroundColour(wx.Colour(122, 239, 255))
        self.button_right.SetToolTipString("Rotate view movie to Right")
        self.button_down.SetBackgroundColour(wx.Colour(122, 239, 255))
        self.button_down.SetToolTipString("Reverses visual movie from top to bottom")
        self.text_rotate.SetMinSize((200, 30))
        self.text_rotate.SetToolTipString("Display show settings")

        #----------------------Handle layout---------------------------------#

        sizerBase = wx.BoxSizer(wx.VERTICAL)
        gridBase = wx.FlexGridSizer(2, 0, 0, 0)
        sizerBase.Add(gridBase, 0, wx.ALL, 0)
        gridBtnExit = wx.FlexGridSizer(1, 3, 0, 0)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        grid_sizerLabel = wx.GridSizer(1, 1, 0, 0)
        grid_sizerBase = wx.GridSizer(1, 2, 0, 0)

        sizer_3.Add(self.button_up, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        grid_sizerBase.Add(self.button_left, 0, wx.ALL 
                                                | wx.ALIGN_CENTER_HORIZONTAL 
                                                | wx.ALIGN_CENTER_VERTICAL, 5
                                                )
        grid_sizerBase.Add(self.button_right, 0, wx.ALL 
                                            | wx.ALIGN_CENTER_HORIZONTAL 
                                            | wx.ALIGN_CENTER_VERTICAL, 5
                                            )
        sizer_3.Add(grid_sizerBase, 1, wx.EXPAND, 0)
        sizer_3.Add(self.button_down, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL 
                                                | wx.ALIGN_CENTER_VERTICAL,5
                                                )
        #grid_sizerLabel.Add(self.button_reset, 0, wx.ALL 
                                            #| wx.ALIGN_CENTER_HORIZONTAL 
                                            #| wx.ALIGN_CENTER_VERTICAL,5
                                            #)
        grid_sizerLabel.Add(self.text_rotate, 0, wx.ALL 
                                        | wx.ALIGN_CENTER_HORIZONTAL 
                                        | wx.ALIGN_CENTER_VERTICAL,5
                                        )
        sizer_3.Add(grid_sizerLabel, 1, wx.EXPAND, 0)
        sizerLabel.Add(sizer_3, 1, wx.EXPAND, 0)
        gridBase.Add(sizerLabel, 1, wx.ALL | 
                                    wx.ALIGN_CENTER_HORIZONTAL | 
                                    wx.ALIGN_CENTER_VERTICAL,5)
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
        self.Bind(wx.EVT_BUTTON, self.on_up, self.button_up)
        self.Bind(wx.EVT_BUTTON, self.on_left, self.button_left)
        self.Bind(wx.EVT_BUTTON, self.on_right, self.button_right)
        self.Bind(wx.EVT_BUTTON, self.on_down, self.button_down)
        #self.Bind(wx.EVT_BUTTON, self.on_reset, self.button_reset)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)
        
        if orientation == '':
            self.orientation = ''
        else:
            self.orientation = orientation
            self.text_rotate.SetValue(msg)

    #----------------------Event handler (callback)--------------------------#
    def on_up(self, event):
        self.orientation = "-vf 'vflip, hflip' -metadata:s:v rotate=0"
        self.text_rotate.SetValue("180° from bottom to top")
        
    #------------------------------------------------------------------#
    def on_left(self, event):
        opt = "-vf 'transpose=1,transpose=1,transpose=1' -metadata:s:v rotate=0"
        self.orientation = opt
        self.text_rotate.SetValue("Rotate 90° Left")
        
    #------------------------------------------------------------------#
    def on_right(self, event):
        self.orientation = "-vf 'transpose=1' -metadata:s:v rotate=0"
        self.text_rotate.SetValue("Rotate 90° Right")
        
    #------------------------------------------------------------------#
    def on_down(self, event):
        self.orientation = "-vf 'hflip, vflip' -metadata:s:v rotate=0"
        self.text_rotate.SetValue("180° from top to bottom")
        
    #------------------------------------------------------------------#
    def on_reset(self, event):
        self.orientation = ""
        self.text_rotate.SetValue("")
        
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
        msg = self.text_rotate.GetValue()
        return (self.orientation, msg)


