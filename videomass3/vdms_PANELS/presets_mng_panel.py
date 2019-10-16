# -*- coding: UTF-8 -*-

#########################################################
# Name: presets_mng_panel.py
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
from videomass3.vdms_IO.presets_manager_properties import json_data
from videomass3.vdms_IO.presets_manager_properties import supported_formats
from videomass3.vdms_IO.presets_manager_properties import delete_profiles
from videomass3.vdms_SYS.os_interaction import copy_restore
from videomass3.vdms_SYS.os_interaction import copy_backup
from videomass3.vdms_SYS.os_interaction import copy_on
from videomass3.vdms_IO.filedir_control import inspect
from videomass3.vdms_DIALOGS import presets_addnew
from videomass3.vdms_DIALOGS.epilogue import Formula

array = [] # Parameters of the selected profile

# set widget colours in some case with html rappresentetion:
azure = '#15a6a6'# rgb form (wx.Colour(217,255,255))
yellow = '#a29500'
red = '#ea312d'
orange = '#f28924'
greenolive = '#8aab3c'
green = '#268826'

class PresetsPanel(wx.Panel):
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
                 PWD, threads, ffmpeg_loglev, ffmpeg_link, OS):
        """
        """
        
        self.src_vdms = os.path.join(path_srcShare, 'vdms')#origin share/vdms
        self.user_vdms = os.path.join(path_confdir, 'vdms')#conf/videomass/vdms
        self.PWD = PWD #current work of videomass
        self.threads = threads
        self.ffmpeg_loglev = ffmpeg_loglev
        self.ffmpeg_link = ffmpeg_link
        self.OS = OS
        self.parent = parent
        self.file_sources = []
        self.file_destin = ''
        self.prstmancmdmod = False # don't show dlg if cmdline is edited
        
        vdms = sorted([os.path.splitext(x)[0] for x in os.listdir(self.user_vdms) 
                if os.path.splitext(x)[1] == '.vdms'])

        
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
                                     choices=vdms,
                                     size=(200,-1),
                                     style=wx.CB_DROPDOWN | 
                                     wx.CB_READONLY
                                     )
        nb1_p2 = wx.Panel(nb1, wx.ID_ANY)
        
        labcmd_1 = wx.StaticBox(nb1_p2, wx.ID_ANY, _("First pass parameters:"))
        self.txt_1_cmd = wx.TextCtrl(nb1_p2, wx.ID_ANY,"", style=wx.TE_MULTILINE| 
                                                          wx.TE_PROCESS_ENTER
                                                          )
        labcmd_2 = wx.StaticBox(nb1_p2, wx.ID_ANY, _("Second pass parameters:"))
        self.txt_2_cmd = wx.TextCtrl(nb1_p2, wx.ID_ANY,"", style=wx.TE_MULTILINE| 
                                                          wx.TE_PROCESS_ENTER
                                                          )
        #----------------------Set Properties----------------------#
        self.cmbx_prst.SetSelection(0)
        
        #self.list_ctrl.SetBackgroundColour(azure)
        self.txt_1_cmd.SetMinSize((430, 60))
        self.txt_1_cmd.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.txt_1_cmd.SetToolTip(_('First pass parameters of the '
                                    'selected profile'))
        self.txt_2_cmd.SetMinSize((430, 60))
        self.txt_2_cmd.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.txt_2_cmd.SetToolTip(_('Second pass parameters of the '
                                    'selected profile'))

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
        grd_s1.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 15)
        
        labcmd_1.Lower()
        sizlab1 = wx.StaticBoxSizer(labcmd_1, wx.VERTICAL)
        sizlab1.Add(self.txt_1_cmd, 0, wx.ALL | wx.EXPAND 
                                            | wx.ALIGN_CENTER_HORIZONTAL 
                                            | wx.ALIGN_CENTER_VERTICAL, 15
                                            )
        grd_s3.Add(sizlab1,  0, wx.ALL | wx.EXPAND 
                                            | wx.ALIGN_CENTER_HORIZONTAL 
                                            | wx.ALIGN_CENTER_VERTICAL, 15
                                            )
        
        labcmd_2.Lower()
        sizlab2 = wx.StaticBoxSizer(labcmd_2, wx.VERTICAL)
        sizlab2.Add(self.txt_2_cmd, 0, wx.ALL | wx.EXPAND 
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
        nb1_p1.SetSizer(grid_siz7)
        nb1_p2.SetSizer(grd_s3)
        nb1.AddPage(nb1_p1, (_("Selecting presets")))
        nb1.AddPage(nb1_p2, (_("Command line FFmpeg")))
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
        self.set_listctrl()
    #-----------------------------------------------------------------------#
    
    def reset_list(self, reset_cmbx=False):
        """
        Clear all data and re-charging new. Used by selecting new preset
        and add/edit/delete profiles events.
        
        """
        if reset_cmbx:
            vdms = sorted([os.path.splitext(x)[0] for x in 
                           os.listdir(self.user_vdms) if 
                           os.path.splitext(x)[1] == '.vdms'])
            self.cmbx_prst.Clear()
            self.cmbx_prst.AppendItems(vdms), self.cmbx_prst.SetSelection(0)
        
        self.list_ctrl.ClearAll()
        self.txt_1_cmd.SetValue(""), self.txt_2_cmd.SetValue("")
        if array != []:
            del array[0:6]
        self.set_listctrl()
    #----------------------------------------------------------------#  
    
    def set_listctrl(self):
        """
        Populates Presets list with JSON data from *.vdms files.
        See presets_manager_properties.py 
        """
        self.list_ctrl.InsertColumn(0, _('Profile Name'), width=230)
        self.list_ctrl.InsertColumn(1, _('Description'), width=350)
        self.list_ctrl.InsertColumn(2, _('Output Format'), width=150)
        self.list_ctrl.InsertColumn(3, _('Supported Formats List'), width=150)
        
        path = os.path.join('%s' % self.user_vdms, 
                            '%s.vdms' % self.cmbx_prst.GetValue()
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
    #------------------------------------------------------------------#
    
    def on_select(self, event): # list_ctrl
        """
        By selecting a profile in the list_ctrl set new request 
        data in to the appropriate objects and sets parameters 
        to the text boxes.
        
        """
        path = os.path.join('%s' % self.user_vdms, 
                            '%s.vdms' % self.cmbx_prst.GetValue()
                            )
        collections = json_data(path)
        selected = event.GetText() # event.GetText is a Name Profile
        self.txt_1_cmd.SetValue(""), self.txt_2_cmd.SetValue("")
        del array[0:6] # delete all: [0],[1],[2],[3],[4],[5]
        
        try:
            for name in collections:
                if selected == name["Name"]:
                    array.append(name["Name"])# profile name 
                    array.append(name["Description"])
                    array.append(name["First_pass"])# first pass command
                    array.append(name["Second_pass"])# second pass command
                    array.append(name["Supported_list"])# supported ext.
                    array.append(name["Output_extension"])
                    
        except KeyError as err:
            wx.MessageBox(_('ERROR: Typing error on JSON keys: {}\n\n'
                            'File: "{}"\nkey malformed ?'.format(err,path)), 
                            "Videomass", wx.ICON_ERROR, self)
            return
        
        self.txt_1_cmd.AppendText('%s' %(array[2]))# cmd1 text ctrl
        if array[3]:
            self.txt_2_cmd.Enable()
            self.txt_2_cmd.AppendText('%s' %(array[3]))# cmd2 text ctrl
        else:
            self.txt_2_cmd.Disable()
        self.parent.statusbar_msg(_('Selected profile name:  %s') % (array[0]),
                                                                     None)
    #------------------------------------------------------------------#
    def exportStreams(self, exported):
        """
        Set the parent.post_process attribute for communicate it the
        file disponibilities for play or metadata functionalities.
        """
        if not exported:
            return
        else:
            self.parent.post_process = exported
            self.parent.postExported_enable()
    #------------------------------------------------------------------#
    def New_preset_vdms(self):
        """
        Create new empty preset '*.vdms' on /vdms path name
        
        """
        pass
    #------------------------------------------------------------------#
    def Del_preset_vdms(self):
        """
        Remove or delete a preset '*.vdms' on /vdms path name
        
        """
        pass

    #------------------------------------------------------------------#
    def Saveme(self):
        """
        save a single file copy of preset. The saved presets must be have
        same name where is saved to restore it correctly
        """
        combvalue = self.cmbx_prst.GetValue()
        filedir = '%s/%s.vdms' % (self.user_vdms, combvalue)
        filename = combvalue
        
        dialsave = wx.DirDialog(self, _("Select a directory to save it"))
        if dialsave.ShowModal() == wx.ID_OK:
            dirname = dialsave.GetPath()
            copy_backup(filedir, '%s/%s.vdms' % (dirname, filename))
            dialsave.Destroy()
            wx.MessageBox(_("Successfully saved"), "Info", wx.OK, self)
    #------------------------------------------------------------------#
    def Restore(self):
        """
        Replace preset by another with saved custom profiles.
        """
        wildcard = "Source (*.vdms)|*.vdms| All files (*.*)|*.*"
        
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
                         '%s/%s' % (self.user_vdms, tail))
            
            self.reset_list(True) # re-charging functions
    #------------------------------------------------------------------#
    def Default(self):
        """
        Replace the selected preset at default values. 
        This replace new personal changes make at any profiles of the 
        selected preset.
        """ 
        #copy_restore('%s/share/av_presets.xml' % (self.PWD), '%s' % (self.dirconf))
        if wx.MessageBox(_("The selected preset will be overwritten to "
                           "default profile!\nproceed?"), 
                           _("Videomass: Please confirm"), 
                            wx.ICON_QUESTION | 
                            wx.YES_NO, self) == wx.NO:
            return
        
        filename = self.cmbx_prst.GetValue()
        copy = copy_restore('%s/%s.vdms' % (self.src_vdms, filename), 
                            '%s/%s.vdms' % (self.user_vdms, filename))
        
        if copy:
            wx.MessageBox(_('Sorry, this preset is not part '
                            'of default Videomass presets.'), "ERROR !", 
                            wx.ICON_ERROR, self)
            return
            
        self.reset_list() # re-charging functions
    #------------------------------------------------------------------#
    def Default_all(self):
        """
        restore all preset files in the path presets of the program
        """
        if wx.MessageBox(_("WARNING: you are restoring all "
                           "default presets!\nProceed?"), 
                           _("Videomass: Please confirm"), 
                            wx.ICON_QUESTION | 
                            wx.YES_NO, self) == wx.NO:
            return

        copy_on('vdms', self.src_vdms, self.user_vdms)
        
        self.reset_list(True) # re-charging functions
    #------------------------------------------------------------------#
    def Refresh(self):
        """ 
        reset_list to re-charging list
        """
        self.reset_list(True)
    
    #------------------------------------------------------------------#
    def Addprof(self):
        """
        Store new profiles in the same presets selected in the
        combobox. The list is reloaded automatically after
        pressed ok button in the dialog for update view.
        """
        filename = self.cmbx_prst.GetValue()
        t = _('Create a new profile on the selected  preset "%s"') % filename

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
        A choice in the list (profile) can be edit in all own part.
        The list is reloaded automatically after pressed save button 
        in the dialog.
        """
        if array == []:
            self.parent.statusbar_msg(_("First select a profile in the list"), 
                                        yellow)
            return
        else:
            filename = self.cmbx_prst.GetValue()
            t = _('Edit profile on "%s" preset: ') % (filename)
            
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
        Delete a selected profile in list_ctrl
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
            
            path = os.path.join('%s' % self.user_vdms, 
                            '%s.vdms' % self.cmbx_prst.GetValue()
                            )
            delete_profiles(path, array[0])

            self.reset_list()
    #------------------------------------------------------------------#
    def on_ok(self):
        """
        File data redirecting .
        
        """
        self.time_seq = self.parent.time_seq
        # make a different id need to avoid attribute overwrite:
        file_sources = self.parent.file_sources[:]
        # make a different id need to avoid attribute overwrite:
        dir_destin = self.file_destin
        # used for file name log 
        self.logname = 'Videomass_PresetsManager.log'

        ######## ------------ VALIDAZIONI: --------------
        if array == []:
            self.parent.statusbar_msg(_("First select a profile in the list"),  
                                        yellow)
            return
        
        if (array[2].strip() != self.txt_1_cmd.GetValue().strip() or 
            array[3].strip() != self.txt_2_cmd.GetValue().strip()):
            if not self.prstmancmdmod:
            
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
                        self.prstmancmdmod = True
                    return
                else:
                    if dlg.IsCheckBoxChecked():
                        # make sure we won't show it again the next time
                        self.prstmancmdmod = True
            
        array4, array5 = array[4], array[5]
        file_sources = supported_formats(array4, file_sources)
        checking = inspect(file_sources, dir_destin, array5)
        if not checking[0]:# l'utente non vuole continuare o files assenti
            return
        # typeproc: batch or single process
        # filename: nome file senza ext.
        # base_name: nome file con ext.
        # countmax: count processing cicles for batch mode
        (typeproc, file_sources, 
         dir_destin, filename, 
         base_name, countmax) = checking

        ######## ------------FINE VALIDAZIONI: --------------
        
        if array[3]: # has double pass
            
            pass1 = " ".join(self.txt_1_cmd.GetValue().split())
            pass2 = " ".join(self.txt_1_cmd.GetValue().split())
            
            valupdate = self.update_dict(countmax, 'Two passes')
            ending = Formula(self, valupdate[0], valupdate[1], _('Starts'))
            if ending.ShowModal() == wx.ID_OK:

                self.parent.switch_Process('twopass_presets',
                                            file_sources, 
                                            array[5], 
                                            dir_destin, 
                                            None, 
                                            [pass1, pass2], 
                                            '',
                                            '', 
                                            self.logname, 
                                            countmax,
                                            )
                #used for play preview and mediainfo:
                f = os.path.basename(file_sources[0]).rsplit('.', 1)[0]
                self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                                    array[5]))

        else:
            command = (self.txt_1_cmd.GetValue())
            valupdate = self.update_dict(countmax, 'One passes')
            ending = Formula(self, valupdate[0], valupdate[1], _('Starts'))
            if ending.ShowModal() == wx.ID_OK:
                self.parent.switch_Process('common_presets',
                                            file_sources, 
                                            array[5], 
                                            dir_destin, 
                                            command, 
                                            None, 
                                            '',
                                            '', 
                                            self.logname, 
                                            countmax,
                                            )
                f = os.path.basename(file_sources[0]).rsplit('.', 1)[0]
                self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                                    array[5]))
    #------------------------------------------------------------------#
    
    def update_dict(self, countmax, passes):
        """
        Update information before send to epilogue
        
        """
        if not self.parent.time_seq:
            time = _('Disable')
        else:
            t = list(self.parent.time_read.items())
            time = '{0}: {1} | {2}: {3}'.format(t[0][0], t[0][1][0], 
                                                t[1][0], t[1][1][0])
            
        numfile = "%s file in pending" % str(countmax)
                    
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

