# -*- coding: UTF-8 -*-
# Name: time_selection.py
# Porpose: show dialog to set duration and time sequences
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.06.2020 *PEP8 compatible*
#########################################################

# This file is part of Videomass.

#    Videomass is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass.  If not, see <http://www.gnu.org/licenses/>.

#########################################################
import wx
import webbrowser
# import wx.lib.masked as masked # not work on macOSX


class Time_Duration(wx.Dialog):
    """
    This class show a simple dialog with a timer selection
    to set duration.
    FIXME: replace spinctrl with a timer spin float ctrl if exist
    """
    def __init__(self, parent, hasSet):
        """
        FFmpeg use this format to specifier a duration range:
        "-ss 00:00:00 -t 00:00:00". The -ss flag is the initial
        start selection time; the -t flag is the duration time amount
        starting from -ss. All this one is specified by hours, minutes
        and seconds values.
        See FFmpeg documents for more details.
        When this dialog is called, the values previously set are returned
        for a complete reading (if there are preconfigured values)
        """
        if hasSet == '':
            self.init_hour = '00'
            self.init_minute = '00'
            self.init_seconds = '00'
            self.cut_hour = '00'
            self.cut_minute = '00'
            self.cut_seconds = '00'
        else:  # return a previus settings:
            self.init_hour = hasSet[4:6]
            self.init_minute = hasSet[7:9]
            self.init_seconds = hasSet[10:12]
            self.cut_hour = hasSet[16:18]
            self.cut_minute = hasSet[19:21]
            self.cut_seconds = hasSet[22:24]

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        """constructor """
        self.start_hour_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                  self.init_hour), min=0, max=23, style=wx.TE_PROCESS_ENTER)
        lab1 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.start_minute_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                self.init_minute), min=0, max=59, style=wx.TE_PROCESS_ENTER)
        lab2 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.start_second_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
               self.init_seconds), min=0, max=59, style=wx.TE_PROCESS_ENTER)
        sizerbox = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                        _("Seeking - start point [h : m : s]"))), wx.VERTICAL)
        self.stop_hour_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                   self.cut_hour), min=0, max=23, style=wx.TE_PROCESS_ENTER)
        lab3 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab3.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.stop_minute_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                 self.cut_minute), min=0, max=59, style=wx.TE_PROCESS_ENTER)
        lab4 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab4.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.stop_second_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                self.cut_seconds), min=0, max=59, style=wx.TE_PROCESS_ENTER)
        sizer_2_staticbox = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                        _("Cut - end point [h : m : s]"))), wx.VERTICAL)
        btn_help = wx.Button(self, wx.ID_HELP, "", size=(-1, -1))
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        btn_ok = wx.Button(self, wx.ID_OK, "")
        btn_reset = wx.Button(self, wx.ID_CLEAR, "")

        # ----------------------Properties ----------------------#
        self.SetTitle(_('Videomass: duration'))
        # self.start_hour_ctrl.SetMinSize((100,-1 ))
        # self.start_minute_ctrl.SetMinSize((100, -1))
        # self.start_second_ctrl.SetMinSize((100, -1))
        self.start_hour_ctrl.SetToolTip(_("Hours time"))
        self.start_minute_ctrl.SetToolTip(_("Minutes Time"))
        self.start_second_ctrl.SetToolTip(_("Seconds time"))
        # self.stop_hour_ctrl.SetMinSize((100, -1))
        # self.stop_minute_ctrl.SetMinSize((100, -1))
        # self.stop_second_ctrl.SetMinSize((100, -1))
        self.stop_hour_ctrl.SetToolTip(_("Hours amount duration"))
        self.stop_minute_ctrl.SetToolTip(_("Minutes amount duration"))
        self.stop_second_ctrl.SetToolTip(_("Seconds amount duration"))
        # ----------------------Layout----------------------#
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        gridFlex1 = wx.FlexGridSizer(1, 5, 0, 0)
        gridFlex2 = wx.FlexGridSizer(1, 5, 0, 0)

        sizer_base.Add(sizerbox, 0, wx.ALL | wx.EXPAND, 10)
        sizerbox.Add(gridFlex1, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        gridFlex1.Add(self.start_hour_ctrl, 0, wx.ALL |
                      wx.ALIGN_CENTER_VERTICAL, 5
                      )
        gridFlex1.Add(lab1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridFlex1.Add(self.start_minute_ctrl, 0, wx.ALL |
                      wx.ALIGN_CENTER_VERTICAL, 5
                      )
        gridFlex1.Add(lab2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridFlex1.Add(self.start_second_ctrl, 0, wx.ALL |
                      wx.ALIGN_CENTER_VERTICAL, 5
                      )
        sizer_base.Add(sizer_2_staticbox, 0, wx.ALL | wx.EXPAND, 10)
        sizer_2_staticbox.Add(gridFlex2, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        gridFlex2.Add(self.stop_hour_ctrl, 0, wx.ALL |
                      wx.ALIGN_CENTER_VERTICAL, 5
                      )
        gridFlex2.Add(lab3, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridFlex2.Add(self.stop_minute_ctrl, 0, wx.ALL |
                      wx.ALIGN_CENTER_VERTICAL, 5
                      )
        gridFlex2.Add(lab4, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridFlex2.Add(self.stop_second_ctrl, 0,
                      wx.ALL |
                      wx.ALIGN_CENTER_VERTICAL, 5
                      )

        gridBtn = wx.GridSizer(1, 2, 0, 0)
        gridhelp = wx.GridSizer(1, 1, 0, 0)
        gridhelp.Add(btn_help, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridBtn.Add(gridhelp)

        gridexit = wx.BoxSizer(wx.HORIZONTAL)

        gridexit.Add(btn_close, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridexit.Add(btn_ok, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridexit.Add(btn_reset, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridBtn.Add(gridexit, 0,
                    flag=wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=0
                    )
        sizer_base.Add(gridBtn, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_SPINCTRL, self.start_hour, self.start_hour_ctrl)
        self.Bind(wx.EVT_SPINCTRL, self.start_minute, self.start_minute_ctrl)
        self.Bind(wx.EVT_SPINCTRL, self.start_second, self.start_second_ctrl)
        self.Bind(wx.EVT_SPINCTRL, self.stop_hour, self.stop_hour_ctrl)
        self.Bind(wx.EVT_SPINCTRL, self.stop_minute, self.stop_minute_ctrl)
        self.Bind(wx.EVT_SPINCTRL, self.stop_second, self.stop_second_ctrl)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.resetValues, btn_reset)

    # ----------------------Event handler (callback)----------------------#

    def start_hour(self, event):
        self.init_hour = '%s' % self.start_hour_ctrl.GetValue()
        if len(self.init_hour) == 1:
            self.init_hour = '0%s' % self.start_hour_ctrl.GetValue()
    # ------------------------------------------------------------------#

    def start_minute(self, event):
        self.init_minute = '%s' % self.start_minute_ctrl.GetValue()
        if len(self.init_minute) == 1:
            self.init_minute = '0%s' % self.start_minute_ctrl.GetValue()
    # ------------------------------------------------------------------#

    def start_second(self, event):
        self.init_seconds = '%s' % self.start_second_ctrl.GetValue()
        if len(self.init_seconds) == 1:
            self.init_seconds = '0%s' % self.start_second_ctrl.GetValue()
    # ------------------------------------------------------------------#

    def stop_hour(self, event):
        self.cut_hour = '%s' % self.stop_hour_ctrl.GetValue()
        if len(self.cut_hour) == 1:
            self.cut_hour = '0%s' % self.stop_hour_ctrl.GetValue()
    # ------------------------------------------------------------------#

    def stop_minute(self, event):
        self.cut_minute = '%s' % self.stop_minute_ctrl.GetValue()
        if len(self.cut_minute) == 1:
            self.cut_minute = '0%s' % self.stop_minute_ctrl.GetValue()
    # ------------------------------------------------------------------#

    def stop_second(self, event):
        self.cut_seconds = '%s' % self.stop_second_ctrl.GetValue()
        if len(self.cut_seconds) == 1:
            self.cut_seconds = '0%s' % self.stop_second_ctrl.GetValue()
    # ------------------------------------------------------------------#

    def resetValues(self, event):
        """
        Reset all values at initial state. Is need to confirm with
        ok Button for apply correctly.
        """
        self.start_hour_ctrl.SetValue(0), self.start_minute_ctrl.SetValue(0),
        self.start_second_ctrl.SetValue(0), self.stop_hour_ctrl.SetValue(0),
        self.stop_minute_ctrl.SetValue(0), self.stop_second_ctrl.SetValue(0)
        self.init_hour, self.init_minute, self.init_seconds = '00', '00', '00'
        self.cut_hour, self.cut_minute, self.cut_seconds = '00', '00', '00'
    # ------------------------------------------------------------------#

    def on_help(self, event):
        """
        """
        page = ('https://jeanslack.github.io/Videomass/Pages/'
                'Toolbar/Duration.html')
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def on_close(self, event):
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
        ss = "%s:%s:%s" % (self.init_hour, self.init_minute, self.init_seconds)
        t = "%s:%s:%s" % (self.cut_hour, self.cut_minute, self.cut_seconds)
        if ss != "00:00:00":
            if t == "00:00:00":
                wx.MessageBox(_("Length of cut missing: "
                                "Cut (end point) [hh,mm,ss]\n\n"
                                "You should calculate the time amount between "
                                "the Seeking (start point) and the cut point, "
                                "then insert it in 'Cut (end point)'. Always "
                                "consider the total duration of the flow in "
                                "order to avoid entering incorrect values."),
                              "Duration",
                              wx.ICON_INFORMATION, self
                              )
                return

        self.GetValue()
        # self.Destroy()
        event.Skip()
    # ------------------------------------------------------------------#

    def GetValue(self):
        """
        This method return values via the interface GetValue()
        """
        cut_range = "-ss %s:%s:%s -t %s:%s:%s" % (self.init_hour,
                                                  self.init_minute,
                                                  self.init_seconds,
                                                  self.cut_hour,
                                                  self.cut_minute,
                                                  self.cut_seconds
                                                  )
        return cut_range
