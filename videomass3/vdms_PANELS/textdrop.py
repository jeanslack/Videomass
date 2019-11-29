# -*- coding: UTF-8 -*-

#########################################################
# Name: textNdrop.py
# Porpose: Allows you to add URLs to download media
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Dec.28.2018, Sept.12.2019
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

dirname = os.path.expanduser('~') # /home/user/
# path to the configuration directory:
get = wx.GetApp()
userpath = get.userpath

azure = '#d9ffff' # rgb form (wx.Colour(217,255,255))
red = '#ea312d'
yellow = '#a29500'
greenolive = '#6aaf23'
orange = '#f28924'

data_files = []

########################################################################
class TextDnD(wx.Panel):
    """
    Accept one or more urls separated by a white space or newline.
    
    """
    def __init__(self, parent, forward_icn, back_icn):
        """
        """
        self.parent = parent # parent is the MainFrame
        self.file_dest = dirname if not userpath else userpath
        """Constructor. This will initiate with an id and a title"""
        wx.Panel.__init__(self, parent=parent)
        self.textCtrl = wx.TextCtrl(self, wx.ID_ANY, "", 
                                   style=wx.TE_MULTILINE| wx.TE_DONTWRAP)
        # create widgets
        btn_clear = wx.Button(self, wx.ID_CLEAR, "")
        self.btn_save = wx.Button(self, wx.ID_OPEN, "...", size=(-1,-1))
        self.text_path_save = wx.TextCtrl(self, wx.ID_ANY, "", 
                                                style=wx.TE_PROCESS_ENTER| 
                                                      wx.TE_READONLY
                                                      )
        self.btn_forward = wx.Button(self, wx.ID_ANY, "", size=(-1,-1))
        self.btn_forward.SetBitmap(wx.Bitmap(forward_icn),wx.RIGHT)
        self.btn_back = wx.Button(self, wx.ID_ANY, "", size=(-1,-1))
        self.btn_back.SetBitmap(wx.Bitmap(back_icn),wx.LEFT)
        self.lbl = wx.StaticText(self, label=_("Enter one or more URLs below"))
        # create sizers layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizerdir = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizerdir, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        sizerdir.Add(self.btn_back, 0, wx.ALL|wx.ALIGN_LEFT, 5)
        sizerdir.Add(self.btn_forward, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        sizer.Add(self.lbl, 0, wx.ALL|
                          wx.ALIGN_CENTER_HORIZONTAL|
                          wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.textCtrl, 1, wx.EXPAND|wx.ALL, 5)
        sizer_ctrl = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer_ctrl, 0, wx.ALL|wx.EXPAND, 5)
        sizer_ctrl.Add(btn_clear, 0, wx.ALL|
                               wx.ALIGN_CENTER_HORIZONTAL|
                               wx.ALIGN_CENTER_VERTICAL, 5
                               )
        sizer_ctrl.Add(self.btn_save, 0, wx.ALL|
                                   wx.ALIGN_CENTER_HORIZONTAL|
                                   wx.ALIGN_CENTER_VERTICAL, 5
                                   )
        sizer_ctrl.Add(self.text_path_save, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)
        
        self.Bind(wx.EVT_BUTTON, self.deleteAll, btn_clear)
        self.Bind(wx.EVT_BUTTON, self.topic_Redirect, self.btn_forward)
        
        self.text_path_save.SetValue(self.file_dest)
        
    #----------------------------------------------------------------------
    def topic_Redirect(self, event):
        """
        Redirects to specific panel
        """
        if not self.textCtrl.GetValue():
            wx.MessageBox(_('Append at least one URL'), "Videomass", 
                             wx.ICON_INFORMATION, self)
            return
        else:
            data = (self.textCtrl.GetValue().split())
            self.parent.topic_Redirect(data)
    #----------------------------------------------------------------------

    def deleteAll(self, event):
        """
        Delete and clear all text lines of the TxtCtrl

        """
        self.textCtrl.Clear()
    #----------------------------------------------------------------------
    def on_custom_save(self):
        """
        Choice a specific directory for files save
        """
        dialdir = wx.DirDialog(self, _("Videomass: Choose a directory"))
            
        if dialdir.ShowModal() == wx.ID_OK:
            self.text_path_save.SetValue("")
            self.text_path_save.AppendText(dialdir.GetPath())
            self.file_dest = '%s' % (dialdir.GetPath())
            self.parent.file_destin = self.file_dest
            dialdir.Destroy()
    #----------------------------------------------------------------------
    
    def statusbar_msg(self, mess, color):
        """
        Set a status bar message of the parent method.
        """
        self.parent.statusbar_msg('%s' % mess, color)
 
