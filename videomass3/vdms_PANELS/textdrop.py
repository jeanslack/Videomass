# -*- coding: UTF-8 -*-

#########################################################
# Name: dragNdrop.py
# Porpose: drag n drop interface
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

azure = '#d9ffff' # rgb form (wx.Colour(217,255,255))
red = '#ea312d'
yellow = '#a29500'
greenolive = '#6aaf23'
orange = '#f28924'


########################################################################

#class TextDrop(wx.TextDropTarget):
 
    ##----------------------------------------------------------------------
    #def __init__(self, textctrl):
        #wx.TextDropTarget.__init__(self)
        #self.textctrl = textctrl
 
    ##----------------------------------------------------------------------
    #def OnDropText(self, x, y, text):
        ##self.textctrl.WriteText("(%d, %d)\n%s\n" % (x, y, text))
        #self.textctrl.WriteText(text)
        #return True
    ##----------------------------------------------------------------------
    #def OnDragOver(self, x, y, d):
        ##print(x,y,d)
        #return wx.DragCopy

class TextDnD(wx.Panel):
    """
    Accept one or more urls.
    """
    def __init__(self, parent, go_icn):  
        """Constructor. This will initiate with an id and a title"""
        wx.Panel.__init__(self, parent=parent)
        self.parent = parent # parent is the MainFrame
        self.file_dest = dirname # path name files destination
        #This builds the list control box:
        
        self.textCtrl = wx.TextCtrl(self, wx.ID_ANY, "", 
                                   style=wx.TE_MULTILINE| wx.TE_DONTWRAP)
        
        #self.textCtrl = wx.TextCtrl(self, style=wx.TE_MULTILINE| wx.TE_DONTWRAP)
        #text_drop_target = TextDrop(self.textCtrl)
        #self.textCtrl.SetDropTarget(text_drop_target)

        # create widgets
        btn_clear = wx.Button(self, wx.ID_CLEAR, "")
        self.btn_save = wx.Button(self, wx.ID_OPEN, "...", size=(-1,-1))
        self.text_path_save = wx.TextCtrl(self, wx.ID_ANY, "", 
                                                style=wx.TE_PROCESS_ENTER| 
                                                      wx.TE_READONLY
                                                      )
        self.btn_go = wx.Button(self, wx.ID_ANY, "GO!", size=(-1,-1))
        self.btn_go.SetBitmap(wx.Bitmap(go_icn),wx.LEFT)
        self.lbl = wx.StaticText(self, label=_("Enter one or more URLs below"))

        # create sizers layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.btn_go, 0, wx.ALL|
                                 wx.ALIGN_CENTER_HORIZONTAL|
                                 wx.ALIGN_CENTER_VERTICAL, 5
                                 )
        sizer.Add(self.lbl, 0, wx.ALL|
                          wx.ALIGN_CENTER_HORIZONTAL|
                          wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.textCtrl, 1, wx.EXPAND|wx.ALL, 5)
        grid = wx.FlexGridSizer(1, 5, 0, 0)
        sizer.Add(grid)
        grid.Add(btn_clear, 1, wx.ALL|
                               wx.ALIGN_CENTER_HORIZONTAL|
                               wx.ALIGN_CENTER_VERTICAL, 5
                               )
        grid.Add(self.btn_save, 1, wx.ALL|
                                   wx.ALIGN_CENTER_HORIZONTAL|
                                   wx.ALIGN_CENTER_VERTICAL, 5
                                   )
        grid.Add(self.text_path_save, 1, wx.ALL|wx.EXPAND, 5)
        self.text_path_save.SetMinSize((290, -1)) 
        self.SetSizer(sizer)
        
        self.Bind(wx.EVT_BUTTON, self.deleteAll, btn_clear)
        self.Bind(wx.EVT_BUTTON, self.topic_Redirect, self.btn_go)
        #self.Bind(wx.EVT_CHAR, self.on_Drop, self.textCtrl)
        
        self.text_path_save.SetValue(self.file_dest)
        
    #----------------------------------------------------------------------
    def on_Drop(self, event):
        print(self.textCtrl.GetValue())
        
        if event.GetKeyCode() == 13:
            self.control.WriteText('\n>>>')
        else:
            event.Skip()
        #self.textCtrl.WriteText("n")
        #self.text.WriteText("\n%s\n" % text)
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
    def which(self):
        """
        return topic name by choose_topic.py selection 
    
        """
        #self.lbl.SetLabel('Drag one or more Video files here')
        return self.parent.topicname
    #----------------------------------------------------------------------
    def deleteAll(self, event):
        """
        Delete and clear all text lines of the TxtCtrl

        """
        self.textCtrl.SetValue('')
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
    def same_filedest(self):
        """
        Save destination as files sources 
        """
        if self.ckbx_dir.GetValue() is True:
            self.file_dest = 'same dest'
            self.text_path_save.Disable(), self.btn_save.Disable()
            self.parent.file_save.Enable(False)
            
        elif self.ckbx_dir.GetValue() is False:
            self.file_dest = self.text_path_save.GetValue()
            self.text_path_save.Enable(), self.btn_save.Enable()
            self.parent.file_save.Enable(True)
    #----------------------------------------------------------------------
    
    def statusbar_msg(self, mess, color):
        """
        Set a status bar message of the parent method.
        """
        self.parent.statusbar_msg('%s' % mess, color)
 
