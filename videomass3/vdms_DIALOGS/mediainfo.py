# -*- coding: UTF-8 -*-

#########################################################
# Name: mediainfo.py
# Porpose: show media streams information through ffprobe
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev (06) Dec.28 2018, Nov.02 2019
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
import webbrowser
from videomass3.vdms_IO.IO_tools import FFProbe

class Mediainfo(wx.Dialog):
    """
    Show dialog for display streams information from
    ffprobe. 
    """
    def __init__(self, title, path, ffprobe_link, OS):
        # with 'None' not depend from vinc. With 'parent, -1' if close
        # vinc also close mediainfo window:
        #wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        wx.Dialog.__init__(self, None, style=wx.DEFAULT_DIALOG_STYLE)
        
        notebook_1 = wx.Notebook(self, wx.ID_ANY)
        notebook_1_pane_1 = wx.Panel(notebook_1, wx.ID_ANY)
        format_list = wx.ListCtrl(notebook_1_pane_1, wx.ID_ANY,
                                  style=wx.LC_REPORT | wx.SUNKEN_BORDER
                                  )
        notebook_1_pane_2 = wx.Panel(notebook_1, wx.ID_ANY)
        
        video_list = wx.ListCtrl(notebook_1_pane_2, wx.ID_ANY,
                                   style=wx.LC_REPORT | wx.SUNKEN_BORDER
                                   )
        notebook_1_pane_3 = wx.Panel(notebook_1, wx.ID_ANY)
        audio_list = wx.ListCtrl(notebook_1_pane_3, wx.ID_ANY,
                                  style=wx.LC_REPORT | wx.SUNKEN_BORDER
                                  )
        notebook_1_pane_4 = wx.Panel(notebook_1, wx.ID_ANY)
        
        subtitle_list = wx.ListCtrl(notebook_1_pane_4, wx.ID_ANY,
                                   style=wx.LC_REPORT | wx.SUNKEN_BORDER
                                   )
        #button_help = wx.Button(self, wx.ID_HELP, "")
        button_close = wx.Button(self, wx.ID_CLOSE, "")
        
        #----------------------Properties----------------------#
        self.SetTitle(title)
        format_list.SetMinSize((640, 300))
        #format_list.SetBackgroundColour(wx.Colour(217, 255, 255))
        format_list.InsertColumn(0, _('References'), width=200)
        format_list.InsertColumn(1, _('Parameters'), width=450)
        #video_list.SetBackgroundColour(wx.Colour(217, 255, 255))
        video_list.InsertColumn(0, _('References'), width=200)
        video_list.InsertColumn(1, _('Parameters'), width=450)
        #format_list.SetBackgroundColour(wx.Colour(217, 255, 255))
        audio_list.InsertColumn(0, _('References'), width=200)
        audio_list.InsertColumn(1, _('Parameters'), width=450)
        #video_list.SetBackgroundColour(wx.Colour(217, 255, 255))
        subtitle_list.InsertColumn(0, _('References'), width=200)
        subtitle_list.InsertColumn(1, _('Parameters'), width=450)
        if OS == 'Darwin':
            format_list.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
            video_list.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
            audio_list.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
            subtitle_list.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
        else:
            video_list.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            format_list.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            audio_list.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            subtitle_list.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        #----------------------Layout--------------------------#
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(2, 1, 0, 0)
        grid_buttons = wx.FlexGridSizer(1, 1, 0, 0)
        
        sizer_tab1 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab1.Add(format_list, 1, wx.ALL | wx.EXPAND, 5)
        notebook_1_pane_1.SetSizer(sizer_tab1)
        
        sizer_tab2 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab2.Add(video_list, 1, wx.ALL | wx.EXPAND, 5)
        notebook_1_pane_2.SetSizer(sizer_tab2)
        
        sizer_tab3 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab3.Add(audio_list, 1, wx.ALL | wx.EXPAND, 5)
        notebook_1_pane_3.SetSizer(sizer_tab3)
        
        sizer_tab4 = wx.BoxSizer(wx.VERTICAL)
        sizer_tab4.Add(subtitle_list, 1, wx.ALL | wx.EXPAND, 5)
        notebook_1_pane_4.SetSizer(sizer_tab4)
        
        notebook_1.AddPage(notebook_1_pane_1, (_("Format Stream")))
        notebook_1.AddPage(notebook_1_pane_2, (_("Video Stream")))
        notebook_1.AddPage(notebook_1_pane_3, (_("Audio Streams")))
        notebook_1.AddPage(notebook_1_pane_4, (_("Subtitle Streams")))
        grid_sizer_1.Add(notebook_1, 1, wx.ALL|wx.EXPAND, 5)
        grid_buttons.Add(button_close, 0, wx.ALL, 5)
        grid_sizer_1.Add(grid_buttons, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=0)
        sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        
        # delete previous append:
        format_list.DeleteAllItems()
        video_list.DeleteAllItems()
        audio_list.DeleteAllItems()
        subtitle_list.DeleteAllItems()
        
        # create instance FFProbe class:
        metadata = FFProbe(ffprobe_link, path) 
        # check for errors:
        if metadata.ERROR():
            wx.MessageBox("[FFprobe] Error:  %s" % (metadata.error), 
                    "Vinc: FFprobe", wx.ICON_ERROR, self)
            self.Destroy()
            return
        
        # create methods instances:
        format_stream = metadata.data_format()
        video_stream = metadata.video_stream()
        audio_stream = metadata.audio_stream()
        subtitle_stream = metadata.subtitle_stream()
                
        #populate format_list:
        index = 0
        if format_stream == []:
            print ('No FORMAT stream metadata found')
        else:
            n = len(format_stream)
            for a in range(n):
                (key, value) = format_stream[a][0].strip().split('=')
                num_items = format_list.GetItemCount()
                format_list.InsertItem(num_items, 'FORMAT STREAM:')
                format_list.SetItemBackgroundColour(index, "GOLD")
                index +=1
                for b in format_stream[a]:
                    (key, value) = b.strip().split('=',1)
                    format_list.InsertItem(index, key)
                    format_list.SetItem(index, 1, value)
                    index += 1
        
        #populate video_list:
        index = 0 
        if video_stream == []:
            print ('No VIDEO stream metadata found')
        else:
            n = len(video_stream)
            for a in range(n):
                (key, value) = video_stream[a][0].strip().split('=')
                num_items = video_list.GetItemCount()
                video_list.InsertItem(num_items, 
                               'VIDEO STREAM (index %s):' % (value[0]))
                video_list.SetItemBackgroundColour(index, "SLATE BLUE")
                index +=1
                for b in video_stream[a]:
                    (key, value) = b.strip().split('=',1)
                    video_list.InsertItem(index, key)
                    video_list.SetItem(index, 1, value)
                    index += 1
        #populate audio_list:
        index = 0
        if audio_stream == []:
            print ('No AUDIO stream metadata found')
        else:    
            n = len(audio_stream)
            for a in range(n):
                (key, value) = audio_stream[a][0].strip().split('=')
                num_items = audio_list.GetItemCount()
                audio_list.InsertItem(num_items, 
                               'AUDIO STREAM (index %s):' % (value[0]))
                audio_list.SetItemBackgroundColour(index, "GOLDENROD")
                index +=1
                for b in audio_stream[a]:
                    (key, value) = b.strip().split('=',1)
                    audio_list.InsertItem(index, key)
                    audio_list.SetItem(index, 1, value)
                    index += 1
        #populate subtitle_list
        index = 0            
        if subtitle_stream == []:
            print ('No SUBTITLE stream metadata found')
        else:
            n = len(subtitle_stream)
            for a in range(n):
                (key, value) = subtitle_stream[a][0].strip().split('=')
                num_items = subtitle_list.GetItemCount()
                subtitle_list.InsertItem(num_items, 
                            'SUBTITLE STREAM (index %s):' % (value[0]))
                subtitle_list.SetItemBackgroundColour(index, "GREEN")
                index +=1
                for b in subtitle_stream[a]:
                    (key, value) = b.strip().split('=',1)
                    subtitle_list.InsertItem(index, key)
                    subtitle_list.SetItem(index, 1, value)
                    index += 1
                    
        #----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close) # controlla la chiusura (x)
        #self.Bind(wx.EVT_BUTTON, self.on_help, button_help)

    #----------------------Event handler (callback)----------------------#
    def on_close(self, event):
        self.Destroy()
        #event.Skip()

    #-------------------------------------------------------------------#
        
