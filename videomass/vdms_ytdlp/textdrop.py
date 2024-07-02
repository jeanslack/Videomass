# -*- coding: UTF-8 -*-
"""
Name: textdrop.py
Porpose: Allows you to add text URLs
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.23.2024
Code checker: flake8, pylint

This file is part of Videomass.

   Videomass is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   Videomass is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with Videomass.  If not, see <http://www.gnu.org/licenses/>.
"""
from urllib.parse import urlparse
import wx
from videomass.vdms_dialogs.list_warning import ListWarning


class MyListCtrl(wx.ListCtrl):
    """
    This is the listControl widget.
    Note that this wideget has DnDPanel parented.
    """
    def __init__(self, parent):
        """
        Constructor.
        WARNING to avoid segmentation error on removing items by
        listctrl, style must be wx.LC_SINGLE_SEL .
        """
        self.index = None
        self.parent = parent  # parent is DnDPanel class
        self.errors = {}
        wx.ListCtrl.__init__(self,
                             parent,
                             style=wx.LC_REPORT
                             | wx.LC_SINGLE_SEL,
                             )
        self.populate()
    # ----------------------------------------------------------------------#

    def populate(self):
        """
        make default colums
        """
        self.InsertColumn(0, ('#'), width=30)
        self.InsertColumn(1, (_('Url')), width=600)

    def dropUpdate(self, url):
        """
        Update list-control during drag and drop.
        """
        self.index = self.GetItemCount()
        res = urlparse(url)
        if not res[1]:  # if empty netloc given from ParseResult
            self.errors[f'{url}'] = _('Invalid URL')
            return False

        self.InsertItem(self.index, str(self.index + 1))
        self.SetItem(self.index, 1, url)
        self.index += 1

        self.parent.changes_in_progress()
        return True
    # ----------------------------------------------------------------------#

    def rejected_urls(self):
        """
        Handles all rejected URLs if any
        """
        if self.errors:
            with ListWarning(self,
                             self.errors,
                             caption=_('Error list'),
                             header=_('Invalid URLs'),
                             buttons='OK',
                             ) as log:
                log.ShowModal()
            self.errors.clear()  # clear values here


class UrlDropTarget(wx.TextDropTarget):
    """
    This is a Drop target object for handle dragging
    text URL data on a ListCtrl object.
    """
    def __init__(self, parent, listctrl):
        """
        Defining the ListCtrl object attribute
        """
        wx.TextDropTarget.__init__(self)
        self.parent = parent
        self.listctrl = listctrl

    def OnDropText(self, x, y, data):
        """
        Update ListCtrl object by dragging text inside it.
        """
        for url in data.split():
            self.listctrl.dropUpdate(url)
        self.listctrl.rejected_urls()

        return True


