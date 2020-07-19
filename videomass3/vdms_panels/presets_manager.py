# -*- coding: UTF-8 -*-
# Name: presets_manager.py
# Porpose: ffmpeg's presets manager panel
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.06.2020 *PEP8 compatible*
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
import wx.lib.agw.floatspin as FS
import wx.lib.agw.gradientbutton as GB
from videomass3.vdms_io.presets_manager_properties import json_data
from videomass3.vdms_io.presets_manager_properties import supported_formats
from videomass3.vdms_io.presets_manager_properties import delete_profiles
from videomass3.vdms_utils.utils import copy_restore
from videomass3.vdms_utils.utils import copy_backup
from videomass3.vdms_utils.utils import copy_on
from videomass3.vdms_io.filenames_check import inspect
from videomass3.vdms_dialogs import presets_addnew
from videomass3.vdms_dialogs.epilogue import Formula
from videomass3.vdms_io.IO_tools import volumeDetectProcess
from videomass3.vdms_frames import shownormlist


class PrstPan(wx.Panel):
    """
    Interface for using and managing presets in the FFmpeg syntax.

    """
    # set colour in RGB rappresentetion:
    GREY_DISABLED = 165, 165, 165
    AZURE_NEON = 158, 201, 232
    # set colour in HTML rappresentetion:
    AZURE = '#15a6a6'  # or rgb form (wx.Colour(217,255,255))
    YELLOW = '#a29500'
    RED = '#ea312d'
    ORANGE = '#f28924'
    GREENOLIVE = '#8aab3c'
    GREEN = '#268826'
    LIMEGREEN = '#87A615'
    TROPGREEN = '#15A660'
    # -----------------------------------------------------------------

    def __init__(self, parent, path_srcShare, path_confdir,
                 PWD, OS, iconanalyzes, iconpeaklevel, btn_color,
                 fontBtncolor):
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
        self.array = []  # Parameters of the selected profile
        # default options:
        self.opt = {"PEAK": "", "RMS": "", "EBU": "",
                    "AudioInMap": ['', ''], "AudioOutMap": ['', '']
                    }
        self.src_prst = os.path.join(path_srcShare, 'presets')  # origin/share
        self.user_prst = os.path.join(path_confdir, 'presets')  # conf dir
        self.PWD = PWD  # current work of videomass
        self.oS = OS
        self.parent = parent
        self.txtcmdedited = True  # show dlg if cmdline is edited
        self.normdetails = []
        prst = sorted([os.path.splitext(x)[0] for x in
                       os.listdir(self.user_prst) if
                       os.path.splitext(x)[1] == '.prst'
                       ])
        self.btnC = btn_color  # tollbar buttons color from conf.
        self.fBtnC = fontBtncolor  # Buttons Font Colour from conf.

        wx.Panel.__init__(self, parent, -1)
        """constructor"""
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        self.list_ctrl = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT |
                                     wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL
                                     )
        sizer_base.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 15)
        nb1 = wx.Notebook(self, wx.ID_ANY, style=0)
        sizer_base.Add(nb1, 0, wx.ALL | wx.EXPAND, 15)
        # ------- page presets
        nb1_p1 = wx.Panel(nb1, wx.ID_ANY)
        grd_prst = wx.GridSizer(2, 1, 0, 0)
        lab_prfl = wx.StaticText(nb1_p1, wx.ID_ANY, _("Select a preset from "
                                                      "the drop down:"))
        grd_prst.Add(lab_prfl, 0, wx.ALIGN_CENTER_HORIZONTAL |
                     wx.ALIGN_CENTER_VERTICAL, 0
                     )
        self.cmbx_prst = wx.ComboBox(nb1_p1, wx.ID_ANY,
                                     choices=prst,
                                     size=(200, -1),
                                     style=wx.CB_DROPDOWN |
                                     wx.CB_READONLY
                                     )
        grd_prst.Add(self.cmbx_prst, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        nb1_p1.SetSizer(grd_prst)
        nb1.AddPage(nb1_p1, _("Presets"))
        # ------- page commands
        nb1_p2 = wx.Panel(nb1, wx.ID_ANY)
        grd_cmd = wx.GridSizer(1, 2, 0, 0)
        box_cmd1 = wx.StaticBoxSizer(wx.StaticBox(nb1_p2, wx.ID_ANY,
                                                  _("1-PASS")),
                                     wx.VERTICAL
                                     )
        grd_cmd.Add(box_cmd1, 0, wx.ALL | wx.EXPAND, 15
                    )
        self.txt_1cmd = wx.TextCtrl(nb1_p2, wx.ID_ANY, "",
                                    style=wx.TE_MULTILINE |
                                    wx.TE_PROCESS_ENTER
                                    )
        box_cmd1.Add(self.txt_1cmd, 1, wx.ALL | wx.EXPAND, 15
                     )
        box_cmd2 = wx.StaticBoxSizer(wx.StaticBox(nb1_p2, wx.ID_ANY,
                                                  _("2-PASS")), wx.VERTICAL
                                     )
        grd_cmd.Add(box_cmd2, 0, wx.ALL | wx.EXPAND, 15
                    )
        self.txt_2cmd = wx.TextCtrl(nb1_p2, wx.ID_ANY, "",
                                    style=wx.TE_MULTILINE |
                                    wx.TE_PROCESS_ENTER
                                    )
        box_cmd2.Add(self.txt_2cmd, 1, wx.ALL | wx.EXPAND, 15
                     )
        nb1_p2.SetSizer(grd_cmd)
        nb1.AddPage(nb1_p2, (_("Command line FFmpeg")))
        # ------- page Automations
        self.nb1_p3 = wx.Panel(nb1, wx.ID_ANY)
        size_auto = wx.BoxSizer(wx.HORIZONTAL)
        grd_autosx = wx.FlexGridSizer(2, 1, 5, 5)
        size_auto.Add(grd_autosx, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        self.rdbx_norm = wx.RadioBox(self.nb1_p3, wx.ID_ANY,
                                     (_("Audio Normalization")),
                                     choices=[('Off'), ('PEAK'),
                                              ('RMS'), ('EBU R128'),
                                              ],
                                     majorDimension=1,
                                     style=wx.RA_SPECIFY_ROWS,
                                     )
        grd_autosx.Add(self.rdbx_norm, 0, wx.ALL, 10)

        boxamap = wx.StaticBoxSizer(wx.StaticBox(self.nb1_p3, wx.ID_ANY,
                                                 _("Audio Streams Mapping")),
                                    wx.VERTICAL
                                    )
        grd_autosx.Add(boxamap, 0, wx.ALL | wx.EXPAND, 10)
        grd_map = wx.FlexGridSizer(2, 2, 0, 0)
        boxamap.Add(grd_map, 0, wx.ALL | wx.EXPAND, 5)
        txtAinmap = wx.StaticText(self.nb1_p3, wx.ID_ANY,
                                  _('Input Audio Index')
                                  )
        grd_map.Add(txtAinmap, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        self.cmb_A_inMap = wx.ComboBox(self.nb1_p3, wx.ID_ANY,
                                       choices=['Auto', '1', '2', '3',
                                                '4', '5', '6', '7', '8'],
                                       size=(160, -1), style=wx.CB_DROPDOWN |
                                       wx.CB_READONLY
                                       )
        grd_map.Add(self.cmb_A_inMap, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        txtAoutmap = wx.StaticText(self.nb1_p3, wx.ID_ANY,
                                   _('Output Audio Index')
                                   )
        grd_map.Add(txtAoutmap, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        self.cmb_A_outMap = wx.ComboBox(self.nb1_p3, wx.ID_ANY,
                                        choices=['Auto', 'All', '1', '2', '3',
                                                 '4', '5', '6', '7', '8'],
                                        size=(160, -1), style=wx.CB_DROPDOWN |
                                        wx.CB_READONLY
                                        )
        grd_map.Add(self.cmb_A_outMap, 0, wx.ALL |
                    wx.ALIGN_CENTER_VERTICAL, 10
                    )
        size_panels = wx.BoxSizer(wx.VERTICAL)
        size_auto.Add(size_panels, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        self.peakpanel = wx.Panel(self.nb1_p3, wx.ID_ANY,
                                  style=wx.TAB_TRAVERSAL
                                  )
        sizer_peak = wx.FlexGridSizer(1, 4, 15, 15)
        analyzebmp = wx.Bitmap(iconanalyzes, wx.BITMAP_TYPE_ANY)
        self.btn_voldect = GB.GradientButton(self.peakpanel,
                                             size=(-1, 25),
                                             bitmap=analyzebmp,
                                             label=_("Volumedected"))
        self.btn_voldect.SetBaseColours(startcolour=wx.Colour(PrstPan.AZURE_NEON),
                                        foregroundcolour=wx.Colour(self.fBtnC)
                                        )
        self.btn_voldect.SetBottomEndColour(wx.Colour(self.btnC))
        self.btn_voldect.SetBottomStartColour(wx.Colour(self.btnC))
        self.btn_voldect.SetTopStartColour(wx.Colour(self.btnC))
        self.btn_voldect.SetTopEndColour(wx.Colour(self.btnC))
        sizer_peak.Add(self.btn_voldect, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        peaklevelbmp = wx.Bitmap(iconpeaklevel, wx.BITMAP_TYPE_ANY)
        self.btn_details = GB.GradientButton(self.peakpanel,
                                             size=(-1, 25),
                                             bitmap=peaklevelbmp,
                                             label=_("Volume Statistics")
                                             )
        self.btn_details.SetBaseColours(startcolour=wx.Colour(PrstPan.AZURE_NEON),
                                        foregroundcolour=wx.Colour(self.fBtnC)
                                        )
        self.btn_details.SetBottomEndColour(wx.Colour(self.btnC))
        self.btn_details.SetBottomStartColour(wx.Colour(self.btnC))
        self.btn_details.SetTopStartColour(wx.Colour(self.btnC))
        self.btn_details.SetTopEndColour(wx.Colour(self.btnC))
        sizer_peak.Add(self.btn_details, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.lab_amplitude = wx.StaticText(self.peakpanel, wx.ID_ANY,
                                           (_("Target level:"))
                                           )
        sizer_peak.Add(self.lab_amplitude, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.spin_target = FS.FloatSpin(self.peakpanel, wx.ID_ANY,
                                        min_val=-99.0, max_val=0.0,
                                        increment=0.5, value=-1.0,
                                        agwStyle=FS.FS_LEFT, size=(120, -1)
                                        )
        sizer_peak.Add(self.spin_target, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.spin_target.SetFormat("%f"), self.spin_target.SetDigits(1)
        size_panels.Add(self.peakpanel, 0, wx.ALL | wx.EXPAND, 0)
        self.peakpanel.SetSizer(sizer_peak)  # set panel
        self.ebupanel = wx.Panel(self.nb1_p3, wx.ID_ANY,
                                 style=wx.TAB_TRAVERSAL
                                 )
        sizer_ebu = wx.FlexGridSizer(3, 2, 5, 5)
        self.lab_i = wx.StaticText(self.ebupanel, wx.ID_ANY,
                                   _("Set integrated loudness target:  ")
                                   )
        sizer_ebu.Add(self.lab_i, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.spin_i = FS.FloatSpin(self.ebupanel, wx.ID_ANY,
                                   min_val=-70.0, max_val=-5.0,
                                   increment=0.5, value=-24.0,
                                   agwStyle=FS.FS_LEFT, size=(120, -1)
                                   )
        self.spin_i.SetFormat("%f"), self.spin_i.SetDigits(1)
        sizer_ebu.Add(self.spin_i, 0, wx.ALL, 0)

        self.lab_tp = wx.StaticText(self.ebupanel, wx.ID_ANY,
                                    _("Set maximum true peak:"))
        sizer_ebu.Add(self.lab_tp, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.spin_tp = FS.FloatSpin(self.ebupanel, wx.ID_ANY,
                                    min_val=-9.0, max_val=0.0,
                                    increment=0.5, value=-2.0,
                                    agwStyle=FS.FS_LEFT, size=(120, -1)
                                    )
        self.spin_tp.SetFormat("%f"), self.spin_tp.SetDigits(1)
        sizer_ebu.Add(self.spin_tp, 0, wx.ALL, 0)
        self.lab_lra = wx.StaticText(self.ebupanel, wx.ID_ANY,
                                     _("Set loudness range target:"))
        sizer_ebu.Add(self.lab_lra, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.spin_lra = FS.FloatSpin(self.ebupanel, wx.ID_ANY,
                                     min_val=1.0, max_val=20.0,
                                     increment=0.5, value=7.0,
                                     agwStyle=FS.FS_LEFT, size=(120, -1)
                                     )
        self.spin_lra.SetFormat("%f"), self.spin_lra.SetDigits(1)
        sizer_ebu.Add(self.spin_lra, 0, wx.ALL, 0)
        size_panels.Add(self.ebupanel, 0, wx.ALL | wx.EXPAND, 0)
        self.ebupanel.SetSizer(sizer_ebu)  # set panel
        self.nb1_p3.SetSizer(size_auto)
        nb1.AddPage(self.nb1_p3, _("Automations"))

        self.SetSizer(sizer_base)
        self.Layout()
        # ----------------------Set Properties----------------------#
        if OS == 'Darwin':
            self.txt_1cmd.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
            self.txt_2cmd.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
        else:
            self.txt_1cmd.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD))
            self.txt_2cmd.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD))

        # ------- tooltips
        toolt = (_('First pass parameters of the selected profile'))
        self.txt_1cmd.SetToolTip(toolt)
        toolt = (_('Second pass parameters of the selected profile'))
        self.txt_2cmd.SetToolTip(toolt)
        toolt = (_('Gets maximum volume and average volume data in dBFS, then '
                   'calculates the offset amount for audio normalization.'))
        self.btn_voldect.SetToolTip(toolt)
        toolt = (_('Limiter for the maximum peak level or the mean level '
                   '(when switch to RMS) in dBFS. From -99.0 to +0.0; '
                   'default for PEAK level is -1.0; default for RMS is -20.0'))
        self.spin_target.SetToolTip(toolt)
        toolt = (_('Integrated Loudness Target in LUFS. From -70.0 to '
                   '-5.0, default is -24.0'))
        self.spin_i.SetToolTip(toolt)
        toolt = (_('Maximum True Peak in dBTP. From -9.0 to +0.0, '
                   'default is -2.0'))
        self.spin_tp.SetToolTip(toolt)
        toolt = (_('Loudness Range Target in LUFS. From +1.0 to '
                   '+20.0, default is +7.0'))
        self.spin_lra.SetToolTip(toolt)
        toolt = (_('Choose from video a specific input audio stream to '
                   'work out.'))
        self.cmb_A_inMap.SetToolTip(toolt)
        toolt = (_('Map on the output index. Keep same input map if saving '
                   'as video; to save as audio select to "all" or "Auto"'))
        self.cmb_A_outMap.SetToolTip(toolt)
        # ----------------------Binder (EVT)----------------------#
        self.Bind(wx.EVT_COMBOBOX, self.on_choice_profiles, self.cmbx_prst)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.list_ctrl)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.parent.click_start,
                  self.list_ctrl
                  )
        self.list_ctrl.Bind(wx.EVT_CONTEXT_MENU, self.onContext)
        self.Bind(wx.EVT_RADIOBOX, self.on_Enable_norm, self.rdbx_norm)
        self.Bind(wx.EVT_BUTTON, self.on_Analyzes, self.btn_voldect)
        self.Bind(wx.EVT_BUTTON, self.on_Show_normlist, self.btn_details)
        self.Bind(wx.EVT_SPINCTRL, self.enter_Amplitude, self.spin_target)
        self.Bind(wx.EVT_COMBOBOX, self.on_audioINstream, self.cmb_A_inMap)
        self.Bind(wx.EVT_COMBOBOX, self.on_audioOUTstream, self.cmb_A_outMap)

        # ---------------------------- defaults
        self.cmbx_prst.SetSelection(0), self.cmb_A_inMap.SetSelection(0)
        self.cmb_A_outMap.SetSelection(1)
        self.set_listctrl()
        self.normalization_default()
    # ------------------------------------------------------------------#

    def normalization_default(self):
        """
        Set default normalization parameters. This method is called by
        main_frame module on MainFrame.switch_audio_conv() during first
        run and when there are changing on dragNdrop panel,
        (like make a clear file list or append new file, etc)

        """
        self.rdbx_norm.SetSelection(0),
        self.peakpanel.Hide(), self.ebupanel.Hide(), self.btn_details.Hide()
        self.spin_target.SetValue(-1.0)
        self.opt["PEAK"], self.opt["EBU"], self.opt["RMS"] = "", "", ""
        del self.normdetails[:]
    # ------------------------------------------------------------------#

    def on_audioINstream(self, event):
        """
        sets the specified audio input stream as index to process e.g.
        for filters volumedected and loudnorm will map 0:N where N is
        digit from 0 to available audio index up to 8.
        See: http://ffmpeg.org/ffmpeg.html#Advanced-options
        When changes this feature affect audio filter peak and rms analyzers
        and then re-enable volume dected button .

        """
        sel = self.cmb_A_inMap.GetValue()
        if sel == 'Auto':
            self.opt["AudioInMap"] = ['', '']
            self.cmb_A_outMap.SetSelection(1)
            self.on_audioOUTstream(self)
        else:
            self.opt["AudioInMap"] = ['-map 0:%s' % sel, sel]
            self.cmb_A_outMap.SetStringSelection(self.cmb_A_inMap.GetValue())
            self.on_audioOUTstream(self)
        if self.rdbx_norm.GetSelection() in [1, 2]:
            if not self.btn_voldect.IsEnabled():
                self.btn_voldect.Enable()
                self.btn_voldect.SetForegroundColour(wx.Colour(self.fBtnC))
    # -------------------------------------------------------------------#

    def on_audioOUTstream(self, event):
        """
        Sets the audio stream index for the output file and sets
        audio codec to specified map.

        """
        sel = self.cmb_A_outMap.GetValue()
        if sel == 'Auto':
            self.opt["AudioOutMap"] = ['', '']
        elif sel == 'All':
            self.opt["AudioOutMap"] = ['-map 0:a?', '']
        else:
            sel = int(sel) - 1
            self.opt["AudioOutMap"] = ['-map 0:a%s?' % str(sel),
                                       '%s' % str(sel)
                                       ]
    # ----------------------------------------------------------------------

    def onContext(self, event):
        """
        Create and show a Context Menu on list_ctrl
        """
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID5"):
            self.popupID6 = wx.NewIdRef()
            self.popupID7 = wx.NewIdRef()
            self.popupID8 = wx.NewIdRef()
            self.Bind(wx.EVT_MENU, self.onPopup, id=self.popupID6)
            self.Bind(wx.EVT_MENU, self.onPopup, id=self.popupID7)
            self.Bind(wx.EVT_MENU, self.onPopup, id=self.popupID8)
        # build the menu
        menu = wx.Menu()
        itemOne = menu.Append(self.popupID6,  _("New profile"))
        menu.AppendSeparator()
        itemThree = menu.Append(self.popupID7, _("Edit selected profile"))
        menu.AppendSeparator()
        itemTwo = menu.Append(self.popupID8, _("Delete selected profile"))
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

        if menuItem.GetItemLabel() == _("New profile"):
            self.Addprof()
        elif menuItem.GetItemLabel() == _("Edit selected profile"):
            self.Editprof(self)
        elif menuItem.GetItemLabel() == _("Delete selected profile"):
            self.Delprof()
    # ------------------------------------------------------------------#

    def reset_list(self, reset_cmbx=False):
        """
        Clear all data and re-charging new. Used by selecting new preset
        and add/edit/delete profiles events.

        """
        if reset_cmbx:
            prst = sorted([os.path.splitext(x)[0] for x in
                          os.listdir(self.user_prst) if
                          os.path.splitext(x)[1] == '.prst'])
            self.cmbx_prst.Clear()
            self.cmbx_prst.AppendItems(prst)
            self.cmbx_prst.SetSelection(0)

        self.list_ctrl.ClearAll()
        self.txt_1cmd.SetValue(""), self.txt_2cmd.SetValue("")
        if self.array != []:
            del self.array[0:6]
        self.set_listctrl()
    # ----------------------------------------------------------------#

    def set_listctrl(self):
        """
        Populates Presets list with JSON data from *.prst files.
        See presets_manager_properties.py
        """
        self.list_ctrl.InsertColumn(0, _('Profile Name'), width=250)
        self.list_ctrl.InsertColumn(1, _('Description'), width=350)
        self.list_ctrl.InsertColumn(2, _('Output Format'), width=200)
        self.list_ctrl.InsertColumn(3, _('Supported Formats List'), width=220)

        path = os.path.join('%s' % self.user_prst,
                            '%s.prst' % self.cmbx_prst.GetValue()
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
        self.parent.statusbar_msg('{}'.format(self.cmbx_prst.GetValue()),
                                  None)
    # ------------------------------------------------------------------#

    def on_select(self, event):  # list_ctrl
        """
        By selecting a profile in the list_ctrl set new request
        data in to the appropriate objects and sets parameters
        to the text boxes.

        """
        path = os.path.join('%s' % self.user_prst,
                            '%s.prst' % self.cmbx_prst.GetValue()
                            )
        collections = json_data(path)
        selected = event.GetText()  # event.GetText is a Name Profile
        self.txt_1cmd.SetValue(""), self.txt_2cmd.SetValue("")
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

        self.txt_1cmd.AppendText('%s' % (self.array[2]))  # cmd1 text ctrl
        if self.array[3]:
            self.txt_2cmd.Enable()
            self.txt_2cmd.AppendText('%s' % (self.array[3]))  # cmd2 text ctrl
        else:
            self.txt_2cmd.Disable()

        sel = '{0} - {1}'.format(self.cmbx_prst.GetValue(), self.array[0])
        self.parent.statusbar_msg(sel, None)

    # ------------------------------------------------------------------#
    def on_Enable_norm(self, event):
        """
        Sets a corresponding choice for audio normalization

        """
        msg_1 = (_('Activate peak level normalization, which will produce '
                   'a maximum peak level equal to the set target level.'
                   ))
        msg_2 = (_('Activate RMS-based normalization, which according to '
                   'mean volume calculates the amount of gain to reach same '
                   'average power signal.'
                   ))
        msg_3 = (_('Activate two passes normalization. It Normalizes the '
                   'perceived loudness using the "​loudnorm" filter, which '
                   'implements the EBU R128 algorithm.'
                   ))
        if self.rdbx_norm.GetSelection() in [1, 2]:  # PEAK or RMS

            if self.rdbx_norm.GetSelection() == 1:
                self.parent.statusbar_msg(msg_1, PrstPan.AZURE)
                self.spin_target.SetValue(-1.0)
            else:
                self.parent.statusbar_msg(msg_2, PrstPan.TROPGREEN)
                self.spin_target.SetValue(-20.0)

            self.peakpanel.Show(), self.btn_voldect.Enable()
            self.btn_voldect.SetForegroundColour(wx.Colour(self.fBtnC))
            self.ebupanel.Hide()
            self.opt["PEAK"], self.opt["RMS"], self.opt["EBU"] = "", "", ""
            del self.normdetails[:]

        elif self.rdbx_norm.GetSelection() == 3:  # EBU
            self.parent.statusbar_msg(msg_3, PrstPan.LIMEGREEN)
            self.peakpanel.Hide(), self.ebupanel.Show()
            self.opt["PEAK"], self.opt["RMS"], self.opt["EBU"] = "", "", ""
            del self.normdetails[:]

        else:  # usually it is 0
            self.parent.statusbar_msg(_("Audio normalization off"), None)
            self.normalization_default()

        if self.btn_details.IsShown:
            self.btn_details.Hide()
        self.nb1_p3.Layout()
    # ------------------------------------------------------------------#

    def enter_Amplitude(self, event):
        """
        when spin_amplitude is changed enable 'Volumedected' to
        update new incomming

        """
        if not self.btn_voldect.IsEnabled():
            self.btn_voldect.Enable()
            self.btn_voldect.SetForegroundColour(wx.Colour(self.fBtnC))
    # ------------------------------------------------------------------#

    def on_Analyzes(self, event):
        """
        ** Volumedected button
        - normalizations based on PEAK Analyzes to get MAXIMUM peak levels
          data to calculates offset in dBFS need for audio normalization
          process.
        - normalizations based on RMS Analyzes to get MEAN peak levels data to
          calculates RMS offset in dBFS need for audio normalization process.

        <https://superuser.com/questions/323119/how-can-i-normalize-audio-
        using-ffmpeg?utm_medium=organic>

        """
        msg2 = (_('Audio normalization is required only for some files'))
        msg3 = (_('Audio normalization is not required based to '
                  'set target level'))
        if self.normdetails:
            del self.normdetails[:]

        self.parent.statusbar_msg("", None)
        self.time_seq = self.parent.time_seq  # -ss to -t will be analyzed
        target = self.spin_target.GetValue()

        data = volumeDetectProcess(self.parent.file_src,
                                   self.time_seq,
                                   self.opt["AudioInMap"][0])
        if data[1]:
            wx.MessageBox(data[1], "ERROR! -Videomass", wx.ICON_ERROR)
            return
        else:
            volume = list()
            if self.rdbx_norm.GetSelection() == 1:  # peak Analyzes
                for f, v in zip(self.parent.file_src, data[0]):
                    maxvol = v[0].split(' ')[0]
                    meanvol = v[1].split(' ')[0]
                    offset = float(maxvol) - float(target)
                    result = float(maxvol) - offset
                    if float(maxvol) == float(target):
                        volume.append('  ')
                    else:
                        volume.append("-filter:a:%s volume=%fdB" % (
                                                    self.opt["AudioOutMap"][1],
                                                    -offset))
                    self.normdetails.append((f,
                                             maxvol,
                                             meanvol,
                                             str(offset),
                                             str(result),
                                             ))
            elif self.rdbx_norm.GetSelection() == 2:  # rms Analyzes
                for f, v in zip(self.parent.file_src, data[0]):
                    maxvol = v[0].split(' ')[0]
                    meanvol = v[1].split(' ')[0]
                    offset = float(meanvol) - float(target)
                    result = float(maxvol) - offset
                    if offset == 0.0:
                        volume.append('  ')
                    else:
                        volume.append("-filter:a:%s volume=%fdB" % (
                                                   self.opt["AudioOutMap"][1],
                                                   -offset))
                    self.normdetails.append((f,
                                             maxvol,
                                             meanvol,
                                             str(offset),
                                             str(result),
                                             ))
        if [a for a in volume if '  ' not in a] == []:
            self.parent.statusbar_msg(msg3, PrstPan.ORANGE)
        else:
            if len(volume) == 1 or '  ' not in volume:
                pass
            else:
                self.parent.statusbar_msg(msg2, PrstPan.YELLOW)
        if self.rdbx_norm.GetSelection() == 1:
            self.opt["PEAK"] = volume
        elif self.rdbx_norm.GetSelection() == 2:
            self.opt["RMS"] = volume

        self.btn_voldect.Disable()
        self.btn_voldect.SetForegroundColour(wx.Colour(PrstPan.GREY_DISABLED))
        self.btn_details.Show()
        self.nb1_p3.Layout()
    # ------------------------------------------------------------------#

    def on_Show_normlist(self, event):
        """
        Show a wx.ListCtrl dialog with volumedected data
        """
        if self.rdbx_norm.GetSelection() == 1:  # peak
            title = _('PEAK-based volume statistics')
        if self.rdbx_norm.GetSelection() == 2:  # rms
            title = _('RMS-based volume statistics')

        audionormlist = shownormlist.NormalizationList(title,
                                                       self.normdetails,
                                                       self.oS)
        audionormlist.Show()
    # ------------------------------------------------------------------#

    def New_preset_prst(self):
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
            filename = "%s.prst" % fileDialog.GetPath()
            try:
                with open(filename, 'w') as file:
                    file.write('[]')
            except IOError:
                wx.LogError(_("Cannot save current "
                            "data in file '{}'.").format(filename))
                return
        if filename:
            wx.MessageBox(_("'Successful!\n\n"
                            "A new preset has been created."),
                          "Videomass ", wx.ICON_INFORMATION, self)

            self.reset_list(True)
    # ------------------------------------------------------------------#

    def Del_preset_prst(self):
        """
        Remove or delete a preset '*.prst' on /presets path name
        and move on Removals folder

        """
        filename = self.cmbx_prst.GetValue()
        if wx.MessageBox(_('Are you sure you want to remove "{}" preset?\n\n '
                           'It will be moved to the "Removals" folder in the '
                           'presets directory').format(filename),
                         _('Videomass: Please confirm'), wx.ICON_QUESTION |
                         wx.YES_NO, self) == wx.NO:
            return

        path = os.path.join('%s' % self.user_prst,
                            '%s.prst' % self.cmbx_prst.GetValue()
                            )
        try:  # if exist dir not exit OSError, go...
            if not os.path.exists(os.path.join(self.user_prst, 'Removals')):
                os.mkdir(os.path.join(self.user_prst, 'Removals'))
        except OSError as err:
            wx.MessageBox(_("{}\n\nSorry, removal failed, I can't "
                            "continue.").format(err),
                          "ERROR !", wx.ICON_ERROR, self
                          )
            return
        s = os.path.join(self.user_prst, '%s.prst' % filename)
        d = os.path.join(self.user_prst, 'Removals', '%s.prst' % filename)
        os.replace(s, d)
        self.reset_list(True)

    # ------------------------------------------------------------------#
    def Saveme(self):
        """
        save a file copy preset

        """
        combvalue = self.cmbx_prst.GetValue()
        filedir = '%s/%s.prst' % (self.user_prst, combvalue)
        filename = combvalue

        dialsave = wx.DirDialog(self, _("Select a directory to save it"))
        if dialsave.ShowModal() == wx.ID_OK:
            dirname = dialsave.GetPath()
            copy_backup(filedir, '%s/%s.prst' % (dirname, filename))
            dialsave.Destroy()
            wx.MessageBox(_("Successfully saved"), "Info", wx.OK, self)
    # ------------------------------------------------------------------#

    def Restore(self):
        """
        Replace preset by another

        """
        wildcard = "Source (*.prst)|*.prst| All files (*.*)|*.*"

        dialfile = wx.FileDialog(self, _("Videomass: Choose a videomass "
                                         "preset to restore "), '', "",
                                 wildcard, wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
                                 )
        if dialfile.ShowModal() == wx.ID_OK:
            dirname = dialfile.GetPath()
            tail = os.path.basename(dirname)
            dialfile.Destroy()

            if wx.MessageBox(_("The following preset:\n\n"
                               "'{0}'\n\n"
                               "will be imported and will overwrite "
                               "the one in use.\n"
                               "Proceed ?").format(tail),
                             _('Videomass: Please confirm'),
                             wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return

            copy_restore('%s' % (dirname), '%s/%s' % (self.user_prst, tail))

            self.reset_list(True)  # re-charging functions
    # ------------------------------------------------------------------#

    def Default(self):
        """
        Replace the selected preset at default values.

        """
        if wx.MessageBox(_("The selected preset will be overwritten with "
                           "default profiles!\nproceed?"),
                         _("Videomass: Please confirm"),
                         wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
            return

        filename = self.cmbx_prst.GetValue()
        copy = copy_restore('%s/%s.prst' % (self.src_prst, filename),
                            '%s/%s.prst' % (self.user_prst, filename)
                            )
        if copy:
            wx.MessageBox(_('Sorry, this preset is not part '
                            'of default Videomass presets.'),
                          "ERROR !", wx.ICON_ERROR, self
                          )
            return

        self.reset_list()  # re-charging functions
    # ------------------------------------------------------------------#

    def Default_all(self):
        """
        restore all preset files directory

        """
        if wx.MessageBox(_("WARNING: you are restoring all "
                           "default presets!\nProceed?"),
                         _("Videomass: Please confirm"),
                         wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
            return

        copy_on('prst', self.src_prst, self.user_prst)

        self.reset_list(True)  # re-charging functions
    # ------------------------------------------------------------------#

    def Refresh(self):
        """
        Force to to re-charging
        """
        self.reset_list(True)

    # ------------------------------------------------------------------#
    def Addprof(self):
        """
        Store new profiles in the selected preset

        """
        filename = self.cmbx_prst.GetValue()
        t = _('Create a new profile on "%s" preset') % filename

        prstdialog = presets_addnew.MemPresets(self,
                                               'newprofile',
                                               filename,
                                               None,
                                               t)
        ret = prstdialog.ShowModal()

        if ret == wx.ID_OK:
            self.reset_list()  # re-charging list_ctrl with newer
    # ------------------------------------------------------------------#

    def Editprof(self, event):
        """
        Edit an existing profile

        """
        if self.array == []:
            self.parent.statusbar_msg(_("First select a profile in the list"),
                                      PrstPan.YELLOW)
            return
        else:
            filename = self.cmbx_prst.GetValue()
            t = _('Edit profile of the "%s" preset: ') % (filename)

            prstdialog = presets_addnew.MemPresets(self,
                                                   'edit',
                                                   filename,
                                                   self.array,
                                                   t)
            ret = prstdialog.ShowModal()
            if ret == wx.ID_OK:
                self.reset_list()  # re-charging list_ctrl with newer
    # ------------------------------------------------------------------#

    def Delprof(self):
        """
        Delete a selected profile

        """
        if self.array == []:
            self.parent.statusbar_msg(_("First select a profile in the list"),
                                      PrstPan.YELLOW)
        else:
            filename = self.cmbx_prst.GetValue()
            if wx.MessageBox(_("Are you sure you want to delete the "
                               "selected profile?"),
                             _("Videomass: Please confirm"),
                             wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return

            path = os.path.join('%s' % self.user_prst,
                                '%s.prst' % self.cmbx_prst.GetValue()
                                )
            delete_profiles(path, self.array[0])
            self.reset_list()
    # ------------------------------------------------------------------#

    def on_start(self):
        """
        File data redirecting .

        """
        # check normalization data offset, if enable.
        if self.rdbx_norm.GetSelection() in [1, 2]:  # PEAK or RMS
            if self.btn_voldect.IsEnabled():
                wx.MessageBox(_('Undetected volume values! use the '
                                '"Volumedetect" control button to analyze '
                                'data on the audio volume.'),
                              "Videomass", wx.ICON_INFORMATION
                              )
                return
        self.time_seq = self.parent.time_seq
        dir_destin = self.parent.file_destin
        # used for file name log
        self.logname = 'Videomass_PresetsManager.log'

        # ------------ VALIDAZIONI: --------------
        if self.array == []:
            self.parent.statusbar_msg(_("First select a profile in the list"),
                                      PrstPan.YELLOW)
            return

        if(self.array[2].strip() != self.txt_1cmd.GetValue().strip() or
           self.array[3].strip() != self.txt_2cmd.GetValue().strip()):
            if self.txtcmdedited:

                msg = _("The selected profile command has been "
                        "changed manually.\n"
                        "Do you want to apply it "
                        "during the conversion process?")
                dlg = wx.RichMessageDialog(self, msg,
                                           _("Videomass: Please confirm"),
                                           wx.ICON_QUESTION |
                                           wx.YES_NO
                                           )
                dlg.ShowCheckBox(_("Don't show this dialog again"))

                if dlg.ShowModal() == wx.ID_NO:
                    if dlg.IsCheckBoxChecked():
                        # make sure we won't show it again the next time
                        self.txtcmdedited = False
                    return
                else:
                    if dlg.IsCheckBoxChecked():
                        # make sure we won't show it again the next time
                        self.txtcmdedited = False

        outext = '' if self.array[5] == 'copy' else self.array[5]
        extlst, outext = self.array[4], outext
        file_sources = supported_formats(extlst, self.parent.file_src)
        checking = inspect(file_sources, dir_destin, outext)

        if not checking[0]:
            # not supported, missing files or user has changed his mind
            return
        (batch, file_sources, dir_destin, fname, bname, cntmax) = checking
        # batch: batch or single process
        # fname: filename, nome file senza ext.
        # bname: basename, nome file con ext.
        # cntmax: count items for batch proc.
        if self.array[5] in ['jpg', 'png', 'bmp']:
            self.savepictures(dir_destin, file_sources)
        elif self.array[3]:  # has double pass
            self.two_Pass(file_sources, dir_destin, cntmax, outext)
        else:
            self.one_Pass(file_sources, dir_destin, cntmax, outext)
    # ----------------------------------------------------------------#

    def one_Pass(self, filesrc, destdir, cntmax, outext):
        """

        """
        audnorm = self.opt["RMS"] if not self.opt["PEAK"] else self.opt["PEAK"]
        command = (self.txt_1cmd.GetValue())
        valupdate = self.update_dict(cntmax, 'One passes')
        ending = Formula(self, valupdate[0], valupdate[1], _('Starts'))
        if ending.ShowModal() == wx.ID_OK:
            self.parent.switch_to_processing('onepass',
                                             filesrc,
                                             outext,
                                             destdir,
                                             command,
                                             None,
                                             '',
                                             audnorm,
                                             self.logname,
                                             cntmax,
                                             )
    # ------------------------------------------------------------------#

    def two_Pass(self, filesrc, destdir, cntmax, outext):
        """
        defines two-pass parameters
        """
        pass1 = " ".join(self.txt_1cmd.GetValue().split())
        pass2 = " ".join(self.txt_2cmd.GetValue().split())

        if 'loudnorm=' in pass1:
            if self.rdbx_norm.GetSelection() == 3:
                if wx.MessageBox(_('EBU normalization is enabled twice in '
                                   'automation and command line. Command '
                                   'line has priority.\n\nDo you wish to '
                                   'continue?'),
                                 _("Videomass: Please confirm"),
                                 wx.ICON_QUESTION |
                                 wx.YES_NO, self) == wx.NO:
                    return

            typeproc, audnorm = 'two pass EBU', ''
            loudnorm = [ebu for ebu in pass1.split() if 'loudnorm=' in ebu][0]

        elif self.rdbx_norm.GetSelection() == 3:
            loudnorm = ('loudnorm=I=%s:TP=%s:LRA=%s:print_format=summary' % (
                                            str(self.spin_i.GetValue()),
                                            str(self.spin_tp.GetValue()),
                                            str(self.spin_lra.GetValue())))
            pass1 = '-filter:a: %s ' % loudnorm + '%s' % pass1
            typeproc, audnorm = 'two pass EBU', ''

        else:  # two-pass std
            typeproc, loudnorm = 'twopass', ''
            audnorm = (self.opt["RMS"] if not self.opt["PEAK"]
                       else self.opt["PEAK"]
                       )
        valupdate = self.update_dict(cntmax, typeproc)
        ending = Formula(self, valupdate[0], valupdate[1], _('Starts'))
        if ending.ShowModal() == wx.ID_OK:

            self.parent.switch_to_processing(typeproc,
                                             filesrc,
                                             outext,
                                             destdir,
                                             None,
                                             [pass1, pass2, loudnorm],
                                             self.opt["AudioOutMap"],
                                             audnorm,
                                             self.logname,
                                             cntmax,
                                             )
    # --------------------------------------------------------------------#

    def savepictures(self, dest, file_sources):
        """
        Save as files image the selected video input. The saved
        images are named as file name + a progressive number + .jpg
        and placed in a folder with the same file name + a progressive
        number in the chosen output path.

        """
        if len(file_sources) == 1:
            clicked = file_sources[0]

        elif not self.parent.filedropselected:
            wx.MessageBox(_("To export as pictures, select "
                            "one file at a time"), 'Videomass',
                          wx.ICON_INFORMATION, self
                          )
            return
        else:
            clicked = self.parent.filedropselected

        valupdate = self.update_dict(1, 'None')
        ending = Formula(self, valupdate[0], valupdate[1], _('Starts'))

        if ending.ShowModal() == wx.ID_OK:
            fname = os.path.basename(clicked.rsplit('.', 1)[0])
            dir_destin = dest[file_sources.index(clicked)]  # specified dest

            try:
                outputdir = "%s/%s-IMAGES_1" % (dir_destin, fname)
                os.mkdir(outputdir)

            except FileExistsError:
                lista = []
                for dir_ in os.listdir(dir_destin):
                    if "%s-IMAGES_" % fname in dir_:
                        lista.append(int(dir_.split('IMAGES_')[1]))

                prog = max(lista) + 1
                outputdir = "%s/%s-IMAGES_%d" % (dir_destin, fname, prog)
                os.mkdir(outputdir)

            fileout = "{0}-%d.{1}".format(fname, self.array[5])
            cmd = ('%s -y "%s"' % (self.txt_1cmd.GetValue(),
                                   os.path.join(outputdir, fileout)
                                   ))
            command = " ".join(cmd.split())  # compact string
            self.parent.switch_to_processing('savepictures',
                                             clicked,
                                             None,
                                             None,
                                             command,
                                             None,
                                             None,
                                             None,
                                             self.logname,
                                             1,
                                             False,  # do not use is reserved
                                             )
    # ------------------------------------------------------------------#

    def update_dict(self, cntmax, passes):
        """
        Update information before send to epilogue

        """
        if self.opt["PEAK"]:
            normalize = 'PEAK'
        elif self.opt["RMS"]:
            normalize = 'RMS'
        elif self.opt["EBU"]:
            normalize = 'EBU R128'
        else:
            normalize = _('Off')
        if not self.parent.time_seq:
            time = _('Disable')
        else:
            t = list(self.parent.time_read.items())
            time = '{0}: {1} | {2}: {3}'.format(t[0][0], t[0][1][0],
                                                t[1][0], t[1][1][0])

        numfile = "%s file in pending" % str(cntmax)

        formula = (_("SUMMARY\n\nFile to Queue\nPass Encoding\
                     \nProfile Used\nOutput Format\nAudio Normalization\
                     \nSelected Input Audio index\nAudio Output Map index\
                     \nTime selection"))
        dictions = ("\n\n%s\n%s\n%s\n"
                    "%s\n%s\n%s\n%s\n%s" % (numfile,
                                            passes,
                                            self.array[0],
                                            self.array[5],
                                            normalize,
                                            self.cmb_A_inMap.GetValue(),
                                            self.cmb_A_outMap.GetValue(),
                                            time
                                            ))

        return formula, dictions
