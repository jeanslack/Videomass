# -*- coding: UTF-8 -*-
"""
Name: filter_scale.py
Porpose: Show dialog to get scale data based on FFmpeg syntax
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.21.2024
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
import time
import webbrowser
import wx
from videomass.vdms_io import io_tools
from videomass.vdms_dialogs.widget_utils import NormalTransientPopup
from videomass.vdms_threads.generic_task import FFmpegGenericTask
from videomass.vdms_utils.utils import time_to_integer
from videomass.vdms_utils.utils import integer_to_time
from videomass.vdms_io.make_filelog import make_log_template


class Scale(wx.Dialog):
    """
    A dialog tool to get scale, setdar and setsar video filters
    data based on FFmpeg syntax.

    """
    LGREEN = '#52ee7d'
    BLACK = '#1f1f1f'
    get = wx.GetApp()
    appdata = get.appset
    LOGDIR = appdata['logdir']
    TMPROOT = os.path.join(appdata['cachedir'], 'tmp', 'Scale')
    TMPSRC = os.path.join(TMPROOT, 'tmpsrc')
    os.makedirs(TMPSRC, mode=0o777, exist_ok=True)

    def __init__(self, parent, *args, **kwa):
        """
        setdar and setsar values only will be returned if `Constrain
        proportions` is not checked. All strings with "0" will disable
        any related filter even in reference to a single value.

        """
        self.width = "0"
        self.height = "0"
        self.darNum = "0"
        self.darDen = "0"
        self.sarNum = "0"
        self.sarDen = "0"
        self.filename = kwa['filename']  # selected filename on file list
        name = os.path.splitext(os.path.basename(self.filename))[0]
        self.frame = os.path.join(f'{Scale.TMPSRC}', f'{name}.png')  # image
        self.mills = time_to_integer(kwa['duration'].split('.')[0])

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        grid_opt = wx.BoxSizer(wx.HORIZONTAL)
        sizerBase.Add(grid_opt, 0)
        btn_readme = wx.Button(self, wx.ID_ANY, _("Read me"), size=(-1, -1))
        btn_readme.SetBackgroundColour(wx.Colour(Scale.LGREEN))
        btn_readme.SetForegroundColour(wx.Colour(Scale.BLACK))
        grid_opt.Add(btn_readme, 0, wx.CENTER | wx.ALL, 5)

        btn_view = wx.Button(self, wx.ID_ANY, _("View result"))
        grid_opt.Add(btn_view, 0, wx.ALL, 5)
        # ----- Scale section:
        box_scale = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                      _("New size in pixels"))), wx.VERTICAL)
        sizerBase.Add(box_scale, 0, wx.ALL | wx.EXPAND, 5)
        Flex_scale = wx.FlexGridSizer(1, 4, 0, 0)
        box_scale.Add(Flex_scale, 0, wx.ALL | wx.CENTER, 5)
        label_width = wx.StaticText(self, wx.ID_ANY, (_("Width:")))
        Flex_scale.Add(label_width, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_scale_width = wx.SpinCtrl(self, wx.ID_ANY, "0",
                                            min=0, max=9000,
                                            style=wx.TE_PROCESS_ENTER
                                            | wx.SP_ARROW_KEYS
                                            )
        Flex_scale.Add(self.spin_scale_width, 0, wx.ALL
                       | wx.ALIGN_CENTER_VERTICAL, 5
                       )
        label_height = wx.StaticText(self, wx.ID_ANY, (_("Height:")))
        Flex_scale.Add(label_height, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_scale_height = wx.SpinCtrl(self, wx.ID_ANY, "0",
                                             min=0, max=9000,
                                             style=wx.TE_PROCESS_ENTER
                                             | wx.SP_ARROW_KEYS
                                             )
        Flex_scale.Add(self.spin_scale_height, 0, wx.ALL
                       | wx.ALIGN_CENTER_VERTICAL, 5
                       )
        dim = _("Source size: {0} x {1} pixels").format(kwa['width'],
                                                        kwa['height'])
        label_sdim = wx.StaticText(self, wx.ID_ANY, dim)
        box_scale.Add(label_sdim, 0, wx.BOTTOM | wx.CENTER, 10)
        # ----- options
        box_scale.Add((5, 5))
        lab = _("Constrain proportions (keep aspect ratio)")
        self.ckbx_keep = wx.CheckBox(self, wx.ID_ANY, lab)
        box_scale.Add(self.ckbx_keep, 0, wx.CENTER, 0)
        # grid_opt.Add((30, 0), 0, wx.ALL, 5)
        self.rdb_scale = wx.RadioBox(self, wx.ID_ANY,
                                     (_("Which dimension to adjust?")),
                                     choices=[_("Width"), _("Height")],
                                     majorDimension=1,
                                     style=wx.RA_SPECIFY_ROWS
                                     )
        self.rdb_scale.Disable()
        box_scale.Add(self.rdb_scale, 0, wx.ALL | wx.CENTER, 10)
        # ----- setdar section:
        sizerBase.Add((15, 0), 0, wx.ALL, 5)
        sbox = wx.StaticBox(self, wx.ID_ANY, (_("Aspect Ratio")))
        box_ar = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        sizerBase.Add(box_ar, 1, wx.ALL | wx.EXPAND, 5)
        lab1 = _("Setdar filter (display aspect ratio) example 16/9, 4/3 ")
        self.lab_dar = wx.StaticText(self, wx.ID_ANY, (lab1))
        box_ar.Add(self.lab_dar, 0, wx.ALL | wx.CENTRE, 5)
        Flex_dar = wx.FlexGridSizer(1, 5, 0, 0)
        box_ar.Add(Flex_dar, 0, wx.ALL | wx.CENTRE, 5)
        self.label_num = wx.StaticText(self, wx.ID_ANY, (_("Numerator")))
        Flex_dar.Add(self.label_num, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_setdarNum = wx.SpinCtrl(self, wx.ID_ANY,
                                          "0", min=0, max=99,
                                          style=wx.TE_PROCESS_ENTER
                                          | wx.SP_ARROW_KEYS,
                                          size=(-1, -1)
                                          )
        Flex_dar.Add(self.spin_setdarNum, 0, wx.ALL
                     | wx.ALIGN_CENTER_VERTICAL, 5
                     )
        self.label_sepdar = wx.StaticText(self, wx.ID_ANY, ("/"))
        self.label_sepdar.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL,
                                  wx.BOLD, 0, ""))
        Flex_dar.Add(self.label_sepdar, 0, wx.ALL
                     | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_setdarDen = wx.SpinCtrl(self, wx.ID_ANY, "0",
                                          min=0, max=99,
                                          style=wx.TE_PROCESS_ENTER
                                          | wx.SP_ARROW_KEYS,
                                          size=(-1, -1)
                                          )
        Flex_dar.Add(self.spin_setdarDen, 0, wx.ALL
                     | wx.ALIGN_CENTER_VERTICAL, 5
                     )
        self.label_den = wx.StaticText(self, wx.ID_ANY, (_("Denominator")))
        Flex_dar.Add(self.label_den, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        # ----- setsar section:
        box_ar.Add((15, 0), 0, wx.ALL, 5)
        lab2 = _("Setsar filter (sample aspect ratio) example 1/1")
        self.lab_sar = wx.StaticText(self, wx.ID_ANY, (lab2))
        box_ar.Add(self.lab_sar, 0, wx.ALL | wx.CENTRE, 5)
        Flex_sar = wx.FlexGridSizer(1, 5, 0, 0)
        box_ar.Add(Flex_sar, 0, wx.ALL | wx.CENTRE, 5)
        self.label_num1 = wx.StaticText(self, wx.ID_ANY, (_("Numerator")))
        Flex_sar.Add(self.label_num1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_setsarNum = wx.SpinCtrl(self, wx.ID_ANY, "0",
                                          min=0, max=99,
                                          style=wx.TE_PROCESS_ENTER
                                          | wx.SP_ARROW_KEYS,
                                          size=(-1, -1)
                                          )
        Flex_sar.Add(self.spin_setsarNum, 0, wx.ALL
                     | wx.ALIGN_CENTER_VERTICAL, 5
                     )
        self.label_sepsar = wx.StaticText(self, wx.ID_ANY, ("/"))
        self.label_sepsar.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL,
                                  wx.BOLD, 0, ""))
        Flex_sar.Add(self.label_sepsar, 0, wx.ALL
                     | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_setsarDen = wx.SpinCtrl(self, wx.ID_ANY, "0",
                                          min=0, max=99,
                                          style=wx.TE_PROCESS_ENTER
                                          | wx.SP_ARROW_KEYS,
                                          size=(-1, -1)
                                          )
        Flex_sar.Add(self.spin_setsarDen, 0, wx.ALL
                     | wx.ALIGN_CENTER_VERTICAL, 5
                     )
        self.label_den1 = wx.StaticText(self, wx.ID_ANY, (_("Denominator")))
        Flex_sar.Add(self.label_den1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

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
        btn_reset.SetBitmap(args[3], wx.LEFT)
        boxaff.Add(btn_reset, 0, wx.LEFT, 5)
        gridbtns.Add(boxaff, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=5)
        sizerBase.Add(gridbtns, 0, wx.EXPAND)

        # ----- Properties
        self.SetTitle(_("Resize Tool"))
        scale_str = _('Scale filter, set to 0 to disable')
        self.spin_scale_width.SetToolTip(scale_str)
        self.spin_scale_height.SetToolTip(scale_str)
        setdar_str = _('Display Aspect Ratio. Set to 0 to disable')
        self.spin_setdarNum.SetToolTip(setdar_str)
        self.spin_setdarDen.SetToolTip(setdar_str)
        setsar_str = (_('Sample (aka Pixel) Aspect Ratio.\nSet to 0 '
                        'to disable'))
        self.spin_setsarNum.SetToolTip(setsar_str)
        self.spin_setsarDen.SetToolTip(setsar_str)

        if Scale.appdata['ostype'] == 'Darwin':
            label_sdim.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            label_sdim.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            self.lab_dar.SetLabelMarkup(f"<b>{lab1}</b>")
            self.lab_sar.SetLabelMarkup(f"<b>{lab2}</b>")

        # ----- Set Layout:
        self.SetSizer(sizerBase)
        sizerBase.Fit(self)
        self.Layout()

        # ----------------------Binding (EVT)--------------------------#
        self.Bind(wx.EVT_BUTTON, self.on_image_viewer, btn_view)
        self.Bind(wx.EVT_CHECKBOX, self.on_constrain, self.ckbx_keep)
        self.Bind(wx.EVT_RADIOBOX, self.on_dimension, self.rdb_scale)
        self.Bind(wx.EVT_BUTTON, self.on_readme, btn_readme)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)

        # Set previous changes
        if args[0]:  # scale
            self.width = args[0].split(':', maxsplit=1)[0][8:]
            self.height = args[0].split(':', maxsplit=1)[1][2:]

            if self.width in ('-1', '-2'):
                self.ckbx_keep.SetValue(True)
                self.rdb_scale.Enable()
                self.rdb_scale.SetSelection(1)
                self.keep_aspect_ratio_on()
                self.on_dimension(self)
            elif self.height in ('-1', '-2'):
                self.ckbx_keep.SetValue(True)
                self.rdb_scale.Enable()
                self.rdb_scale.SetSelection(0)
                self.keep_aspect_ratio_on()
                self.on_dimension(self)

            self.spin_scale_width.SetValue(self.width)
            self.spin_scale_height.SetValue(self.height)

        if args[1]:  # dar
            self.darNum = args[1].split('/')[0][7:]
            self.darDen = args[1].split('/')[1]
            self.spin_setdarNum.SetValue(int(self.darNum))
            self.spin_setdarDen.SetValue(int(self.darDen))
        if args[2]:  # sar
            self.sarNum = args[2].split('/')[0][7:]
            self.sarDen = args[2].split('/')[1]
            self.spin_setsarNum.SetValue(int(self.sarNum))
            self.spin_setsarDen.SetValue(int(self.sarDen))

        scaledata = {"scale": args[0], "sedar": args[1], "setsar": args[2]}
        concat = self.concat_filter(scaledata)
        error = self.process(concat)
        if error:
            wx.MessageBox(f'{error}', _('Videomass - Error!'),
                          wx.ICON_ERROR, self)

    def keep_aspect_ratio_on(self):
        """
        Reset the setdar and setsar filters and disable them
        """
        self.spin_setdarNum.SetValue(0)
        self.spin_setdarDen.SetValue(0)
        self.spin_setdarNum.Disable()
        self.spin_setdarDen.Disable()
        self.lab_dar.Disable()
        self.label_num.Disable()
        self.label_sepdar.Disable()
        self.label_den.Disable()
        self.spin_setsarNum.SetValue(0)
        self.spin_setsarDen.SetValue(0)
        self.spin_setsarNum.Disable()
        self.spin_setsarDen.Disable()
        self.lab_sar.Disable()
        self.label_num1.Disable()
        self.label_sepsar.Disable()
        self.label_den1.Disable()

    def keep_aspect_ratio_off(self):
        """
        Re-enable the setdar and setsar filters
        """
        self.spin_setdarNum.Enable()
        self.spin_setdarDen.Enable()
        self.lab_dar.Enable()
        self.label_num.Enable()
        self.label_sepdar.Enable()
        self.label_den.Enable()
        self.spin_setsarNum.Enable()
        self.spin_setsarDen.Enable()
        self.lab_sar.Enable()
        self.label_num1.Enable()
        self.label_sepsar.Enable()
        self.label_den1.Enable()

    def concat_filter(self, scaledata):
        """
        Concatenates `scale` options values.
        Returns the `scale` filter string in ffmpeg syntax.
        """
        orderf = list(scaledata.values())
        concat = ''.join([f'{x},' for x in orderf if x])[:-1]
        return concat

    def process(self, concat):
        """
        Generate a new frame at the clock position using the scale
        filter. Note that the trim start point on this process is
        set to the total length of the movie divided by two.
        """
        logfile = make_log_template('generic_task.log',
                                    Scale.LOGDIR,
                                    mode="w",
                                    )
        if not self.mills:
            sseg = ''
        else:
            stime = integer_to_time(int(self.mills / 2), False)
            sseg = f'-ss {stime}'
        scale = '' if not concat else f'-vf "{concat}"'
        arg = (f'{sseg} -i "{self.filename}" -f image2 -update 1 '
               f'-frames:v 1 {scale} "{self.frame}"')
        thread = FFmpegGenericTask(arg, 'Scale', logfile)
        error = thread.status
        if error:
            return error
        return None
    # ----------------------Event handler (callback)---------------------#

    def on_readme(self, event):
        """
        event on button help
        """
        msg = (_('If you want to keep the aspect ratio, select "Constrain '
                 'proportions" below and\nspecify only one dimension, either '
                 'width or height, and set the other dimension\nto -1 or -2 '
                 '(some codecs require -2, so you should do some testing '
                 'first).'))
        win = NormalTransientPopup(self,
                                   wx.SIMPLE_BORDER,
                                   msg,
                                   Scale.LGREEN,
                                   Scale.BLACK)

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = event.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Popup()
    # --------------------------------------------------------------#

    def on_image_viewer(self, event):
        """
        Open the image file (frame) with default OS image viewer.
        """
        concat = self.concat_filter(self.getvalue())
        error = self.process(concat)
        if error:
            wx.MessageBox(f'{error}', _('Videomass - Error!'),
                          wx.ICON_ERROR, self)
            return

        if os.path.exists(self.frame) and os.path.isfile(self.frame):
            time.sleep(0.5)  # to ensure correct size in default image viewer
            io_tools.openpath(self.frame)
    # ------------------------------------------------------------------#

    def on_constrain(self, event):
        """
        Evaluate CheckBox status
        """
        if self.ckbx_keep.IsChecked():
            self.keep_aspect_ratio_on()
            self.rdb_scale.Enable()
        else:
            self.keep_aspect_ratio_off()
            self.rdb_scale.Disable()

        self.on_dimension(self)
    # ------------------------------------------------------------------#

    def on_dimension(self, event):
        """
        Set the scaling controls according to RadioBox choices
        """
        if self.rdb_scale.IsEnabled():
            if self.rdb_scale.GetSelection() == 0:
                self.spin_scale_height.SetMin(-2)
                self.spin_scale_height.SetMax(-1)
                self.spin_scale_width.SetMin(0)
                self.spin_scale_width.SetMax(9000)

            elif self.rdb_scale.GetSelection() == 1:
                self.spin_scale_width.SetMin(-2)
                self.spin_scale_width.SetMax(-1)
                self.spin_scale_height.SetMax(9000)
                self.spin_scale_height.SetMin(0)
        else:
            self.spin_scale_width.SetMin(0)
            self.spin_scale_width.SetMax(9000)
            self.spin_scale_height.SetMin(0)
            self.spin_scale_height.SetMax(9000)
    # ------------------------------------------------------------------#

    def on_help(self, event):
        """
        Open default web browser via Python Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        page = ('https://jeanslack.github.io/Videomass/User-guide/'
                'Video_filters_en.pdf#%5B%7B%22num%22%3A10%2C%22gen%22%'
                '3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2C56.7%2C785.'
                '189%2C0%5D')

        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def on_reset(self, event):
        """
        Revert all controls to default
        """
        self.width, self.height = "0", "0"
        self.darNum, self.darDen = "0", "0"
        self.sarNum, self.sarDen = "0", "0"
        self.ckbx_keep.SetValue(False)
        self.on_constrain(self)
        self.spin_scale_width.SetValue(0)
        self.spin_scale_height.SetValue(0)
        self.spin_setdarNum.SetValue(0)
        self.spin_setdarDen.SetValue(0)
        self.spin_setsarNum.SetValue(0)
        self.spin_setsarDen.SetValue(0)
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
        This method return values via the getvalue() interface
        from the caller. See the caller for more info and usage.
        """
        diction = {'scale': '', 'setdar': '', 'setsar': ''}
        self.width = f'{self.spin_scale_width.GetValue()}'
        self.height = f'{self.spin_scale_height.GetValue()}'
        self.darNum = f'{self.spin_setdarNum.GetValue()}'
        self.darDen = f'{self.spin_setdarDen.GetValue()}'
        self.sarNum = f'{self.spin_setsarNum.GetValue()}'
        self.sarDen = f'{self.spin_setsarDen.GetValue()}'

        if self.width == '0' or self.height == '0':
            size = ''
        else:
            size = f'scale=w={self.width}:h={self.height}'
            diction['scale'] = size

        if self.darNum == '0' or self.darDen == '0':
            setdar = ''
        else:
            setdar = f'setdar={self.darNum}/{self.darDen}'
            diction['setdar'] = setdar

        if self.sarNum == '0' or self.sarDen == '0':
            setsar = ''
        else:
            setsar = f'setsar={self.sarNum}/{self.sarDen}'
            diction['setsar'] = setsar

        return diction
