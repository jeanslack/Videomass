# -*- coding: UTF-8 -*-
# Name: filedrop.py
# Porpose: files drag n drop interface
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Apr.04.2021 *PEP8 compatible*
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
import sys
from videomass3.vdms_utils.get_bmpfromsvg import get_bmp
from videomass3.vdms_io import IO_tools
from videomass3.vdms_utils.utils import get_milliseconds


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
    WHITE = '#fbf4f4'
    BLACK = '#060505'
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
        msg_badfn = _("Invalid filename. Contains double quotes")

        if '"' in path:
            self.parent.statusbar_msg(msg_badfn, MyListCtrl.ORANGE,
                                      MyListCtrl.WHITE)
            return

        elif os.path.isdir(path):
            self.parent.statusbar_msg(msg_dir, MyListCtrl.ORANGE,
                                      MyListCtrl.WHITE)
            return
        elif os.path.splitext(os.path.basename(path))[1] == '':
            self.parent.statusbar_msg(msg_noext, MyListCtrl.ORANGE,
                                      MyListCtrl.WHITE)
            return

        if not [x for x in self.data if x['format']['filename'] == path]:
            data = IO_tools.probeInfo(path)

            if data[1]:
                self.parent.statusbar_msg(data[1], MyListCtrl.RED,
                                          MyListCtrl.WHITE)
                return

            data = eval(data[0])
            self.InsertItem(self.index, path)

            if 'duration' not in data['format'].keys():
                self.SetItem(self.index, 1, 'N/A')
                # NOTE these are my adds in ffprobe data
                data['format']['time'] = '00:00:00.000'
                data['format']['duration'] = 0

            else:
                t = data['format']['duration'].split(':')
                s, ms = t[2].split('.')[0], t[2].split('.')[1]
                t = '%sh : %sm : %ss : %sms' % (t[0], t[1], s, ms)
                self.SetItem(self.index, 1, t)
                data.get('format')['time'] = data.get('format').pop('duration')
                time = get_milliseconds(data.get('format')['time'])
                data['format']['duration'] = time

            media = data['streams'][0]['codec_type']
            formatname = data['format']['format_long_name']
            self.SetItem(self.index, 2, '%s: %s' % (media, formatname))
            self.SetItem(self.index, 3, data['format']['size'])
            self.index += 1
            self.data.append(data)
            self.parent.statusbar_msg('', None)
            self.parent.reset_tl()

        else:
            mess = _("Duplicate files are rejected: > '%s'") % path
            self.parent.statusbar_msg(mess, MyListCtrl.YELLOW,
                                      MyListCtrl.WHITE)
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
    OUTSAVE = get.FFMPEGoutdir  # files destination folder
    OS = get.OS
    SAMEDIR = get.SAMEdir
    SUFFIX = get.FILEsuffix
    WHITE = '#fbf4f4'
    BLACK = '#060505'

    def __init__(self, parent, iconplay):
        """Constructor. This will initiate with an id and a title"""
        self.parent = parent  # parent is the MainFrame
        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up
            bmpplay = get_bmp(iconplay, ((16, 16)))
        else:
            bmpplay = wx.Bitmap(iconplay, wx.BITMAP_TYPE_ANY)
        self.data = self.parent.data_files  # set items list data on parent
        self.file_dest = FileDnD.OUTSAVE
        self.selected = None  # tells if an imported file is selected or not

        wx.Panel.__init__(self, parent=parent)

        # This builds the list control box:
        self.flCtrl = MyListCtrl(self)  # class MyListCtr
        # Establish the listctrl as a drop target:
        file_drop_target = FileDrop(self.flCtrl)
        self.flCtrl.SetDropTarget(file_drop_target)  # Make drop target.
        # create widgets
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((0, 10))
        infomsg = _("Drag one or more files below")
        lbl_info = wx.StaticText(self, wx.ID_ANY, label=infomsg)
        sizer.Add(lbl_info, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.flCtrl, 1, wx.EXPAND | wx.ALL, 2)
        sizer.Add((0, 10))
        sizer_media = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_play = wx.Button(self, wx.ID_ANY, _("Play"))
        self.btn_play.SetBitmap(bmpplay, wx.LEFT)
        self.btn_play.Disable()
        sizer_media.Add(self.btn_play, 1, wx.ALL | wx.EXPAND, 2)
        self.btn_remove = wx.Button(self, wx.ID_REMOVE, "")
        self.btn_remove.Disable()
        sizer_media.Add(self.btn_remove, 1, wx.ALL | wx.EXPAND, 2)
        self.btn_clear = wx.Button(self, wx.ID_CLEAR, "")
        self.btn_clear.Disable()
        sizer_media.Add(self.btn_clear, 1, wx.ALL | wx.EXPAND, 2)
        sizer.Add(sizer_media, 0, wx.EXPAND)
        sizer_outdir = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_save = wx.Button(self, wx.ID_OPEN, "...", size=(35, -1))
        self.text_path_save = wx.TextCtrl(self, wx.ID_ANY, "",
                                          style=wx.TE_PROCESS_ENTER |
                                          wx.TE_READONLY
                                          )
        sizer_outdir.Add(self.text_path_save, 1, wx.ALL | wx.EXPAND, 2)
        sizer_outdir.Add(self.btn_save, 0, wx.ALL |
                         wx.ALIGN_CENTER_HORIZONTAL |
                         wx.ALIGN_CENTER_VERTICAL, 2
                         )
        sizer.Add(sizer_outdir, 0, wx.EXPAND)
        self.SetSizer(sizer)
        # properties
        self.flCtrl.InsertColumn(0, _('File Name'), width=350)
        self.flCtrl.InsertColumn(1, _('Duration'), width=230)
        self.flCtrl.InsertColumn(2, _('Media type'), width=200)
        self.flCtrl.InsertColumn(3, _('Size'), width=150)

        if self.OS == 'Darwin':
            lbl_info.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        else:
            lbl_info.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        self.text_path_save.SetValue(self.file_dest)

        if FileDnD.SAMEDIR == 'true':
            self.btn_save.Disable(), self.text_path_save.Disable()
            self.parent.same_destin = True
            if not FileDnD.SUFFIX == 'none':  # otherwise must be '' on parent
                self.parent.suffix = FileDnD.SUFFIX

        # Tooltip
        self.btn_remove.SetToolTip(_('Remove the selected file from the list'))
        self.btn_clear.SetToolTip(_('Delete all files from the list'))
        tip = (_("Set up a temporary folder for conversions"))
        self.btn_save.SetToolTip(tip)
        self.btn_play.SetToolTip(_("Play the selected files in the list"))
        self.text_path_save.SetToolTip(_("Destination folder"))

        # Binding (EVT)
        self.Bind(wx.EVT_BUTTON, self.playSelect, self.btn_play)
        self.Bind(wx.EVT_BUTTON, self.deleteAll, self.btn_clear)
        self.Bind(wx.EVT_BUTTON, self.delSelect, self.btn_remove)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.flCtrl)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect, self.flCtrl)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_doubleClick, self.flCtrl)
        self.Bind(wx.EVT_CONTEXT_MENU, self.onContext)

    # ----------------------------------------------------------------------

    def reset_tl(self):
        """
        When you drop new files resets the timeline on main_frame.
        it is also needed by the MyListCtrl class.

        """
        self.parent.reset_Timeline()
        if not self.btn_clear.IsEnabled():
            self.btn_clear.Enable()
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
            self.popupID2 = wx.NewIdRef()
            self.Bind(wx.EVT_MENU, self.onPopup, id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.onPopup, id=self.popupID2)
        # build the menu
        menu = wx.Menu()
        itemOne = menu.Append(self.popupID2, _("Play"))
        itemTwo = menu.Append(self.popupID1, _("Remove"))
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

        if menuItem.GetItemLabel() == _("Play"):
            self.playSelect(self)

        elif menuItem.GetItemLabel() == _("Remove"):
            self.delSelect(self)

    # ----------------------------------------------------------------------

    def playSelect(self, event):
        """
        Playback the selected file

        """
        if not self.selected:
            self.parent.statusbar_msg(_('No file selected'), 'GOLDENROD',
                                      FileDnD.WHITE)
        else:
            self.parent.statusbar_msg(_('Add Files'), None)
            index = self.flCtrl.GetFocusedItem()
            item = self.flCtrl.GetItemText(index)
            if self.parent.checktimestamp:
                tstamp = '-vf "%s"' % (self.parent.cmdtimestamp)
            else:
                tstamp = ""
            IO_tools.stream_play(item, self.parent.time_seq,
                                 tstamp, self.parent.autoexit
                                 )
    # ----------------------------------------------------------------------

    def delSelect(self, event):
        """
        Delete the selected file

        """
        if not self.selected:
            self.parent.statusbar_msg(_('No file selected'), 'GOLDENROD',
                                      FileDnD.WHITE)
        else:
            self.parent.statusbar_msg(_('Add Files'), None)

            if self.flCtrl.GetItemCount() == 1:
                self.deleteAll(self)
            else:
                item = self.flCtrl.GetFocusedItem()
                self.flCtrl.DeleteItem(item)  # remove from listctrl
                self.reset_tl()  # delete parent.timeline
                self.on_deselect(self)  # deselect removed file
                self.data.pop(item)  # remove all data item
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
        self.reset_tl()
        self.selected = None
        self.btn_play.Disable(), self.btn_remove.Disable()
        self.btn_clear.Disable()
    # ----------------------------------------------------------------------

    def on_select(self, event):
        """
        Selecting a line with mouse or up/down keyboard buttons
        """
        index = self.flCtrl.GetFocusedItem()
        item = self.flCtrl.GetItemText(index)
        self.parent.filedropselected = item
        self.selected = item
        self.btn_play.Enable(), self.btn_remove.Enable()
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
        self.btn_play.Disable(), self.btn_remove.Disable()
    # ----------------------------------------------------------------------

    def on_file_save(self, path):
        """
        Set a specific directory for files saving

        """
        self.text_path_save.SetValue("")
        self.text_path_save.AppendText(path)
        self.file_dest = '%s' % (path)
    # -----------------------------------------------------------------------

    def statusbar_msg(self, mess, bcolor, fcolor=None):
        """
        Set a status bar message of the parent method.
        bcolor: background, fcolor: foreground
        """
        self.parent.statusbar_msg('%s' % mess, bcolor, fcolor)
