# -*- coding: UTF-8 -*-
# Name: filter_stab.py
# Porpose: Show dialog to get vidstab data based on FFmpeg syntax
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: March.17.2021 *PEP8 compatible*
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
import webbrowser
import wx.lib.agw.floatspin as FS
# import wx.lib.masked as masked # not work on macOSX


class Vidstab(wx.Dialog):
    """
    A dialog tool to get vidstabdetect and vidstabtransform
    data based on FFmpeg syntax.

    """
    get = wx.GetApp()
    OS = get.OS
    GET_LANG = get.GETlang
    SUPPLANG = get.SUPP_langs

    def __init__(self, parent, vidstabdetect, vidstabtransform, unsharp):
        """
        vidstabdetect parameters for pass one.
        vidstabtransform parameters for pass two
        unsharp parameters for pass two

        """
        self.vidstabdetect = vidstabdetect
        self.vidstabtransform = vidstabtransform
        self.unsharp = unsharp

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        """constructor"""
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        box_detect = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                      _("Video Detect"))), wx.VERTICAL)
        sizerBase.Add(box_detect, 0, wx.ALL | wx.EXPAND, 5)

        Flex_detect1 = wx.FlexGridSizer(1, 6, 0, 0)
        box_detect.Add(Flex_detect1, 0, wx.ALL, 5)
        lab_shake = wx.StaticText(self, wx.ID_ANY, (_("Shakiness:")))
        Flex_detect1.Add(lab_shake, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 2)
        self.spin_shake = wx.SpinCtrl(self, wx.ID_ANY, "5",
                                      min=1, max=10,
                                      style=wx.TE_PROCESS_ENTER |
                                      wx.SP_ARROW_KEYS
                                      )
        Flex_detect1.Add(self.spin_shake, 0, wx.RIGHT |
                         wx.ALIGN_CENTER_VERTICAL, 15
                         )
        lab_accuracy = wx.StaticText(self, wx.ID_ANY, (_("Accuracy:")))
        Flex_detect1.Add(lab_accuracy, 0, wx.RIGHT |
                         wx.ALIGN_CENTER_VERTICAL, 2
                         )
        self.spin_accuracy = wx.SpinCtrl(self, wx.ID_ANY, "15",
                                             min=1, max=15,
                                             style=wx.TE_PROCESS_ENTER |
                                             wx.SP_ARROW_KEYS
                                             )
        Flex_detect1.Add(self.spin_accuracy, 0, wx.RIGHT |
                         wx.ALIGN_CENTER_VERTICAL, 15
                         )
        lab_stepsize = wx.StaticText(self, wx.ID_ANY, (_("Stepsize:")))
        Flex_detect1.Add(lab_stepsize, 0, wx.RIGHT |
                         wx.ALIGN_CENTER_VERTICAL, 2
                         )
        self.spin_stepsize = wx.SpinCtrl(self, wx.ID_ANY, "6",
                                         min=1, max=10000,
                                         style=wx.TE_PROCESS_ENTER |
                                         wx.SP_ARROW_KEYS
                                         )
        Flex_detect1.Add(self.spin_stepsize, 0, wx.RIGHT |
                         wx.ALIGN_CENTER_VERTICAL, 15
                         )
        Flex_detect2 = wx.FlexGridSizer(1, 4, 0, 0)
        box_detect.Add(Flex_detect2, 0, wx.ALL, 5)
        lab_mincontr = wx.StaticText(self, wx.ID_ANY, (_("Mincontrast:")))
        Flex_detect2.Add(lab_mincontr, 0, wx.RIGHT |
                         wx.ALIGN_CENTER_VERTICAL, 2)
        self.spin_mincontr = FS.FloatSpin(self, wx.ID_ANY,
                                          min_val=0, max_val=1,
                                          increment=0.01, value=0.25,
                                          agwStyle=FS.FS_LEFT, size=(120, -1)
                                          )
        self.spin_mincontr.SetFormat("%f")
        self.spin_mincontr.SetDigits(2)
        Flex_detect2.Add(self.spin_mincontr, 0, wx.RIGHT |
                         wx.ALIGN_CENTER_VERTICAL, 15
                         )
        Flex_detect2.Add((15, 0), 0, wx.ALL, 5)
        lab = _("Set reference frame number for tripod mode")
        self.ckbx_tripod1 = wx.CheckBox(self, wx.ID_ANY, lab)
        Flex_detect2.Add(self.ckbx_tripod1, 0, wx.ALL |
                         wx.ALIGN_CENTER_VERTICAL, 5
                         )
        # --- vidstabtransform section:
        sizerBase.Add((15, 0), 0, wx.ALL, 5)
        box_trans = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                   _("Video transform"))), wx.VERTICAL)
        sizerBase.Add(box_trans, 1, wx.ALL | wx.EXPAND, 5)
        flex_trans1 = wx.FlexGridSizer(1, 5, 0, 0)
        box_trans.Add(flex_trans1, 0, wx.ALL, 5)
        self.lab_smooth = wx.StaticText(self, wx.ID_ANY, (_("Smoothing:")))
        flex_trans1.Add(self.lab_smooth, 0, wx.RIGHT |
                        wx.ALIGN_CENTER_VERTICAL, 2
                        )
        self.spin_smooth = wx.SpinCtrl(self, wx.ID_ANY, "15", min=0,
                                       max=30, style=wx.TE_PROCESS_ENTER |
                                       wx.SP_ARROW_KEYS, size=(-1, -1)
                                       )
        flex_trans1.Add(self.spin_smooth, 0, wx.RIGHT |
                        wx.ALIGN_CENTER_VERTICAL, 15
                        )
        self.rdb_optalgo = wx.RadioBox(self, wx.ID_ANY,
                                       (_("optalgo: Set the camera path "
                                          "optimization algorithm ")),
                                        choices=[("gauss"), ("avg")],
                                        majorDimension=1,
                                        style=wx.RA_SPECIFY_ROWS
                                        )
        flex_trans1.Add(self.rdb_optalgo, 0, wx.RIGHT |
                     wx.ALIGN_CENTER_VERTICAL, 15
                     )
        self.lab_maxangle = wx.StaticText(self, wx.ID_ANY, (_("Maxangle:")))
        flex_trans1.Add(self.lab_maxangle, 0, wx.RIGHT |
                        wx.ALIGN_CENTER_VERTICAL, 2
                        )
        self.spin_maxangle = wx.SpinCtrl(self, wx.ID_ANY, "-1", min=-1,
                                         max=360, style=wx.TE_PROCESS_ENTER |
                                         wx.SP_ARROW_KEYS, size=(-1, -1)
                                         )
        flex_trans1.Add(self.spin_maxangle, 0, wx.RIGHT |
                        wx.ALIGN_CENTER_VERTICAL, 5
                        )
        self.rdb_crop = wx.RadioBox(self, wx.ID_ANY,
                                    (_("Crop: Specify how to deal with borders "
                                        "that may be visible due to movement "
                                        "compensation ")),
                                        choices=[("keep"), ("black")],
                                        majorDimension=1,
                                        style=wx.RA_SPECIFY_ROWS
                                        )
        box_trans.Add(self.rdb_crop, 0, wx.ALL, 5)
        lab = _("Invert transforms if checked (set to 1)")
        self.ckbx_invert = wx.CheckBox(self, wx.ID_ANY, lab)
        box_trans.Add(self.ckbx_invert, 0, wx.ALL, 5)
        lab = _("Consider transforms as relative to previous frame if "
                "checked (set to 1), absolute if unchecked (set to 0)")
        self.ckbx_relative = wx.CheckBox(self, wx.ID_ANY, lab)
        box_trans.Add(self.ckbx_relative, 0, wx.ALL, 5)
        flex_trans2 = wx.FlexGridSizer(1, 6, 0, 0)
        box_trans.Add(flex_trans2, 0, wx.ALL, 5)
        self.lab_zoom = wx.StaticText(self, wx.ID_ANY, (_("Zoom:")))
        flex_trans2.Add(self.lab_zoom, 0, wx.RIGHT |
                        wx.ALIGN_CENTER_VERTICAL, 2
                        )
        self.spin_zoom = wx.SpinCtrl(self, wx.ID_ANY, "0", min=0,
                                       max=100, style=wx.TE_PROCESS_ENTER |
                                       wx.SP_ARROW_KEYS, size=(-1, -1)
                                       )
        flex_trans2.Add(self.spin_zoom, 0, wx.RIGHT |
                        wx.ALIGN_CENTER_VERTICAL, 15
                        )
        self.lab_optzoom = wx.StaticText(self, wx.ID_ANY, (_("OptZoom:")))
        flex_trans2.Add(self.lab_optzoom, 0, wx.RIGHT |
                        wx.ALIGN_CENTER_VERTICAL, 2
                        )
        self.spin_optzoom = wx.SpinCtrl(self, wx.ID_ANY, "1", min=0,
                                        max=2, style=wx.TE_PROCESS_ENTER |
                                        wx.SP_ARROW_KEYS, size=(-1, -1)
                                        )
        flex_trans2.Add(self.spin_optzoom, 0, wx.RIGHT |
                        wx.ALIGN_CENTER_VERTICAL, 15
                        )
        self.lab_zoomspeed = wx.StaticText(self, wx.ID_ANY, (_("Zoom speed:")))
        flex_trans2.Add(self.lab_zoomspeed, 0, wx.RIGHT |
                        wx.ALIGN_CENTER_VERTICAL, 2
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
                                        (_("Specify type of interpolation ")),
                                        choices=[("no"), ("linear"),
                                                 ("bilinear"), ("bicubic")],
                                        majorDimension=1,
                                        style=wx.RA_SPECIFY_ROWS
                                        )
        self.rdb_interpol.SetSelection(2)
        box_trans.Add(self.rdb_interpol, 0, wx.ALL, 5)
        lab = _("Enable virtual tripod mode if checked (set to 1), which "
                "is equivalent to relative=0:smoothing=0")
        self.ckbx_tripod2 = wx.CheckBox(self, wx.ID_ANY, lab)
        box_trans.Add(self.ckbx_tripod2, 0, wx.ALL, 5)
        flex_trans3 = wx.FlexGridSizer(1, 2, 0, 0)
        box_trans.Add(flex_trans3, 0, wx.ALL, 5)
        self.lab_unsharp = wx.StaticText(self, wx.ID_ANY,
                                         (_("Unsharp filter:")))
        flex_trans3.Add(self.lab_unsharp, 0, wx.RIGHT |
                        wx.ALIGN_CENTER_VERTICAL, 2
                        )
        self.txt_unsharp = wx.TextCtrl(self, wx.ID_ANY,
                                       value="unsharp=5:5:0.8:3:3:0.4",
                                       size=(500, -1),
                                       )
        flex_trans3.Add(self.txt_unsharp, 0, wx.RIGHT |
                        wx.ALIGN_CENTER_VERTICAL, 5
                        )
        # --- confirm buttons section
        gridBtn = wx.GridSizer(1, 2, 0, 0)
        gridhelp = wx.GridSizer(1, 1, 0, 0)
        btn_help = wx.Button(self, wx.ID_HELP, "")
        gridhelp.Add(btn_help, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridBtn.Add(gridhelp)
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        gridexit.Add(btn_close, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.btn_ok = wx.Button(self, wx.ID_OK, _("Apply"))
        gridexit.Add(self.btn_ok, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.btn_activate = wx.ToggleButton(self, wx.ID_ANY, _("Diasbled"))
        gridexit.Add(self.btn_activate, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5
                     )
        gridBtn.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)
        sizerBase.Add(gridBtn, 0, wx.EXPAND)
        # final settings:
        self.SetSizer(sizerBase)
        sizerBase.Fit(self)
        self.Layout()

        # Properties
        self.SetTitle(_("Video stabilizer filter"))

        ## Set previous changes
        if vidstabdetect:
            self.set_values()
        else:
            self.set_default()

        # ----------------------Binding (EVT)--------------------------#

        self.Bind(wx.EVT_SPINCTRL, self.on_optzoom, self.spin_optzoom)
        self.Bind(wx.EVT_CHECKBOX, self.on_Tripod1, self.ckbx_tripod1)
        self.Bind(wx.EVT_CHECKBOX, self.on_Tripod2, self.ckbx_tripod2)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_activate, self.btn_activate)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)

    # ------------------------------------------------------------------#
    def set_default(self):
        """
        Revert all control values to default

        """
        self.btn_activate.SetLabel('Disabled')
        self.btn_activate.SetValue(False)
        # vidstabdetect
        self.spin_shake.SetValue('5'),
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
        self.spin_zoomspeed.SetValue(0.25), self.spin_zoomspeed.Disable()
        self.rdb_interpol.SetSelection(2)
        self.ckbx_tripod2.SetValue(False), self.ckbx_tripod2.Disable()
        # unsharp filter
        self.txt_unsharp.Clear()
        self.txt_unsharp.write('unsharp=5:5:0.8:3:3:0.4')
    # ------------------------------------------------------------------#

    def set_values(self):
        """
        set values previously confirmed

        """
        dect = self.vidstabdetect.split(':')

        for v in dect:
            if 'shakiness=' in v:
                self.spin_shake.SetValue(v.split('=')[2])
            if 'accuracy' in v:
                self.spin_accuracy.SetValue(v.split('=')[1])
            if 'stepsize' in v:
                self.spin_stepsize.SetValue(v.split('=')[1])
            if 'mincontrast' in v:
                self.spin_mincontr.SetValue(float(v.split('=')[1]))
            if 'tripod' in v:
                if v.split('=')[1] == '1':
                    self.ckbx_tripod1.SetValue(True)
                    self.ckbx_tripod2.SetValue(True)
                    self.ckbx_tripod2.Enable()
                else:
                    self.ckbx_tripod1.SetValue(False)
                    self.ckbx_tripod2.SetValue(False)
                    self.ckbx_tripod2.Disable()

        transf = self.vidstabtransform.split(':')

        for v in transf:
            if 'smoothing' in v:
                self.spin_smooth.SetValue(v.split('=')[2])
            if 'optalgo' in v:
                if v.split('=')[1] == 'gauss':
                    self.rdb_optalgo.SetSelection(0)
                else:
                    self.rdb_optalgo.SetSelection(1)
            if 'maxangle' in v:
                self.spin_maxangle.SetValue(v.split('=')[1])
            if 'crop' in v:
                if v.split('=')[1] == 'keep':
                    self.rdb_crop.SetSelection(0)
                else:
                    self.rdb_crop.SetSelection(1)
            if 'invert' in v:
                if v.split('=')[1] == '1':
                    self.ckbx_invert.SetValue(True)
                else:
                    self.ckbx_invert.SetValue(False)
            if 'relative' in v:
                if v.split('=')[1] == '1':
                    self.ckbx_relative.SetValue(True)
                else:
                    self.ckbx_relative.SetValue(False)
            if 'zoom' in v:
                self.spin_zoom.SetValue(v.split('=')[1])
            if 'optzoom' in v:
                self.spin_optzoom.SetValue(v.split('=')[1])
                if v.split('=')[1] == '2':
                    self.spin_zoomspeed.Enable()
                else:
                    self.spin_zoomspeed.Disable()
            if 'zoomspeed' in v:
                self.spin_zoomspeed.SetValue(float(v.split('=')[1]))
            if 'interpol' in v:
                if v.split('=')[1] == 'no':
                    self.rdb_interpol.SetSelection(0)
                elif v.split('=')[1] == 'linear':
                    self.rdb_interpol.SetSelection(1)
                elif v.split('=')[1] == 'bilinear':
                    self.rdb_interpol.SetSelection(2)
                else:
                    self.rdb_interpol.SetSelection(3)

        self.txt_unsharp.Clear()
        self.txt_unsharp.write(self.unsharp)
        self.btn_activate.SetValue(True)
        self.on_activate(self)

    # ----------------------Event handler (callback)---------------------#

    def on_optzoom(self, event):
        """
        If optzoom value is equal to 2, enable zoomspeed

        """
        if self.spin_optzoom.GetValue() == 2:
            self.spin_zoomspeed.Enable()
        else:
            self.spin_zoomspeed.SetValue(0.25)
            self.spin_zoomspeed.Disable()
    # ------------------------------------------------------------------#

    def on_Tripod1(self, event):
        """
        If self.ckbx_tripod1 is checked, enable and
        check self.ckbx_tripod2

        """
        if self.ckbx_tripod1.IsChecked():
            self.ckbx_tripod2.Enable(), self.ckbx_tripod2.SetValue(True)
        else:
            self.ckbx_tripod2.Disable(), self.ckbx_tripod2.SetValue(False)
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
        if Vidstab.GET_LANG in Vidstab.SUPPLANG:
            lang = Vidstab.GET_LANG.split('_')[0]
            page = ('https://jeanslack.github.io/Videomass/Pages/User-guide-'
                    'languages/%s/4-Video_Filters_%s.pdf' % (lang, lang))
        else:
            page = ('https://jeanslack.github.io/Videomass/Pages/User-guide-'
                    'languages/en/4-Video_Filters_en.pdf')

        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def on_activate(self, event):
        """
        Enable or disable vidstab filter

        """
        if self.btn_activate.GetValue():
            self.btn_activate.SetLabel('Enabled')
        else:
            self.set_default()

    # ------------------------------------------------------------------#

    def on_close(self, event):
        event.Skip()
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        if you enable self.Destroy(), it delete from memory all data
        event and does not return anything. It has the right behavior if
        not used here, because it is called in the main frame.

        Event.Skip(), work correctly here. Sometimes needs to disable
        it for needs to maintain the view of the window (for exemple).

        """
        self.GetValue()
        # self.Destroy()
        event.Skip()
    # ------------------------------------------------------------------#

    def GetValue(self):
        """
        This method return values via the interface GetValue()

        """
        if not self.btn_activate.GetValue():
            return (None)

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
        interpol = self.rdb_interpol.GetString(self.rdb_interpol.GetSelection())

        vidstabdetect = ('vidstabdetect=shakiness=%s:'
                         'accuracy=%s:'
                         'stepsize=%s:'
                         'mincontrast=%s:'
                         'tripod=%s:'
                         'show=0' % (shakiness, accuracy, stepsize,
                                     mincontrast, tripod1)
                         )
        vidstabtransform = ('vidstabtransform=smoothing=%s:'
                            'optalgo=%s:'
                            'maxshift=-1:'
                            'maxangle=%s:'
                            'crop=%s:'
                            'invert=%s:'
                            'relative=%s:'
                            'zoom=%s:'
                            'optzoom=%s:'
                            'zoomspeed=%s:'
                            'interpol=%s:'
                            'tripod=%s' % (smoothing, optalgo, maxangle,
                                           crop, invert, relative, zoom,
                                           optzoom, zoomspeed, interpol,
                                           tripod2)
                            )
        unsharp = self.txt_unsharp.GetValue()

        return (vidstabdetect, vidstabtransform, unsharp)
