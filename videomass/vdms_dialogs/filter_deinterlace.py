# -*- coding: UTF-8 -*-
"""
Name: filter_deinterlace.py
Porpose: Show dialog to get deinterlace/interlace data based on FFmpeg syntax
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: May.09.2024
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
import webbrowser
import wx


class Deinterlace(wx.Dialog):
    """
    A dialog tool to get video interlacing/deinterlacing values
    based on FFmpeg syntax.
    See ``av_conversions.py`` -> ``on_Set_deinterlace`` method
    for how to use this class.
    """
    get = wx.GetApp()
    appdata = get.appset

    def __init__(self, parent, deinterlace, interlace, iconreset):
        """
        Make sure you use the clear button when you finish the task.
        """
        self.cmd_opt = {}
        if deinterlace:
            self.cmd_opt["deinterlace"] = deinterlace
        elif interlace:
            self.cmd_opt["interlace"] = interlace
        else:
            pass

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)

        self.enable_opt = wx.ToggleButton(self, wx.ID_ANY,
                                          _("Advanced Options"))
        boxs = wx.StaticBox(self, wx.ID_ANY, (_("Deinterlace")))
        zone1 = wx.StaticBoxSizer(boxs, wx.VERTICAL)
        boxs = wx.StaticBox(self, wx.ID_ANY, (_("Interlace")))
        zone2 = wx.StaticBoxSizer(boxs, wx.VERTICAL)

        self.ckbx_deintW3fdif = wx.CheckBox(self, wx.ID_ANY,
                                            (_("Deinterlaces with "
                                               "w3fdif filter"))
                                            )
        self.rdbx_w3fdif = wx.RadioBox(self, wx.ID_ANY, ("Filter"),
                                       choices=[("simple"), ("complex")],
                                       majorDimension=0,
                                       style=wx.RA_SPECIFY_ROWS
                                       )
        self.rdbx_w3fdif_d = wx.RadioBox(self, wx.ID_ANY, ("Deint"),
                                         choices=[("all"), ("interlaced")],
                                         majorDimension=0,
                                         style=wx.RA_SPECIFY_ROWS
                                         )
        self.ckbx_deintYadif = wx.CheckBox(self, wx.ID_ANY,
                                           (_("Deinterlaces with "
                                              "yadif filter"))
                                           )
        yadif = [("0, send_frame"), ("1, send_field"),
                 ("2, send_frame_nospatial"), ("3, send_field_nospatial")
                 ]
        self.rdbx_Yadif_mode = wx.RadioBox(self, wx.ID_ANY, ("Mode"),
                                           choices=yadif, majorDimension=0,
                                           style=wx.RA_SPECIFY_ROWS
                                           )
        self.rdbx_Yadif_parity = wx.RadioBox(self, wx.ID_ANY, ("Parity"),
                                             choices=[("0, tff"),
                                                      ("1, bff"),
                                                      ("-1, auto")],
                                             majorDimension=0,
                                             style=wx.RA_SPECIFY_ROWS
                                             )
        self.rdbx_Yadif_deint = wx.RadioBox(self, wx.ID_ANY, ("Deint"),
                                            choices=[("0, all"),
                                                     ("1, interlaced")],
                                            majorDimension=0,
                                            style=wx.RA_SPECIFY_ROWS
                                            )
        self.ckbx_interlace = wx.CheckBox(self, wx.ID_ANY,
                                          (_("Interlaces with "
                                             "interlace filter"))
                                          )
        self.rdbx_inter_scan = wx.RadioBox(self, wx.ID_ANY, ("Scanning mode"),
                                           choices=[("scan=tff"),
                                                    ("scan=bff")],
                                           majorDimension=0,
                                           style=wx.RA_SPECIFY_ROWS
                                           )
        self.rdbx_inter_lowpass = wx.RadioBox(self, wx.ID_ANY,
                                              ("Set vertical low-pass filter"),
                                              choices=[("lowpass=0"),
                                                       ("lowpass=1")],
                                              majorDimension=0,
                                              style=wx.RA_SPECIFY_ROWS
                                              )
        # set Properties
        self.SetTitle(_("Deinterlacing and Interlacing"))
        self.rdbx_w3fdif.Hide()
        self.rdbx_w3fdif_d.Hide()
        self.rdbx_Yadif_mode.Hide()
        self.rdbx_Yadif_parity.Hide()
        self.rdbx_Yadif_deint.Hide()
        self.rdbx_inter_scan.Hide()
        self.rdbx_inter_lowpass.Hide()
        self.ckbx_deintW3fdif.SetValue(False)
        self.ckbx_deintYadif.SetValue(False)
        self.ckbx_interlace.SetValue(False)
        self.rdbx_w3fdif.SetSelection(1)
        self.rdbx_w3fdif_d.SetSelection(0)
        self.rdbx_Yadif_mode.SetSelection(0)
        self.rdbx_Yadif_parity.SetSelection(2)
        self.rdbx_Yadif_deint.SetSelection(0)
        self.rdbx_inter_scan.SetSelection(0)
        self.rdbx_inter_lowpass.SetSelection(1)
        self.rdbx_w3fdif.Disable()
        self.rdbx_w3fdif_d.Disable()
        self.rdbx_Yadif_mode.Disable()
        self.rdbx_Yadif_parity.Disable()
        self.rdbx_Yadif_deint.Disable()
        self.rdbx_inter_scan.Disable()
        self.rdbx_inter_lowpass.Disable()

        self.ckbx_deintW3fdif.SetToolTip(_('Deinterlace the input video '
                                           'with `w3fdif` filter'))
        self.rdbx_w3fdif.SetToolTip(_('Set the interlacing filter '
                                      'coefficients.'))
        self.rdbx_w3fdif_d.SetToolTip(_('Specify which frames to '
                                        'deinterlace.'))
        toolt = _('Deinterlace the input video with `yadif` filter. '
                  'Using FFmpeg, this is the best and fastest choice')
        self.ckbx_deintYadif.SetToolTip(toolt)
        self.rdbx_Yadif_mode.SetToolTip(_('mode\n'
                                          'The interlacing mode to adopt.'))
        toolt = _('parity\nThe picture field parity assumed for the '
                  'input interlaced video.')
        self.rdbx_Yadif_parity.SetToolTip(toolt)
        self.rdbx_Yadif_deint.SetToolTip(_('Specify which frames to '
                                           'deinterlace.'))
        self.ckbx_interlace.SetToolTip(_('Simple interlacing filter from '
                                         'progressive contents.'))
        toolt = _('scan:\ndetermines whether the interlaced frame is '
                  'taken from the even (tff - default) or odd (bff) '
                  'lines of the progressive frame.')
        self.rdbx_inter_scan.SetToolTip(toolt)
        toolt = _('lowpass:\nEnable (default) or disable the vertical '
                  'lowpass filter to avoid twitter interlacing and reduce '
                  'moire patterns.\nDefault is no setting.')
        self.rdbx_inter_lowpass.SetToolTip(toolt)

        self.sizer_base = wx.BoxSizer(wx.VERTICAL)
        self.sizer_base.Add(self.enable_opt, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        self.sizer_base.Add(zone1, 0, wx.ALL | wx.EXPAND, 5)
        grid_w3fdif = wx.FlexGridSizer(1, 4, 0, 0)
        zone1.Add(grid_w3fdif)
        grid_w3fdif.Add(self.ckbx_deintW3fdif, 0, wx.ALL
                        | wx.ALIGN_CENTER_VERTICAL
                        | wx.ALIGN_CENTER_HORIZONTAL, 5)
        grid_w3fdif.Add(self.rdbx_w3fdif, 0, wx.ALL, 5)
        grid_w3fdif.Add(self.rdbx_w3fdif_d, 0, wx.ALL, 5)
        grid_yadif = wx.FlexGridSizer(1, 4, 0, 0)
        zone1.Add(grid_yadif)
        grid_yadif.Add(self.ckbx_deintYadif, 0, wx.ALL
                       | wx.ALIGN_CENTER_VERTICAL
                       | wx.ALIGN_CENTER_HORIZONTAL, 5)
        grid_yadif.Add(self.rdbx_Yadif_mode, 0, wx.ALL, 5)
        grid_yadif.Add(self.rdbx_Yadif_parity, 0, wx.ALL, 5)
        grid_yadif.Add(self.rdbx_Yadif_deint, 0, wx.ALL, 5)
        self.sizer_base.Add(zone2, 0, wx.ALL | wx.EXPAND, 5)
        inter_grid = wx.FlexGridSizer(1, 3, 0, 0)
        zone2.Add(inter_grid)
        inter_grid.Add(self.ckbx_interlace, 0, wx.ALL
                       | wx.ALIGN_CENTER_VERTICAL
                       | wx.ALIGN_CENTER_HORIZONTAL, 5)
        inter_grid.Add(self.rdbx_inter_scan, 0, wx.ALL, 5)
        inter_grid.Add(self.rdbx_inter_lowpass, 0, wx.ALL, 5)

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
        self.sizer_base.Add(gridbtns, 0, wx.EXPAND)
        # ----- Set layout
        self.SetSizer(self.sizer_base)
        self.sizer_base.Fit(self)
        self.Layout()

        # ----------------------Binding (EVT)-------------------------#
        self.Bind(wx.EVT_CHECKBOX, self.on_DeintW3fdif, self.ckbx_deintW3fdif)
        self.Bind(wx.EVT_RADIOBOX, self.on_W3fdif_filter, self.rdbx_w3fdif)
        self.Bind(wx.EVT_RADIOBOX, self.on_W3fdif_deint, self.rdbx_w3fdif_d)
        self.Bind(wx.EVT_CHECKBOX, self.on_DeintYadif, self.ckbx_deintYadif)
        self.Bind(wx.EVT_RADIOBOX, self.on_modeYadif, self.rdbx_Yadif_mode)
        self.Bind(wx.EVT_RADIOBOX, self.on_parityYadif, self.rdbx_Yadif_parity)
        self.Bind(wx.EVT_RADIOBOX, self.on_deintYadif, self.rdbx_Yadif_deint)
        self.Bind(wx.EVT_CHECKBOX, self.on_Interlace, self.ckbx_interlace)
        self.Bind(wx.EVT_RADIOBOX, self.on_intScan, self.rdbx_inter_scan)
        self.Bind(wx.EVT_RADIOBOX, self.on_intLowpass, self.rdbx_inter_lowpass)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.Advanced_Opt, self.enable_opt)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)

        self.settings()

    def settings(self):
        """
        set default or set in according with previusly activated option
        """
        if 'deinterlace' in self.cmd_opt:
            if self.cmd_opt["deinterlace"].startswith('yadif'):
                self.ckbx_deintYadif.SetValue(True)
                self.ckbx_deintW3fdif.Disable()
                self.ckbx_interlace.Disable()
                self.rdbx_Yadif_mode.Enable()
                self.rdbx_Yadif_parity.Enable()
                self.rdbx_Yadif_deint.Enable()
                indx = self.cmd_opt["deinterlace"].split('=')[1].split(':')
                parity = 2 if indx[1] == '-1' else indx[1]
                self.rdbx_Yadif_mode.SetSelection(int(indx[0]))
                self.rdbx_Yadif_parity.SetSelection(int(parity))
                self.rdbx_Yadif_deint.SetSelection(int(indx[2]))

            elif self.cmd_opt["deinterlace"].startswith('w3fdif'):
                self.ckbx_deintW3fdif.SetValue(True)
                self.ckbx_deintYadif.Disable()
                self.ckbx_interlace.Disable()
                self.rdbx_w3fdif.Enable()
                self.rdbx_w3fdif_d.Enable()
                indx = self.cmd_opt["deinterlace"].split(':')
                if indx[0].split('=')[2] == 'complex':
                    self.rdbx_w3fdif.SetSelection(1)
                elif indx[0].split('=')[2] == 'simple':
                    self.rdbx_w3fdif.SetSelection(0)
                if indx[1].split('=')[1] == 'all':
                    self.rdbx_w3fdif_d.SetSelection(0)
                elif indx[1].split('=')[1] == 'interlaced':
                    self.rdbx_w3fdif_d.SetSelection(1)

        elif 'interlace' in self.cmd_opt:
            self.ckbx_interlace.SetValue(True)
            self.ckbx_deintW3fdif.Disable()
            self.ckbx_deintYadif.Disable()
            self.rdbx_inter_scan.Enable()
            self.rdbx_inter_lowpass.Enable()
            scan = self.cmd_opt["interlace"].split('=')[2].split(':')
            if 'tff' in scan[0]:
                scan = 0
            elif 'bff' in scan[0]:
                scan = 1
            self.rdbx_inter_scan.SetSelection(scan)

            lowpass = self.cmd_opt["interlace"].split(':')
            if 'lowpass=0' in lowpass[1]:
                lowpass = 0
            elif 'lowpass=1' in lowpass[1]:
                lowpass = 1
            self.rdbx_inter_lowpass.SetSelection(lowpass)
        else:
            pass
    # --------------------Event handler (callback)----------------------#

    def on_DeintW3fdif(self, event):
        """
        Enable/disable Deinterlace using `W3fdif` filter
        """
        if self.ckbx_deintW3fdif.IsChecked():
            self.rdbx_w3fdif.Enable()
            self.rdbx_w3fdif_d.Enable()
            self.ckbx_deintYadif.Disable()
            self.ckbx_interlace.Disable()
            self.cmd_opt["deinterlace"] = "w3fdif=filter=complex:deint=all"

        elif not self.ckbx_deintW3fdif.IsChecked():
            self.rdbx_w3fdif.Disable()
            self.rdbx_w3fdif_d.Disable()
            self.ckbx_deintYadif.Enable()
            self.ckbx_interlace.Enable()
            self.cmd_opt.clear()
    # ------------------------------------------------------------------#

    def on_W3fdif_filter(self, event):
        """
        When `W3fdif` is enabled, even enables the `Filter`
        radiobox control for setting the additional parameter
        to `simple` or `complex`, default is `complex`.
        """
        val = (f"w3fdif=filter={self.rdbx_w3fdif.GetStringSelection()}:"
               f"deint={self.rdbx_w3fdif_d.GetStringSelection()}")
        self.cmd_opt["deinterlace"] = val
    # ------------------------------------------------------------------#

    def on_W3fdif_deint(self, event):
        """
        When `W3fdif` is enabled, even enables the `Deint`
        radiobox control for setting the additional parameters
        to `all` or `interlaced`, default is `all`.
        """
        val = (f"w3fdif=filter={self.rdbx_w3fdif.GetStringSelection()}:"
               f"deint={self.rdbx_w3fdif_d.GetStringSelection()}")
        self.cmd_opt["deinterlace"] = val
    # ------------------------------------------------------------------#

    def on_DeintYadif(self, event):
        """
        Enable/disable Deinterlace using `yadif` filter
        """
        if self.ckbx_deintYadif.IsChecked():
            self.ckbx_deintW3fdif.Disable()
            self.rdbx_Yadif_mode.Enable()
            self.rdbx_Yadif_parity.Enable()
            self.rdbx_Yadif_deint.Enable()
            self.ckbx_interlace.Disable()
            self.cmd_opt["deinterlace"] = "yadif=0:-1:0"

        elif not self.ckbx_deintYadif.IsChecked():
            self.ckbx_deintW3fdif.Enable()
            self.rdbx_Yadif_mode.Disable()
            self.rdbx_Yadif_parity.Disable()
            self.rdbx_Yadif_deint.Disable()
            self.ckbx_interlace.Enable()
            self.cmd_opt.clear()
    # ------------------------------------------------------------------#

    def on_modeYadif(self, event):
        """
        When `yadif` is enabled, even enables the `Mode`
        radiobox control for setting additional parameters.
        """
        parity = self.rdbx_Yadif_parity.GetStringSelection().split(',')
        val = (f"yadif={self.rdbx_Yadif_mode.GetStringSelection()[0]}:"
               f"{parity[0]}:{self.rdbx_Yadif_deint.GetStringSelection()[0]}")
        self.cmd_opt["deinterlace"] = val
    # ------------------------------------------------------------------#

    def on_parityYadif(self, event):
        """
        When `yadif` is enabled, even enables the `Parity`
        radiobox control for setting additional parameters.
        """
        parity = self.rdbx_Yadif_parity.GetStringSelection().split(',')

        val = (f"yadif={self.rdbx_Yadif_mode.GetStringSelection()[0]}:"
               f"{parity[0]}:{self.rdbx_Yadif_deint.GetStringSelection()[0]}")
        self.cmd_opt["deinterlace"] = val
    # ------------------------------------------------------------------#

    def on_deintYadif(self, event):
        """
        When `yadif` is enabled, even enables the `Deint`
        radiobox control for setting additional parameters.
        """
        parity = self.rdbx_Yadif_parity.GetStringSelection().split(',')
        val = (f"yadif={self.rdbx_Yadif_mode.GetStringSelection()[0]}:"
               f"{parity[0]}:{self.rdbx_Yadif_deint.GetStringSelection()[0]}")
        self.cmd_opt["deinterlace"] = val
    # ------------------------------------------------------------------#

    def on_Interlace(self, event):
        """
        Enable/disable Deinterlace using `yadif` filter
        """
        if self.ckbx_interlace.IsChecked():
            self.ckbx_deintW3fdif.Disable()
            self.ckbx_deintYadif.Disable()
            self.rdbx_inter_scan.Enable()
            self.rdbx_inter_lowpass.Enable()
            self.cmd_opt["interlace"] = "interlace=scan=tff:lowpass=1"

        elif not self.ckbx_interlace.IsChecked():
            self.ckbx_deintW3fdif.Enable()
            self.ckbx_deintYadif.Enable()
            self.rdbx_inter_scan.Disable()
            self.rdbx_inter_lowpass.Disable()
            self.cmd_opt.clear()
    # ------------------------------------------------------------------#

    def on_intScan(self, event):
        """
        When `interlace` is enabled, even enables the `Scanning mode`
        radiobox control for setting additional parameters.
        """
        val = (f"interlace={self.rdbx_inter_scan.GetStringSelection()}:"
               f"{self.rdbx_inter_lowpass.GetStringSelection()}")
        self.cmd_opt["interlace"] = val
    # ------------------------------------------------------------------#

    def on_intLowpass(self, event):
        """
        When `interlace` is enabled, even enables the
        `Set vertical low-pass filter` radiobox control
        for setting additional parameters.
        """
        val = (f"interlace={self.rdbx_inter_scan.GetStringSelection()}:"
               f"{self.rdbx_inter_lowpass.GetStringSelection()}")
        self.cmd_opt["interlace"] = val
    # ------------------------------------------------------------------#

    def Advanced_Opt(self, event):
        """
        Show or Hide advanved option for all filters
        """
        if self.enable_opt.GetValue():
            # self.enable_opt.SetBackgroundColour(wx.Colour(240, 161, 125))
            self.rdbx_w3fdif.Show()
            self.rdbx_w3fdif_d.Show()
            self.rdbx_Yadif_mode.Show()
            self.rdbx_Yadif_parity.Show()
            self.rdbx_Yadif_deint.Show()
            self.rdbx_inter_scan.Show()
            self.rdbx_inter_lowpass.Show()
        else:
            # self.enable_opt.SetBackgroundColour(wx.NullColour)
            self.rdbx_w3fdif.Hide()
            self.rdbx_w3fdif_d.Hide()
            self.rdbx_Yadif_mode.Hide()
            self.rdbx_Yadif_parity.Hide()
            self.rdbx_Yadif_deint.Hide()
            self.rdbx_inter_scan.Hide()
            self.rdbx_inter_lowpass.Hide()

        self.SetSizer(self.sizer_base)
        self.sizer_base.Fit(self)
        self.Layout()

    # ------------------------------------------------------------------#

    def on_reset(self, event):
        """
        Reset all option and values
        """
        self.cmd_opt.clear()  # deleting dictionary keys+values
        self.ckbx_deintW3fdif.SetValue(False)
        self.ckbx_deintYadif.SetValue(False)
        self.ckbx_interlace.SetValue(False)
        self.ckbx_deintW3fdif.Enable()
        self.ckbx_deintYadif.Enable()
        self.ckbx_interlace.Enable()
        self.rdbx_w3fdif.SetSelection(1)
        self.rdbx_w3fdif_d.SetSelection(0)
        self.rdbx_Yadif_mode.SetSelection(0)
        self.rdbx_Yadif_parity.SetSelection(2)
        self.rdbx_Yadif_deint.SetSelection(0)
        self.rdbx_inter_scan.SetSelection(0)
        self.rdbx_inter_lowpass.SetSelection(1)
        self.rdbx_w3fdif.Disable()
        self.rdbx_w3fdif_d.Disable()
        self.rdbx_Yadif_mode.Disable()
        self.rdbx_Yadif_parity.Disable()
        self.rdbx_Yadif_deint.Disable()
        self.rdbx_inter_scan.Disable()
        self.rdbx_inter_lowpass.Disable()
    # ------------------------------------------------------------------#

    def on_help(self, event):
        """
        Open default web browser via Python Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        page = ('https://jeanslack.github.io/Videomass/User-guide/'
                'Video_filters_en.pdf#%5B%7B%22num%22%3A19%2C%22gen'
                '%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2C56.7%2C468.'
                '539%2C0%5D')

        webbrowser.open(page)
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
        return self.cmd_opt
