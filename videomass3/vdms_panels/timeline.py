# -*- coding: UTF-8 -*-
# Name: time_selection.py
# Porpose: show panel to set duration and time sequences
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Dec.21.2020 *PEP8 compatible*
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
from videomass3.vdms_utils.utils import milliseconds2timeformat
# import wx.lib.masked as masked # not work on macOSX


class Timeline(wx.Panel):
    """
    This class show a panel box to set a time range selection and
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

    # Theme Colors used in HTML
    if get.THEME in ('Breeze-Blues', 'Videomass-Colours'):  # all themes
        RULER_BKGRD = '#294083'  # dark blue for panel bkgrd
        SELECTION = '#4368d3'  # medium azure for selection
        DELIMITER_COLOR = '#da4453'  # red for margin selection
        TEXT_PEN_COLOR = '#00cc57'  # green for text and draw lines

    elif get.THEME in ('Breeze-Blues', 'Breeze-Dark', 'Videomass-Dark'):
        RULER_BKGRD = '#294083'  # dark blue for panel bkgrd
        SELECTION = '#4368d3'  # medium azure for selection
        DELIMITER_COLOR = '#00FE00'  # green for margin selection
        TEXT_PEN_COLOR = '#ffffff'  # white for text and draw lines

    else:  # white theme
        RULER_BKGRD = '#84D2C9'  # light blue for panelruler background
        SELECTION = '#31BAA7'  # CYAN
        DELIMITER_COLOR = '#00FE00'  # green for margin selection
        TEXT_PEN_COLOR = '#020D0F'  # black for text and draw lines

    # ruler and panel specifications
    RW = 450  # ruler width
    RM = 0  # ruler margin
    PW = 452  # panel width
    PH = 35  # panel height

    def __init__(self, parent):
        """
        If no file has a duration, the limit to the maximum time
        selection is set (86399999 ms = 23:59:59.999), to allow for
        example slideshows with images.

        self.px: scale pixels to time seconds for ruler selection
        self.milliseconds: int(milliseconds)
        self.timeformat: time format with ms (00:00:00.000)
        self.bar_w: width value for time bar selection
        self.bar_x: x axis value for time bar selection

        """
        self.parent = parent
        self.milliseconds = 1  # max val must be greater than the min val
        self.timeformat = None
        self.px = 0
        self.bar_w = 0
        self.bar_x = 0

        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)
        """constructor """
        '''
        self.font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch'
                            )
        '''
        self.font = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        sizer_base = wx.BoxSizer(wx.HORIZONTAL)

        self.paneltime = wx.Panel(self, wx.ID_ANY,
                                  size=(Timeline.PW, Timeline.PH),
                                  style=wx.BORDER_SUNKEN)
        sizer_base.Add(self.paneltime, 0, wx.LEFT | wx.RIGHT | wx.CENTRE, 5)
        self.sldseek = wx.Slider(self, wx.ID_ANY, 0, 0, self.milliseconds,
                                 size=(200, -1), style=wx.SL_HORIZONTAL
                                 )
        self.sldseek.Disable()
        self.txtseek = wx.StaticText(self, wx.ID_ANY, '00:00:00.000')
        txtstaticseek = wx.StaticText(self, wx.ID_ANY, _('Seek'))

        self.sldcut = wx.Slider(self, wx.ID_ANY, 0, 0, self.milliseconds,
                                size=(200, -1), style=wx.SL_HORIZONTAL
                                )
        self.txtcut = wx.StaticText(self, wx.ID_ANY, '00:00:00.000')
        txtstaticdur = wx.StaticText(self, wx.ID_ANY, _('Duration'))

        # ----------------------Properties ----------------------#
        self.paneltime.SetBackgroundColour(wx.Colour(Timeline.RULER_BKGRD))
        self.sldseek.SetToolTip(_("Seek to given time position"))
        self.sldcut.SetToolTip(_("Total duration"))

        # ----------------------Layout----------------------#

        gridtime = wx.FlexGridSizer(2, 3, 0, 5)
        gridtime.Add(txtstaticseek, 0, wx.LEFT | wx.RIGHT |
                     wx.ALIGN_CENTRE_VERTICAL, 5)
        gridtime.Add(self.sldseek, 0, wx.ALL | wx.CENTRE, 0)
        gridtime.Add(self.txtseek, 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 0)
        gridtime.Add(txtstaticdur, 0, wx.LEFT | wx.RIGHT |
                     wx.ALIGN_CENTRE_VERTICAL, 5)
        gridtime.Add(self.sldcut, 0, wx.ALL | wx.CENTRE, 0)
        gridtime.Add(self.txtcut, 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer_base.Add(gridtime, 0, wx.ALL | wx.CENTRE, 0)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # ----------------------Binding (EVT)----------------------#
        self.paneltime.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.on_Cut, self.sldcut)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.on_Seek, self.sldseek)

    # ----------------------Event handler (callback)----------------------#

    def on_Cut(self, event):
        """
        Get total duration event

        """
        cut = self.sldcut.GetValue()
        if cut == 0:
            self.sldcut.SetValue(0), self.sldseek.Disable()
            self.sldcut.SetMax(self.milliseconds)
        else:
            self.sldseek.Enable()

        self.sldseek.SetMax(self.milliseconds - cut)  # seek offset
        time = milliseconds2timeformat(cut)
        self.parent.time_seq = "-ss %s -t %s" % (self.txtseek.GetLabel(), time)
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

        self.sldcut.SetMax(self.milliseconds - seek)  # cut offset
        time = milliseconds2timeformat(seek)  # convert to time format
        self.parent.time_seq = "-ss %s -t %s" % (time, self.txtcut.GetLabel())
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
        dc.SetPen(wx.Pen(Timeline.DELIMITER_COLOR, 2, wx.PENSTYLE_SOLID))
        # dc.SetBrush(wx.Brush(wx.Colour(30, 30, 30, 200)))
        dc.SetBrush(wx.Brush(Timeline.SELECTION, wx.BRUSHSTYLE_SOLID))
        dc.DrawRectangle(self.bar_x + 1, -8, self.bar_w, 66)
        dc.SetFont(self.font)
        dc.SetPen(wx.Pen(Timeline.TEXT_PEN_COLOR))
        dc.SetTextForeground(Timeline.TEXT_PEN_COLOR)

        for i in range(Timeline.RW):

            if not (i % 600):
                dc.DrawLine(i+Timeline.RM, 0, i+Timeline.RM, 12)
                w, h = dc.GetTextExtent(str(i))
                dc.DrawText('%02d:00:00.000' % i, i+Timeline.RM+5-w/2, 14)

            elif not (i % 300):
                dc.DrawLine(i+Timeline.RM, 0, i+Timeline.RM, 12)  # metà

            elif not (i % 150):
                dc.DrawLine(i+Timeline.RM, 0, i+Timeline.RM, 12)  # ogni 5

            elif not (i % 25):
                dc.DrawLine(i+Timeline.RM, 0, i+Timeline.RM, 5)

        dc.DrawLine(i, 0, i, 12)
        w, h = dc.GetTextExtent(self.timeformat)
        dc.DrawText(self.timeformat, i-Timeline.RM-3-w, 14)
    # ------------------------------------------------------------------#

    def resetValues(self):
        """
        Reset all values to default. This method is called out side
        of this class.
        WARNING: It is recommended that you follow the order below
        for success

        """
        self.sldseek.SetValue(0), self.on_Seek(self)
        self.sldcut.SetValue(0), self.on_Cut(self)
    # ------------------------------------------------------------------#

    def set_values(self, duration):
        """
        Set new values with new entries. This method is called out side
        of this class.
        """
        if not duration:
            msg0 = _('The maximum time selection is set to 24:00:00, '
                     'allowing to make a slideshow')
            self.milliseconds = 86399999
        else:
            msg0 = _('The maximum time refers to the file with the longest '
                     'duration')
            self.milliseconds = round(duration)
            # rounds all float number to prevent ruler selection inaccuracy
        self.paneltime.SetToolTip(msg0)
        self.px = Timeline.RW / self.milliseconds
        self.timeformat = milliseconds2timeformat(self.milliseconds)
        self.sldseek.SetMax(self.milliseconds)
        self.sldcut.SetMax(self.milliseconds)
