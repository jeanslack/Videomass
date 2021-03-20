# -*- coding: UTF-8 -*-
# Name: filter_transpose.py
# Porpose: Show dialog to get video transpose data based on FFmpeg syntax
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Jan.27.2021 *PEP8 compatible*
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
from math import pi as pi
import os
from time import sleep
from videomass3.vdms_threads.generic_task import FFmpegGenericTask


class Transpose(wx.Dialog):
    """
    A dialog tool to get video transpose data based on FFmpeg syntax.

    """
    get = wx.GetApp()
    OS = get.OS
    TMP = get.TMP
    BACKGROUND = '#1b0413'

    def __init__(self, parent, transpose, start_label,
                 v_width, v_height, fname, duration):
        """
        Make sure you use the clear button when you finish the task.

        """
        # current video size (first video file dragged into the list)
        self.v_width = v_width
        self.v_height = v_height
        # resizing values preserving aspect ratio for pseudo-monitor
        self.thr = 150 if self.v_height > self.v_width else 270
        self.h_ratio = (self.v_height / self.v_width) * self.thr
        self.w_ratio = (self.v_width / self.v_height) * self.h_ratio
        self.current_angle = 0
        self.center = ((self.w_ratio/2), (self.h_ratio/2))  # orignal center
        self.transpose = {'degrees': ['', 0]}

        self.duration = duration
        self.video = fname
        name = os.path.splitext(os.path.basename(self.video))[0]
        self.frame = os.path.join('%s' % Transpose.TMP, '%s.png' % name)

        if os.path.exists(self.frame):
            bitmap = wx.Bitmap(self.frame)
            img = bitmap.ConvertToImage()
            img = img.Scale(self.w_ratio, self.h_ratio,
                            wx.IMAGE_QUALITY_NORMAL)
            bmp = img.ConvertToBitmap()
            self.image = wx.Bitmap(bmp)
        else:
            self.image = wx.Bitmap(self.w_ratio, self.h_ratio)  # make empty

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.panelimg = wx.Panel(self, wx.ID_ANY, size=(270, 270),)
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        sizerBase.Add(self.panelimg, 0, wx.ALL | wx.CENTER, 5)

        self.x = wx.StaticBitmap(self.panelimg, wx.ID_ANY, self.image)
        self.statictxt = wx.StaticText(self, wx.ID_ANY,
                                       label=_("Default position"),
                                       style=wx.ST_NO_AUTORESIZE |
                                       wx.ALIGN_CENTRE_HORIZONTAL
                                       )
        sizerBase.Add(self.statictxt, 0, wx.CENTER | wx.EXPAND)
        self.btn_load = wx.Button(self, wx.ID_ANY, _("Load Frame"))
        sizerBase.Add(self.btn_load, 0, wx.ALL | wx.CENTRE, 5)
        msg = _("Rotation setting")
        sizerLabel = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (msg)),
                                       wx.VERTICAL)
        sizerBase.Add(sizerLabel, 0, wx.ALL | wx.EXPAND, 5)
        boxctrl = wx.BoxSizer(wx.VERTICAL)
        sizerLabel.Add(boxctrl, 0, wx.CENTRE)
        grid_sizerBase = wx.GridSizer(1, 2, 0, 0)
        self.button_left = wx.Button(self, wx.ID_ANY,
                                     (_("90° (left)")))  # ruota sx
        grid_sizerBase.Add(self.button_left, 0, wx.ALL | wx.CENTRE, 5)
        self.button_right = wx.Button(self, wx.ID_ANY, (_("90° (right)")))
        grid_sizerBase.Add(self.button_right, 0, wx.ALL | wx.CENTRE, 5)
        boxctrl.Add(grid_sizerBase, 0, wx.EXPAND)
        self.button_down = wx.Button(self, wx.ID_ANY,
                                     (_("180°")))  # capovolgi sotto
        boxctrl.Add(self.button_down, 0, wx.ALL | wx.CENTRE, 5)
        # buttons bottom
        gridBtn = wx.GridSizer(1, 2, 0, 0)
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_reset = wx.Button(self, wx.ID_CLEAR, _("Reset"))
        gridBtn.Add(btn_reset, 0, wx.ALL, 5)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        gridexit.Add(btn_close, 0, wx.ALL, 5)
        self.btn_ok = wx.Button(self, wx.ID_OK, _("Apply"))
        gridexit.Add(self.btn_ok, 0, wx.ALL, 5)
        gridBtn.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)
        sizerBase.Add(gridBtn, 0, wx.EXPAND)
        # ----------------------Properties--------------------------------#
        self.SetTitle(_("Transpose Filter"))
        self.panelimg.SetBackgroundColour(wx.Colour(Transpose.BACKGROUND))
        if Transpose.OS == 'Darwin':
            self.statictxt.SetFont(wx.Font(11, wx.SWISS, wx.ITALIC, wx.NORMAL))
        else:
            self.statictxt.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        # ----------------------Set layout------------------------------#
        self.SetSizer(sizerBase)
        # sizerBase.Fit(self)
        self.Fit()
        self.Layout()

        if os.path.exists(self.frame):
            self.btn_load.Disable()

        if transpose:
            self.statictxt.SetLabel(start_label)

            if transpose == "transpose=1":
                self.transpose['degrees'] = ["transpose=1", 90]
                self.rotate90(90)

            elif transpose == "transpose=2,transpose=2":
                self.transpose['degrees'] = ["transpose=2,transpose=2", 180]
                self.rotate90(180)

            elif transpose == "transpose=2":
                self.transpose['degrees'] = ["transpose=2", 270]
                self.rotate90(270)

        # ----------------------Binding (EVT)---------------------------------#
        self.Bind(wx.EVT_BUTTON, self.onLoad, self.btn_load)
        self.Bind(wx.EVT_BUTTON, self.on_left, self.button_left)
        self.Bind(wx.EVT_BUTTON, self.on_right, self.button_right)
        self.Bind(wx.EVT_BUTTON, self.on_down, self.button_down)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)
    # ------------------------------------------------------------------#

    def rotate90(self, degrees):
        """
        """
        self.current_angle += degrees
        val = float(self.current_angle * -pi/180)  # neg. value rot. clockwise
        image = self.image.ConvertToImage()
        image = image.Scale(self.w_ratio, self.h_ratio,
                            wx.IMAGE_QUALITY_NORMAL
                            )
        image = image.Rotate(val, self.center)
        self.x.SetBitmap(wx.Bitmap(image))
        self.panelimg.Layout()

    # ----------------------Event handler (callback)--------------------------#

    def onLoad(self, event):
        """
        Build FFmpeg argument to get a specific video frame for
        loading as StaticBitmap

        """
        t = self.duration.split(':')
        h, m, s = (int(t[0]) / 2, int(t[1]) / 2, float(t[2]) / 2)
        h, m, s = ("%02d" % h, "%02d" % m, "%02d" % s)
        arg = ('-ss %s:%s:%s -i "%s" -vframes 1 -y "%s"' % (h, m, s,
                                                            self.video,
                                                            self.frame
                                                            ))
        thread = FFmpegGenericTask(arg)
        thread.join()  # wait end thread
        error = thread.status
        if error:
            wx.MessageBox('%s' % error, 'ERROR', wx.ICON_ERROR)
            return
        else:
            sleep(1.0)  # need to wait end task for saving
            bitmap = wx.Bitmap(self.frame)
            img = bitmap.ConvertToImage()
            img = img.Scale(self.w_ratio, self.h_ratio)
            bmp = img.ConvertToBitmap()
            self.image = wx.Bitmap(bmp)  # convert to bitmap
            self.x.SetBitmap(self.image)  # set StaticBitmap
            self.panelimg.Layout()
            self.btn_load.Disable()
            self.on_reset(self)  # make default position
    # ------------------------------------------------------------------#

    def on_right(self, event):
        """
        """
        if self.transpose['degrees'][1] == 0:
            self.rotate90(90)

        elif self.transpose['degrees'][1] == 90:
            return

        elif self.transpose['degrees'][1] == 180:
            self.rotate90(270)

        elif self.transpose['degrees'][1] == 270:
            self.rotate90(180)

        self.transpose['degrees'] = ["transpose=1", 90]
        self.statictxt.SetLabel(_("Rotate 90 degrees right"))

        self.Layout()
    # ------------------------------------------------------------------#

    def on_down(self, event):
        """
        """
        if self.transpose['degrees'][1] == 0:
            self.rotate90(180)

        elif self.transpose['degrees'][1] == 90:
            self.rotate90(90)

        elif self.transpose['degrees'][1] == 180:
            return

        elif self.transpose['degrees'][1] == 270:
            self.rotate90(270)

        self.transpose['degrees'] = ["transpose=2,transpose=2", 180]
        self.statictxt.SetLabel(_("Rotate 180 degrees"))
        self.Layout()
    # ------------------------------------------------------------------#

    def on_left(self, event):
        """
        """
        if self.transpose['degrees'][1] == 0:
            self.rotate90(270)

        elif self.transpose['degrees'][1] == 90:
            self.rotate90(180)

        elif self.transpose['degrees'][1] == 180:
            self.rotate90(90)

        elif self.transpose['degrees'][1] == 270:
            return

        self.transpose['degrees'] = ["transpose=2", 270]
        self.statictxt.SetLabel(_("Rotate 90 degrees left"))
        self.Layout()
    # ------------------------------------------------------------------#

    def on_reset(self, event):
        """
        Revert to default positioning
        """
        if self.transpose['degrees'][1] == 0:
            pass

        elif self.transpose['degrees'][1] == 90:
            self.rotate90(270)

        elif self.transpose['degrees'][1] == 180:
            self.rotate90(180)

        elif self.transpose['degrees'][1] == 270:
            self.rotate90(90)

        self.transpose['degrees'] = ["", 0]
        self.statictxt.SetLabel(_("Default position"))
        self.Layout()
    # ------------------------------------------------------------------#

    def on_close(self, event):
        event.Skip()
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        if you enable self.Destroy(), it delete from memory all
        data event and no return correctly. It has the right behavior
        if not used here, because it is called in the main frame.

        Event.Skip(), work correctly here. Sometimes needs to disable
        it for needs to maintain the view of the window.
        """
        self.GetValue()
        # self.Destroy()
        event.Skip()
    # ------------------------------------------------------------------#

    def GetValue(self):
        """
        This method return values via the interface GetValue()
        """
        msg = self.statictxt.GetLabel()
        return (self.transpose['degrees'][0], msg)
