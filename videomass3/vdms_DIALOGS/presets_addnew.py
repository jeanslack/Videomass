# -*- coding: UTF-8 -*-

#########################################################
# Name: presets_addnew.py
# Porpose: profile storing and profile editing dialog
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev (04) December 28 2018
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
import string
from videomass3.vdms_IO.presets_manager_properties import delete_profiles
import webbrowser

class MemPresets(wx.Dialog):
    """
    Class for show dialog and store or edit single profiles of 
    the selected preset .
    """
    def __init__(self, parent, arg, full_pathname, filename, array, title):
        """
        arg: argument for evaluate if this dialog is used for add new
        profile or edit a existing profiles. Then you can pass three type 
        of strings: 
        arg = 'newprofile'  
        arg = 'edit'
        arg = 'addprofile'
        """
        wx.Dialog.__init__(self, parent, -1, title, style=wx.DEFAULT_DIALOG_STYLE)
        
        self.path_xml = full_pathname
        self.filename = filename
        self.arg = arg # arg é solo un parametro di valutazione (edit o newprofile).
        self.array = array
        
        self.txt_name = wx.TextCtrl(self, wx.ID_ANY, "", 
                                    style=wx.TE_PROCESS_ENTER
                                    )
        siz1_staticbox = wx.StaticBox(self, wx.ID_ANY, _("Profile Name"))
        self.txt_descript = wx.TextCtrl(self, wx.ID_ANY, "", 
                                        style=wx.TE_PROCESS_ENTER
                                        )
        siz2_staticbox = wx.StaticBox(self, wx.ID_ANY, _("Description"))
        self.txt_cmd = wx.TextCtrl(self, wx.ID_ANY, "", 
                                   style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE)
        siz3_staticbox = wx.StaticBox(self, wx.ID_ANY, 
                                      (_("Command Line Parameters "
                                   "Do not use `-i` or output filename)"))
                                      )
        self.txt_supp = wx.TextCtrl(self, wx.ID_ANY, "", 
                                    style=wx.TE_PROCESS_ENTER
                                    )
        siz4_supp = wx.StaticBox(self, wx.ID_ANY, (_("Files supported in the "
                                        "import (do not include the `.`)"))
                                                    )
        self.txt_ext = wx.TextCtrl(self, wx.ID_ANY, "", 
                                   style=wx.TE_PROCESS_ENTER
                                   )
        siz4_ext = wx.StaticBox(self, wx.ID_ANY, (_("Output format extension "
                                                  "(do not include the `.`)"))
                                                  )
        btn_help = wx.Button(self, wx.ID_HELP, "")
        btn_canc = wx.Button(self, wx.ID_CANCEL, "")
        btn_save = wx.Button(self, wx.ID_OK, _("Save.."))

        #----------------------Set Properties----------------------#
        self.txt_name.SetMinSize((150, -1))
        self.txt_descript.SetMinSize((300, -1))
        self.txt_cmd.SetMinSize((350, 60))
        self.txt_supp.SetMinSize((300, -1))
        self.txt_ext.SetMinSize((150, -1))

        self.txt_name.SetToolTip(_("Assign a short name to the profile. "
                                        ))
        self.txt_descript.SetToolTip(_("Assign a long description to "
                                           "the profile.")
                                           )
        self.txt_cmd.SetToolTip(_("Do not use `-i` or output file, please."
                                        ))
        self.txt_supp.SetToolTip(_("You can limit the type "
                            "of files formats imported by specifying in a box "
                            "a format or multiple formats separated by a space "
                            "(a list of extensions without the dot)."
                            "Leave blank to involve any type of file to import " 
                            "inbound."))
        self.txt_ext.SetToolTip(_("Write here the output format extension"))
        
        #----------------------Build layout----------------------#
        grd_s1 = wx.FlexGridSizer(4, 1, 0, 0)
        boxSiz = wx.BoxSizer(wx.VERTICAL)
        grdexit = wx.GridSizer(1, 2, 0, 0)
        grd_s4 = wx.GridSizer(1, 2, 0, 0)
        siz4_ext.Lower()
        s4_ext = wx.StaticBoxSizer(siz4_ext, wx.VERTICAL)
        siz4_supp.Lower()
        s4_f_supp = wx.StaticBoxSizer(siz4_supp, wx.VERTICAL)
        siz3_staticbox.Lower()
        siz3 = wx.StaticBoxSizer(siz3_staticbox, wx.VERTICAL)
        grd_s2 = wx.GridSizer(1, 2, 0, 0)
        siz2_staticbox.Lower()
        siz2 = wx.StaticBoxSizer(siz2_staticbox, wx.VERTICAL)
        siz1_staticbox.Lower()
        siz1 = wx.StaticBoxSizer(siz1_staticbox, wx.VERTICAL)
        siz1.Add(self.txt_name, 0, wx.ALL, 15)
        grd_s2.Add(siz1, 1, wx.ALL | wx.EXPAND, 15)
        siz2.Add(self.txt_descript, 0, wx.ALL, 15)
        grd_s2.Add(siz2, 1, wx.ALL | wx.EXPAND, 15)
        grd_s1.Add(grd_s2, 1, wx.EXPAND, 0)
        siz3.Add(self.txt_cmd, 0, wx.ALL|wx.EXPAND, 15)
        grd_s1.Add(siz3, 1, wx.ALL | wx.EXPAND, 15)
        s4_f_supp.Add(self.txt_supp, 0, wx.ALL, 15)
        grd_s4.Add(s4_f_supp, 1, wx.ALL | wx.EXPAND, 15)
        s4_ext.Add(self.txt_ext, 0, wx.ALL, 15)
        grd_s4.Add(s4_ext, 1, wx.ALL | wx.EXPAND, 15)
        grd_s1.Add(grd_s4, 1, wx.EXPAND, 0)
        grdBtn =  wx.GridSizer(1, 2, 0, 0)
        grdhelp = wx.GridSizer(1, 1, 0, 0)
        grdhelp.Add(btn_help, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grdBtn.Add(grdhelp)
        grdexit.Add(btn_canc, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grdexit.Add(btn_save, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grdBtn.Add(grdexit, flag=wx.ALL|wx.ALIGN_RIGHT|wx.RIGHT, border=0)
        
        boxSiz.Add(grdBtn,1, wx.ALL | wx.EXPAND, 5)
        grd_s1.Add(boxSiz, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(grd_s1)
        grd_s1.Fit(self)
        self.Layout()

        #----------------------Binder (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_canc)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_BUTTON, self.on_apply, btn_save)
        
        #-------------------Binder (EVT) End --------------------#
        if arg == 'edit':
            self.change() # passo alla modifica del profilo, altrimenti
                        # vado avanti per memorizzarne di nuovi
        elif arg == 'addprofile':
            self.txt_cmd.AppendText(self.array[0]) # command or param
            if self.array[1] == '-c:v copy':
                self.txt_ext.AppendText('Not set')
            else:
                self.txt_ext.AppendText(self.array[1]) # extension
        
                        
    def change(self):
        """
        Copio gli elementi della lista array sui relativi campi di testo.
        questa funzione viene chiamata solo se si modificano i profili
        """
        self.txt_name.AppendText(self.array[0]) # name
        self.txt_descript.AppendText(self.array[1]) # descript
        self.txt_cmd.AppendText(self.array[2]) # command or param
        self.txt_supp.AppendText(self.array[3]) # file supportted
        self.txt_ext.AppendText(self.array[4]) # extension
    
#---------------------Callback (event handler)----------------------#
    
    def on_help(self, event):
        """
        """
        page = ('https://jeanslack.github.io/Videomass/Pages/Main_Toolbar/'
                'PresetsManager_Panel/Profiles_management.html')
        webbrowser.open(page)
    #------------------------------------------------------------------#
    def on_close(self, event):
        #self.Destroy()
        event.Skip()
    #------------------------------------------------------------------#
    def on_apply(self, event):
        
        nameprofile = self.txt_name.GetValue()
        descriptprofile = self.txt_descript.GetValue()
        paramprofile = self.txt_cmd.GetValue()
        file_support = self.txt_supp.GetValue()
        extprofile = self.txt_ext.GetValue() 
        
        if file_support in string.whitespace:
            wildcard = " "
        
        else:
            wildcard = file_support.strip()
            
        with open('%s' % (self.path_xml),'r') as readxml: # leggo il file
            rlist = readxml.readlines() # metto in lista il contenuto
        raw_list = ''.join(rlist)
        names = 'name="%s"' % (nameprofile)
        
        if nameprofile == '' or descriptprofile == '' or\
                                paramprofile == '' or extprofile ==  '':
                                    
            wx.MessageBox(_("Incomplete profile assignement. I can't save"),
                             "Videomass: warning", wx.ICON_EXCLAMATION, self)
            return
                                            
        elif names in raw_list and self.arg == 'newprofile': # if exist name
                
            wx.MessageBox(_("Profile already stored with the same name."), 
                          "Videomass: warning", wx.ICON_EXCLAMATION, self)
            return

        if self.arg == 'edit':
            # call module-function in os_processing and pass list
            delete_profiles(self.array, self.filename)
            # riapro e leggo il file
            with open('%s' % (self.path_xml),'r') as open_xml: # leggo il file
                rlist = open_xml.readlines() # metto in lista il contenuto
            
        del rlist[len(rlist)-1] # cancello ultimo elemento
        #open('%s' % (self.path_xml),'w').writelines(rlist)
        with open('%s' % (self.path_xml), "w") as f:
            f.writelines(rlist)
        #rlist = open('%s' % (self.path_xml),'a') # mette in coda al file
        with open('%s' % (self.path_xml), "a") as rlist:

            model = """
    <label name="%s" type="%s">
        <parameters>%s</parameters>
        <filesupport>%s</filesupport>
        <extension>%s</extension>
    </label>
</presets>
""" % (nameprofile, descriptprofile, paramprofile, wildcard, extprofile)

            rlist.writelines(model)
        
        if self.arg == 'newprofile':
            wx.MessageBox(_("Successfull storing !"))
            self.txt_name.SetValue(''), self.txt_descript.SetValue(''),
            self.txt_cmd.SetValue(''), self.txt_ext.SetValue('')
            self.txt_supp.SetValue('')
            
        elif self.arg == 'edit':
            wx.MessageBox(_("Successfull modified !"))
            #self.Destroy() # con ID_OK e ID_CANCEL non serve
            
        elif self.arg == 'addprofile':
            wx.MessageBox(_("Successfull storing !\n\n"
                          "You will find this profile in the 'User Profiles' "
                          "preset in the 'Presets Manager' panel.\n"
                          "Use the 'Reload presets list' on File menu to "
                          "update profile list."))
                
        event.Skip() 
