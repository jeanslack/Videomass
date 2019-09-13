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
from videomass3.vdms_IO.presets_manager_properties import parser_xml
from videomass3.vdms_IO.presets_manager_properties import delete_profiles
from videomass3.vdms_IO.presets_manager_properties import supported_formats
from videomass3.vdms_SYS.os_interaction import copy_restore
from videomass3.vdms_SYS.os_interaction import copy_backup
from videomass3.vdms_SYS.os_interaction import copy_on
from videomass3.vdms_IO.filedir_control import inspect
from videomass3.vdms_DIALOGS import presets_addnew
from videomass3.vdms_DIALOGS.epilogue import Formula

array = []# all parameters of the selected profile
# this dictionary content all presets in ~/.videomass:
dict_presets = {
_("Audio Conversions") : ("preset-v1-Audio", "Audio Conversions"), 
_("Extract audio from video"): ("preset-v1-VideoAudio", 
                                "Extract audio from video"),
_("Extract images from video"): ("preset-v1-VideoImages", 
                                "Extract images from video"),
_("Convert to AVI") : ("preset-v1-AVI", "Convert to AVI"),
_("Mobile Phones multimedia") : ("preset-v1-MobilePhones", 
                                 "Mobile Phones multimedia"),
"iPod iTunes" : ("preset-v1-iPod-iTunes", "iPod iTunes"),
_("Convert to VCD (mpg)") : ("preset-v1-VCD", "Convert to VCD (mpg)"),
_("Convert DVD VOB") : ("preset-v1-VOB", "Convert DVD VOB"),
_("Convert to quicktime (mov)") : ("preset-v1-quicktime", 
                                   "Convert to quicktime (mov)"),
_("Convert to DV") : ("preset-v1-DV", "Convert to DV"),
"Google Android" : ("preset-v1-GoogleAndroid", "Google Android"),
"Google webm" : ("preset-v1-GoogleWebm", "Google webm"),
_("DVD Conversions") : ("preset-v1-DVD", "DVD Conversions"),
_("MPEG-4 Conversions") : ("preset-v1-MPEG-4", "MPEG-4 Conversions"),
_("PS3 Compatible") : ("preset-v1-PS3", "PS3 Compatible"),
_("PSP Compatible") : ("preset-v1-PSP", "PSP Compatible"),
_("Websites") : ("preset-v1-websites", "Websites"),
_("User Profiles") : ("preset-v1-Personal", "User Profiles"),
                    }
# set widget colours in some case with html rappresentetion:
azure = '#15a6a6'# rgb form (wx.Colour(217,255,255))
yellow = '#a29500'
red = '#ea312d'
orange = '#f28924'
greenolive = '#8aab3c'

