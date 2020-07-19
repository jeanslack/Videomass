# -*- coding: UTF-8 -*-
# Name: filedrop.py
# Porpose: files drag n drop interface
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: June.02.2020 *PEP8 compatible*
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
from videomass3.vdms_io import IO_tools
from videomass3.vdms_utils.utils import time_seconds


class MyListCtrl(wx.ListCtrl):
    """
    This is the listControl widget. Note that this wideget has DnDPanel
    parent.
    """
    AZURE = '#d9ffff'  # rgb form (wx.Colour(217,255,255))
    RED = '#ea312d'
    YELLOW = '#a29500'
    GREENOLIVE = '#6aaf23'
    ORANGE = '#f28924'
    # ----------------------------------------------------------------------

    def __init__(self, parent):
        """Constructor"""
        self.index = None
        self.parent = parent  # parent is DnDPanel class
        self.data = self.parent.data
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT |
                             wx.LC_SINGLE_SEL
                             )
    # ----------------------------------------------------------------------#

    def dropUpdate(self, path):
        """
        Update list-control during drag and drop

        """
        self.index = self.GetItemCount()
        msg_dir = _("Directories are not allowed, just add files, please.")
        msg_noext = _("File without format extension: please give an "
                      "appropriate extension to the file name, example "
                      "'.mkv', '.avi', '.mp3', etc.")
        if os.path.isdir(path):
            self.parent.statusbar_msg(msg_dir, MyListCtrl.ORANGE)
            return
        elif os.path.splitext(os.path.basename(path))[1] == '':
            self.parent.statusbar_msg(msg_noext, MyListCtrl.ORANGE)
            return

        if not [x for x in self.data if x['format']['filename'] == path]:
            data = IO_tools.probeInfo(path)

            if data[1]:
                self.parent.statusbar_msg(data[1], MyListCtrl.RED)
                return

            data = eval(data[0])
            self.InsertItem(self.index, path)

            if 'duration' not in data['format'].keys():
                self.SetItem(self.index, 1, 'N/A')
                data['format']['duration'] = 0
            else:

                t = data['format']['duration'].split(':')
                s, ms = t[2].split('.')[0], t[2].split('.')[1]
                t = '%sh : %sm : %ss : %s micro s' % (t[0], t[1], s, ms)
                self.SetItem(self.index, 1, t)
                data.get('format')['time'] = data.get('format').pop('duration')
                time = time_seconds(data.get('format')['time'])
                data['format']['duration'] = time

            media = data['streams'][0]['codec_type']
            formatname = data['format']['format_long_name']
            self.SetItem(self.index, 2, '%s: %s' % (media, formatname))
            self.SetItem(self.index, 3, data['format']['size'])
            self.index += 1
            self.data.append(data)
            self.parent.statusbar_msg('', None)

        else:
            mess = _("Duplicate files are rejected: > '%s'") % path
            self.parent.statusbar_msg(mess, MyListCtrl.YELLOW)
    # ----------------------------------------------------------------------#


class FileDrop(wx.FileDropTarget):
    """
    This is the file drop target
    """
    # ----------------------------------------------------------------------#

    def __init__(self, window):
        """
        Constructor. File Drop targets are subsets of windows
        """
        wx.FileDropTarget.__init__(self)
        self.window = window  # window is MyListCtr class
    # ----------------------------------------------------------------------#

    def OnDropFiles(self, x, y, filenames):
        """
        When files are dropped, write where they were dropped and then
        the file paths themselves
        """
        for filepath in filenames:
            self.window.dropUpdate(filepath)  # update list control

        return True
    # ----------------------------------------------------------------------#


