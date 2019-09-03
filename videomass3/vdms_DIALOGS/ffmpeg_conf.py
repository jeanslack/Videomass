# -*- coding: UTF-8 -*-

#########################################################
# Name: ffmpeg_conf.py
# Porpose: Dialog to show the build configuration of the FFmpeg
# Compatibility: Python3, wxPython4
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Aug.18 2019
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
import os
from shutil import which

class Checkconf(wx.Dialog):
    """
    View the features of the build configuration of 
    FFmpeg on different notebook panels
    
    """
    def __init__(self, out, ffmpeg_link, ffprobe_link, ffplay_link, OS):
        """
        with 'None' not depend from parent:
        wx.Dialog.__init__(self, None, style=wx.DEFAULT_DIALOG_STYLE)
        
        With parent, -1:
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        if close videomass also close parent window:
        
        """
        wx.Dialog.__init__(self, None, style=wx.DEFAULT_DIALOG_STYLE)
        notebook_1 = wx.Notebook(self, wx.ID_ANY)
        notebook_1_pane_1 = wx.Panel(notebook_1, wx.ID_ANY,)
        txtinfo = wx.StaticText(notebook_1_pane_1, wx.ID_ANY,)
        notebook_1_pane_2 = wx.Panel(notebook_1, wx.ID_ANY)
        others_opt = wx.ListCtrl(notebook_1_pane_2, wx.ID_ANY, 
                                    style=wx.LC_REPORT | 
                                    wx.SUNKEN_BORDER
                                    )
        notebook_1_pane_3 = wx.Panel(notebook_1, wx.ID_ANY)
        enable_opt = wx.ListCtrl(notebook_1_pane_3, wx.ID_ANY, 
                                     style=wx.LC_REPORT | 
                                     wx.SUNKEN_BORDER
                                     )
        notebook_1_pane_4 = wx.Panel(notebook_1, wx.ID_ANY)
        
        disabled_opt = wx.ListCtrl(notebook_1_pane_4, wx.ID_ANY, 
                                       style=wx.LC_REPORT | 
                                       wx.SUNKEN_BORDER
                                       )
        #button_help = wx.Button(self, wx.ID_HELP, "")
        button_close = wx.Button(self, wx.ID_CLOSE, "")
        
        #----------------------Properties----------------------#
        self.SetTitle(_("Videomass: FFmpeg specifications"))
        others_opt.SetMinSize((700, 400))
        others_opt.InsertColumn(0, _('flags'), width=300)
        others_opt.InsertColumn(1, _('options'), width=450)
        #others_opt.SetBackgroundColour(wx.Colour(217, 255, 255))
        enable_opt.SetMinSize((700, 400))
        enable_opt.InsertColumn(0, _('status'), width=300)
        enable_opt.InsertColumn(1, _('options'), width=450)
        #enable_opt.SetBackgroundColour(wx.Colour(217, 255, 255))
        disabled_opt.SetMinSize((700, 400))
        disabled_opt.InsertColumn(0, _('status'), width=300)
        disabled_opt.InsertColumn(1, _('options'), width=450)
        #disabled_opt.SetBackgroundColour(wx.Colour(217, 255, 255))
        
        if OS == 'Darwin':
            txtinfo.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL))
            others_opt.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
            enable_opt.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
            disabled_opt.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
        else:
            txtinfo.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.NORMAL))
            others_opt.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            enable_opt.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            disabled_opt.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        
        #----------------------Layout--------------------------#
        Base = wx.BoxSizer(wx.VERTICAL)

        grid_buttons = wx.FlexGridSizer(1, 1, 0, 0)
        sizer_tab1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_tab2 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab3 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab4 = wx.BoxSizer(wx.VERTICAL)

        grid_tab1 = wx.FlexGridSizer(1, 1, 10, 10)
        sizer_tab1.Add(grid_tab1)
        grid_tab1.Add(txtinfo, 1, wx.ALL , 5)
        notebook_1_pane_1.SetSizer(sizer_tab1)
        
        sizer_tab2.Add(others_opt, 1, wx.ALL | wx.EXPAND, 5)
        notebook_1_pane_2.SetSizer(sizer_tab2)
        
        sizer_tab3.Add(enable_opt, 1, wx.ALL | wx.EXPAND, 5)
        notebook_1_pane_3.SetSizer(sizer_tab3)
        
        sizer_tab4.Add(disabled_opt, 1, wx.ALL | wx.EXPAND, 5)
        notebook_1_pane_4.SetSizer(sizer_tab4)
        
        notebook_1.AddPage(notebook_1_pane_1, (_("Informations")))
        notebook_1.AddPage(notebook_1_pane_2, (_("System options")))
        notebook_1.AddPage(notebook_1_pane_3, (_("Options enabled")))
        notebook_1.AddPage(notebook_1_pane_4, (_("Options disabled")))

        Base.Add(notebook_1, 1, wx.ALL|wx.EXPAND, 5)####
        grid_buttons.Add(button_close, 0, wx.ALL, 5)

        Base.Add(grid_buttons, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=0)####

        self.SetSizer(Base)
        Base.Fit(self)
        self.Layout()
        
        # create lists by out:
        info, others, enable, disable = out
        #---------
        if OS == 'Windows':
            biname = ['ffmpeg.exe','ffprobe.exe','ffplay.exe']
        else:
            biname = ['ffmpeg','ffprobe','ffplay']
        #---------
        if which(biname[0]):
            ffmpeg = _("FFmpeg   ...installed")
        else:
            if os.path.exists(ffmpeg_link):
                ffmpeg = _("FFmpeg   ...was imported locally")
            
        if which(biname[1]):
            ffprobe = _("FFprobe   ...installed")
        else:
            if os.path.exists(ffprobe_link):
                ffprobe = _("FFprobe   ...was imported locally")
            else:
                ffprobe = _("FFprobe   ...not found !")
                
        if which(biname[2]):
            ffplay = _("FFplay   ...installed")
        else:
            if os.path.exists(ffplay_link):
                ffplay = _("FFplay   ...was imported locally")
            else:
                ffplay = _("FFplay   ...not found !")
        
        #### populate txtinfo TextCtrl output:
        txtinfo.SetLabel("\n\n\n\n"
                         "              %s\n"
                         "              %s\n"
                         "\n\n\n"
                         "             - %s\n"
                         "             - %s\n"
                         "             - %s\n" % (info[0].strip(),
                                                  info[1].strip(),
                                                  ffmpeg,
                                                  ffprobe,
                                                  ffplay,
                                                  ))
        #### populate others_opt listctrl output:
        index = 0 
        if not others:
            print ('No others option found')
        else:
            others_opt.InsertItem(index, _('Specific compilation options'))
            others_opt.SetItemBackgroundColour(index, "CORAL")
            n = len(others)
            for a in range(n):
                if '=' in others[a]:
                    (key, value) = others[a].strip().split('=')
                    #(key, value) = others[a][0].strip().split('=')
                    num_items = others_opt.GetItemCount()
                    index +=1
                    others_opt.InsertItem(index, key)
                    others_opt.SetItem(index, 1, value)
                
        #### populate enable_opt listctrl output:
        index = 0
        if not enable:
            print ('No options enabled')
        else:
            enable_opt.InsertItem(index, _('ENABLED:'))
            enable_opt.SetItemBackgroundColour(index, "GREEN")
            n = len(enable)
            for a in range(n):
                (key, value) = _('Enabled'), enable[a]
                num_items = enable_opt.GetItemCount()
                index +=1
                enable_opt.InsertItem(index, key)
                enable_opt.SetItem(index, 1, value)
        
        #### populate disabled_opt listctrl output:
        index = 0 
        if not disable:
            print ('No options disabled')
        else:
            disabled_opt.InsertItem(index, _('DISABLED:'))
            disabled_opt.SetItemBackgroundColour(index, "RED")
            n = len(disable)
            for a in range(n):
                (key, value) = _('Disabled'), disable[a]
                num_items = disabled_opt.GetItemCount()
                index +=1
                disabled_opt.InsertItem(index, key)
                disabled_opt.SetItem(index, 1, value)
                    
        #----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close) # controlla la chiusura (x)
        #self.Bind(wx.EVT_BUTTON, self.on_help, button_help)

    #----------------------Event handler (callback)----------------------#
    def on_close(self, event):
        self.Destroy()
        #event.Skip()

    #-------------------------------------------------------------------#
