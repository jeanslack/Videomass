# -*- coding: UTF-8 -*-

#########################################################
# Name: infoprog.py
# Porpose: about videomass 
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev (01) December 28 2018
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
import wx.adv
from videomass3.vdms_SYS.msg_info import current_release, descriptions_release

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
        info =  wx.adv.AboutDialogInfo()

        info.SetIcon(wx.Icon(videomass_icon, type=wx.BITMAP_TYPE_PNG))
        #info.SetIcon(videomass_icon)
        
        info.SetName("%s" % Name)
        
        info.SetVersion("v%s" % Version)
        
        info.SetDescription(_("Videomass provides a graphical interface for\n"
                              "audio and video conversion through FFmpeg\n"
                              "\n"
                              "This is a test release version.\n"
                              "It is based on Python3 and wxPython Phoenix")
                            )
        info.SetCopyright("Copyright %s %s" %(Copyright, Author))
        
        info.SetWebSite(Website)
        
        info.SetLicence(Long_Lic)
        
        #info.AddDeveloper("\n%s \n"
                        #"%s\n"
                        #"%s\n\n"
                        #"%s\n" %(Author,Mail,Website,Comment))
        #info.SetDevelopers('')
        info.AddDeveloper("%s %s\n" %(Author,Mail))
        info.AddDeveloper("Thanks to:")
        info.AddDeveloper("- Python (programming language)\n<https://www.python.org/>")
        info.AddDeveloper("- wxPython "
                          "(cross-platform GUI toolkit for the Python language)"
                          "\n<https://wxpython.org/>")
        info.AddDeveloper("- FFmpeg (a complete, cross-platform solution for media)\n"
                           "<http://ffmpeg.org/>")
        info.AddDeveloper("- Material design icons\n"
               "http://google.github.io/material-design-icons/#getting-icons")
        info.AddDeveloper("- Flat Color Icons\nhttp://icons8.com/color-icons\n")
        
        #info.SetDocWriters('')
        info.AddDocWriter("Gianluca Pernigotto (online documentation)\n")
                        
        #info.AddArtist('Gianluca Pernigotto powered by wx.Python')
        
        #info.SetTranslators('')
        info.AddTranslator("Gianluca Pernigotto <jeanlucperni@gmail.com> "
                           "English to Italian translations.\n")
        #info.SetArtists('')
        #info.AddArtist('- Gianluca Pernigotto (Videomass app icons only)\nhttp://jeanslack.github.io/Videomass/')
        #info.AddArtist('- Material design icons from Google\nhttp://google.github.io/material-design-icons/#getting-icons')
        #info.AddArtist('- Flat Color Icons\nhttp://icons8.com/color-icons')
                    
        wx.adv.AboutBox(info)
        #event.Skip()
