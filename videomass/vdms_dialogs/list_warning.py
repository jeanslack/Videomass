# -*- coding: UTF-8 -*-
"""
Name: list_warning.py
Porpose: A custom multipurpose dialog for listing alert messages and confirms
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
import wx


class ListWarning(wx.Dialog):
    """
    This class represents a modal dialog that shows a
    text control for list items associated to a warning
    message, with a choice of wx.OK or wx.Cancel/wx.YES_NO
    buttons.

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
                             caption='Please confirm',
                             header='Files that will be overwritten ...',
                             buttons='CONFIRM',
                             ) as log:
                if log.ShowModal() == wx.ID_YES:
                    print('you are clicked Yes button')
    """
    def __init__(self, parent, items, **kwargs):
        """
        parent: None or parent.
        items: (dict) a dict object with `item: message, ...`
        caption: (str) specified title for window.
        header: (str) An explanatory message that should appear
                      before the list.
        buttons: (str) 'OK', show only a wx.ID_OK button.
                 (str) 'CONFIRM' show wx.ID_CANCEL/wx.YES_NO buttons.
        """
        get = wx.GetApp()  # get data from bootstrap
        colorscheme = get.appset['colorscheme']
        # Use 'parent, -1' param. to make parent, use 'None' otherwise
        wx.Dialog.__init__(self, parent, -1,
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
                           )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(10, 10)
        labheader = wx.StaticText(self, wx.ID_ANY, kwargs['header'])
        sizer.Add(labheader, 0, wx.ALL | wx.EXPAND, 5)
        textlist = wx.TextCtrl(self,
                               wx.ID_ANY, "",
                               style=wx.TE_MULTILINE
                               | wx.TE_READONLY
                               | wx.TE_RICH2
                               | wx.HSCROLL,
                               )
        textlist.SetMinSize((700, 300))
        sizer.Add(textlist, 1, wx.ALL | wx.EXPAND, 5)

        # confirm buttons
        if kwargs['buttons'] == 'CONFIRM':
            btngrid = wx.GridSizer(1, 2, 0, 0)
            gridcanc = wx.GridSizer(1, 1, 0, 0)
            btn_canc = wx.Button(self, wx.ID_CANCEL, "")
            gridcanc.Add(btn_canc, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
            btngrid.Add(gridcanc)
            gridconfirm = wx.BoxSizer(wx.HORIZONTAL)
            btn_no = wx.Button(self, wx.ID_NO, "", name='NO')
            self.Bind(wx.EVT_BUTTON, self.on_confirm, btn_no)
            gridconfirm.Add(btn_no, 0, wx.ALIGN_CENTER_VERTICAL)
            btn_yes = wx.Button(self, wx.ID_YES, "", name='YES')
            self.Bind(wx.EVT_BUTTON, self.on_confirm, btn_yes)
            gridconfirm.Add(btn_yes, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
            btngrid.Add(gridconfirm, 0, flag=wx.ALL | wx.ALIGN_RIGHT
                        | wx.RIGHT, border=5)
            sizer.Add(btngrid, 0, wx.EXPAND)
        else:
            btn_ok = wx.Button(self, wx.ID_OK, "")
            btngrid = wx.FlexGridSizer(1, 1, 0, 0)
            btngrid.Add(btn_ok, 0)
            sizer.Add(btngrid, 0, flag=wx.ALL | wx.ALIGN_RIGHT
                      | wx.RIGHT, border=5)
            self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)

        textlist.SetBackgroundColour(colorscheme['BACKGRD'])

        # ------ Properties
        self.SetTitle(kwargs['caption'])
        index = 1
        for fname, msg in items.items():
            textlist.SetDefaultStyle(wx.TextAttr(colorscheme['TXT3']))
            textlist.AppendText(f"{index}   {fname}   ")
            textlist.SetDefaultStyle(wx.TextAttr(colorscheme['ERR0']))
            textlist.AppendText(f"{msg}\n")
            index += 1
        textlist.SetInsertionPoint(0)  # set cursor to initial point

        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()
        self.SetMinSize((550, 300))
    # ----------------------------------------------------------------------#

    def on_ok(self, event):
        """
        On OK event, this dialog box is auto-destroyed only
        """
        event.Skip()
    # ----------------------------------------------------------------------#

    def on_confirm(self, event):
        """
        Event on yes/no confirm ID buttons.
        Note:
            wx.ID_YES button int(5103)
            wx.ID_NO button int(5104)
            wx.ID_CANCEL button int(5101)

        Other Get examples:
            btn = event.GetEventObject()
            btn.GetId(), btn.GetName(), btn.GetLabel()
        """
        btnid = event.GetEventObject().GetId()
        self.EndModal(btnid)
