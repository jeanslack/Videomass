# -*- coding: UTF-8 -*-
"""
Name: filter_colorcorrection.py
Porpose: Show dialog to set color correction data based on FFmpeg syntax
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.18.2023
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
import wx
from videomass.vdms_utils.utils import get_milliseconds
from videomass.vdms_utils.utils import milliseconds2clocksec
from videomass.vdms_threads.generic_task import FFmpegGenericTask


class ColorEQ(wx.Dialog):
    """
    A dialog tool to set video contrast, brightness,
    saturation, gamma values based on FFmpeg syntax.
    See ``av_conversions.py`` -> ``on_Set_colorcorrect`` method
    for how to use this class.
    """
    get = wx.GetApp()
    OS = get.appset['ostype']
    TMPROOT = os.path.join(get.appset['cachedir'], 'tmp', 'ColorEQ')
    TMPSRC = os.path.join(TMPROOT, 'tmpsrc')
    TMPEDIT = os.path.join(TMPROOT, 'tmpedit')
    os.makedirs(TMPSRC, mode=0o777, exist_ok=True)
    os.makedirs(TMPEDIT, mode=0o777, exist_ok=True)
    # BACKGROUND = '#1b0413'

    def __init__(self, parent, colorset, v_width, v_height, fname, duration):
        """
        colorset: previus data already saved.
        v_width: source video width
        v_height: source video height
        fname: matches with the only one video file dragged
               into the list or the selected one if many.
        duration: Overall time duration of video.
        """
        self.filesource = fname
        name = os.path.splitext(os.path.basename(self.filesource))[0]
        self.framesrc = os.path.join(ColorEQ.TMPSRC, f'{name}.png')
        self.frameedit = os.path.join(ColorEQ.TMPEDIT, f'{name}.png')
        self.filetime = os.path.join(ColorEQ.TMPROOT, f'{name}.clock')
        self.v_width = v_width
        self.v_height = v_height
        # resizing values preserving aspect ratio for pseudo-monitors
        thr = 150 if self.v_height > self.v_width else 270
        self.h_ratio = int((self.v_height / self.v_width) * thr)
        self.w_ratio = int((self.v_width / self.v_height) * self.h_ratio)
        self.bitmap_src = None
        self.bitmap_edit = None
        self.contrast = ""
        self.brightness = ""
        self.saturation = ""
        self.gamma = ""
        if os.path.exists(self.filetime):
            with open(self.filetime, "r", encoding='utf8') as atime:
                self.clock = atime.read().strip()
        else:
            self.clock = '00:00:00'

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        sizerpanels = wx.FlexGridSizer(2, 2, 2, 2)
        sizerBase.Add(sizerpanels, 0)
        self.panel_img1 = wx.Panel(self, wx.ID_ANY,
                                   size=(self.w_ratio, self.h_ratio))
        sizerpanels.Add(self.panel_img1, 0, wx.ALL | wx.CENTER, 5)
        self.panel_img2 = wx.Panel(self, wx.ID_ANY,
                                   size=(self.w_ratio, self.h_ratio))
        sizerpanels.Add(self.panel_img2, 0, wx.ALL | wx.CENTER, 5)
        lab_imgsrc = wx.StaticText(self, wx.ID_ANY,
                                   label=_("Before"),
                                   style=wx.ST_NO_AUTORESIZE
                                   | wx.ALIGN_CENTRE_HORIZONTAL,
                                   )
        sizerpanels.Add(lab_imgsrc, 0, wx.CENTER | wx.EXPAND)
        lab_imgfilt = wx.StaticText(self, wx.ID_ANY,
                                    label=_("After"),
                                    style=wx.ST_NO_AUTORESIZE
                                    | wx.ALIGN_CENTRE_HORIZONTAL,
                                    )
        sizerpanels.Add(lab_imgfilt, 0, wx.CENTER | wx.EXPAND)
        msg = _("Search for a specific frame")
        stboxtime = wx.StaticBox(self, wx.ID_ANY, msg)
        sizertime = wx.StaticBoxSizer(stboxtime, wx.HORIZONTAL)
        sizerBase.Add(sizertime, 0, wx.ALL | wx.CENTER, 5)
        self.sld_time = wx.Slider(self, wx.ID_ANY,
                                  get_milliseconds(self.clock),
                                  0,
                                  get_milliseconds(duration),
                                  size=(250, -1),
                                  style=wx.SL_HORIZONTAL,
                                  )
        sizertime.Add(self.sld_time, 0, wx.ALL | wx.CENTER, 5)
        self.txttime = wx.StaticText(self, wx.ID_ANY, self.clock)
        sizertime.Add(self.txttime, 0, wx.ALL | wx.CENTER, 5)
        self.btn_load = wx.Button(self, wx.ID_ANY, _("Load"))
        self.btn_load.Disable()
        sizertime.Add(self.btn_load, 1, wx.ALL | wx.EXPAND, 10)
        sizergrid = wx.FlexGridSizer(2, 4, 0, 0)
        lbl_contrast = wx.StaticText(self, wx.ID_ANY, _('Contrast:'))
        sizergrid.Add(lbl_contrast, 0, wx.LEFT
                      | wx.ALIGN_CENTRE_VERTICAL
                      | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.sld_contrast = wx.Slider(self, wx.ID_ANY, 0, -100, 100,
                                      size=(180, -1), style=wx.SL_HORIZONTAL
                                      | wx.SL_AUTOTICKS
                                      | wx.SL_LABELS,
                                      )
        sizergrid.Add(self.sld_contrast, 0, wx.LEFT
                      | wx.ALIGN_CENTRE_VERTICAL
                      | wx.ALIGN_CENTRE_HORIZONTAL, 5)

        lbl_brigh = wx.StaticText(self, wx.ID_ANY, _('Brightness:'))
        sizergrid.Add(lbl_brigh, 0, wx.LEFT
                      | wx.ALIGN_CENTRE_VERTICAL
                      | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.sld_bright = wx.Slider(self, wx.ID_ANY, 0, -100, 100,
                                    size=(180, -1), style=wx.SL_HORIZONTAL
                                    | wx.SL_AUTOTICKS
                                    | wx.SL_LABELS,
                                    )
        sizergrid.Add(self.sld_bright, 0, wx.LEFT
                      | wx.ALIGN_CENTRE_VERTICAL
                      | wx.ALIGN_CENTRE_HORIZONTAL, 5)

        lbl_sat = wx.StaticText(self, wx.ID_ANY, _('Saturation:'))
        sizergrid.Add(lbl_sat, 0, wx.LEFT
                      | wx.ALIGN_CENTRE_VERTICAL
                      | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.sld_sat = wx.Slider(self, wx.ID_ANY, 0, 0, 300,
                                 size=(180, -1), style=wx.SL_HORIZONTAL
                                 | wx.SL_AUTOTICKS
                                 | wx.SL_LABELS,
                                 )
        sizergrid.Add(self.sld_sat, 0, wx.LEFT
                      | wx.ALIGN_CENTRE_VERTICAL
                      | wx.ALIGN_CENTRE_HORIZONTAL, 5)

        lbl_gam = wx.StaticText(self, wx.ID_ANY, _('Gamma:'))
        sizergrid.Add(lbl_gam, 0, wx.LEFT
                      | wx.ALIGN_CENTRE_VERTICAL
                      | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        self.sld_gam = wx.Slider(self, wx.ID_ANY, 0, 0, 100,
                                 size=(180, -1), style=wx.SL_HORIZONTAL
                                 | wx.SL_AUTOTICKS
                                 | wx.SL_LABELS,
                                 )
        sizergrid.Add(self.sld_gam, 0, wx.LEFT
                      | wx.ALIGN_CENTRE_VERTICAL
                      | wx.ALIGN_CENTRE_HORIZONTAL, 5)
        boxcolor = wx.StaticBox(self, wx.ID_ANY, (_("Color EQ")))
        sizercolor = wx.StaticBoxSizer(boxcolor, wx.VERTICAL)
        sizerBase.Add(sizercolor, 0, wx.ALL | wx.EXPAND, 5)
        sizercolor.Add(sizergrid, 0, wx.BOTTOM | wx.CENTRE, 10)
        # bottom btns
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
        self.SetSizer(sizerBase)
        sizerBase.Fit(self)
        self.Layout()
        # ----------------------Properties-----------------------#
        if ColorEQ.OS == 'Darwin':
            lab_imgsrc.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            lab_imgfilt.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            lab_imgsrc.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            lab_imgfilt.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self.SetTitle(_("Color Correction Equalizer"))
        # ----------------------Binding (EVT)-------------------------#
        self.Bind(wx.EVT_COMMAND_SCROLL, self.on_seek_time, self.sld_time)
        self.Bind(wx.EVT_BUTTON, self.on_load_at_time, self.btn_load)
        self.Bind(wx.EVT_SCROLL_CHANGED, self.on_contrast, self.sld_contrast)
        self.Bind(wx.EVT_SCROLL_CHANGED, self.on_brightness, self.sld_bright)
        self.Bind(wx.EVT_SCROLL_CHANGED, self.on_saturation, self.sld_sat)
        self.Bind(wx.EVT_SCROLL_CHANGED, self.on_gamma, self.sld_gam)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)

        if duration == '00:00:00.000':
            self.sld_time.Disable()

        if colorset:  # previusly values
            self.set_default(colorset)
        self.loader_initial_source()
        if not colorset:
            wx.StaticBitmap(self.panel_img2, wx.ID_ANY, self.bitmap_src)
        else:
            self.loader_initial_edit()

    # ----------------------Event handler (callback)--------------------------#

    def process(self, pathtosave, equalizer=''):
        """
        Calls thread to Run ffmpeg process
        """
        eql = '' if not equalizer else f'-vf "{equalizer}"'
        arg = (f'-ss {self.clock} -i "{self.filesource}" -vframes 1 '
               f'{eql} -y "{pathtosave}"')
        thread = FFmpegGenericTask(arg)
        thread.join()  # wait end thread
        error = thread.status
        if error:
            return error
        return None
    # ------------------------------------------------------------------------#

    def loader_initial_source(self):
        """
        Loads initial StaticBitmaps on panels 1 (source)
        To set previus values (colorset) you have to call
        this method before call `loader_initial_edit`.
        """
        if not os.path.exists(self.framesrc):
            error = self.process(self.framesrc)
            if error:
                wx.MessageBox(f'{error}', 'ERROR', wx.ICON_ERROR, self)
                return
        bitmap = wx.Bitmap(self.framesrc)
        img = bitmap.ConvertToImage()
        img = img.Scale(self.w_ratio, self.h_ratio, wx.IMAGE_QUALITY_NORMAL)
        bmp = img.ConvertToBitmap()
        self.bitmap_src = wx.Bitmap(bmp)
        wx.StaticBitmap(self.panel_img1, wx.ID_ANY, self.bitmap_src)
    # ------------------------------------------------------------------------#

    def loader_initial_edit(self):
        """
        Loads initial StaticBitmaps on panels 2 (edit)
        """
        if os.path.exists(self.frameedit):
            bitmap = wx.Bitmap(self.frameedit)
            img = bitmap.ConvertToImage()
            img = img.Scale(self.w_ratio, self.h_ratio,
                            wx.IMAGE_QUALITY_NORMAL)
            bmp = img.ConvertToBitmap()
            self.bitmap_edit = wx.Bitmap(bmp)
            wx.StaticBitmap(self.panel_img2, wx.ID_ANY, self.bitmap_edit)
        else:
            self.bitmap_edit = wx.Bitmap(self.w_ratio, self.h_ratio)
            wx.StaticBitmap(self.panel_img2, wx.ID_ANY, self.bitmap_edit)
    # ------------------------------------------------------------------------#

    def set_default(self, colorset):
        """
        Set previusly setting with colorset data.
        """
        filterlist = colorset.split(':')
        filterlist[0] = filterlist[0].split(sep='=', maxsplit=1)[1]
        values = dict(x.split('=') for x in filterlist)

        print(filterlist)
        print(values)

        for x, y in values.items():
            if x == 'contrast':
                self.contrast = f'contrast={y}'
            if x == 'brightness':
                self.contrast = f'brightness={y}'
            if x == 'saturation':
                self.contrast = f'saturation={y}'
            if x == 'gamma':
                self.contrast = f'gamma={y}'

        contrast = round(float(values.get('contrast', 1.0)) * 100 - 100)
        brightness = int(float(values.get('brightness', 0.0)) * 100)
        gamma = int(float(values.get('gamma', 0.0)) * 10)

        self.sld_contrast.SetValue(contrast)
        self.sld_bright.SetValue(brightness)
        self.sld_sat.SetValue(int(values.get('saturation', 0)))
        self.sld_gam.SetValue(gamma)
    # ------------------------------------------------------------------#

    def loader_edit(self, equalizer=''):
        """
        Loads edited StaticBitmap on panel 2
        """
        error = self.process(self.frameedit, equalizer=equalizer)
        if error:
            wx.MessageBox(f'{error}', 'ERROR', wx.ICON_ERROR, self)
            return
        bitmap = wx.Bitmap(self.frameedit)
        img = bitmap.ConvertToImage()
        img = img.Scale(self.w_ratio, self.h_ratio)
        bmp = img.ConvertToBitmap()
        self.bitmap_edit = wx.Bitmap(bmp)  # convert to bitmap
        # SetBitmap(self.bitmap_edit)  # set StaticBitmap
        wx.StaticBitmap(self.panel_img2, wx.ID_ANY, self.bitmap_edit)
    # ------------------------------------------------------------------#

    def concat_filter(self):
        """
        Concatenates all equalizers.
        Return an equalizer string in ffmpeg syntax.
        """
        orderf = (self.contrast, self.brightness, self.saturation, self.gamma)
        concat = ''.join([f'{x}:' for x in orderf if x])[:-1]
        if not concat:
            return concat
        return f'eq={concat}'
    # ------------------------------------------------------------------#

    def on_seek_time(self, event):
        """
        gets value from time slider, converts it to clock format
        e.g (00:00:00), and sets the label with the converted value.
        """
        seek = self.sld_time.GetValue()
        clock = milliseconds2clocksec(seek, rounds=True)  # to 24-hour
        self.txttime.SetLabel(clock)  # update StaticText
        if not self.btn_load.IsEnabled():
            self.btn_load.Enable()
    # ------------------------------------------------------------------------#

    def on_load_at_time(self, event):
        """
        Reloads all images frame at a given time clock point
        """
        seek = self.sld_time.GetValue()
        self.clock = milliseconds2clocksec(seek, rounds=True)  # to 24-hour
        error = self.process(self.framesrc)
        if error:
            wx.MessageBox(f'{error}', 'ERROR', wx.ICON_ERROR, self)
            return
        self.loader_initial_source()

        error = self.process(self.frameedit, self.concat_filter())
        if error:
            wx.MessageBox(f'{error}', 'ERROR', wx.ICON_ERROR, self)
            return
        self.loader_initial_edit()

        with open(self.filetime, "w", encoding='utf8') as atime:
            atime.write(self.clock)
        self.btn_load.Disable()
    # ------------------------------------------------------------------------#

    def on_contrast(self, event):
        """
        Scroll event for contrast eq.
        """
        val = 1.0 + self.sld_contrast.GetValue() / 100
        self.contrast = '' if val == 1.0 else f'contrast={val}'
        self.loader_edit(self.concat_filter())
    # ------------------------------------------------------------------#

    def on_brightness(self, event):
        """
        Scroll event for brightness eq.
        """
        val = 0.00 + self.sld_bright.GetValue() / 100
        self.brightness = '' if val == 0.00 else f'brightness={val}'
        self.loader_edit(self.concat_filter())
    # ------------------------------------------------------------------#

    def on_saturation(self, event):
        """
        Scroll event for saturation eq.
        """
        val = self.sld_sat.GetValue()
        self.saturation = '' if val == 0 else f'saturation={val}'
        self.loader_edit(self.concat_filter())
    # ------------------------------------------------------------------#

    def on_gamma(self, event):
        """
        Scroll event for gamma eq.
        """
        val = self.sld_gam.GetValue() / 10
        self.gamma = '' if val == 0 else f'gamma={val}'
        self.loader_edit(self.concat_filter())
    # ------------------------------------------------------------------#

    def on_reset(self, event):
        """
        Reset all control values
        """
        self.contrast = ""
        self.brightness = ""
        self.saturation = ""
        self.gamma = ""
        self.loader_edit(self.concat_filter())
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
        return self.concat_filter()
