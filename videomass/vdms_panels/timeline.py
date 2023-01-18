# -*- coding: UTF-8 -*-
"""
Name: timeline.py
Porpose: show panel to set duration and time sequences
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Gen.03.2022
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
import sys
import wx
import wx.adv
from videomass.vdms_dialogs.widget_utils import NormalTransientPopup
from videomass.vdms_utils.utils import milliseconds2clock
from videomass.vdms_utils.utils import get_milliseconds
from videomass.vdms_utils.get_bmpfromsvg import get_bmp


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
    VIOLET = '#D64E93'
    LGREEN = '#52ee7d'
    BLACK = '#1f1f1f'

    def __init__(self, parent, iconreset):
        """
        The time values results are setted on the `time_seq`
        parent (main_frame) attribute.
        If no file has a duration, the limit to the maximum time
        selection is set to 86399999ms (23:59:59.999).

        Used attributes:
        self.milliseconds: total duration of media in ms
        self.hour24format: total duration of media in 24h (HH:MM:SS.ms)
        self.ms_start: seek position in milliseconds
        self.ms_end: duration of the selection in milliseconds
        self.time_start: seek position in 24-hour format
        self.time_end: duration of the selection in 24-hour format

        """
        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up
            bmpreset = get_bmp(iconreset, ((16, 16)))
        else:
            bmpreset = wx.Bitmap(iconreset, wx.BITMAP_TYPE_ANY)

        self.parent = parent
        self.milliseconds = 1
        self.hour24format = None
        self.ms_start = 0
        self.ms_end = 0
        self.time_start = '00:00:00.000'
        self.time_end = '00:00:00.000'
        get = wx.GetApp()
        appdata = get.appset

        wx.Panel.__init__(self, parent, -1)
        sizer_v = wx.BoxSizer(wx.VERTICAL)
        sizer_v.Add(10, 10)
        sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        sizer_v.Add(sizer_h, 0, wx.ALL | wx.CENTRE, 5)
        lbl_trim = wx.StaticText(self, wx.ID_ANY, label=_('Trim'))
        if appdata['ostype'] == 'Darwin':
            lbl_trim.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        else:
            lbl_trim.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizer_h.Add(lbl_trim, 0, wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 5)
        sizer_h.Add(20, 20)
        self.btn_reset = wx.Button(self, wx.ID_ANY, _("Reset"), size=(-1, -1))
        self.btn_reset.SetBitmap(bmpreset, wx.LEFT)
        sizer_h.Add(self.btn_reset, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        lbl_start = wx.StaticText(self, wx.ID_ANY, label=_('Start:'))
        sizer_h.Add(lbl_start, 0, wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 20)
        self.ctrl_start = wx.adv.TimePickerCtrl(self,
                                                size=(170, -1),
                                                style=wx.adv.TP_DEFAULT,
                                                )
        self.ctrl_start.SetTime(00, 00, 00)
        sizer_h.Add(self.ctrl_start, 0, wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 5)
        self.ctrl_start.Disable()
        lbl_duration = wx.StaticText(self, wx.ID_ANY, label=_('End:'))
        sizer_h.Add(lbl_duration, 0, wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 20)
        self.ctrl_end = wx.adv.TimePickerCtrl(self,
                                              size=(170, -1),
                                              style=wx.adv.TP_DEFAULT,
                                              )
        self.ctrl_end.SetTime(00, 00, 00)
        sizer_h.Add(self.ctrl_end, 0, wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 5)
        self.btn_maxdur = wx.Button(self, wx.ID_ANY,
                                    "00:00:00",
                                    size=(-1, -1),
                                    )
        self.btn_maxdur.SetBackgroundColour(wx.Colour(Timeline.LGREEN))
        self.btn_maxdur.SetForegroundColour(wx.Colour(Timeline.BLACK))
        sizer_h.Add(self.btn_maxdur, 0, wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 20)
        # ----------------------Properties ----------------------#
        self.SetSizer(sizer_v)
        sizer_v.Fit(self)
        self.Layout()

        self.btn_maxdur.SetToolTip(_("Stream duration. Click me for details."))
        self.ctrl_end.SetToolTip(_("End segment in 24-hour format (HH:MM:SS)"))
        self.ctrl_start.SetToolTip(_("Start segment in "
                                     "24-hour format (HH:MM:SS)"))

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_help, self.btn_maxdur)
        self.Bind(wx.adv.EVT_TIME_CHANGED, self.on_start, self.ctrl_start)
        self.Bind(wx.adv.EVT_TIME_CHANGED, self.on_end, self.ctrl_end)
        self.Bind(wx.EVT_BUTTON, self.on_reset_values, self.btn_reset)

    # ----------------------Event handler (callback)----------------------#

    def time_join(self, seq):
        """
        Translates a sequence of integer time values
        (Hours, Minutes, Seconds) into a convenient 24-hour
        string ('00:00:00.000') format with milliseconds.
        """
        h, m, s = seq
        return ':'.join((str(h).zfill(2),
                         str(m).zfill(2),
                         str(s).zfill(2) + '.000',
                         ))
    # ------------------------------------------------------------------#

    def on_start(self, event):
        """
        Set trim for start time
        """
        timef = self.time_join(self.ctrl_start.GetTime())
        timems = get_milliseconds(timef)

        if timems >= self.ms_end:
            start = milliseconds2clock(self.ms_end - 1000)
            h, m, s = start.split(':')
            self.ctrl_start.SetTime(int(h), int(m), int(s.split('.')[0]))
            timef = self.time_join(self.ctrl_start.GetTime())
            timems = self.ms_end - 1000

        self.time_start = timef
        self.ms_start = timems
        duration = milliseconds2clock(self.ms_end - self.ms_start)
        self.parent.time_seq = f"-ss {self.time_start} -t {duration}"
    # ------------------------------------------------------------------#

    def on_end(self, event):
        """
        Set trim for end time
        """
        timef = self.time_join(self.ctrl_end.GetTime())
        timems = get_milliseconds(timef)
        if timems == 0:
            self.ctrl_start.Disable()
        else:
            if not self.ctrl_start.IsEnabled():
                self.ctrl_start.Enable()

        if timems <= self.ms_start:
            if self.ms_start == 0:
                self.ctrl_end.SetTime(00, 00, 00)
                self.ctrl_start.Disable()
            else:
                end = milliseconds2clock(self.ms_start + 1000)
                h, m, s = end.split(':')
                self.ctrl_end.SetTime(int(h), int(m), int(s.split('.')[0]))
            timef = self.time_join(self.ctrl_end.GetTime())
            timems = get_milliseconds(timef)

        elif timems >= self.milliseconds:
            h, m, s = self.hour24format.split(':')
            self.ctrl_end.SetTime(int(h), int(m), int(s.split('.')[0]))
            timef = self.time_join(self.ctrl_end.GetTime())
            timems = get_milliseconds(timef)

        self.time_end = timef
        self.ms_end = timems
        duration = milliseconds2clock(self.ms_end - self.ms_start)
        self.parent.time_seq = f"-ss {self.time_start} -t {duration}"
    # ------------------------------------------------------------------#

    def on_help(self, event):
        """
        event on maxdur button
        """
        msg = _('Stream duration always refers to the file with '
                'the longest duration.\nIf the "Duration" data is missing, '
                'it will be set to {0}.').format('23:59:59')

        win = NormalTransientPopup(self,
                                   wx.SIMPLE_BORDER,
                                   msg,
                                   Timeline.LGREEN,
                                   Timeline.BLACK)

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = event.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Popup()
    # ------------------------------------------------------------------#

    def on_reset_values(self, event):
        """
        Reset all values to default. This method is
        also called on MainFrame.
        """
        self.time_start = '00:00:00.000'  # seek position
        self.time_end = '00:00:00.000'  # duration of the selection
        self.parent.time_seq = f"-ss {self.time_start} -t {self.time_end}"
        self.ms_end = 0
        self.ms_start = 0
        self.ctrl_start.SetTime(00, 00, 00)
        self.ctrl_end.SetTime(00, 00, 00)
        self.ctrl_start.Disable()
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

        self.hour24format = milliseconds2clock(self.milliseconds)
        self.btn_maxdur.SetLabel(self.hour24format.split('.')[0])
