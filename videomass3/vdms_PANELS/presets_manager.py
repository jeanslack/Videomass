# -*- coding: UTF-8 -*-

#########################################################
# Name: presets_pan.py
# Porpose: ffmpeg's presets manager panel
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Dec 28 2018, Aug.28 2019
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
from videomass3.vdms_IO.presets_manager_properties import json_data
from videomass3.vdms_IO.presets_manager_properties import supported_formats
from videomass3.vdms_IO.presets_manager_properties import delete_profiles
from videomass3.vdms_UTILS.utils import copy_restore
from videomass3.vdms_UTILS.utils import copy_backup
from videomass3.vdms_UTILS.utils import copy_on
from videomass3.vdms_IO.filenames_check import inspect
from videomass3.vdms_DIALOGS import presets_addnew
from videomass3.vdms_DIALOGS.epilogue import Formula
from videomass3.vdms_IO.IO_tools import volumeDetectProcess
from videomass3.vdms_FRAMES import shownormlist


cmd_opt = {"PEAK": "", "RMS": "","EBU": "",} # normalization data
array = [] # Parameters of the selected profile

# set widget colours in some case with html rappresentetion:
azure = '#15a6a6'# rgb form (wx.Colour(217,255,255))
yellow = '#a29500'
red = '#ea312d'
orange = '#f28924'
greenolive = '#8aab3c'
green = '#268826'
###################################################################

