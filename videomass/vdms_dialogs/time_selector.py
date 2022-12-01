# -*- coding: UTF-8 -*-
"""
Name: time_selector.py
Porpose: an alternative tool to adjust the time selection.
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.29.2022
Code checker: flake8, pylint
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
import wx
from videomass.vdms_utils.utils import get_milliseconds
# import wx.lib.masked as masked (not work on macOSX)


class Time_Selector(wx.Dialog):
    """
    This dialog is an alternative way to adjust the time selection
    FIXME: replace spinctrl with a timer spin float ctrl if exist

    """
    def __init__(self, parent, seektxt, cuttxt):
        """
        When this dialog is called, the values already set
        in the timeline panel are reproduced exactly here.

        """
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        staticbox1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                        _("Seek"))), wx.VERTICAL)
        boxsiz1 = wx.BoxSizer(wx.HORIZONTAL)
        staticbox1.Add(boxsiz1, 0, wx.ALL | wx.ALIGN_CENTER, 0)
        sizer_base.Add(staticbox1, 0, wx.ALL | wx.EXPAND, 5)

        self.seek_hour = wx.SpinCtrl(self, wx.ID_ANY, value=f"{seektxt[0:2]}",
                                     min=0, max=23, style=wx.SP_ARROW_KEYS)
        boxsiz1.Add(self.seek_hour, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        lab1 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        boxsiz1.Add(lab1, 0, wx.ALIGN_CENTER, 5)

        self.seek_min = wx.SpinCtrl(self, wx.ID_ANY, value=f"{seektxt[3:5]}"
                                    , min=0, max=59, style=wx.SP_ARROW_KEYS)
        boxsiz1.Add(self.seek_min, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        lab2 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        boxsiz1.Add(lab2, 0, wx.ALIGN_CENTER, 5)

        self.seek_sec = wx.SpinCtrl(self, wx.ID_ANY, value=f"{seektxt[6:8]}",
                                    min=0, max=59, style=wx.SP_ARROW_KEYS)
        boxsiz1.Add(self.seek_sec, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        lab3 = wx.StaticText(self, wx.ID_ANY, ("."))
        lab3.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        boxsiz1.Add(lab3, 0, wx.ALIGN_CENTER, 5)

        self.seek_mills = wx.SpinCtrl(self, wx.ID_ANY,
                                      value=f"{seektxt[9:12]}",
                                      min=000, max=999,
                                      style=wx.SP_ARROW_KEYS)
        boxsiz1.Add(self.seek_mills, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        staticbox2 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                        _("Duration"))), wx.VERTICAL)
        sizer_base.Add(staticbox2, 0, wx.ALL | wx.EXPAND, 5)
        boxsiz2 = wx.BoxSizer(wx.HORIZONTAL)
        staticbox2.Add(boxsiz2, 0, wx.ALL | wx.ALIGN_CENTER, 0)

        self.duration_hour = wx.SpinCtrl(self, wx.ID_ANY,
                                         value=f"{cuttxt[0:2]}", min=0, max=23,
                                         style=wx.SP_ARROW_KEYS)
        boxsiz2.Add(self.duration_hour, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        lab4 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab4.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        boxsiz2.Add(lab4, 0, wx.ALIGN_CENTER, 5)

        self.duration_min = wx.SpinCtrl(self, wx.ID_ANY,
                                        value=f"{cuttxt[3:5]}", min=0, max=59,
                                        style=wx.SP_ARROW_KEYS)
        boxsiz2.Add(self.duration_min, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        lab5 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab5.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        boxsiz2.Add(lab5, 0, wx.ALIGN_CENTER, 5)

        self.duration_sec = wx.SpinCtrl(self, wx.ID_ANY,
                                        value=f"{cuttxt[6:8]}", min=0, max=59,
                                        style=wx.SP_ARROW_KEYS)
        boxsiz2.Add(self.duration_sec, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        lab6 = wx.StaticText(self, wx.ID_ANY, ("."))
        lab6.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        boxsiz2.Add(lab6, 0, wx.ALIGN_CENTER, 5)

        self.duration_mills = wx.SpinCtrl(self, wx.ID_ANY,
                                          value=f"{cuttxt[9:12]}",
                                          min=000, max=999,
                                          style=wx.SP_ARROW_KEYS)
        boxsiz2.Add(self.duration_mills, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # confirm btn section:
        gridbtn = wx.GridSizer(1, 2, 0, 0)
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_reset = wx.Button(self, wx.ID_CLEAR, _("Reset"))
        gridbtn.Add(btn_reset, 0, wx.ALL, 5)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        gridexit.Add(btn_close, 0, wx.ALL, 5)
        btn_ok = wx.Button(self, wx.ID_OK, _("Apply"))
        gridexit.Add(btn_ok, 0, wx.ALL, 5)
        gridbtn.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)
        sizer_base.Add(gridbtn, 0, wx.EXPAND)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # ----------------------Properties ----------------------#
        self.SetTitle(_('Time Selection Adjustment'))

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.resetvalues, btn_reset)
    # ----------------------Event handler (callback)----------------------#

    def resetvalues(self, event):
        """
        Reset all values at initial state. Is need to confirm with
        ok Button for apply correctly.
        """
        self.seek_hour.SetValue(0)
        self.seek_min.SetValue(0)
        self.seek_sec.SetValue(0)
        self.seek_mills.SetValue(0)
        self.duration_hour.SetValue(0)
        self.duration_min.SetValue(0)
        self.duration_sec.SetValue(0)
        self.duration_mills.SetValue(0)
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        Close this dialog without saving anything
        """
        event.Skip()  # need if destroy from parent
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        if you enable self.Destroy(), it delete from memory all data
        event and no return correctly. It has the right behavior if
        not used here, because it is called in the main frame.

        Event.Skip(), work correctly here. Sometimes needs to disable
        it for needs to maintain the view of the window (for exemple).
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def getvalue(self):
        """
        This method return values via the interface GetValue()
        """
        seek = (f'{self.seek_hour.GetValue()}:'
                f'{self.seek_min.GetValue()}:'
                f'{self.seek_sec.GetValue()}.'
                f'{str(self.seek_mills.GetValue()).zfill(3)}'
                )
        duration = (f'{self.duration_hour.GetValue()}:'
                    f'{self.duration_min.GetValue()}:'
                    f'{self.duration_sec.GetValue()}.'
                    f'{str(self.duration_mills.GetValue()).zfill(3)}'
                    )
        return get_milliseconds(seek), get_milliseconds(duration)
