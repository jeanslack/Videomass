# -*- coding: UTF-8 -*-
"""
Name: infoprog.py
Porpose: about videomass
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.13.2022
Code checker: pylint, flake8
########################################################

This file is part of Videomass.

   Videomass is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   Videomass is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with Videomass.  If not, see <http://www.gnu.org/licenses/>.
"""

import wx
import wx.adv
from videomass.vdms_sys.msg_info import current_release
from videomass.vdms_sys.msg_info import descriptions_release


def info(parent, videomass_icon):
    """
    It's a predefined template to create a dialogue on
    the program information

    """
    # ------------------
    cr = current_release()
    name_upper = cr[0]
    name_lower = cr[1]
    version = cr[2]
    Release = cr[3]
    copyright = cr[4]
    website = cr[5]
    author = cr[6]
    mail = cr[7]
    comment = cr[8]
    # -----------------
    dr = descriptions_release()
    Short_Dscrp = dr[0]
    Long_Dscrp = dr[1]
    Short_Lic = dr[2]
    long_lic = dr[3]
    # ------------------
    info = wx.adv.AboutDialogInfo()
    info.SetIcon(wx.Icon(videomass_icon, type=wx.BITMAP_TYPE_PNG))
    info.SetName(f"{name_upper}")
    info.SetVersion(f"v{version}")
    info.SetDescription(_("Cross-platform graphical interface "
                          "for FFmpeg and youtube-dl.\n"))
    info.SetCopyright(f"Copyright {copyright} {author[0]} {author[1]}")
    info.SetWebSite(website)
    info.SetLicence(long_lic)
    info.AddDeveloper(f"{author[0]} <{mail}>")
    info.AddDocWriter("Gianluca Pernigotto <jeanlucperni@gmail.com>")
    info.AddTranslator("Gianluca Pernigotto <jeanlucperni@gmail.com> (it_IT)")
    info.AddTranslator("ChourS <ChourS2008@yandex.ru> (ru_RU)")
    info.AddTranslator("Roelof Berkepeis <roelof@imoma.eu> (nl_NL)")
    info.AddTranslator("johannesdedoper https://github.com/johannesdedoper (nl_NL)")
    info.AddTranslator("Samuel (pt_BR)")
    info.AddTranslator("katnatek from blogdrake https://www.blogdrake.net/ (es_ES)")
    # info.AddTranslator("Nestor Blanco <random@mail.es> (es_ES)")
    info.SetArtists(
        ['Gianluca Pernigotto <jeanlucperni@gmail.com>',])
    wx.adv.AboutBox(info)
    # event.Skip()
