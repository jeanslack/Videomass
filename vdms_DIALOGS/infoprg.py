# -*- coding: UTF-8 -*-

#########################################################
# Name: infoprog.py
# Porpose: about videomass2 dialog
# resource: <http://zetcode.com/wxpython/dialogs/>
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

def info(parent, videomass_icon):
        """
        It's a predefined template to create a dialogue on 
        the program information
        
        """
        info = wx.AboutDialogInfo()

        info.SetIcon(wx.Icon(videomass_icon, wx.BITMAP_TYPE_PNG))
        
        info.SetName("%s" % Name)
        
        info.SetVersion("- %s" % Version)
        
        info.SetDescription(_(u'%s\nThis is a test release version.') %(
                                                                Short_Dscrp)
                            )
        info.SetCopyright("Copyright %s %s" %(Copyright, Author))
        
        info.SetWebSite(Website)
        
        info.SetLicence(Long_Lic)
        
        #info.AddDeveloper(u"\n%s \n"
                        #u"%s\n"
                        #u"%s\n\n"
                        #u"%s\n" %(Author,Mail,Website,Comment))
        info.SetDevelopers('')
        info.AddDeveloper(u"%s %s\n" %(Author,Mail))
        info.AddDeveloper(u"Thanks to:")
        info.AddDeveloper(u"- FFmpeg, FFmpeg is a trademark of Fabrice Bellard,\n"
                           "originator of the FFmpeg project\n<http://ffmpeg.org/>")
        info.AddDeveloper(u"- Material design icons from Google\n"
               "http://google.github.io/material-design-icons/#getting-icons")
        info.AddDeveloper(u"- Flat Color Icons\nhttp://icons8.com/color-icons\n")
        
        info.SetDocWriters('')
        info.AddDocWriter("Gianluca Pernigotto (online documentation)\n")
                        
        #info.AddArtist(u'Gianluca Pernigotto powered by wx.Python')
        
        info.SetTranslators('')
        info.AddTranslator("Gianluca Pernigotto <jeanlucperni@gmail.com> English and Italian translations.\n")
        info.SetArtists('')
        info.AddArtist('- Gianluca Pernigotto (Videomass2 app icon only)\nhttp://jeanslack.github.io/Videomass2/')
        info.AddArtist('- Material design icons from Google\nhttp://google.github.io/material-design-icons/#getting-icons')
        info.AddArtist('- Flat Color Icons\nhttp://icons8.com/color-icons')
                    
        wx.AboutBox(info)
        #event.Skip()
