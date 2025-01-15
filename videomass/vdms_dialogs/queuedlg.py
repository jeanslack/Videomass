# -*- coding: UTF-8 -*-
"""
Name: queuedlg.py
Porpose: A proper dialog for queue managements
Compatibility: Python3, wxPython4
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.25.2024
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
import os
import wx
import wx.lib.scrolledpanel as scrolled
from videomass.vdms_utils.queue_utils import load_json_file_queue
from videomass.vdms_utils.queue_utils import write_json_file_queue
from videomass.vdms_utils.queue_utils import extend_data_queue
from videomass.vdms_dialogs.queue_edit import Edit_Queue_Item


class QueueManager(wx.Dialog):
    """
    This class provides a graphical representation for
    managing file queues for viewing, redefining or
    modifying data before sending it to processing.
    """
    def __init__(self, parent,
                 datalist,
                 movetotrash,
                 emptylist,
                 removequeue):
        """
        `datalist` is a class list.
        `movetotrash`, `emptylist` are class booleans
        """
        get = wx.GetApp()  # get data from bootstrap
        self.appdata = get.appset
        colorscheme = self.appdata['colorscheme']
        self.datalist = datalist
        self.movetotrash = movetotrash
        self.emptylist = emptylist
        self.delqueuefile = removequeue
        self.parent = parent
        wx.Dialog.__init__(self, parent, -1,
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        sizerbase = wx.BoxSizer(wx.HORIZONTAL)
        sizerbtn = wx.BoxSizer(wx.VERTICAL)
        sizerbase.Add(sizerbtn, 0)
        self.btn_edit = wx.Button(self, wx.ID_ANY, _("Edit"), size=(-1, -1))
        sizerbtn.Add(self.btn_edit, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_remove = wx.Button(self, wx.ID_ANY,
                                    _("Remove"), size=(-1, -1))
        sizerbtn.Add(self.btn_remove, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_remall = wx.Button(self, wx.ID_ANY,
                                    _("Remove all"), size=(-1, -1))
        sizerbtn.Add(self.btn_remall, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_expqueue = wx.Button(self, wx.ID_ANY,
                                      _("Export\nqueue file"), size=(-1, -1))
        sizerbtn.Add(self.btn_expqueue, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_impqueue = wx.Button(self, wx.ID_ANY,
                                      _("Import\nqueue file"), size=(-1, -1))
        sizerbtn.Add(self.btn_impqueue, 0, wx.ALL | wx.EXPAND, 5)

        self.quelist = wx.ListCtrl(self,
                                   style=wx.LC_REPORT
                                   | wx.LC_SINGLE_SEL
                                   )
        # self.quelist.SetMinSize((400, 500))
        self.quelist.InsertColumn(0, _('Destination file name'), width=700)
        index = 0
        for items in self.datalist:  # populate listctrl:
            desttitle = os.path.basename(items['destination'])
            self.quelist.InsertItem(index, desttitle)
            index += 1

        sizervert = wx.BoxSizer(wx.VERTICAL)
        sizerbase.Add(sizervert, 1, wx.EXPAND)
        sizervert.Add(self.quelist, 1, wx.EXPAND | wx.ALL, 5)

        panelscroll = scrolled.ScrolledPanel(self, wx.ID_ANY,
                                             size=(700, 200),
                                             name="panelscr",
                                             style=wx.TAB_TRAVERSAL
                                             | wx.BORDER_THEME,
                                             )
        sizervert.Add(panelscroll, 0, wx.ALL | wx.EXPAND, 5)
        self.labkey = wx.StaticText(panelscroll, wx.ID_ANY, '')
        self.labval = wx.StaticText(panelscroll, wx.ID_ANY, '')
        panelscroll.SetBackgroundColour(colorscheme['BACKGRD'])
        self.labkey.SetForegroundColour(colorscheme['TXT3'])
        self.labval.SetForegroundColour(colorscheme['TXT1'])
        grid_pan = wx.BoxSizer(wx.HORIZONTAL)
        grid_pan.Add(self.labkey, 0, wx.ALL
                     | wx.ALIGN_CENTRE_VERTICAL
                     | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        grid_pan.Add(self.labval, 0, wx.ALL
                     | wx.ALIGN_CENTRE_VERTICAL
                     | wx.ALIGN_CENTRE_HORIZONTAL, 5)

        panelscroll.SetSizer(grid_pan)
        panelscroll.SetAutoLayout(1)
        panelscroll.SetupScrolling()

        lab = (_('When finished, once the operations '
                 'have been completed successfully:'))
        lbl = wx.StaticText(self, label=lab)
        sizervert.Add(lbl, 0, wx.LEFT | wx.TOP, 5)
        sizeropt = wx.BoxSizer(wx.HORIZONTAL)
        sizervert.Add(sizeropt, 0)
        descr = _('Trash the source files')
        self.ckbx_trash = wx.CheckBox(self, wx.ID_ANY, (descr))
        self.ckbx_trash.SetValue(self.movetotrash)
        sizeropt.Add(self.ckbx_trash, 0, wx.ALL, 5)
        descr = _('Clear the File List')
        self.ckbx_del = wx.CheckBox(self, wx.ID_ANY, (descr))
        self.ckbx_del.SetValue(self.emptylist)
        if self.movetotrash:
            self.ckbx_del.Disable()
        sizeropt.Add(self.ckbx_del, 0, wx.ALL, 5)

        descr = _('Remove all items in the queue')
        self.ckbx_queue = wx.CheckBox(self, wx.ID_ANY, (descr))
        self.ckbx_queue.SetValue(self.delqueuefile)
        sizeropt.Add(self.ckbx_queue, 0, wx.ALL, 5)
        btncancel = wx.Button(self, wx.ID_CANCEL, "")
        btnok = wx.Button(self, wx.ID_OK, _("Run"))
        btngrid = wx.FlexGridSizer(1, 2, 0, 0)
        btngrid.Add(btncancel, 0)
        btngrid.Add(btnok, 0, wx.LEFT, 5)
        sizervert.Add(btngrid, flag=wx.ALL
                      | wx.ALIGN_RIGHT
                      | wx.RIGHT, border=5
                      )
        # ----------------------Properties----------------------#
        self.SetTitle(_('Videomass - Queue'))
        self.SetMinSize((820, 550))

        self.SetSizer(sizerbase)
        sizerbase.Fit(self)
        self.Layout()

        # ----------------------Binding (EVT)------------------------#
        self.Bind(wx.EVT_BUTTON, self.on_edit_item, self.btn_edit)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.quelist)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect, self.quelist)
        self.Bind(wx.EVT_CHECKBOX, self.on_file_to_trash, self.ckbx_trash)
        self.Bind(wx.EVT_CHECKBOX, self.on_empty_list, self.ckbx_del)
        self.Bind(wx.EVT_BUTTON, self.on_remove_all, self.btn_remall)
        self.Bind(wx.EVT_CHECKBOX, self.on_keep_queuefile, self.ckbx_queue)
        self.Bind(wx.EVT_BUTTON, self.on_remove_item, self.btn_remove)
        self.Bind(wx.EVT_BUTTON, self.on_save_queue, self.btn_expqueue)
        self.Bind(wx.EVT_BUTTON, self.on_load_queue, self.btn_impqueue)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, btncancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btnok)

        if self.datalist:
            self.quelist.Focus(0)  # make the line the current line
            self.quelist.Select(0, on=1)  # default event selection
    # ------------------------- Callbacks --------------------------------

    def on_edit_item(self, event):
        """
        This allow to edit a selected item
        """
        if self.quelist.GetFirstSelected() == -1:  # None
            return

        index = self.quelist.GetFocusedItem()  # index (int)
        with Edit_Queue_Item(self,
                             self.datalist[index]) as editsel:
            if editsel.ShowModal() == wx.ID_OK:
                write_json_file_queue(self.datalist)
                self.on_select(None)
        return
    # ----------------------------------------------------------------------

    def on_load_queue(self, event):
        """
        Load a previously saved json queue file
        """
        selidx = self.quelist.GetFirstSelected()
        newdata = load_json_file_queue()
        if not newdata:
            return

        update = extend_data_queue(self, self.datalist, newdata)
        if not update:
            return

        self.quelist.DeleteAllItems()
        index = 0
        for item in self.datalist:  # populate listctrl:
            desttitle = os.path.basename(item['destination'])
            self.quelist.InsertItem(index, desttitle)
            index += 1

        write_json_file_queue(self.datalist)

        if not selidx == -1:
            self.quelist.Focus(selidx)  # make the line the current line
            self.quelist.Select(selidx, on=1)  # default event selection
        self.parent.queue_tool_counter()
    # ----------------------------------------------------------------------

    def on_save_queue(self, event):
        """
        Save a queue file in local.
        """
        if not self.datalist:
            return

        with wx.FileDialog(self, _("Export queue file"),
                           defaultDir=os.path.expanduser('~'),
                           wildcard="Queue files (*.json)|*.json",
                           style=wx.FD_SAVE
                           | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            fileDialog.SetFilename('Videomass queue.json')
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            filename = fileDialog.GetPath()

        write_json_file_queue(self.datalist, filename)
    # ----------------------------------------------------------------------

    def on_remove_item(self, event):
        """
        Delete a selected item, if nothing is selected return None
        """
        if self.quelist.GetFirstSelected() == -1:  # None
            return

        item, indexes = -1, []
        while 1:
            item = self.quelist.GetNextItem(item,
                                            wx.LIST_NEXT_ALL,
                                            wx.LIST_STATE_SELECTED)
            indexes.append(item)
            if item == -1:
                indexes.remove(-1)
                break

        if self.quelist.GetItemCount() == len(indexes):
            self.on_remove_all(None)
            return

        for num in sorted(indexes, reverse=True):
            self.quelist.DeleteItem(num)  # remove selected items
            self.datalist.pop(num)  # remove selected items
            self.quelist.Select(num - 1)  # select the previous one

        write_json_file_queue(self.datalist)
        self.parent.queue_tool_counter()
        return
    # ----------------------------------------------------------------------

    def on_remove_all(self, event):
        """
        Clear the listCtrl and datalist, if already empty,
        return None.
        """
        if self.quelist.GetItemCount() == 0:
            return
        self.quelist.DeleteAllItems()
        self.datalist.clear()
        self.on_deselect(None)
        queuebak = os.path.join(self.appdata["confdir"], 'queue.backup')
        os.remove(queuebak)
        self.parent.queue_tool_counter()
    # ----------------------------------------------------------------------

    def on_select(self, event):
        """
        Selecting line with mouse or up/down keyboard buttons
        """
        index = self.quelist.GetFocusedItem()  # index (int)
        itemsel = self.datalist[index]
        passes = '1' if itemsel["args"][1] == '' else '2'

        if not itemsel["start-time"] or not itemsel["end-time"]:
            sst, endt = _('Same as source'), _('Same as source')
        else:
            sst = itemsel["start-time"].split()[1]
            endt = itemsel["end-time"].split()[1]

        keys = (_("Source\nFile destination\nAutomation/Preset\n"
                  "Encoding passes\nOutput Format\nStart of segment\n"
                  "Clip duration"))
        vals = (f'{itemsel["source"]}\n{itemsel["destination"]}\n'
                f'{itemsel["preset name"]}\n{passes}\n{itemsel["extension"]}\n'
                f'{sst}\n{endt}'
                )
        self.labkey.SetLabel(keys)
        self.labval.SetLabel(vals)
        self.Layout()
    # ----------------------------------------------------------------------

    def on_deselect(self, event):
        """
        Event to deselect a line when clicking
        in an empty space of the control list
        """
        self.labkey.SetLabel('')
        self.labval.SetLabel('')
    # ----------------------------------------------------------------------

    def on_empty_list(self, event):
        """
        enable/disable empty imported file list.
        """
        if self.ckbx_del.IsChecked():
            self.emptylist = True
        else:
            self.emptylist = False
    # ----------------------------------------------------------------------

    def on_file_to_trash(self, event):
        """
        enable/disable "Move file to trash" after successful encoding
        """
        trashdir = self.appdata['trashdir_loc']
        if self.ckbx_trash.IsChecked():
            self.movetotrash = True
            self.ckbx_del.SetValue(True)
            self.ckbx_del.Disable()
            self.emptylist = True
            if not os.path.exists(trashdir):
                os.mkdir(trashdir, mode=0o777)
        else:
            self.movetotrash = False
            self.ckbx_del.Enable()
            self.ckbx_del.SetValue(False)
            self.emptylist = False
    # ----------------------------------------------------------------------

    def on_keep_queuefile(self, event):
        """
        enable/disable keep or remove queue file backup.
        """
        if self.ckbx_queue.IsChecked():
            self.delqueuefile = True
        else:
            self.delqueuefile = False
    # ----------------------------------------------------------------------

    def on_cancel(self, event):
        """
        exit from formula dialog
        """
        # self.Destroy()
        event.Skip()
    # ----------------------------------------------------------------------

    def on_ok(self, event):
        """
        get confirmation to proceed
        """
        # self.Destroy()
        event.Skip()
    # ----------------------------------------------------------------------

    def getvalue(self):
        """
        This method return values via the getvalue() interface
        from the caller. See the caller for more info and usage.
        """
        return (self.datalist, self.movetotrash,
                self.emptylist, self.delqueuefile)
