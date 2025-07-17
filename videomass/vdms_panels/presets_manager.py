# -*- coding: UTF-8 -*-

"""
Name: presets_manager.py
Porpose: ffmpeg's presets manager panel
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: July.17.2025
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
import time
import os
import sys
import wx
from videomass.vdms_utils.get_bmpfromsvg import get_bmp
from videomass.vdms_utils.presets_manager_utils import json_data
from videomass.vdms_utils.presets_manager_utils import supported_formats
from videomass.vdms_utils.presets_manager_utils import delete_profiles
from videomass.vdms_utils.presets_manager_utils import update_oudated_profiles
from videomass.vdms_utils.presets_manager_utils import write_new_profile
from videomass.vdms_utils.utils import copy_restore
from videomass.vdms_utils.utils import copy_on
from videomass.vdms_utils.utils import copydir_recursively
from videomass.vdms_utils.utils import copy_missing_data
from videomass.vdms_utils.utils import update_timeseq_duration
from videomass.vdms_io.checkup import check_files
from videomass.vdms_dialogs import setting_profiles
from videomass.vdms_dialogs.epilogue import Formula


class PrstPan(wx.Panel):
    """
    Interface for using and managing presets in the FFmpeg syntax.

    """
    # set colour in RGB rappresentetion:
    AZURE_NEON = 158, 201, 232
    # set colour in HTML rappresentetion:
    AZURE = '#15a6a6'  # or rgb form (wx.Colour(217,255,255))
    YELLOW = '#bd9f00'
    RED = '#ea312d'
    ORANGE = '#f28924'
    GREENOLIVE = '#8aab3c'
    GREEN = '#268826'
    LIMEGREEN = '#87A615'
    TROPGREEN = '#15A660'
    WHITE = '#fbf4f4'  # white for background status bar
    BLACK = '#060505'  # black for background status bar
    # -----------------------------------------------------------------

    def __init__(self, parent):
        """
        Each presets is a JSON file (Javascript object notation) which is
        a list object with a variable number of items (called profiles)
        of type <class 'dict'>, each of which collect 5 keys object in
        the following form:

        {'Name': "",
        "Descritpion": "",
        "First_pass": "",
        "Second_pass": "",
        "Supported_list": "",
        "Output_extension": "",
        }
        """
        self.parent = parent  # parent is the MainFrame
        get = wx.GetApp()  # get data from bootstrap
        self.appdata = get.appset
        icons = get.iconset
        self.src_prst = os.path.join(self.appdata['srcdata'], 'presets')
        self.user_prst = os.path.join(self.appdata['confdir'], 'presets')
        self.array = []  # Parameters of the selected profile
        self.txtcmdedited = True  # show warning if cmdline is edited
        self.check_presets_version = False  # see `update_preset_state`

        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up
            bmpnewprf = get_bmp(icons['profile_add'], ((16, 16)))
            bmpeditprf = get_bmp(icons['profile_edit'], ((16, 16)))
            bmpdelprf = get_bmp(icons['profile_del'], ((16, 16)))
            bmpcopyprf = get_bmp(icons['profile_copy'], ((16, 16)))
            bmpdelprst = get_bmp(icons['delpreset'], ((16, 16)))
            bmpexpall = get_bmp(icons['exportall'], ((16, 16)))
            bmpexpsel = get_bmp(icons['exportselected'], ((16, 16)))
            bmpimpdir = get_bmp(icons['importfolder'], ((16, 16)))
            bmpimpprst = get_bmp(icons['importpreset'], ((16, 16)))
            bmpnewprst = get_bmp(icons['newpreset'], ((16, 16)))
            bmpreload = get_bmp(icons['reload'], ((16, 16)))
            bmprestall = get_bmp(icons['restoreall'], ((16, 16)))
            bmprestsel = get_bmp(icons['restoreselected'], ((16, 16)))
        else:
            bmpnewprf = wx.Bitmap(icons['profile_add'], wx.BITMAP_TYPE_ANY)
            bmpeditprf = wx.Bitmap(icons['profile_edit'], wx.BITMAP_TYPE_ANY)
            bmpdelprf = wx.Bitmap(icons['profile_del'], wx.BITMAP_TYPE_ANY)
            bmpcopyprf = wx.Bitmap(icons['profile_copy'], wx.BITMAP_TYPE_ANY)
            bmpdelprst = wx.Bitmap(icons['delpreset'], wx.BITMAP_TYPE_ANY)
            bmpexpall = wx.Bitmap(icons['exportall'], wx.BITMAP_TYPE_ANY)
            bmpexpsel = wx.Bitmap(icons['exportselected'], wx.BITMAP_TYPE_ANY)
            bmpimpdir = wx.Bitmap(icons['importfolder'], wx.BITMAP_TYPE_ANY)
            bmpimpprst = wx.Bitmap(icons['importpreset'], wx.BITMAP_TYPE_ANY)
            bmpnewprst = wx.Bitmap(icons['newpreset'], wx.BITMAP_TYPE_ANY)
            bmpreload = wx.Bitmap(icons['reload'], wx.BITMAP_TYPE_ANY)
            bmprestall = wx.Bitmap(icons['restoreall'], wx.BITMAP_TYPE_ANY)
            bmprestsel = wx.Bitmap(icons['restoreselected'],
                                   wx.BITMAP_TYPE_ANY)

        prst = sorted([os.path.splitext(x)[0] for x in
                       os.listdir(self.user_prst) if
                       os.path.splitext(x)[1] == '.json'
                       ])
        wx.Panel.__init__(self, parent, -1)
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        # ------- BOX PRESETS
        fgs1 = wx.BoxSizer(wx.HORIZONTAL)
        self.cmbx_prst = wx.ComboBox(self, wx.ID_ANY,
                                     choices=prst,
                                     size=(150, -1),
                                     style=wx.CB_DROPDOWN
                                     | wx.CB_READONLY,
                                     )
        fgs1.Add(self.cmbx_prst, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_newpreset = wx.Button(self, wx.ID_ANY, "", size=(40, -1))
        self.btn_newpreset.SetBitmap(bmpnewprst, wx.LEFT)
        fgs1.Add(self.btn_newpreset, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_delpreset = wx.Button(self, wx.ID_ANY, "", size=(40, -1))
        self.btn_delpreset.SetBitmap(bmpdelprst, wx.LEFT)
        fgs1.Add(self.btn_delpreset, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_savecopy = wx.Button(self, wx.ID_ANY, "", size=(40, -1))
        self.btn_savecopy.SetBitmap(bmpexpsel, wx.LEFT)
        fgs1.Add(self.btn_savecopy, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_saveall = wx.Button(self, wx.ID_ANY, "", size=(40, -1))
        self.btn_saveall.SetBitmap(bmpexpall, wx.LEFT)
        fgs1.Add(self.btn_saveall, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_restore = wx.Button(self, wx.ID_ANY, "", size=(40, -1))
        self.btn_restore.SetBitmap(bmpimpprst, wx.LEFT)
        fgs1.Add(self.btn_restore, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_restoreall = wx.Button(self, wx.ID_ANY, "", size=(40, -1))
        self.btn_restoreall.SetBitmap(bmpimpdir, wx.LEFT)
        fgs1.Add(self.btn_restoreall, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_restoredef = wx.Button(self, wx.ID_ANY, "", size=(40, -1))
        self.btn_restoredef.SetBitmap(bmprestsel, wx.LEFT)
        fgs1.Add(self.btn_restoredef, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_restorealldefault = wx.Button(self, wx.ID_ANY,
                                               "", size=(40, -1))
        self.btn_restorealldefault.SetBitmap(bmprestall, wx.LEFT)
        fgs1.Add(self.btn_restorealldefault, 0, wx.ALL | wx.CENTRE, 5)
        self.btn_refresh = wx.Button(self, wx.ID_ANY, "", size=(40, -1))
        self.btn_refresh.SetBitmap(bmpreload, wx.LEFT)
        fgs1.Add(self.btn_refresh, 0, wx.ALL | wx.CENTRE, 5)
        boxprst = wx.StaticBox(self, wx.ID_ANY, _("Presets"))
        boxpresets = wx.StaticBoxSizer(boxprst, wx.VERTICAL)
        sizer_base.Add(boxpresets, 0, wx.ALL | wx.EXPAND, 5)
        boxpresets.Add(fgs1, 0, wx.ALL, 5)
        # ------ LIST CONTROL & BOX PROFILES
        # --- listctrl
        self.lctrl = wx.ListCtrl(self, wx.ID_ANY,
                                 style=wx.LC_REPORT
                                 | wx.SUNKEN_BORDER
                                 | wx.LC_SINGLE_SEL,
                                 )
        # --- profile buttons
        grid_profiles = wx.FlexGridSizer(0, 4, 0, 5)
        self.btn_newprofile = wx.Button(self, wx.ID_ANY,
                                        _("Write"), size=(-1, -1))
        self.btn_newprofile.SetBitmap(bmpnewprf, wx.LEFT)
        grid_profiles.Add(self.btn_newprofile, 0, wx.ALL, 0)
        self.btn_delprofile = wx.Button(self, wx.ID_ANY,
                                        _("Delete"), size=(-1, -1))
        self.btn_delprofile.SetBitmap(bmpdelprf, wx.LEFT)
        self.btn_delprofile.Disable()
        grid_profiles.Add(self.btn_delprofile, 0, wx.ALL, 0)
        self.btn_editprofile = wx.Button(self, wx.ID_ANY,
                                         _("Edit"), size=(-1, -1))
        self.btn_editprofile.SetBitmap(bmpeditprf, wx.LEFT)
        self.btn_editprofile.Disable()
        grid_profiles.Add(self.btn_editprofile, 0, wx.ALL, 0)
        self.btn_copyprofile = wx.Button(self, wx.ID_ANY,
                                         _("Duplicate"), size=(-1, -1))
        self.btn_copyprofile.SetBitmap(bmpcopyprf, wx.LEFT)
        self.btn_copyprofile.Disable()
        grid_profiles.Add(self.btn_copyprofile, 0, wx.ALL, 0)
        boxprofiles = wx.StaticBoxSizer(wx.StaticBox(
            self, wx.ID_ANY, _('Profiles')), wx.VERTICAL)
        boxprofiles.Add(self.lctrl, 1, wx.ALL | wx.EXPAND, 5)
        boxprofiles.Add(grid_profiles, 0, wx.ALL, 5)
        sizer_base.Add(boxprofiles, 1, wx.ALL | wx.EXPAND, 5)
        # ------- command line
        grd_cmd = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(grd_cmd, 0, wx.EXPAND)
        sbox1 = wx.StaticBox(self, wx.ID_ANY, _("One-Pass Encoding"))
        box_cmd1 = wx.StaticBoxSizer(sbox1, wx.VERTICAL)
        grd_cmd.Add(box_cmd1, 1, wx.ALL | wx.EXPAND, 5)
        self.txt_1cmd = wx.TextCtrl(self, wx.ID_ANY, "",
                                    size=(-1, 120), style=wx.TE_MULTILINE
                                    | wx.TE_PROCESS_ENTER,
                                    )
        box_cmd1.Add(self.txt_1cmd, 1, wx.ALL | wx.EXPAND, 5)
        self.pass_1_pre = wx.TextCtrl(self, wx.ID_ANY, "",
                                      style=wx.TE_PROCESS_ENTER,
                                      )
        box_cmd1.Add(self.pass_1_pre, 0, wx.ALL | wx.EXPAND, 5)
        sbox2 = wx.StaticBox(self, wx.ID_ANY, _("Two-Pass Encoding"))
        box_cmd2 = wx.StaticBoxSizer(sbox2, wx.VERTICAL)
        grd_cmd.Add(box_cmd2, 1, wx.ALL | wx.EXPAND, 5)
        self.txt_2cmd = wx.TextCtrl(self, wx.ID_ANY, "",
                                    size=(-1, 120), style=wx.TE_MULTILINE
                                    | wx.TE_PROCESS_ENTER,
                                    )
        box_cmd2.Add(self.txt_2cmd, 1, wx.ALL | wx.EXPAND, 5)
        self.pass_2_pre = wx.TextCtrl(self, wx.ID_ANY, "",
                                      style=wx.TE_PROCESS_ENTER,
                                      )
        box_cmd2.Add(self.pass_2_pre, 0, wx.ALL | wx.EXPAND, 5)

        # ------- tipips
        self.cmbx_prst.SetToolTip(_("Choose a preset and view its profiles"))
        tip = _("Write a new profile and save it in the selected preset")
        self.btn_newprofile.SetToolTip(tip)
        self.btn_delprofile.SetToolTip(_("Delete the selected profile"))
        self.btn_editprofile.SetToolTip(_("Edit the selected profile"))
        self.btn_copyprofile.SetToolTip(_("Duplicate the selected profile"))
        tip = _("Create new preset")
        self.btn_newpreset.SetToolTip(tip)
        tip = _("Remove selected preset")
        self.btn_delpreset.SetToolTip(tip)
        tip = _("Backup selected preset")
        self.btn_savecopy.SetToolTip(tip)
        tip = _("Backup the presets folder")
        self.btn_saveall.SetToolTip(tip)
        tip = _("Restore a preset")
        self.btn_restore.SetToolTip(tip)
        tip = _("Restore a presets folder")
        self.btn_restoreall.SetToolTip(tip)
        tip = _("Resets the selected preset to default values")
        self.btn_restoredef.SetToolTip(tip)
        tip = _("Reset all presets to default values")
        self.btn_restorealldefault.SetToolTip(tip)
        self.btn_refresh.SetToolTip(_("Refresh the presets list"))
        tip = _('FFmpeg arguments for one-pass encoding')
        self.txt_1cmd.SetToolTip(tip)
        tip = _('FFmpeg arguments for two-pass encoding')
        self.txt_2cmd.SetToolTip(tip)
        tip = (_('Any optional arguments to add before input file on the '
                 'one-pass encoding, e.g required names of some hardware '
                 'accelerations like -hwaccel to use with CUDA.'))
        self.pass_1_pre.SetToolTip(tip)
        tip = (_('Any optional arguments to add before input file on the '
                 'two-pass encoding, e.g required names of some hardware '
                 'accelerations like -hwaccel to use with CUDA.'))
        self.pass_2_pre.SetToolTip(tip)

        self.SetSizer(sizer_base)
        self.Layout()

        if self.appdata['ostype'] == 'Darwin':
            self.pass_1_pre.SetFont(wx.Font(10, wx.FONTFAMILY_TELETYPE,
                                            wx.NORMAL, wx.NORMAL))
            self.pass_2_pre.SetFont(wx.Font(10, wx.FONTFAMILY_TELETYPE,
                                            wx.NORMAL, wx.NORMAL))
            self.txt_1cmd.SetFont(wx.Font(10, wx.FONTFAMILY_TELETYPE,
                                          wx.NORMAL, wx.NORMAL))
            self.txt_2cmd.SetFont(wx.Font(10, wx.FONTFAMILY_TELETYPE,
                                          wx.NORMAL, wx.NORMAL))
        else:
            self.pass_1_pre.SetFont(wx.Font(8, wx.FONTFAMILY_TELETYPE,
                                            wx.NORMAL, wx.NORMAL))
            self.pass_2_pre.SetFont(wx.Font(8, wx.FONTFAMILY_TELETYPE,
                                            wx.NORMAL, wx.NORMAL))
            self.txt_1cmd.SetFont(wx.Font(8, wx.FONTFAMILY_TELETYPE,
                                          wx.NORMAL, wx.NORMAL))
            self.txt_2cmd.SetFont(wx.Font(8, wx.FONTFAMILY_TELETYPE,
                                          wx.NORMAL, wx.NORMAL))

        # ----------------------Binder (EVT)----------------------#
        self.Bind(wx.EVT_COMBOBOX, self.on_preset_selection, self.cmbx_prst)
        self.Bind(wx.EVT_BUTTON, self.profile_add, self.btn_newprofile)
        self.Bind(wx.EVT_BUTTON, self.profile_del, self.btn_delprofile)
        self.Bind(wx.EVT_BUTTON, self.profile_edit, self.btn_editprofile)
        self.Bind(wx.EVT_BUTTON, self.profile_copy, self.btn_copyprofile)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.lctrl)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect, self.lctrl)
        self.Bind(wx.EVT_BUTTON, self.preset_new, self.btn_newpreset)
        self.Bind(wx.EVT_BUTTON, self.preset_del, self.btn_delpreset)
        self.Bind(wx.EVT_BUTTON, self.preset_export, self.btn_savecopy)
        self.Bind(wx.EVT_BUTTON, self.preset_export_all, self.btn_saveall)
        self.Bind(wx.EVT_BUTTON, self.preset_import, self.btn_restore)
        self.Bind(wx.EVT_BUTTON, self.preset_default, self.btn_restoredef)
        self.Bind(wx.EVT_BUTTON, self.preset_import_all, self.btn_restoreall)
        self.Bind(wx.EVT_BUTTON, self.preset_default_all,
                  self.btn_restorealldefault)
        self.Bind(wx.EVT_BUTTON, self.presets_refresh, self.btn_refresh)

        # ---------------------------- defaults
        self.cmbx_prst.SetSelection(0),
        self.set_listctrl(self.appdata['prstmng_column_width'])
    # ----------------------------------------------------------------------

    def update_preset_state(self):
        """
        Check the version of the installed presets (inside conf dir).
        If the preset database is updatable, it asks the user for
        his confirmation.
        """
        if self.check_presets_version:
            return

        srctext = os.path.join(self.src_prst, 'version', 'version.txt')
        conftext = os.path.join(self.user_prst, 'version', 'version.txt')
        if not os.path.isfile(conftext) or not os.path.isfile(srctext):
            return

        with open(conftext, "r", encoding='utf-8') as vers:
            confversion = vers.read().strip()
        with open(srctext, "r", encoding='utf-8') as vers:
            srcversion = vers.read().strip()

        old = sum((int(x) for x in confversion.split('.')))
        updated = sum((int(x) for x in srcversion.split('.')))
        self.check_presets_version = True

        if updated > old:
            msg = _('Outdated presets version found: v{1}\n'
                    'A new version is available: v{0}\n\n'
                    'This update provides new presets included on the '
                    'latest versions of Videomass.\n\n'
                    'To avoid data loss and allow for possible recovery, '
                    'the outdated presets folder will be backed up in the '
                    'program configuration directory:\n«{2}»\n\n'
                    'Do you want to perform this '
                    'update now?').format(srcversion,
                                          confversion,
                                          self.appdata["confdir"])
            if wx.MessageBox(msg, _('Please confirm'), wx.ICON_QUESTION
                             | wx.CANCEL | wx.YES_NO, self) != wx.YES:
                return
            err = self.preset_import_all(event=None)
            if err:
                return

            # update version.txt file to latest version
            with open(conftext, "w", encoding='utf-8') as updatevers:
                updatevers.write(f'{srcversion}\n')

            # copies missing file/dir to the destination directory
            copy_missing_data(self.src_prst, self.user_prst)
    # --------------------------------------------------------------------

    def reset_list(self, reset_cmbx=False):
        """
        Clear all data and re-load new one. Used by selecting
        new preset and add/edit/delete profiles events.
        Note, If you have methods to call related to `self.lctrl`,
        do so before calling `ClearAll()` method which deletes
        the pre-set references making the data no longer available.
        """
        if reset_cmbx:
            prst = sorted([os.path.splitext(x)[0] for x in
                          os.listdir(self.user_prst) if
                          os.path.splitext(x)[1] == '.json'])
            self.cmbx_prst.Clear()
            self.cmbx_prst.AppendItems(prst)
            self.cmbx_prst.SetSelection(0)

        # get column widths now before calling ClearAll()
        colw = [self.lctrl.GetColumnWidth(0),
                self.lctrl.GetColumnWidth(1),
                self.lctrl.GetColumnWidth(2),
                self.lctrl.GetColumnWidth(3),
                ]
        self.lctrl.ClearAll()
        self.txt_1cmd.SetValue("")
        self.txt_2cmd.SetValue("")
        self.pass_1_pre.SetValue("")
        self.pass_2_pre.SetValue("")

        if self.array:
            del self.array[0:6]

        self.set_listctrl(colw)
    # ----------------------------------------------------------------#

    def set_listctrl(self, colw):
        """
        Populates Presets list with JSON data files.
        See `presets_manager_utils.py`
        """
        self.lctrl.InsertColumn(0, _('Name'), width=colw[0])
        self.lctrl.InsertColumn(1, _('Description'), width=colw[1])
        self.lctrl.InsertColumn(2, _('Output Format'), width=colw[2])
        self.lctrl.InsertColumn(3, _('Supported Format List'), width=colw[3])

        tofile = os.path.join(self.user_prst,
                              self.cmbx_prst.GetValue() + '.json'
                              )
        collections = json_data(tofile)
        if collections == 'error':
            return
        try:
            index = 0
            for name in collections:
                index += 1
                rows = self.lctrl.InsertItem(index, name['Name'])
                self.lctrl.SetItem(rows, 0, name['Name'])
                self.lctrl.SetItem(rows, 1, name["Description"])
                self.lctrl.SetItem(rows, 2, name["Output_extension"])
                self.lctrl.SetItem(rows, 3, name["Supported_list"])

        except (TypeError, KeyError) as err:
            wx.MessageBox(f"ERROR: {str(err)}.\nInvalid file: «{tofile}»",
                          _('Videomass - Error!'), wx.ICON_ERROR, self)
            return
    # ----------------------Event handler (callback)----------------------#

    def on_preset_selection(self, event):
        """
        Event when user select a preset
        in the presets combobox list.
        """
        self.reset_list()
        self.on_deselect(self, cleardata=False)
        self.parent.statusbar_msg(f'{self.cmbx_prst.GetValue()}', None)
    # ------------------------------------------------------------------#

    def on_deselect(self, event, cleardata=True):
        """
        Event when deselecting a line by clicking
        in an empty space in the control list
        """
        if cleardata:
            self.txt_1cmd.SetValue("")
            self.txt_2cmd.SetValue("")
            self.pass_1_pre.SetValue("")
            self.pass_2_pre.SetValue("")
            del self.array[0:8]  # delete all: [0],[1],[2],[3],[4],[5],[6],[7]
        self.btn_copyprofile.Disable()
        self.btn_delprofile.Disable()
        self.btn_editprofile.Disable()
        self.parent.statusbar_msg("", None)
    # ------------------------------------------------------------------#

    def on_select(self, event):  # lctrl
        """
        Event when selecting a profile in the lctrl,
        this update the request data of the objects.
        """
        tofile = os.path.join(self.user_prst,
                              self.cmbx_prst.GetValue() + '.json'
                              )
        collections = json_data(tofile)
        selected = event.GetText()  # event.GetText is a Name Profile
        self.txt_1cmd.SetValue("")
        self.txt_2cmd.SetValue("")
        self.pass_1_pre.SetValue("")
        self.pass_2_pre.SetValue("")
        self.btn_copyprofile.Enable()
        self.btn_delprofile.Enable()
        self.btn_editprofile.Enable()
        del self.array[0:8]  # delete all: [0],[1],[2],[3],[4],[5],[6],[7]

        try:
            for name in collections:
                if selected == name["Name"]:  # profile name
                    self.array.append(name["Name"])
                    self.array.append(name["Description"])
                    self.array.append(name["First_pass"])
                    self.array.append(name["Second_pass"])
                    self.array.append(name["Supported_list"])
                    self.array.append(name["Output_extension"])
                    self.array.append(name["Preinput_1"])
                    self.array.append(name["Preinput_2"])

        except KeyError as err:
            wx.MessageBox(f'key error {str(err)}\nInvalid file: «{tofile}»',
                          _('Videomass - Error!'), wx.ICON_ERROR, self)
            return

        self.txt_1cmd.AppendText(f'{self.array[2]}')  # cmd1 text ctrl
        self.pass_1_pre.AppendText(f'{self.array[6]}')  # cmd1 text ctrl
        if self.array[3]:
            self.txt_2cmd.Enable()
            self.pass_2_pre.Enable()
            self.txt_2cmd.AppendText(f'{self.array[3]}')  # cmd2 text ctrl
            self.pass_2_pre.AppendText(f'{self.array[7]}')  # cmd1 text ctrl
        else:
            self.txt_2cmd.Disable()
            self.pass_2_pre.Disable()

        sel = f'{self.cmbx_prst.GetValue()} - {self.array[0]}'
        self.parent.statusbar_msg(sel, None)
    # ------------------------------------------------------------------#

    def preset_new(self, event):
        """
        Create new `*.json` empty preset
        """
        filename = None
        with wx.FileDialog(self, _("Enter name for new preset"),
                           defaultDir=self.user_prst,
                           wildcard="Videomass preset (*.json;)|*.json;",
                           style=wx.FD_SAVE
                           | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            fileDialog.SetFilename('New preset.json')
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            filename = fileDialog.GetPath()
            if os.path.splitext(filename)[1].strip() != '.json':
                wx.LogError(_('Invalid file name, make sure to provide a '
                              'valid name including the «.json» extension'))
                return
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write('[]')
            except IOError:
                wx.LogError(_("Cannot save current "
                              "data in file '{}'.").format(filename))
                return
        if filename:
            wx.MessageBox(_("You just successfully created a new preset!"),
                          "Videomass", wx.ICON_INFORMATION, self)

            self.reset_list(True)
            self.on_deselect(self, cleardata=False)
    # ------------------------------------------------------------------#

    def preset_del(self, event):
        """
        Remove selected preset moving to the `Removals` folder
        """
        prstname = self.cmbx_prst.GetValue()
        if wx.MessageBox(_('Are you sure you want to remove "{}" preset?\n\n '
                           'It will be moved to the "Removals" subfolder '
                           'inside the presets folder.').format(prstname),
                         _('Please confirm'), wx.ICON_QUESTION
                         | wx.CANCEL | wx.YES_NO, self) != wx.YES:
            return

        try:
            if not os.path.exists(os.path.join(self.user_prst, 'Removals')):
                os.mkdir(os.path.join(self.user_prst, 'Removals'))
        except OSError as err:
            wx.MessageBox(_("{}\n\nSorry, removal failed, cannot "
                            "continue..").format(err),
                          _('Videomass - Error!'), wx.ICON_ERROR, self
                          )
            return

        s = os.path.join(self.user_prst, prstname + '.json')
        d = os.path.join(self.user_prst, 'Removals', prstname + '.json')
        os.replace(s, d)

        wx.MessageBox(_('The preset "{0}" was successfully '
                        'removed').format(prstname), _('Videomass'),
                      wx.OK, self
                      )
        self.reset_list(True)
        self.on_deselect(self, cleardata=False)
    # ------------------------------------------------------------------#

    def preset_export(self, event):
        """
        save one preset on media
        """
        combvalue = self.cmbx_prst.GetValue()
        tofile = os.path.join(self.user_prst, combvalue + '.json')

        dlg = wx.DirDialog(self, _("Open a destination folder"),
                           "", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if os.path.exists(os.path.join(path, combvalue + '.json')):
                if wx.MessageBox(_('A file with this name already exists, '
                                   'do you want to overwrite it?'),
                                 _('Please confirm'), wx.ICON_QUESTION
                                 | wx.CANCEL | wx.YES_NO, self) != wx.YES:
                    return

            status = copy_restore(tofile,
                                  os.path.join(path, combvalue + '.json'))
            dlg.Destroy()

            if status:
                wx.MessageBox(f'{status}', _('Videomass - Error!'),
                              wx.ICON_ERROR, self)
                return
            wx.MessageBox(_("Backup completed successfully"),
                          "Videomass", wx.OK, self)
    # ------------------------------------------------------------------#

    def preset_export_all(self, event):
        """
        Save the presets directory on media
        """
        src = self.user_prst

        dialsave = wx.DirDialog(self, _("Open a destination folder"),
                                "", wx.DD_DEFAULT_STYLE)
        if dialsave.ShowModal() == wx.ID_OK:
            dest = dialsave.GetPath()
            status = copydir_recursively(src, dest, 'Videomass-presets-backup')
            dialsave.Destroy()
            if status:
                wx.MessageBox(f'{status}', _('Videomass - Error!'),
                              wx.ICON_ERROR, self)
            else:
                wx.MessageBox(_("Backup completed successfully"),
                              "Videomass", wx.OK, self)
    # ------------------------------------------------------------------#

    def preset_import(self, event):
        """
        Import a new preset. If the preset already exists you will
        be asked to overwrite it or not.
        """
        with wx.FileDialog(self, _("Open the preset you want to restore"),
                           defaultDir=os.path.expanduser('~'),
                           wildcard="Videomass preset (*.json;)|*.json;",
                           style=wx.FD_OPEN
                           | wx.FD_FILE_MUST_EXIST) as filedlg:

            if filedlg.ShowModal() == wx.ID_CANCEL:
                return

            newincoming = filedlg.GetPath()
            new = os.path.basename(newincoming)

        if os.path.exists(os.path.join(self.user_prst, new)):

            if wx.MessageBox(_("This preset already exists and is about to be "
                               "updated. Don't worry, it will keep all your "
                               "saved profiles.\n\n"
                               "Do you want to continue?"),
                             _('Please confirm'), wx.ICON_QUESTION
                             | wx.CANCEL | wx.YES_NO, self) != wx.YES:
                return

            update_oudated_profiles(newincoming,
                                    os.path.join(self.user_prst, new))
        status = copy_restore(newincoming, os.path.join(self.user_prst, new))
        if status:
            wx.MessageBox(f'{status}', _('Videomass - Error!'),
                          wx.ICON_ERROR, self)
            return

        self.reset_list(True)  # reload presets
        self.on_deselect(self, cleardata=False)
        wx.MessageBox(_("Restore successful"),
                      "Videomass", wx.OK, self)
    # ------------------------------------------------------------------#

    def preset_import_all(self, event):
        """
        This method depends on the event given as argument: If it is
        `None` it will restore the user's preset directory to the
        directory given by the `source` attribute. Otherwise the
        event will be triggered by clicking on the `Import group`
        button which will have a slightly different behavior. In any
        case it will not overwrite existing presets but will update
        them with missing profiles on the destination files.
        In addition it will copy all other presets that do not yet
        exist on the destination.
        """
        source = self.src_prst
        if event:
            if wx.MessageBox(_("This will update the presets database. "
                               "Don't worry, it will keep all your saved "
                               "profiles.\n\nDo you want to continue?"),
                             _("Please confirm"), wx.ICON_QUESTION
                             | wx.CANCEL | wx.YES_NO, self) != wx.YES:
                return None

            dialsave = wx.DirDialog(self,
                                    _("Open the presets folder to restore"),
                                    "", style=wx.DD_DEFAULT_STYLE)
            if dialsave.ShowModal() == wx.ID_CANCEL:
                return None
            source = dialsave.GetPath()
            dialsave.Destroy()

        # create a dir backup
        datenow = time.strftime('%H%M%S-%a_%d_%B_%Y')
        err = copydir_recursively(self.user_prst, self.appdata['confdir'],
                                  f'presets-{datenow}-Backup')
        if err:
            wx.MessageBox(f'{err}', _('Videomass - Error!'),
                          wx.ICON_ERROR, self)
            return err

        incom = [n for n in os.listdir(source) if n.endswith('.json')]
        outcom = [n for n in os.listdir(self.user_prst) if n.endswith('.json')]

        # Return a new set with elements common to the set and all others.
        # In short, copy only files with matching basenames.
        for f in set(incom).intersection(outcom):
            err = update_oudated_profiles(os.path.join(source, f),
                                          os.path.join(self.user_prst, f))
            if err:
                wx.MessageBox(f"{err}", _('Videomass - Error!'),
                              wx.ICON_ERROR, self)
                return err
        # copies non-existent ones to the destination directory
        if event:  # only `Import group` event
            err = copy_on('json', source, self.user_prst, overw=False)
            if err:
                wx.MessageBox(f"{err}", _('Videomass - Error!'),
                              wx.ICON_ERROR, self)
                return err

        wx.MessageBox(_("The presets database has been successfully "
                        "updated"), "Videomass", wx.OK, self)
        self.reset_list(True)
        self.on_deselect(self, cleardata=False)
        return None
    # ------------------------------------------------------------------#

    def preset_default(self, event):
        """
        Replace the selected preset at default values.
        """
        combvalue = self.cmbx_prst.GetValue()
        sourceprst = os.path.join(self.src_prst, combvalue + '.json')
        userprst = os.path.join(self.user_prst, combvalue + '.json')
        if not os.path.exists(sourceprst) and not os.path.isfile(sourceprst):
            wx.MessageBox(_("The selected preset is not part of Videomass's "
                            "default presets."),
                          "Videomass", wx.ICON_INFORMATION, self)
            return

        msg = _("Be careful! The selected preset will be "
                "overwritten with the default one. Your profiles "
                "may be deleted!\n\nDo you want to continue?"
                )
        if wx.MessageBox(msg, _("Please confirm"),
                         wx.ICON_WARNING
                         | wx.YES_NO
                         | wx.CANCEL,
                         self) == wx.YES:
            status = copy_restore(sourceprst, userprst)
            if status:
                wx.MessageBox(status, _('Videomass - Error!'),
                              wx.ICON_ERROR, self)
                return

            wx.MessageBox(_("Successful recovery"), "Videomass", wx.OK, self)
            self.reset_list()  # reload presets
            self.on_deselect(self, cleardata=False)
    # ------------------------------------------------------------------#

    def preset_default_all(self, event):
        """
        restore all preset files directory
        """
        if wx.MessageBox(_("Be careful! This action will restore all presets "
                           "to default ones. Your profiles may be deleted!\n\n"
                           "In any case, to avoid data loss, the presets "
                           "folder will be backed up in the program's "
                           "configuration directory."
                           "\n\nDo you want to continue?"),
                         _("Please confirm"),
                         wx.ICON_WARNING | wx.YES_NO | wx.CANCEL,
                         self) == wx.YES:

            if os.path.exists(self.user_prst):
                # create a dir backup
                datenow = time.strftime('%H%M%S-%a_%d_%B_%Y')
                err = os.rename(self.user_prst,
                                f"{self.user_prst}-{datenow}-Backup")
                if err:
                    wx.MessageBox(f'{err}', _('Videomass - Error!'),
                                  wx.ICON_ERROR, self)
                    return

            err = copydir_recursively(self.src_prst, self.appdata['confdir'])
            if err:
                wx.MessageBox(f"{err}", _('Videomass - Error!'),
                              wx.ICON_ERROR, self)
            else:
                wx.MessageBox(_("Successful recovery"),
                              "Videomass", wx.OK, self)
                self.reset_list(True)
                self.on_deselect(self, cleardata=False)
    # ------------------------------------------------------------------#

    def presets_refresh(self, event):
        """
        Force to to re-charging
        """
        self.reset_list(True)
        self.on_deselect(self, cleardata=False)
    # ------------------------------------------------------------------#

    def profile_add(self, event):
        """
        Store new profiles in the selected preset
        """
        selprst = self.cmbx_prst.GetValue()
        tofile = os.path.join(self.user_prst, selprst + '.json')
        title = _('Write profile on «{0}»').format(selprst)
        prstdialog = setting_profiles.SettingProfile(self,
                                                     'newprofile',
                                                     tofile,
                                                     None,
                                                     title,
                                                     )
        ret = prstdialog.ShowModal()
        if ret == wx.ID_OK:
            self.reset_list()  # re-charging lctrl with newer
            self.on_deselect(self, cleardata=False)
    # ------------------------------------------------------------------#

    def profile_edit(self, event):
        """
        Edit an existing profile
        """
        selprst = self.cmbx_prst.GetValue()
        tofile = os.path.join(self.user_prst, selprst + '.json')
        title = _('Edit profile on «{0}»').format(selprst)
        prstdialog = setting_profiles.SettingProfile(self,
                                                     'edit',
                                                     tofile,
                                                     self.array,
                                                     title)
        ret = prstdialog.ShowModal()
        if ret == wx.ID_OK:
            self.reset_list()  # re-charging lctrl with newer
            self.on_deselect(self, cleardata=False)
    # ------------------------------------------------------------------#

    def profile_copy(self, event):
        """
        Copy (duplicate) selected profile
        """
        tofile = os.path.join(self.user_prst,
                              self.cmbx_prst.GetValue() + '.json'
                              )
        newprst = write_new_profile(tofile,
                                    Name=f'{self.array[0]} (duplicated)',
                                    Description=self.array[1],
                                    First_pass=self.array[2],
                                    Second_pass=self.array[3],
                                    Supported_list=self.array[4],
                                    Output_extension=self.array[5],
                                    Preinput_1=self.array[6],
                                    Preinput_2=self.array[7],
                                    )
        if not newprst:
            self.reset_list()
            self.on_deselect(self, cleardata=False)
    # ------------------------------------------------------------------#

    def profile_del(self, event):
        """
        Delete a selected profile

        """
        if wx.MessageBox(_("Are you sure you want to delete the "
                           "selected profile? It will no longer be "
                           "possible to recover it."), _("Please confirm"),
                         wx.ICON_WARNING | wx.YES_NO | wx.CANCEL,
                         self) == wx.YES:

            tofile = os.path.join(self.user_prst,
                                  self.cmbx_prst.GetValue() + '.json'
                                  )
            delete_profiles(tofile, self.array[0])
            self.reset_list()
            self.on_deselect(self, cleardata=False)
    # ------------------------------------------------------------------#

    def check_options(self, index=None):
        """
        Update entries and file check.
        """
        if not self.array:
            self.parent.statusbar_msg(_("First select a profile in the list"),
                                      PrstPan.YELLOW, PrstPan.BLACK)
            return None

        if (self.array[2].strip() != self.txt_1cmd.GetValue().strip()
                or self.array[3].strip() != self.txt_2cmd.GetValue().strip()):
            if self.txtcmdedited:

                msg = _("The selected profile command has been "
                        "changed manually.\n"
                        "Do you want to apply it "
                        "during the conversion process?")
                dlg = wx.RichMessageDialog(self, msg,
                                           _("Please confirm"),
                                           wx.ICON_QUESTION
                                           | wx.CANCEL
                                           | wx.YES_NO,
                                           )
                dlg.ShowCheckBox(_("Don't show this dialog again"))

                if dlg.ShowModal() != wx.ID_YES:
                    if dlg.IsCheckBoxChecked():
                        # make sure we won't show it again the next time
                        self.txtcmdedited = False
                    return None
                if dlg.IsCheckBoxChecked():
                    # make sure we won't show it again the next time
                    self.txtcmdedited = False

        if index is not None:
            infile = [self.parent.file_src[index]]
            outfilenames = [self.parent.outputnames[index]]
        else:
            infile = self.parent.file_src
            outfilenames = self.parent.outputnames

        outext = '' if self.array[5] == 'copy' else self.array[5]
        extlst = self.array[4]
        src = supported_formats(extlst, infile)
        filecheck = check_files(src,
                                self.appdata['outputdir'],
                                self.appdata['outputdir_asinput'],
                                self.appdata['filesuffix'],
                                outext,
                                outfilenames,
                                )
        if not filecheck:
            # not supported, missing files or user has changed his mind
            return None

        return filecheck
    # ----------------------------------------------------------------#

    def get_codec_args(self):
        """
        Get data from encoder panels and set ffmpeg
        command arguments
        """
        if self.array[3]:
            thrtype = 'Two pass'
        else:
            thrtype = 'One pass'

        preinput_1 = " ".join(self.pass_1_pre.GetValue().split())
        preinput_2 = " ".join(self.pass_2_pre.GetValue().split())
        pass1 = " ".join(self.txt_1cmd.GetValue().split())
        pass2 = " ".join(self.txt_2cmd.GetValue().split())
        preset = self.cmbx_prst.GetValue()
        kwargs = {'type': thrtype, 'args': [pass1, pass2],
                  'pre-input-1': preinput_1, 'pre-input-2': preinput_2,
                  'preset name': f'Presets Manager - {preset}',
                  }
        return kwargs
    # ----------------------------------------------------------------#

    def queue_mode(self):
        """
        build queue mode arguments. This method is
        called by `parent.on_add_to_queue`.
        Return a dictionary of data.
        """
        logname = 'Queue Processing.log'
        index = self.parent.file_src.index(self.parent.filedropselected)

        check = self.check_options(index)
        if not check:
            return None

        f_src, f_dest = check[0][0], check[1][0]
        kwargs = self.get_codec_args()
        dur, ss, et = update_timeseq_duration(self.parent.time_seq,
                                              self.parent.duration
                                              )
        kwargs['start-time'], kwargs['end-time'] = ss, et
        kwargs['logname'] = logname
        kwargs['extension'] = '' if self.array[5] == 'copy' else self.array[5]
        kwargs['source'] = f_src
        kwargs['destination'] = f_dest
        kwargs["duration"] = dur[index]

        return kwargs
    # ------------------------------------------------------------------#

    def batch_mode(self):
        """
        build batch mode arguments. This method is called
        by `parent.click_start`
        """
        logname = 'Presets Manager.log'

        check = self.check_options()
        if not check:
            return None

        f_src, f_dest = check
        kwargs = self.get_codec_args()
        dur, ss, et = update_timeseq_duration(self.parent.time_seq,
                                              self.parent.duration
                                              )
        kwargs['start-time'], kwargs['end-time'] = ss, et
        kwargs['extension'] = '' if self.array[5] == 'copy' else self.array[5]

        batchlist = []
        for index in enumerate(self.parent.file_src):
            kw = kwargs.copy()
            kw['source'] = f_src[index[0]]
            kw['destination'] = f_dest[index[0]]
            kw['duration'] = dur[index[0]]
            batchlist.append(kw)

        keyval = self.update_dict(len(self.parent.file_src), **kwargs)
        ending = Formula(self, (700, 200),
                         self.parent.movetotrash,
                         self.parent.emptylist,
                         **keyval,
                         )
        if ending.ShowModal() == wx.ID_OK:
            (self.parent.movetotrash,
             self.parent.emptylist) = ending.getvalue()
            self.parent.switch_to_processing(kwargs["type"],
                                             logname,
                                             datalist=batchlist)
        return None
    # ----------------------------------------------------------------#

    def update_dict(self, cntmax, **kwa):
        """
        Update information before send to epilogue

        """
        passes = '2' if self.array[3] else '1'

        if not self.parent.time_seq:
            sst, endt = _('Same as source'), _('Same as source')
        else:
            sst = kwa["start-time"].split()[1]
            endt = kwa["end-time"].split()[1]

        if self.appdata['outputdir_asinput']:
            dest = _('Same destination paths as source files')
        else:
            dest = self.appdata['outputdir']

        keys = (_("Batch processing items\nDestination\nAutomation/Preset\n"
                  "Encoding passes\nProfile Used\nOutput Format\n"
                  "Start of segment\nClip duration"))
        vals = (f"{cntmax}\n{dest}\n{kwa['preset name']}"
                f"\n{passes}\n{self.array[0]}\n{self.array[5]}\n{sst}\n{endt}"
                )
        return {'key': keys, 'val': vals}
