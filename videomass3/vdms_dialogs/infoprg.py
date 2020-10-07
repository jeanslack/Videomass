# -*- coding: UTF-8 -*-
# Name: infoprog.py
# Porpose: about videomass
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Sept.12.2020 *PEP8 compatible*
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
from videomass3.vdms_sys.msg_info import current_release
from videomass3.vdms_sys.msg_info import descriptions_release


def info(parent, videomass_icon):
    """
    It's a predefined template to create a dialogue on
    the program information

    """
    # ------------------
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
    # -----------------
    dr = descriptions_release()
    Short_Dscrp = dr[0]
    Long_Dscrp = dr[1]
    Short_Lic = dr[2]
    Long_Lic = dr[3]
    # ------------------
    info = wx.adv.AboutDialogInfo()
    info.SetIcon(wx.Icon(videomass_icon, type=wx.BITMAP_TYPE_PNG))
    info.SetName("%s" % Name)
    info.SetVersion("v%s" % Version)
    info.SetDescription(_("Cross-platform graphical interface "
                          "for FFmpeg and youtube-dl.\n"))
    info.SetCopyright("Copyright %s %s %s" % (Copyright, Author[0], Author[1]))
    info.SetWebSite(Website)
    info.SetLicence(Long_Lic)
    info.AddDeveloper("%s <%s>" % (Author[0], Mail))
    info.AddDocWriter("Gianluca Pernigotto <jeanlucperni@gmail.com>")
    info.AddTranslator("Gianluca Pernigotto <jeanlucperni@gmail.com> (it)")
    #info.AddTranslator("Nestor Blanco <random@ES.pe> ES")
    info.SetArtists(['Gianluca Pernigotto <jeanlucperni@gmail.com>',
                     'Material design icons '
                     'http://google.github.io/material-design-icons/'
                     '#getting-icons'])
    wx.adv.AboutBox(info)
    # event.Skip()
