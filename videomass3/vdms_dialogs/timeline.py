# -*- coding: UTF-8 -*-
# Name: time_selection.py
# Porpose: show dialog to set duration and time sequences
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Dec.14.2020 *PEP8 compatible*
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
from videomass3.vdms_utils.utils import time_seconds
# import wx.lib.masked as masked # not work on macOSX


class Timeline(wx.Dialog):
    """
    This class show dialog box to set a time range selection and
    get data in the FFmpeg syntax using this form :

        `-ss 00:00:00.000 -t 00:00:00.000`

    The -ss flag indicates the start selection; the -t flag
    indicates the  time amount (duration) starting from -ss.
    See FFmpeg documentation for details:

        <https://ffmpeg.org/documentation.html>

    or wiki page: <https://trac.ffmpeg.org/wiki/Seeking#Timeunitsyntax>

    """
    get = wx.GetApp()
    OS = get.OS

    BACKGROUND = '#294083'  # dark azure for panel bkgrd
    SELECTION = '#4368d3'  # medium azure foe selection
    WHITE = '#ffffff'  # white for text and draw lines
    GREEN = '#00fe00'  # for margin selection

    RW = 600  # ruler width
    RM = 0  # ruler margin
    PW = 600  # panel width
    PH = 35  # panel height

    def __init__(self, parent, curset, duration):
        """
        If no file has a duration, the limit to the maximum time
        selection is set (86399999 ms = 23:59:59.999), to allow for
        example slideshows with images.

        self.px: scale pixels to time seconds for ruler selection
        self.timeHum: from seconds to time format (00:00:00)
        self.bar_w: width value for time bar selection
        self.bar_x: x axis value for time bar selection

        """
        if not duration:
            msg0 = _('The maximum time selection is set to 24:00:00, to '
                     'allow make the slideshows')
            self.duration = 86399999
        else:
            msg0 = _('The maximum time refers to the file with the longest '
                     'duration')
            self.duration = round(duration)
            # rounds all float number to prevent ruler selection inaccuracy

        self.px = Timeline.RW / self.duration
        self.timeHum = time_human(self.duration)
        self.bar_w = 0
        self.bar_x = 0

        if curset == '':
            start_time = '00:00:00.000'
            end_time = '00:00:00.000'

        else:  # return a previus settings:
            start_time = curset.split()[1]
            end_time = curset.split()[3]

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        """constructor """

        self.font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch'
                            )

        sizer_base = wx.BoxSizer(wx.VERTICAL)

        box_displ = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, _(
                                'Time selection display')), wx.VERTICAL)
        sizer_base.Add(box_displ, 0, wx.ALL | wx.CENTRE, 10)
        self.paneltime = wx.Panel(self, wx.ID_ANY,
                                  size=(Timeline.PW, Timeline.PH)
                                  )
        box_displ.Add(self.paneltime, 0, wx.ALL | wx.CENTRE, 10)

        label0 = wx.StaticText(self, wx.ID_ANY, msg0)
        box_displ.Add(label0, 0, wx.BOTTOM | wx.CENTRE, 5)
        self.sldseek = wx.Slider(self, wx.ID_ANY, 0, 0, self.duration,
                                 size=(300, -1), style=wx.SL_HORIZONTAL
                                 )
        self.sldseek.Disable()
        self.txtseek = wx.StaticText(self, wx.ID_ANY, start_time)

        self.sldcut = wx.Slider(self, wx.ID_ANY, 0, 0, self.duration,
                                size=(300, -1), style=wx.SL_HORIZONTAL
                                )
        self.txtcut = wx.StaticText(self, wx.ID_ANY, end_time)

        btn_help = wx.Button(self, wx.ID_HELP, "", size=(-1, -1))
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        btn_ok = wx.Button(self, wx.ID_OK, _("Apply"))
        btn_reset = wx.Button(self, wx.ID_CLEAR, _("Reset"))

        # ----------------------Properties ----------------------#
        self.SetTitle(_('Timeline'))
        self.paneltime.SetBackgroundColour(wx.Colour(Timeline.BACKGROUND))
        self.sldseek.SetToolTip(_("Seek to given time position"))
        self.sldcut.SetToolTip(_("Total amount duration"))

        if Timeline.OS == 'Darwin':
            label0.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            label0.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        # ----------------------Layout----------------------#

        gridtime = wx.FlexGridSizer(2, 2, 0, 0)
        sizer_base.Add(gridtime, 0, wx.CENTRE | wx.ALL, 0)
        gridtime.Add(self.sldseek, 0, wx.ALL | wx.CENTRE, 0)
        gridtime.Add(self.sldcut, 0, wx.ALL | wx.CENTRE, 0)
        gridtime.Add(self.txtseek, 0, wx.ALL, 0)
        gridtime.Add(self.txtcut, 0, wx.ALL, 0)

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
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.resetValues, btn_reset)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.on_Cut, self.sldcut)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.on_Seek, self.sldseek)

        if end_time != '00:00:00.000':
            self.sldseek.SetValue(time_seconds(start_time))
            self.sldcut.SetValue(time_seconds(end_time))
            self.on_Cut(self)
            self.on_Seek(self)

    # ----------------------Event handler (callback)----------------------#

    def on_Cut(self, event):
        """
        Get total duration event

        """
        cut = self.sldcut.GetValue()
        if cut == 0:
            self.sldcut.SetValue(0), self.sldseek.Disable()
            self.sldcut.SetMax(self.duration)
        else:
            self.sldseek.Enable()

        self.sldseek.SetMax(self.duration - cut)  # seek offset
        time = time_human(cut)
        self.txtcut.SetLabel(time)
        self.set_coordinates()

    def on_Seek(self, event):
        """
        Get seek event
        """
        seek = self.sldseek.GetValue()
        if seek == 0:
            self.sldcut.SetMin(0)
        else:
            self.sldcut.SetMin(1)  # constrains to 1

        self.sldcut.SetMax(self.duration - seek)  # cut offset
        time = time_human(seek)  # convert to time format
        self.txtseek.SetLabel(time)  # update StaticText
        self.set_coordinates()

    def set_coordinates(self):
        """
        Define width and x axis for selection rectangle before
        call onRedraw
        """
        self.bar_w = self.sldcut.GetValue() * self.px
        self.bar_x = self.sldseek.GetValue() * self.px

        self.onRedraw(self)
    # ------------------------------------------------------------------#

    def OnPaint(self, event):
        """
        wx.PaintDC event
        """
        dc = wx.PaintDC(self.paneltime)  # draw window boundary
        dc.Clear()
        self.onRedraw(self)
    # ------------------------------------------------------------------#

    def onRedraw(self, event):
        """
        Draw a ruler and update the selection rectangle
        (a semi-transparent background rectangle upon a ruler)

        """
        dc = wx.ClientDC(self.paneltime)
        dc.Clear()
        dc.SetPen(wx.Pen(Timeline.GREEN, 2, wx.PENSTYLE_SOLID))
        # dc.SetBrush(wx.Brush(wx.Colour(30, 30, 30, 200)))
        dc.SetBrush(wx.Brush(Timeline.SELECTION, wx.BRUSHSTYLE_SOLID))
        dc.DrawRectangle(self.bar_x + 1, -8, self.bar_w, 66)
        dc.SetFont(self.font)
        dc.SetPen(wx.Pen(Timeline.WHITE))
        dc.SetTextForeground(Timeline.WHITE)

        for i in range(Timeline.RW):

            if not (i % 600):
                dc.DrawLine(i+Timeline.RM, 0, i+Timeline.RM, 12)
                w, h = dc.GetTextExtent(str(i))
                dc.DrawText('%02d:00:00.000' % i, i+Timeline.RM+3-w/2, 14)

            elif not (i % 300):
                dc.DrawLine(i+Timeline.RM, 0, i+Timeline.RM, 12)  # metà

            elif not (i % 150):
                dc.DrawLine(i+Timeline.RM, 0, i+Timeline.RM, 12)  # ogni 5

            elif not (i % 25):
                dc.DrawLine(i+Timeline.RM, 0, i+Timeline.RM, 5)

        dc.DrawLine(i, 0, i, 12)
        w, h = dc.GetTextExtent(self.timeHum)
        dc.DrawText(self.timeHum, i+1-w, 14)
    # ------------------------------------------------------------------#

    def resetValues(self, event):
        """
        Reset all values to default .
        WARNING: It is recommended that you follow the order below
        for success

        """
        self.sldseek.SetValue(0), self.on_Seek(self)
        self.sldcut.SetValue(0), self.on_Cut(self)
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
        self.GetValue()
        # self.Destroy()
        event.Skip()
    # ------------------------------------------------------------------#

    def GetValue(self):
        """
        This method return values via the GetValue() interface

        """
        cut_range = "-ss %s -t %s" % (self.txtseek.GetLabel(),
                                      self.txtcut.GetLabel()
                                      )
        return cut_range
