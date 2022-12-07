# -*- coding: UTF-8 -*-
"""
Name: timeline.py
Porpose: show panel to set duration and time sequences
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Dec.04.2022
Code checker:
    flake8: --ignore F821, W504
    pylint: --ignore E0602, E1101

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
import sys
import wx
from videomass.vdms_utils.utils import milliseconds2clock
from videomass.vdms_utils.get_bmpfromsvg import get_bmp
from videomass.vdms_dialogs.time_selector import Time_Selector


class Timeline(wx.Panel):
    """
    A representation of the time selection meter as duration
    and position values viewed as time range selection
    for the FFmpeg syntax, in the following form:

        `-ss 00:00:00.000 -t 00:00:00.000`

    The -ss flag means the start selection (SEEK); the -t flag
    means the time amount (DURATION) starting from -ss.
    See FFmpeg documentation for details:

        <https://ffmpeg.org/documentation.html>
        <https://trac.ffmpeg.org/wiki/Seeking#Timeunitsyntax>

    """
    # Colours used here
    RULER_BKGRD = '#84D2C9'  # CYAN for ruler background
    SELECTION = '#a3e6dd' # LIGHT CYAN for ruller background selection
    DELIMITER_COLOR = '#ffdf00' #'#fe004c' # red for margin selection
    TEXT_PEN_COLOR = '#020D0F'  # black for static text and draw lines
    # ORANGE = '#f56b38'  # Orange color
    DURATION_START = '#1f5dda'  # Light blue for duration/start indicators

    # ruler and panel specifications
    RW = 600  # ruler width
    RM = 0  # ruler margin
    PW = 602  # panel width
    PH = 45  # panel height

    def __init__(self, parent, iconedit, iconreset):
        """
        Note, the time values results are setted on `on_time_selection`
        method using the `time_seq` parent (main_frame) attribute.
        If no file has a duration, the limit to the maximum time
        selection is set to 4800000ms (01:20:00.000).

        self.pix: scale pixels to time seconds for ruler selection
        self.milliseconds: int(milliseconds)
        self.timeformat: time format with ms (00:00:00.000)
        self.bar_w: width value for time bar selection
        self.bar_x: x axis value for time bar selection

        """
        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up
            bmpedit = get_bmp(iconedit, ((16, 16)))
            bmpreset = get_bmp(iconreset, ((16, 16)))
        else:
            bmpedit = wx.Bitmap(iconedit, wx.BITMAP_TYPE_ANY)
            bmpreset = wx.Bitmap(iconreset, wx.BITMAP_TYPE_ANY)

        self.parent = parent
        self.milliseconds = 1  # total duration in ms
        self.timeformat = None  # total duration of media  (HH:MM:SS.MLS)
        self.ms_start = 0  # seek position in milliseconds
        self.ms_dur = 0  # duration of the selection in milliseconds
        self.time_start = '00:00:00.000'  # seek position
        self.time_dur = '00:00:00.000'  # duration of the selection
        self.pix = 0
        self.bar_w = 0
        self.bar_x = 0

        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)

        # self.font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
        #                     wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch'
        #                     )
        self.font_med = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        sizer_base = wx.BoxSizer(wx.HORIZONTAL)
        btn_edit = wx.Button(self, wx.ID_ANY, _("Set"), size=(-1, -1))
        btn_edit.SetBitmap(bmpedit, wx.BU_LEFT)
        sizer_base.Add(btn_edit, 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 5)
        self.btn_reset = wx.Button(self, wx.ID_ANY, _("Reset"), size=(-1, -1))
        self.btn_reset.SetBitmap(bmpreset, wx.BU_LEFT)
        sizer_base.Add(self.btn_reset, 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 5)
        self.paneltime = wx.Panel(self, wx.ID_ANY,
                                  size=(Timeline.PW, Timeline.PH),
                                  style=wx.BORDER_SUNKEN)
        sizer_base.Add(self.paneltime, 0, wx.LEFT | wx.RIGHT | wx.CENTRE, 5)
        self.maxdur = wx.StaticText(self, wx.ID_ANY, '')
        sizer_base.Add(self.maxdur, 0, wx.LEFT | wx.RIGHT |
                       wx.ALIGN_CENTRE_VERTICAL, 5)

        # ----------------------Properties ----------------------#
        self.paneltime.SetBackgroundColour(wx.Colour(Timeline.RULER_BKGRD))

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # ----------------------Binding (EVT)----------------------#
        self.paneltime.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_BUTTON, self.on_time_selection, btn_edit)
        self.Bind(wx.EVT_BUTTON, self.on_reset_values, self.btn_reset)

    # ----------------------Event handler (callback)----------------------#

    def set_coordinates(self):
        """
        Define width and x axis for selection rectangle before
        call `onRedraw` method
        """
        self.bar_w = self.ms_dur * self.pix
        self.bar_x = self.ms_start * self.pix

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
        dc.SetPen(wx.Pen(Timeline.TEXT_PEN_COLOR))
        dc.SetTextForeground(Timeline.TEXT_PEN_COLOR)

        for i in range(Timeline.RW):

            if not i % 600:
                dc.DrawLine(i+Timeline.RM, 0, i+Timeline.RM, 10)

            elif not i % 300:
                dc.DrawLine(i+Timeline.RM, 0, i+Timeline.RM, 10)  # metà

            elif not i % 150:
                dc.DrawLine(i+Timeline.RM, 0, i+Timeline.RM, 10)  # ogni 5

            elif not i % 25:
                dc.DrawLine(i+Timeline.RM, 0, i+Timeline.RM, 5)

        dc.DrawLine(i, 0, i, 10)

        dc.SetFont(self.font_med)
        txt_s = _('Start')
        txt_d = _('Duration')
        # Make start txt
        txt1 = f'{txt_s}  {self.time_start}'
        dc.SetTextForeground(Timeline.DURATION_START)
        w = dc.GetTextExtent(txt1)[0]
        if w > self.bar_x:
            dc.DrawText(txt1, self.bar_x, 9)
        elif w > self.bar_x - Timeline.RW:
            dc.DrawText(txt1, self.bar_x - w, 9)
        else:
            dc.DrawText(txt1, self.bar_x, 9)
        # Make duration txt
        txt2 = f'{txt_d}  {self.time_dur}'
        w = dc.GetTextExtent(txt2)[0]
        if w > Timeline.RW - (self.bar_x + self.bar_w):
            dc.DrawText(txt2, (self.bar_x + self.bar_w) - w, 29)
        elif w > self.bar_w:
            dc.DrawText(txt2, self.bar_x + self.bar_w, 29)
        else:
            dc.DrawText(txt2, (self.bar_x + self.bar_w) - w, 29)
    # ------------------------------------------------------------------#

    def on_reset_values(self, event):
        """
        Reset all values to default. This method is also called on
        MainFrame.
        WARNING: It is recommended that you follow the order below
        for success

        """
        self.time_start = '00:00:00.000'  # seek position
        self.time_dur = '00:00:00.000'  # duration of the selection
        self.ms_dur = 0
        self.ms_start = 0
        self.btn_reset.Disable()
        self.set_coordinates()
    # ------------------------------------------------------------------#

    def set_values(self, duration):
        """
        Set new values each time new files are loaded.
        This method is called out side of this class, see parent.
        """
        if not duration:
            self.milliseconds = 86399999
        else:
            self.milliseconds = round(duration)
            # rounds all float number to prevent ruler selection inaccuracy

        msg0 = _('"Total Duration" refers to the file '
                 'with the longest duration, it will be '
                 'set to {0} otherwise.').format('23:59:59.999')
        self.paneltime.SetToolTip(msg0)
        self.pix = Timeline.RW / self.milliseconds
        self.timeformat = milliseconds2clock(self.milliseconds)
        self.maxdur.SetLabel(_('Total Duration:\n{}').format(self.timeformat))
        self.btn_reset.Disable()
    # ------------------------------------------------------------------#

    def on_time_selection(self, event):
        """
        Show a dialog as alternative tool to adjust the time selection.
        """
        with Time_Selector(self,
                           self.time_start,
                           self.time_dur,
                           self.milliseconds,
                           ) as tms:
            if tms.ShowModal() == wx.ID_OK:
                data = tms.getvalue()
                if not data[0] and not data[1]:
                    self.on_reset_values(self)
                elif data[1]:
                    self.ms_dur = data[1]
                    self.ms_start = data[0]
                    self.time_start = milliseconds2clock(self.ms_start)
                    self.time_dur = milliseconds2clock(self.ms_dur)
                    self.parent.time_seq = (f"-ss {self.time_start} "
                                            f"-t {self.time_dur}")
                    self.btn_reset.Enable()
                    self.set_coordinates()