class PresetsPanel(wx.Panel):
    """
    The Presets manager panel is used for the direct execution of profiles 
    with the ffmpeg commands, for editing, restoring and storing them.
    
    """

    def __init__(self, parent, path_srcShare, path_confdir,
                 PWD, threads, cpu_used, ffmpeg_loglev, 
                 ffmpeg_link, OS):
        
        self.src_vdms = os.path.join(path_srcShare, 'vdms')#origine share/vdms
        self.user_vdms = os.path.join(path_confdir, 'vdms')#conf/videomass/vdms
        self.PWD = PWD #current work of videomass
        self.threads = threads
        self.cpu_used = cpu_used if not cpu_used == 'Disabled' else ''
        self.ffmpeg_loglev = ffmpeg_loglev
        self.ffmpeg_link = ffmpeg_link
        self.OS = OS
        self.parent = parent
        self.file_sources = []
        self.file_destin = ''
        self.prstmancmdmod = False # don't show dlg if cmdline is mod manually
        
        wx.Panel.__init__(self, parent, -1) 
        """constructor"""

        self.panel_1 = wx.Panel(self, wx.ID_ANY)

        self.list_ctrl = wx.ListCtrl(self.panel_1, wx.ID_ANY, 
                                        style=wx.LC_REPORT | wx.SUNKEN_BORDER
                                        )
        nb1 = wx.Notebook(self.panel_1, wx.ID_ANY, style=0)
        nb1_p1 = wx.Panel(nb1, wx.ID_ANY)
        lab_prfl = wx.StaticText(nb1_p1, wx.ID_ANY, _("Select a preset from "
                                                    "the drop down:"))
        self.cmbx_prst = wx.ComboBox(nb1_p1,wx.ID_ANY, choices=[
                        (_("Audio Conversions")),
                        (_("Extract audio from video")),
                        (_("Extract images from video")),
                        (_("Convert to AVI")),
                        (_("Mobile Phones multimedia")),
                        ("iPod iTunes"),
                        (_("Convert to VCD (mpg)")),
                        (_("Convert DVD VOB")),
                        (_("Convert to quicktime (mov)")),
                        (_("Convert to DV")),
                        ("Google Android"),
                        ("Google webm"),
                        (_("DVD Conversions")),
                        (_("MPEG-4 Conversions")),
                        (_("PS3 Compatible")),
                        (_("PSP Compatible")),
                        (_("Websites")),
                        (_("User Profiles")),
                        ],
                        style=wx.CB_DROPDOWN | wx.CB_READONLY
                        )
        nb1_p2 = wx.Panel(nb1, wx.ID_ANY)
        self.txt_cmd = wx.TextCtrl(nb1_p2, wx.ID_ANY,"",
                                style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)
        
        #----------------------Set Properties----------------------#
        self.cmbx_prst.SetSelection(0)
        
        #self.list_ctrl.SetBackgroundColour(azure)
        self.list_ctrl.SetToolTip(_("List selection profiles"))
        self.txt_cmd.SetMinSize((430, 60))
        self.txt_cmd.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.txt_cmd.SetToolTip(_("Command of the selected profile"))

        #----------------------Build Layout----------------------#
        #siz1 = wx.BoxSizer(wx.VERTICAL)
        siz1 = wx.FlexGridSizer(1, 1, 0, 0)
        grid_siz7 = wx.GridSizer(2, 1, 0, 0)
        grd_s1 = wx.FlexGridSizer(2, 1, 0, 0)
        grd_s2 = wx.FlexGridSizer(3, 1, 0, 0)
        grd_s4 = wx.GridSizer(1, 3, 0, 0)
        grid_siz5 = wx.FlexGridSizer(2, 2, 0, 0)
        grid_siz6 = wx.FlexGridSizer(1, 7, 0, 0)
        grd_s3 = wx.GridSizer(1, 1, 0, 0)
        #siz1.Add(self.DnD, 1, wx.EXPAND|wx.ALL, 10)#########################
        grd_s1.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 15)
        grd_s3.Add(self.txt_cmd, 0, wx.ALL | wx.EXPAND 
                                            | wx.ALIGN_CENTER_HORIZONTAL 
                                            | wx.ALIGN_CENTER_VERTICAL, 15
                                            )
        grid_siz7.Add(lab_prfl, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
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
                                              self.list_ctrl
                                              )
        self.Bind(wx.EVT_TEXT, self.enter_command, self.txt_cmd)
        
        #----------------------Create preset list----------------------#
        if array != []: # appena avvio, cancella i dati in memoria se esistono
            del array[0:5]

        self.set_listctrl() # passo l'istanza al parsing e creo la lista
    
    #-----------------------------------------------------------------------#
    def disableParent(self):
        """
        disabling the main fraim also automatically disables this panel
        """
        self.parent.Disable()
    #-----------------------------------------------------------------------#
    def enableParent(self):
        """
        Enabling the main fraim also automatically enable this panel
        """
        self.parent.Enable()
    #-----------------------------------------------------------------------#
    def reset_list(self):
        """
        Clear all memory presets and pass to set_listctrl() for 
        re-charging new. This is used when add/edit or delete profiles. 
        The list is reloaded automatically after closing the dialogs for 
        view update .
        """
        self.list_ctrl.ClearAll()
        self.txt_cmd.SetValue("")
        self.set_listctrl()
        if array != []:
            del array[0:5]
            
    def set_listctrl(self):
        """
        Order list of preset (Name/Descript.) from reading xml (vdms)
        """
        try:
            av_presets = dict_presets[self.cmbx_prst.GetValue()][0]
            dati = parser_xml(av_presets, self.user_vdms) # xml parsing
            
            self.list_ctrl.InsertColumn(0, _('Profile Name'), width=230)
            self.list_ctrl.InsertColumn(1, _('Description'), width=350)
            self.list_ctrl.InsertColumn(2, _('Output Extension Type'), width=150)
            self.list_ctrl.InsertColumn(3, _('Supported formats'), width=150)
            
            index = 0
            for name in sorted(dati.keys()):
                rows = self.list_ctrl.InsertItem(index, name)
                self.list_ctrl.SetItem(rows, 0, name)
                param = dati[name]
                self.list_ctrl.SetItem(rows, 1, param["type"])
                self.list_ctrl.SetItem(rows, 2, param["estensione"])
                self.list_ctrl.SetItem(rows, 3, param["filesupport"])
        except:
            UnboundLocalError
            wx.MessageBox(_("For some circumstance, the selected preset is "
                          "corrupted. To restore the original copy at least go "
                          "to the File menu and choose 'restore the preset "
                          "source in use'. Note, before you make this choice, "
                          "saved your personal settings."), "ERROR !", 
                          wx.ICON_ERROR, self)
            return
    #----------------------Event handler (callback)----------------------#
    #------------------------------------------------------------------#
    def on_choice_profiles(self, event): # combobox
        """
        Whenever change preset type in the combobox list, clear all
        in the list_ctrl and re-charge with new file xml, clear the 
        text command and delete elements of array[] if in list.
        """
        self.reset_list()
        
    #------------------------------------------------------------------#
    def on_select(self, event): # list_ctrl
        """
        When select a profile into the list_ctrl, set the parameters
        request.
        Is the main point where be filled the list_ctrl for view.
        The presets are the files with extension vdms. The profiles
        are content it on presets and are selected in list_ctrl
        """
        combvalue = dict_presets[self.cmbx_prst.GetValue()][0] # name xml
        dati = parser_xml(combvalue, self.user_vdms) # All data go in dict
        if array != []:
            del array[0:5] # delete all: lista [0],[1],[2],[3],[4]
            
        slct = event.GetText() # event.GetText is a Name Profile
        self.txt_cmd.SetValue("")
        # param, pass a name profile and search all own elements in list.
        param = dati[event.GetText()] 
        # lista extract and construct command from param and description (type)
        # slct is the profile name
        lista =  [slct, param["type"],param["parametri"], 
                  param["filesupport"], param["estensione"]
                  ]

        array.append(lista[0])# lista[0] is the profile name 
        array.append(lista[1])# lista[1] description
        array.append(lista[2])# lista[2] is the final command
        array.append(lista[3])# lista[3] the file support
        array.append(lista[4])# lista[4] output format name
        
        self.txt_cmd.AppendText(lista[2]) # this is cmd show in text ctrl
        
        self.parent.statusbar_msg(_('Selected profile name:  %s') % (array[0]),
                                                                        None)

    #------------------------------------------------------------------#
    def enter_command(self, event): # text command view
        """
        If a profile is selected, append text into the text_ctrl. Also
        modified the text received signal event
        """
        self.txt_cmd.GetValue()
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
    def Saveme(self):
        """
        save a single file copy of preset. The saved presets must be have
        same name where is saved to restore it correctly
        """
        combvalue = dict_presets[self.cmbx_prst.GetValue()][0]
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
            
            for k,v in dict_presets.items():
                if tail in "%s.vdms" % v[0]:
                    vdms = True
                    name = v[1]
                    break
                else:
                    vdms = False
            
            if not vdms:
                wx.MessageBox(_("This file does not match those used "
                                "by Videomass:\n\n'{0}'").format(dirname), 
                                "Videomass",  wx.ICON_INFORMATION, self)
                return
            
            if wx.MessageBox(_("The following preset:\n\n"
                               "'{0}'   ({1})\n\n"
                               "will be imported and will overwrite "
                               "the one in use.\n"
                               "Proceed ?").format(tail, name), 
                             _('Videomass: Please confirm'), 
                                                wx.ICON_QUESTION | 
                                                wx.YES_NO, 
                                                self) == wx.NO:
                return
            
            copy_restore('%s' % (dirname), 
                         '%s/%s' % (self.user_vdms, tail))
            
            self.reset_list() # re-charging functions
    #------------------------------------------------------------------#
    def Default(self):
        """
        Replace the selected preset at default values. 
        This replace new personal changes make at any profiles of the 
        selected preset.
        """ 
        #copy_restore('%s/share/av_presets.xml' % (self.PWD), '%s' % (self.dirconf))
        if wx.MessageBox(_("The selected preset will be overwritten to "
                           "default values!\nproceed?"), 
                           _("Videomass: Please confirm"), 
                            wx.ICON_QUESTION | 
                            wx.YES_NO, self) == wx.NO:
            return
        
        filename = dict_presets[self.cmbx_prst.GetValue()][0]
        copy_restore('%s/%s.vdms' % (self.src_vdms, 
                                     filename), 
                                     '%s/%s.vdms' % (self.user_vdms,
                                                     filename))
        self.reset_list() # re-charging functions
    #------------------------------------------------------------------#
    def Default_all(self):
        """
        restore all preset files in the path presets of the program
        """
        if wx.MessageBox(_("WARNING: you are restoring all the "
                           "default presets!\nProceed?"), 
                           _("Videomass: Please confirm"), 
                            wx.ICON_QUESTION | 
                            wx.YES_NO, self) == wx.NO:
            return

        copy_on('vdms', self.src_vdms, self.user_vdms)
        
        self.reset_list() # re-charging functions
    #------------------------------------------------------------------#
    def Refresh(self):
        """ 
        Pass to reset_list function for re-charging list
        """
        self.reset_list()
    
    #------------------------------------------------------------------#
    def Addprof(self):
        """
        Store new profiles in the same presets selected in the
        combobox. The list is reloaded automatically after
        pressed ok button in the dialog for update view.
        """
        filename = dict_presets[self.cmbx_prst.GetValue()][0]
        name_preset = dict_presets[self.cmbx_prst.GetValue()][1]
        full_pathname = '%s/%s.vdms' % (self.user_vdms, filename)

        prstdialog = presets_addnew.MemPresets(self, 
                                               'newprofile', 
                                               full_pathname, 
                                               filename, 
                                               None, _('Create a new '
                                'profile on the selected  preset "%s"') % (
                                                name_preset)
                                                )
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
            filename = dict_presets[self.cmbx_prst.GetValue()][0]
            name_preset = dict_presets[self.cmbx_prst.GetValue()][1]
            full_pathname = '%s/%s.vdms' % (self.user_vdms, filename)
            
            prstdialog = presets_addnew.MemPresets(self, 
                                                   'edit', 
                                                   full_pathname, 
                                                   filename, 
                                                   array, 
                                            _('Edit profile on "%s" preset: ') 
                                                   % (name_preset)
                                                   )
            ret = prstdialog.ShowModal()
            if ret == wx.ID_OK:
                self.reset_list() # re-charging list_ctrl with newer
    #------------------------------------------------------------------#
    def Delprof(self):
        """
        Delete a choice in list_ctrl. This delete only single
        profile of the preset used
        """
        if array == []:
            self.parent.statusbar_msg(_("First select a profile in the list"), 
                                         yellow)
        else:
            filename = dict_presets[self.cmbx_prst.GetValue()][0]
            if wx.MessageBox(_("Are you sure you want to delete the "
                             "selected profile?"), 
                             _("Videomass: Please confirm"), 
                             wx.ICON_QUESTION | 
                             wx.YES_NO, self) == wx.NO:
                return
        
            filename = dict_presets[self.cmbx_prst.GetValue()][0]
            # call module-function and pass list as argument
            delete_profiles(array, filename, self.user_vdms)
            self.reset_list()
    #------------------------------------------------------------------#
    def on_ok(self):
        """
        The method composes the command strings to be sent to the 
        ffmpeg's process.
        It also involves the files existence verification procedures,
        overwriting control and log writing.
        
        """
        self.time_seq = self.parent.time_seq
        # make a different id need to avoid attribute overwrite:
        file_sources = self.parent.file_sources[:]
        # make a different id need to avoid attribute overwrite:
        dir_destin = self.file_destin
        # comcheck, cut string in spaces and become list:
        comcheck = self.txt_cmd.GetValue().split()#ffmpeg command
        # used for file name log 
        self.logname = 'Videomass_PresetsManager.log'

        ######## ------------ VALIDAZIONI: --------------
        if array == []:
            self.parent.statusbar_msg(_("First select a profile in the list"),  
                                        yellow)
            return
        
        if array[2].strip() != self.txt_cmd.GetValue().strip():
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
            
        array3, array4 = array[3], array[4]
        file_sources = supported_formats(array3, file_sources)
        checking = inspect(file_sources, dir_destin, array4)
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
        if array[4] in ['jpg','png','bmp']:
            #self.saveimages(dir_destin)
            self.saveimages(dir_destin, file_sources)
            
        elif 'DOUBLE_PASS' in comcheck:
            
            split = self.txt_cmd.GetValue().split('DOUBLE_PASS')
            passOne = split[0].strip()
            passTwo = split[1].strip()
            
            command1 = ("-loglevel %s %s %s %s -f rawvideo" % (
                                                    self.ffmpeg_loglev, 
                                                    passOne, 
                                                    self.threads, 
                                                    self.cpu_used,
                                                                )
                        )
            command2 = ("-loglevel %s %s %s %s" % (self.ffmpeg_loglev, 
                                                    passTwo, 
                                                    self.threads, 
                                                    self.cpu_used,
                                                    )
                        )
            pass1 = " ".join(command1.split())# mi formatta la stringa
            pass2 = " ".join(command2.split())# mi formatta la stringa
            
            valupdate = self.update_dict(countmax)
            ending = Formula(self, valupdate[0], valupdate[1], _('Starts'))
            if ending.ShowModal() == wx.ID_OK:

                self.parent.switch_Process('doublepass',
                                            file_sources, 
                                            array[4], 
                                            dir_destin, 
                                            None, 
                                            [pass1, pass2], 
                                            self.ffmpeg_link,
                                            '', 
                                            self.logname, 
                                            countmax, 
                                            )
                #used for play preview and mediainfo:
                f = os.path.basename(file_sources[0]).rsplit('.', 1)[0]
                self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                                    array[4]))

        else:
            command = ("-loglevel %s %s %s %s -y" % (self.ffmpeg_loglev, 
                                                    self.txt_cmd.GetValue(), 
                                                    self.threads, 
                                                    self.cpu_used,)
                                                    )
            valupdate = self.update_dict(countmax)
            ending = Formula(self, valupdate[0], valupdate[1], _('Starts'))
            if ending.ShowModal() == wx.ID_OK:
                self.parent.switch_Process('normal',
                                            file_sources, 
                                            array[4], 
                                            dir_destin, 
                                            command, 
                                            None, 
                                            self.ffmpeg_link,
                                            '', 
                                            self.logname, 
                                            countmax, 
                                            )
                f = os.path.basename(file_sources[0]).rsplit('.', 1)[0]
                self.exportStreams('%s/%s.%s' % (dir_destin[0], f, 
                                                    array[4]))
    #--------------------------------------------------------------------#
    def saveimages(self, dest, file_sources):
        """
        Save as files image the selected video input. The saved 
        images are named as file name + a progressive number + .jpg 
        and placed in a folder with the same file name + a progressive 
        number in the chosen output path.
        
        """
        if not self.parent.import_clicked:
            wx.MessageBox(_('To export images, select one of the files '
                            'in the "Add files" panel'), 'Videomass', 
                            wx.ICON_INFORMATION, self)
            return
        
        valupdate = self.update_dict('1')
        ending = Formula(self, valupdate[0], valupdate[1], _('Starts'))
        
        if ending.ShowModal() == wx.ID_OK:
            clicked = self.parent.import_clicked
            fname = os.path.basename(clicked.rsplit('.', 1)[0])
            dir_destin = dest[file_sources.index(clicked)]# specified dest
            
            try: 
                outputdir = "%s/%s-IMAGES_1" % (dir_destin, fname)
                os.mkdir(outputdir)
                
            except FileExistsError:
                lista = []
                for dir_ in os.listdir(dir_destin):
                    if "%s-IMAGES_" % fname in dir_:
                        lista.append(int(dir_.split('IMAGES_')[1]))
                        
                prog = max(lista) +1
                outputdir = "%s/%s-IMAGES_%d" % (dir_destin, fname, prog)
                os.mkdir(outputdir)

            fileout = "{0}-%d.{1}".format(fname,array[4])
            cmd = ('%s %s -i "%s" -loglevel %s %s %s %s -y "%s/%s"' % (
                                                    self.ffmpeg_link, 
                                                    self.parent.time_seq,
                                                    clicked, 
                                                    self.ffmpeg_loglev,
                                                    self.txt_cmd.GetValue(),
                                                    self.threads, 
                                                    self.cpu_used,
                                                    outputdir, 
                                                    fileout)
                                                    )
            command = " ".join(cmd.split())# compact string
            self.parent.switch_Process('saveimages',
                                        clicked, 
                                        None, 
                                        None, 
                                        command, 
                                        None, 
                                        None, 
                                        None, 
                                        self.logname, 
                                        '1', 
                                        )
    #------------------------------------------------------------------#
    #------------------------------------------------------------------#
    
    def update_dict(self, countmax):
        """
        This method is required for update info before send at epilogue
        """
        numfile = "%s file in pending" % str(countmax)
                    
        formula = (_(u"SUMMARY:\n\nFile to Queue\
                      \nProfile Used:\nOut Format:\
                      \nTime selection:"
                      ))
        dictions = ("\n\n%s\n%s\n%s\n%s" % (numfile, 
                                            array[0], 
                                            array[4],
                                            self.time_seq)
                    )

        return formula, dictions

