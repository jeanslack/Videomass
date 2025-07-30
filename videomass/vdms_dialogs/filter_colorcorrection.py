# -*- coding: UTF-8 -*-
"""
Name: filter_colorcorrection.py
Porpose: Show dialog to set color correction data based on FFmpeg syntax
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: July.17.2023
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
import webbrowser
import wx
from videomass.vdms_utils.utils import time_to_integer
from videomass.vdms_utils.utils import integer_to_time
from videomass.vdms_utils.utils import clockset
from videomass.vdms_io.make_filelog import make_log_template
from videomass.vdms_threads.generic_task import FFmpegGenericTask


class ColorEQ(wx.Dialog):
    """
    A dialog tool to set video contrast, brightness,
    saturation, gamma values based on FFmpeg syntax.
    see docs at <https://ffmpeg.org/ffmpeg-filters.html#toc-eq>.
    See ``av_conversions.py`` -> ``on_Set_colorcorrect`` method
    for how to use this class.
    """
    get = wx.GetApp()
    OS = get.appset['ostype']
    LOGDIR = get.appset['logdir']
    TMPROOT = os.path.join(get.appset['cachedir'], 'tmp', 'ColorEQ')
    TMPSRC = os.path.join(TMPROOT, 'tmpsrc')
    TMPEDIT = os.path.join(TMPROOT, 'tmpedit')
    os.makedirs(TMPSRC, mode=0o777, exist_ok=True)
    os.makedirs(TMPEDIT, mode=0o777, exist_ok=True)
    # BACKGROUND = '#1b0413'

    def __init__(self, parent, colorset, iconreset, **kwa):
        """
        colorset: previus data already saved.
        width: source video width
        height: source video height
        fname: matches with the only one video file dragged
               into the list or the selected one if many.
        duration: Overall time duration of video.
        """
        self.filename = kwa['filename']
        name = os.path.splitext(os.path.basename(self.filename))[0]
        self.framesrc = os.path.join(ColorEQ.TMPSRC, f'{name}.png')
        self.frameedit = os.path.join(ColorEQ.TMPEDIT, f'{name}.png')
        self.fileclock = os.path.join(ColorEQ.TMPROOT, f'{name}.clock')
        # resizing values preserving aspect ratio for monitors
        thr = 150 if kwa['height'] > kwa['width'] else 270
        self.h_ratio = int((kwa['height'] / kwa['width']) * thr)
        self.w_ratio = int((kwa['width'] / kwa['height']) * self.h_ratio)
        self.contrast = ""
        self.brightness = ""
        self.saturation = ""
        self.gamma = ""
        tcheck = clockset(kwa['duration'], self.fileclock)
        self.clock = tcheck['duration']
        self.mills = tcheck['millis']

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        sizerpanels = wx.FlexGridSizer(2, 2, 2, 2)
        sizerBase.Add(sizerpanels, 0, wx.CENTER, 0)
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
        lab_imgedit = wx.StaticText(self, wx.ID_ANY,
                                    label=_("After"),
                                    style=wx.ST_NO_AUTORESIZE
                                    | wx.ALIGN_CENTRE_HORIZONTAL,
                                    )
        sizerpanels.Add(lab_imgedit, 0, wx.CENTER | wx.EXPAND)
        sizerBase.Add(10, 10)
        msg = _("Search for a specific frame")
        stboxtime = wx.StaticBox(self, wx.ID_ANY, msg)
        sizertime = wx.StaticBoxSizer(stboxtime, wx.HORIZONTAL)
        sizerBase.Add(sizertime, 0, wx.ALL | wx.CENTER, 5)
        self.sld_time = wx.Slider(self, wx.ID_ANY,
                                  time_to_integer(self.clock),
                                  0,
                                  1 if not self.mills else self.mills,
                                  size=(250, -1),
                                  style=wx.SL_HORIZONTAL,
                                  )
        sizertime.Add(self.sld_time, 0, wx.ALL | wx.CENTER, 5)
        self.txttime = wx.StaticText(self, wx.ID_ANY, self.clock)
        sizertime.Add(self.txttime, 0, wx.ALL | wx.CENTER, 5)
        self.btn_load = wx.Button(self, wx.ID_ANY, _("Load"))
        self.btn_load.Disable()
        sizertime.Add(self.btn_load, 0, wx.ALL | wx.CENTER, 5)
        boxcolor = wx.StaticBox(self, wx.ID_ANY, (_("Color EQ")))
        sizercolor = wx.StaticBoxSizer(boxcolor, wx.VERTICAL)
        sizerBase.Add(sizercolor, 0, wx.ALL | wx.EXPAND, 5)
        sizerflex1 = wx.FlexGridSizer(0, 4, 0, 0)
        sizercolor.Add(sizerflex1, 0, wx.ALL | wx.CENTRE, 5)

        lbl_contrast = wx.StaticText(self, wx.ID_ANY, _('Contrast:'))
        sizerflex1.Add(lbl_contrast, 0, wx.ALIGN_CENTRE_VERTICAL
                       | wx.ALIGN_CENTRE_HORIZONTAL, 0)
        self.sld_contrast = wx.Slider(self, wx.ID_ANY, 0, -100, 100,
                                      size=(200, -1), style=wx.SL_HORIZONTAL
                                      | wx.SL_AUTOTICKS
                                      | wx.SL_LABELS,
                                      )
        self.sld_contrast.SetToolTip(_("-100 to +100, default value 0"))
        sizerflex1.Add(self.sld_contrast, 0, wx.LEFT
                       | wx.ALIGN_CENTRE_VERTICAL
                       | wx.ALIGN_CENTRE_HORIZONTAL, 10)

        lbl_brigh = wx.StaticText(self, wx.ID_ANY, _('Brightness:'))
        sizerflex1.Add(lbl_brigh, 0, wx.LEFT
                       | wx.ALIGN_CENTRE_VERTICAL
                       | wx.ALIGN_CENTRE_HORIZONTAL, 20)
        self.sld_brightness = wx.Slider(self, wx.ID_ANY, 0, -100, 100,
                                        size=(200, -1), style=wx.SL_HORIZONTAL
                                        | wx.SL_AUTOTICKS
                                        | wx.SL_LABELS,
                                        )
        self.sld_brightness.SetToolTip(_("-100 to +100, default value 0"))
        sizerflex1.Add(self.sld_brightness, 0, wx.LEFT
                       | wx.ALIGN_CENTRE_VERTICAL
                       | wx.ALIGN_CENTRE_HORIZONTAL, 10)
        line = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                             size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                             name=wx.StaticLineNameStr,
                             )
        sizercolor.Add(line, 0, wx.ALL | wx.EXPAND, 5)
        sizerflex2 = wx.FlexGridSizer(0, 4, 0, 0)
        lbl_sat = wx.StaticText(self, wx.ID_ANY, _('Saturation:'))
        sizerflex2.Add(lbl_sat, 0, wx.ALIGN_CENTRE_VERTICAL
                       | wx.ALIGN_CENTRE_HORIZONTAL, 0)
        self.sld_saturation = wx.Slider(self, wx.ID_ANY, 100, 0, 300,
                                        size=(200, -1), style=wx.SL_HORIZONTAL
                                        | wx.SL_AUTOTICKS
                                        | wx.SL_LABELS,
                                        )
        self.sld_saturation.SetToolTip(_("0 to 300, default value 100"))
        sizerflex2.Add(self.sld_saturation, 0, wx.LEFT
                       | wx.ALIGN_CENTRE_VERTICAL
                       | wx.ALIGN_CENTRE_HORIZONTAL, 10)
        lbl_gam = wx.StaticText(self, wx.ID_ANY, _('Gamma:'))
        sizerflex2.Add(lbl_gam, 0, wx.LEFT
                       | wx.ALIGN_CENTRE_VERTICAL
                       | wx.ALIGN_CENTRE_HORIZONTAL, 20)
        self.sld_gamma = wx.Slider(self, wx.ID_ANY, 10, 0, 100,
                                   size=(200, -1), style=wx.SL_HORIZONTAL
                                   | wx.SL_AUTOTICKS
                                   | wx.SL_LABELS,
                                   )
        self.sld_gamma.SetToolTip(_("0 to 100, default value 10"))
        sizerflex2.Add(self.sld_gamma, 0, wx.LEFT
                       | wx.ALIGN_CENTRE_VERTICAL
                       | wx.ALIGN_CENTRE_HORIZONTAL, 10)
        sizercolor.Add(sizerflex2, 0, wx.ALL | wx.CENTRE, 5)

        # ----- confirm buttons section
        gridbtns = wx.GridSizer(1, 2, 0, 0)
        gridhelp = wx.GridSizer(1, 1, 0, 0)
        btn_help = wx.Button(self, wx.ID_HELP, "")
        gridhelp.Add(btn_help, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridbtns.Add(gridhelp)
        boxaff = wx.BoxSizer(wx.HORIZONTAL)
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "")
        boxaff.Add(btn_cancel, 0)
        btn_ok = wx.Button(self, wx.ID_OK)
        boxaff.Add(btn_ok, 0, wx.LEFT, 5)
        btn_reset = wx.Button(self, wx.ID_ANY, _("Reset"))
        btn_reset.SetBitmap(iconreset, wx.LEFT)
        boxaff.Add(btn_reset, 0, wx.LEFT, 5)
        gridbtns.Add(boxaff, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=5)
        sizerBase.Add(gridbtns, 0, wx.EXPAND)

        # ----------------------Properties-----------------------#
        if ColorEQ.OS == 'Darwin':
            lab_imgsrc.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            lab_imgedit.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            lab_imgsrc.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            lab_imgedit.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self.SetTitle(_("Color Correction EQ Tool"))
        # ----- Set layout
        self.SetSizer(sizerBase)
        sizerBase.Fit(self)
        self.Layout()
        # ----------------------Binding (EVT)-------------------------#

        self.Bind(wx.EVT_COMMAND_SCROLL, self.on_seek_time, self.sld_time)
        self.Bind(wx.EVT_BUTTON, self.on_load_at_time, self.btn_load)

        if ColorEQ.OS == 'Windows':
            self.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.on_contrast,
                      self.sld_contrast)
            self.Bind(wx.EVT_SCROLL_CHANGED, self.on_contrast,
                      self.sld_contrast)
            self.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.on_brightness,
                      self.sld_brightness)
            self.Bind(wx.EVT_SCROLL_CHANGED, self.on_brightness,
                      self.sld_brightness)
            self.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.on_saturation,
                      self.sld_saturation)
            self.Bind(wx.EVT_SCROLL_CHANGED, self.on_saturation,
                      self.sld_saturation)
            self.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.on_gamma,
                      self.sld_gamma)
            self.Bind(wx.EVT_SCROLL_CHANGED, self.on_gamma, self.sld_gamma)

        if ColorEQ.OS == 'Darwin':
            self.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.on_contrast,
                      self.sld_contrast)
            self.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.on_brightness,
                      self.sld_brightness)
            self.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.on_saturation,
                      self.sld_saturation)
            self.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.on_gamma,
                      self.sld_gamma)

        else:
            self.Bind(wx.EVT_SCROLL_CHANGED, self.on_contrast,
                      self.sld_contrast)
            self.Bind(wx.EVT_SCROLL_CHANGED, self.on_brightness,
                      self.sld_brightness)
            self.Bind(wx.EVT_SCROLL_CHANGED, self.on_saturation,
                      self.sld_saturation)
            self.Bind(wx.EVT_SCROLL_CHANGED, self.on_gamma, self.sld_gamma)

        self.Bind(wx.EVT_BUTTON, self.on_close, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)

        if not self.mills:
            self.sld_time.Disable()

        if colorset:  # previus values
            self.set_default(colorset)
        self.process(self.framesrc)
        self.loader_initial_source()
        self.equalize_image(self.concat_filter())
    # -----------------------------------------------------------------------#

    def process(self, pathtosave, equalizer=''):
        """
        Generate a new frame at the clock position using
        ffmpeg `eq` filter.
        """
        logfile = make_log_template('generic_task.log',
                                    ColorEQ.LOGDIR,
                                    mode="w",
                                    )
        if not self.mills:
            sseg = ''
        else:
            sseg = f'-ss {self.clock}'
        eql = '' if not equalizer else f'-vf "{equalizer}"'
        arg = (f'{sseg} -i "{self.filename}" -f image2 '
               f'-update 1 -frames:v 1 {eql} "{pathtosave}"')
        thread = FFmpegGenericTask(arg, 'ColorEQ', logfile)
        thread.join()  # wait end thread
        error = thread.status
        if error:
            return error
        return None
    # -----------------------------------------------------------------------#

    def loader_initial_source(self):
        """
        Loads initial StaticBitmaps on panels 1 (source).
        """
        img = wx.Image(self.framesrc, wx.BITMAP_TYPE_ANY)
        img = img.Scale(self.w_ratio, self.h_ratio, wx.IMAGE_QUALITY_NORMAL)
        bitmap = img.ConvertToBitmap()
        wx.StaticBitmap(self.panel_img1, wx.ID_ANY, bitmap)
    # -----------------------------------------------------------------------#

    def loader_initial_edit(self):
        """
        Loads initial StaticBitmaps on panels 2 (edit)
        """
        img = wx.Image(self.frameedit, wx.BITMAP_TYPE_ANY)
        img = img.Scale(self.w_ratio, self.h_ratio, wx.IMAGE_QUALITY_NORMAL)
        bitmap = img.ConvertToBitmap()
        wx.StaticBitmap(self.panel_img2, wx.ID_ANY, bitmap)
    # -----------------------------------------------------------------------#

    def set_default(self, colorset):
        """
        Set previus setting stored on `colorset` data.
        """
        filterlist = colorset.split(':')
        filterlist[0] = filterlist[0].split(sep='=', maxsplit=1)[1]
        eqval = dict(x.split('=') for x in filterlist)
        # set attributes strings if eqval has keys else as init ("")
        for key, val in eqval.items():
            if key == 'contrast':
                self.contrast = f'contrast={val}'
            if key == 'brightness':
                self.brightness = f'brightness={val}'
            if key == 'saturation':
                self.saturation = f'saturation={val}'
            if key == 'gamma':
                self.gamma = f'gamma={val}'

        # compute to sliders values (int)
        contrast = round((float(eqval.get('contrast', 1.0)) * 100 - 100) / 2)
        brightness = int(float(eqval.get('brightness', 0.0)) * 100)
        saturation = int(float(eqval.get('saturation', 1.0)) * 100)
        gamma = int(float(eqval.get('gamma', 1.0)) * 10)
        # set sliders
        self.sld_contrast.SetValue(contrast)
        self.sld_brightness.SetValue(brightness)
        self.sld_saturation.SetValue(saturation)
        self.sld_gamma.SetValue(gamma)
    # -----------------------------------------------------------------------#

    def equalize_image(self, equalizer=''):
        """
        Sends the equalization values to the process
        """
        error = self.process(self.frameedit, equalizer=equalizer)
        if error:
            wx.MessageBox(f'{error}', _('Videomass - Error!'),
                          wx.ICON_ERROR, self)
            return
        self.loader_initial_edit()
    # -----------------------------------------------------------------------#

    def concat_filter(self):
        """
        Concatenates all EQ values.
        Returns the EQ filter string in ffmpeg syntax.
        """
        orderf = (self.contrast, self.brightness, self.saturation, self.gamma)
        concat = ''.join([f'{x}:' for x in orderf if x])[:-1]
        if not concat:
            return concat
        return f'eq={concat}'
    # -----------------------------------------------------------------------#

    def on_seek_time(self, event):
        """
        Event to get slider position.
        Getting the value in ms from the time slider,
        converts it to clock format e.g (00:00:00),
        and sets the label with the converted value.
        """
        seek = self.sld_time.GetValue()
        clock = integer_to_time(seek, False)  # to 24-hour
        self.txttime.SetLabel(clock)  # update StaticText
        if not self.btn_load.IsEnabled():
            self.btn_load.Enable()
    # -----------------------------------------------------------------------#

    def on_load_at_time(self, event):
        """
        Reloads all images frame at a given time clock point
        """
        seek = self.sld_time.GetValue()
        self.clock = integer_to_time(seek, False)  # to 24-hour
        error = self.process(self.framesrc)
        if error:
            wx.MessageBox(f'{error}', _('Videomass - Error!'),
                          wx.ICON_ERROR, self)
            return
        self.loader_initial_source()

        error = self.process(self.frameedit, self.concat_filter())
        if error:
            wx.MessageBox(f'{error}', _('Videomass - Error!'),
                          wx.ICON_ERROR, self)
            return
        self.loader_initial_edit()

        with open(self.fileclock, "w", encoding='utf-8') as atime:
            atime.write(self.clock)
        self.btn_load.Disable()
    # -----------------------------------------------------------------------#

    def on_contrast(self, event):
        """
        Scroll event for contrast EQ.
        Set the contrast expression. The value must be a float
        value in range -1000.0 to 1000.0. The default value is "1".
        """
        val = 1.0 + self.sld_contrast.GetValue() / 50
        self.contrast = "" if val == 1.0 else f'contrast={val}'
        self.equalize_image(self.concat_filter())
    # -----------------------------------------------------------------------#

    def on_brightness(self, event):
        """
        Scroll event for brightness EQ.
        Set the brightness expression. The value must be a float
        value in range -1.0 to 1.0. The default value is "0".
        """
        val = 0.0 + self.sld_brightness.GetValue() / 100
        self.brightness = "" if val == 0.0 else f'brightness={val}'
        self.equalize_image(self.concat_filter())
    # -----------------------------------------------------------------------#

    def on_saturation(self, event):
        """
        Scroll event for saturation EQ.
        Set the saturation expression. The value must be a float
        in range 0.0 to 3.0. The default value is "1".
        """
        val = 0.0 + self.sld_saturation.GetValue() / 100
        self.saturation = "" if val == 1.0 else f'saturation={val}'
        self.equalize_image(self.concat_filter())
    # -----------------------------------------------------------------------#

    def on_gamma(self, event):
        """
        Scroll event for gamma EQ.
        Set the gamma expression. The value must be a float
        in range 0.1 to 10.0. The default value is "1".
        """
        val = self.sld_gamma.GetValue() / 10
        self.gamma = "" if val == 1.0 else f'gamma={val}'
        self.equalize_image(self.concat_filter())
    # -----------------------------------------------------------------------#

    def on_reset(self, event):
        """
        Reset all control values
        """
        self.contrast = ""
        self.brightness = ""
        self.saturation = ""
        self.gamma = ""
        self.sld_contrast.SetValue(0)
        self.sld_brightness.SetValue(0)
        self.sld_saturation.SetValue(100)
        self.sld_gamma.SetValue(10)
        self.equalize_image(self.concat_filter())
    # -----------------------------------------------------------------------#

    def on_help(self, event):
        """
        Open default web browser via Python Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>

        """
        page = ('https://jeanslack.github.io/Videomass/User-guide/'
                'Video_filters_en.pdf#%5B%7B%22num%22%3A40%2C%22gen'
                '%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2C56.7%2C625.'
                '389%2C0%5D')

        webbrowser.open(page)
    # -----------------------------------------------------------------------#

    def on_close(self, event):
        """
        Close this dialog without saving anything.
        Don't use self.Destroy() here, it is used by the caller
        """
        event.Skip()
    # -----------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Before destroying the dialog getvalue() will be called.
        Don't use self.Destroy() here, it is used by the caller
        """
        event.Skip()
    # -----------------------------------------------------------------------#

    def getvalue(self):
        """
        This method return values via the getvalue() interface
        from the caller. See the caller for more info and usage.
        """
        return self.concat_filter()
