# -*- coding: UTF-8 -*-
"""
FileName: video_encodercopy.py
Porpose: Contains copy-codec functionalities for A/V Conversions
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.05.2024
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
import wx
import wx.lib.scrolledpanel as scrolled


class Copy_Vcodec(scrolled.ScrolledPanel):
    """
    This scroll panel implements video controls functions
    for Copy Source Video Codec on A/V Conversions.
    """
    # supported libx264 Bit Depths (10bit need 0 to 63 cfr quantizer scale)
    PIXELFRMT = [('Auto'), ('gray'), ('gray10le'), ('nv12'), ('nv16'),
                 ('nv20le'), ('nv21'), ('yuv420p'), ('yuv420p10le'),
                 ('yuv422p'), ('yuv422p10le'), ('yuv444p'), ('yuv444p10le'),
                 ('yuvj420p'), ('yuvj422p'), ('yuvj444p'),
                 ]
    ASPECTRATIO = [("Auto"), ("1:1"), ("1.3333"), ("1.7777"), ("2.4:1"),
                   ("3:2"), ("4:3"), ("5:4"), ("8:7"), ("14:10"), ("16:9"),
                   ("16:10"), ("19:10"), ("21:9"), ("32:9"),
                   ]
    FPS = [("Auto"), ("ntsc"), ("pal"), ("film"), ("23.976"), ("24"),
           ("25"), ("29.97"), ("30"), ("48"), ("50"), ("59.94"), ("60"),
           ]

    def __init__(self, parent, opt):
        """
        This is a child of `AV_Conv` class-panel (parent).
        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.parent = parent  # parent is the `nb_Video` here.
        self.opt = opt
        scrolled.ScrolledPanel.__init__(self, parent, -1,
                                        size=(1024, 1024),
                                        style=wx.TAB_TRAVERSAL
                                        | wx.BORDER_NONE,
                                        name="Copy Video Codec scrolledpanel",
                                        )
        sizerbase = wx.BoxSizer(wx.VERTICAL)
        self.labinfo = wx.StaticText(self, wx.ID_ANY, label="")
        sizerbase.Add(self.labinfo, 0, wx.ALL | wx.CENTER, 2)
        self.labsubinfo = wx.StaticText(self, wx.ID_ANY,
                                        style=wx.ST_ELLIPSIZE_END
                                        | wx.ALIGN_CENTRE_HORIZONTAL)
        sizerbase.Add(self.labsubinfo, 0, wx.ALL | wx.CENTER, 2)
        if self.appdata['ostype'] == 'Darwin':
            self.labinfo.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            self.labsubinfo.SetFont(wx.Font(11, wx.DEFAULT,
                                            wx.NORMAL, wx.NORMAL))
        else:
            self.labinfo.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            self.labsubinfo.SetFont(wx.Font(8, wx.DEFAULT,
                                            wx.NORMAL, wx.NORMAL))

        sizerbase.Add((0, 60), 0)
        sizpix = wx.BoxSizer(wx.HORIZONTAL)
        labpixfrm = wx.StaticText(self, wx.ID_ANY, 'Bit Depth:')
        sizpix.Add(labpixfrm, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        self.cmb_pixfrm = wx.ComboBox(self, wx.ID_ANY,
                                      choices=Copy_Vcodec.PIXELFRMT,
                                      size=(150, -1), style=wx.CB_DROPDOWN
                                      | wx.CB_READONLY,
                                      )
        sizpix.Add(self.cmb_pixfrm, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        sizerbase.Add(sizpix, 0, wx.ALL | wx.CENTER, 0)
        sizerbase.Add((0, 20), 0)
        line0 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=(400, -1), style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        sizerbase.Add(line0, 0, wx.ALL | wx.CENTER, 5)
        self.ckbx_web = wx.CheckBox(self, wx.ID_ANY, (_('Optimize for Web')))
        sizerbase.Add(self.ckbx_web, 0, wx.ALL | wx.CENTER, 2)
        line1 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=(400, -1), style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        sizerbase.Add(line1, 0, wx.ALL | wx.CENTER, 5)

        # Options -------------------------------------------
        sizerbase.Add((0, 10), 0)
        sizopt = wx.BoxSizer(wx.HORIZONTAL)
        labvaspect = wx.StaticText(self, wx.ID_ANY, 'Aspect Ratio:')
        sizopt.Add(labvaspect, 0, wx.ALIGN_CENTER_VERTICAL)
        self.cmb_vaspect = wx.ComboBox(self, wx.ID_ANY,
                                       choices=Copy_Vcodec.ASPECTRATIO,
                                       size=(120, -1), style=wx.CB_DROPDOWN
                                       | wx.CB_READONLY,
                                       )
        sizopt.Add(self.cmb_vaspect, 0, wx.LEFT | wx.CENTER, 5)
        labfps = wx.StaticText(self, wx.ID_ANY, 'FPS (frame rate):')
        sizopt.Add(labfps, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        self.cmb_fps = wx.ComboBox(self, wx.ID_ANY,
                                   choices=Copy_Vcodec.FPS,
                                   size=(120, -1),
                                   style=wx.CB_DROPDOWN
                                   | wx.CB_READONLY,
                                   )
        sizopt.Add(self.cmb_fps, 0, wx.LEFT | wx.CENTER, 5)
        sizerbase.Add(sizopt, 0, wx.ALL | wx.CENTER, 0)

        self.SetSizer(sizerbase)  # set panel
        self.SetAutoLayout(1)
        self.SetupScrolling()

        tip = _('Video width and video height ratio.')
        self.cmb_vaspect.SetToolTip(tip)
        tip = (_('Frames repeat a given number of times per second. In some '
                 'countries this is 30 for NTSC, other countries (like '
                 'Italy) use 25 for PAL'))
        self.cmb_fps.SetToolTip(tip)

        self.Bind(wx.EVT_CHECKBOX, self.on_web_optimize, self.ckbx_web)
        self.Bind(wx.EVT_COMBOBOX, self.on_vaspect, self.cmb_vaspect)
        self.Bind(wx.EVT_COMBOBOX, self.on_rate_fps, self.cmb_fps)
        self.Bind(wx.EVT_COMBOBOX, self.on_bit_depth, self.cmb_pixfrm)
    # ------------------------------------------------------------------#

    def video_options(self):
        """
        Get all video parameters
        """
        return (f'{self.opt["VideoMap"]} {self.opt["VideoCodec"]} '
                f'{self.opt["PixFmt"]} {self.opt["WebOptim"]} '
                f'{self.opt["AspectRatio"]} {self.opt["FPS"]}'
                )
    # ------------------------------------------------------------------#

    def default(self):
        """
        Reset all controls to default
        """
        self.cmb_fps.SetSelection(0), self.on_rate_fps(None, False)
        self.cmb_vaspect.SetSelection(0), self.on_vaspect(None, False)
        self.cmb_pixfrm.SetSelection(0), self.on_bit_depth(None, False)
        self.ckbx_web.SetValue(False), self.on_web_optimize(None, False)
        self.labinfo.SetLabel(_("Copy Video Codec"))
        self.labsubinfo.SetLabel(_("This will just copy the video track "
                                   "as is, without any video re-encoding.\n"
                                   "You will only be able to change output "
                                   "format, select other audio encoders and\n"
                                   "a few other options."))
    # ------------------------------------------------------------------#

    def on_bit_depth(self, event, btnreset=True):
        """
        Event on seting pixel format
        """
        val = self.cmb_pixfrm.GetValue()
        self.opt["PixFmt"] = '' if val == 'Auto' else f'-pix_fmt {val}'
    # ------------------------------------------------------------------#

    def on_web_optimize(self, event, btnreset=True):
        """
        Adds or removes -movflags faststart flag to maximize
        speed on video streaming.
        """
        check = self.ckbx_web.IsChecked()
        self.opt["WebOptim"] = '-movflags faststart' if check else ''
    # ------------------------------------------------------------------#

    def on_vaspect(self, event, btnreset=True):
        """
        Set aspect parameter (16:9, 4:3)
        """
        val = self.cmb_vaspect.GetValue()
        self.opt["AspectRatio"] = '' if val == 'Auto' else f'-aspect {val}'
    # ------------------------------------------------------------------#

    def on_rate_fps(self, event, btnreset=True):
        """
        Set video rate parameter with fps values
        """
        fps = self.cmb_fps.GetValue()
        self.opt["FPS"] = '' if fps == 'Auto' else f'-r {fps}'
    # ------------------------------------------------------------------#
