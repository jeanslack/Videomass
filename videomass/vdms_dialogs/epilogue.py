# -*- coding: UTF-8 -*-
"""
Name: epilogue.py
Porpose: shows dialog box before start process
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: July.17.2022
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
import os
import wx
import wx.lib.scrolledpanel as scrolled


class Formula(wx.Dialog):
    """
    Show a dialog box before run process.
    """
    def __init__(self, parent, *args, **kwargs):

        get = wx.GetApp()  # get data from bootstrap
        self.appdata = get.appset
        colorscheme = self.appdata['colorscheme']
        self.movetotrash = args[1]
        self.emptylist = args[2]

        wx.Dialog.__init__(self, parent, -1,
                           style=wx.DEFAULT_DIALOG_STYLE
                           | wx.RESIZE_BORDER
                           )
        sizbase = wx.BoxSizer(wx.VERTICAL)
        panelscroll = scrolled.ScrolledPanel(self, wx.ID_ANY,
                                             size=args[0],
                                             style=wx.TAB_TRAVERSAL
                                             | wx.BORDER_THEME,
                                             name="panelscr",
                                             )
        sizbase.Add(panelscroll, 1, wx.ALL | wx.EXPAND, 5)
        label1 = wx.StaticText(panelscroll, wx.ID_ANY, kwargs['key'])
        label2 = wx.StaticText(panelscroll, wx.ID_ANY, kwargs['val'])
        panelscroll.SetBackgroundColour(colorscheme['BACKGRD'])
        label1.SetForegroundColour(colorscheme['TXT3'])
        label2.SetForegroundColour(colorscheme['TXT1'])
        grid_pan = wx.BoxSizer(wx.HORIZONTAL)
        grid_pan.Add(label1, 0, wx.ALL
                     | wx.ALIGN_CENTRE_VERTICAL
                     | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        grid_pan.Add(label2, 0, wx.ALL
                     | wx.ALIGN_CENTRE_VERTICAL
                     | wx.ALIGN_CENTRE_HORIZONTAL, 5)

        panelscroll.SetSizer(grid_pan)
        panelscroll.SetAutoLayout(1)
        panelscroll.SetupScrolling()

        lab = (_('When finished, once the operations '
                 'have been completed successfully:'))
        lbl = wx.StaticText(self, label=lab)
        sizbase.Add(lbl, 0, wx.LEFT | wx.TOP, 5)
        sizeropt = wx.BoxSizer(wx.HORIZONTAL)
        sizbase.Add(sizeropt, 0)
        descr = _("Trash the source files")
        self.ckbx_trash = wx.CheckBox(self, wx.ID_ANY, (descr))
        self.ckbx_trash.SetValue(self.movetotrash)
        sizeropt.Add(self.ckbx_trash, 0, wx.ALL, 5)
        descr = _("Clear the File List")
        self.ckbx_del = wx.CheckBox(self, wx.ID_ANY, (descr))
        self.ckbx_del.SetValue(self.emptylist)
        if self.movetotrash:
            self.ckbx_del.Disable()
        sizeropt.Add(self.ckbx_del, 0, wx.ALL, 5)
        btncancel = wx.Button(self, wx.ID_CANCEL, "")
        btnok = wx.Button(self, wx.ID_OK, _("Run"))
        btngrid = wx.FlexGridSizer(1, 2, 0, 0)
        btngrid.Add(btncancel, 0)
        btngrid.Add(btnok, 0, wx.LEFT, 5)
        sizbase.Add(btngrid, flag=wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=5)

        self.SetTitle(_('Videomass - Batch Mode'))
        self.SetMinSize(args[0])
        self.SetSizer(sizbase)
        sizbase.Fit(self)
        self.Layout()
        # ----------------------Binders (EVT)--------------------#
        self.Bind(wx.EVT_CHECKBOX, self.on_file_to_trash, self.ckbx_trash)
        self.Bind(wx.EVT_CHECKBOX, self.on_empty_list, self.ckbx_del)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, btncancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btnok)

        # --------------  Event handler (callback)  --------------#

    def on_empty_list(self, event):
        """
        enable/disable empty imported file list.
        """
        if self.ckbx_del.IsChecked():
            self.emptylist = True
        else:
            self.emptylist = False
    # --------------------------------------------------------------------#

    def on_file_to_trash(self, event):
        """
        enable/disable "Move file to trash" after successful encoding
        """
        trashdir = self.appdata['trashdir_loc']
        if self.ckbx_trash.IsChecked():
            self.movetotrash = True
            self.ckbx_del.SetValue(True)
            self.ckbx_del.Disable()
            self.emptylist = True
            if not os.path.exists(trashdir):
                os.mkdir(trashdir, mode=0o777)
        else:
            self.movetotrash = False
            self.ckbx_del.Enable()
            self.ckbx_del.SetValue(False)
            self.emptylist = False
    # --------------------------------------------------------------------#

    def on_cancel(self, event):
        """
        exit from formula dialog
        """
        # self.Destroy()
        event.Skip()

    def on_ok(self, event):
        """
        get confirmation to proceed
        """
        # self.Destroy()
        event.Skip()

    def getvalue(self):
        """
        This method return values via the getvalue() interface
        from the caller. See the caller for more info and usage.
        """
        return self.movetotrash, self.emptylist
