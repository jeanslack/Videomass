# -*- coding: UTF-8 -*-

#########################################################
# Name: checkconf.py
# Porpose: Dialog to show the build configuration of the FFmpeg
# Compatibility: Python2, wxPython classic
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
from videomass2.vdms_SYS.whichcraft import which

class Checkconf(wx.Dialog):
    """
    View the features of the build configuration of 
    FFmpeg on different notebook panels
    
    """
    def __init__(self, out, ffmpeg_link, ffprobe_link, ffplay_link):
        # with 'None' not depend from videomass. With 'parent, -1' if close
        # videomass also close mediainfo window:
        #wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        wx.Dialog.__init__(self, None, style=wx.DEFAULT_DIALOG_STYLE)
        notebook_1 = wx.Notebook(self, wx.ID_ANY)
        notebook_1_pane_1 = wx.Panel(notebook_1, wx.ID_ANY)
        txtinfo = wx.StaticText(notebook_1_pane_1, wx.ID_ANY,)
        txtffmpeg = wx.StaticText(notebook_1_pane_1, wx.ID_ANY,)
        txtffprobe = wx.StaticText(notebook_1_pane_1, wx.ID_ANY,)
        txtffplay = wx.StaticText(notebook_1_pane_1, wx.ID_ANY,)
        notebook_1_pane_2 = wx.Panel(notebook_1, wx.ID_ANY)
        others_opt = wx.ListCtrl(notebook_1_pane_2, wx.ID_ANY, 
                                    style=wx.LC_REPORT | 
                                    wx.SUNKEN_BORDER
                                    )
        notebook_1_pane_3 = wx.Panel(notebook_1, wx.ID_ANY)
        optconf = wx.ListCtrl(notebook_1_pane_3, wx.ID_ANY, 
                                     style=wx.LC_REPORT | 
                                     wx.SUNKEN_BORDER
                                     )
        #notebook_1_pane_4 = wx.Panel(notebook_1, wx.ID_ANY)
        
        #optconf = wx.ListCtrl(notebook_1_pane_4, wx.ID_ANY, 
                                       #style=wx.LC_REPORT | 
                                       #wx.SUNKEN_BORDER
                                       #)
        ##button_help = wx.Button(self, wx.ID_HELP, "")
        button_close = wx.Button(self, wx.ID_CLOSE, "")
        
        #----------------------Properties----------------------#
        self.SetTitle(_(u"Videomass: FFmpeg specifications"))
        others_opt.SetMinSize((700, 400))
        others_opt.InsertColumn(0, _(u'Flags'), width=300)
        others_opt.InsertColumn(1, _(u'Options'), width=450)
        #others_opt.SetBackgroundColour(wx.Colour(217, 255, 255))
        optconf.SetMinSize((700, 400))
        optconf.InsertColumn(0, _(u'Status'), width=300)
        optconf.InsertColumn(1, _(u'Options'), width=450)
        ##optconf.SetBackgroundColour(wx.Colour(217, 255, 255))
        #optconf.SetMinSize((700, 400))
        #optconf.InsertColumn(0, _('Status'), width=300)
        #optconf.InsertColumn(1, _('Options'), width=450)
        ##optconf.SetBackgroundColour(wx.Colour(217, 255, 255))
        
        #----------------------Layout--------------------------#
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(2, 1, 0, 0)
        grid_buttons = wx.FlexGridSizer(1, 1, 0, 0)
        #sizer_tab4 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab3 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab2 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab1 = wx.BoxSizer(wx.VERTICAL)
        
        grid_tab1 = wx.FlexGridSizer(4, 1, 0, 0)
        sizer_tab1.Add(grid_tab1)
        grid_tab1.Add(txtinfo, 1, wx.ALL , 5)
        grid_tab1.Add(txtffmpeg, 1, wx.ALL , 5)
        grid_tab1.Add(txtffplay, 1, wx.ALL , 5)
        grid_tab1.Add(txtffprobe, 1, wx.ALL , 5)
        notebook_1_pane_1.SetSizer(sizer_tab1)
        
        sizer_tab2.Add(others_opt, 1, wx.ALL | wx.EXPAND, 5)
        notebook_1_pane_2.SetSizer(sizer_tab2)
        
        sizer_tab3.Add(optconf, 1, wx.ALL | wx.EXPAND, 5)
        notebook_1_pane_3.SetSizer(sizer_tab3)
        #sizer_tab4.Add(optconf, 1, wx.ALL | wx.EXPAND, 5)
        #notebook_1_pane_4.SetSizer(sizer_tab4)
        notebook_1.AddPage(notebook_1_pane_1, (_(u"Informations")))
        notebook_1.AddPage(notebook_1_pane_2, (_(u"System Options")))
        notebook_1.AddPage(notebook_1_pane_3, (_(u"Support Options")))
        #notebook_1.AddPage(notebook_1_pane_4, (_("Options Disabled")))
        grid_sizer_1.Add(notebook_1, 1, wx.ALL|wx.EXPAND, 5)
        grid_buttons.Add(button_close, 0, wx.ALL, 5)
        grid_sizer_1.Add(grid_buttons, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=0)

        sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        
        # delete previous append:
        #txtinfo.Clear()# reset textctrl before close
        txtinfo.SetLabel('')
        txtffmpeg.SetLabel('')
        txtffplay.SetLabel('')
        txtffprobe.SetLabel('')
        others_opt.DeleteAllItems()
        optconf.DeleteAllItems()
        #optconf.DeleteAllItems()
        
        # create lists by out:
        info, others, enable, disable = out
        
        if which(ffmpeg_link):
            txtffmpeg.SetForegroundColour((45,208,28))
            ffmpeg = _(u"FFmpeg   ...installed")
        else:
            if os.path.exists(ffmpeg_link):
                txtffmpeg.SetForegroundColour((208,198,28))
                ffmpeg = _(u"FFmpeg   ...was imported locally")
            
        if which(ffprobe_link):
            txtffprobe.SetForegroundColour((45,208,28))
            ffprobe = _(u"FFprobe   ...installed")
        else:
            if os.path.exists(ffprobe_link):
                txtffprobe.SetForegroundColour((208,198,28))
                ffprobe = _(u"FFprobe   ...was imported locally")
            else:
                txtffprobe.SetForegroundColour((209,28,28))
                ffprobe = _(u"FFprobe   ...not found !")
                
        if which(ffplay_link):
            txtffplay.SetForegroundColour((45,208,28))
            ffplay = _(u"FFplay   ...installed")
        else:
            if os.path.exists(ffplay_link):
                txtffplay.SetForegroundColour((208,198,28))
                ffplay = _(u"FFplay   ...was imported locally")
            else:
                txtffplay.SetForegroundColour((200,28,28))
                ffplay = _(u"FFplay   ...not found !")
        
        #### populate txtinfo TextCtrl output:
        txtinfo.SetFont(wx.Font(10, wx.SWISS, wx.ITALIC, wx.NORMAL))
        txtinfo.SetLabel( """\n
            %s\n
            %s\n
            -------------------------------------\n""" % (info[0].strip(),
                                                           info[1].strip(),
                                                           ))
        txtffmpeg.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
        txtffmpeg.SetLabel("          - %s" % ffmpeg)
        txtffprobe.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
        txtffprobe.SetLabel("                  - %s" % ffprobe)
        txtffplay.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
        txtffplay.SetLabel("              - %s" % ffplay)
            
        #### populate others_opt listctrl output:
        index = 0 
        if not others:
            print('No others option found')
        else:
            others_opt.InsertStringItem(index, _(u'Specific compilation options'))
            others_opt.SetItemBackgroundColour(index, "blue")
            n = len(others)
            for a in range(n):
                if '=' in others[a]:
                    (key, value) = others[a].strip().split('=')
                    #(key, value) = others[a][0].strip().split('=')
                    num_items = others_opt.GetItemCount()
                    index +=1
                    others_opt.InsertStringItem(index, key)
                    others_opt.SetStringItem(index, 1, value)
                
        #### populate optconf listctrl output:
        index = 0
        if not enable:
            print('No options enabled')
        else:
            optconf.InsertStringItem(index, _(u'ENABLED:'))
            optconf.SetItemBackgroundColour(index, "green")
            n = len(enable)
            for a in range(n):
                (key, value) = _(u'Enabled'), enable[a]
                num_items = optconf.GetItemCount()
                index +=1
                optconf.InsertStringItem(index, key)
                optconf.SetStringItem(index, 1, value)
        
        #### populate optconf listctrl output:
        index = 0 
        if not disable:
            print('No options disabled')
        else:
            optconf.InsertStringItem(index, _(u'DISABLED:'))
            optconf.SetItemBackgroundColour(index, "red")
            n = len(disable)
            for a in range(n):
                (key, value) = _(u'Disabled'), disable[a]
                num_items = optconf.GetItemCount()
                index +=1
                optconf.InsertStringItem(index, key)
                optconf.SetStringItem(index, 1, value)
                    
        #----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close) # controlla la chiusura (x)
        #self.Bind(wx.EVT_BUTTON, self.on_help, button_help)

    #----------------------Event handler (callback)----------------------#
    def on_close(self, event):
        self.Destroy()
        #event.Skip()

    #-------------------------------------------------------------------#
