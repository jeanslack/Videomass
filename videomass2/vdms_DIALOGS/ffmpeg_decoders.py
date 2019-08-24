# -*- coding: UTF-8 -*-

#########################################################
# Name: ffmpeg_decoders.py
# Porpose: Dialog to show the available decoders on the FFmpeg
# Compatibility: Python2, wxPython3 CLASSIC
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

class FFmpeg_decoders(wx.Dialog):
    """
    It shows a dialog box with a pretty kind of GUI to view 
    the formats available on FFmpeg
    
    """
    def __init__(self, dict_decoders):
        """
        with 'None' not depend from parent:
        wx.Dialog.__init__(self, None, style=wx.DEFAULT_DIALOG_STYLE)
        
        With parent, -1:
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        if close videomass also close parent window:
        
        """
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
        self.SetTitle(_("Videomass: FFmpeg decoders"))
        vid.SetMinSize((500, 300))
        vid.InsertColumn(0, ('codec'), width=150)
        vid.InsertColumn(1, ('F'), width=40)
        vid.InsertColumn(2, ('S'), width=40)
        vid.InsertColumn(3, ('X'), width=40)
        vid.InsertColumn(4, ('B'), width=40)
        vid.InsertColumn(5, ('D'), width=40)
        vid.InsertColumn(6, _('description'), width=450)
        #vid.SetBackgroundColour(wx.Colour(217, 255, 255))
        aud.SetMinSize((500, 300))
        aud.InsertColumn(0, ('codec'), width=150)
        aud.InsertColumn(1, ('F'), width=40)
        aud.InsertColumn(2, ('S'), width=40)
        aud.InsertColumn(3, ('X'), width=40)
        aud.InsertColumn(4, ('B'), width=40)
        aud.InsertColumn(5, ('D'), width=40)
        aud.InsertColumn(6, _('description'), width=450)
        #aud.SetBackgroundColour(wx.Colour(217, 255, 255))
        sub.SetMinSize((500, 300))
        sub.InsertColumn(0, ('codec'), width=150)
        sub.InsertColumn(1, ('F'), width=40)
        sub.InsertColumn(2, ('S'), width=40)
        sub.InsertColumn(3, ('X'), width=40)
        sub.InsertColumn(4, ('B'), width=40)
        sub.InsertColumn(5, ('D'), width=40)
        sub.InsertColumn(6, _('description'), width=450)
        #sub.SetBackgroundColour(wx.Colour(217, 255, 255))
        
        #----------------------Layout--------------------------#
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(3, 1, 0, 0)
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
        grid_sizer_1.Add(grid_buttons, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=0)

        sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        leg = ("F = frame-level multithreading\n"
               "S = slice-level multithreading\n"
               "X = Codec is experimental\n"
               "B = Supports draw_horiz_band\n"
               "D = Supports direct rendering method 1")
        stext.SetFont(wx.Font(8, wx.SWISS, wx.ITALIC, wx.NORMAL))
        stext.SetLabel(leg)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        
        #### populate vid listctrl output:
        index = 0 
        l = dict_decoders['Video']
        if not l:
            print ('No ffmpeg codecs available')
        else:
            vid.InsertStringItem(index, _('DECODING CAPABILITY'))
            vid.SetItemBackgroundColour(index, "SIENNA")
            for a in l:
                index+=1
                vid.InsertStringItem(index, a[6:].split(' ')[1])
                if 'F' in a[1]:
                    vid.SetStringItem(index, 1, 'YES')
                if 'S' in a[2]:
                    vid.SetStringItem(index, 2, 'YES')
                if 'X' in a[3]:
                    vid.SetStringItem(index, 3, 'YES')
                if 'B' in [4]:
                    vid.SetStringItem(index, 4, 'YES')
                if 'D' in [5]:
                    vid.SetStringItem(index, 5, 'YES')
                d = " ".join(a.split()).split(None,2)[2]
                if len(d):
                    vid.SetStringItem(index, 6, d)
                else:
                    vid.SetStringItem(index, 6, '')
                
        ##### populate aud listctrl output:
        index = 0 
        l = dict_decoders['Audio']
        if not l:
            print ('No ffmpeg codecs available')
        else:
            aud.InsertStringItem(index, _('DECODING CAPABILITY'))
            aud.SetItemBackgroundColour(index, "SIENNA")
            for a in l:
                index+=1
                aud.InsertStringItem(index, a[6:].split(' ')[1])
                if 'F' in a[1]:
                    aud.SetStringItem(index, 1, 'YES')
                if 'S' in a[2]:
                    aud.SetStringItem(index, 2, 'YES')
                if 'X' in a[3]:
                    aud.SetStringItem(index, 3, 'YES')
                if 'B' in [4]:
                    aud.SetStringItem(index, 4, 'YES')
                if 'D' in [5]:
                    aud.SetStringItem(index, 5, 'YES')
                d = " ".join(a.split()).split(None,2)[2]
                if len(d):
                    aud.SetStringItem(index, 6, d)
                else:
                    aud.SetStringItem(index, 6, '')
        
        ###### populate sub listctrl output:
        index = 0 
        l = dict_decoders['Subtitle']
        if not l:
            print ('No ffmpeg codecs available')
        else:
            sub.InsertStringItem(index, _('DECODING CAPABILITY'))
            sub.SetItemBackgroundColour(index, "SIENNA")
            for a in l:
                index+=1
                sub.InsertStringItem(index, a[6:].split(' ')[1])
                if 'F' in a[1]:
                    sub.SetStringItem(index, 1, 'YES')
                if 'S' in a[2]:
                    sub.SetStringItem(index, 2, 'YES')
                if 'X' in a[3]:
                    sub.SetStringItem(index, 3, 'YES')
                if 'B' in [4]:
                    sub.SetStringItem(index, 4, 'YES')
                if 'D' in [5]:
                    sub.SetStringItem(index, 5, 'YES')
                d = " ".join(a.split()).split(None,2)[2]
                if len(d):
                    sub.SetStringItem(index, 6, d)
                else:
                    sub.SetStringItem(index, 6, '')
                    
        #----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close) # controlla la chiusura (x)
        #self.Bind(wx.EVT_BUTTON, self.on_help, button_help)

    #----------------------Event handler (callback)----------------------#
    def on_close(self, event):
        self.Destroy()
        #event.Skip()

    #-------------------------------------------------------------------# 