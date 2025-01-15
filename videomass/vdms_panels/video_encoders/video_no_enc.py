# -*- coding: UTF-8 -*-
"""
FileName: video_no_enc.py
Porpose: Contains text messages for A/V Conversions
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.05.2024
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
import wx.lib.scrolledpanel as scrolled


class Video_No_Enc(scrolled.ScrolledPanel):
    """
    This scroll panel implements text messages when `Audio`
    is selected from `Media` taget combobox.
    """
    def __init__(self, parent):
        """
        This is a child of `nb_Video` of `AV_Conv` class-panel (parent).
        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.parent = parent  # parent is the `nb_Video` here.
        scrolled.ScrolledPanel.__init__(self, parent, -1,
                                        size=(1024, 1024),
                                        style=wx.TAB_TRAVERSAL
                                        | wx.BORDER_NONE,
                                        name="Text messages scrolledpanel",
                                        )
        sizerbase = wx.BoxSizer(wx.VERTICAL)
        self.labinfo = wx.StaticText(self, wx.ID_ANY, label="")
        sizerbase.Add(self.labinfo, 0, wx.ALL | wx.CENTER, 2)
        sizerbase.Add((0, 50), 0)
        self.labsubinfo = wx.StaticText(self, wx.ID_ANY,
                                        style=wx.ST_ELLIPSIZE_END
                                        | wx.ALIGN_CENTRE_HORIZONTAL)
        sizerbase.Add(self.labsubinfo, 0, wx.ALL | wx.CENTER, 2)
        if self.appdata['ostype'] == 'Darwin':
            self.labinfo.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            self.labsubinfo.SetFont(wx.Font(12, wx.DEFAULT,
                                            wx.NORMAL, wx.NORMAL))
        else:
            self.labinfo.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            self.labsubinfo.SetFont(wx.Font(9, wx.DEFAULT,
                                            wx.NORMAL, wx.NORMAL))
        self.SetSizer(sizerbase)  # set panel
        self.SetAutoLayout(1)
        self.SetupScrolling()
    # ------------------------------------------------------------------#

    def default(self):
        """
        Reset all controls to default
        """
        self.labinfo.SetLabel(_("Video export disabled"))
        msg = (_('The Media target you just selected will only allow you to '
                 'export files as audio tracks.\nYou can then process audio '
                 'source files only or extract indexed audio streams on\n'
                 'video files.'))
        self.labsubinfo.SetLabel(msg)
    # ------------------------------------------------------------------#

    def video_options(self):
        """
        Get all video parameters
        """
        return ''
    # ------------------------------------------------------------------#
