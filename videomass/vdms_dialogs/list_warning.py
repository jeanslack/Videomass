# -*- coding: UTF-8 -*-
"""
Name: filelist_warning.py
Porpose: A custom dialog for list warning messages
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: April.15.2023
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


class ListWarning(wx.Dialog):
    """
    This class represents a modal dialog that shows a
    text control for list items associated to a warning
    message, with a choice of wx.OK or wx.Cancel/wx.OK buttons.

    Usage examples:
            with ListWarning(None,
                             dict.fromkeys(list, 'message string'),
                             caption='Non-existing file list',
                             header='Source files are missing ...',
                             buttons='OK',
                             ) as log:
                log.ShowModal()

            with ListWarning(Self,
                             dict.fromkeys(list, 'message string'),
                             caption='Please Confirm',
                             header='Files that will be overwritten ...',
                             buttons='CONFIRM',
                             ) as log:
                if log.ShowModal() != wx.ID_OK:
                    return None

    """
    def __init__(self, parent, items, caption='', header='', buttons='OK'):
        """
        items: (dict) a dict object with `item: message, ...`
        caption: (str) specified title for window.
        header: (str) An explanatory message that should appear
                before the list.
        buttons: (str) default is 'OK'(show only 'Ok' button),
                 'CONFIRM' show 'Ok' button and a 'Cancel' button.
        """
        get = wx.GetApp()  # get data from bootstrap
        colorscheme = get.appset['icontheme'][1]
        # Use 'parent, -1' param. to make parent, use 'None' otherwise
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE
                           | wx.RESIZE_BORDER,
                           )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(10, 10)
        labheader = wx.StaticText(self, wx.ID_ANY, header)
        sizer.Add(labheader, 0, wx.ALL | wx.EXPAND, 5)
        textlist = wx.TextCtrl(self,
                               wx.ID_ANY, "",
                               style=wx.TE_MULTILINE
                               | wx.TE_READONLY
                               | wx.TE_RICH2
                               | wx.HSCROLL,
                               )
        sizer.Add(textlist, 1, wx.ALL | wx.EXPAND, 5)
        # confirm buttons
        btn_ok = wx.Button(self, wx.ID_OK, "")
        if buttons == 'CONFIRM':
            btngrid = wx.FlexGridSizer(1, 2, 0, 0)
            btn_canc = wx.Button(self, wx.ID_CANCEL, "")
            btngrid.Add(btn_canc, 0, wx.ALL, 5)
        else:
            btngrid = wx.FlexGridSizer(1, 1, 0, 0)
        btngrid.Add(btn_ok, 0, wx.ALL, 5)
        sizer.Add(btngrid, 0, flag=wx.ALL | wx.ALIGN_RIGHT
                  | wx.RIGHT, border=0)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)

        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()

        textlist.SetBackgroundColour(colorscheme['BACKGRD'])

        if get.appset['ostype'] == 'Darwin':
            textlist.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
        else:
            textlist.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))

        # ------ Properties
        self.SetTitle(caption)
        index = 1
        for fname, msg in items.items():
            textlist.SetDefaultStyle(wx.TextAttr(colorscheme['TXT3']))
            textlist.AppendText(f"{index}: {fname}  ")
            textlist.SetDefaultStyle(wx.TextAttr(colorscheme['ERR0']))
            textlist.AppendText(f"{msg}\n")
            index += 1
        self.SetMinSize((550, 300))
        # textlist.SetMinSize((550, 300))
        textlist.SetInsertionPoint(0)

    def on_ok(self, event):
        """
        On OK event, this dialog box is auto-destroyed only
        """
        event.Skip()
