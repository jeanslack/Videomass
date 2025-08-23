# -*- coding: UTF-8 -*-
"""
Name: filedrop.py
Porpose: files drag n drop interface
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Aug.20.2025
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
import re
import wx
from pubsub import pub
from videomass.vdms_threads.ffplay_file import FilePlay
from videomass.vdms_threads.ffprobe import ffprobe
from videomass.vdms_utils.utils import time_to_integer
from videomass.vdms_utils.utils import to_bytes
from videomass.vdms_dialogs.renamer import Renamer
from videomass.vdms_dialogs.list_warning import ListWarning


def fullpathname_sanitize(fullpathfilename):
    """
    Check for 'full path file name' sanitize.
    return message `string` if warning, `None` otherwise
    """
    illegal = '^` ~ " # % & * : < > ? / \\ { | }'
    illegalchars = _("File has illegal characters like:")
    invalidpath = _("Invalid character found in path name: (\")")
    justfile = _("Directories are not allowed, just add files, please.")
    noext = _("File without format extension: please give an "
              "appropriate extension to the file name, example "
              "'.mkv', '.avi', '.mp3', etc.")

    check = bool(re.search(r"^(?:[^\^\`\~\"\#\%\&\*\:\<\>\?\/\\\{\|\}])*$",
                 os.path.basename(fullpathfilename)))
    if check is not True:
        return f'{illegalchars} {illegal}'

    if '"' in fullpathfilename:
        return invalidpath

    if os.path.isdir(fullpathfilename):
        return justfile

    if os.path.splitext(os.path.basename(fullpathfilename))[1] == '':
        return noext

    return None
# ----------------------------------------------------------------------#


def filename_sanitize(newname, outputnames):
    """
    Check for 'filename' sanitize. It performs a check to
    ensure that output files do NOT have the same name,
    or illegal chars like:

            ^` ~ " # % & * : < > ? / \\ { | }

    The maximum filename lengh is fixed to 255 characters.

    return a str(string) if warning,
    return None otherwise
    """
    illegal = '^` ~ " # % & * : < > ? / \\ { | }'
    msg_invalid = _('Name has illegal characters like: {0}').format(illegal)
    msg_inuse = _('Name already in use:')

    check = bool(re.search(r"^(?:[^\^\`\~\"\#\%\&\*\:\<\>\?\/\\\{\|\}]"
                           r"{1,255}$)*$", newname))
    if check is not True:
        return f'{msg_invalid}'

    if newname in outputnames:
        return f'{msg_inuse} {newname}'

    return None
# ----------------------------------------------------------------------


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
        get = wx.GetApp()
        self.appdata = get.appset
        self.index = None
        self.parent = parent  # parent is DnDPanel class
        self.data = self.parent.data
        self.file_src = self.parent.file_src
        self.duration = self.parent.duration
        self.outputnames = self.parent.outputnames
        self.errors = {}
        wx.ListCtrl.__init__(self,
                             parent,
                             style=wx.LC_REPORT
                             | wx.LC_SINGLE_SEL,
                             )
    # ----------------------------------------------------------------------#

    def dropUpdate(self, path, newname=None):
        """
        Update list-control during drag and drop.
        Note that the optional 'newname' argument is given by
        the 'on_col_click' method in the 'FileDnD' class to preserve
        the related renames in column 5 of wx.ListCtrl.

        """
        self.index = self.GetItemCount()
        warn = fullpathname_sanitize(path)  # check for fullname sanitize
        if warn:
            self.errors[f'"{path}"'] = warn
            return

        if not [x for x in self.data if x['format']['filename'] == path]:
            probe = ffprobe(path, cmd=self.appdata['ffprobe_cmd'],
                            txtenc=self.appdata['encoding'],
                            hide_banner=None, pretty=None)
            if probe[1]:
                self.errors[f'"{path}"'] = probe[1]
                return

            probe = probe[0]
            self.InsertItem(self.index, str(self.index + 1))
            self.SetItem(self.index, 1, path)

            if 'duration' not in probe['format'].keys():
                self.SetItem(self.index, 2, 'N/A')
                # NOTE these are my custom adds to probe data
                probe['format']['time'] = '00:00:00.000'
                probe['format']['duration'] = 0

            else:
                tdur = probe['format']['duration'].split(':')
                sec, msec = tdur[2].split('.')[0], tdur[2].split('.')[1]
                tdur = f'{tdur[0]}h : {tdur[1]}m : {sec} : {msec}'
                self.SetItem(self.index, 2, tdur)
                probe['format']['time'] = probe.get('format').pop('duration')
                time = time_to_integer(probe.get('format')['time'])
                probe['format']['duration'] = time

            media = probe['streams'][0]['codec_type']
            formatname = probe['format']['format_long_name']
            self.SetItem(self.index, 3, f'{media}: {formatname}')
            self.SetItem(self.index, 4, probe['format']['size'])
            if newname:
                self.SetItem(self.index, 5, newname)
                self.outputnames.append(newname)
            else:
                fname = os.path.splitext(os.path.basename(path))[0]
                self.SetItem(self.index, 5, fname)
                self.outputnames.append(fname)
            self.index += 1
            self.data.append(probe)
            self.file_src.append(path)
            self.duration.append(probe['format']['duration'])
            # self.parent.statusbar_msg('', None)
            self.parent.changes_in_progress()
        else:
            mess = _("Duplicate file, it has already been added to the list.")
            self.errors[f'"{path}"'] = mess
    # ----------------------------------------------------------------------#

    def rejected_files(self):
        """
        Handles all rejected files if any
        """
        if self.errors:
            with ListWarning(self,
                             self.errors,
                             caption=_('Error list'),
                             header=_('Rejected files'),
                             buttons='OK',
                             ) as log:
                log.ShowModal()
            self.errors.clear()  # clear values here


