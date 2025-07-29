# -*- coding: UTF-8 -*-
"""
Name: filter_stab.py
Porpose: Show dialog to get vidstab data based on FFmpeg syntax
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Apr.23.2024
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
import wx.lib.agw.floatspin as FS
from videomass.vdms_utils.utils import time_to_integer
from videomass.vdms_utils.utils import integer_to_time
from videomass.vdms_utils.utils import clockset
from videomass.vdms_io import io_tools
from videomass.vdms_threads.generic_task import FFmpegGenericTask
from videomass.vdms_dialogs.widget_utils import PopupDialog
from videomass.vdms_io.make_filelog import make_log_template


class VidstabSet(wx.Dialog):
    """
    A dialog tool to get vidstabdetect and vidstabtransform
    data based on FFmpeg syntax.

    """
    get = wx.GetApp()
    appdata = get.appset
    LOGDIR = appdata['logdir']
    TMPROOT = os.path.join(appdata['cachedir'], 'tmp', 'VidStab')
    TMPSRC = os.path.join(TMPROOT, 'tmpedit')
    os.makedirs(TMPSRC, mode=0o777, exist_ok=True)

    def __init__(self, parent, *args, **kwa):
        """
        parameters defined here:
        vidstabdetect parameters for pass one.
        vidstabtransform parameters for pass two
        unsharp parameters for pass two
        makeduo, to produce another video for comparison

        """
        self.vidstabdetect = args[0]
        self.vidstabtransform = args[1]
        self.unsharp = args[2]
        self.makeduo = args[3]

        self.filename = kwa['filename']
        name = os.path.splitext(os.path.basename(self.filename))[0]
        self.framesrc = os.path.join(VidstabSet.TMPSRC, f'{name}.mkv')
        self.frameduo = os.path.join(VidstabSet.TMPSRC, f'{name}_DUO.mkv')
        self.fileclock = os.path.join(VidstabSet.TMPROOT, f'{name}.clock')
        tcheck = clockset(kwa['duration'], self.fileclock)
        self.clock = tcheck['duration']
        self.mills = tcheck['millis']
        self.logfile = None
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        boxenable = wx.BoxSizer(wx.HORIZONTAL)
        sizerBase.Add(boxenable, 0, wx.CENTER, 5)
        self.ckbx_enable = wx.CheckBox(self, wx.ID_ANY,
                                       _('Enable stabilizer'))
        boxenable.Add(self.ckbx_enable, 0, wx.ALL | wx.CENTER, 2)
        self.ckbx_duo = wx.CheckBox(self, wx.ID_ANY, _('Create a side-by-side '
                                                       'comparison video'))
        boxenable.Add(self.ckbx_duo, 0, wx.ALL | wx.CENTER, 2)
        # preview
        sizerBase.Add((5, 5), 0)
        msg = _("Create a snapshot")
        stboxtime = wx.StaticBox(self, wx.ID_ANY, msg)
        sizertime = wx.StaticBoxSizer(stboxtime, wx.HORIZONTAL)
        sizerBase.Add(sizertime, 0, wx.EXPAND | wx.ALL, 5)

        boxtime = wx.BoxSizer(wx.HORIZONTAL)
        sizertime.Add(boxtime, 0, wx.ALL | wx.CENTER, 5)

        self.sld_time = wx.Slider(self, wx.ID_ANY,
                                  time_to_integer(self.clock),
                                  0,
                                  1 if not self.mills else self.mills,
                                  size=(250, -1),
                                  style=wx.SL_HORIZONTAL,
                                  )
        boxtime.Add(self.sld_time, 0, wx.CENTER, 0)
        self.lab_time = wx.StaticText(self, wx.ID_ANY, self.clock)
        boxtime.Add(self.lab_time, 0, wx.LEFT | wx.CENTER, 20)
        self.btn_snap = wx.Button(self, wx.ID_ANY, _("Preview"))
        self.btn_snap.Disable()
        boxtime.Add(self.btn_snap, 0, wx.LEFT | wx.CENTER, 20)
        self.lab_dur = wx.StaticText(self, wx.ID_ANY, _("Duration seconds:"))
        boxtime.Add(self.lab_dur, 0, wx.LEFT | wx.CENTER, 20)
        self.spin_dur = wx.SpinCtrl(self, wx.ID_ANY, "5",
                                    min=3, max=15,
                                    style=wx.TE_PROCESS_ENTER
                                    | wx.SP_ARROW_KEYS,
                                    )
        boxtime.Add(self.spin_dur, 0, wx.LEFT | wx.CENTER, 2)
        # Box detect
        sbox = wx.StaticBox(self, wx.ID_ANY, (_("Video Detect")))
        box_detect = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        sizerBase.Add(box_detect, 0, wx.ALL | wx.EXPAND, 5)
        Flex_detect1 = wx.FlexGridSizer(1, 6, 0, 0)
        box_detect.Add(Flex_detect1, 0, wx.ALL, 5)
        self.lab_shake = wx.StaticText(self, wx.ID_ANY, ("Shakiness:"))
        Flex_detect1.Add(self.lab_shake, 0, wx.RIGHT
                         | wx.ALIGN_CENTER_VERTICAL, 2
                         )
        self.spin_shake = wx.SpinCtrl(self, wx.ID_ANY, "5",
                                      min=1, max=10,
                                      style=wx.TE_PROCESS_ENTER
                                      | wx.SP_ARROW_KEYS
                                      )
        Flex_detect1.Add(self.spin_shake, 0, wx.RIGHT
                         | wx.ALIGN_CENTER_VERTICAL, 15
                         )
        self.lab_accuracy = wx.StaticText(self, wx.ID_ANY, ("Accuracy:"))
        Flex_detect1.Add(self.lab_accuracy, 0, wx.RIGHT
                         | wx.ALIGN_CENTER_VERTICAL, 2
                         )
        self.spin_accuracy = wx.SpinCtrl(self, wx.ID_ANY, "15",
                                         min=1, max=15,
                                         style=wx.TE_PROCESS_ENTER
                                         | wx.SP_ARROW_KEYS
                                         )
        Flex_detect1.Add(self.spin_accuracy, 0, wx.RIGHT
                         | wx.ALIGN_CENTER_VERTICAL, 15
                         )
        self.lab_stepsize = wx.StaticText(self, wx.ID_ANY, ("Stepsize:"))
        Flex_detect1.Add(self.lab_stepsize, 0, wx.RIGHT
                         | wx.ALIGN_CENTER_VERTICAL, 2
                         )
        self.spin_stepsize = wx.SpinCtrl(self, wx.ID_ANY, "6",
                                         min=1, max=10000,
                                         style=wx.TE_PROCESS_ENTER
                                         | wx.SP_ARROW_KEYS
                                         )
        Flex_detect1.Add(self.spin_stepsize, 0, wx.RIGHT
                         | wx.ALIGN_CENTER_VERTICAL, 15
                         )
        Flex_detect2 = wx.FlexGridSizer(1, 4, 0, 0)
        box_detect.Add(Flex_detect2, 0, wx.ALL, 5)
        self.lab_mincontr = wx.StaticText(self, wx.ID_ANY, ("Mincontrast:"))
        Flex_detect2.Add(self.lab_mincontr, 0, wx.RIGHT
                         | wx.ALIGN_CENTER_VERTICAL, 2)
        self.spin_mincontr = FS.FloatSpin(self, wx.ID_ANY,
                                          min_val=0, max_val=1,
                                          increment=0.01, value=0.25,
                                          agwStyle=FS.FS_LEFT,
                                          size=(120, -1),
                                          )
        self.spin_mincontr.SetFormat("%f")
        self.spin_mincontr.SetDigits(2)
        Flex_detect2.Add(self.spin_mincontr, 0, wx.RIGHT
                         | wx.ALIGN_CENTER_VERTICAL, 15
                         )
        Flex_detect2.Add((15, 0), 0, wx.ALL, 5)
        lab = _("[TRIPOD] Enable tripod mode if checked")
        self.ckbx_tripod1 = wx.CheckBox(self, wx.ID_ANY, lab)
        Flex_detect2.Add(self.ckbx_tripod1, 0, wx.ALL
                         | wx.ALIGN_CENTER_VERTICAL, 5
                         )
        # Box transform
        sizerBase.Add((15, 0), 0, wx.ALL, 5)
        sbox = wx.StaticBox(self, wx.ID_ANY, (_("Video transform")))
        box_trans = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        sizerBase.Add(box_trans, 1, wx.ALL | wx.EXPAND, 5)
        flex_trans1 = wx.FlexGridSizer(1, 5, 0, 0)
        box_trans.Add(flex_trans1, 0, wx.ALL, 5)
        self.lab_smooth = wx.StaticText(self, wx.ID_ANY, ("Smoothing:"))
        flex_trans1.Add(self.lab_smooth, 0, wx.RIGHT
                        | wx.ALIGN_CENTER_VERTICAL, 2
                        )
        self.spin_smooth = wx.SpinCtrl(self, wx.ID_ANY, "15",
                                       min=0, max=30,
                                       style=wx.TE_PROCESS_ENTER
                                       | wx.SP_ARROW_KEYS,
                                       size=(-1, -1),
                                       )
        flex_trans1.Add(self.spin_smooth, 0, wx.RIGHT
                        | wx.ALIGN_CENTER_VERTICAL, 15
                        )
        self.rdb_optalgo = wx.RadioBox(self, wx.ID_ANY,
                                       (_("[OPTALGO] optimization algorithm")),
                                       choices=[("gauss"), ("avg")],
                                       majorDimension=1,
                                       style=wx.RA_SPECIFY_ROWS,
                                       )
        flex_trans1.Add(self.rdb_optalgo, 0, wx.RIGHT
                        | wx.ALIGN_CENTER_VERTICAL, 15
                        )
        self.lab_maxangle = wx.StaticText(self, wx.ID_ANY, ("Maxangle:"))
        flex_trans1.Add(self.lab_maxangle, 0, wx.RIGHT
                        | wx.ALIGN_CENTER_VERTICAL, 2
                        )
        self.spin_maxangle = wx.SpinCtrl(self, wx.ID_ANY, "-1",
                                         min=-1, max=360,
                                         style=wx.TE_PROCESS_ENTER
                                         | wx.SP_ARROW_KEYS,
                                         size=(-1, -1),
                                         )
        flex_trans1.Add(self.spin_maxangle, 0, wx.RIGHT
                        | wx.ALIGN_CENTER_VERTICAL, 5
                        )
        self.rdb_crop = wx.RadioBox(self, wx.ID_ANY,
                                    (_("[CROP] Specify how to deal with "
                                        "borders at movement compensation")),
                                    choices=[("keep"), ("black")],
                                    majorDimension=1,
                                    style=wx.RA_SPECIFY_ROWS,
                                    )
        box_trans.Add(self.rdb_crop, 0, wx.ALL, 5)
        lab = _("[INVERT] Invert transforms if checked")
        self.ckbx_invert = wx.CheckBox(self, wx.ID_ANY, lab)
        box_trans.Add(self.ckbx_invert, 0, wx.ALL, 5)
        lab = _("[RELATIVE] Consider transforms as relative to previous "
                "frame if checked, absolute if unchecked")
        self.ckbx_relative = wx.CheckBox(self, wx.ID_ANY, lab)
        box_trans.Add(self.ckbx_relative, 0, wx.ALL, 5)
        flex_trans2 = wx.FlexGridSizer(1, 6, 0, 0)
        box_trans.Add(flex_trans2, 0, wx.ALL, 5)
        self.lab_zoom = wx.StaticText(self, wx.ID_ANY, ("Zoom:"))
        flex_trans2.Add(self.lab_zoom, 0, wx.RIGHT
                        | wx.ALIGN_CENTER_VERTICAL, 2
                        )
        self.spin_zoom = wx.SpinCtrl(self, wx.ID_ANY, "0",
                                     min=0, max=100,
                                     style=wx.TE_PROCESS_ENTER
                                     | wx.SP_ARROW_KEYS,
                                     size=(-1, -1),
                                     )
        flex_trans2.Add(self.spin_zoom, 0, wx.RIGHT
                        | wx.ALIGN_CENTER_VERTICAL, 15
                        )
        self.lab_optzoom = wx.StaticText(self, wx.ID_ANY, ("OptZoom:"))
        flex_trans2.Add(self.lab_optzoom, 0, wx.RIGHT
                        | wx.ALIGN_CENTER_VERTICAL, 2
                        )
        self.spin_optzoom = wx.SpinCtrl(self, wx.ID_ANY, "1",
                                        min=0, max=2,
                                        style=wx.TE_PROCESS_ENTER
                                        | wx.SP_ARROW_KEYS,
                                        size=(-1, -1),
                                        )
        flex_trans2.Add(self.spin_optzoom, 0, wx.RIGHT
                        | wx.ALIGN_CENTER_VERTICAL, 15
                        )
        self.lab_zoomspeed = wx.StaticText(self, wx.ID_ANY, ("Zoom speed:"))
        flex_trans2.Add(self.lab_zoomspeed, 0, wx.RIGHT
                        | wx.ALIGN_CENTER_VERTICAL, 2
                        )
        self.spin_zoomspeed = FS.FloatSpin(self, wx.ID_ANY,
                                           min_val=0, max_val=5,
                                           increment=0.05, value=0.25,
                                           agwStyle=FS.FS_LEFT, size=(120, -1)
                                           )
        self.spin_zoomspeed.SetFormat("%f")
        self.spin_zoomspeed.SetDigits(2)
        flex_trans2.Add(self.spin_zoomspeed, 0, wx.RIGHT, 5)
        self.rdb_interpol = wx.RadioBox(self, wx.ID_ANY,
                                        (_("Specify type of interpolation")),
                                        choices=[("no"), ("linear"),
                                                 ("bilinear"), ("bicubic")],
                                        majorDimension=1,
                                        style=wx.RA_SPECIFY_ROWS,
                                        )
        self.rdb_interpol.SetSelection(2)
        box_trans.Add(self.rdb_interpol, 0, wx.ALL, 5)
        lab = _("[TRIPOD2] virtual tripod mode, equivalent to "
                "relative=unchecked:smoothing=0")
        self.ckbx_tripod2 = wx.CheckBox(self, wx.ID_ANY, lab)
        box_trans.Add(self.ckbx_tripod2, 0, wx.ALL, 5)
        flex_trans3 = wx.FlexGridSizer(1, 2, 0, 0)
        box_trans.Add(flex_trans3, 0, wx.ALL, 5)
        self.lab_unsharp = wx.StaticText(self, wx.ID_ANY,
                                         (_("Unsharp filter:")))
        flex_trans3.Add(self.lab_unsharp, 0, wx.RIGHT
                        | wx.ALIGN_CENTER_VERTICAL, 2
                        )
        self.txt_unsharp = wx.TextCtrl(self, wx.ID_ANY,
                                       value="unsharp=5:5:0.8:3:3:0.4",
                                       size=(500, -1),
                                       )
        flex_trans3.Add(self.txt_unsharp, 0, wx.RIGHT
                        | wx.ALIGN_CENTER_VERTICAL, 5
                        )
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
        btn_reset.SetBitmap(args[4], wx.LEFT)
        boxaff.Add(btn_reset, 0, wx.LEFT, 5)
        gridbtns.Add(boxaff, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=5)
        sizerBase.Add(gridbtns, 0, wx.EXPAND)

        # ----- Set properties
        tip = _('Seek to a position on the video.')
        self.sld_time.SetToolTip(tip)
        tip = _('Make a snapshot of the video with the settings made.')
        self.btn_snap.SetToolTip(tip)
        tip = _('Set the snapshot duration from 3 to 15 seconds from '
                'the seek position, default is 5 seconds.')
        self.spin_dur.SetToolTip(tip)
        # vidstabdetect
        tip = _('Set how shaky the video is and how quick the camera is. A '
                'value of 1 means little shakiness, a value of 10 means '
                'strong shakiness. Default value is 5.')
        self.spin_shake.SetToolTip(tip)
        tip = _('Set the accuracy of the detection process. A value of 1 '
                'means low accuracy, a value of 15 means high accuracy. '
                'Default value is 15.')
        self.spin_accuracy.SetToolTip(tip)
        tip = _('Set stepsize of the search process. The region around '
                'minimum is scanned with 1 pixel resolution. Default value '
                'is 6.')
        self.spin_stepsize.SetToolTip(tip)
        tip = _('Set minimum contrast. Below this value a local measurement '
                'field is discarded. The range is 0-1. Default value is 0.25.')
        self.spin_mincontr.SetToolTip(tip)
        tip = _('Set reference frame number for tripod mode. If enabled, the '
                'motion of the frames is compared to a reference frame in '
                'the filtered stream, identified by the specified number. '
                'The idea is to compensate all movements in a more-or-less '
                'static scene and keep the camera view absolutely still. '
                'The frames are counted starting from 1.')
        self.ckbx_tripod1.SetToolTip(tip)

        # vidstabtransform
        tip = _('Set the number of frames (value*2 + 1) used for lowpass '
                'filtering the camera movements. Default value is 15. For '
                'example a number of 10 means that 21 frames are used (10 in '
                'the past and 10 in the future) to smoothen the motion in '
                'the video. A larger value leads to a smoother video, but '
                'limits the acceleration of the camera (pan/tilt movements). '
                '0 is a special case where a static camera is simulated.')
        self.spin_smooth.SetToolTip(tip)
        tip = _('Set the camera path optimization algorithm. Values are: '
                '`gauss`: gaussian kernel low-pass filter on camera motion '
                '(default), and `avg`: averaging on transformations')
        self.rdb_optalgo.SetToolTip(tip)
        tip = _('Set maximal angle in radians (degree*PI/180) to rotate '
                'frames. Default value is -1, meaning no limit.')
        self.spin_maxangle.SetToolTip(tip)
        tip = _('Specify how to deal with borders that may be visible due to '
                'movement compensation. Values are: `keep` keep image '
                'information from previous frame (default), `black` fill the '
                'border black')
        self.rdb_crop.SetToolTip(tip)
        tip = _('Invert transforms if checked. Default is unchecked.')
        self.ckbx_invert.SetToolTip(tip)
        tip = _('Consider transforms as relative to previous frame if '
                'checked, absolute if unchecked. Default is checked.')
        self.ckbx_relative.SetToolTip(tip)
        tip = _('Set percentage to zoom. A positive value will result in a '
                'zoom-in effect, a negative value in a zoom-out effect. '
                'Default value is 0 (no zoom).')
        self.spin_zoom.SetToolTip(tip)
        tip = _('Set optimal zooming to avoid borders. Accepted values are: '
                '`0` disabled, `1` optimal static zoom value is determined '
                '(only very strong movements will lead to visible borders) '
                '(default), `2` optimal adaptive zoom value is determined '
                '(no borders will be visible), see zoomspeed. Note that the '
                'value given at zoom is added to the one calculated here.')
        self.spin_optzoom.SetToolTip(tip)
        tip = _('Set percent to zoom maximally each frame (enabled when '
                'optzoom is set to 2). Range is from 0 to 5, default value '
                'is 0.25.')
        self.spin_zoomspeed.SetToolTip(tip)
        tip = _('Specify type of interpolation. Available values are: `no` '
                'no interpolation, `linear` linear only horizontal, '
                '`bilinear` linear in both directions (default), `bicubic` '
                'cubic in both directions (slow)')
        self.rdb_interpol.SetToolTip(tip)
        tip = _('Enable virtual tripod mode if checked, which is equivalent '
                'to relative=0:smoothing=0. Default is unchecked. Use also '
                'tripod option of vidstabdetect.')
        self.ckbx_tripod2.SetToolTip(tip)
        # unsharp filter
        tip = _('Sharpen or blur the input video. Note the use of the '
                'unsharp filter which is always recommended.')
        self.txt_unsharp.SetToolTip(tip)

        self.SetTitle(_("Video Stabilizer Tool"))

        # ----- Set layout
        self.SetSizer(sizerBase)
        sizerBase.Fit(self)
        self.Layout()

        # ----------------------Binding (EVT)--------------------------#
        self.Bind(wx.EVT_CHECKBOX, self.on_activate, self.ckbx_enable)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.on_seek_time, self.sld_time)
        self.Bind(wx.EVT_BUTTON, self.on_load_at_time, self.btn_snap)
        self.Bind(wx.EVT_SPINCTRL, self.on_optzoom, self.spin_optzoom)
        self.Bind(wx.EVT_CHECKBOX, self.on_Tripod1, self.ckbx_tripod1)
        self.Bind(wx.EVT_CHECKBOX, self.on_Tripod2, self.ckbx_tripod2)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.set_default, btn_reset)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)

        if self.vidstabdetect:
            self.set_values()  # Set previous changes
        else:
            self.set_default(self)
            self.on_activate(self)
    # ------------------------------------------------------------------#

    def concat_filter(self, orderf):
        """
        Concatenates all VidstabSet values.
        Returns the VidstabSet filter string in ffmpeg syntax.
        """
        concat = ''.join([f'{x},' for x in orderf if x])[:-1]
        if not concat:
            return concat
        return f'-vf {concat}'
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
        self.lab_time.SetLabel(clock)  # update StaticText
        if not self.btn_snap.IsEnabled():
            self.btn_snap.Enable()
    # ------------------------------------------------------------------#

    def on_load_at_time(self, event):
        """
        Reloads processes at a given time clock point
        """
        data = self.getvalue()
        detect = f'-vf {data[0]}'
        trasform = self.concat_filter((data[1], data[2]))
        self.logfile = make_log_template('generic_task.log',
                                         VidstabSet.LOGDIR,
                                         mode="w",
                                         )
        error = self.process(self.filename, args=detect, mode='detect')
        if error:
            wx.MessageBox(f'{error}', _('Videomass - Error!'),
                          wx.ICON_ERROR, self)
            return

        error = self.process(self.filename,
                             self.framesrc,
                             args=trasform,
                             mode='trasform',
                             )
        if error:
            wx.MessageBox(f'{error}', _('Videomass - Error!'),
                          wx.ICON_ERROR, self)
            return

        if self.ckbx_duo.IsChecked():
            error = self.process(self.filename,
                                 self.frameduo,
                                 args='',
                                 mode='makeduo',
                                 )
            if error:
                wx.MessageBox(f'{error}', _('Videomass - Error!'),
                              wx.ICON_ERROR, self)
                return
            io_tools.openpath(self.frameduo)
            return

        io_tools.openpath(self.framesrc)
        return
    # ------------------------------------------------------------------#

    def process(self, infile, outfile=None, args='', mode=None):
        """
        Generate a new frame at the clock position using
        ffmpeg `eq` filter.
        """
        if not self.mills:
            sseg, tseg = '', ''
        else:
            seek = self.sld_time.GetValue()
            stime = self.spin_dur.GetValue() * 1000
            if seek + stime > self.mills:
                seek = self.mills - stime
                if seek < 0:
                    seek, stime = 0, self.mills
            duration = integer_to_time(stime, False)  # to 24-hour
            self.clock = integer_to_time(seek, False)  # to 24-hour
            sseg = f'-ss {self.clock}.000'
            tseg = f'-t {duration}.000'

        if mode == 'detect':
            nul = ('NUL' if VidstabSet.appdata['ostype']
                   == 'Windows' else '/dev/null')
            argstr = f'{sseg} -i "{infile}" {tseg} {args} -f null {nul}'

        elif mode == 'trasform':
            argstr = f'{sseg} -i "{infile}" {tseg} {args} "{outfile}"'

        elif mode == 'makeduo':
            argstr = (f'{sseg} -i "{infile}" {tseg} -i "{self.framesrc}" '
                      f'{tseg} -filter_complex hstack "{outfile}"')
        else:
            return None

        thread = FFmpegGenericTask(argstr,
                                   procname=f'VidStab - {mode}',
                                   logfile=self.logfile,
                                   )
        caption = _("Videomass - Loading...")
        msg = _("Please wait,\nThis process will take a few seconds.")
        dlgload = PopupDialog(self, caption, msg)
        dlgload.ShowModal()
        thread.join()  # wait end thread
        error = thread.status
        if error:
            dlgload.Destroy()
            return error
        dlgload.Destroy()
        return None
    # ------------------------------------------------------------------#

    def set_default(self, event):
        """
        Revert all control values to default

        """
        # vidstabdetect
        self.spin_shake.SetValue('5')
        self.spin_accuracy.SetValue('15')
        self.spin_stepsize.SetValue('6')
        self.spin_mincontr.SetValue(0.25)
        self.ckbx_tripod1.SetValue(False)
        # vidstabtransform
        self.spin_smooth.SetValue('15')
        self.rdb_optalgo.SetSelection(0)
        self.spin_maxangle.SetValue('-1')
        self.rdb_crop.SetSelection(0)
        self.ckbx_invert.SetValue(False)
        self.ckbx_relative.SetValue(True)
        self.spin_zoom.SetValue('0')
        self.spin_optzoom.SetValue('1')
        self.spin_zoomspeed.SetValue(0.25)
        self.spin_zoomspeed.Disable()
        self.rdb_interpol.SetSelection(2)
        self.ckbx_tripod2.SetValue(False)
        self.ckbx_tripod2.Disable()
        # unsharp filter
        self.txt_unsharp.Clear()
        self.txt_unsharp.write('unsharp=5:5:0.8:3:3:0.4')
    # ------------------------------------------------------------------#

    def set_values(self):
        """
        set values previously confirmed

        """
        k_v_detect = dict(i.split('=') for i in self.vidstabdetect.split(
                          'vidstabdetect=')[1].split(':'))

        self.spin_shake.SetValue(k_v_detect['shakiness'])
        self.spin_accuracy.SetValue(k_v_detect['accuracy'])
        self.spin_stepsize.SetValue(k_v_detect['stepsize'])
        self.spin_mincontr.SetValue(float(k_v_detect['mincontrast']))
        if k_v_detect['tripod'] == '1':
            self.ckbx_tripod1.SetValue(True)
            self.ckbx_tripod2.SetValue(True)
            self.ckbx_tripod2.Enable()
        else:
            self.ckbx_tripod1.SetValue(False)
            self.ckbx_tripod2.SetValue(False)
            self.ckbx_tripod2.Disable()

        k_v_transf = dict(i.split('=') for i in self.vidstabtransform.split(
                          'vidstabtransform=')[1].split(':'))

        self.spin_smooth.SetValue(k_v_transf['smoothing'])
        if k_v_transf['optalgo'] == 'gauss':
            self.rdb_optalgo.SetSelection(0)
        else:
            self.rdb_optalgo.SetSelection(1)
        self.spin_maxangle.SetValue(k_v_transf['maxangle'])
        if k_v_transf['crop'] == 'keep':
            self.rdb_crop.SetSelection(0)
        else:
            self.rdb_crop.SetSelection(1)
        if k_v_transf['invert'] == '1':
            self.ckbx_invert.SetValue(True)
        else:
            self.ckbx_invert.SetValue(False)
        if k_v_transf['relative'] == '1':
            self.ckbx_relative.SetValue(True)
        else:
            self.ckbx_relative.SetValue(False)
        self.spin_zoom.SetValue(k_v_transf['zoom'])
        self.spin_optzoom.SetValue(k_v_transf['optzoom'])
        if k_v_transf['optzoom'] == '2':
            self.spin_zoomspeed.Enable()
            self.lab_zoomspeed.Enable()
        else:
            self.spin_zoomspeed.Disable()
            self.lab_zoomspeed.Disable()
        self.spin_zoomspeed.SetValue(float(k_v_transf['zoomspeed']))
        if k_v_transf['interpol'] == 'no':
            self.rdb_interpol.SetSelection(0)
        elif k_v_transf['interpol'] == 'linear':
            self.rdb_interpol.SetSelection(1)
        elif k_v_transf['interpol'] == 'bilinear':
            self.rdb_interpol.SetSelection(2)
        else:
            self.rdb_interpol.SetSelection(3)

        self.txt_unsharp.Clear()
        self.txt_unsharp.write(self.unsharp)
        self.ckbx_enable.SetValue(True)
        self.ckbx_duo.SetValue(self.makeduo)
        self.on_activate(self)

    # ----------------------Event handler (callback)---------------------#

    def on_optzoom(self, event):
        """
        If optzoom value is equal to 2, enable zoomspeed

        """
        if self.spin_optzoom.GetValue() == 2:
            self.spin_zoomspeed.Enable()
            self.lab_zoomspeed.Enable()
        else:
            self.spin_zoomspeed.SetValue(0.25)
            self.spin_zoomspeed.Disable()
            self.lab_zoomspeed.Disable()
    # ------------------------------------------------------------------#

    def on_Tripod1(self, event):
        """
        If self.ckbx_tripod1 is checked, enable and
        check self.ckbx_tripod2

        """
        if self.ckbx_tripod1.IsChecked():
            self.ckbx_tripod2.Enable()
            self.ckbx_tripod2.SetValue(True)
        else:
            self.ckbx_tripod2.Disable()
            self.ckbx_tripod2.SetValue(False)
    # ------------------------------------------------------------------#

    def on_Tripod2(self, event):
        """
        If self.ckbx_tripod2 is unchecked, disable it and
        uncheck self.ckbx_tripod1

        """
        if not self.ckbx_tripod2.IsChecked():
            self.ckbx_tripod1.SetValue(False)
            self.on_Tripod1(self)

    # ------------------------------------------------------------------#

    def on_help(self, event):
        """
        Open default web browser via Python Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>

        """
        page = ('https://jeanslack.github.io/Videomass/User-guide/'
                'Video_filters_en.pdf#%5B%7B%22num%22%3A28%2C%22gen'
                '%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2C56.7%2C785.'
                '189%2C0%5D')

        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def on_activate(self, event):
        """
        Enable or disable vidstab filter

        """
        if self.ckbx_enable.IsChecked():
            self.spin_shake.Enable()
            self.spin_accuracy.Enable()
            self.spin_stepsize.Enable()
            self.spin_mincontr.Enable()
            self.ckbx_tripod1.Enable()
            self.spin_smooth.Enable()
            self.rdb_optalgo.Enable()
            self.spin_maxangle.Enable()
            self.rdb_crop.Enable()
            self.ckbx_invert.Enable()
            self.ckbx_relative.Enable()
            self.spin_zoom.Enable()
            self.spin_optzoom.Enable()
            self.lab_shake.Enable()
            self.lab_accuracy.Enable()
            self.lab_stepsize.Enable()
            self.lab_mincontr.Enable()
            self.lab_smooth.Enable()
            self.lab_maxangle.Enable()
            self.lab_zoom.Enable()
            self.lab_optzoom.Enable()
            self.lab_unsharp.Enable()
            # self.spin_zoomspeed.Enable(), self.lab_zoomspeed.Enable()
            self.rdb_interpol.Enable()
            # self.ckbx_tripod2.Enable()
            self.txt_unsharp.Enable()
            self.ckbx_duo.Enable()
            # enable preview only if greater than 3 seconds
            if self.mills > 3000:
                self.btn_snap.Enable()
                self.sld_time.Enable()
                self.lab_time.Enable()
                self.lab_dur.Enable()
                self.spin_dur.Enable()
        else:
            self.spin_shake.Disable()
            self.spin_accuracy.Disable()
            self.spin_stepsize.Disable()
            self.spin_mincontr.Disable()
            self.ckbx_tripod1.Disable()
            self.spin_smooth.Disable()
            self.rdb_optalgo.Disable()
            self.spin_maxangle.Disable()
            self.rdb_crop.Disable()
            self.ckbx_invert.Disable()
            self.ckbx_relative.Disable()
            self.spin_zoom.Disable()
            self.spin_optzoom.Disable()
            self.spin_zoomspeed.Disable()
            self.rdb_interpol.Disable()
            self.ckbx_tripod2.Disable()
            self.txt_unsharp.Disable()
            self.lab_shake.Disable()
            self.lab_accuracy.Disable()
            self.lab_stepsize.Disable()
            self.lab_mincontr.Disable()
            self.lab_smooth.Disable()
            self.lab_maxangle.Disable()
            self.lab_zoom.Disable()
            self.lab_optzoom.Disable()
            self.lab_zoomspeed.Disable()
            self.lab_unsharp.Disable()
            # disable makeduo
            self.ckbx_duo.SetValue(False)
            self.ckbx_duo.Disable()
            # disable preview
            self.btn_snap.Disable()
            self.sld_time.Disable()
            self.lab_time.Disable()
            self.lab_dur.Disable()
            self.spin_dur.Disable()
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
        if not self.ckbx_enable.IsChecked():
            return None

        # vidstabdetect
        shakiness = self.spin_shake.GetValue()
        accuracy = self.spin_accuracy.GetValue()
        stepsize = self.spin_stepsize.GetValue()
        mincontrast = self.spin_mincontr.GetValue()
        if self.ckbx_tripod1.IsChecked():
            tripod1, tripod2 = '1', '1'
        else:
            tripod1, tripod2 = '0', '0'
        # vidstabtransform
        smoothing = self.spin_smooth.GetValue()
        optalgo = self.rdb_optalgo.GetString(self.rdb_optalgo.GetSelection())
        maxangle = self.spin_maxangle.GetValue()
        crop = self.rdb_crop.GetString(self.rdb_crop.GetSelection())

        invert = '1' if self.ckbx_invert.IsChecked() else '0'
        relative = '1' if self.ckbx_relative.IsChecked() else '0'

        zoom = self.spin_zoom.GetValue()
        optzoom = self.spin_optzoom.GetValue()
        zoomspeed = self.spin_zoomspeed.GetValue()
        interp = self.rdb_interpol.GetString(self.rdb_interpol.GetSelection())

        vidstabdetect = (f'vidstabdetect=shakiness={shakiness}:'
                         f'accuracy={accuracy}:'
                         f'stepsize={stepsize}:'
                         f'mincontrast={mincontrast}:'
                         f'tripod={tripod1}:'
                         f'show=0'
                         )
        vidstabtransform = (f'vidstabtransform=smoothing={smoothing}:'
                            f'optalgo={optalgo}:'
                            f'maxshift=-1:'
                            f'maxangle={maxangle}:'
                            f'crop={crop}:'
                            f'invert={invert}:'
                            f'relative={relative}:'
                            f'zoom={zoom}:'
                            f'optzoom={optzoom}:'
                            f'zoomspeed={zoomspeed}:'
                            f'interpol={interp}:'
                            f'tripod={tripod2}'
                            )
        unsharp = self.txt_unsharp.GetValue()
        makeduo = self.ckbx_duo.IsChecked()

        return vidstabdetect, vidstabtransform, unsharp, makeduo
