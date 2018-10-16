# -*- coding: UTF-8 -*-

#########################################################
# Name: presets_addnew.py
# Porpose: profile storing and profile editing dialog
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2015-2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3

# This file is part of Videomass2.

#    Videomass2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass2.  If not, see <http://www.gnu.org/licenses/>.

# Rev (01) 01/May/2015
# Rev (02) 03/Sept/2018
#########################################################

import wx
import string
from vdms_IO.presets_manager_properties import delete_profiles

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
        
        self.txt_name = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        siz1_staticbox = wx.StaticBox(self, wx.ID_ANY, "  Profile Name:")
        self.txt_descript = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        siz2_staticbox = wx.StaticBox(self, wx.ID_ANY, "  Description:")
        self.txt_cmd = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE)
        siz3_staticbox = wx.StaticBox(self, wx.ID_ANY, "  ffmpeg command line:")
        self.txt_supp = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        siz4_supp = wx.StaticBox(self, wx.ID_ANY, "  Supported file types import:")
        self.txt_ext = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        siz4_ext = wx.StaticBox(self, wx.ID_ANY, "  Output format extension:")
        btn5 = wx.Button(self, wx.ID_CANCEL, "")
        #btn4 = wx.Button(self, wx.ID_HELP, "")
        btn3 = wx.Button(self, wx.ID_OK, "SAVE") 

        #----------------------Set Properties----------------------#
        self.txt_name.SetMinSize((150, -1))
        self.txt_descript.SetMinSize((300, -1))
        self.txt_cmd.SetMinSize((350, 60))
        self.txt_supp.SetMinSize((300, -1))
        self.txt_ext.SetMinSize((150, -1))

        self.txt_name.SetToolTipString("Assign a short name to the profile "
                                    "Example:'Convert video for youtube'"
                                        )
        self.txt_descript.SetToolTipString("Assign a long description to "
                            "the profile. Example: 'video h264, video size "
                            "640x480 and audio mp3, stereo, bitrate 160kb, etc'"
                                        )
         
        self.txt_cmd.SetToolTipString("No type ffmpeg command call "
                    "here, no input flag '-i' and no type input/output file/dir "
                    "names, Yes this:\n "
                    "-vn -acodec libfaac -ab 128\n "
                    "No this:\n "
                    "ffmpeg -i name.ext -vn -acodec libfaac -ab 128 name.avi"
                                        )
        self.txt_supp.SetToolTipString("You can limit the type "
                            "of files formats imported by specifying in a box "
                            "a format or multiple formats separated by a space "
                            "(a list of extensions without the dot)."
                            "Leave blank to involve any type of file to import " 
                            "inbound."
        )
        self.txt_ext.SetToolTipString("Write here the output format extension")
        
        #----------------------Build layout----------------------#
        grd_s1 = wx.FlexGridSizer(4, 1, 0, 0)
        siz5 = wx.BoxSizer(wx.VERTICAL)
        grd_s3 = wx.GridSizer(1, 2, 0, 0)
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
        grd_s3.Add(btn5, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        #grd_s3.Add(btn4, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 15)
        grd_s3.Add(btn3, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        #siz5.Add(grd_s3, 1, wx.EXPAND, 15)
        siz5.Add(grd_s3, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=10)
        grd_s1.Add(siz5, 1, wx.ALL | wx.EXPAND, 15)
        self.SetSizer(grd_s1)
        grd_s1.Fit(self)
        self.Layout()

        #----------------------Binder (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, btn5)
        #self.Bind(wx.EVT_BUTTON, self.on_help, btn4)
        self.Bind(wx.EVT_BUTTON, self.on_apply, btn3)
        
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

    def on_close(self, event):
        #self.Destroy()
        event.Skip()

    #def on_help(self, event):
        #wx.MessageBox(u"Work in progress")
        
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
        raw_list = string.join(rlist)
        names = 'name="%s"' % (nameprofile)
        cod_names = names.encode("utf-8")
        
        
        if nameprofile == '' or descriptprofile == '' or\
                                paramprofile == '' or extprofile ==  '':
                                    
            wx.MessageBox(u"Incomplete profile assignement. I can't save",
                        "Warning", wx.ICON_EXCLAMATION, self)
            return
                                            
        elif cod_names in raw_list and self.arg == 'newprofile': # if exist name
                
            wx.MessageBox(u"Profile already stored with the same name."
                "nome", "Warning", wx.ICON_EXCLAMATION, self)
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
            """
            ho hackerato un po qui per risolvere l'eccezione "TypeError: 
            writelines() argument must be a sequence of strings", e alla riga 
            503 "UnicodeWarning: Unicode equal comparison failed to convert 
            both arguments to Unicode - interpreting them as being unequal" 
            per problemi di codifica.
            """
            Coding = model.encode("utf-8") 
            rlist.writelines(Coding)
            #rlist.close()
        
        if self.arg == 'newprofile':
            wx.MessageBox("Successfull storing !")
            self.txt_name.SetValue(''), self.txt_descript.SetValue(''),
            self.txt_cmd.SetValue(''), self.txt_ext.SetValue('')
            self.txt_supp.SetValue('')
            
        elif self.arg == 'edit':
            wx.MessageBox(u"Successfull modified !")
            #self.Destroy() # con ID_OK e ID_CANCEL non serve
            
        elif self.arg == 'addprofile':
            wx.MessageBox(u"Successfull storing !\n\n"
                          "You will find this profile in the 'Users Profiles' "
                          "preset in the 'Presets Manager' panel.\n"
                          "Use the 'Reload presets list' on File menu to "
                          "update profile list.")
                
        event.Skip() 
