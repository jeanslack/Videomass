# -*- coding: UTF-8 -*-
"""
Name: infoprog.py
Porpose: about videomass
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.13.2022
Code checker: flake8, pylint

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
from videomass.vdms_sys import about_app


def show_about_dlg(parent, videomass_icon, aboutrel=about_app):
    """
    It's a predefined template to create a dialogue on
    the program information

    """
    # ------------------
    name_upper = aboutrel.RELNAME
    version = aboutrel.VERSION
    copyr = aboutrel.COPYRIGHT
    website = aboutrel.WEBSITE
    author = aboutrel.AUTHOR
    mail = aboutrel.MAIL
    long_lic = aboutrel.LICENSE
    # ------------------
    info = wx.adv.AboutDialogInfo()
    info.SetIcon(wx.Icon(videomass_icon, type=wx.BITMAP_TYPE_PNG))
    info.SetName(f"{name_upper}")
    info.SetVersion(f"v{version}")
    info.SetDescription(_("Cross-platform graphical user interface for FFmpeg"
                          "\n"))
    info.SetCopyright(f"Copyright {copyr} {author[0]} {author[1]}")
    info.SetWebSite(website)
    info.SetLicence(long_lic)
    info.AddDeveloper(f"{author[0]} <{mail}>")
    info.AddDocWriter("Gianluca Pernigotto <jeanlucperni@gmail.com>")
    info.AddTranslator("Gianluca Pernigotto <jeanlucperni@gmail.com> (it_IT)")
    info.AddTranslator("bovirus https://github.com/bovirus (it_IT)")
    info.AddTranslator("ChourS <ChourS2008@yandex.ru> (ru_RU)")
    info.AddTranslator("Roelof Berkepeis <roelof@imoma.eu> (nl_NL)")
    info.AddTranslator("johannesdedoper https://github.com/johannesdedoper "
                       "(nl_NL)")
    info.AddTranslator("Samuel http://littlesvr.ca/ostd/ (pt_BR)")
    info.AddTranslator("katnatek from blogdrake https://www.blogdrake.net/ "
                       "(es_ES)")
    info.AddTranslator("katnatek from blogdrake https://www.blogdrake.net/ "
                       "(es_CU)")
    info.AddTranslator("katnatek from blogdrake https://www.blogdrake.net/ "
                       "(es_MX)")
    info.AddTranslator("Phil Aug <philiaug@live.fr> (fr_FR)")
    info.AddTranslator("MaiJZ https://github.com/maijz128 (zh_CN)")

    info.SetArtists(['WxPython Phoenix <wxpython-users@googlegroups.com>',
                     'Gianluca Pernigotto <jeanlucperni@gmail.com>'])
    wx.adv.AboutBox(info)
    # event.Skip()
