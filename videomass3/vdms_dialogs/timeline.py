# -*- coding: UTF-8 -*-
# Name: time_selection.py
# Porpose: show dialog to set duration and time sequences
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Dec.08.2020 *PEP8 compatible*
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
from videomass3.vdms_utils.utils import time_human
# import wx.lib.masked as masked # not work on macOSX


class Timeline(wx.Dialog):
    """
    This class show dialog box to set a time range selection and
    get data in the FFmpeg syntax using this form :
    "-ss 00:00:00 -t 00:00:00" .
    The -ss flag is the initial start selection time; the -t flag
    is the duration time amount starting from -ss. All this one is
    specified by hours, minutes and seconds values.
    See FFmpeg documents for more details.

    FIXME: replace spinctrl with a timer spin float ctrl if exist
    """
    get = wx.GetApp()
    OS = get.OS
    RW = 600  # ruler width
    RM = 0   # ruler margin
    PW = 600  # panel width
    PH = 50  # panel height

    def __init__(self, parent, curset, duration):
        """
        If no file has a duration, the limit to the maximum time
        selection is set (86400 sec. = 23:59:59), to allow for
        example slideshows with images.

        """
        if not duration:
            msg0 = _('The maximum time selection is set to 23:59:59, to '
                     'allow make the slideshows')
            self.seconds = Timeline.PW / 86400  # secs/px ratio
            self.timeHum = time_human(86400)  # readable string i.e. 01:01:59
            h_range, m_range, s_range = 23, 59, 59  # set max limit
        else:
            msg0 = _('The maximum time refers to the file with the longest '
                     'duration')
            self.seconds = Timeline.PW / duration  # secs/px ratio
            # convert seconds to readable string i.e. 01:01:59
            self.timeHum = time_human(duration)
            h, m, s = self.timeHum.split(':')
            # set max limit
            h_range = 0 if h == '00' else int(h)
            m_range = 0 if m == '00' else int(m) if h == '00' else 59
            s_range = 0 if s == '00' else int(s) if m == '00' else 59
            #print(h_range, m_range, s_range)

        self.minutes = self.seconds * 60  # min/px ratio
        self.hours = self.minutes * 60  # hours/px ratio
        self.bar_w = 0  # width value for time bar selection
        self.bar_x = 0  # x axis value for time bar selection

        if curset == '':
            self.init_hour = '00'
            self.init_minute = '00'
            self.init_seconds = '00'
            self.cut_hour = '00'
            self.cut_minute = '00'
            self.cut_seconds = '00'
        else:  # return a previus settings:
            self.init_hour = curset[4:6]
            self.init_minute = curset[7:9]
            self.init_seconds = curset[10:12]
            self.cut_hour = curset[16:18]
            self.cut_minute = curset[19:21]
            self.cut_seconds = curset[22:24]

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        """constructor """
        #self.font = wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            #wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch'
                            #)
        sizer_base = wx.BoxSizer(wx.VERTICAL)

        box_displ = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, _(
                                'Time selection display')), wx.VERTICAL)
        sizer_base.Add(box_displ, 0, wx.ALL | wx.CENTRE, 10)
        self.paneltime = wx.Panel(self, wx.ID_ANY,
                                  size=(Timeline.PW, Timeline.PH)
                                  )
        box_displ.Add(self.paneltime, 0, wx.ALL | wx.CENTRE, 10)

        label0 = wx.StaticText(self, wx.ID_ANY,(msg0))
        box_displ.Add(label0, 0, wx.BOTTOM | wx.CENTRE, 5)

        self.start_hour_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                  self.init_hour), min=0, max=h_range, style=wx.TE_PROCESS_ENTER)
        lab1 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

        self.start_minute_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                self.init_minute), min=0, max=m_range, style=wx.TE_PROCESS_ENTER)
        lab2 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

        self.start_second_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
               self.init_seconds), min=0, max=s_range, style=wx.TE_PROCESS_ENTER)

        msg1 = _("Seeking - [hours : minutes : seconds]")
        boxSeek = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (msg1)),
                                    wx.VERTICAL)
        self.stop_hour_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                   self.cut_hour), min=0, max=h_range, style=wx.TE_PROCESS_ENTER)
        lab3 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab3.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.stop_minute_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                 self.cut_minute), min=0, max=m_range, style=wx.TE_PROCESS_ENTER)
        lab4 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab4.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.stop_second_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "%s" % (
                self.cut_seconds), min=0, max=s_range, style=wx.TE_PROCESS_ENTER)
        msg2 = _("Cut - [hours : minutes : seconds]")
        boxCut = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (msg2)),
                                   wx.VERTICAL)
        btn_help = wx.Button(self, wx.ID_HELP, "", size=(-1, -1))
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        btn_ok = wx.Button(self, wx.ID_OK, _("Apply"))
        btn_reset = wx.Button(self, wx.ID_CLEAR, _("Reset"))

        # ----------------------Properties ----------------------#
        self.SetTitle(_('Timeline'))
        self.paneltime.SetBackgroundColour(wx.Colour('#1b0413'))

        self.start_hour_ctrl.SetToolTip(_("Seek to given time position "
                                          "by hours"))
        self.start_minute_ctrl.SetToolTip(_("Seek to given time position "
                                            "by minutes"))
        self.start_second_ctrl.SetToolTip(_("Seek to given time position "
                                            "by seconds"))
        self.stop_hour_ctrl.SetToolTip(_("Total amount duration by hours"))
        self.stop_minute_ctrl.SetToolTip(_("Total amount duration by minutes"))
        self.stop_second_ctrl.SetToolTip(_("Total amount duration by seconds"))

        if Timeline.OS == 'Darwin':
            label0.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            label0.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        # ----------------------Layout----------------------#


        gridFlex1 = wx.FlexGridSizer(1, 5, 0, 0)
        gridFlex2 = wx.FlexGridSizer(1, 5, 0, 0)

        sizer_base.Add(boxSeek, 0, wx.ALL | wx.EXPAND, 10)
        boxSeek.Add(gridFlex1, 0, wx.ALL | wx.ALIGN_CENTER, 5)
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
        sizer_base.Add(boxCut, 0, wx.ALL | wx.EXPAND, 10)
        boxCut.Add(gridFlex2, 0, wx.ALL | wx.ALIGN_CENTER, 5)
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
        self.paneltime.Bind(wx.EVT_PAINT, self.OnPaint)
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

    def barval(self):
        """
        """
        hw = int(self.stop_hour_ctrl.GetValue()) * self.hours
        mw = int(self.stop_minute_ctrl.GetValue()) * self.minutes
        sw = int(self.stop_second_ctrl.GetValue()) * self.seconds

        hx = int(self.start_hour_ctrl.GetValue()) * self.hours
        mx = int(self.start_minute_ctrl.GetValue()) * self.minutes
        sx = int(self.start_second_ctrl.GetValue()) * self.seconds

        self.bar_w = hw+mw+sw
        self.bar_x = hx+mx+sx

        self.onRedraw(self)
    # ------------------------------------------------------------------#

    def OnPaint(self, event):
        """
        """
        dc = wx.PaintDC(self.paneltime)  ## draw window boundary
        dc.Clear()
        self.barval()
    # ------------------------------------------------------------------#

    def onRedraw(self, event):
        """
        Update Drawing: A transparent background rectangle in a bitmap
        for selections

        """
        dc = wx.ClientDC(self.paneltime)
        dc.Clear()
        dc.SetPen(wx.Pen('#ea3535', 1, wx.PENSTYLE_SOLID))
        r, g, b = (92, 21, 21)
        dc.SetBrush(wx.Brush(wx.Colour(r, g, b, 240)))
        dc.DrawRectangle(self.bar_x, -8,
                         self.bar_w, 66)

        #dc.SetFont(self.font)
        dc.SetPen(wx.Pen('#F8FF25'))
        dc.SetTextForeground('#F8FF25')

        for i in range(Timeline.RW):

            if not (i % 600):

                dc.DrawLine(i+Timeline.RM, 0, i+Timeline.RM, 10)
                w, h = dc.GetTextExtent(str(i))
                dc.DrawText('%02d:00:00' % i, i+Timeline.RM+3-w/2, 11)

            elif not (i % 300):

                dc.DrawLine(i+Timeline.RM, 0, i+Timeline.RM, 10)

            elif not (i % 75):

                dc.DrawLine(i+Timeline.RM, 0, i+Timeline.RM, 5)

        dc.DrawLine(i, 0, i, 10)
        w, h = dc.GetTextExtent(self.timeHum)
        dc.DrawText(self.timeHum, i+1-w, 11)
    # ------------------------------------------------------------------#

    def start_hour(self, event):
        self.init_hour = '%02d' % int(self.start_hour_ctrl.GetValue())
        self.barval()
        #self.onRedraw(self)
    # ------------------------------------------------------------------#

    def start_minute(self, event):
        self.init_minute = '%02d' % int(self.start_minute_ctrl.GetValue())
        self.barval()
        #self.onRedraw(self)
    # ------------------------------------------------------------------#

    def start_second(self, event):
        self.init_seconds = '%02d' % int(self.start_second_ctrl.GetValue())
        self.barval()
        #self.onRedraw(self)
    # ------------------------------------------------------------------#

    def stop_hour(self, event):
        self.cut_hour = '%02d' % int(self.stop_hour_ctrl.GetValue())
        self.barval()
        #self.onRedraw(self)
    # ------------------------------------------------------------------#

    def stop_minute(self, event):

        self.cut_minute = '%02d' % int(self.stop_minute_ctrl.GetValue())
        self.barval()
        #self.onRedraw(self)
    # ------------------------------------------------------------------#

    def stop_second(self, event):

        self.cut_seconds = '%02d' % int(self.stop_second_ctrl.GetValue())
        self.barval()
        #self.onRedraw(self)
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
        self.bar_w, self.bar_x = 0, 0
        self.barval()
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
                wx.MessageBox(_("Length of cut missing"), "Videomass",
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
