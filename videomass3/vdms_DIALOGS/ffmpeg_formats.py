# -*- coding: UTF-8 -*-

#########################################################
# Name: ffmpeg_formats.py
# Porpose: Dialog to show the available formats on the FFmpeg
# Compatibility: Python3, wxPython Phoenix
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

class FFmpeg_formats(wx.Dialog):
    """
    It shows a dialog box with a pretty kind of GUI to view 
    the formats available on FFmpeg
    
    """
    def __init__(self, dict_formats, OS):
        """
        with 'None' not depend from parent:
        wx.Dialog.__init__(self, None, style=wx.DEFAULT_DIALOG_STYLE)
        
        With parent, -1:
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        if close videomass also close parent window:
        
        """
        wx.Dialog.__init__(self, None, style=wx.DEFAULT_DIALOG_STYLE)
        notebook_1 = wx.Notebook(self, wx.ID_ANY)
        notebook_1_pane_1 = wx.Panel(notebook_1, wx.ID_ANY)
        dmx = wx.ListCtrl(notebook_1_pane_1, wx.ID_ANY, 
                                    style=wx.LC_REPORT | 
                                    wx.SUNKEN_BORDER
                                    )
        notebook_1_pane_2 = wx.Panel(notebook_1, wx.ID_ANY)
        mx = wx.ListCtrl(notebook_1_pane_2, wx.ID_ANY, 
                                     style=wx.LC_REPORT | 
                                     wx.SUNKEN_BORDER
                                     )
        notebook_1_pane_3 = wx.Panel(notebook_1, wx.ID_ANY)
        dmx_mx = wx.ListCtrl(notebook_1_pane_3, wx.ID_ANY, 
                                       style=wx.LC_REPORT | 
                                       wx.SUNKEN_BORDER
                                       )
        #button_help = wx.Button(self, wx.ID_HELP, "")
        button_close = wx.Button(self, wx.ID_CLOSE, "")
        
        #----------------------Properties----------------------#
        self.SetTitle(_("Videomass: FFmpeg file formats"))
        dmx.SetMinSize((500, 400))
        dmx.InsertColumn(0, _('format'), width=150)
        dmx.InsertColumn(1, _('description'), width=450)
        #dmx.SetBackgroundColour(wx.Colour(217, 255, 255))
        mx.SetMinSize((500, 400))
        mx.InsertColumn(0, _('format'), width=150)
        mx.InsertColumn(1, _('description'), width=450)
        #mx.SetBackgroundColour(wx.Colour(217, 255, 255))
        dmx_mx.SetMinSize((500, 400))
        dmx_mx.InsertColumn(0, _('format'), width=150)
        dmx_mx.InsertColumn(1, _('description'), width=450)
        #dmx_mx.SetBackgroundColour(wx.Colour(217, 255, 255))
        
        if OS == 'Darwin':
            dmx.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
            mx.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
            dmx_mx.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
        else:
            dmx.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            mx.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            dmx_mx.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        
        #----------------------Layout--------------------------#
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(2, 1, 0, 0)
        grid_buttons = wx.FlexGridSizer(1, 1, 0, 0)
        sizer_tab3 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab2 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab1 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab1.Add(dmx, 1, wx.ALL | wx.EXPAND, 5)
        notebook_1_pane_1.SetSizer(sizer_tab1)
        sizer_tab2.Add(mx, 1, wx.ALL | wx.EXPAND, 5)
        notebook_1_pane_2.SetSizer(sizer_tab2)
        sizer_tab3.Add(dmx_mx, 1, wx.ALL | wx.EXPAND, 5)
        notebook_1_pane_3.SetSizer(sizer_tab3)
        notebook_1.AddPage(notebook_1_pane_1, (_("Demuxing only")))
        notebook_1.AddPage(notebook_1_pane_2, (_("Muxing only")))
        notebook_1.AddPage(notebook_1_pane_3, (_("Demuxing/Muxing support")))
        grid_sizer_1.Add(notebook_1, 1, wx.ALL|wx.EXPAND, 5)
        grid_buttons.Add(button_close, 0, wx.ALL, 5)
        grid_sizer_1.Add(grid_buttons, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=0)

        sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        
        # delete previous append:
        dmx.DeleteAllItems()
        mx.DeleteAllItems()
        dmx_mx.DeleteAllItems()
            
        #### populate dmx listctrl output:
        index = 0 
        l = dict_formats['Demuxing Supported']
        
        if not l:
            print ('No ffmpeg formats available')
        else:
            dmx.InsertItem(index, ('----'))
            dmx.SetItemBackgroundColour(index, "CORAL")
            for a in l:
                s = " ".join(a.split()).split(None,1)
                if len(s) == 1:
                    key, value = s[0],''
                else:
                    key , value = s[0], s[1]
                index +=1
                dmx.InsertItem(index, key)
                dmx.SetItem(index, 1, value)
                
        #### populate mx listctrl output:
        index = 0
        l = dict_formats['Muxing Supported']
        
        if not l:
            print ('No ffmpeg formats available')
        else:
            mx.InsertItem(index, ('----'))
            mx.SetItemBackgroundColour(index, "CORAL")
            for a in l:
                s = " ".join(a.split()).split(None,1)
                if len(s) == 1:
                    key, value = s[0],''
                else:
                    key , value = s[0], s[1]
                index +=1
                mx.InsertItem(index, key)
                mx.SetItem(index, 1, value)
        
        ##### populate dmx_mx listctrl output:
        index = 0 
        l = dict_formats["Mux/Demux Supported"]
        
        if not l:
            print ('No ffmpeg formats available')
        else:
            dmx_mx.InsertItem(index, ('----'))
            dmx_mx.SetItemBackgroundColour(index, "CORAL")
            for a in l:
                s = " ".join(a.split()).split(None,1)
                if len(s) == 1:
                    key, value = s[0],''
                else:
                    key , value = s[0], s[1]
                index +=1
                dmx_mx.InsertItem(index, key)
                dmx_mx.SetItem(index, 1, value)
                    
        #----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close) # controlla la chiusura (x)
        #self.Bind(wx.EVT_BUTTON, self.on_help, button_help)

    #----------------------Event handler (callback)----------------------#
    def on_close(self, event):
        self.Destroy()
        #event.Skip()

    #-------------------------------------------------------------------#
