# -*- coding: UTF-8 -*-

#########################################################
# Name: palette.py
# Porpose: show a table with shortcut while playing
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

# Rev (01) October 13 2018
#########################################################

import wx

class Shortcut_Playing(wx.Dialog):
    """
    Class for show epilogue dialog before run process (if all ok 
    (validations?)). It not return usable values.
    """
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        
        panel = wx.Panel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        labeltitle = wx.StaticText(self, wx.ID_ANY, "Shortcut while playing")
        label1 = wx.StaticText(panel, wx.ID_ANY, "| q, ESC (Quit) |")
        label2 = wx.StaticText(panel, wx.ID_ANY, "| f, Toggle full screen. |")
        label3 = wx.StaticText(panel, wx.ID_ANY, "| p, SPC Pause. |")
        label4 = wx.StaticText(panel, wx.ID_ANY, "| m, Toggle mute. |")
        label5 = wx.StaticText(panel, wx.ID_ANY, "| 9, 0 \nDecrease and "
                                            " increase volume respectively. |")
        label6 = wx.StaticText(panel, wx.ID_ANY, "| /, * \nDecrease and increase "
                                               "volume respectively. |")
        self.button_1 = wx.Button(self, wx.ID_CANCEL, "")
        self.button_2 = wx.Button(self, wx.ID_OK, "")
        
        #----------------------Properties----------------------#
        self.SetTitle("While Playing - Videomass2")
        label2.SetForegroundColour(wx.Colour(255, 106, 249))
        panel.SetBackgroundColour(wx.Colour(212, 255, 249))
        
        #---------------------- Layout ----------------------#
        s1 = wx.BoxSizer(wx.VERTICAL)
        gr_t = wx.FlexGridSizer(1, 1, 0, 0)
        gr_t.Add(labeltitle, 0, wx.ALL, 5)
        gr_s1 = wx.FlexGridSizer(3, 2, 0, 0)
        gr_s1.Add(label1, 0, wx.ALL, 5)
        gr_s1.Add(label2, 0, wx.ALL, 5)
        gr_s1.Add(label3, 0, wx.ALL, 5)
        gr_s1.Add(label4, 0, wx.ALL, 5)
        gr_s1.Add(label5, 0, wx.ALL, 5)
        gr_s1.Add(label6, 0, wx.ALL, 5)
        
        btngrid = wx.FlexGridSizer(1,2,0,0)
        btngrid.Add(self.button_1, 0, wx.ALL, 5)
        btngrid.Add(self.button_2, 0, wx.ALL, 5)
        panel.SetSizer(gr_s1)#
        s1.Add(gr_t, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        s1.Add(panel, 1, wx.ALL, 10)
        s1.Add(btngrid, flag=wx.ALL|wx.ALIGN_RIGHT|wx.RIGHT, border=10)
        self.SetSizer(s1)
        s1.Fit(self)
        self.Layout()
        
        #----------------------Binders (EVT)--------------------#
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.button_2)
        
        #----------------------Event handler (callback)----------------------#
    def on_cancel(self, event):  
        #self.Destroy()
        event.Skip()
        
    def on_ok(self, event):  
        #self.Destroy()
        event.Skip()
# end of class MyDialog
if __name__ == "__main__":

	app = wx.App()
	dialog_1 = Shortcut_Playing(None)
	dialog_1.Show()
	app.MainLoop()
