# -*- coding: UTF-8 -*-
"""
Name: filter_transpose.py
Porpose: Show dialog to get video transpose data based on FFmpeg syntax
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.20.2023
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
import os
from math import pi as pigreco
import wx
from videomass.vdms_threads.generic_task import FFmpegGenericTask


class Transpose(wx.Dialog):
    """
    A dialog tool to get video transpose data based on FFmpeg syntax.

    """
    get = wx.GetApp()
    appdata = get.appset
    TMPROOT = os.path.join(get.appset['cachedir'], 'tmp', 'Transpose')
    TMPSRC = os.path.join(TMPROOT, 'tmpsrc')
    os.makedirs(TMPSRC, mode=0o777, exist_ok=True)
    BACKGROUND = '#1b0413'

    def __init__(self, parent, transpose, start_label,
                 v_width, v_height, fname, duration):
        """
        transpose: previus data already saved.
        start_label: label rotate indicator
        v_width: source video width
        v_height: source video height
        fname: matches with the only one video file dragged
               into the list or the selected one if many.
        duration: Overall time duration of video.
        """
        self.v_width = v_width
        self.v_height = v_height
        # resizing values preserving aspect ratio for pseudo-monitor
        self.thr = 150 if self.v_height > self.v_width else 270
        self.h_ratio = int((self.v_height / self.v_width) * self.thr)
        self.w_ratio = int((self.v_width / self.v_height) * self.h_ratio)
        self.current_angle = 0
        self.center = (int((self.w_ratio / 2)),
                       int((self.h_ratio / 2)),
                       )  # original center
        self.transpose = {'degrees': ['', 0]}
        self.duration = duration
        self.video = fname
        name = os.path.splitext(os.path.basename(self.video))[0]
        self.frame = os.path.join(Transpose.TMPSRC, f'{name}.png')
        self.stbitmap = None
        self.image = None

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.panelimg = wx.Panel(self, wx.ID_ANY, size=(270, 270),)
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        sizerBase.Add(self.panelimg, 0, wx.ALL | wx.CENTER, 5)
        self.statictxt = wx.StaticText(self, wx.ID_ANY,
                                       label=_("Default position"),
                                       style=wx.ST_NO_AUTORESIZE
                                       | wx.ALIGN_CENTRE_HORIZONTAL,
                                       )
        sizerBase.Add(self.statictxt, 0, wx.CENTER | wx.EXPAND)
        sizerBase.Add(10, 10)
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
        if Transpose.appdata['ostype'] == 'Darwin':
            self.statictxt.SetFont(wx.Font(11, wx.SWISS, wx.ITALIC, wx.NORMAL))
        else:
            self.statictxt.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        # ----------------------Set layout------------------------------#
        self.SetSizer(sizerBase)
        # sizerBase.Fit(self)
        self.Fit()
        self.Layout()

        self.image_loader()
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
        self.Bind(wx.EVT_BUTTON, self.on_left, self.button_left)
        self.Bind(wx.EVT_BUTTON, self.on_right, self.button_right)
        self.Bind(wx.EVT_BUTTON, self.on_down, self.button_down)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)
    # ------------------------------------------------------------------#

    def process(self):
        """
        Calls thread to Run ffmpeg process. Note that the
        trim start point on this process is set to the total
        length of the movie divided by two.
        """
        h, m, s = self.duration.split(':')
        intseq = (int(h) // 2, int(m) // 2, round(float(s) / 2))
        stime = ':'.join([str(x).zfill(2) for x in intseq])
        arg = f'-ss {stime} -i "{self.video}" -vframes 1 -y "{self.frame}"'
        thread = FFmpegGenericTask(arg)
        thread.join()  # wait end thread
        error = thread.status
        if error:
            return error
        return None
    # ------------------------------------------------------------------------#

    def image_loader(self):
        """
        Loads initial StaticBitmap on panel
        """
        if not os.path.exists(self.frame):
            error = self.process()
            if error:
                wx.MessageBox(f'{error}', 'ERROR', wx.ICON_ERROR, self)
                return
        bitmap = wx.Bitmap(self.frame)
        img = bitmap.ConvertToImage()
        img = img.Scale(self.w_ratio, self.h_ratio, wx.IMAGE_QUALITY_NORMAL)
        bmp = img.ConvertToBitmap()
        self.image = wx.Bitmap(bmp)  # convert to bitmap
        self.stbitmap = wx.StaticBitmap(self.panelimg, wx.ID_ANY, self.image)
        self.panelimg.Layout()
        self.on_reset(self)  # make default position
    # ------------------------------------------------------------------#

    def rotate90(self, degrees):
        """
        Rotates image to a specified `degrees`
        """
        self.current_angle += degrees
        # neg. value rot. clockwise:
        val = float(self.current_angle * -pigreco / 180)
        image = self.image.ConvertToImage()
        image = image.Scale(self.w_ratio, self.h_ratio,
                            wx.IMAGE_QUALITY_NORMAL
                            )
        image = image.Rotate(val, self.center)
        self.stbitmap.SetBitmap(wx.Bitmap(image))
        self.panelimg.Layout()

    # ----------------------Event handler (callback)--------------------------#

    def on_right(self, event):
        """
        Rotate 90 degrees right
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
        Rotate 180 degrees
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
        Rotate 90 degrees left
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
        """
        Close this dialog without saving anything
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Don't use self.Destroy() in this dialog
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def getvalue(self):
        """
        This method return values via the interface getvalue()
        by the caller. See the caller for more info and usage.
        """
        msg = self.statictxt.GetLabel()
        return (self.transpose['degrees'][0], msg)