class FileDnD(wx.Panel):
    """
    Panel for dragNdrop files queue. Accept one or more files.
    """
    # CONSTANTS:
    get = wx.GetApp()
    OUTSAVE = get.USERfilesave  # path to the configuration directory
    OS = get.OS

    def __init__(self, parent):
        """Constructor. This will initiate with an id and a title"""
        self.parent = parent  # parent is the MainFrame
        self.data = self.parent.data_files  # set items list data on parent
        dirname = os.path.expanduser('~')  # /home/user/
        self.file_dest = dirname if not self.OUTSAVE else self.OUTSAVE
        self.selected = None  # tells if an imported file is selected or not

        wx.Panel.__init__(self, parent=parent)

        # This builds the list control box:
        self.flCtrl = MyListCtrl(self)  # class MyListCtr
        # Establish the listctrl as a drop target:
        file_drop_target = FileDrop(self.flCtrl)
        self.flCtrl.SetDropTarget(file_drop_target)  # Make drop target.
        # create widgets
        sizer = wx.BoxSizer(wx.VERTICAL)
        infomsg = _("Drag one or more files below")
        lbl_info = wx.StaticText(self, label=infomsg)
        sizer.Add(lbl_info, 0, wx.ALL, 5)
        sizer.Add(self.flCtrl, 1, wx.EXPAND | wx.ALL, 5)
        optionsmsg = _("Options")
        lbl_options = wx.StaticText(self, label=optionsmsg)
        sizer.Add(lbl_options, 0, wx.ALL, 5)
        sizer_media = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer_media, 0, wx.EXPAND | wx.ALL, 5)
        btn_delsel = wx.Button(self, wx.ID_REMOVE, "")
        sizer_media.Add(btn_delsel, 1, wx.ALL | wx.EXPAND, 5)
        btn_clear = wx.Button(self, wx.ID_CLEAR, "")
        sizer_media.Add(btn_clear, 1, wx.ALL | wx.EXPAND, 5)
        outdirmsg = _("Output Directory")
        lbl_outdir = wx.StaticText(self, label=outdirmsg)
        sizer.Add(lbl_outdir, 0, wx.ALL, 5)
        sizer_outdir = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer_outdir, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_save = wx.Button(self, wx.ID_OPEN, "...", size=(-1, -1))
        sizer_outdir.Add(self.btn_save, 0, wx.ALL |
                         wx.ALIGN_CENTER_HORIZONTAL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        self.text_path_save = wx.TextCtrl(self, wx.ID_ANY, "",
                                          style=wx.TE_PROCESS_ENTER |
                                          wx.TE_READONLY
                                          )
        sizer_outdir.Add(self.text_path_save, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(sizer)

        # properties
        self.flCtrl.InsertColumn(0, _('Input files'), width=550)
        self.flCtrl.InsertColumn(1, _('Duration'), width=230)
        self.flCtrl.InsertColumn(2, _('Media type'), width=200)
        self.flCtrl.InsertColumn(3, _('File size'), width=150)
        if self.OS != 'Darwin':
            lbl_info.SetLabelMarkup("<b>%s</b>" % infomsg)
            lbl_options.SetLabelMarkup("<b>%s</b>" % optionsmsg)
            lbl_outdir.SetLabelMarkup("<b>%s</b>" % outdirmsg)
        self.text_path_save.SetValue(self.file_dest)

        # Tooltip
        btn_delsel.SetToolTip(_('Remove the selected file from the list'))
        btn_clear.SetToolTip(_('Delete all files from the list'))
        tip = (_('Choose another output directory for files saving'))
        self.btn_save.SetToolTip(tip)

        # Binding (EVT)
        self.Bind(wx.EVT_BUTTON, self.deleteAll, btn_clear)
        self.Bind(wx.EVT_BUTTON, self.delSelect, btn_delsel)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.flCtrl)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect, self.flCtrl)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_doubleClick, self.flCtrl)
        self.Bind(wx.EVT_CONTEXT_MENU, self.onContext)

    # ----------------------------------------------------------------------

    def which(self):
        """
        return topic name by choose_topic.py selection

        """
        return self.parent.topicname
    # ----------------------------------------------------------------------

    def onContext(self, event):
        """
        Create and show a Context Menu
        """
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewIdRef()
            self.Bind(wx.EVT_MENU, self.onPopup, id=self.popupID1)
        # build the menu
        menu = wx.Menu()
        itemThree = menu.Append(self.popupID1,
                                _("Remove the selected file")
                                )
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
        if menuItem.GetItemLabel() == _("Remove the selected file"):
            self.delSelect(self)
    # ----------------------------------------------------------------------

    def delSelect(self, event):
        """
        Delete the file selected in the list

        """
        if not self.selected:
            self.parent.statusbar_msg(_('No file selected'), 'GOLDENROD')
        else:
            self.parent.statusbar_msg(_('Add Files'), None)

            if self.flCtrl.GetItemCount() == 1:
                self.deleteAll(self)
            else:
                item = self.flCtrl.GetFocusedItem()
                self.flCtrl.DeleteItem(item)
                self.selected = None
                self.data.pop(item)
    # ----------------------------------------------------------------------

    def deleteAll(self, event):
        """
        Delete and clear all text lines of the TxtCtrl,
        reset the fileList[], disable Toolbar button and menu bar
        Stream/play select imported file - Stream/display imported...
        """
        # self.flCtrl.ClearAll()
        self.flCtrl.DeleteAllItems()
        del self.data[:]
        self.parent.filedropselected = None
        self.selected = None
    # ----------------------------------------------------------------------

    def on_select(self, event):
        """
        Selecting a line with mouse or up/down keyboard buttons
        """
        index = self.flCtrl.GetFocusedItem()
        item = self.flCtrl.GetItemText(index)
        self.parent.filedropselected = item
        self.selected = item
    # ----------------------------------------------------------------------

    def on_doubleClick(self, row):
        """
        Double click or keyboard enter button, open media info
        """
        self.onContext(self)
        # self.parent.ImportInfo(self)
    # ----------------------------------------------------------------------

    def on_deselect(self, event):
        """
        De-selecting a line with mouse by click in empty space of
        the control list
        """
        self.parent.filedropselected = None
        self.selected = None
    # ----------------------------------------------------------------------

    def on_file_save(self, path):
        """
        Set a specific directory for files saving

        """
        self.text_path_save.SetValue("")
        self.text_path_save.AppendText(path)
        self.file_dest = '%s' % (path)
    # -----------------------------------------------------------------------

    def statusbar_msg(self, mess, color):
        """
        Set a status bar message of the parent method.
        """
        self.parent.statusbar_msg('%s' % mess, color)
