# -*- coding: UTF-8 -*-
"""
Name: time_selector.py
Porpose: an alternative tool to adjust the time selection.
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Dec.11.2022
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
from videomass.vdms_utils.utils import time_to_integer
from videomass.vdms_utils.utils import integer_to_time
# import wx.lib.masked as masked (not work on macOSX)


class Time_Selector(wx.Dialog):
    """
    This dialog is an alternative way to adjust the time selection
    FIXME: replace spinctrl with a timer spin float ctrl if exist

    """
    def __init__(self, parent, seektxt, cuttxt, milliseconds):
        """
        When this dialog is called, the values already set
        in the timeline panel are reproduced exactly here.

        """
        self.seek_mills = time_to_integer(seektxt)
        self.cut_mills = time_to_integer(cuttxt)
        self.milliseconds = milliseconds  # media total duration in ms
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        boxs = wx.StaticBox(self, wx.ID_ANY, (_("Segment Start   "
                                                "(HH:MM:SS.ms)")))
        staticbox1 = wx.StaticBoxSizer(boxs, wx.VERTICAL)
        self.btn_reset_start = wx.Button(self, wx.ID_ANY, _("Reset"))
        staticbox1.Add(self.btn_reset_start, 0, wx.ALL, 5)
        boxsiz1 = wx.BoxSizer(wx.HORIZONTAL)
        staticbox1.Add(boxsiz1, 0, wx.ALL | wx.ALIGN_CENTER, 0)
        sizer_base.Add(staticbox1, 0, wx.ALL | wx.EXPAND, 5)

        self.start_hour = wx.SpinCtrl(self, wx.ID_ANY,
                                      value=f"{seektxt[0:2]}",
                                      min=0, max=23,
                                      style=wx.SP_ARROW_KEYS)

        boxsiz1.Add(self.start_hour, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        lab1 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        boxsiz1.Add(lab1, 0, wx.ALIGN_CENTER, 5)

        self.start_min = wx.SpinCtrl(self, wx.ID_ANY,
                                     value=f"{seektxt[3:5]}",
                                     min=0, max=59,
                                     style=wx.SP_ARROW_KEYS)

        boxsiz1.Add(self.start_min, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        lab2 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        boxsiz1.Add(lab2, 0, wx.ALIGN_CENTER, 5)

        self.start_sec = wx.SpinCtrl(self, wx.ID_ANY,
                                     value=f"{seektxt[6:8]}",
                                     min=0, max=59,
                                     style=wx.SP_ARROW_KEYS)

        boxsiz1.Add(self.start_sec, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        lab3 = wx.StaticText(self, wx.ID_ANY, ("."))
        lab3.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        boxsiz1.Add(lab3, 0, wx.ALIGN_CENTER, 5)

        self.start_mills = wx.SpinCtrl(self, wx.ID_ANY,
                                       value=f"{seektxt[9:12]}",
                                       min=000, max=999,
                                       style=wx.SP_ARROW_KEYS)

        boxsiz1.Add(self.start_mills, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        boxs = wx.StaticBox(self, wx.ID_ANY, (_("Segment Duration   "
                                                "(HH:MM:SS.ms)")))
        staticbox2 = wx.StaticBoxSizer(boxs, wx.VERTICAL)
        self.btn_reset_dur = wx.Button(self, wx.ID_ANY, _("Reset"))
        staticbox2.Add(self.btn_reset_dur, 0, wx.ALL, 5)
        sizer_base.Add(staticbox2, 0, wx.ALL | wx.EXPAND, 5)
        boxsiz2 = wx.BoxSizer(wx.HORIZONTAL)
        staticbox2.Add(boxsiz2, 0, wx.ALL | wx.ALIGN_CENTER, 0)

        self.duration_hour = wx.SpinCtrl(self, wx.ID_ANY,
                                         value=f"{cuttxt[0:2]}",
                                         min=0, max=23,
                                         style=wx.SP_ARROW_KEYS)
        boxsiz2.Add(self.duration_hour, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        lab4 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab4.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        boxsiz2.Add(lab4, 0, wx.ALIGN_CENTER, 5)

        self.duration_min = wx.SpinCtrl(self, wx.ID_ANY,
                                        value=f"{cuttxt[3:5]}",
                                        min=0, max=59,
                                        style=wx.SP_ARROW_KEYS)
        boxsiz2.Add(self.duration_min, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        lab5 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab5.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        boxsiz2.Add(lab5, 0, wx.ALIGN_CENTER, 5)

        self.duration_sec = wx.SpinCtrl(self, wx.ID_ANY,
                                        value=f"{cuttxt[6:8]}",
                                        min=0, max=59,
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

        # confirm buttons:
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        gridexit.Add(btn_close, 0, wx.ALL, 5)
        btn_ok = wx.Button(self, wx.ID_OK, "")
        gridexit.Add(btn_ok, 0, wx.ALL, 5)
        sizer_base.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # ----------------------Properties ----------------------#
        self.SetTitle(_('Time Selection Adjustment'))
        self.duration_hour.SetToolTip(_("Duration hours"))
        self.duration_min.SetToolTip(_("Duration minutes"))
        self.duration_sec.SetToolTip(_("Duration seconds"))
        self.duration_mills.SetToolTip(_("Duration milliseconds"))
        self.start_hour.SetToolTip(_("Start hours"))
        self.start_min.SetToolTip(_("Start minutes"))
        self.start_sec.SetToolTip(_("Start seconds"))
        self.start_mills.SetToolTip(_("Start milliseconds"))

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_reset_start, self.btn_reset_start)
        self.Bind(wx.EVT_SPINCTRL, self.on_start, self.start_hour)
        self.Bind(wx.EVT_SPINCTRL, self.on_start, self.start_min)
        self.Bind(wx.EVT_SPINCTRL, self.on_start, self.start_sec)
        self.Bind(wx.EVT_SPINCTRL, self.on_start, self.start_mills)
        self.Bind(wx.EVT_SPINCTRL, self.on_duration, self.duration_hour)
        self.Bind(wx.EVT_SPINCTRL, self.on_duration, self.duration_min)
        self.Bind(wx.EVT_SPINCTRL, self.on_duration, self.duration_sec)
        self.Bind(wx.EVT_SPINCTRL, self.on_duration, self.duration_mills)
        self.Bind(wx.EVT_BUTTON, self.reset_all_values, self.btn_reset_dur)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)

        if self.cut_mills > 0:
            self.enable_start_ctrls(True)
        else:
            self.enable_start_ctrls(False)

    # ----------------------Event handler (callback)----------------------#

    def resetvalues(self, reset='all'):
        """
        Reset values by default arg.
        """
        if reset == 'all':
            self.start_hour.SetValue(0)
            self.start_min.SetValue(0)
            self.start_sec.SetValue(0)
            self.start_mills.SetValue(0)
            self.duration_hour.SetValue(0)
            self.duration_min.SetValue(0)
            self.duration_sec.SetValue(0)
            self.duration_mills.SetValue(0)
        elif reset == 'start':
            self.start_hour.SetValue(0)
            self.start_min.SetValue(0)
            self.start_sec.SetValue(0)
            self.start_mills.SetValue(0)
        elif reset == 'duration':
            self.duration_hour.SetValue(0)
            self.duration_min.SetValue(0)
            self.duration_sec.SetValue(0)
            self.duration_mills.SetValue(0)
    # ------------------------------------------------------------------#

    def get_duration_values(self):
        """
        Returns a list object with `duration` values
        `[str(timeformat), int(milliseconds)]`
        """
        duration = (f'{self.duration_hour.GetValue()}:'
                    f'{self.duration_min.GetValue()}:'
                    f'{self.duration_sec.GetValue()}.'
                    f'{str(self.duration_mills.GetValue()).zfill(3)}'
                    )
        return duration, time_to_integer(duration)
    # ------------------------------------------------------------------#

    def get_start_values(self):
        """
        Returns a list object with `start` values
        `[str(timeformat), int(milliseconds)]`
        """
        start = (f'{self.start_hour.GetValue()}:'
                 f'{self.start_min.GetValue()}:'
                 f'{self.start_sec.GetValue()}.'
                 f'{str(self.start_mills.GetValue()).zfill(3)}'
                 )
        return start, time_to_integer(start)
    # ------------------------------------------------------------------#

    def enable_start_ctrls(self, enable=True):
        """
        Enables or disables spin controls by default arg
        """
        if enable:
            self.start_hour.Enable()
            self.start_min.Enable()
            self.start_sec.Enable()
            self.start_mills.Enable()
            self.btn_reset_start.Enable()
        else:
            self.start_hour.Disable()
            self.start_min.Disable()
            self.start_sec.Disable()
            self.start_mills.Disable()
            self.btn_reset_start.Disable()
    # ------------------------------------------------------------------#

    def on_reset_start(self, event):
        """
        Resets all spin ctrls of the Start time
        """
        self.resetvalues('start')
    # ------------------------------------------------------------------#

    def on_duration(self, event):
        """
        This handler method is reserved to all duration spin controls
        """
        duration = self.get_duration_values()
        start = self.get_start_values()

        if duration[1] > 0:
            self.enable_start_ctrls(True)
        else:
            self.enable_start_ctrls(False)
            self.resetvalues(reset='start')

        entersum = start[1] + duration[1]
        if entersum > self.milliseconds:
            setmax = integer_to_time(self.milliseconds - start[1])
            h, m, s = setmax.split(':')
            sec, ms = s.split('.')
            self.duration_hour.SetValue(int(h))
            self.duration_min.SetValue(int(m))
            self.duration_sec.SetValue(int(sec))
            self.duration_mills.SetValue(int(ms))
    # ------------------------------------------------------------------#

    def on_start(self, event):
        """
        This handler method is reserved to all duration spin controls
        """
        duration = self.get_duration_values()
        start = self.get_start_values()
        entersum = start[1] + duration[1]

        if entersum > self.milliseconds:
            setmax = integer_to_time(self.milliseconds - duration[1])
            h, m, s = setmax.split(':')
            sec, ms = s.split('.')
            self.start_hour.SetValue(int(h))
            self.start_min.SetValue(int(m))
            self.start_sec.SetValue(int(sec))
            self.start_mills.SetValue(int(ms))
    # ------------------------------------------------------------------#

    def reset_all_values(self, event):
        """
        On click reset btn, Reset all values.
        """
        self.resetvalues('all')
        self.enable_start_ctrls(False)
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
        return self.get_start_values()[1], self.get_duration_values()[1]
