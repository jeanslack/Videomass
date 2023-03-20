# -*- coding: UTF-8 -*-
"""
Name: textdrop.py
Porpose: Allows you to add text URLs
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.17.2023
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


class TextDnD(wx.Panel):
    """
    Text control with text drag ability, accept one or
    more urls separated by a white space or newline.

    """
    def __init__(self, parent):
        """
        parent is the MainFrame
        """
        self.parent = parent
        get = wx.GetApp()
        # colors = get.appset['icontheme'][1]

        wx.Panel.__init__(self, parent, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((0, 25))
        infomsg = _("Enter URLs below")
        lbl_info = wx.StaticText(self, wx.ID_ANY, label=infomsg)
        sizer.Add(lbl_info, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add((0, 10))
        self.textctrl_urls = wx.TextCtrl(self, wx.ID_ANY, "",
                                         style=wx.TE_MULTILINE
                                         | wx.TE_DONTWRAP,
                                         )
        sizer.Add(self.textctrl_urls, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add((0, 10))
        sizer_ctrl = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer_ctrl, 0, wx.ALL | wx.EXPAND, 0)
        self.text_path_save = wx.TextCtrl(self, wx.ID_ANY, "",
                                          style=wx.TE_PROCESS_ENTER
                                          | wx.TE_READONLY,
                                          )
        sizer_ctrl.Add(self.text_path_save, 1, wx.LEFT | wx.EXPAND, 5)

        self.btn_save = wx.Button(self, wx.ID_OPEN, "...", size=(35, -1))
        sizer_ctrl.Add(self.btn_save, 0, wx.RIGHT | wx.LEFT
                       | wx.ALIGN_CENTER_HORIZONTAL
                       | wx.ALIGN_CENTER_VERTICAL, 5,
                       )
        # self.textctrl_urls.SetBackgroundColour(colors['BACKGRD'])
        # self.textctrl_urls.SetDefaultStyle(wx.TextAttr(colors['TXT3']))
        self.SetSizer(sizer)

        if get.appset['ostype'] == 'Darwin':
            lbl_info.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        else:
            lbl_info.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.text_path_save.SetValue(self.parent.filedldir)
        # Tooltip
        tip = _("Set up a temporary folder for downloads")
        self.btn_save.SetToolTip(tip)
        self.text_path_save.SetToolTip(_("Destination folder"))
    # ---------------------------------------------------------

    def delete_all(self, event):
        """
        clear all text lines of the TxtCtrl
        """
        self.textctrl_urls.Clear()
        self.parent.destroy_orphaned_window()
    # -----------------------------------------------------------

    def on_file_save(self, path):
        """
        Set a specific directory for files saving
        """
        self.text_path_save.SetValue("")
        self.text_path_save.AppendText(path)
        self.parent.filedldir = path
