# -*- coding: UTF-8 -*-
"""
Name: filter_transpose.py
Purpose: Show a dialog to get video transpose data based on FFmpeg syntax
Compatibility: Python >= 3.11, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.12.2026
Code checker: flake8, pylint, ruff

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
import webbrowser
from math import pi as pigreco

import wx
from pubsub import pub

from videomass.vdms_io.io_tools import show_msg_notify
from videomass.vdms_io.make_filelog import make_log_template
from videomass.vdms_threads.generic_task import FFmpegGenericTask
from videomass.vdms_utils.utils import integer_to_time, time_to_integer


class Transpose(wx.Dialog):
    """
    A dialog tool to get video transpose data based on FFmpeg syntax.
    """

    get = wx.GetApp()
    appdata = get.appset
    LOGDIR = appdata["logdir"]
    TMPROOT = os.path.join(get.appset["cachedir"], "tmp", "Transpose")
    TMPSRC = os.path.join(TMPROOT, "tmpsrc")
    os.makedirs(TMPSRC, mode=0o777, exist_ok=True)
    BACKGROUND = "#1b0413"

    def __init__(self, parent, *args, **kwa):
        """
        args[0]: transpose data if any.
        args[1]: label rotate indicator
        args[2]: reset button bitmap
        v_width: source video width
        v_height: source video height
        filename: matches with the only one video file dragged
                  into the list or the selected one if many.
        duration: Overall time duration of video.
        """
        self.v_width = kwa["width"]
        self.v_height = kwa["height"]
        # resizing values preserving aspect ratio for pseudo-monitor
        self.thr = 150 if self.v_height > self.v_width else 270
        self.h_ratio = int((self.v_height / self.v_width) * self.thr)
        self.w_ratio = int((self.v_width / self.v_height) * self.h_ratio)
        self.current_angle = 0
        self.center = int(self.w_ratio / 2), int(self.h_ratio / 2)
        self.transpose = {"degrees": ["", 0]}
        self.initial_args = (args[0], args[1])
        self.video = kwa["filename"]
        name = os.path.splitext(os.path.basename(self.video))[0]
        self.frame = os.path.join(Transpose.TMPSRC, f"{name}.png")
        self.stbitmap = None
        self.scaled_img = None  # Cache per l'immagine pre-scalata
        self.mills = time_to_integer(kwa["duration"].split(".")[0])
        self.thread = None
        self.logfile = None

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.panelimg = wx.Panel(
            self,
            wx.ID_ANY,
            size=(270, 270),
        )
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        sizerBase.Add(self.panelimg, 0, wx.ALL | wx.CENTER, 5)
        self.statictxt = wx.StaticText(
            self,
            wx.ID_ANY,
            label=_("Loading preview..."),
            style=wx.ST_NO_AUTORESIZE | wx.ALIGN_CENTRE_HORIZONTAL,
        )
        sizerBase.Add(self.statictxt, 0, wx.CENTER | wx.EXPAND)
        sizerBase.Add(10, 10)
        msg = _("Rotation setting")
        sbox = wx.StaticBox(self, wx.ID_ANY, (msg))
        sizerLabel = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        sizerBase.Add(sizerLabel, 0, wx.ALL | wx.EXPAND, 5)
        boxctrl = wx.BoxSizer(wx.VERTICAL)
        sizerLabel.Add(boxctrl, 0, wx.CENTRE)
        grid_sizerBase = wx.GridSizer(1, 2, 0, 0)
        self.button_left = wx.Button(sbox, wx.ID_ANY, (_("90° (left)")))
        grid_sizerBase.Add(self.button_left, 0, wx.ALL | wx.CENTRE, 5)
        self.button_right = wx.Button(sbox, wx.ID_ANY, (_("90° (right)")))
        grid_sizerBase.Add(self.button_right, 0, wx.ALL | wx.CENTRE, 5)
        boxctrl.Add(grid_sizerBase, 0, wx.EXPAND)
        self.button_down = wx.Button(sbox, wx.ID_ANY, (_("180°")))
        boxctrl.Add(self.button_down, 0, wx.ALL | wx.CENTRE, 5)

        # ----- confirm buttons section
        gridbtns = wx.GridSizer(1, 2, 0, 0)
        gridhelp = wx.GridSizer(1, 1, 0, 0)
        btn_help = wx.Button(self, wx.ID_HELP, "")
        gridhelp.Add(btn_help, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridbtns.Add(gridhelp)
        boxaff = wx.BoxSizer(wx.HORIZONTAL)
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "")
        boxaff.Add(btn_cancel, 0)
        self.btn_ok = wx.Button(self, wx.ID_OK)
        boxaff.Add(self.btn_ok, 0, wx.LEFT, 5)
        self.btn_reset = wx.Button(self, wx.ID_ANY, _("Reset"))
        self.btn_reset.SetBitmap(args[2], wx.LEFT)
        boxaff.Add(self.btn_reset, 0, wx.LEFT, 5)
        gridbtns.Add(boxaff, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=5)
        sizerBase.Add(gridbtns, 0, wx.EXPAND)

        # ----------------------Properties--------------------------------#
        self.SetTitle(_("Transpose Tool"))
        self.panelimg.SetBackgroundColour(wx.Colour(Transpose.BACKGROUND))
        if Transpose.appdata["ostype"] == "Darwin":
            self.statictxt.SetFont(wx.Font(11, wx.SWISS, wx.ITALIC, wx.NORMAL))
        else:
            self.statictxt.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        # Disabilita i controlli finché l'anteprima non è pronta
        self._set_controls_enabled(False)

        # ----- Set layout
        self.SetSizer(sizerBase)
        sizerBase.Fit(self)
        self.Layout()

        # Avvia l'estrazione asincrona tramite pubsub
        self.process()

        # ----------------------Binding (EVT)---------------------------------#
        self.Bind(wx.EVT_BUTTON, self.on_left, self.button_left)
        self.Bind(wx.EVT_BUTTON, self.on_right, self.button_right)
        self.Bind(wx.EVT_BUTTON, self.on_down, self.button_down)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, self.btn_reset)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    # ------------------------------------------------------------------#

    def _set_controls_enabled(self, state):
        """Abilita o disabilita i pulsanti durante il caricamento."""
        self.button_left.Enable(state)
        self.button_right.Enable(state)
        self.button_down.Enable(state)
        self.btn_reset.Enable(state)
        self.btn_ok.Enable(state)

    # ------------------------------------------------------------------#

    def process(self):
        """
        Avvia FFmpegGenericTask senza join() e si iscrive a RESULT_EVT.
        """
        self.logfile = make_log_template(
            "generic_task.log",
            Transpose.LOGDIR,
            mode="w",
        )
        if not self.mills:
            sseg = ""
        else:
            stime = integer_to_time(int(self.mills / 2), False)
            sseg = f"-ss {stime}"
        arg = (
            f'{sseg} -i "{self.video}" -f image2 '
            f'-update 1 -frames:v 1 "{self.frame}"'
        )
        pub.subscribe(self.on_frame_ready, "RESULT_EVT")
        self.thread = FFmpegGenericTask(arg, "Transpose", self.logfile)

    # ------------------------------------------------------------------#

    def on_frame_ready(self, status):
        """
        Callback invocata da pubsub sul thread GUI al termine di FFmpeg.
        """
        pub.unsubscribe(self.on_frame_ready, "RESULT_EVT")
        if not self or self.thread is None:
            return

        if self.thread.status:
            self.statictxt.SetLabel(_("Preview unavailable"))
            show_msg_notify(
                self.GetParent(), logname=os.path.basename(self.logfile)
            )
            return

        # Carica, scala e salva in cache la wx.Image una sola volta
        img = wx.Image(self.frame, wx.BITMAP_TYPE_PNG)
        if not img.IsOk():
            self.statictxt.SetLabel(_("Preview unavailable"))
            return

        self.scaled_img = img.Scale(
            self.w_ratio, self.h_ratio, wx.IMAGE_QUALITY_NORMAL
        )
        bmp = wx.Bitmap(self.scaled_img)
        self.stbitmap = wx.StaticBitmap(self.panelimg, wx.ID_ANY, bmp)
        self._center_bitmap(bmp)

        self._set_controls_enabled(True)
        self.on_reset(None)

        # Ripristina lo stato precedente se passato in args
        arg_filter, arg_label = self.initial_args
        presets = {
            "transpose=1": 90,
            "transpose=2,transpose=2": 180,
            "transpose=2": 270,
        }
        if arg_filter in presets:
            self._apply_rotation(arg_filter, presets[arg_filter], arg_label)
        else:
            self.on_reset(None)

        self.Layout()

    # ------------------------------------------------------------------#

    def _center_bitmap(self, bmp):
        """Centra la bitmap all'interno del pannello 270x270."""
        pw, ph = self.panelimg.GetSize()
        bw, bh = bmp.GetSize()
        self.stbitmap.SetPosition(((pw - bw) // 2, (ph - bh) // 2))

    # ------------------------------------------------------------------#

    def rotate90(self, degrees):
        """
        Ruota l'immagine pre-scalata in cache senza ricaricarla o riscalarla.
        """
        if self.scaled_img is None:
            return

        self.current_angle = (self.current_angle + degrees) % 360
        # val negativo per rotazione oraria in wx.Image.Rotate
        val = float(self.current_angle * -pigreco / 180)
        rotated_img = self.scaled_img.Rotate(val, self.center)
        bmp = wx.Bitmap(rotated_img)
        self.stbitmap.SetBitmap(bmp)
        self._center_bitmap(bmp)
        self.panelimg.Layout()

    # ----------------------Event handler (callback)--------------------------#

    def _apply_rotation(self, ffmpeg_filter, degrees, label):
        """
        Imposta l'orientamento assoluto, aggiorna l'etichetta
        e ruota l'anteprima.
        """
        if self.scaled_img is None:
            return

        if self.current_angle == degrees and self.stbitmap is not None:
            self.statictxt.SetLabel(label)
            return

        self.current_angle = degrees
        self.transpose["degrees"] = [ffmpeg_filter, degrees]
        self.statictxt.SetLabel(label)

        # val negativo per rotazione oraria in wx.Image.Rotate
        val = float(degrees * -pigreco / 180)
        rotated_img = self.scaled_img.Rotate(val, self.center)
        bmp = wx.Bitmap(rotated_img)
        self.stbitmap.SetBitmap(bmp)
        self._center_bitmap(bmp)
        self.panelimg.Layout()
        self.Layout()

    # ----------------------Event handler (callback)--------------------------#

    def on_right(self, event):
        """
        Rotate 90 degrees right
        """
        self._apply_rotation("transpose=1", 90, _("Rotate 90 degrees right"))

    # ------------------------------------------------------------------#

    def on_down(self, event):
        """
        Rotate 180 degrees
        """
        self._apply_rotation(
            "transpose=2,transpose=2", 180, _("Rotate 180 degrees")
        )

    # ------------------------------------------------------------------#

    def on_left(self, event):
        """
        Rotate 90 degrees left
        """
        self._apply_rotation("transpose=2", 270, _("Rotate 90 degrees left"))

    # ------------------------------------------------------------------#

    def on_reset(self, event):
        """
        Revert to default positioning
        """
        self._apply_rotation("", 0, _("Default position"))

    # ------------------------------------------------------------------#

    def on_help(self, event):
        """
        Open default web browser via Python Web-browser controller.
        see <https://python.org>
        """
        page = (
            "https://github.io"
            "Video_filters_en.pdf#%5B%7B%22num%22%3A19%2C%22gen"
            "%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2C56.7%2C711."
            "639%2C0%5D"
        )
        webbrowser.open(page)

    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        Close this dialog without saving anything
        """
        pub.unsubscribe(self.on_frame_ready, "RESULT_EVT")
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
        This method return values via the getvalue() interface
        from the caller. See the caller for more info and usage.
        """
        msg = self.statictxt.GetLabel()
        return (self.transpose["degrees"][0], msg)
