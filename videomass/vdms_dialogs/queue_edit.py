# -*- coding: UTF-8 -*-
"""
Name: edit_queue.py
Porpose: edit a selected item queue
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Apr.03.2024
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


class Edit_Queue_Item(wx.Dialog):
    """
    This dialog is useful to edit command arguments on the fly
    before run the process.

    """
    PASS_1 = _("One-Pass, Do not start with `ffmpeg "
               "-i filename`; do not end with "
               "`output-filename`"
               )
    PASS_2 = _("Two-Pass (optional), Do not start with "
               "`ffmpeg -i filename`; do not end with "
               "`output-filename`"
               )
    # ------------------------------------------------------------------

    def __init__(self, parent, kwargs):
        """
        `kwargs` is a class dict
        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.kwargs = kwargs
        if self.appdata['ostype'] == 'Darwin':
            fontsize = 10
        else:
            fontsize = 8

        wx.Dialog.__init__(self, parent, -1,
                           _("Videomass - Edit the selected "
                             "item in the queue"),
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        size_base = wx.BoxSizer(wx.VERTICAL)
        size_base.Add((0, 15), 0)
        labpass1 = wx.StaticText(self, wx.ID_ANY, Edit_Queue_Item.PASS_1)
        size_base.Add(labpass1, 0, wx.ALL | wx.EXPAND, 5)
        self.pass_1_cmd = wx.TextCtrl(self, wx.ID_ANY, "",
                                      style=wx.TE_MULTILINE
                                      )
        size_base.Add(self.pass_1_cmd, 1, wx.ALL | wx.EXPAND, 5)

        msg = _("Pre-input arguments for One-Pass (optional)")
        labpre1 = wx.StaticText(self, wx.ID_ANY, msg)
        size_base.Add(labpre1, 0, wx.ALL | wx.EXPAND, 5)

        self.pass_1_pre = wx.TextCtrl(self, wx.ID_ANY, "")
        size_base.Add(self.pass_1_pre, 0, wx.ALL | wx.EXPAND, 5)
        self.pass_1_cmd.SetFont(wx.Font(fontsize,
                                        wx.FONTFAMILY_TELETYPE,
                                        wx.NORMAL,
                                        wx.NORMAL
                                        ))
        self.pass_1_cmd.SetToolTip(_('FFmpeg arguments for one-pass encoding'))
        self.pass_1_pre.SetFont(wx.Font(fontsize,
                                        wx.FONTFAMILY_TELETYPE,
                                        wx.NORMAL,
                                        wx.NORMAL
                                        ))
        tip = (_('Any optional arguments to add before input file on the '
                 'one-pass encoding, e.g required names of some hardware '
                 'accelerations like -hwaccel to use with CUDA.'))
        self.pass_1_pre.SetToolTip(tip)
        self.pass_1_cmd.AppendText(self.kwargs['args'][0])  # command 1
        self.pass_1_pre.AppendText(self.kwargs['pre-input-1'])  # input 1
        # box
        if self.kwargs['args'][1].strip() != '':
            labpass2 = wx.StaticText(self, wx.ID_ANY, Edit_Queue_Item.PASS_2)
            size_base.Add(labpass2, 0, wx.ALL | wx.EXPAND, 5)
            self.pass_2_cmd = wx.TextCtrl(self, wx.ID_ANY, "",
                                          style=wx.TE_MULTILINE
                                          )
            size_base.Add(self.pass_2_cmd, 1, wx.ALL | wx.EXPAND, 5)
            msg = _("Pre-input arguments for Two-Pass (optional)")
            labpre2 = wx.StaticText(self, wx.ID_ANY, msg)
            size_base.Add(labpre2, 0, wx.ALL | wx.EXPAND, 5)

            self.pass_2_pre = wx.TextCtrl(self, wx.ID_ANY, "")
            size_base.Add(self.pass_2_pre, 0, wx.ALL | wx.EXPAND, 5)
            self.pass_2_cmd.SetFont(wx.Font(fontsize,
                                            wx.FONTFAMILY_TELETYPE,
                                            wx.NORMAL,
                                            wx.NORMAL
                                            ))
            tip = _('FFmpeg arguments for two-pass encoding')
            self.pass_2_cmd.SetToolTip(tip)
            self.pass_2_pre.SetFont(wx.Font(fontsize,
                                            wx.FONTFAMILY_TELETYPE,
                                            wx.NORMAL,
                                            wx.NORMAL
                                            ))
            tip = (_('Any optional arguments to add before input file on the '
                     'two-pass encoding, e.g required names of some hardware '
                     'accelerations like -hwaccel to use with CUDA.'))
            self.pass_2_pre.SetToolTip(tip)
            self.pass_2_cmd.AppendText(self.kwargs['args'][1])
            self.pass_2_pre.AppendText(self.kwargs['pre-input-2'])
            minsize = (800, 550)
        else:
            minsize = (800, 275)

        # ----- confirm buttons section
        btncancel = wx.Button(self, wx.ID_CANCEL, "")
        btnok = wx.Button(self, wx.ID_OK)
        btngrid = wx.FlexGridSizer(1, 2, 0, 0)
        btngrid.Add(btncancel, 0)
        btngrid.Add(btnok, 0, wx.LEFT, 5)
        size_base.Add(btngrid, flag=wx.ALL
                      | wx.ALIGN_RIGHT
                      | wx.RIGHT, border=5
                      )
        # ------ Set Layout
        self.SetMinSize(minsize)
        self.SetSizer(size_base)
        self.Fit()
        self.Layout()

        # ----------------------Binder (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_cancel, btncancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btnok)

    # ---------------------Callbacks (event handler)----------------------#

    def on_ok(self, event):
        """
        Accept and close this dialog.
        Don't use self.Destroy() here.
        """
        self.kwargs['args'][0] = self.pass_1_cmd.GetValue()
        self.kwargs['pre-input-1'] = self.pass_1_pre.GetValue()

        if self.kwargs['args'][1].strip() != '':
            self.kwargs['pre-input-2'] = self.pass_2_pre.GetValue()
            self.kwargs['args'][1] = self.pass_2_cmd.GetValue()

        event.Skip()
    # ------------------------------------------------------------------#

    def on_cancel(self, event):
        """
        Close this dialog without saving anything
        """
        event.Skip()
    # ------------------------------------------------------------------#
