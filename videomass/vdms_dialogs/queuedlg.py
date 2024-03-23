# -*- coding: UTF-8 -*-
"""
Name: queuedlg.py
Porpose: A proper dialog for queue managements
Compatibility: Python3, wxPython4
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.19.2024
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
from videomass.vdms_utils.get_queue_json import load_json_file_queue


class QueueManager(wx.Dialog):
    """
    This class provides a graphical representation for
    managing file queues for viewing, redefining or
    modifying data before sending it to processing.
    """
    def __init__(self, parent, datalist, movetotrash, emptylist):
        """
        `datalist` is a class dict.
        `movetotrash`, `emptylist` are class booleans
        """
        get = wx.GetApp()  # get data from bootstrap
        self.appdata = get.appset
        colorscheme = self.appdata['icontheme'][1]
        self.datalist = datalist
        self.movetotrash = movetotrash
        self.emptylist = emptylist
        wx.Dialog.__init__(self, parent, -1,
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        sizerbase = wx.BoxSizer(wx.HORIZONTAL)
        sizerbtn = wx.BoxSizer(wx.VERTICAL)
        sizerbase.Add(sizerbtn, 0)
        # self.btn_up = wx.Button(self, wx.ID_ANY,
        #                         _("Move up"), size=(-1, -1))
        # sizerbtn.Add(self.btn_up, 0, wx.ALL | wx.EXPAND, 5)
        # self.btn_down = wx.Button(self, wx.ID_ANY,
        #                           _("Move down"), size=(-1, -1))
        # sizerbtn.Add(self.btn_down, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_remove = wx.Button(self, wx.ID_ANY,
                                    _("Remove"), size=(-1, -1))
        sizerbtn.Add(self.btn_remove, 0, wx.ALL | wx.EXPAND, 5)

        self.btn_remall = wx.Button(self, wx.ID_ANY,
                                    _("Remove All"), size=(-1, -1))
        sizerbtn.Add(self.btn_remall, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_expqueue = wx.Button(self, wx.ID_ANY,
                                      _("Save Queue"), size=(-1, -1))
        sizerbtn.Add(self.btn_expqueue, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_impqueue = wx.Button(self, wx.ID_ANY,
                                      _("Load queue"), size=(-1, -1))
        sizerbtn.Add(self.btn_impqueue, 0, wx.ALL | wx.EXPAND, 5)

        self.quelist = wx.ListCtrl(self,
                                   style=wx.LC_REPORT
                                   | wx.LC_SINGLE_SEL
                                   )
        # self.quelist.SetMinSize((400, 500))
        self.quelist.InsertColumn(0, _('Title/File name'), width=700)
        index = 0
        for items in self.datalist:  # populate listctrl:
            desttitle = os.path.basename(items['fdest'])
            self.quelist.InsertItem(index, desttitle)
            index += 1

        sizervert = wx.BoxSizer(wx.VERTICAL)
        sizerbase.Add(sizervert, 1, wx.EXPAND)
        sizervert.Add(self.quelist, 1, wx.EXPAND | wx.ALL, 5)

        panelscroll = scrolled.ScrolledPanel(self, wx.ID_ANY,
                                             size=(700, 210),
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
        sizeropt = wx.BoxSizer(wx.HORIZONTAL)
        sizervert.Add(sizeropt, 0)
        descr = _("Trash the source files when finished")
        self.ckbx_trash = wx.CheckBox(self, wx.ID_ANY, (descr))
        self.ckbx_trash.SetValue(self.movetotrash)
        sizeropt.Add(self.ckbx_trash, 0, wx.ALL, 5)
        descr = _("Clear the File List when the operation is complete")
        self.ckbx_del = wx.CheckBox(self, wx.ID_ANY, (descr))
        self.ckbx_del.SetValue(self.emptylist)
        if self.movetotrash:
            self.ckbx_del.Disable()
        sizeropt.Add(self.ckbx_del, 0, wx.ALL, 5)
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
        self.SetTitle(_('Videomass Queue'))
        self.SetMinSize((700, 500))
        self.SetSizer(sizerbase)
        sizerbase.Fit(self)
        self.Layout()

        # ----------------------Binding (EVT)------------------------#
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.quelist)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect, self.quelist)
        self.Bind(wx.EVT_CHECKBOX, self.on_file_to_trash, self.ckbx_trash)
        self.Bind(wx.EVT_CHECKBOX, self.on_empty_list, self.ckbx_del)
        self.Bind(wx.EVT_BUTTON, self.on_remove_all, self.btn_remall)
        self.Bind(wx.EVT_BUTTON, self.on_remove_item, self.btn_remove)
        self.Bind(wx.EVT_BUTTON, self.on_save_queue, self.btn_expqueue)
        self.Bind(wx.EVT_BUTTON, self.on_load_queue, self.btn_impqueue)
        # self.Bind(wx.EVT_BUTTON, self.on_up, self.btn_up)
        # self.Bind(wx.EVT_BUTTON, self.on_down, self.btn_down)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, btncancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btnok)

    # ------------------------- Callbacks --------------------------------

    # def on_up(self, event):
    #     """
    #     move the selected item to up
    #     """
    #     if self.quelist.GetFirstSelected() == -1:  # None
    #         return
    #     index = self.quelist.GetFocusedItem()  # index (int)
    #     item = self.quelist.GetItemText(index)  # name (str)
    #     count = self.quelist.GetItemCount()  # len items
    #     print(index)
    #     print(item)
    #     print(count)
    #     curritems = []
    #
    #
    #     current_selection = self.quelist.GetSelectedObject()  # index
    #     data = self.quelist.GetObjects()
    #     if current_selection:
    #         index = data.index(current_selection)
    #         if index > 0:
    #             new_index = index - 1
    #         else:
    #             new_index = len(data)-1
    #         data.insert(new_index, data.pop(index))
    #         # self.products = data
    #         # self.setBooks()
    #         self.quelist.Select(new_index)
    # ----------------------------------------------------------------------

    # def on_down(self, event):
    #     """
    #     move the selected item to down
    #     """
    #     if self.quelist.GetFirstSelected() == -1:  # None
    #         return
    #     index = self.quelist.GetFocusedItem()  # index (int)
    #     item = self.quelist.GetItemText(index, 0)  # name (str)
    #     count = self.quelist.GetItemCount()
    #     print(index)
    #     print(item)
    #     print(count)
    #     curritems = []
    # ----------------------------------------------------------------------

    def on_load_queue(self, event):
        """
        Load a previously saved json queue file
        """
        newdata = load_json_file_queue()
        if not newdata:
            return
        self.datalist.extend(newdata)
        self.quelist.DeleteAllItems()
        index = 0
        for item in self.datalist:  # populate listctrl:
            desttitle = os.path.basename(item['fdest'])
            self.quelist.InsertItem(index, desttitle)
            index += 1
    # ----------------------------------------------------------------------

    def on_save_queue(self, event):
        """
        Save a queue file in local
        """
        filename = None
        with wx.FileDialog(self, _("Save queue"),
                           defaultDir=os.path.expanduser('~'),
                           wildcard="Videomass queue (*.json;)|*.json;",
                           style=wx.FD_SAVE
                           | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            fileDialog.SetFilename('Videomass queue')

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            filename = f"{fileDialog.GetPath()}.json"

        with open(filename, 'w', encoding='utf8') as outfile:
            json.dump(self.datalist, outfile, ensure_ascii=False, indent=4)
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
    # ----------------------------------------------------------------------

    def on_select(self, event):
        """
        Selecting line with mouse or up/down keyboard buttons
        """
        index = self.quelist.GetFocusedItem()  # index (int)
        itemsel = self.datalist[index]
        passes = 'One Pass' if itemsel["args"][1] == '' else 'Two pass'
        sst, endt = itemsel["start-time"], itemsel["end-time"]

        keys = (_("Source\nDestination\nType\nEncoding passes\n"
                  "Output Format\nStart Time\nEnd Time"))
        vals = (f'{itemsel["fsrc"]}\n{itemsel["fdest"]}\n{itemsel["type"]}\n'
                f'{passes}\n{itemsel["fext"]}\n{sst}\n{endt}'
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
        trashdir = os.path.join(self.appdata['confdir'], 'Trash')
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
        return self.datalist, self.movetotrash, self.emptylist
