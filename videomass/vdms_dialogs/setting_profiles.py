# -*- coding: UTF-8 -*-
"""
Name: setting_profiles.py
Porpose: profiles storing and profiles editing dialog
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Apr.06.2024
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
import webbrowser
import wx
from videomass.vdms_utils.presets_manager_utils import write_new_profile
from videomass.vdms_utils.presets_manager_utils import edit_existing_profile


class SettingProfile(wx.Dialog):
    """
    Show dialog to store and edit profiles of a selected preset.

    """
    PASS_1 = _("One-Pass, Do not start with `ffmpeg "
               "-i filename`; do not end with "
               "`output-filename`"
               )
    PASS_2 = _("Two-Pass (optional), Do not start with "
               "`ffmpeg -i filename`; do not end with "
               "`output-filename`"
               )
    SUPFORMAT = _("Supported Formats list (optional). Do not include the `.`")
    OUTFORMAT = _("Output Format. Empty to copy format and codec. "
                  "Do not include the `.`")
    # ------------------------------------------------------------------

    def __init__(self, parent, arg, filename, array, title):
        """
        arg: evaluate if this dialog is used for add new profile or
             edit a existing profiles from three message strings:
        arg = 'newprofile'  from preset manager
        arg = 'edit' from preset manager
        arg = 'addprofile' from video and audio conversions

        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.filename = filename
        self.arg = arg  # evaluate if 'edit', 'newprofile', 'addprofile'
        self.array = array  # param list [name,descript,cmd1,cmd2,supp,ext,..]

        wx.Dialog.__init__(self, parent, -1, title,
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        size_base = wx.BoxSizer(wx.VERTICAL)
        labname = wx.StaticText(self, wx.ID_ANY, _("Profile Name"))
        size_base.Add(labname, 0, wx.ALL | wx.EXPAND, 5)
        self.txt_name = wx.TextCtrl(self, wx.ID_ANY, "")
        size_base.Add(self.txt_name, 0, wx.ALL | wx.EXPAND, 5)
        labdescr = wx.StaticText(self, wx.ID_ANY, _("Description"))
        size_base.Add(labdescr, 0, wx.ALL | wx.EXPAND, 5)
        self.txt_descript = wx.TextCtrl(self, wx.ID_ANY, "", size=(-1, 80),
                                        style=wx.TE_MULTILINE)
        size_base.Add(self.txt_descript, 0, wx.ALL | wx.EXPAND, 5)
        labpass1 = wx.StaticText(self, wx.ID_ANY, SettingProfile.PASS_1)
        size_base.Add(labpass1, 0, wx.ALL | wx.EXPAND, 5)
        self.pass_1_cmd = wx.TextCtrl(self, wx.ID_ANY, "",
                                      style=wx.TE_MULTILINE
                                      )
        size_base.Add(self.pass_1_cmd, 1, wx.ALL | wx.EXPAND, 5)
        labpass2 = wx.StaticText(self, wx.ID_ANY, SettingProfile.PASS_2)
        size_base.Add(labpass2, 0, wx.ALL | wx.EXPAND, 5)
        self.pass_2_cmd = wx.TextCtrl(self, wx.ID_ANY, "",
                                      style=wx.TE_MULTILINE
                                      )
        size_base.Add(self.pass_2_cmd, 1, wx.ALL | wx.EXPAND, 5)
        boxpre1 = wx.BoxSizer(wx.VERTICAL)
        msg = _("Pre-input arguments for One-Pass (optional)")
        labpre1 = wx.StaticText(self, wx.ID_ANY, msg)
        boxpre1.Add(labpre1, 0, wx.ALL | wx.EXPAND, 5)
        self.pass_1_pre = wx.TextCtrl(self, wx.ID_ANY, "")
        boxpre1.Add(self.pass_1_pre, 1, wx.ALL | wx.EXPAND, 5)
        boxpre2 = wx.BoxSizer(wx.VERTICAL)
        msg = _("Pre-input arguments for Two-Pass (optional)")
        labpre2 = wx.StaticText(self, wx.ID_ANY, msg)
        boxpre2.Add(labpre2, 0, wx.ALL | wx.EXPAND, 5)
        self.pass_2_pre = wx.TextCtrl(self, wx.ID_ANY, "")
        boxpre2.Add(self.pass_2_pre, 1, wx.ALL | wx.EXPAND, 5)
        boxpre = wx.BoxSizer(wx.HORIZONTAL)
        boxpre.Add(boxpre1, 1, wx.ALL | wx.EXPAND, 0)
        boxpre.Add(boxpre2, 1, wx.ALL | wx.EXPAND, 0)
        size_base.Add(boxpre, 0, wx.ALL | wx.EXPAND, 0)
        boxsupp = wx.BoxSizer(wx.VERTICAL)
        labsupp = wx.StaticText(self, wx.ID_ANY, SettingProfile.SUPFORMAT)
        boxsupp.Add(labsupp, 0, wx.ALL | wx.EXPAND, 5)
        self.txt_supp = wx.TextCtrl(self, wx.ID_ANY, size=(350, -1), value="")
        boxsupp.Add(self.txt_supp, 0, wx.ALL, 5)
        boxext = wx.BoxSizer(wx.VERTICAL)
        labext = wx.StaticText(self, wx.ID_ANY, SettingProfile.OUTFORMAT)
        boxext.Add(labext, 0, wx.ALL | wx.EXPAND, 5)
        self.txt_ext = wx.TextCtrl(self, wx.ID_ANY, "")
        boxext.Add(self.txt_ext, 0, wx.ALL | wx.SHAPED, 5)
        boxbot = wx.BoxSizer(wx.HORIZONTAL)
        boxbot.Add(boxsupp, 1, wx.ALL | wx.EXPAND, 0)
        boxbot.Add(boxext, 1, wx.ALL | wx.EXPAND, 0)
        size_base.Add(boxbot, 0, wx.ALL | wx.EXPAND, 0)
        # ----- confirm buttons section
        grdBtn = wx.GridSizer(1, 2, 0, 0)
        grdhelp = wx.GridSizer(1, 1, 0, 0)
        btn_help = wx.Button(self, wx.ID_HELP, "")
        grdhelp.Add(btn_help, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grdBtn.Add(grdhelp)
        grdexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_canc = wx.Button(self, wx.ID_CANCEL, "")
        grdexit.Add(btn_canc, 0, wx.ALIGN_CENTER_VERTICAL)
        btn_save = wx.Button(self, wx.ID_OK)
        grdexit.Add(btn_save, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        grdBtn.Add(grdexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=5)
        size_base.Add(grdBtn, 0, wx.EXPAND)

        # ----- set_properties:
        if self.appdata['ostype'] == 'Darwin':
            fontsize = 10
        else:
            fontsize = 8
        self.pass_1_cmd.SetFont(wx.Font(fontsize, wx.FONTFAMILY_TELETYPE,
                                        wx.NORMAL, wx.NORMAL))
        self.pass_2_cmd.SetFont(wx.Font(fontsize, wx.FONTFAMILY_TELETYPE,
                                        wx.NORMAL, wx.NORMAL))
        self.pass_1_pre.SetFont(wx.Font(fontsize, wx.FONTFAMILY_TELETYPE,
                                        wx.NORMAL, wx.NORMAL))
        self.pass_2_pre.SetFont(wx.Font(fontsize, wx.FONTFAMILY_TELETYPE,
                                        wx.NORMAL, wx.NORMAL))

        self.txt_name.SetToolTip(_('A short profile name'))
        self.txt_descript.SetToolTip(_('A long description of the profile'))
        self.pass_1_cmd.SetToolTip(_('FFmpeg arguments for one-pass encoding'))
        self.pass_2_cmd.SetToolTip(_('FFmpeg arguments for two-pass encoding'))
        self.txt_supp.SetToolTip(_('One or more comma-separated format names '
                                   'compatible with this profile'))
        self.txt_ext.SetToolTip(_('Output format extension. Leave empty to '
                                  'copy codec and format'))

        tip = (_('Any optional arguments to add before input file on the '
                 'one-pass encoding, e.g required names of some hardware '
                 'accelerations like -hwaccel to use with CUDA.'))
        self.pass_1_pre.SetToolTip(tip)
        tip = (_('Any optional arguments to add before input file on the '
                 'two-pass encoding, e.g required names of some hardware '
                 'accelerations like -hwaccel to use with CUDA.'))
        self.pass_2_pre.SetToolTip(tip)
        # ------ Set Layout
        self.SetMinSize((850, 600))
        self.SetSizer(size_base)
        self.Fit()
        self.Layout()

        # ----------------------Binder (EVT)----------------------#
        self.Bind(wx.EVT_TEXT, self.on_Name, self.txt_name)
        self.Bind(wx.EVT_TEXT, self.on_Descript, self.txt_descript)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_canc)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_BUTTON, self.on_apply, btn_save)

        # -------------------Binder (EVT) End --------------------#
        if arg == 'edit':
            self.array[5] = '' if array[5] == 'copy' else array[5]
            self.change()
        elif arg == 'addprofile':
            self.pass_1_cmd.AppendText(self.array[0])  # command or param
            self.pass_2_cmd.AppendText(self.array[1])
            self.txt_ext.AppendText(self.array[2])  # extension

    def change(self):
        """
        In edit mode only, paste the array items on text boxes

        """
        self.txt_name.AppendText(self.array[0])  # name
        self.txt_descript.AppendText(self.array[1])  # descript
        self.pass_1_cmd.AppendText(self.array[2])  # command 1
        self.pass_2_cmd.AppendText(self.array[3])  # command 2
        self.txt_supp.AppendText(self.array[4])  # file supportted
        self.txt_ext.AppendText(self.array[5])  # extension
        self.pass_1_pre.AppendText(self.array[6])  # input 1
        self.pass_2_pre.AppendText(self.array[7])  # input 2
    # ---------------------Callbacks (event handler)----------------------#

    def on_Name(self, event):
        """Set default background"""
        if self.txt_name.GetBackgroundColour() == (152, 131, 19, 255):
            # html: ('#988313') == rgb: (152, 131, 19, 255) =
            self.txt_name.SetBackgroundColour(wx.NullColour)
    # ------------------------------------------------------------------#

    def on_Descript(self, event):
        """Set default background"""
        if self.txt_descript.GetBackgroundColour() == (152, 131, 19, 255):
            # html: ('#988313') == rgb: (152, 131, 19, 255) =
            self.txt_descript.SetBackgroundColour(wx.NullColour)
    # ------------------------------------------------------------------#

    def on_help(self, event):
        """
        Open default web browser via Python Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        page = ('https://jeanslack.github.io/Videomass/User-guide/'
                'Presets_Manager_en.pdf')

        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        Close this dialog without saving anything
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def on_apply(self, event):
        """
        Apply changes
        """
        name = self.txt_name.GetValue()
        descript = self.txt_descript.GetValue()
        pass_1 = self.pass_1_cmd.GetValue()
        pass_2 = self.pass_2_cmd.GetValue()
        file_support = self.txt_supp.GetValue().strip()
        extens = self.txt_ext.GetValue().strip()
        extens = 'copy' if not extens else extens
        preinput1 = self.pass_1_pre.GetValue()
        preinput2 = self.pass_2_pre.GetValue()

        # ---------------------------------------------------------------
        if [txt for txt in [name, descript] if txt.strip() == '']:
            if not name.strip():
                self.txt_name.SetBackgroundColour('#988313')
            if not descript.strip():
                self.txt_descript.SetBackgroundColour('#988313')

            wx.MessageBox(_("Incomplete profile assignments"),
                          _('Videomass - Warning!'), wx.ICON_WARNING, self)
            return

        if len(file_support.split()) > 1:
            supp = ''.join(file_support.split())
            if [i for i in supp.split() if ',' not in i]:
                wx.MessageBox(_("Formats must be comma-separated"),
                              _('Videomass - Warning!'), wx.ICON_WARNING, self)
                return

        if self.arg in ('newprofile', 'addprofile'):
            writenewprf = write_new_profile(self.filename,
                                            Name=name.strip(),
                                            Description=descript,
                                            First_pass=pass_1,
                                            Second_pass=pass_2,
                                            Supported_list=file_support,
                                            Output_extension=extens,
                                            Preinput_1=preinput1,
                                            Preinput_2=preinput2,
                                            )
            if writenewprf == 'invalid JSON file':
                msg = (_('ERROR: Keys mismatched for requested data.\n'
                         'Invalid file: «{0}»').format(self.filename))
                wx.MessageBox(msg, _('Videomass - Error!'), wx.STAY_ON_TOP
                              | wx.ICON_ERROR | wx.OK, self)
                return
            if writenewprf == 'already exist':
                wx.MessageBox(_("Profile already stored with same name"),
                              _('Videomass - Warning!'), wx.ICON_WARNING, self)
                return
            if writenewprf is not None:
                wx.MessageBox(writenewprf, _('Videomass - Error!'),
                              wx.ICON_WARNING, self)
                return

            wx.MessageBox(_("Profile stored successfully!"))

        elif self.arg == 'edit':
            editprf = edit_existing_profile(self.filename,
                                            self.array[0],
                                            Name=name.strip(),
                                            Description=descript,
                                            First_pass=pass_1,
                                            Second_pass=pass_2,
                                            Supported_list=file_support,
                                            Output_extension=extens,
                                            Preinput_1=preinput1,
                                            Preinput_2=preinput2,
                                            )
            if editprf == 'already exist':
                wx.MessageBox(_("Profile already stored with same name"),
                              _('Videomass - Warning!'), wx.ICON_WARNING, self)
                return
            wx.MessageBox(_("Profile change successful!"))
            # self.Destroy() # con ID_OK e ID_CANCEL non serve

        event.Skip()
