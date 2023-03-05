# -*- coding: UTF-8 -*-
"""
FileName: webm.py
Porpose: Contains vp8/vp9 functionality for A/V Conversions
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.03.2023
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


class WebMPan(scrolled.ScrolledPanel):
    """
    This scroll panel implements controls for extra options
    of the `vp8/vp9` encoders.
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
                                        name="WEBM scrolledpanel",
                                        )
        sizerbase = wx.BoxSizer(wx.VERTICAL)
        sizerbase.Add((10, 10), 0)
        infomsg = "WebM"
        self.lbl_info = wx.StaticText(self, wx.ID_ANY, label=infomsg)
        sizerbase.Add(self.lbl_info, 0, wx.ALL | wx.CENTER, 5)
        if osplat == 'Darwin':
            self.lbl_info.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        else:
            self.lbl_info.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerbase.Add((10, 10), 0)
        self.rdb_deadline = wx.RadioBox(self, wx.ID_ANY,
                                        (_("Quality and Compression")),
                                        choices=[("best"),
                                                 ("good"),
                                                 ("realtime"),
                                                 ],
                                        majorDimension=0,
                                        style=wx.RA_SPECIFY_ROWS,
                                        )
        sizerbase.Add(self.rdb_deadline, 0, wx.TOP | wx.CENTRE, 5)
        lab_cpu = wx.StaticText(self, wx.ID_ANY, (_("Quality and Speed:")))
        sizerbase.Add(lab_cpu, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.spin_cpu = wx.SpinCtrl(self, wx.ID_ANY, "1", min=-8,
                                    max=8, size=(-1, -1),
                                    style=wx.TE_PROCESS_ENTER,
                                    )
        sizerbase.Add(self.spin_cpu, 0, wx.TOP | wx.CENTRE, 5)
        self.ckbx_rowmt = wx.CheckBox(self,
                                      wx.ID_ANY,
                                      ('Row based multithreading'),
                                      )
        sizerbase.Add(self.ckbx_rowmt, 0, wx.TOP | wx.CENTRE, 5)

        self.SetSizer(sizerbase)  # set panel
        self.SetAutoLayout(1)
        self.SetupScrolling()

        tip = (_('"good" is the default and recommended for most '
                 'applications; "best" is recommended if you have lots of '
                 'time and want the best compression efficiency; "realtime" '
                 'is recommended for live/fast encoding'))
        self.rdb_deadline.SetToolTip(tip)
        tip = (_('"cpu-used" sets how efficient the compression will be. '
                 'The meaning depends on the Quality and Compression '
                 'mode above.'))
        self.spin_cpu.SetToolTip(tip)

        self.Bind(wx.EVT_RADIOBOX, self.on_deadline, self.rdb_deadline)
        self.Bind(wx.EVT_SPINCTRL, self.on_cpu_used, self.spin_cpu)
        self.Bind(wx.EVT_CHECKBOX, self.on_row_mt, self.ckbx_rowmt)
    # ------------------------------------------------------------------#

    def default(self):
        """
        Set to default
        """
        if self.opt["VideoCodec"] == "-c:v libvpx":
            self.ckbx_rowmt.SetValue(False)
            self.ckbx_rowmt.Disable()
            self.opt["RowMthreading"] = ''
            self.lbl_info.SetLabel("VP8 - libvpx")
        else:
            self.ckbx_rowmt.SetValue(True)
            self.ckbx_rowmt.Enable()
            self.opt["RowMthreading"] = '-row-mt 1'
            self.lbl_info.SetLabel("VP9 - libvpx-vp9")

        self.rdb_deadline.SetSelection(1)
        self.opt["Deadline"] = '-deadline good'
        self.spin_cpu.SetRange(0, 5)
        self.spin_cpu.SetValue(1)
        self.opt["CpuUsed"] = '-cpu-used 1'

        self.opt["Preset"] = ''
        self.opt["Profile"] = ''
        self.opt["Level"] = ''
        self.opt["Tune"] = ''
        self.opt["Usage"] = ''
        self.opt["GOP"] = ''
    # ------------------------------------------------------------------#

    def on_deadline(self, event):
        """
        Sets range according to spin_cpu used
        """
        if self.rdb_deadline.GetSelection() in [0, 1]:
            self.spin_cpu.SetRange(0, 5), self.spin_cpu.SetValue(0)
        else:
            self.spin_cpu.SetRange(0, 15), self.spin_cpu.SetValue(0)
        val = self.rdb_deadline.GetStringSelection()
        self.opt["Deadline"] = f'-deadline {val}'
    # ------------------------------------------------------------------#

    def on_cpu_used(self, event):
        """
        Set cpu-used according to deadline value
        """
        self.opt["CpuUsed"] = f'-cpu-used {self.spin_cpu.GetValue()}'
    # ------------------------------------------------------------------#

    def on_row_mt(self, event):
        """
        Sets row-mt option only for vp9
        """
        if self.ckbx_rowmt.IsChecked():
            self.opt["RowMthreading"] = '-row-mt 1'
        else:
            self.opt["RowMthreading"] = ''
