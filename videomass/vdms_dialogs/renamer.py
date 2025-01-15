# -*- coding: UTF-8 -*-
"""
Name: renamer.py
Porpose: batch and single file renamer
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
import re
import wx


class Renamer(wx.Dialog):
    """
    Simple file renaming dialog.
    It can be used both for renaming individual
    items and groups of items (batch mode). It has
    a dynamic interface for both modes.

    Usage example:
            with Renamer(self,
                         nameprop='New Name',
                         caption='My awesome title',
                         message='My message here',
                         mode=0,
                         ) as dlg:
                if dlg.ShowModal() == wx.ID_OK:
                    newname = dlg.getvalue()

    See __init__ docstring for parameter details.

    """

    def __init__(self,
                 parent,
                 nameprop=str('New name'),
                 caption=str('Caption'),
                 message=str('Message'),
                 mode=int(0),
                 ):
        """
        Parameters:

        parent (wx.Window) – Parent window. Must not be None.
        nameprop (string) – Proposed name, default value as text.
        caption (string) – title header on top of window.
        message (string) – the message you want to see.
        mode (int) – the "mode" parameter determines the type of renaming
                     See below for specification.

        mode=n (if n >= 1) rename multiple items as many as the given number.
        mode=n (if n == 0) rename an item only.
        Default is 0
        Note that mode=1 means to rename two filenames.

        """
        self.mode = mode
        msg = _("# will be replaced by ascending numbers starting with:")
        width = 472
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add((10, 10))
        labhead = wx.StaticText(self, wx.ID_ANY, message)
        sizer_base.Add(labhead, 0, wx.EXPAND | wx.ALL, 5)
        self.entry = wx.TextCtrl(self, wx.ID_ANY,
                                 nameprop,
                                 size=(width, -1)
                                 )
        sizer_base.Add(self.entry, 0, wx.EXPAND | wx.ALL, 5)
        boxsiz = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(boxsiz, 0, wx.EXPAND)
        if self.mode >= 1:
            labnum = wx.StaticText(self, wx.ID_ANY, msg)
            boxsiz.Add(labnum, 0, wx.ALL | wx.ALIGN_CENTER, 5)
            self.prognum = wx.SpinCtrl(self, wx.ID_ANY,
                                       value="1",
                                       min=0, max=999999999,
                                       style=wx.SP_ARROW_KEYS,
                                       )
            boxsiz.Add(self.prognum, 0, wx.ALL | wx.ALIGN_CENTER, 5)
            width = labnum.GetSize()[0] + self.prognum.GetSize()[0]
            self.entry.SetSize(width, -1)

        # confirm buttons:
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        gridexit.Add(btn_close, 0)
        self.btn_ok = wx.Button(self, wx.ID_OK, "")
        gridexit.Add(self.btn_ok, 0, wx.LEFT, 5)
        sizer_base.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 5)

        self.SetTitle(caption)
        # self.SetMinSize((width, -1))
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        # ----------------------Binding (EVT)--------------------------#

        self.Bind(wx.EVT_TEXT, self.on_entry_text, self.entry)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
    # ------------------------------------------------------------------#

    def get_newname(self):
        """
        Set newname attribute.
        Return `list(newname)` if mode >= 1,
        Return `str(newname)` if mode == 0,
        Return `None` if raise ValueError.
        """
        string = self.entry.GetValue()
        if self.mode >= 1:
            startfrom = self.prognum.GetValue()
            try:
                lasthashchar = string.rindex('#')
            except ValueError:
                return None

            newname = [string for x in range(self.mode)]
            for num, name in enumerate(newname):
                temp = list(name)
                temp[lasthashchar] = str(startfrom + num)
                newname[num] = re.sub('#', '0', ''.join(temp))
        else:
            newname = string

        return newname
    # ------------------------------------------------------------------#

    def rename_file(self):
        """
        Checks for consistency of the entered string
        in one file renaming.
        """
        if self.entry.GetValue() == '' or self.entry.GetValue().isspace():
            self.btn_ok.Disable()
            return

        self.btn_ok.Enable()
    # ------------------------------------------------------------------#

    def rename_batch(self):
        """
        Checks for consistency of the entered string
        in batch renaming.
        """
        string = self.entry.GetValue()
        occur = re.findall(r'((\#)\#*)', string)

        if '#' not in string or len(occur) > 1:
            self.btn_ok.Disable()
            return

        self.btn_ok.Enable()
    # ----------------------Event handler (callback)----------------------#

    def on_entry_text(self, event):
        """
        Updates datas given from rename_batch/rename_file,
        during TextCtrl event.
        """
        if self.mode >= 1:
            self.rename_batch()
        else:
            self.rename_file()
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        Close this dialog without saving anything
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Accept and close this dialog.
        Don't use self.Destroy() here.
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def getvalue(self):
        """
        This method return values via the getvalue() interface
        from the caller. See Renamer class docstring or the caller
        for more info and usage.
        """
        return self.get_newname()
