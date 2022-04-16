# -*- coding: UTF-8 -*-

"""
Name: presets_manager.py
Porpose: ffmpeg's presets manager panel
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.21.2022
Code checker:
    flake8: --ignore F821, W504
    pylint: --ignore E0602, E1101
########################################################

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
import sys
import wx
import wx.lib.scrolledpanel as scrolled
from videomass.vdms_utils.get_bmpfromsvg import get_bmp
from videomass.vdms_io.presets_manager_properties import json_data
from videomass.vdms_io.presets_manager_properties import supported_formats
from videomass.vdms_io.presets_manager_properties import delete_profiles
from videomass.vdms_io.presets_manager_properties import preserve_old_profiles
from videomass.vdms_io.presets_manager_properties import write_new_profile
from videomass.vdms_utils.utils import copy_restore
from videomass.vdms_utils.utils import copy_on
from videomass.vdms_utils.utils import copydir_recursively
from videomass.vdms_io.checkup import check_files
from videomass.vdms_dialogs import presets_addnew
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

    def __init__(self, parent, path_srcShare, path_confdir,
                 PWD, OS, iconnewprf, icondelprf, iconeditprf, iconcopyprf):
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
        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up
            bmpnewprf = get_bmp(iconnewprf, ((16, 16)))
            bmpeditprf = get_bmp(iconeditprf, ((16, 16)))
            bmpdelprf = get_bmp(icondelprf, ((16, 16)))
            bmpcopyprf = get_bmp(iconcopyprf, ((16, 16)))
        else:
            bmpnewprf = wx.Bitmap(iconnewprf, wx.BITMAP_TYPE_ANY)
            bmpeditprf = wx.Bitmap(iconeditprf, wx.BITMAP_TYPE_ANY)
            bmpdelprf = wx.Bitmap(icondelprf, wx.BITMAP_TYPE_ANY)
            bmpcopyprf = wx.Bitmap(iconcopyprf, wx.BITMAP_TYPE_ANY)

        self.array = []  # Parameters of the selected profile
        self.src_prst = os.path.join(path_srcShare, 'presets')  # origin/share
        self.user_prst = os.path.join(path_confdir, 'presets')  # conf dir
        self.PWD = PWD  # current work of videomass
        self.oS = OS
        self.parent = parent
        self.txtcmdedited = True  # show dlg if cmdline is edited

        prst = sorted([os.path.splitext(x)[0] for x in
                       os.listdir(self.user_prst) if
                       os.path.splitext(x)[1] == '.prst'
                       ])
        wx.Panel.__init__(self, parent, -1)

        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_div = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(sizer_div, 1, wx.EXPAND)
        # ------- BOX PRESETS
        boxpresets = wx.StaticBoxSizer(wx.StaticBox(
            self, wx.ID_ANY, _('Presets')), wx.VERTICAL)
        sizer_div.Add(boxpresets, 0, wx.ALL | wx.EXPAND, 5)
        self.cmbx_prst = wx.ComboBox(self, wx.ID_ANY,
                                     choices=prst,
                                     size=(200, -1),
                                     style=wx.CB_DROPDOWN |
                                     wx.CB_READONLY
                                     )
        boxpresets.Add(self.cmbx_prst, 0, wx.ALL | wx.EXPAND, 5)
        boxpresets.Add((5, 5))
        line0 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        boxpresets.Add(line0, 0, wx.ALL | wx.EXPAND, 5)
        boxpresets.Add((5, 5))
        panelscr = scrolled.ScrolledPanel(self, -1, size=(200, 500),
                                          style=wx.TAB_TRAVERSAL |
                                          wx.BORDER_THEME, name="panelscroll")
        fgs1 = wx.BoxSizer(wx.VERTICAL)
        self.btn_newpreset = wx.Button(panelscr, wx.ID_ANY,
                                       _("New"), size=(-1, -1))
        fgs1.Add(self.btn_newpreset, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_delpreset = wx.Button(panelscr, wx.ID_ANY,
                                       _("Remove"), size=(-1, -1))
        fgs1.Add(self.btn_delpreset, 0, wx.ALL | wx.EXPAND, 5)
        line1 = wx.StaticLine(panelscr, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        fgs1.Add((5, 5))
        fgs1.Add(line1, 0, wx.ALL | wx.EXPAND, 5)
        fgs1.Add((5, 5))
        self.btn_savecopy = wx.Button(panelscr, wx.ID_ANY,
                                      _("Export selected"), size=(-1, -1))
        fgs1.Add(self.btn_savecopy, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_saveall = wx.Button(panelscr, wx.ID_ANY,
                                     _("Export all..."), size=(-1, -1))
        fgs1.Add(self.btn_saveall, 0, wx.ALL | wx.EXPAND, 5)

        line2 = wx.StaticLine(panelscr, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        fgs1.Add((5, 5))
        fgs1.Add(line2, 0, wx.ALL | wx.EXPAND, 5)
        fgs1.Add((5, 5))
        self.btn_restore = wx.Button(panelscr, wx.ID_ANY,
                                     _("Import preset"), size=(-1, -1))
        fgs1.Add(self.btn_restore, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_restoreall = wx.Button(panelscr, wx.ID_ANY,
                                        _("Import group"), size=(-1, -1))
        fgs1.Add(self.btn_restoreall, 0, wx.ALL | wx.EXPAND, 5)

        line3 = wx.StaticLine(panelscr, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        fgs1.Add((5, 5))
        fgs1.Add(line3, 0, wx.ALL | wx.EXPAND, 5)
        fgs1.Add((5, 5))
        self.btn_restoredef = wx.Button(panelscr, wx.ID_ANY,
                                        _("Restore"), size=(-1, -1))
        fgs1.Add(self.btn_restoredef, 0, wx.ALL | wx.EXPAND, 5)

        self.btn_restorealldefault = wx.Button(panelscr, wx.ID_ANY,
                                               _("Restore all..."),
                                               size=(-1, -1)
                                               )
        fgs1.Add(self.btn_restorealldefault, 0, wx.ALL | wx.EXPAND, 5)
        line4 = wx.StaticLine(panelscr, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        fgs1.Add((5, 5))
        fgs1.Add(line4, 0, wx.ALL | wx.EXPAND, 5)
        fgs1.Add((5, 5))
        self.btn_refresh = wx.Button(panelscr, wx.ID_ANY,
                                     _("Reload"), size=(-1, -1))
        fgs1.Add(self.btn_refresh, 0, wx.ALL | wx.EXPAND, 5)
        boxpresets.Add(panelscr, 0, wx.ALL | wx.CENTRE, 5)

        panelscr.SetSizer(fgs1)
        panelscr.SetAutoLayout(1)
        panelscr.SetupScrolling()

        # ------ BOX PROFILES
        # --- listctrl
        self.list_ctrl = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT |
                                     wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL
                                     )
        boxprofiles = wx.StaticBoxSizer(wx.StaticBox(
            self, wx.ID_ANY, _('Profiles')), wx.VERTICAL)
        boxprofiles.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        # --- profile buttons
        grid_profiles = wx.FlexGridSizer(0, 4, 0, 5)
        self.btn_newprofile = wx.Button(self, wx.ID_ANY,
                                        _("Add"), size=(-1, -1))
        self.btn_newprofile.SetBitmap(bmpnewprf, wx.LEFT)
        grid_profiles.Add(self.btn_newprofile, 0, wx.ALL, 0)
        self.btn_delprofile = wx.Button(self, wx.ID_ANY,
                                        _("Delete"), size=(-1, -1))
        self.btn_delprofile.SetBitmap(bmpdelprf, wx.LEFT)
        grid_profiles.Add(self.btn_delprofile, 0, wx.ALL, 0)
        self.btn_editprofile = wx.Button(self, wx.ID_ANY,
                                         _("Edit"), size=(-1, -1))
        self.btn_editprofile.SetBitmap(bmpeditprf, wx.LEFT)
        grid_profiles.Add(self.btn_editprofile, 0, wx.ALL, 0)
        self.btn_copyprofile = wx.Button(self, wx.ID_ANY,
                                         _("Duplicate"), size=(-1, -1))
        self.btn_copyprofile.SetBitmap(bmpcopyprf, wx.LEFT)
        grid_profiles.Add(self.btn_copyprofile, 0, wx.ALL, 0)
        boxprofiles.Add(grid_profiles, 0, wx.ALL, 5)
        sizer_div.Add(boxprofiles, 1, wx.ALL | wx.EXPAND, 5)

        # ------- command line
        grd_cmd = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(grd_cmd, 0, wx.EXPAND)
        box_cmd1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY,
                                                  _("One-Pass")),
                                     wx.VERTICAL
                                     )
        grd_cmd.Add(box_cmd1, 1, wx.ALL | wx.EXPAND, 5)
        self.txt_1cmd = wx.TextCtrl(self, wx.ID_ANY, "",
                                    size=(-1, 120), style=wx.TE_MULTILINE |
                                    wx.TE_PROCESS_ENTER
                                    )
        box_cmd1.Add(self.txt_1cmd, 1, wx.ALL | wx.EXPAND, 5)

        box_cmd2 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY,
                                                  _("Two-Pass")), wx.VERTICAL
                                     )
        grd_cmd.Add(box_cmd2, 1, wx.ALL | wx.EXPAND, 5)
        self.txt_2cmd = wx.TextCtrl(self, wx.ID_ANY, "",
                                    size=(-1, 120), style=wx.TE_MULTILINE |
                                    wx.TE_PROCESS_ENTER
                                    )
        box_cmd2.Add(self.txt_2cmd, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer_base)
        self.Layout()

        # ----------------------Set Properties----------------------#
        if OS == 'Darwin':
            self.txt_1cmd.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
            self.txt_2cmd.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
        else:
            self.txt_1cmd.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD))
            self.txt_2cmd.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD))

        # ------- tipips
        self.cmbx_prst.SetToolTip(_("Choose a preset and view its profiles"))
        tip = (_("Create a new profile and save it in the selected preset"))
        self.btn_newprofile.SetToolTip(tip)
        self.btn_delprofile.SetToolTip(_("Delete the selected profile"))
        self.btn_editprofile.SetToolTip(_("Edit the selected profile"))
        tip = (_("Create a new preset"))
        self.btn_newpreset.SetToolTip(tip)
        tip = (_("Remove the selected preset from the Presets Manager"))
        self.btn_delpreset.SetToolTip(tip)
        tip = (_("Export selected preset as copy"))
        self.btn_savecopy.SetToolTip(tip)
        tip = (_("Export entire presets folder as copy"))
        self.btn_saveall.SetToolTip(tip)
        tip = (_("Import a new preset or update an existing one"))
        self.btn_restore.SetToolTip(tip)
        tip = (_("Import a group of presets from a folder and update "
                 "existing ones"))
        self.btn_restoreall.SetToolTip(tip)
        tip = (_("Replace the selected preset with the Videomass default one"))
        self.btn_restoredef.SetToolTip(tip)
        tip = (_("Retrieve all Videomass default presets"))
        self.btn_restorealldefault.SetToolTip(tip)
        self.btn_refresh.SetToolTip(_("Update the presets list"))
        tip = (_('First pass of the selected profile'))
        self.txt_1cmd.SetToolTip(tip)
        tip = (_('Second pass of the selected profile'))
        self.txt_2cmd.SetToolTip(tip)

        # ----------------------Binder (EVT)----------------------#
        self.Bind(wx.EVT_COMBOBOX, self.on_choice_profiles, self.cmbx_prst)
        self.Bind(wx.EVT_BUTTON, self.profile_add, self.btn_newprofile)
        self.Bind(wx.EVT_BUTTON, self.profile_del, self.btn_delprofile)
        self.Bind(wx.EVT_BUTTON, self.profile_edit, self.btn_editprofile)
        self.Bind(wx.EVT_BUTTON, self.profile_copy, self.btn_copyprofile)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.list_ctrl)
        self.list_ctrl.Bind(wx.EVT_CONTEXT_MENU, self.onContext)
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
        self.set_listctrl()
    # ----------------------------------------------------------------------

    def onContext(self, event):
        """
        Create and show a Context Menu on list_ctrl
        """
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID6"):
            popupID6 = wx.ID_ANY
            popupID7 = wx.ID_ANY
            popupID8 = wx.ID_ANY
            popupID9 = wx.ID_ANY
            self.Bind(wx.EVT_MENU, self.onPopup, id=popupID6)
            self.Bind(wx.EVT_MENU, self.onPopup, id=popupID7)
            self.Bind(wx.EVT_MENU, self.onPopup, id=popupID8)
            self.Bind(wx.EVT_MENU, self.onPopup, id=popupID9)
        # build the menu
        menu = wx.Menu()
        menu.Append(popupID6,  _("Add"))
        menu.Append(popupID7, _("Edit"))
        menu.Append(popupID9, _("Duplicate"))
        menu.AppendSeparator()
        menu.Append(popupID8, _("Delete"))
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
        # item = self.list_ctrl.GetFocusedItem()

        if menuItem.GetItemLabel() == _("Add"):
            self.profile_add(self)
        elif menuItem.GetItemLabel() == _("Edit"):
            self.profile_edit(self)
        elif menuItem.GetItemLabel() == _("Delete"):
            self.profile_del(self)
        elif menuItem.GetItemLabel() == _("Duplicate"):
            self.profile_copy(self)
    # ------------------------------------------------------------------#

    def reset_list(self, reset_cmbx=False):
        """
        Clear all data and re-load new one. Used by selecting
        new preset and add/edit/delete profiles events.

        """
        if reset_cmbx:
            prst = sorted([os.path.splitext(x)[0] for x in
                          os.listdir(self.user_prst) if
                          os.path.splitext(x)[1] == '.prst'])
            self.cmbx_prst.Clear()
            self.cmbx_prst.AppendItems(prst)
            self.cmbx_prst.SetSelection(0)

        self.list_ctrl.ClearAll()
        self.txt_1cmd.SetValue("")
        self.txt_2cmd.SetValue("")

        if self.array:
            del self.array[0:6]
        self.set_listctrl()
    # ----------------------------------------------------------------#

    def set_listctrl(self):
        """
        Populates Presets list with JSON data from *.prst files.
        See presets_manager_properties.py
        """
        self.list_ctrl.InsertColumn(0, _('Name'), width=250)
        self.list_ctrl.InsertColumn(1, _('Description'), width=350)
        self.list_ctrl.InsertColumn(2, _('Output Format'), width=200)
        self.list_ctrl.InsertColumn(3, _('Supported Format List'), width=220)

        path = os.path.join(f'{self.user_prst}',
                            f'{self.cmbx_prst.GetValue()}.prst'
                            )
        collections = json_data(path)
        if collections == 'error':
            return
        try:
            index = 0
            for name in collections:
                index += 1
                rows = self.list_ctrl.InsertItem(index, name['Name'])
                self.list_ctrl.SetItem(rows, 0, name['Name'])
                self.list_ctrl.SetItem(rows, 1, name["Description"])
                self.list_ctrl.SetItem(rows, 2, name["Output_extension"])
                self.list_ctrl.SetItem(rows, 3, name["Supported_list"])
        except KeyError as err:
            wx.MessageBox(_('ERROR: Typing error on JSON keys: {}\n\n'
                            'File: "{}"\nkey malformed ?'.format(err, path)),
                          "Videomass", wx.ICON_ERROR, self)
            return
    # ----------------------Event handler (callback)----------------------#

    def on_choice_profiles(self, event):
        """
        Combobox event.

        """
        self.reset_list()
        self.parent.statusbar_msg(f'{self.cmbx_prst.GetValue()}', None)
    # ------------------------------------------------------------------#

    def on_select(self, event):  # list_ctrl
        """
        By selecting a profile in the list_ctrl set new request
        data in to the appropriate objects and sets parameters
        to the text boxes.

        """
        path = os.path.join(f'{self.user_prst}',
                            f'{self.cmbx_prst.GetValue()}.prst'
                            )
        collections = json_data(path)
        selected = event.GetText()  # event.GetText is a Name Profile
        self.txt_1cmd.SetValue("")
        self.txt_2cmd.SetValue("")

        del self.array[0:6]  # delete all: [0],[1],[2],[3],[4],[5]

        try:
            for name in collections:
                if selected == name["Name"]:  # profile name
                    self.array.append(name["Name"])
                    self.array.append(name["Description"])
                    self.array.append(name["First_pass"])
                    self.array.append(name["Second_pass"])
                    self.array.append(name["Supported_list"])
                    self.array.append(name["Output_extension"])

        except KeyError as err:
            wx.MessageBox(_('ERROR: Typing error on JSON keys: {}\n\n'
                            'File: "{}"\nkey malformed ?'.format(err, path)),
                          "Videomass", wx.ICON_ERROR, self)
            return

        self.txt_1cmd.AppendText(f'{self.array[2]}')  # cmd1 text ctrl
        if self.array[3]:
            self.txt_2cmd.Enable()
            self.txt_2cmd.AppendText(f'{self.array[3]}')  # cmd2 text ctrl
        else:
            self.txt_2cmd.Disable()

        sel = f'{self.cmbx_prst.GetValue()} - {self.array[0]}'
        self.parent.statusbar_msg(sel, None)
    # ------------------------------------------------------------------#

    def preset_new(self, event):
        """
        Create new empty preset '*.prst' on /presets path name

        """
        filename = None
        with wx.FileDialog(self, _("Enter name for new preset"),
                           defaultDir=self.user_prst,
                           wildcard="Videomass presets (*.prst;)|*.prst;",
                           style=wx.FD_SAVE |
                           wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            filename = f"{fileDialog.GetPath()}.prst"
            try:
                with open(filename, 'w', encoding='utf8') as file:
                    file.write('[]')
            except IOError:
                wx.LogError(_("Cannot save current "
                            "data in file '{}'.").format(filename))
                return
        if filename:
            wx.MessageBox(_("'Successful!\n\n"
                            "A new empty preset has been created."),
                          "Videomass ", wx.ICON_INFORMATION, self)

            self.reset_list(True)
    # ------------------------------------------------------------------#

    def preset_del(self, event):
        """
        Remove or delete a preset '*.prst' on /presets path name
        and move on Removals folder

        """
        filename = self.cmbx_prst.GetValue()
        if wx.MessageBox(_('Are you sure you want to remove "{}" preset?\n\n '
                           'It will be moved to the "Removals" subfolder '
                           'of the presets folder.').format(filename),
                         _('Please confirm'), wx.ICON_QUESTION |
                         wx.YES_NO, self) == wx.NO:
            return

        try:
            if not os.path.exists(os.path.join(self.user_prst, 'Removals')):
                os.mkdir(os.path.join(self.user_prst, 'Removals'))
        except OSError as err:
            wx.MessageBox(_("{}\n\nSorry, removal failed, cannot "
                            "continue..").format(err),
                          "Videomass", wx.ICON_ERROR, self
                          )
            return

        s = os.path.join(self.user_prst, f'{filename}.prst')
        d = os.path.join(self.user_prst, 'Removals', f'{filename}.prst')
        os.replace(s, d)

        wx.MessageBox(_('The preset "{0}" was successfully '
                        'removed').format(filename), "Videomass",
                      wx.ICON_ERROR, self
                      )
        self.reset_list(True)
    # ------------------------------------------------------------------#

    def preset_export(self, event):
        """
        save one preset on media

        """
        combvalue = self.cmbx_prst.GetValue()
        filedir = f'{self.user_prst}/{combvalue}.prst'

        dlg = wx.DirDialog(self, _("Choose a folder to save the selected "
                                   "preset"), "", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if os.path.exists(os.path.join(path, f'{combvalue}.prst')):
                if wx.MessageBox(_('A file with this name already exists, '
                                   'do you want to overwrite it?'),
                                 _('Please confirm'),
                                 wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                    return

            status = copy_restore(filedir,
                                  os.path.join(path, f'{combvalue}.prst'))
            dlg.Destroy()

            if status:
                wx.MessageBox(f'{status}', "Videomass", wx.ICON_ERROR, self)
                return
            wx.MessageBox(_("The preset was exported successfully"),
                          "Videomass", wx.OK, self)
    # ------------------------------------------------------------------#

    def preset_export_all(self, event):
        """
        Save the presets directory on media

        """
        src = self.user_prst

        dialsave = wx.DirDialog(self, _("Choose a folder to export all "
                                        "presets"), "", wx.DD_DEFAULT_STYLE)
        if dialsave.ShowModal() == wx.ID_OK:
            dest = dialsave.GetPath()
            status = copydir_recursively(src, dest, 'Videomass-Presets-copy')
            dialsave.Destroy()
            if status:
                wx.MessageBox(f'{status}', "Videomass", wx.ICON_ERROR, self)
            else:
                wx.MessageBox(_("All presets have been exported successfully"),
                              "Videomass", wx.OK, self)
    # ------------------------------------------------------------------#

    def preset_import(self, event):
        """
        Import a new preset. If the preset already exists you will
        be asked to overwrite it or not.

        """
        wildcard = "Source (*.prst)|*.prst| All files (*.*)|*.*"

        with wx.FileDialog(self, _("Import a new preset"),
                           "", "", wildcard, wx.FD_OPEN |
                           wx.FD_FILE_MUST_EXIST) as filedlg:

            if filedlg.ShowModal() == wx.ID_CANCEL:
                return

            newincoming = filedlg.GetPath()
            new = os.path.basename(newincoming)

        if not newincoming.endswith('.prst'):
            wx.MessageBox(_('Error, invalid preset: "{}"').format(
                                    os.path.basename(newincoming)),
                          "Videomass", wx.ICON_ERROR, self
                          )
            return

        if os.path.exists(os.path.join(self.user_prst, new)):

            if wx.MessageBox(_("This preset already exists and is about to be "
                               "updated. Don't worry, it will keep all your "
                               "saved profiles.\n\n"
                               "Do you want to continue?"),
                             _('Please confirm'), wx.ICON_QUESTION |
                             wx.YES_NO, self) == wx.NO:
                return

            preserve_old_profiles(newincoming,
                                  os.path.join(self.user_prst, new)
                                  )
        status = copy_restore(newincoming, os.path.join(self.user_prst, new))
        if status:
            wx.MessageBox(f'{status}', "Videomass", wx.ICON_ERROR, self)
            return

        self.reset_list(True)  # reload presets
        wx.MessageBox(_("A new preset was successfully imported"),
                      "Videomass", wx.OK, self)
    # ------------------------------------------------------------------#

    def preset_import_all(self, event):
        """
        Import all presets previously saved in a folder and replaces
        the existing ones

        """
        if wx.MessageBox(_("This will update the presets database. "
                           "Don't worry, it will keep all your saved "
                           "profiles.\n\nDo you want to continue?"),
                         _("Please confirm"), wx.ICON_QUESTION |
                         wx.YES_NO, self) == wx.NO:
            return

        dialsave = wx.DirDialog(self, _("Import a new presets folder"),
                                "", style=wx.DD_DEFAULT_STYLE
                                )
        if dialsave.ShowModal() == wx.ID_CANCEL:
            return
        source = dialsave.GetPath()
        dialsave.Destroy()

        incoming = [n for n in os.listdir(source) if n.endswith('.prst')]
        outcoming = [n for n in os.listdir(self.user_prst)
                     if n.endswith('.prst')]

        #  Return a new set with elements common to the set and all others.
        for f in set(incoming).intersection(outcoming):
            preserve_old_profiles(os.path.join(source, f),
                                  os.path.join(self.user_prst, f)
                                  )
        outerror = copy_on('prst', source, self.user_prst)

        if outerror:
            wx.MessageBox(f"{outerror}", "Videomass", wx.ICON_ERROR, self)
        else:
            wx.MessageBox(_("The presets database has been successfully "
                            "updated"), "Videomass", wx.OK, self)
            self.reset_list(True)
    # ------------------------------------------------------------------#

    def preset_default(self, event):
        """
        Replace the selected preset at default values.

        """
        if wx.MessageBox(_("Be careful! The selected preset will be "
                           "overwritten with the default one. Your profiles "
                           "may be deleted!\n\nDo you want to continue?"),
                         _("Warning"),
                         wx.ICON_WARNING | wx.YES_NO | wx.CANCEL,
                         self) == wx.YES:

            filename = self.cmbx_prst.GetValue()
            status = copy_restore(f'{self.user_prst}/{filename}.prst',
                                  f'{self.user_prst}/{filename}.prst'
                                  )
            if status:
                wx.MessageBox(_('Sorry, this preset is not part '
                                'of default Videomass presets.'),
                              "Videomass", wx.ICON_ERROR, self
                              )
                return

            wx.MessageBox(_("Successful recovery"), "Videomass", wx.OK, self)
            self.reset_list()  # reload presets
    # ------------------------------------------------------------------#

    def preset_default_all(self, event):
        """
        restore all preset files directory

        """
        if wx.MessageBox(_("Be careful! This action will restore all presets "
                           "to default ones. Your profiles may be deleted!"
                           "\n\nDo you want to continue?"), _("Warning"),
                         wx.ICON_WARNING | wx.YES_NO | wx.CANCEL,
                         self) == wx.YES:

            outerror = copy_on('prst', self.src_prst, self.user_prst)
            if outerror:
                wx.MessageBox(f"{outerror}", "Videomass", wx.ICON_ERROR, self)
            else:
                wx.MessageBox(_("All default presets have been "
                                "successfully recovered"),
                              "Videomass", wx.OK, self)
                self.reset_list(True)
    # ------------------------------------------------------------------#

    def presets_refresh(self, event):
        """
        Force to to re-charging
        """
        self.reset_list(True)

    # ------------------------------------------------------------------#
    def profile_add(self, event):
        """
        Store new profiles in the selected preset

        """
        filename = self.cmbx_prst.GetValue()
        title = _('Create a new profile on "{}" preset').format(filename)

        prstdialog = presets_addnew.MemPresets(self,
                                               'newprofile',
                                               filename,
                                               None,
                                               title)
        ret = prstdialog.ShowModal()

        if ret == wx.ID_OK:
            self.reset_list()  # re-charging list_ctrl with newer
    # ------------------------------------------------------------------#

    def profile_edit(self, event):
        """
        Edit an existing profile

        """
        if not self.array:
            self.parent.statusbar_msg(_("First select a profile in the list"),
                                      PrstPan.YELLOW, PrstPan.BLACK)
            return

        filename = self.cmbx_prst.GetValue()
        title = _('Edit profile of the "{}" preset').format(filename)
        prstdialog = presets_addnew.MemPresets(self,
                                               'edit',
                                               filename,
                                               self.array,
                                               title)
        ret = prstdialog.ShowModal()
        if ret == wx.ID_OK:
            self.reset_list()  # re-charging list_ctrl with newer
    # ------------------------------------------------------------------#

    def profile_copy(self, event):
        """
        Copy (duplicate) selected profile
        """
        if not self.array:
            self.parent.statusbar_msg(_("First select a profile in the list"),
                                      PrstPan.YELLOW, PrstPan.BLACK)
            return
        filename = os.path.join(f'{self.user_prst}',
                                f'{self.cmbx_prst.GetValue()}.prst'
                            )
        newprst = write_new_profile(filename,
                                    Name=f'{self.array[0]} (duplicated)',
                                    Description=self.array[1],
                                    First_pass=self.array[2],
                                    Second_pass=self.array[3],
                                    Supported_list=self.array[4],
                                    Output_extension=self.array[5],
                                    )
        if newprst is None:
            self.reset_list()
    # ------------------------------------------------------------------#

    def profile_del(self, event):
        """
        Delete a selected profile

        """
        if not self.array:
            self.parent.statusbar_msg(_("First select a profile in the list"),
                                      PrstPan.YELLOW, PrstPan.BLACK)
            return

        if wx.MessageBox(_("Are you sure you want to delete the "
                           "selected profile? It will no longer be "
                           "possible to recover it."), _("Please confirm"),
                         wx.ICON_WARNING | wx.YES_NO | wx.CANCEL,
                         self) == wx.YES:

            filename = os.path.join(f'{self.user_prst}',
                                f'{self.cmbx_prst.GetValue()}.prst'
                                )
            delete_profiles(filename, self.array[0])
            self.reset_list()
    # ------------------------------------------------------------------#

    def on_start(self):
        """
        File data redirecting .

        """
        if not self.array:
            self.parent.statusbar_msg(_("First select a profile in the list"),
                                      PrstPan.YELLOW, PrstPan.BLACK)
            return

        if(self.array[2].strip() != self.txt_1cmd.GetValue().strip() or
           self.array[3].strip() != self.txt_2cmd.GetValue().strip()):
            if self.txtcmdedited:

                msg = _("The selected profile command has been "
                        "changed manually.\n"
                        "Do you want to apply it "
                        "during the conversion process?")
                dlg = wx.RichMessageDialog(self, msg,
                                           _("Please confirm"),
                                           wx.ICON_QUESTION |
                                           wx.YES_NO
                                           )
                dlg.ShowCheckBox(_("Don't show this dialog again"))

                if dlg.ShowModal() == wx.ID_NO:
                    if dlg.IsCheckBoxChecked():
                        # make sure we won't show it again the next time
                        self.txtcmdedited = False
                    return
                if dlg.IsCheckBoxChecked():
                    # make sure we won't show it again the next time
                    self.txtcmdedited = False

        outext = '' if self.array[5] == 'copy' else self.array[5]
        extlst = self.array[4]
        file_src = supported_formats(extlst, self.parent.file_src)
        checking = check_files(file_src,
                               self.parent.outpath_ffmpeg,
                               self.parent.same_destin,
                               self.parent.suffix,
                               outext,
                               )
        if checking is None:
            # not supported, missing files or user has changed his mind
            return
        fsrc, dirdest, cntmax = checking

        if self.array[3]:  # has double pass
            self.two_Pass(fsrc, dirdest, cntmax, outext)

        else:
            self.one_Pass(fsrc, dirdest, cntmax, outext)
    # ----------------------------------------------------------------#

    def one_Pass(self, filesrc, destdir, cntmax, outext):
        """
        Build args string for one pass process
        """
        pass1 = " ".join(self.txt_1cmd.GetValue().split())
        valupdate = self.update_dict(cntmax, 'One passes')
        ending = Formula(self, valupdate[0], valupdate[1], _('Starts'))
        if ending.ShowModal() == wx.ID_OK:
            self.parent.switch_to_processing('onepass',
                                             filesrc,
                                             outext,
                                             destdir,
                                             pass1,
                                             None,
                                             '',
                                             '',
                                             'presets_manager.log',
                                             cntmax,
                                             )
    # ------------------------------------------------------------------#

    def two_Pass(self, filesrc, destdir, cntmax, outext):
        """
        Build args string for two pass process
        """
        pass1 = " ".join(self.txt_1cmd.GetValue().split())
        pass2 = " ".join(self.txt_2cmd.GetValue().split())
        typeproc = 'twopass'
        valupdate = self.update_dict(cntmax, typeproc)
        ending = Formula(self, valupdate[0], valupdate[1], _('Starts'))

        if ending.ShowModal() == wx.ID_OK:
            self.parent.switch_to_processing(typeproc,
                                             filesrc,
                                             outext,
                                             destdir,
                                             None,
                                             [pass1, pass2],
                                             '',
                                             '',
                                             'presets_manager.log',
                                             cntmax,
                                             )
    # --------------------------------------------------------------------#

    def update_dict(self, cntmax, passes):
        """
        Update information before send to epilogue

        """
        if self.parent.time_seq == "-ss 00:00:00.000 -t 00:00:00.000":
            time = _('Unset')
        else:
            t = self.parent.time_seq.split()
            time = _('start  {} | duration  {}').format(t[1], t[3])

        numfile = f"{str(cntmax)} file in queue"

        formula = (_("SUMMARY\n\nQueued File\nPass Encoding\
                     \nProfile Used\nOutput Format\nTime Period"))
        dictions = (f"\n\n{numfile}\n{passes}\n"
                    f"{self.array[0]}\n{self.array[5]}\n{time}"
                    )
        return formula, dictions
