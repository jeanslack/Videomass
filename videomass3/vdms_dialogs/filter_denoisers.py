# -*- coding: UTF-8 -*-
# Name: filter_denoiser.py
# Porpose: Show dialog to get denoiser data based on FFmpeg syntax
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: November.24.2020 *PEP8 compatible*
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


class Denoisers(wx.Dialog):
    """
    A dialog tool to get video denoiser values
    based on FFmpeg syntax.

    """
    get = wx.GetApp()
    GET_LANG = get.GETlang
    SUPPLANG = get.SUPP_langs

    def __init__(self, parent, denoiser):
        """
        Make sure you use the clear button when you finish the task.
        Enable filters denoiser useful in some case, example when apply
        a deinterlace filter
        <https://askubuntu.com/questions/866186/how-to-get-good-quality-when-
        converting-digital-video>

        """
        if denoiser:
            self.denoiser = denoiser
        else:
            self.denoiser = ''

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)

        zone = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY,
                                              (_("Apply Denoisers Filters"))
                                              ), wx.VERTICAL)
        self.ckbx_nlmeans = wx.CheckBox(self, wx.ID_ANY,
                                        (_("Enable nlmeans denoiser"))
                                        )
        nlmeans = [("Default"),
                   ("Old VHS tapes - good starting point restoration"),
                   ("Heavy - really noisy inputs"),
                   ("Light - good quality inputs")
                   ]
        self.rdb_nlmeans = wx.RadioBox(self, wx.ID_ANY, (_("nlmeans options")),
                                       choices=nlmeans, majorDimension=0,
                                       style=wx.RA_SPECIFY_ROWS
                                       )
        self.ckbx_hqdn3d = wx.CheckBox(self, wx.ID_ANY,
                                       (_("Enable hqdn3d denoiser"))
                                       )
        hqdn3d = [("Default"), ("Conservative [4.0:4.0:3.0:3.0]"),
                  ("Old VHS tapes restoration [9.0:5.0:3.0:3.0]")
                  ]
        self.rdb_hqdn3d = wx.RadioBox(self, wx.ID_ANY, (_("hqdn3d options")),
                                      choices=hqdn3d, majorDimension=0,
                                      style=wx.RA_SPECIFY_ROWS
                                      )
        # ----- confirm buttons section
        btn_help = wx.Button(self, wx.ID_HELP, "")
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        self.btn_ok = wx.Button(self, wx.ID_OK, _("Apply"))
        btn_reset = wx.Button(self, wx.ID_CLEAR, _("Reset"))
        # ------ set Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(zone, 1, wx.ALL | wx.EXPAND, 5)
        grid_den = wx.FlexGridSizer(2, 2, 0, 0)
        zone.Add(grid_den)
        grid_den.Add(self.ckbx_nlmeans, 0,
                     wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL |
                     wx.ALIGN_CENTER_HORIZONTAL,
                     5)
        grid_den.Add(self.rdb_nlmeans, 0,
                     wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL |
                     wx.ALIGN_CENTER_HORIZONTAL,
                     5)
        grid_den.Add(self.ckbx_hqdn3d, 0,
                     wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL |
                     wx.ALIGN_CENTER_HORIZONTAL,
                     5)
        grid_den.Add(self.rdb_hqdn3d, 0,
                     wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL |
                     wx.ALIGN_CENTER_HORIZONTAL,
                     5)
        # confirm btn section:
        gridBtn = wx.GridSizer(1, 2, 0, 0)
        gridhelp = wx.GridSizer(1, 1, 0, 0)
        gridhelp.Add(btn_help, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridBtn.Add(gridhelp)
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        gridexit.Add(btn_close, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridexit.Add(self.btn_ok, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridexit.Add(btn_reset, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridBtn.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)
        # final settings:
        sizer_base.Add(gridBtn, 0, wx.EXPAND)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        # set Properties
        self.SetTitle(_("Denoiser filters"))
        tool = _('nlmeans:\nDenoise frames using Non-Local Means algorithm '
                 'is capable of restoring video sequences with even strong '
                 'noise. It is ideal for enhancing the quality of old VHS '
                 'tapes.')
        self.ckbx_nlmeans.SetToolTip(tool)
        tool = _('hqdn3d:\nThis is a high precision/quality 3d denoise '
                 'filter. It aims to reduce image noise, producing smooth '
                 'images and making still images really still. It should '
                 'enhance compressibility.')
        self.ckbx_hqdn3d.SetToolTip(tool)

        # ----------------------Binding (EVT)--------------------------#
        self.Bind(wx.EVT_CHECKBOX, self.on_nlmeans, self.ckbx_nlmeans)
        self.Bind(wx.EVT_CHECKBOX, self.on_hqdn3d, self.ckbx_hqdn3d)
        self.Bind(wx.EVT_RADIOBOX, self.on_nlmeans_opt, self.rdb_nlmeans)
        self.Bind(wx.EVT_RADIOBOX, self.on_hqdn3d_opt, self.rdb_hqdn3d)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)

        self.settings()

    def settings(self):
        """
        Set default or set in according with previusly activated option
        """
        if self.denoiser:
            if self.denoiser.startswith('nlmeans'):
                spl = self.denoiser.split('=')
                if len(spl) == 1:
                    self.rdb_nlmeans.SetSelection(0)
                else:
                    if spl[1] == '8:3:2':
                        self.rdb_nlmeans.SetSelection(1)
                    if spl[1] == '10:5:3':
                        self.rdb_nlmeans.SetSelection(2)
                    if spl[1] == '6:3:1':
                        self.rdb_nlmeans.SetSelection(3)
                self.ckbx_nlmeans.SetValue(True)
                self.ckbx_hqdn3d.SetValue(False)
                self.ckbx_nlmeans.Enable()
                self.ckbx_hqdn3d.Disable()
                self.rdb_nlmeans.Enable()
                self.rdb_hqdn3d.Disable()

            elif self.denoiser.startswith('hqdn3d'):
                spl = self.denoiser.split('=')
                if len(spl) == 1:
                    self.rdb_hqdn3d.SetSelection(0)
                else:
                    if spl[1] == '4.0:4.0:3.0:3.0':
                        self.rdb_hqdn3d.SetSelection(1)
                    if spl[1] == '9.0:5.0:3.0:3.0':
                        self.rdb_hqdn3d.SetSelection(2)

                self.ckbx_nlmeans.SetValue(False)
                self.ckbx_hqdn3d.SetValue(True)
                self.ckbx_nlmeans.Disable()
                self.ckbx_hqdn3d.Enable()
                self.rdb_nlmeans.Disable()
                self.rdb_hqdn3d.Enable()
        else:
            self.ckbx_nlmeans.SetValue(False)
            self.ckbx_hqdn3d.SetValue(False)
            self.ckbx_nlmeans.Enable()
            self.ckbx_hqdn3d.Enable()
            self.rdb_nlmeans.SetSelection(0)
            self.rdb_nlmeans.Disable()
            self.rdb_hqdn3d.Disable()

    # ----------------------Event handler (callback)----------------------#

    def on_nlmeans(self, event):
        """
        """
        if self.ckbx_nlmeans.IsChecked():
            self.rdb_nlmeans.Enable()
            self.rdb_hqdn3d.Disable()
            self.ckbx_hqdn3d.Disable()
            self.denoiser = "nlmeans"

        elif not self.ckbx_nlmeans.IsChecked():
            self.rdb_nlmeans.Disable()
            self.ckbx_hqdn3d.Enable()
            self.denoiser = ""
    # ------------------------------------------------------------------#

    def on_nlmeans_opt(self, event):
        """
        """
        opt = self.rdb_nlmeans.GetStringSelection()
        if opt == "Default":
            self.denoiser = "nlmeans"
        elif opt == "Old VHS tapes - good starting point restoration":
            self.denoiser = "nlmeans=8:3:2"
        elif opt == "Heavy - really noisy inputs":
            self.denoiser = "nlmeans=10:5:3"
        elif opt == "Light - good quality inputs":
            self.denoiser = "nlmeans=6:3:1"
    # ------------------------------------------------------------------#

    def on_hqdn3d(self, event):
        """
        """
        if self.ckbx_hqdn3d.IsChecked():
            self.ckbx_nlmeans.Disable()
            self.rdb_hqdn3d.Enable()
            self.denoiser = "hqdn3d"

        elif not self.ckbx_hqdn3d.IsChecked():
            self.ckbx_nlmeans.Enable()
            self.rdb_hqdn3d.Disable()
            self.denoiser = ""
    # ------------------------------------------------------------------#

    def on_hqdn3d_opt(self, event):
        """
        """
        opt = self.rdb_hqdn3d.GetStringSelection()
        if opt == "Default":
            self.denoiser = "hqdn3d"

        elif opt == "Conservative [4.0:4.0:3.0:3.0]":
            self.denoiser = "hqdn3d=4.0:4.0:3.0:3.0"

        elif opt == "Old VHS tapes restoration [9.0:5.0:3.0:3.0]":
            self.denoiser = "hqdn3d=9.0:5.0:3.0:3.0"
    # ------------------------------------------------------------------#

    def on_help(self, event):
        """
        Open default web browser via Python Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        if Denoisers.GET_LANG in Denoisers.SUPPLANG:
            lang = Denoisers.GET_LANG.split('_')[0]
            page = ('https://jeanslack.github.io/Videomass/Pages/User-guide-'
                    'languages/%s/4-Video_filters_%s.pdf' % (lang, lang))
        else:
            page = ('https://jeanslack.github.io/Videomass/Pages/User-guide-'
                    'languages/en/4-Video_filters_en.pdf')

        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def on_reset(self, event):
        """
        Reset all option and values
        """
        self.denoiser = ""  # deleting dictionary keys+values
        self.ckbx_nlmeans.SetValue(False)
        self.ckbx_hqdn3d.SetValue(False)
        self.ckbx_nlmeans.Enable()
        self.ckbx_hqdn3d.Enable()
        self.rdb_nlmeans.SetSelection(0)
        self.rdb_nlmeans.Disable()
        self.rdb_hqdn3d.SetSelection(0)
        self.rdb_hqdn3d.Disable()
    # ------------------------------------------------------------------#

    def on_close(self, event):

        event.Skip()
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        if you enable self.Destroy(), it delete from memory all data
        event and no return correctly. It has the right behavior if
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
        return self.denoiser