class Url_DnD_Panel(wx.Panel):
    """
    Panel responsible to embed URLs controls
    """
    def __init__(self, parent):
        """
        parent is the MainFrame
        """
        get = wx.GetApp()  # get data from bootstrap
        self.appdata = get.appset
        self.parent = parent
        wx.Panel.__init__(self, parent, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((0, 25))
        infomsg = _("Drag or paste URLs here")
        lbl_info = wx.StaticText(self, wx.ID_ANY, label=infomsg)
        sizer.Add(lbl_info, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add((0, 10))
        self.urlctrl = MyListCtrl(self)
        dragt = UrlDropTarget(self, self.urlctrl)
        self.urlctrl.SetDropTarget(dragt)
        sizer.Add(self.urlctrl, 1, wx.EXPAND | wx.ALL, 5)

        sizer_ctrl = wx.BoxSizer(wx.HORIZONTAL)
        lblsave = wx.StaticText(self, wx.ID_ANY, label=_("Save to:"))
        sizer_ctrl.Add(lblsave, 0, wx.LEFT | wx.RIGHT | wx.CENTRE, 2)
        self.text_path_save = wx.TextCtrl(self, wx.ID_ANY, "",
                                          style=wx.TE_PROCESS_ENTER
                                          | wx.TE_READONLY,
                                          )
        sizer_ctrl.Add(self.text_path_save, 1, wx.LEFT
                       | wx.RIGHT
                       | wx.EXPAND, 2,
                       )
        self.btn_save = wx.Button(self, wx.ID_OPEN, _('Change'))
        sizer_ctrl.Add(self.btn_save, 0, wx.LEFT | wx.CENTER, 2)
        sizer.Add(sizer_ctrl, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)

        if self.appdata['ostype'] == 'Darwin':
            lbl_info.SetFont(wx.Font(13, wx.SWISS, wx.NORMAL, wx.BOLD))
            lblsave.SetFont(wx.Font(13, wx.SWISS, wx.NORMAL, wx.BOLD))
        else:
            lbl_info.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            lblsave.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.text_path_save.SetValue(self.appdata['ydlp-outputdir'])
        # ---- Tooltips
        self.btn_save.SetToolTip(_("Set a new destination folder "
                                   "for downloads"))
        self.text_path_save.SetToolTip(_("Destination folder of downloads"))

        # ---------------------- Binding (EVT) ----------------------#
        self.Bind(wx.EVT_CONTEXT_MENU, self.onContext)
    # ---------------------------------------------------------

    def onContext(self, event):
        """
        Create and show a Context Menu
        """
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID1"):
            popupID1 = wx.ID_ANY
            popupID2 = wx.ID_ANY
            popupID3 = wx.ID_ANY
            self.Bind(wx.EVT_MENU, self.onPopup, id=popupID1)
            self.Bind(wx.EVT_MENU, self.onPopup, id=popupID2)
            self.Bind(wx.EVT_MENU, self.onPopup, id=popupID3)
        # build the menu
        menu = wx.Menu()
        menu.Append(popupID2, _("Paste\tCtrl+V"))
        menu.Append(popupID1, _("Remove selected URL\tDEL"))
        menu.Append(popupID3, _("Clear list\tShift+DEL"))
        # show the popup menu
        self.PopupMenu(menu)
        menu.Destroy()
    # ----------------------------------------------------------------------

    def onPopup(self, event):
        """
        Evaluate the label string of the menu item selected and starts
        the related process
        """
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)

        if menuItem.GetItemLabel() == _("Paste\tCtrl+V"):
            self.on_paste(self)

        elif menuItem.GetItemLabel() == _("Remove selected URL\tDEL"):
            self.on_del_url_selected(self)

        elif menuItem.GetItemLabel() == _("Clear list\tShift+DEL"):
            self.delete_all(self)
    # ----------------------------------------------------------------------

    def changes_in_progress(self, setfocus=True):
        """
        Update new URLs list by drag&drop operations.
        """
        if setfocus:
            sel = self.urlctrl.GetFocusedItem()  # Get the current row
            selitem = sel if sel != -1 else 0
            self.urlctrl.Focus(selitem)  # make the line the current line
            self.urlctrl.Select(selitem, on=1)  # default event selection

        data = []
        for x in range(self.urlctrl.GetItemCount()):
            data.append(self.urlctrl.GetItemText(x, 1))

        if not data == self.parent.data_url:
            self.parent.changed = True

        self.parent.statusbar_msg(_('Ready'), None)
        self.parent.data_url = data.copy()
        self.parent.destroy_orphaned_window()
        self.parent.toolbar.EnableTool(25, True)
    # -----------------------------------------------------------------------

    def on_paste(self, event):
        """
        Event on clicking paste button to paste
        text data on the ListCtrl
        """
        text_data = wx.TextDataObject()
        success = False
        if wx.TheClipboard.Open():
            success = wx.TheClipboard.GetData(text_data)
            wx.TheClipboard.Close()
        if success:
            data = text_data.GetText().split()
            for url in data:
                self.urlctrl.dropUpdate(url)
            self.urlctrl.rejected_urls()
    # ----------------------------------------------------------------------

    def delete_all(self, event):
        """
        Clear all text lines of the TxtCtrl.
        If already empty, return None
        """
        if self.urlctrl.GetItemCount() == 0:
            return
        self.urlctrl.DeleteAllItems()
        self.parent.destroy_orphaned_window()
        self.parent.toolbar.EnableTool(25, False)
        del self.parent.data_url[:]
    # -----------------------------------------------------------

    def on_del_url_selected(self, event):
        """
        Delete a selected url, if nothing is selected return None
        """
        if self.urlctrl.GetFirstSelected() == -1:  # None
            return

        item, indexes = -1, []
        while 1:
            item = self.urlctrl.GetNextItem(item,
                                            wx.LIST_NEXT_ALL,
                                            wx.LIST_STATE_SELECTED)
            indexes.append(item)
            if item == -1:
                indexes.remove(-1)
                break

        if self.urlctrl.GetItemCount() == len(indexes):
            self.delete_all(self)
            return

        for num in sorted(indexes, reverse=True):
            self.urlctrl.DeleteItem(num)  # remove selected items
            self.urlctrl.Select(num - 1)  # select the previous one
        self.changes_in_progress(setfocus=False)

        for x in range(self.urlctrl.GetItemCount()):
            self.urlctrl.SetItem(x, 0, str(x + 1))  # re-load counter
        return
    # ----------------------------------------------------------------------

    def on_file_save(self, path):
        """
        Set a specific directory for files saving
        """
        self.text_path_save.SetValue("")
        self.text_path_save.AppendText(path)
