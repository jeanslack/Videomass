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
data_files = []

azure = '#d9ffff' # rgb form (wx.Colour(217,255,255))
red = '#ea312d'
yellow = '#a29500'
greenolive = '#6aaf23'
orange = '#f28924'


########################################################################

class MyTextDropTarget(wx.TextDropTarget):
 
    #----------------------------------------------------------------------
    def __init__(self, textctrl):
        wx.TextDropTarget.__init__(self)
        self.textctrl = textctrl
 
    #----------------------------------------------------------------------
    def OnDropText(self, x, y, text):
        #self.textctrl.WriteText("(%d, %d)\n%s\n" % (x, y, text))
        self.textctrl.WriteText(text)
        return True
    #----------------------------------------------------------------------
    def OnDragOver(self, x, y, d):
        print(x,y,d)
        return wx.DragCopy

class TextDnD(wx.Panel):
    """
    Panel for dragNdrop files queue. Accept one or more files.
    """
    def __init__(self, parent, go_icn):  
        """Constructor. This will initiate with an id and a title"""
        wx.Panel.__init__(self, parent=parent)
        self.parent = parent # parent is the MainFrame
        self.file_dest = dirname # path name files destination
        self.selected = None # tells if an imported file is selected or not
        #This builds the list control box:
        
        self.myTextCtrl = wx.TextCtrl(self, style=wx.TE_MULTILINE| wx.TE_DONTWRAP)
        text_drop_target = MyTextDropTarget(self.myTextCtrl)
        self.myTextCtrl.SetDropTarget(text_drop_target)

        # create widgets
        btn_clear = wx.Button(self, wx.ID_CLEAR, "")
        self.ckbx_dir = wx.CheckBox(self, wx.ID_ANY, (
                                _("Save destination in source folder")))
        self.btn_save = wx.Button(self, wx.ID_OPEN, "...", size=(-1,-1))
        self.text_path_save = wx.TextCtrl(self, wx.ID_ANY, "", 
                                                style=wx.TE_PROCESS_ENTER| 
                                                      wx.TE_READONLY
                                                      )
        self.btn_go = wx.Button(self, wx.ID_ANY, "GO!", size=(-1,-1))
        self.btn_go.SetBitmap(wx.Bitmap(go_icn),wx.LEFT)
        self.lbl = wx.StaticText(self, label=_("Enter one or more URLs here:"))

        # create sizers layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(1, 5, 0, 0)
        sizer.Add(self.lbl, 0, wx.ALL|
                          wx.ALIGN_CENTER_HORIZONTAL|
                          wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(self.myTextCtrl, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(grid)
        grid.Add(btn_clear, 1, wx.ALL|
                               wx.ALIGN_CENTER_HORIZONTAL|
                               wx.ALIGN_CENTER_VERTICAL, 5
                               )
        grid.Add(self.ckbx_dir, 1, wx.ALL|
                                   wx.ALIGN_CENTER_HORIZONTAL|
                                   wx.ALIGN_CENTER_VERTICAL, 5
                                   )
        grid.Add(self.btn_save, 1, wx.ALL|
                                   wx.ALIGN_CENTER_HORIZONTAL|
                                   wx.ALIGN_CENTER_VERTICAL, 5
                                   )
        grid.Add(self.text_path_save, 1, wx.ALL|wx.EXPAND, 5)
        self.text_path_save.SetMinSize((290, -1)) 
        grid.Add(self.btn_go, 1, wx.ALL|
                                 wx.ALIGN_CENTER_HORIZONTAL|
                                 wx.ALIGN_CENTER_VERTICAL, 5
                                 )
        self.SetSizer(sizer)
        
        self.Bind(wx.EVT_BUTTON, self.deleteAll, btn_clear)
        #self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.flCtrl)
        #self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect, self.flCtrl)
        #self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_doubleClick, self.flCtrl)
        #self.Bind(wx.EVT_CONTEXT_MENU, self.onContext)
        #self.Bind(wx.EVT_CHECKBOX, self.same_filedest, self.ckbx_dir)
        self.Bind(wx.EVT_BUTTON, self.topic_Redirect, self.btn_go)
        
        self.text_path_save.SetValue(self.file_dest)
        
    #----------------------------------------------------------------------
    def WriteText(self, text):
        self.text.WriteText("\n%s\n" % text)
        #self.text.WriteText("\n%s\n" % text)
        
    
    #----------------------------------------------------------------------
    def topic_Redirect(self, event):
        """
        Redirects to specific panel
        """
        if not self.myTextCtrl.GetValue():
            wx.MessageBox(_('Append at least one URL'), "Videomass", 
                             wx.ICON_INFORMATION, self)
            return
        else:
            data = (self.myTextCtrl.GetValue().split())
            self.parent.topic_Redirect(data)
    #----------------------------------------------------------------------
    def which(self):
        """
        return topic name by choose_topic.py selection 
    
        """
        #self.lbl.SetLabel('Drag one or more Video files here')
        return self.parent.topicname
    #----------------------------------------------------------------------
    def onContext(self, event):
        """
        Create and show a Context Menu
        """
        # only do this part the first time so the events are only bound once 
        if not hasattr(self, "popupID1"):
            self.itemThreeId = wx.NewId()
            self.Bind(wx.EVT_MENU, self.onPopup, id=self.itemThreeId)
        # build the menu
        menu = wx.Menu()
        itemThree = menu.Append(self.itemThreeId, _("Remove the selected file"))
        # show the popup menu
        self.PopupMenu(menu)
        menu.Destroy()
    #----------------------------------------------------------------------
    def onPopup(self, event):
        """
        Evaluate the label string of the menu item selected and starts
        the related process
        """
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)
        
        if not self.selected:
            self.parent.statusbar_msg(_('No file selected to `%s` yet') % 
                                      menuItem.GetLabel(), yellow)
        else:
            self.parent.statusbar_msg('Add Files', None)
                
            if menuItem.GetLabel() == _("Remove the selected file"):
                if self.flCtrl.GetItemCount() == 1:
                    self.deleteAll(self)
                else:
                    item = self.flCtrl.GetFocusedItem()
                    self.flCtrl.DeleteItem(item)
                    self.selected = None
                    data_files.pop(item)

    #----------------------------------------------------------------------
    def deleteAll(self, event):
        """
        Delete and clear all text lines of the TxtCtrl,
        reset the fileList[], disable Toolbar button and menu bar
        Stream/play select imported file - Stream/display imported...
        """
        #self.flCtrl.ClearAll()
        self.myTextCtrl.SetValue('')
        del data_files[:]
        self.selected = None
    #----------------------------------------------------------------------
    def on_select(self, event):
        """
        Selecting a line with mouse or up/down keyboard buttons
        """
        index = self.flCtrl.GetFocusedItem()
        item = self.flCtrl.GetItemText(index)
        self.selected = item
        
    #----------------------------------------------------------------------
    def on_doubleClick(self, row):
        """
        Double click or keyboard enter button, open media info
        """
        self.onContext(self)
        #self.parent.ImportInfo(self)
    #----------------------------------------------------------------------
    def on_deselect(self, event):
        """
        De-selecting a line with mouse by click in empty space of
        the control list
        """
        self.selected = None
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
 
