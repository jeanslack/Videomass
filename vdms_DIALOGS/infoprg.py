# -*- coding: UTF-8 -*-

#########################################################
# Name: infoprog.py
# Porpose: about videomass dialog
# resource: <http://zetcode.com/wxpython/dialogs/>
# Copyright: (c) 2015-2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3

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

# Rev (00) 10/Nov/2017
#########################################################

import wx
from vdms_SYS.msg_info import current_release, descriptions_release

cr = current_release()
Name = cr[0]
name = cr[1]
Version = cr[2]
Release = cr[3]
Copyright = cr[4]
Website = cr[5]
Author = cr[6]
Mail = cr[7]
Comment = cr[8]

dr = descriptions_release()
Short_Dscrp = dr[0]
Long_Dscrp = dr[1]
Short_Lic = dr[2]
Long_Lic = dr[3]

def info(videomass_icon):
        """
        It's a predefined template to create a dialogue on 
        the program information
        
        """
        info = wx.AboutDialogInfo()

        info.SetIcon(wx.Icon(videomass_icon, wx.BITMAP_TYPE_PNG))
        
        info.SetName(Name)
        
        info.SetVersion(Version)
        
        info.SetDescription(u'%s\n\n%s' %(Short_Dscrp,Long_Dscrp))
        
        info.SetCopyright("%s\nby %s" %(Copyright, Author))
        
        info.SetWebSite(Website)
        
        info.SetLicence(Long_Lic)
        
        info.AddDeveloper(u"\n%s \n"
                        u"%s\n"
                        u"%s\n\n"
                        u"%s\n" %(Author,Mail,Website,Comment))
        #info.AddDocWriter(u"La documentazione ufficiale é parziale e ancora\n"
                        #u"in fase di sviluppo, si prega di contattare l'autore\n"
                        #u"per ulteriori delucidazioni.")
                        
        #info.AddArtist(u'Gianluca Pernigotto powered by wx.Python')
        
        #info.AddTranslator(u"Al momento, il supporto alle traduzioni manca del\n"
                        #u"tutto, l'unica lingua presente nel programma é\n"
                        #u"quella italiana a cura di: Gianluca Pernigotto\n\n"

                        #u"Se siete interessati a tradurre il programma\n"
                        #u"in altre lingue, contattare l'autore.")
                    
        wx.AboutBox(info)
        #event.Skip()
