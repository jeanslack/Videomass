# -*- coding: UTF-8 -*-

#########################################################
# Name: ffmpeg_decoders.py
# Porpose: Dialog to show the available decoders on the FFmpeg
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Aug.19 2019
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

class FFmpeg_Codecs(wx.Dialog):
    """
    It shows a dialog box with a pretty kind of GUI to view 
    the formats available on FFmpeg
    
    """
    def __init__(self, dict_decoders, OS, type_opt):
        """
        with 'None' not depend from parent:
        wx.Dialog.__init__(self, None, style=wx.DEFAULT_DIALOG_STYLE)
        
        With parent, -1:
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        if close videomass also close parent window:
        
        """
        if type_opt == '-encoders':
            cod =  _('CODING ABILITY')
            colctrl = 'ORANGE'
            title = _("Videomass: FFmpeg encoders")
        else:
            cod =  _('DECODING CAPABILITY')
            colctrl = 'SIENNA'
            title = _("Videomass: FFmpeg decoders")
            
        wx.Dialog.__init__(self, None, style=wx.DEFAULT_DIALOG_STYLE)
        notebook_1 = wx.Notebook(self, wx.ID_ANY,)
        notebook_1_pane_1 = wx.Panel(notebook_1, wx.ID_ANY)
        vid = wx.ListCtrl(notebook_1_pane_1, wx.ID_ANY, 
                                    style=wx.LC_REPORT | 
                                    wx.SUNKEN_BORDER
                                    )
        notebook_1_pane_2 = wx.Panel(notebook_1, wx.ID_ANY)
        aud = wx.ListCtrl(notebook_1_pane_2, wx.ID_ANY, 
                                     style=wx.LC_REPORT | 
                                     wx.SUNKEN_BORDER
                                     )
        notebook_1_pane_3 = wx.Panel(notebook_1, wx.ID_ANY)
        sub = wx.ListCtrl(notebook_1_pane_3, wx.ID_ANY, 
                                       style=wx.LC_REPORT | 
                                       wx.SUNKEN_BORDER
                                       )
        stext = wx.StaticText(self, wx.ID_ANY, "")
        #button_help = wx.Button(self, wx.ID_HELP, "")
        button_close = wx.Button(self, wx.ID_CLOSE, "")
        
        #----------------------Properties----------------------#
        self.SetTitle(title)
        vid.SetMinSize((600, 300))
        vid.InsertColumn(0, ('codec'), width=150)
        vid.InsertColumn(1, ('F'), width=40)
        vid.InsertColumn(2, ('S'), width=40)
        vid.InsertColumn(3, ('X'), width=40)
        vid.InsertColumn(4, ('B'), width=40)
        vid.InsertColumn(5, ('D'), width=40)
        vid.InsertColumn(6, _('description'), width=450)
        #vid.SetBackgroundColour(wx.Colour(217, 255, 255))
        aud.SetMinSize((600, 300))
        aud.InsertColumn(0, ('codec'), width=150)
        aud.InsertColumn(1, ('F'), width=40)
        aud.InsertColumn(2, ('S'), width=40)
        aud.InsertColumn(3, ('X'), width=40)
        aud.InsertColumn(4, ('B'), width=40)
        aud.InsertColumn(5, ('D'), width=40)
        aud.InsertColumn(6, _('description'), width=450)
        #aud.SetBackgroundColour(wx.Colour(217, 255, 255))
        sub.SetMinSize((600, 300))
        sub.InsertColumn(0, ('codec'), width=150)
        sub.InsertColumn(1, ('F'), width=40)
        sub.InsertColumn(2, ('S'), width=40)
        sub.InsertColumn(3, ('X'), width=40)
        sub.InsertColumn(4, ('B'), width=40)
        sub.InsertColumn(5, ('D'), width=40)
        sub.InsertColumn(6, _('description'), width=450)
        #sub.SetBackgroundColour(wx.Colour(217, 255, 255))
        
        if OS == 'Darwin':
            vid.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
            aud.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
            sub.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
            stext.SetFont(wx.Font(11, wx.SWISS, wx.ITALIC, wx.NORMAL))
        else:
            vid.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            aud.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            sub.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            stext.SetFont(wx.Font(8, wx.SWISS, wx.ITALIC, wx.NORMAL))
        
        leg = ("F = frame-level multithreading\n"
               "S = slice-level multithreading\n"
               "X = Codec is experimental\n"
               "B = Supports draw_horiz_band\n"
               "D = Supports direct rendering method 1")
        stext.SetLabel(leg)
        
        #----------------------Layout--------------------------#
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(2, 1, 0, 0)
        grid_buttons = wx.FlexGridSizer(1, 1, 0, 0)
        sizer_tab3 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab2 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab1 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab1.Add(vid, 1, wx.ALL | wx.EXPAND, 5)
        notebook_1_pane_1.SetSizer(sizer_tab1)
        sizer_tab2.Add(aud, 1, wx.ALL | wx.EXPAND, 5)
        notebook_1_pane_2.SetSizer(sizer_tab2)
        sizer_tab3.Add(sub, 1, wx.ALL | wx.EXPAND, 5)
        notebook_1_pane_3.SetSizer(sizer_tab3)
        notebook_1.AddPage(notebook_1_pane_1, (_("Video")))
        notebook_1.AddPage(notebook_1_pane_2, (_("Audio")))
        notebook_1.AddPage(notebook_1_pane_3, (_("Subtitle")))
        grid_sizer_1.Add(notebook_1, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_1.Add(stext, 1, wx.ALL, 5)
        grid_buttons.Add(button_close, 0, wx.ALL, 5)
        sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        sizer_1.Add(grid_buttons, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=0)

        self.SetSizerAndFit(sizer_1)
        
        #### populate vid listctrl output:
        index = 0 
        l = dict_decoders['Video']
        if not l:
            print ('No ffmpeg codecs available')
        else:
            vid.InsertItem(index, cod)
            vid.SetItemBackgroundColour(index, colctrl)
            for a in l:
                index+=1
                vid.InsertItem(index, a[6:].split(' ')[1])
                if 'F' in a[1]:
                    vid.SetItem(index, 1, 'YES')
                if 'S' in a[2]:
                    vid.SetItem(index, 2, 'YES')
                if 'X' in a[3]:
                    vid.SetItem(index, 3, 'YES')
                if 'B' in [4]:
                    vid.SetItem(index, 4, 'YES')
                if 'D' in [5]:
                    vid.SetItem(index, 5, 'YES')
                d = " ".join(a.split()).split(None,2)[2]
                if len(d):
                    vid.SetItem(index, 6, d)
                else:
                    vid.SetItem(index, 6, '')
                
        ##### populate aud listctrl output:
        index = 0 
        l = dict_decoders['Audio']
        if not l:
            print ('No ffmpeg codecs available')
        else:
            aud.InsertItem(index, cod)
            aud.SetItemBackgroundColour(index, colctrl)
            for a in l:
                index+=1
                aud.InsertItem(index, a[6:].split(' ')[1])
                if 'F' in a[1]:
                    aud.SetItem(index, 1, 'YES')
                if 'S' in a[2]:
                    aud.SetItem(index, 2, 'YES')
                if 'X' in a[3]:
                    aud.SetItem(index, 3, 'YES')
                if 'B' in [4]:
                    aud.SetItem(index, 4, 'YES')
                if 'D' in [5]:
                    aud.SetItem(index, 5, 'YES')
                d = " ".join(a.split()).split(None,2)[2]
                if len(d):
                    aud.SetItem(index, 6, d)
                else:
                    aud.SetItem(index, 6, '')
        
        ###### populate sub listctrl output:
        index = 0 
        l = dict_decoders['Subtitle']
        if not l:
            print('No ffmpeg codecs available')
        else:
            sub.InsertItem(index, cod)
            sub.SetItemBackgroundColour(index, colctrl)
            for a in l:
                index+=1
                sub.InsertItem(index, a[6:].split(' ')[1])
                if 'F' in a[1]:
                    sub.SetItem(index, 1, 'YES')
                if 'S' in a[2]:
                    sub.SetItem(index, 2, 'YES')
                if 'X' in a[3]:
                    sub.SetItem(index, 3, 'YES')
                if 'B' in [4]:
                    sub.SetItem(index, 4, 'YES')
                if 'D' in [5]:
                    sub.SetItem(index, 5, 'YES')
                d = " ".join(a.split()).split(None,2)[2]
                if len(d):
                    sub.SetItem(index, 6, d)
                else:
                    sub.SetItem(index, 6, '')
                    
        #----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close) # controlla la chiusura (x)
        #self.Bind(wx.EVT_BUTTON, self.on_help, button_help)

    #----------------------Event handler (callback)----------------------#
    def on_close(self, event):
        self.Destroy()
        #event.Skip()

    #-------------------------------------------------------------------# 
