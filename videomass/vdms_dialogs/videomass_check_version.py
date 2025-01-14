# -*- coding: UTF-8 -*-
"""
Name: videomass_check_version.py
Porpose: shows informative messages on version in use and new releases
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: July.17.2023
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
import webbrowser
import wx


class CheckNewVersion(wx.Dialog):
    """
    shows informative messages on version in use and new releases

    """
    get = wx.GetApp()  # get data from bootstrap
    OS = get.appset['ostype']
    APPTYPE = get.appset['app']
    COLOR = get.appset['colorscheme']

    def __init__(self, parent, msg, newvers, this):
        """
        NOTE Use 'parent, -1' param. to make parent, use 'None' otherwise

        """
        self.msg = msg
        self.newvers = newvers
        self.curvers = this
        self.color = CheckNewVersion.COLOR

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)

        # ------ Add widget controls

        self.tctrl = wx.TextCtrl(self,
                                 wx.ID_ANY, "",
                                 style=wx.TE_MULTILINE
                                 | wx.TE_READONLY
                                 | wx.TE_RICH2
                                 | wx.TE_AUTO_URL
                                 | wx.TE_CENTRE,
                                 )
        btn_get = wx.Button(self, wx.ID_ANY, _("Get Latest Version"))
        btn_ok = wx.Button(self, wx.ID_OK, "")

        # ------ Properties
        self.SetTitle(_("Checking for newer version"))
        self.SetMinSize((450, 200))
        self.tctrl.SetMinSize((450, 200))

        # ------ set Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.tctrl, 0, wx.ALL | wx.EXPAND, 5)

        btngrid = wx.FlexGridSizer(1, 2, 0, 0)
        btngrid.Add(btn_get, 0)
        btngrid.Add(btn_ok, 0, wx.LEFT, 5)
        sizer.Add(btngrid, flag=wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=5)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()

        self.tctrl.SetBackgroundColour(self.color['BACKGRD'])

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_get, btn_get)

        self.textstyle()

    def textstyle(self):
        """
        Populate TextCtrl
        """
        defmsg1 = _('\n\nNew releases fix bugs and offer new features.')
        defmsg2 = _('\n\nThis is Videomass v.{0}\n\n').format(self.curvers)

        if CheckNewVersion.OS == 'Darwin':
            self.tctrl.SetFont(wx.Font(13, wx.SWISS, wx.NORMAL, wx.BOLD))
        else:
            self.tctrl.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.tctrl.Clear()
        self.tctrl.SetDefaultStyle(wx.TextAttr(self.color['TXT0']))
        self.tctrl.AppendText(f'{defmsg1}')

        self.tctrl.SetDefaultStyle(wx.TextAttr(self.color['TXT3']))
        self.tctrl.AppendText(f'{defmsg2}')
        self.tctrl.AppendText(f'{self.msg}')
    # ------------------------------------------------------------------#

    def on_get(self, event):
        """
        Go to the specific download page for your platform
        """
        if CheckNewVersion.OS == 'Linux':

            if CheckNewVersion.APPTYPE == 'appimage':
                page = ('https://jeanslack.github.io/Videomass'
                        '/Pages/Packages/Linux.html#appimage')
            else:
                page = ('https://github.com/jeanslack/'
                        'Videomass/releases/latest/')

        elif CheckNewVersion.OS == 'Darwin':

            if CheckNewVersion.APPTYPE == 'pyinstaller':
                page = ('https://jeanslack.github.io/Videomass'
                        '/Pages/Packages/MacOS.html')
            else:
                page = page = ('https://github.com/jeanslack/'
                               'Videomass/releases/latest/')

        elif CheckNewVersion.OS == 'Windows':

            if CheckNewVersion.APPTYPE == 'pyinstaller':
                page = ('https://jeanslack.github.io/Videomass'
                        '/Pages/Packages/Windows.html')
            else:
                page = ('https://github.com/jeanslack/'
                        'Videomass/releases/latest/')
        else:
            page = ('https://jeanslack.github.io/Videomass/'
                    'download_installation.html')

        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        The dialog box is auto-destroyed

        """
        event.Skip()
