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
import webbrowser
import json

class MemPresets(wx.Dialog):
    """
    Show dialog to store and edit profiles of a selected preset.
    """
    def __init__(self, filename, array, title):
        """
        """
        wx.Dialog.__init__(self, None, style=wx.DEFAULT_DIALOG_STYLE)
        
        self.path_prst = filename
        self.array = array # param list [name, descript, cmd1, cmd2, supp, ext]
        
        self.txt_name = wx.TextCtrl(self, wx.ID_ANY, "", 
                                    style=wx.TE_PROCESS_ENTER
                                    )
        siz1_staticbox = wx.StaticBox(self, wx.ID_ANY, _("Profile Name"))
        self.txt_descript = wx.TextCtrl(self, wx.ID_ANY, "", 
                                        style=wx.TE_PROCESS_ENTER
                                        )
        siz2_staticbox = wx.StaticBox(self, wx.ID_ANY, _("Description"))
        self.pass_1_cmd = wx.TextCtrl(self, wx.ID_ANY, "", 
                                   style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE)
        siz3_staticbox = wx.StaticBox(self, wx.ID_ANY, (_("1-PASS, "
                                    "Do not start with: `ffmpeg -i filename`, "
                                    "Do not end with: `output-filename`"))
                                      )
        self.pass_2_cmd = wx.TextCtrl(self, wx.ID_ANY, "", 
                                   style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE)
        siz5_staticbox = wx.StaticBox(self, wx.ID_ANY, (_("2-PASS (optional), "
                                    "Do not start with: `ffmpeg -i filename`, "
                                    "Do not end with: `output-filename`"))
                                      )
        self.txt_supp = wx.TextCtrl(self, wx.ID_ANY, "", 
                                    style=wx.TE_PROCESS_ENTER
                                    )
        siz4_supp = wx.StaticBox(self, wx.ID_ANY, (_("Supported Formats list "
                                        "(optional), do not include the `.`"))
                                                    )
        self.txt_ext = wx.TextCtrl(self, wx.ID_ANY, "", 
                                   style=wx.TE_PROCESS_ENTER
                                   )
        siz4_ext = wx.StaticBox(self, wx.ID_ANY, (_("Output Format, do not "
                                                    "include the `.`"))
                                                  )
        btn_help = wx.Button(self, wx.ID_HELP, "")
        btn_canc = wx.Button(self, wx.ID_CANCEL, "")
        btn_save = wx.Button(self, wx.ID_OK, _("Save.."))

        #----------------------Set Properties----------------------#
        self.txt_name.SetMinSize((150, -1))
        self.txt_descript.SetMinSize((300, -1))
        self.pass_1_cmd.SetMinSize((350, 60))
        self.pass_2_cmd.SetMinSize((350, 60))
        self.txt_supp.SetMinSize((300, -1))
        self.txt_ext.SetMinSize((150, -1))

        self.txt_name.SetToolTip(_('Assign a short name to the profile'))
        self.txt_descript.SetToolTip(_('Assign a long description'
                                       'to the profile'))
        self.pass_1_cmd.SetToolTip(_('Reserved arguments for the first pass'
                                        ))
        self.pass_2_cmd.SetToolTip(_('Reserved arguments for the second pass'
                                        ))
        self.txt_supp.SetToolTip(_('You can specify one or more comma-separated'
                                   ' format names to include in the profile'))
        self.txt_ext.SetToolTip(_("Type the output format extension here. "
                                  "Leave blank to copy codec and format"))
        
        #----------------------Build layout----------------------#
        grd_s1 = wx.FlexGridSizer(5, 1, 0, 0)
        boxSiz = wx.BoxSizer(wx.VERTICAL)
        grdexit = wx.GridSizer(1, 2, 0, 0)
        grd_s4 = wx.GridSizer(1, 2, 0, 0)
        siz4_ext.Lower()
        s4_ext = wx.StaticBoxSizer(siz4_ext, wx.VERTICAL)
        siz4_supp.Lower()
        s4_f_supp = wx.StaticBoxSizer(siz4_supp, wx.VERTICAL)
        siz3_staticbox.Lower()
        siz3 = wx.StaticBoxSizer(siz3_staticbox, wx.VERTICAL)
        siz5_staticbox.Lower()
        siz5 = wx.StaticBoxSizer(siz5_staticbox, wx.VERTICAL)
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
        siz3.Add(self.pass_1_cmd, 0, wx.ALL|wx.EXPAND, 15)
        siz5.Add(self.pass_2_cmd, 0, wx.ALL|wx.EXPAND, 15)
        grd_s1.Add(siz3, 1, wx.ALL | wx.EXPAND, 15)
        grd_s1.Add(siz5, 1, wx.ALL | wx.EXPAND, 15)
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
        self.pass_1_cmd.AppendText(self.array[0]) # command or param
        self.pass_2_cmd.AppendText(self.array[1])
        self.txt_ext.AppendText(self.array[2]) # extension
        
#---------------------Callback (event handler)----------------------#
    
    def on_help(self, event):
        """
        """
        page = ('https://jeanslack.github.io/Videomass/Pages/Main_Toolbar/'
                'PresetsManager_Panel/Profiles_management.html')
        webbrowser.open(page)
    #------------------------------------------------------------------#
    def on_close(self, event):
        self.Destroy()
        #event.Skip()
    #------------------------------------------------------------------#
    def on_apply(self, event):
        
        name = self.txt_name.GetValue()
        decript = self.txt_descript.GetValue()
        pass_1 = self.pass_1_cmd.GetValue()
        pass_2 = self.pass_2_cmd.GetValue()
        file_support = self.txt_supp.GetValue().strip()
        extens = self.txt_ext.GetValue().strip() 
        extens = 'copy' if not extens else extens

        ####---------------------------------------------------------------
        if [txt for txt in [name, decript, pass_1] if txt == '']:
            wx.MessageBox(_("Incomplete profile assignments"),
                            "Videomass ", wx.ICON_INFORMATION, self)
            return
        
        if len(file_support.split()) > 1:
            supp = ''.join(file_support.split())
            if [i for i in supp.split() if not ',' in i]:
                wx.MessageBox(_("Formats must be comma-separated"),
                            "Videomass ", wx.ICON_INFORMATION, self)
                return
                
        
        with open(self.path_prst, 'r', encoding='utf-8') as infile:
            stored_data = json.load(infile)
        
        for x in stored_data:
            if x["Name"] == name:
                wx.MessageBox(_("Profile already stored with same name"), 
                                "Videomass ", wx.ICON_INFORMATION, self)
                return
            
        data = [{"Name": "%s" % name,
                    "Description": "%s" % decript,
                    "First_pass": "%s" % pass_1,
                    "Second_pass": "%s" % pass_2,
                    "Supported_list": "%s" % file_support,
                    "Output_extension": "%s" % extens
                }]
                
        new_data = stored_data + data
        new_data.sort(key=lambda s: s["Name"])# make sorted by name
                    
        new_data.sort(key=lambda s: s["Name"])# make sorted by name
        with open(self.path_prst, 'w', encoding='utf-8') as outfile:
            json.dump(new_data, outfile, ensure_ascii=False, indent=4)
        
            wx.MessageBox(_("Successful storing!"), "Videomass", 
                        wx.ICON_INFORMATION, self)
            self.txt_name.SetValue(''), self.txt_descript.SetValue(''),
            self.pass_1_cmd.SetValue(''), self.txt_ext.SetValue('')
            self.txt_supp.SetValue('')
            
            self.on_close(self)
