# -*- coding: UTF-8 -*-
"""
FileName: libaom.py
Porpose: Contains AV1 functionality for A/V Conversions
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.04.2023
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
import wx.lib.scrolledpanel as scrolled


class AV1Pan(scrolled.ScrolledPanel):
    """
    This scroll panel implements controls for extra options
    of the `av1-libaom` encoder.
    """
    def __init__(self, parent, opt, osplat):
        """
        This is a child of `AV_Conv` class-panel (parent) and the `opt`
        attribute is a dict owned by that class.
        """
        self.parent = parent
        self.opt = opt
        scrolled.ScrolledPanel.__init__(self, parent, -1,
                                        size=(300, 700),
                                        style=wx.TAB_TRAVERSAL
                                        | wx.BORDER_NONE,
                                        name="AV1 scrollpanel",
                                        )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((10, 10), 0)
        infomsg = "AV1 - libaom-av1"
        lbl_info = wx.StaticText(self, wx.ID_ANY, label=infomsg)
        sizer.Add(lbl_info, 0, wx.ALL | wx.CENTER, 5)
        if osplat == 'Darwin':
            lbl_info.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        else:
            lbl_info.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizer.Add((10, 10), 0)
        self.rdb_usage = wx.RadioBox(self, wx.ID_ANY,
                                     (_("Quality and Compression")),
                                     choices=[("good"), ("realtime"),
                                              ],
                                     majorDimension=0,
                                     style=wx.RA_SPECIFY_ROWS,
                                     )
        sizer.Add(self.rdb_usage, 0, wx.TOP | wx.CENTRE, 5)
        lab_cpu = wx.StaticText(self, wx.ID_ANY, (_("Quality and Speed:")))
        sizer.Add(lab_cpu, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.spin_cpu = wx.SpinCtrl(self, wx.ID_ANY,
                                    "1", min=0,
                                    max=8, size=(-1, -1),
                                    style=wx.TE_PROCESS_ENTER,
                                    )
        sizer.Add(self.spin_cpu, 0, wx.TOP | wx.CENTRE, 5)

        lab_gop = wx.StaticText(self, wx.ID_ANY, ("Group of picture (GOP):"))
        sizer.Add(lab_gop, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.spin_gop = wx.SpinCtrl(self, wx.ID_ANY,
                                    "250", min=-1,
                                    max=1000, size=(-1, -1),
                                    style=wx.TE_PROCESS_ENTER,
                                    )
        sizer.Add(self.spin_gop, 0, wx.TOP | wx.CENTRE, 5)

        self.SetSizer(sizer)  # set panel
        self.SetAutoLayout(1)
        self.SetupScrolling()

        tip = (_('"good" is the default and recommended for most '
                 'applications; "realtime" is recommended for live/fast '
                 'encoding (live streaming, video conferencing, etc)'))
        self.rdb_usage.SetToolTip(tip)
        tip = (_('"cpu-used" sets how efficient the compression will be. '
                 'Default is 1. Lower values mean slower encoding with '
                 'better quality, and vice-versa. Valid values are from 0 '
                 'to 8 inclusive.'))
        self.spin_cpu.SetToolTip(tip)

        tip = (_('The "GOP" option can be used to set the maximum keyframe '
                 'interval. Anything up to 10 seconds is considered '
                 'reasonable for most content, so for 30 frames per second '
                 'content one would set to 300, for 60 fps content set '
                 'to 600. For "intra-only" output, set to 0. Set to -1 to '
                 'disable this control.'))
        self.spin_gop.SetToolTip(tip)

        self.Bind(wx.EVT_RADIOBOX, self.on_usage, self.rdb_usage)
        self.Bind(wx.EVT_SPINCTRL, self.on_cpu_used, self.spin_cpu)
        self.Bind(wx.EVT_SPINCTRL, self.on_gop, self.spin_gop)
    # ------------------------------------------------------------------#

    def default(self):
        """
        Set to default
        """
        self.spin_gop.SetValue(250)
        self.opt["GOP"] = '-g 250 -keyint_min 250'
        self.opt["RowMthreading"] = '-row-mt 1 -tiles 2x2'
        self.rdb_usage.SetSelection(0)
        self.opt["Usage"] = '-usage good'
        self.spin_cpu.SetValue(1)
        self.opt["CpuUsed"] = '-cpu-used 1'

        self.opt["Preset"] = ''
        self.opt["Profile"] = ''
        self.opt["Level"] = ''
        self.opt["Tune"] = ''
        self.opt["Deadline"] = ''

    # ------------------------------------------------------------------#

    def on_usage(self, event):
        """
        Set d-eadline
        """
        val = self.rdb_usage.GetStringSelection()
        self.opt["Usage"] = f'-usage {val}'
    # ------------------------------------------------------------------#

    def on_cpu_used(self, event):
        """
        Set cpu-used
        """
        self.opt["CpuUsed"] = f'-cpu-used {self.spin_cpu.GetValue()}'
    # ------------------------------------------------------------------#

    def on_gop(self, event):
        """
        Set group of pictures (GOP)
        """
        val = self.spin_gop.GetValue()
        if val == -1:
            self.opt["GOP"] = ''
        elif val == 0:
            self.opt["GOP"] = f'-g {val}'
        else:
            self.opt["GOP"] = f'-g {val} -keyint_min {val}'
    # ------------------------------------------------------------------#