class FileDrop(wx.FileDropTarget):
    """
    This is the file drop target class
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
        self.window.rejected_files()  # call parent.rejected_files at end

        return True
    # ----------------------------------------------------------------------#


class FileDnD(wx.Panel):
    """
    This panel hosts a listctrl for Drag AND Drop actions on which
    you can add new files, select them, remove them, play them,
    sort them or remove them from the listctrl.

    """
    # CONSTANTS:
    YELLOW = '#bd9f00'
    BLACK = '#060505'  # black for background status bar
    ORANGE = '#f28924'

    def __init__(self, parent, *args):
        """
        Constructor. This will initiate with an id and a title
        """
        get = wx.GetApp()  # get data from bootstrap
        self.appdata = get.appset
        self.themecolor = self.appdata['colorscheme']
        self.parent = parent  # parent is the MainFrame
        self.outputnames = args[0]
        self.data = args[1]
        self.file_src = args[2]
        self.duration = args[3]
        self.sortingstate = None  # ascending or descending order

        wx.Panel.__init__(self, parent, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((0, 25))
        # This builds the list control box:
        self.flCtrl = MyListCtrl(self)  # class MyListCtr
        # Establish the listctrl as a drop target:
        file_drop_target = FileDrop(self.flCtrl)
        self.flCtrl.SetDropTarget(file_drop_target)  # Make drop target.
        # populate columns
        colw = self.appdata['filedrop_column_width']
        self.flCtrl.InsertColumn(0, '#', width=colw[0])
        self.flCtrl.InsertColumn(1, _('Source file'), width=colw[1])
        self.flCtrl.InsertColumn(2, _('Duration'), width=colw[2])
        self.flCtrl.InsertColumn(3, _('Media type'), width=colw[3])
        self.flCtrl.InsertColumn(4, _('Size'), width=colw[4])
        self.flCtrl.InsertColumn(5, _('Destination file name'), width=colw[5])
        # create widgets
        infomsg = _("Drag one or more files below")
        self.lbl_info = wx.StaticText(self, wx.ID_ANY, label=infomsg)
        sizer.Add(self.lbl_info, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add((0, 10))
        sizer.Add(self.flCtrl, 1, wx.EXPAND | wx.ALL, 2)
        sizer.Add((0, 10))
        sizer_outdir = wx.BoxSizer(wx.HORIZONTAL)
        lblsave = wx.StaticText(self, wx.ID_ANY, label=_("Save to:"))
        sizer_outdir.Add(lblsave, 0, wx.LEFT | wx.RIGHT | wx.CENTRE, 2)
        self.btn_destpath = wx.Button(self, wx.ID_OPEN, _('Change'),
                                      name='button destpath filedrop')
        self.text_path_save = wx.TextCtrl(self, wx.ID_ANY, "",
                                          style=wx.TE_PROCESS_ENTER
                                          | wx.TE_READONLY,
                                          )
        sizer_outdir.Add(self.text_path_save, 1, wx.LEFT
                         | wx.RIGHT
                         | wx.EXPAND, 2,
                         )
        sizer_outdir.Add(self.btn_destpath, 0, wx.LEFT | wx.CENTER, 2)
        sizer.Add(sizer_outdir, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)

        if self.appdata['ostype'] == 'Darwin':
            self.lbl_info.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            lblsave.SetFont(wx.Font(13, wx.SWISS, wx.NORMAL, wx.BOLD))
        else:
            self.lbl_info.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            lblsave.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

        # ---- Tooltips
        self.btn_destpath.SetToolTip(_('Set a new destination folder for '
                                       'encodings'))
        self.text_path_save.SetToolTip(_("Encodings destination folder"))

        # ---- Binding (EVT)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.flCtrl)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect, self.flCtrl)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.on_col_click, self.flCtrl)
        self.Bind(wx.EVT_CONTEXT_MENU, self.onContext)

        self.on_file_save(self.appdata['outputdir'])
        pub.subscribe(self.text_information, "SET_DRAG_AND_DROP_TOPIC")
    # ----------------------------------------------------------------------

    def onContext(self, event):
        """
        Create and show a Context Menu
        """
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID1"):
            popupID5 = wx.ID_ANY
            popupID1 = wx.ID_ANY
            popupID2 = wx.ID_ANY
            popupID3 = wx.ID_ANY
            popupID4 = wx.ID_ANY
            self.Bind(wx.EVT_MENU, self.onPopup, id=popupID5)
            self.Bind(wx.EVT_MENU, self.onPopup, id=popupID1)
            self.Bind(wx.EVT_MENU, self.onPopup, id=popupID2)
            self.Bind(wx.EVT_MENU, self.onPopup, id=popupID3)
            self.Bind(wx.EVT_MENU, self.onPopup, id=popupID4)
        # build the menu
        menu = wx.Menu()
        playfile = menu.Append(popupID5, _("Play file"))
        menu.AppendSeparator()
        rename = menu.Append(popupID2, _("Rename selected file\tCtrl+R"))
        rename_batch = menu.Append(popupID1, _("Batch rename files\tCtrl+B"))
        menu.AppendSeparator()
        delfile = menu.Append(popupID3, _("Remove selected entry\tDEL"))
        clearall = menu.Append(popupID4, _("Clear list\tShift+DEL"))
        # Enabling the correct items
        if self.outputnames:
            clearall.Enable(True)
            if len(self.outputnames) > 1:
                rename_batch.Enable(True)
            else:
                rename_batch.Enable(False)
            if self.parent.filedropselected:
                playfile.Enable(True)
                rename.Enable(True)
                delfile.Enable(True)
            else:
                playfile.Enable(False)
                rename.Enable(False)
                delfile.Enable(False)
        else:
            playfile.Enable(False)
            rename.Enable(False)
            rename_batch.Enable(False)
            delfile.Enable(False)
            clearall.Enable(False)

        # show the popup menu
        self.PopupMenu(menu)
        menu.Destroy()
    # ----------------------------------------------------------------------

    def onPopup(self, event):
        """
        Evaluate the label string of the menu item selected
        and starts the related process
        """
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)

        if menuItem.GetItemLabel() == _("Rename selected file\tCtrl+R"):
            self.renaming_file()

        elif menuItem.GetItemLabel() == _("Batch rename files\tCtrl+B"):
            if len(self.outputnames) > 1:
                self.renaming_batch_files()

        elif menuItem.GetItemLabel() == _("Remove selected entry\tDEL"):
            self.on_delete_selected(None)

        elif menuItem.GetItemLabel() == _("Clear list\tShift+DEL"):
            self.delete_all(event)  # need pass event here

        elif menuItem.GetItemLabel() == _("Play file"):
            self.on_play_select(None)
    # ----------------------------------------------------------------------

    def text_information(self, topic):
        """
        Set informative properties on selected topic.
        This method is called using pub/sub protocol
        "SET_DRAG_AND_DROP_TOPIC".
        """
        if topic in ('Presets Manager', 'Audio/Video Conversions'):
            self.lbl_info.SetLabel(_('Drag one or more files below'))

        elif topic == 'Concatenate Demuxer':
            self.lbl_info.SetLabel(_('Drag two or more Audio/Video '
                                     'files below'))

        elif topic == 'Image Sequence to Video':
            self.lbl_info.SetLabel(_('Drag one or more Image files below'))

        elif topic == 'Video to Pictures':
            self.lbl_info.SetLabel(_('Drag one or more Video files below'))
    # ----------------------------------------------------------------------

    def on_col_click(self, event):
        """
        Sort items by LEFT clicking on column headers
        (from ascending to descending and back to ascending).
        For this feature is required to delete all items from
        listctrl and data list before re-loading the same
        items with the new sorted order using `dropUpdate` method.

        if plane to use wx.EVT_LIST_COL_RIGHT_CLICK event:
            `if event.GetEventType() == wx.EVT_LIST_COL_RIGHT_CLICK.typeId:`
                `curritems.reverse()`
        see: <https://discuss.wxpython.org/t/event-geteventtype/22860/4>
        """
        count = self.flCtrl.GetItemCount()
        curritems = []
        if count > 1:
            if event.GetColumn() in (0, -1):
                return

            for x in range(count):
                curritems.append((self.flCtrl.GetItemText(x, col=1),
                                  self.flCtrl.GetItemText(x, col=2),
                                  self.flCtrl.GetItemText(x, col=3),
                                  self.flCtrl.GetItemText(x, col=4),
                                  self.flCtrl.GetItemText(x, col=5),
                                  ))
            if event.GetColumn() == 1:
                curritems.sort(key=lambda item: item[0])
            elif event.GetColumn() == 2:
                curritems.sort(key=lambda item: item[1])
            elif event.GetColumn() == 3:
                curritems.sort(key=lambda item: item[2])
            elif event.GetColumn() == 4:
                curritems.sort(key=lambda item:
                               to_bytes(''.join(item[3].split())))
            elif event.GetColumn() == 5:
                curritems.sort(key=lambda item: item[4])

            self.delete_all(None, setstate=False)  # no event, no setstate here

            if self.sortingstate == 'descending':
                self.sortingstate = 'ascending'
            elif self.sortingstate == 'ascending':
                self.sortingstate = 'descending'
            elif not self.sortingstate:
                self.sortingstate = 'ascending'

            if self.sortingstate == 'descending':
                curritems.reverse()

            for data in curritems:
                self.flCtrl.dropUpdate(data[0], data[4])
    # ----------------------------------------------------------------------

    def changes_in_progress(self, setfocus=True):
        """
        Routine operations on changes: receiving new files by
        opening, drag&drop, or removing files or sorting items by
        LEFT clicking on column headers in the ListCtrl.
        """
        self.parent.destroy_orphaned_window()
        self.parent.toolbar.EnableTool(9, True)
        if len(self.outputnames) > 1:
            self.parent.rename_batch.Enable(True)
        else:
            self.parent.rename_batch.Enable(False)
        self.parent.clearall.Enable(True)

        selitem = None

        if setfocus:
            sel = self.flCtrl.GetFocusedItem()  # Get the current row
            selitem = sel if sel != -1 else 0
            self.flCtrl.Focus(selitem)  # make the line the current line
            self.flCtrl.Select(selitem, on=1)  # default event selection

        pub.sendMessage("RESET_ON_CHANGED_LIST", msg=selitem)
    # ----------------------------------------------------------------------

    def on_play_select(self, event):
        """
        Playback the selected file
        """
        if self.flCtrl.GetFirstSelected() == -1:  # None
            wx.MessageBox(_("Have to select an item in the file list first"),
                          'Videomass', wx.ICON_INFORMATION, self)
            return
        index = self.flCtrl.GetFocusedItem()
        item = self.flCtrl.GetItemText(index, 1)

        autoexit = '-autoexit' if self.parent.autoexit else ''
        if self.parent.checktimestamp:
            args = (f'{autoexit} -i "{item}" '
                    f'{self.parent.time_seq} '
                    f'-vf "{self.parent.cmdtimestamp}"')
        else:
            args = f'{autoexit} -i "{item}" {self.parent.time_seq}'
        try:
            with open(item, encoding='utf-8'):
                FilePlay(args)
        except IOError:
            wx.MessageBox(_("Invalid or unsupported file:  %s") % (filepath),
                          "Videomass", wx.ICON_EXCLAMATION, self)
            return
    # ----------------------------------------------------------------------

    def on_delete_selected(self, event):
        """
        Delete a selected file, if nothing is selected return None
        """
        if self.flCtrl.GetFirstSelected() == -1:  # None
            return

        item, indexes = -1, []
        while 1:
            item = self.flCtrl.GetNextItem(item,
                                           wx.LIST_NEXT_ALL,
                                           wx.LIST_STATE_SELECTED)
            indexes.append(item)
            if item == -1:
                indexes.remove(-1)
                break

        if self.flCtrl.GetItemCount() == len(indexes):
            self.delete_all(self)
            return

        for num in sorted(indexes, reverse=True):
            self.flCtrl.DeleteItem(num)  # remove selected items
            self.data.pop(num)  # remove selected items
            self.outputnames.pop(num)  # remove selected items
            self.file_src.pop(num)
            self.duration.pop(num)
            self.flCtrl.Select(num - 1)  # select the previous one
        self.changes_in_progress(setfocus=True)  # reset timeline
        # self.on_deselect(self)  # deselect removed file

        for x in range(self.flCtrl.GetItemCount()):
            self.flCtrl.SetItem(x, 0, str(x + 1))  # re-load counter
        return
    # ----------------------------------------------------------------------

    def delete_all(self, event, setstate=True):
        """
        Clear all lines on the listCtrl and delete
        self.data list. If already empty, return None.
        """
        if self.flCtrl.GetItemCount() == 0:
            return
        # self.flCtrl.ClearAll()
        self.flCtrl.DeleteAllItems()
        del self.data[:]
        del self.outputnames[:]
        del self.file_src[:]
        del self.duration[:]
        if event:
            self.changes_in_progress(setfocus=False)
            self.parent.rename.Enable(False)
            self.parent.rename_batch.Enable(False)
            self.parent.delfile.Enable(False)
            self.parent.clearall.Enable(False)
            self.parent.filedropselected = None
        if setstate:
            self.sortingstate = None
            self.parent.toolbar.EnableTool(9, False)
    # ----------------------------------------------------------------------

    def on_select(self, event):
        """
        Selecting line with mouse or up/down keyboard buttons
        """
        index = self.flCtrl.GetFocusedItem()
        item = self.flCtrl.GetItemText(index, 1)
        self.parent.filedropselected = item
        self.parent.rename.Enable(True)
        self.parent.delfile.Enable(True)
        pub.sendMessage("RESET_ON_CHANGED_LIST", msg=index)
    # ----------------------------------------------------------------------

    def on_deselect(self, event):
        """
        Event to deselect a line when clicking
        in an empty space of the control list
        """
        self.parent.filedropselected = None
        self.parent.rename.Enable(False)
        self.parent.delfile.Enable(False)
        pub.sendMessage("RESET_ON_CHANGED_LIST", msg=None)
    # ----------------------------------------------------------------------

    def on_file_save(self, path):
        """
        Set a specific directory for files saving
        """
        if self.appdata['outputdir_asinput']:
            msg = _('Same destination paths as source files')
            self.text_path_save.SetValue(msg)
            return
        self.text_path_save.SetValue(path)
    # -----------------------------------------------------------------------

    def renaming_file(self):
        """
        This method is responsible for renaming the selected
        output file.
        Names consisting of only whitespaces or tabs or matching
        same name as outputnames are rejected silently.
        """
        if self.flCtrl.GetFirstSelected() == -1:  # None
            wx.MessageBox(_("Have to select an item in the file list first"),
                          'Videomass', wx.ICON_INFORMATION, self)
            return

        row_id = self.flCtrl.GetFocusedItem()  # Get the current row
        oldname = self.flCtrl.GetItemText(row_id, 5)  # Get current name
        newname = ''
        title = _('Rename the file destination')
        msg = _('Rename the selected file to:')

        with Renamer(self,
                     nameprop=oldname,
                     caption=title,
                     message=msg,
                     mode=0,
                     ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                newname = dlg.getvalue()
            else:
                return

        if newname == '' or newname == oldname or newname.isspace():
            self.parent.statusbar_msg(_('Add Files'), None)
            return

        sanitize = filename_sanitize(newname, self.outputnames)
        if sanitize:
            self.parent.statusbar_msg(sanitize, FileDnD.YELLOW, FileDnD.BLACK)
            return

        self.flCtrl.SetItem(row_id, 5, newname)
        self.outputnames[row_id] = newname
        self.parent.statusbar_msg(_('Add Files'), None)
# -----------------------------------------------------------------------

    def renaming_batch_files(self):
        """
        This method is responsible for batch file renaming.
        """
        title = _('Rename in batch')
        msg = _('Rename the {0} items to:').format(len(self.outputnames))
        with Renamer(self,
                     nameprop=_('New Name #'),
                     caption=title,
                     message=msg,
                     mode=len(self.outputnames)
                     ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                newname = dlg.getvalue()
            else:
                return

        for name in newname:
            sanitize = filename_sanitize(name, self.outputnames)
            if sanitize:
                self.parent.statusbar_msg(sanitize, FileDnD.YELLOW,
                                          FileDnD.BLACK)
                return

        for num, name in enumerate(newname):
            self.flCtrl.SetItem(num, 5, name)
            self.outputnames[num] = name

        self.parent.statusbar_msg(_('Add Files'), None)
