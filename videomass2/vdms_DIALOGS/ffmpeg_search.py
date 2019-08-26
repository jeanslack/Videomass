# -*- coding: UTF-8 -*-

#########################################################
# Name: ffmpeg_search.py
# Porpose: Show a dialog box to search FFmpeg topics
# Compatibility: Python2, wxPython3 classic
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Aug.23 2019
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

from videomass2.vdms_IO import IO_tools
import wx
import re

class FFmpeg_Search(wx.Dialog):
    """
    Search and view all the FFmpeg help options.
    
    """
    def __init__(self, ffmpeg_link, OS):
        """
        The list of topics in the combo box is part of the 
        'Print help / information / capabilities:' section 
        given by the -h option on the FFmpeg command line.
        
        """
        self.ffmpeg = ffmpeg_link
        self.OS = OS
        self.row = None
        
        wx.Dialog.__init__(self, None, style=wx.DEFAULT_DIALOG_STYLE |
                                             wx.RESIZE_BORDER
                                             )
        """
        with 'None' not depend from parent:
        wx.Dialog.__init__(self, None, style=wx.DEFAULT_DIALOG_STYLE)
        
        With parent, -1:
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        if close videomass also close parent window:
        
        """
        self.cmbx_choice = wx.ComboBox(self,wx.ID_ANY, choices=[
                        ("--"),
                        (_("print basic options")),
                        (_("print more options")),
                        (_("print all options (very long)")),
                        (_("show available devices")),
                        (_("show available bit stream filters")),
                        (_("show available protocols")),
                        (_("show available filters")),
                        (_("show available pixel formats")),
                        (_("show available audio sample formats")),
                        (_("show available color names")),
                        (_("list sources of the input device")),
                        (_("list sinks of the output device")),
                        (_("show available HW acceleration methods")),
                        ],
                        style=wx.CB_DROPDOWN | wx.CB_READONLY
                        )
        self.cmbx_choice.SetSelection(0)
        self.cmbx_choice.SetToolTipString(_(
                                      "Choose one of the topics in the list"))
        self.texthelp = wx.TextCtrl(self, wx.ID_ANY, "", 
                                    size=(550,400),
                                    style = wx.TE_READONLY |
                                            wx.TE_MULTILINE | 
                                            wx.TE_RICH | 
                                            wx.HSCROLL)
        if OS == 'Darwin':
            self.texthelp.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
        else:
            self.texthelp.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.search = wx.SearchCtrl(self, wx.ID_ANY, size=(200,30),
                                    style=wx.TE_PROCESS_ENTER,)
        self.search.SetToolTipString(_("The search function allows you to "
                                       "find entries in the current topic"
                                       ))
        self.case = wx.CheckBox(self, wx.ID_ANY, (_("Ignore-case")))
        self.case.SetToolTipString(_("Ignore case distinctions, so that "
                                     "characters that differ only in case "
                                     "match each other."
                                    ))
        self.button_close = wx.Button(self, wx.ID_CLOSE, "")

        sizer = wx.BoxSizer(wx.VERTICAL)
        grid_src = wx.GridSizer(1, 2, 5, 5)
        grid = wx.GridSizer(1, 1, 0, 0)
        sizer.Add(self.texthelp, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(self.cmbx_choice, 0, wx.ALL, 5)
        grid_src.Add(self.search, 0, wx.ALL, 5)
        grid_src.Add(self.case, 0,  wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(grid_src, 0, wx.ALL, 5)
        sizer.Add(grid, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=5)
        grid.Add(self.button_close, 1, wx.ALL, 5)
        
        self.SetTitle(_("Videomass: FFmpeg search topics"))
        # set_properties:
        #self.texthelp.SetBackgroundColour((217, 255, 255))
        #self.SetSizer(sizer)
        self.SetSizerAndFit(sizer)
        
        self.Bind(wx.EVT_COMBOBOX, self.on_Selected, self.cmbx_choice)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_Search, self.search)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_Search, self.search)
        self.Bind(wx.EVT_BUTTON, self.on_close, self.button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close) # controlla la chiusura (x)

    #---------------------------------------------------------#
    def on_Selected(self, event):
        """
        Gets output given ffmpeg -*topic* and set textctrl.
        The topic options are values of the dicdef dictionary.
        """
        dicdef = {"--":'None',
                  _("print basic options"): ['-h'],
                  _("print more options"):['-h', 'long'],
                  _("print all options (very long)"):['-h','full'],
                  _("show available devices"):['-devices'],
                  _("show available bit stream filters"):['-bsfs'],
                  _("show available protocols"):['-protocols'],
                  _("show available filters"):['-filters'],
                  _("show available pixel formats"):['-pix_fmts'],
                  _("show available audio sample formats"):['-sample_fmts'],
                  _("show available color names"):['-colors'],
                  _("list sources of the input device"):['-sources', 'device'],
                  _("list sinks of the output device"):['-sinks', 'device'],
                  _("show available HW acceleration methods"):['-hwaccels'],
                  }
        if "None" in dicdef[self.cmbx_choice.GetValue()]:
            self.row = None
            self.texthelp.Clear()# reset textctrl
        else:
            self.texthelp.Clear()# reset textctrl
            topic = dicdef[self.cmbx_choice.GetValue()]
            out = IO_tools.findtopic(self.ffmpeg, topic, self.OS)
            self.row = out
            if self.row:
                self.texthelp.AppendText(self.row)
            else:
                self.texthelp.AppendText(_("\n  ..Nothing available"))

    #--------------------------------------------------------------#
    def on_Search(self, event):
        """
        Search the string typed on the search control and find 
        on the current self.row output. The result is very similar 
        to 
        `ffmpeg -*option* | grep string` 
        or (if checkbox is True)
        `ffmpeg -*option* | grep -i string` on the shell.
        """
        strsrc = event.GetString()
        
        if self.row and not strsrc:
            self.texthelp.Clear()# reset textctrl
            self.texthelp.AppendText('%s' % self.row)
            return
        
        if self.row: # se vuoi una ricerca specifica (è come grep)
            find = []

            if self.case.GetValue() == True:# include tutto Hello/hello
                
                for lines in self.row.split('\n'): 
                    if re.search(strsrc, lines, re.IGNORECASE):
                        find.append("%s\n" % lines)
            else:
                for lines in self.row.split('\n'): # case sensitive
                    if strsrc in lines:
                        find.append("%s\n" % lines)
                    
            if not find:
                self.texthelp.Clear()# reset textctrl
                self.texthelp.AppendText(_('\n  ...Not found'))
            else:
                self.texthelp.Clear()# reset textctrl
                self.texthelp.AppendText(' '.join(find))
        else:
            self.texthelp.Clear()# reset textctrl
            self.texthelp.AppendText(_(
                                "\n  Choose a topic in the drop down first"))
        

        
    #--------------------------------------------------------------# 
    def on_close(self, event):
        '''
        destroy dialog by button and the X
        '''
        self.Destroy()
        #event.Skip()

    #-------------------------------------------------------------------#
