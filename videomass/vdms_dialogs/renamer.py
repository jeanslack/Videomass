# -*- coding: UTF-8 -*-

"""
Name: renamer.py
Porpose: batch and single file renamer
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Dec.09.2022
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
import re
import wx


class Renamer(wx.Dialog):
    """
    Simple file renaming dialog.
    It can be used for renaming individual items or for
    groups of items (batch mode). It has dynamic interface
    adaptive for batch mode and single file mode.

    Usage example:
            with Renamer(self,
                         nameprop=_('New Name'),
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
        nameprop (string) – Default value (as text).
        caption (string) – title header on top of window.
        message (string) – the message you want to see
        mode (int) – the "mode" parameter determines the type of renaming
                     See below for specification.

        mode=n (if n >= 1) rename multiple items as many as the given number.
        mode=n (if n == 0) rename an item only.
        Default is 0
        Note that mode=1 means to rename two filenames.

        """
        self.mode = mode
        if self.mode >= 1:
            self.newname = []
        else:
            self.newname = None
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add((10, 10))
        labhead = wx.StaticText(self, wx.ID_ANY, message)
        sizer_base.Add(labhead, 0, wx.EXPAND | wx.ALL, 5)
        self.entry = wx.TextCtrl(self, wx.ID_ANY,
                                 nameprop,
                                 size=(-1, -1)
                                 )
        sizer_base.Add(self.entry, 0, wx.EXPAND | wx.ALL, 5)
        boxsiz = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(boxsiz, 0, wx.EXPAND)
        if self.mode >= 1:
            msg = _("# It will be replaced by increasing "
                    "numbers starting with:")
            labnum = wx.StaticText(self, wx.ID_ANY, msg)
            boxsiz.Add(labnum, 0, wx.ALL | wx.ALIGN_CENTER, 5)
            self.prognum = wx.SpinCtrl(self, wx.ID_ANY,
                                       value="1",
                                       min=0, max=999999999,
                                       # size=(102, -1),
                                       style=wx.SP_ARROW_KEYS
                                       )
            boxsiz.Add(self.prognum, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # confirm buttons:
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        gridexit.Add(btn_close, 0, wx.ALL, 5)
        self.btn_ok = wx.Button(self, wx.ID_OK, "")
        gridexit.Add(self.btn_ok, 0, wx.ALL, 5)
        sizer_base.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)

        self.SetTitle(caption)
        self.SetMinSize((512, -1))
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        # ----------------------Binding (EVT)--------------------------#

        self.Bind(wx.EVT_TEXT, self.on_entry_text, self.entry)
        if self.mode >= 1:
            self.Bind(wx.EVT_SPINCTRL, self.on_get_startnumber, self.prognum)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
    # ------------------------------------------------------------------#

    def rename_file(self):
        """
        Set the newname attribute.
        Return str(newname)
        """
        #self.newname = self.entry.GetValue()
        #return self.newname


        if self.entry.GetValue() == '' or self.entry.GetValue().isspace():
            self.btn_ok.Disable()
            self.newname = None
            return None
        self.btn_ok.Enable()
        self.newname = self.entry.GetValue()
        return self.newname
    # ------------------------------------------------------------------#

    def rename_batch(self):
        """
        Set newname attribute.
        Return tuple(str(newname), int(startnum))
        """
        string =  self.entry.GetValue()
        startnum = self.prognum.GetValue()
        group = re.findall(r'((\#)\#*)', string)
        if len(group) > 1:
            self.btn_ok.Disable()
            del self.newname[:]
            return None
        if '#' not in string:
            self.btn_ok.Disable()
            del self.newname[:]
            return None

        self.btn_ok.Enable()
        try:
            lastidx = string.rindex('#')
        except ValueError:
            del self.newname[:]
            return None

        self.newname = [string for x in range(self.mode)]
        for num, name in enumerate(self.newname):
            temp = list(name)
            temp[lastidx] = str(startnum+num)
            self.newname[num] = re.sub('#','0', ''.join(temp))

        return self.newname
    # ----------------------Event handler (callback)----------------------#

    def on_get_startnumber(self, event):
        """
        Updates the rename_batch datas, during SpinCtrl event
        """
        self.rename_batch()
    # ------------------------------------------------------------------#

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
        This method return values via the interface getvalue()
        by the caller. See Renamer class docstring or the caller
        for more info and usage.
        """
        if not self.newname:
            if self.mode >= 1:
                return self.rename_batch()

            return self.rename_file()

        return self.newname