class PrstPan(wx.Panel):
    """
    Interface for using and managing presets in the FFmpeg syntax. 
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
    def __init__(self, parent, path_srcShare, path_confdir, 
                 PWD, OS, iconanalyzes, iconpeaklevel, btn_color, 
                 fontBtncolor):
        """
        
        """
        self.src_prst = os.path.join(path_srcShare, 'presets')#origin/share
        self.user_prst = os.path.join(path_confdir, 'presets')#conf/videomass
        self.PWD = PWD #current work of videomass
        self.OS = OS
        self.parent = parent
        self.file_src = []
        self.txtcmdedited = False # show dlg if cmdline is edited
        self.normdetails = []
        prst = sorted([os.path.splitext(x)[0] for x in 
                      os.listdir(self.user_prst) if 
                      os.path.splitext(x)[1] == '.prst'])
        self.btnC = btn_color
        self.fBtnC = fontBtncolor

        wx.Panel.__init__(self, parent, -1) 
        """constructor"""

        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        self.list_ctrl = wx.ListCtrl(self.panel_1, wx.ID_ANY, 
                                    style=wx.LC_REPORT| 
                                          wx.SUNKEN_BORDER
                                    )
        nb1 = wx.Notebook(self.panel_1, wx.ID_ANY, style=0)
        nb1_p1 = wx.Panel(nb1, wx.ID_ANY)
        lab_prfl = wx.StaticText(nb1_p1, wx.ID_ANY, _("Select a preset from "
                                                      "the drop down:"))
        self.cmbx_prst = wx.ComboBox(nb1_p1,wx.ID_ANY, 
                                     choices=prst,
                                     size=(200,-1),
                                     style=wx.CB_DROPDOWN | 
                                     wx.CB_READONLY
                                     )
        nb1_p2 = wx.Panel(nb1, wx.ID_ANY)
        labcmd_1 = wx.StaticBox(nb1_p2, wx.ID_ANY, _("First pass parameters"))
        self.txt_1cmd = wx.TextCtrl(nb1_p2, wx.ID_ANY,"", style=wx.TE_MULTILINE| 
                                                          wx.TE_PROCESS_ENTER
                                                          )
        labcmd_2 = wx.StaticBox(nb1_p2, wx.ID_ANY, _("Second pass parameters"))
        self.txt_2cmd = wx.TextCtrl(nb1_p2, wx.ID_ANY,"", style=wx.TE_MULTILINE| 
                                                          wx.TE_PROCESS_ENTER
                                                          )
        #--------------------------------### Audio.
        self.nb1_p3 = wx.Panel(nb1, wx.ID_ANY)
        self.rdbx_norm = wx.RadioBox(self.nb1_p3,wx.ID_ANY,
                                     (_("Audio Normalization")), 
                                     choices=[
                                       ('Off'), 
                                       ('PEAK'), 
                                       ('RMS'),
                                       ('EBU R128'),
                                              ], 
                                     majorDimension=0, 
                                     style=wx.RA_SPECIFY_ROWS,
                                            )
        analyzebmp = wx.Bitmap(iconanalyzes, wx.BITMAP_TYPE_ANY)
        self.btn_analyzes = GB.GradientButton(self.nb1_p3,
                                           size=(-1,25),
                                           bitmap=analyzebmp,
                                           label=_("Volumedected"))
        self.btn_analyzes.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_analyzes.SetBottomEndColour(wx.Colour(self.btnC))
        self.btn_analyzes.SetBottomStartColour(wx.Colour(self.btnC))
        self.btn_analyzes.SetTopStartColour(wx.Colour(self.btnC))
        self.btn_analyzes.SetTopEndColour(wx.Colour(self.btnC))
        
        peaklevelbmp = wx.Bitmap(iconpeaklevel, wx.BITMAP_TYPE_ANY)
        self.btn_details = GB.GradientButton(self.nb1_p3,
                                            size=(-1,25),
                                            bitmap=peaklevelbmp,
                                            label=_("Volume Statistics"))
        self.btn_details.SetBaseColours(startcolour=wx.Colour(158,201,232),
                                    foregroundcolour=wx.Colour(self.fBtnC))
        self.btn_details.SetBottomEndColour(wx.Colour(self.btnC))
        self.btn_details.SetBottomStartColour(wx.Colour(self.btnC))
        self.btn_details.SetTopStartColour(wx.Colour(self.btnC))
        self.btn_details.SetTopEndColour(wx.Colour(self.btnC))
        
        self.lab_amplitude = wx.StaticText(self.nb1_p3, wx.ID_ANY, (
                            _("Target level:")))
        self.spin_target = FS.FloatSpin(self.nb1_p3, wx.ID_ANY, min_val=-99.0, 
                                    max_val=0.0, increment=0.5, value=-1.0, 
                                    agwStyle=FS.FS_LEFT,size=(-1,-1))
        self.spin_target.SetFormat("%f"), self.spin_target.SetDigits(1)
        
        self.lab_i = wx.StaticText(self.nb1_p3, wx.ID_ANY, (
                             _("Set integrated loudness target:  ")))
        self.spin_i = FS.FloatSpin(self.nb1_p3, wx.ID_ANY, min_val=-70.0, 
                                    max_val=-5.0, increment=0.5, value=-24.0, 
                                    agwStyle=FS.FS_LEFT,size=(-1,-1))
        self.spin_i.SetFormat("%f"), self.spin_i.SetDigits(1)
        
        self.lab_tp = wx.StaticText(self.nb1_p3, wx.ID_ANY, (
                                    _("Set maximum true peak:")))
        self.spin_tp = FS.FloatSpin(self.nb1_p3, wx.ID_ANY, min_val=-9.0, 
                                    max_val=0.0, increment=0.5, value=-2.0, 
                                    agwStyle=FS.FS_LEFT,size=(-1,-1))
        self.spin_tp.SetFormat("%f"), self.spin_tp.SetDigits(1)
        
        self.lab_lra = wx.StaticText(self.nb1_p3, wx.ID_ANY, (
                                    _("Set loudness range target:")))
        self.spin_lra = FS.FloatSpin(self.nb1_p3, wx.ID_ANY, min_val=1.0, 
                                    max_val=20.0, increment=0.5, value=7.0, 
                                    agwStyle=FS.FS_LEFT,size=(-1,-1))
        self.spin_lra.SetFormat("%f"), self.spin_lra.SetDigits(1)
        
        #----------------------Set Properties----------------------#
        if OS == 'Darwin':
            self.txt_1cmd.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
            self.txt_2cmd.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
        else:
            self.txt_1cmd.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD))
            self.txt_2cmd.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD))
        
        self.txt_1cmd.SetMinSize((430, 100))
        self.txt_2cmd.SetMinSize((430, 100))    
        #self.list_ctrl.SetBackgroundColour(azure)
        #------- tooltips
        self.txt_1cmd.SetToolTip(_('First pass parameters of the '
                                    'selected profile'))
        self.txt_2cmd.SetToolTip(_('Second pass parameters of the '
                                    'selected profile'))
        self.btn_analyzes.SetToolTip(_('Gets maximum volume and average volume '
                'data in dBFS, then calculates the offset amount for audio '
                'normalization.'))
        self.spin_target.SetToolTip(_('Limiter for the maximum peak level or '
                'the mean level (when switch to RMS) in dBFS. From -99.0 to '
                '+0.0; default for PEAK level is -1.0; default for RMS is '
                '-20.0'))
        self.spin_i.SetToolTip(_('Integrated Loudness Target in LUFS. '
                                 'From -70.0 to -5.0, default is -24.0'
                                 ))
        self.spin_tp.SetToolTip(_('Maximum True Peak in dBTP. From -9.0 '
                                  'to +0.0, default is -2.0'
                                  ))
        self.spin_lra.SetToolTip(_('Loudness Range Target in LUFS. '
                                   'From +1.0 to +20.0, default is +7.0'
                                   ))
        #----------------------Build Layout----------------------#
        #siz1 = wx.BoxSizer(wx.VERTICAL)
        siz1 = wx.FlexGridSizer(1, 1, 0, 0)
        grid_siz7 = wx.GridSizer(2, 1, 0, 0)
        grd_s1 = wx.FlexGridSizer(2, 1, 0, 0)
        grd_s2 = wx.FlexGridSizer(3, 1, 0, 0)
        grd_s4 = wx.GridSizer(1, 3, 0, 0)
        grid_siz5 = wx.FlexGridSizer(2, 2, 0, 0)
        grid_siz6 = wx.FlexGridSizer(1, 7, 0, 0)
        grd_s3 = wx.GridSizer(1, 2, 0, 0)
        grd_s5 =  wx.FlexGridSizer(1, 2, 0, 0)
        
        grd_s1.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 15)
        labcmd_1.Lower()
        sizlab1 = wx.StaticBoxSizer(labcmd_1, wx.VERTICAL)
        sizlab1.Add(self.txt_1cmd, 0, wx.ALL | wx.EXPAND 
                                            | wx.ALIGN_CENTER_HORIZONTAL 
                                            | wx.ALIGN_CENTER_VERTICAL, 15
                                            )
        grd_s3.Add(sizlab1,  0, wx.ALL | wx.EXPAND 
                                            | wx.ALIGN_CENTER_HORIZONTAL 
                                            | wx.ALIGN_CENTER_VERTICAL, 15
                                            )
        
        labcmd_2.Lower()
        sizlab2 = wx.StaticBoxSizer(labcmd_2, wx.VERTICAL)
        sizlab2.Add(self.txt_2cmd, 0, wx.ALL | wx.EXPAND 
                                            | wx.ALIGN_CENTER_HORIZONTAL 
                                            | wx.ALIGN_CENTER_VERTICAL, 15
                                            )
        grd_s3.Add(sizlab2, 0, wx.ALL | wx.EXPAND 
                                            | wx.ALIGN_CENTER_HORIZONTAL 
                                            | wx.ALIGN_CENTER_VERTICAL, 15
                                            )
        grid_siz7.Add(lab_prfl, 0, wx.ALIGN_CENTER_HORIZONTAL | 
                                   wx.ALIGN_CENTER_VERTICAL, 0
                                   )
        grid_siz7.Add(self.cmbx_prst, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        
        grd_s5.Add(self.rdbx_norm, 0, wx.ALL, 5)
        
        grid_normctrl = wx.FlexGridSizer(5, 2, 0, 0)

        grid_normctrl.Add(self.btn_analyzes,0, wx.ALL, 10)
        grid_normctrl.Add(self.btn_details, 0, wx.ALL, 10)
        grid_normctrl.Add(self.lab_amplitude, 0, wx.ALL, 10)
        grid_normctrl.Add(self.spin_target, 0, wx.ALL, 5)
        grid_normctrl.Add(self.lab_i, 0, wx.ALL, 10)
        grid_normctrl.Add(self.spin_i, 0, wx.ALL, 5)
        grid_normctrl.Add(self.lab_tp, 0, wx.ALL, 10)
        grid_normctrl.Add(self.spin_tp, 0, wx.ALL, 5)
        grid_normctrl.Add(self.lab_lra, 0, wx.ALL, 10)
        grid_normctrl.Add(self.spin_lra, 0, wx.ALL, 5)
        grd_s5.Add(grid_normctrl)
        
        grid_siz8 = wx.GridSizer(1, 1, 0, 0)
        grid_siz8.Add(grd_s5, 0, wx.ALIGN_CENTER_HORIZONTAL | 
                                 wx.ALIGN_CENTER_VERTICAL, 5
                                   )
        nb1_p1.SetSizer(grid_siz7)
        nb1_p2.SetSizer(grd_s3)
        self.nb1_p3.SetSizer(grid_siz8)
        nb1.AddPage(nb1_p1, (_("Preset Selection")))
        nb1.AddPage(nb1_p2, (_("Command line FFmpeg")))
        nb1.AddPage(self.nb1_p3, (_("Automations")))
        grd_s2.Add(nb1, 1, wx.EXPAND, 0)
        grd_s2.Add(grd_s4, 1, wx.EXPAND, 0)
        grd_s1.Add(grd_s2, 1, wx.ALL | wx.EXPAND, 15)
        self.panel_1.SetSizer(grd_s1)
        siz1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(siz1)
        siz1.AddGrowableRow(0)
        siz1.AddGrowableCol(0)
        grd_s1.AddGrowableRow(0)
        grd_s1.AddGrowableCol(0)
        grd_s2.AddGrowableRow(0)
        grd_s2.AddGrowableCol(0)
        self.Layout()
        
        #----------------------Binder (EVT)----------------------#
        self.Bind(wx.EVT_COMBOBOX, self.on_choice_profiles, self.cmbx_prst)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.list_ctrl)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.parent.Run_Coding, 
                                              self.list_ctrl)
        self.Bind(wx.EVT_RADIOBOX, self.on_Enable_norm, self.rdbx_norm)
        self.Bind(wx.EVT_BUTTON, self.on_Analyzes, self.btn_analyzes)
        self.Bind(wx.EVT_BUTTON, self.on_Show_normlist, self.btn_details)
        self.Bind(wx.EVT_SPINCTRL, self.enter_Amplitude, self.spin_target)
        
        #---------------------------- defaults
        self.cmbx_prst.SetSelection(0)
        self.set_listctrl()
        self.normalization_default()
        
    #-------------------------------------------------------------------#
    def normalization_default(self):
        """
        Set default normalization parameters. This method is called by 
        main_frame module on MainFrame.switch_audio_conv() during first 
        run and when there are changing on dragNdrop panel, 
        (like make a clear file list or append new file, etc)
        
        """
        self.rdbx_norm.SetSelection(0), 
        self.btn_analyzes.Hide(), self.btn_details.Hide()
        self.lab_amplitude.Hide()
        self.spin_target.Hide(), self.spin_target.SetValue(-1.0)
        self.lab_i.Hide(), self.spin_i.Hide(), self.lab_lra.Hide(),
        self.spin_lra.Hide(), self.lab_tp.Hide(), self.spin_tp.Hide()
        cmd_opt["PEAK"], cmd_opt["EBU"], cmd_opt["RMS"] = "", "", ""
        del self.normdetails[:]
    #-----------------------------------------------------------------------#
    
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
        if array != []:
            del array[0:6]
        self.set_listctrl()
    #----------------------------------------------------------------#  
    
    def set_listctrl(self):
        """
        Populates Presets list with JSON data from *.prst files.
        See presets_manager_properties.py 
        """
        self.list_ctrl.InsertColumn(0, _('Profile Name'), width=150)
        self.list_ctrl.InsertColumn(1, _('Description'), width=250)
        self.list_ctrl.InsertColumn(2, _('Output Format'), width=100)
        self.list_ctrl.InsertColumn(3, _('Supported Formats List'), width=150)
        
        path = os.path.join('%s' % self.user_prst, 
                            '%s.prst' % self.cmbx_prst.GetValue()
                            )
        collections = json_data(path)
        if collections == 'error':
            return
        try:
            index = 0
            for name in collections:
                index+=1
                rows = self.list_ctrl.InsertItem(index, name['Name'])
                self.list_ctrl.SetItem(rows, 0, name['Name'])
                self.list_ctrl.SetItem(rows, 1, name["Description"])
                self.list_ctrl.SetItem(rows, 2, name["Output_extension"])
                self.list_ctrl.SetItem(rows, 3, name["Supported_list"])
        except KeyError as err:
            wx.MessageBox(_('ERROR: Typing error on JSON keys: {}\n\n'
                            'File: "{}"\nkey malformed ?'.format(err,path)), 
                            "Videomass", wx.ICON_ERROR, self)
            return
    #----------------------Event handler (callback)----------------------#
    def on_choice_profiles(self, event):
        """
        Combobox event.
        
        """
        self.reset_list()
        self.parent.statusbar_msg('{}'.format(self.cmbx_prst.GetValue()),None)
    #------------------------------------------------------------------#
    
    def on_select(self, event): # list_ctrl
        """
        By selecting a profile in the list_ctrl set new request 
        data in to the appropriate objects and sets parameters 
        to the text boxes.
        
        """
        path = os.path.join('%s' % self.user_prst, 
                            '%s.prst' % self.cmbx_prst.GetValue()
                            )
        collections = json_data(path)
        selected = event.GetText() # event.GetText is a Name Profile
        self.txt_1cmd.SetValue(""), self.txt_2cmd.SetValue("")
        del array[0:6] # delete all: [0],[1],[2],[3],[4],[5]
        
        try:
            for name in collections:
                if selected == name["Name"]:# profile name
                    array.append(name["Name"]) 
                    array.append(name["Description"])
                    array.append(name["First_pass"])
                    array.append(name["Second_pass"])
                    array.append(name["Supported_list"])
                    array.append(name["Output_extension"])
                    
        except KeyError as err:
            wx.MessageBox(_('ERROR: Typing error on JSON keys: {}\n\n'
                            'File: "{}"\nkey malformed ?'.format(err,path)), 
                            "Videomass", wx.ICON_ERROR, self)
            return
        
        self.txt_1cmd.AppendText('%s' %(array[2]))# cmd1 text ctrl
        if array[3]:
            self.txt_2cmd.Enable()
            self.txt_2cmd.AppendText('%s' %(array[3]))# cmd2 text ctrl
        else:
            self.txt_2cmd.Disable()
        
        sel = '{0} - {1}'.format(self.cmbx_prst.GetValue(), array[0])
        self.parent.statusbar_msg(sel, None)
    
    #------------------------------------------------------------------#
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
        if self.rdbx_norm.GetSelection() in [1,2]: # PEAK or RMS
            
            if self.rdbx_norm.GetSelection() == 1:
                self.parent.statusbar_msg(msg_1, azure)
                self.spin_target.SetValue(-1.0)
            else:
                self.parent.statusbar_msg(msg_2, '#15A660')
                self.spin_target.SetValue(-20.0)
                
            self.btn_analyzes.Enable()
            self.btn_analyzes.SetForegroundColour(wx.Colour(self.fBtnC))
            self.btn_analyzes.Show(), self.spin_target.Show(),
            self.lab_amplitude.Show(), self.btn_details.Hide()
            self.lab_i.Hide(), self.spin_i.Hide(), self.lab_lra.Hide(),
            self.spin_lra.Hide(), self.lab_tp.Hide(), self.spin_tp.Hide()
            cmd_opt["PEAK"], cmd_opt["RMS"], cmd_opt["EBU"] = "", "", ""
            del self.normdetails[:]
            
        elif self.rdbx_norm.GetSelection() == 3: # EBU
            self.parent.statusbar_msg(msg_3, '#87A615')
            self.btn_analyzes.Hide(), self.lab_amplitude.Hide()
            self.spin_target.Hide(), self.btn_details.Hide()
            self.lab_i.Show(), self.spin_i.Show(), self.lab_lra.Show(),
            self.spin_lra.Show(), self.lab_tp.Show(), self.spin_tp.Show()
            cmd_opt["PEAK"], cmd_opt["RMS"], cmd_opt["EBU"] = "", "", ""
            del self.normdetails[:]

        else: # usually it is 0
            self.parent.statusbar_msg(_("Audio normalization off"), None)
            self.normalization_default()
            
        self.nb1_p3.Layout()
    #------------------------------------------------------------------#
    
    def enter_Amplitude(self, event):
        """
        when spin_amplitude is changed enable 'Volumedected' to
        update new incomming
        
        """
        if not self.btn_analyzes.IsEnabled():
            self.btn_analyzes.Enable()
            self.btn_analyzes.SetForegroundColour(wx.Colour(self.fBtnC))
        
    #------------------------------------------------------------------#
    def on_Analyzes(self, event):  # Volumedected button
        """
        Evaluates the user's choices and directs them to the references 
        for audio normalizations based on PEAK or RMS .
        
        """
        if self.rdbx_norm.GetSelection() == 1:
            self.max_volume_PEAK(self.file_src)
            
        elif self.rdbx_norm.GetSelection() == 2:
            self.mean_volume_RMS(self.file_src)
    #------------------------------------------------------------------#
    def max_volume_PEAK(self, file_sources):
        """
        Analyzes to get MAXIMUM peak levels data to calculates offset in
        dBFS values need for audio normalization process.

        <https://superuser.com/questions/323119/how-can-i-normalize-audio-
        using-ffmpeg?utm_medium=organic>
        
        """
        msg2 = (_('Audio normalization is required only for some files'))
        msg3 = (_('Audio normalization is not required based to '
                  'set target level'))
        if self.normdetails:
            del self.normdetails[:]
        
        self.parent.statusbar_msg("",None)
        self.time_seq = self.parent.time_seq #from -ss to -t will be analyzed
        target = self.spin_target.GetValue()

        data = volumeDetectProcess(file_sources, self.time_seq)
        if data[1]:
            wx.MessageBox(data[1], "ERROR! -Videomass", wx.ICON_ERROR)
            return
        else:
            volume = list()

            for f, v in zip(file_sources, data[0]):
                maxvol = v[0].split(' ')[0]
                meanvol = v[1].split(' ')[0]
                offset = float(maxvol) - float(target)
                result = float(maxvol) - offset
                
                if float(maxvol) == float(target):
                    volume.append('  ')
                else:
                    volume.append("-af volume=%fdB" % -offset)

                self.normdetails.append((f, 
                                         maxvol,
                                         meanvol,
                                         str(offset),
                                         str(result),
                                         ))
        if [a for a in volume if not '  ' in a] == []:
             self.parent.statusbar_msg(msg3, orange)
        else:
            if len(volume) == 1 or not '  ' in volume:
                 pass
            else:
                self.parent.statusbar_msg(msg2, yellow)

        cmd_opt["PEAK"] = volume
        self.btn_analyzes.Disable()
        self.btn_analyzes.SetForegroundColour(wx.Colour(165,165, 165))
        self.btn_details.Show()
        self.Layout()
    #------------------------------------------------------------------#
    
    def mean_volume_RMS(self, file_sources):  # Volumedetect button
        """
        Analyzes to get MEAN peak levels data to calculates RMS offset in
        dBFS need for audio normalization process.
        """
        msg2 = (_('Audio normalization is required only for some files'))
        msg3 = (_('Audio normalization is not required based to '
                  'set target level'))
        if self.normdetails:
            del self.normdetails[:]
        
        self.parent.statusbar_msg("",None)
        self.time_seq = self.parent.time_seq #from -ss to -t will be analyzed
        target = self.spin_target.GetValue()

        data = volumeDetectProcess(file_sources, self.time_seq)
        if data[1]:
            wx.MessageBox(data[1], "ERROR! -Videomass", wx.ICON_ERROR)
            return
        else:
            volume = list()

            for f, v in zip(file_sources, data[0]):
                maxvol = v[0].split(' ')[0]
                meanvol = v[1].split(' ')[0]
                offset = float(meanvol) - float(target)
                result = float(maxvol) - offset
                
                if offset == 0.0:
                    volume.append('  ')
                else:
                    volume.append("-af volume=%fdB" % -offset)
                    
                self.normdetails.append((f, 
                                         maxvol,
                                         meanvol,
                                         str(offset),
                                         str(result),
                                         ))
                    
        if [a for a in volume if not '  ' in a] == []:
             self.parent.statusbar_msg(msg3, orange)
        else:
            if len(volume) == 1 or not '  ' in volume:
                 pass
            else:
                self.parent.statusbar_msg(msg2, yellow)
       
        cmd_opt["RMS"] = volume
        self.btn_analyzes.Disable()
        self.btn_analyzes.SetForegroundColour(wx.Colour(165,165, 165))
        self.btn_details.Show()
        self.Layout()
    #------------------------------------------------------------------#
    
    def on_Show_normlist(self, event):
        """
        Show a wx.ListCtrl dialog with volumedected data
        """
        if cmd_opt["PEAK"]:
            title = _('PEAK-based volume statistics')
        elif cmd_opt["RMS"]:
            title = _('RMS-based volume statistics')
            
        audionormlist = shownormlist.NormalizationList(title, 
                                                       self.normdetails, 
                                                       self.OS)
        audionormlist.Show()
    #-----------------------------------------------------------------------#

    def New_preset_prst(self):
        """
        Create new empty preset '*.prst' on /presets path name
        
        """
        filename = None
        with wx.FileDialog(self, "Enter name for new preset", 
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
                    wx.LogError("Cannot save current "
                                "data in file '%s'." % filename)
                    return
        if filename:
            wx.MessageBox(_("'Successful!\n\n"
                            "A new preset has been created."), 
                            "Videomass ", wx.ICON_INFORMATION, self)
            
            self.reset_list(True)

    #------------------------------------------------------------------#
    def Del_preset_prst(self):
        """
        Remove or delete a preset '*.prst' on /presets path name
        and move on Removals folder
        
        """
        filename = self.cmbx_prst.GetValue()
        if wx.MessageBox(_('Are you sure you want to remove "{}" preset?\n\n '
                           'It will be moved to the "Removals" folder in the '
                           'presets directory'
                           ).format(filename), _('Videomass: Please confirm'), 
                            wx.ICON_QUESTION | 
                            wx.YES_NO, self) == wx.NO:
            return
        
        path = os.path.join('%s' % self.user_prst, 
                        '%s.prst' % self.cmbx_prst.GetValue()
                        )
        try: # if exist dir not exit OSError, go...
            if not os.path.exists(os.path.join(self.user_prst, 'Removals')):
                os.mkdir(os.path.join(self.user_prst, 'Removals'))
        except OSError as err:
            wx.MessageBox(_("{}\n\nSorry, removal failed, I can't "
                            "continue.").format(err), "ERROR !", 
                            wx.ICON_ERROR, self)
            return
        s = os.path.join(self.user_prst, '%s.prst' % filename)
        d = os.path.join(self.user_prst, 'Removals', '%s.prst' % filename)
        os.replace(s, d)
        self.reset_list(True)

    #------------------------------------------------------------------#
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
    #------------------------------------------------------------------#
    def Restore(self):
        """
        Replace preset by another
        
        """
        wildcard = "Source (*.prst)|*.prst| All files (*.*)|*.*"
        
        dialfile = wx.FileDialog(self,
                                 _("Videomass: Choose a videomass preset "
                                   "to restore "), '', "", wildcard, 
                                   wx.FD_OPEN | 
                                   wx.FD_FILE_MUST_EXIST
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
                                                wx.ICON_QUESTION | 
                                                wx.YES_NO, 
                                                self) == wx.NO:
                return
            
            copy_restore('%s' % (dirname), 
                         '%s/%s' % (self.user_prst, tail))
            
            self.reset_list(True) # re-charging functions
    #------------------------------------------------------------------#
    def Default(self):
        """
        Replace the selected preset at default values. 
        
        """ 
        if wx.MessageBox(_("The selected preset will be overwritten with "
                           "default profiles!\nproceed?"), 
                           _("Videomass: Please confirm"), 
                            wx.ICON_QUESTION | 
                            wx.YES_NO, self) == wx.NO:
            return
        
        filename = self.cmbx_prst.GetValue()
        copy = copy_restore('%s/%s.prst' % (self.src_prst, filename), 
                            '%s/%s.prst' % (self.user_prst, filename))
        
        if copy:
            wx.MessageBox(_('Sorry, this preset is not part '
                            'of default Videomass presets.'), "ERROR !", 
                            wx.ICON_ERROR, self)
            return
            
        self.reset_list() # re-charging functions
    #------------------------------------------------------------------#
    def Default_all(self):
        """
        restore all preset files directory
        
        """
        if wx.MessageBox(_("WARNING: you are restoring all "
                           "default presets!\nProceed?"), 
                           _("Videomass: Please confirm"), 
                            wx.ICON_QUESTION | 
                            wx.YES_NO, self) == wx.NO:
            return

        copy_on('prst', self.src_prst, self.user_prst)
        
        self.reset_list(True) # re-charging functions
    #------------------------------------------------------------------#
    def Refresh(self):
        """ 
        Force to to re-charging
        """
        self.reset_list(True)
    
    #------------------------------------------------------------------#
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
            self.reset_list() # re-charging list_ctrl with newer
    #------------------------------------------------------------------#
    def Editprof(self, event):
        """
        Edit an existing profile
        
        """
        if array == []:
            self.parent.statusbar_msg(_("First select a profile in the list"), 
                                        yellow)
            return
        else:
            filename = self.cmbx_prst.GetValue()
            t = _('Edit profile of the "%s" preset: ') % (filename)
            
            prstdialog = presets_addnew.MemPresets(self, 
                                                   'edit', 
                                                   filename, 
                                                   array, 
                                                   t,
                                                   )
            ret = prstdialog.ShowModal()
            if ret == wx.ID_OK:
                self.reset_list() # re-charging list_ctrl with newer
    #------------------------------------------------------------------#
    def Delprof(self):
        """
        Delete a selected profile
        
        """
        if array == []:
            self.parent.statusbar_msg(_("First select a profile in the list"), 
                                         yellow)
        else:
            filename = self.cmbx_prst.GetValue()
            if wx.MessageBox(_("Are you sure you want to delete the "
                             "selected profile?"), 
                             _("Videomass: Please confirm"), 
                             wx.ICON_QUESTION | 
                             wx.YES_NO, self) == wx.NO:
                return
            
            path = os.path.join('%s' % self.user_prst, 
                            '%s.prst' % self.cmbx_prst.GetValue()
                            )
            delete_profiles(path, array[0])

            self.reset_list()
    #------------------------------------------------------------------#
    def on_start(self):
        """
        File data redirecting .
        
        """
        # check normalization data offset, if enable.
        if self.rdbx_norm.GetSelection() in [1,2]: # PEAK or RMS
            if self.btn_analyzes.IsEnabled():
                wx.MessageBox(_('Undetected volume values! use the '
                                '"Volumedetect" control button to analyze '
                                'data on the audio volume.'),
                                "Videomass", wx.ICON_INFORMATION)
                return
        self.time_seq = self.parent.time_seq
        dir_destin = self.parent.file_destin
        # used for file name log 
        self.logname = 'Videomass_PresetsManager.log'

        ######## ------------ VALIDAZIONI: --------------
        if array == []:
            self.parent.statusbar_msg(_("First select a profile in the list"),  
                                        yellow)
            return
        
        if (array[2].strip() != self.txt_1cmd.GetValue().strip() or 
            array[3].strip() != self.txt_2cmd.GetValue().strip()):
            if not self.txtcmdedited:
            
                msg = _("The selected profile command has been "
                        "changed manually.\n"
                        "Do you want to apply it "
                        "during the conversion process?")
                dlg = wx.RichMessageDialog(self, msg, 
                                           _("Videomass: Please confirm"), 
                                            wx.ICON_QUESTION | 
                                            wx.YES_NO,)

                dlg.ShowCheckBox(_("Don't show this dialog again"))

                if dlg.ShowModal() == wx.ID_NO:
                    if dlg.IsCheckBoxChecked():
                        # make sure we won't show it again the next time
                        self.txtcmdedited = True
                    return
                else:
                    if dlg.IsCheckBoxChecked():
                        # make sure we won't show it again the next time
                        self.txtcmdedited = True
                        
        outext = '' if array[5] == 'copy' else array[5] 
        extlst, outext = array[4], outext
        file_sources = supported_formats(extlst, self.file_src)
        checking = inspect(file_sources, dir_destin, outext)
        
        if not checking[0]:# missing files or user has changed his mind
            return
        
        (batch, file_sources, dir_destin, fname, bname, cntmax) = checking
        # batch: batch or single process
        # fname: filename, nome file senza ext.
        # bname: basename, nome file con ext.
        # cntmax: count items for batch proc.
        if array[3]: # has double pass
            self.two_Pass(file_sources, dir_destin, cntmax, outext)
        else:
            self.one_Pass(file_sources, dir_destin, cntmax, outext)
    #----------------------------------------------------------------#
    
    def one_Pass(self, filesrc, destdir, cntmax, outext):
        """
        
        """
        audnorm = cmd_opt["RMS"] if not cmd_opt["PEAK"] else cmd_opt["PEAK"]
        command = (self.txt_1cmd.GetValue())
        valupdate = self.update_dict(cntmax, 'One passes')
        ending = Formula(self, valupdate[0], valupdate[1], _('Starts'))
        if ending.ShowModal() == wx.ID_OK:
            self.parent.switch_Process('onepass',
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
    #------------------------------------------------------------------#
    
    def two_Pass(self, filesrc, destdir, cntmax, outext):
        """
        defines two-pass parameters
        """
        pass1 = " ".join(self.txt_1cmd.GetValue().split())
        pass2 = " ".join(self.txt_2cmd.GetValue().split())
        
        if 'loudnorm=' in pass1:
            if self.rdbx_norm.GetSelection() == 3:
                if wx.MessageBox(_('EBU automation is active but has also been '
                                'inserted in the preset parameters '
                                '(-af loudnorm). The parameters have priority.'
                                '\n\nDo you wish to continue?'), 
                                _("Videomass: Please confirm"), 
                                wx.ICON_QUESTION | 
                                wx.YES_NO, self) == wx.NO:
                    return
            
            typeproc, audnorm = 'two pass EBU', ''
            loudnorm = [ln for ln in pass1.split() if 'loudnorm=' in ln][0]
            
        elif self.rdbx_norm.GetSelection() == 3:
            loudnorm = ('loudnorm=I=%s:TP=%s:LRA=%s:print_format=summary' %(
                                            str(self.spin_i.GetValue()),
                                            str(self.spin_tp.GetValue()),
                                            str(self.spin_lra.GetValue())))
            pass1 = '-af %s ' % loudnorm + '%s' % pass1
            typeproc, audnorm = 'two pass EBU', ''
            
                
            
        else: # two-pass std
            typeproc, loudnorm = 'twopass', ''
            audnorm = cmd_opt["RMS"] if not cmd_opt["PEAK"] else cmd_opt["PEAK"]
        
        
        valupdate = self.update_dict(cntmax, typeproc)
        ending = Formula(self, valupdate[0], valupdate[1], _('Starts'))
        if ending.ShowModal() == wx.ID_OK:

            self.parent.switch_Process(typeproc,
                                        filesrc, 
                                        outext, 
                                        destdir, 
                                        None, 
                                        [pass1, pass2, loudnorm], 
                                        '',
                                        audnorm, 
                                        self.logname, 
                                        cntmax,
                                        )
    #--------------------------------------------------------------------#
    def update_dict(self, cntmax, passes):
        """
        Update information before send to epilogue
        
        """
        if not self.parent.time_seq:
            time = _('Disable')
        else:
            t = list(self.parent.time_read.items())
            time = '{0}: {1} | {2}: {3}'.format(t[0][0], t[0][1][0], 
                                                t[1][0], t[1][1][0])
            
        numfile = "%s file in pending" % str(cntmax)
                    
        formula = (_("SUMMARY\n\nFile to Queue\
                      \nPass Encoding\
                      \nProfile Used\nOut Format\
                      \nTime selection"
                      ))
        dictions = ("\n\n%s\n%s\n%s\n%s\n%s" % (numfile,
                                                passes,
                                                array[0], 
                                                array[5],
                                                time,)
                    )

        return formula, dictions
    #--------------------------------------------------------------------#
