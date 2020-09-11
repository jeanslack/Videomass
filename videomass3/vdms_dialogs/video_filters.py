# -*- coding: UTF-8 -*-
# Name: video_filters.py
# Porpose: a module with multiple dialog tools for video filters
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.06.2020 *PEP8 compatible*
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
# import wx.lib.masked as masked # not work on macOSX


class VideoRotate(wx.Dialog):
    """
    Show a dialog to movie frame orientation.
    TODO: make rotate button with images
    """

    def __init__(self, parent, orientation, msg):
        """
        Make sure you use the clear button when you finish the task.
        """
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)

        self.button_up = wx.Button(self, wx.ID_ANY,
                                   (_("Flip over")))  # capovolgi Sopra
        self.button_left = wx.Button(self, wx.ID_ANY,
                                     (_("Rotate Left")))  # ruota sx
        self.button_right = wx.Button(self, wx.ID_ANY,
                                      (_("Rotate Right")))  # ruota a destra
        self.button_down = wx.Button(self, wx.ID_ANY,
                                     (_("Flip below")))  # capovolgi sotto
        self.text_rotate = wx.TextCtrl(self, wx.ID_ANY, "",
                                       style=wx.TE_PROCESS_ENTER |
                                       wx.TE_READONLY
                                       )
        sizerLabel = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY,
                                                    (_("Orientation points"))),
                                       wx.VERTICAL
                                       )
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        self.btn_ok = wx.Button(self, wx.ID_OK, "")
        btn_reset = wx.Button(self, wx.ID_CLEAR, "")

        # ----------------------Properties--------------------------------#
        self.SetTitle(_("Videomass: Rotate and flip"))
        # self.button_up.SetBackgroundColour(wx.Colour(122, 239, 255))
        self.button_up.SetToolTip(_("Reverses visual movie from bottom "
                                    "to top"))
        # self.button_left.SetBackgroundColour(wx.Colour(122, 239, 255))
        self.button_left.SetToolTip(_("Rotate view movie to left"))
        # self.button_right.SetBackgroundColour(wx.Colour(122, 239, 255))
        self.button_right.SetToolTip(_("Rotate view movie to Right"))
        # self.button_down.SetBackgroundColour(wx.Colour(122, 239, 255))
        self.button_down.SetToolTip(_("Reverses visual movie from top to "
                                      "bottom"))
        self.text_rotate.SetToolTip(_("Display show settings"))

        # ----------------------Handle layout------------------------------#
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        sizerBase.Add(sizerLabel, 0, wx.ALL | wx.EXPAND, 10)
        boxctrl = wx.BoxSizer(wx.VERTICAL)
        sizerLabel.Add(boxctrl, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 15)

        grid_sizerLabel = wx.GridSizer(1, 1, 0, 0)
        grid_sizerBase = wx.GridSizer(1, 2, 0, 0)

        boxctrl.Add(self.button_up, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 15)

        grid_sizerBase.Add(self.button_left, 0, wx.ALL |
                           wx.ALIGN_CENTER_HORIZONTAL |
                           wx.ALIGN_CENTER_VERTICAL, 15
                           )
        grid_sizerBase.Add(self.button_right, 0, wx.ALL |
                           wx.ALIGN_CENTER_HORIZONTAL |
                           wx.ALIGN_CENTER_VERTICAL, 15
                           )
        boxctrl.Add(grid_sizerBase, 0, wx.EXPAND, 0)
        boxctrl.Add(self.button_down, 0, wx.ALL |
                    wx.ALIGN_CENTER_HORIZONTAL, 15
                    )
        grid_sizerLabel.Add(self.text_rotate, 0, wx.EXPAND, 5)
        boxctrl.Add(grid_sizerLabel,  0, wx.EXPAND, 5)
        gridBtn = wx.GridSizer(1, 2, 0, 0)
        gridhelp = wx.GridSizer(1, 1, 0, 0)
        gridhelp.Add(btn_reset, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridBtn.Add(gridhelp)
        gridExit = wx.BoxSizer(wx.HORIZONTAL)
        gridExit.Add(btn_close, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridExit.Add(self.btn_ok, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        gridBtn.Add(gridExit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)
        sizerBase.Add(gridBtn, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(sizerBase)
        sizerBase.Fit(self)
        self.Layout()

        # ----------------------Binding (EVT)---------------------------------#
        self.Bind(wx.EVT_BUTTON, self.on_up, self.button_up)
        self.Bind(wx.EVT_BUTTON, self.on_left, self.button_left)
        self.Bind(wx.EVT_BUTTON, self.on_right, self.button_right)
        self.Bind(wx.EVT_BUTTON, self.on_down, self.button_down)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)

        if orientation == '':
            self.orientation = ''
        else:
            self.orientation = orientation
            self.text_rotate.SetValue(msg)

    # ----------------------Event handler (callback)--------------------------#
    def on_up(self, event):
        self.orientation = "transpose=2,transpose=2"
        self.text_rotate.SetValue(_("180° from bottom to top"))
    # ------------------------------------------------------------------#

    def on_left(self, event):
        opt = "transpose=2"
        self.orientation = opt
        self.text_rotate.SetValue(_("Rotate 90° Left"))
    # ------------------------------------------------------------------#

    def on_right(self, event):
        self.orientation = "transpose=1"
        self.text_rotate.SetValue(_("Rotate 90° Right"))
    # ------------------------------------------------------------------#

    def on_down(self, event):
        self.orientation = "transpose=2,transpose=2"
        self.text_rotate.SetValue(_("180° from top to bottom"))
    # ------------------------------------------------------------------#

    def on_reset(self, event):
        self.orientation = ""
        self.text_rotate.SetValue("")
    # ------------------------------------------------------------------#

    def on_close(self, event):
        event.Skip()
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        if you enable self.Destroy(), it delete from memory all
        data event and no return correctly. It has the right behavior
        if not used here, because it is called in the main frame.

        Event.Skip(), work correctly here. Sometimes needs to disable
        it for needs to maintain the view of the window.
        """
        self.GetValue()
        # self.Destroy()
        event.Skip()
    # ------------------------------------------------------------------#

    def GetValue(self):
        """
        This method return values via the interface GetValue()
        """
        msg = self.text_rotate.GetValue()
        return (self.orientation, msg)
###########################################################################


class VideoCrop(wx.Dialog):
    """
    Show a dialog with buttons for movie image orientation.
    TODO: make rotate button with images
    """

    def __init__(self, parent, fcrop):
        """
        Make sure you use the clear button when you finish the task.
        """
        self.w = ''  # set -1 = disable
        self.h = ''  # set -1 = disable
        self.y = ''  # set -1 = disable
        self.x = ''  # set -1 = disable

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)

        self.label_width = wx.StaticText(self, wx.ID_ANY, (_("Width")))
        self.crop_width = wx.SpinCtrl(self, wx.ID_ANY, "-1",
                                      min=-1,  max=10000, size=(-1, -1),
                                      style=wx.TE_PROCESS_ENTER
                                      )
        self.label_height = wx.StaticText(self, wx.ID_ANY, (_("Height")))
        self.crop_height = wx.SpinCtrl(self, wx.ID_ANY, "-1",
                                       min=-1, max=10000, size=(-1, -1),
                                       style=wx.TE_PROCESS_ENTER
                                       )
        self.label_X = wx.StaticText(self, wx.ID_ANY, ("X"))
        self.crop_X = wx.SpinCtrl(self, wx.ID_ANY, "-1",
                                  min=-1, max=10000, size=(-1, -1),
                                  style=wx.TE_PROCESS_ENTER
                                  )
        self.label_Y = wx.StaticText(self, wx.ID_ANY, ("Y"))
        self.crop_Y = wx.SpinCtrl(self, wx.ID_ANY, "-1",
                                  min=-1, max=10000, size=(-1, -1),
                                  style=wx.TE_PROCESS_ENTER
                                  )
        sizerLabel = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                       _("Crop Dimensions"))), wx.VERTICAL)
        btn_help = wx.Button(self, wx.ID_HELP, "")
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        self.btn_ok = wx.Button(self, wx.ID_OK, "")
        btn_reset = wx.Button(self, wx.ID_CLEAR, "")

        # --------------------Handle layout----------------------#
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        sizerBase.Add(sizerLabel, 0, wx.ALL | wx.EXPAND, 10)
        boxctrl = wx.BoxSizer(wx.VERTICAL)
        sizerLabel.Add(boxctrl, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 15)
        grid_sizerBase = wx.FlexGridSizer(1, 5, 0, 0)

        boxctrl.Add(self.label_height, 0, wx.ALL |
                    wx.ALIGN_CENTER_HORIZONTAL, 5
                    )
        boxctrl.Add(self.crop_height, 0, wx.ALL |
                    wx.ALIGN_CENTER_HORIZONTAL, 5
                    )
        grid_sizerBase.Add(self.label_Y, 0, wx.ALL |
                           wx.ALIGN_CENTER_HORIZONTAL |
                           wx.ALIGN_CENTER_VERTICAL, 5
                           )
        grid_sizerBase.Add(self.crop_Y, 0, wx.ALL |
                           wx.ALIGN_CENTER_HORIZONTAL |
                           wx.ALIGN_CENTER_VERTICAL, 5
                           )
        grid_sizerBase.Add((50, 50), 0, wx.ALL |
                           wx.ALIGN_CENTER_HORIZONTAL |
                           wx.ALIGN_CENTER_VERTICAL, 5
                           )
        grid_sizerBase.Add(self.crop_width, 0, wx.ALL |
                           wx.ALIGN_CENTER_HORIZONTAL |
                           wx.ALIGN_CENTER_VERTICAL, 5
                           )
        grid_sizerBase.Add(self.label_width, 0, wx.ALL |
                           wx.ALIGN_CENTER_HORIZONTAL |
                           wx.ALIGN_CENTER_VERTICAL, 5
                           )
        boxctrl.Add(grid_sizerBase, 1, wx.EXPAND, 0)
        boxctrl.Add(self.crop_X, 0, wx.ALL |
                    wx.ALIGN_CENTER_HORIZONTAL |
                    wx.ALIGN_CENTER_VERTICAL, 5
                    )
        boxctrl.Add(self.label_X, 0, wx.ALL |
                    wx.ALIGN_CENTER_HORIZONTAL |
                    wx.ALIGN_CENTER_VERTICAL, 5
                    )
        gridBtn = wx.GridSizer(1, 2, 0, 0)
        gridhelp = wx.GridSizer(1, 1, 0, 0)
        gridBtn.Add(gridhelp)
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        gridhelp.Add(btn_help, 0, wx.ALL, 5)
        gridexit.Add(btn_close, 0, wx.ALL, 5)
        gridexit.Add(self.btn_ok, 0, wx.ALL, 5)
        gridexit.Add(btn_reset, 0, wx.ALL, 5)
        gridBtn.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)

        sizerBase.Add(gridBtn, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizerBase)
        sizerBase.Fit(self)
        self.Layout()

        # ----------------------Properties-----------------------#
        self.SetTitle(_("Videomass: video/image crop"))
        height = (_('The height of the output video.\n'
                    'Set to -1 for disabling.'))
        width = (_('The width of the output video.\n'
                   'Set to -1 for disabling.'))
        x = (_('The horizontal position of the left edge.'))
        y = (_('The vertical position of the top edge of the left corner.'))
        self.crop_width.SetToolTip(_('Width:\n%s') % width)
        self.crop_Y.SetToolTip('Y:\n%s' % y)
        self.crop_X.SetToolTip('X:\n%s' % x)
        self.crop_height.SetToolTip(_('Height:\n%s') % height)

        # ----------------------Binding (EVT)------------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)

        if fcrop:  # set the previusly values
            s = fcrop.split(':')
            item1 = s[0][5:]  # remove `crop=` word
            s[0] = item1  # replace first item
            for i in s:
                if i.startswith('w'):
                    self.w = i[2:]
                    self.crop_width.SetValue(int(self.w))
                if i.startswith('h'):
                    self.h = i[2:]
                    self.crop_height.SetValue(int(self.h))
                if i.startswith('x'):
                    self.x = i[2:]
                    self.crop_X.SetValue(int(self.x))
                if i.startswith('y'):
                    self.y = i[2:]
                    self.crop_Y.SetValue(int(self.y))
    # ------------------------------------------------------------------#

    def on_help(self, event):
        """
        """
        page = ('https://jeanslack.github.io/Videomass/Pages/Main_Toolbar/'
                'VideoConv_Panel/Filters/FilterCrop.html')
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def on_reset(self, event):
        self.h, self.y, self.x, self.w = "", "", "", ""
        self.crop_width.SetValue(-1), self.crop_X.SetValue(-1)
        self.crop_height.SetValue(-1), self.crop_Y.SetValue(-1)
    # ------------------------------------------------------------------#

    def on_close(self, event):

        event.Skip()
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        if you enable self.Destroy(), it delete from memory all data
        event and no return correctly. It has the right behavior if not
        used here, because it is called in the main frame.

        Event.Skip(), work correctly here. Sometimes needs to disable it for
        needs to maintain the view of the window (for exemple).
        """
        self.GetValue()
        # self.Destroy()
        event.Skip()
    # ------------------------------------------------------------------#

    def GetValue(self):
        """
        This method return values via the interface GetValue()

        """
        if self.crop_width.GetValue() == -1:
            self.w = ''
        else:
            self.w = 'w=%s:' % self.crop_width.GetValue()

        if self.crop_height.GetValue() == -1:
            self.h = ''
        else:
            self.h = 'h=%s:' % self.crop_height.GetValue()

        if self.crop_X.GetValue() == -1:
            self.x = ''
        else:
            self.x = 'x=%s:' % self.crop_X.GetValue()

        if self.crop_Y.GetValue() == -1:
            self.y = ''
        else:
            self.y = 'y=%s:' % self.crop_Y.GetValue()

        s = '%s%s%s%s' % (self.w, self.h, self.x, self.y)
        if s:
            lst = len(s)
            val = '%s' % s[:lst - 1]
        else:
            val = ''
        return (val)
###########################################################################


class VideoResolution(wx.Dialog):
    """
    This class show parameters for set custom video resizing.
    Include a video size, video scaling with setdar and
    setsar options.
    """
    def __init__(self, parent, scale, dar, sar):
        """
        See FFmpeg documents for more details..
        When this dialog is called, the values previously set are returned
        for a complete reading (if there are preconfigured values)
        """
        self.width = "0"
        self.height = "0"
        self.darNum = "0"
        self.darDen = "0"
        self.sarNum = "0"
        self.sarDen = "0"

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        """constructor"""

        # ----scaling static box section
        v_scalingbox = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                         _("Scale (resize)"))), wx.VERTICAL)
        label_width = wx.StaticText(self, wx.ID_ANY, (_("Width")))
        self.spin_scale_width = wx.SpinCtrl(self, wx.ID_ANY, "0", min=-2,
                                            max=9000, style=wx.TE_PROCESS_ENTER
                                            )
        label_x1 = wx.StaticText(self, wx.ID_ANY, ("X"))
        label_x1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.spin_scale_height = wx.SpinCtrl(self, wx.ID_ANY, "0",
                                             min=-2, max=9000,
                                             style=wx.TE_PROCESS_ENTER
                                             )
        label_height = wx.StaticText(self, wx.ID_ANY, (_("Height")))
        # -------
        v_setdar = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                                  _("Setdar (display aspect "
                                                    "ratio):"))), wx.VERTICAL)
        label_num = wx.StaticText(self, wx.ID_ANY, (_("Numerator")))
        self.spin_setdarNum = wx.SpinCtrl(self, wx.ID_ANY, "0", min=0,
                                          max=99, style=wx.TE_PROCESS_ENTER,
                                          size=(-1, -1)
                                          )
        label_sepdar = wx.StaticText(self, wx.ID_ANY, ("/"))
        label_sepdar.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL,
                                     wx.BOLD, 0, ""))
        self.spin_setdarDen = wx.SpinCtrl(self, wx.ID_ANY, "0", min=0,
                                          max=99, style=wx.TE_PROCESS_ENTER,
                                          size=(-1, -1)
                                          )
        label_den = wx.StaticText(self, wx.ID_ANY, (_("Denominator")))
        # ----------
        v_setsar = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                                  _("SetSar (sample aspect "
                                                    "ratio):"))), wx.VERTICAL)
        label_num1 = wx.StaticText(self, wx.ID_ANY, (_("Numerator")))
        self.spin_setsarNum = wx.SpinCtrl(self, wx.ID_ANY, "0", min=0,
                                          max=10000, style=wx.TE_PROCESS_ENTER,
                                          size=(-1, -1)
                                          )
        label_sepsar = wx.StaticText(self, wx.ID_ANY, ("/"))
        label_sepsar.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL,
                                     wx.BOLD, 0, ""
                                     ))
        self.spin_setsarDen = wx.SpinCtrl(self, wx.ID_ANY, "0", min=0,
                                          max=10000, style=wx.TE_PROCESS_ENTER,
                                          size=(-1, -1)
                                          )
        label_den1 = wx.StaticText(self, wx.ID_ANY, (_("Denominator")))
        # ----- confirm buttons section
        btn_help = wx.Button(self, wx.ID_HELP, "")
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        self.btn_ok = wx.Button(self, wx.ID_OK, "")
        btn_reset = wx.Button(self, wx.ID_CLEAR, "")
        # ------Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(4, 1, 0, 0)
        # scaling section:
        sizer_base.Add(v_scalingbox, 1, wx.ALL | wx.EXPAND, 10)
        sizer_base.Add(v_setdar, 1, wx.ALL | wx.EXPAND, 10)
        sizer_base.Add(v_setsar, 1, wx.ALL | wx.EXPAND, 10)

        Flex_scale = wx.FlexGridSizer(1, 5, 0, 0)
        v_scalingbox.Add(Flex_scale, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        Flex_scale.Add(label_width, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_scale.Add(self.spin_scale_width, 0, wx.ALL |
                       wx.ALIGN_CENTER_VERTICAL, 5
                       )
        Flex_scale.Add(label_x1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_scale.Add(self.spin_scale_height, 0, wx.ALL |
                       wx.ALIGN_CENTER_VERTICAL, 5
                       )
        Flex_scale.Add(label_height, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_dar = wx.FlexGridSizer(1, 5, 0, 0)
        v_setdar.Add(Flex_dar, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        Flex_dar.Add(label_num, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_dar.Add(self.spin_setdarNum, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5
                     )
        Flex_dar.Add(label_sepdar, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_dar.Add(self.spin_setdarDen, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5
                     )
        Flex_dar.Add(label_den, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_sar = wx.FlexGridSizer(1, 5, 0, 0)
        v_setsar.Add(Flex_sar, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        Flex_sar.Add(label_num1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_sar.Add(self.spin_setsarNum, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5
                     )
        Flex_sar.Add(label_sepsar, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        Flex_sar.Add(self.spin_setsarDen, 0, wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL, 5
                     )
        Flex_sar.Add(label_den1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
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
        sizer_base.Add(gridBtn, 0, wx.ALL | wx.EXPAND, 5)
        # final settings:
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        # Properties
        self.SetTitle(_("Videomass: resize (change resolution)"))
        scale_str = (_('Scale (resize) the input video or image.'))
        self.spin_scale_width.SetToolTip(_('WIDTH:\n%s') % scale_str)
        self.spin_scale_height.SetToolTip(_('HEIGHT:\n%s') % scale_str)
        setdar_str = (_('Sets the Display Aspect '
                        'Ratio.\nSet to 0 to disabling.'))
        self.spin_setdarNum.SetToolTip(_('-NUMERATOR-\n%s') % setdar_str)
        self.spin_setdarDen.SetToolTip(_('-DENOMINATOR-\n%s') % setdar_str)
        setsar_str = (_('The setsar filter sets the Sample (aka Pixel) '
                        'Aspect Ratio.\nSet to 0 to disabling.'))
        self.spin_setsarNum.SetToolTip(_('-NUMERATOR-\n%s') % setsar_str)
        self.spin_setsarDen.SetToolTip(_('-DENOMINATOR-\n%s') % setsar_str)

        # ----------------------Binding (EVT)--------------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)

        if scale:
            self.width = scale.split(':')[0][8:]
            self.height = scale.split(':')[1][2:]
            self.spin_scale_width.SetValue(int(self.width))
            self.spin_scale_height.SetValue(int(self.height))
        if dar:
            self.darNum = dar.split('/')[0][7:]
            self.darDen = dar.split('/')[1]
            self.spin_setdarNum.SetValue(int(self.darNum))
            self.spin_setdarDen.SetValue(int(self.darDen))
        if sar:
            self.sarNum = sar.split('/')[0][7:]
            self.sarDen = sar.split('/')[1]
            self.spin_setsarNum.SetValue(int(self.sarNum))
            self.spin_setsarDen.SetValue(int(self.sarDen))

    # ----------------------Event handler (callback)---------------------#

    def on_help(self, event):
        """
        """
        page = ('https://jeanslack.github.io/Videomass/Pages/Main_Toolbar/'
                'VideoConv_Panel/Filters/FilterScaling.html')
        webbrowser.open(page)
    # ------------------------------------------------------------------#

    def on_reset(self, event):
        self.width, self.height = "0", "0"
        self.darNum, self.darDen = "0", "0"
        self.sarNum, self.sarDen = "0", "0"
        self.spin_scale_width.SetValue(0), self.spin_scale_height.SetValue(0)
        self.spin_setdarNum.SetValue(0), self.spin_setdarDen.SetValue(0)
        self.spin_setsarNum.SetValue(0), self.spin_setsarDen.SetValue(0)
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
        diction = {}
        self.width = '%s' % self.spin_scale_width.GetValue()
        self.height = '%s' % self.spin_scale_height.GetValue()
        self.darNum = '%s' % self.spin_setdarNum.GetValue()
        self.darDen = '%s' % self.spin_setdarDen.GetValue()
        self.sarNum = '%s' % self.spin_setsarNum.GetValue()
        self.sarDen = '%s' % self.spin_setsarDen.GetValue()

        if self.width == '0' or self.height == '0':
            size = ''
        else:
            size = 'scale=w=%s:h=%s' % (self.width, self.height)
            diction['scale'] = size

        if self.darNum == '0' or self.darDen == '0':
            setdar = ''
        else:
            setdar = 'setdar=%s/%s' % (self.darNum, self.darDen)
            diction['setdar'] = setdar

        if self.sarNum == '0' or self.sarDen == '0':
            setsar = ''
        else:
            setsar = 'setsar=%s/%s' % (self.sarNum, self.sarDen)
            diction['setsar'] = setsar

        return (diction)
#############################################################################


class Lacing(wx.Dialog):
    """
    Show a dialog for image deinterlace/interlace functions
    with advanced option for each filter.
    """

    def __init__(self, parent, deinterlace, interlace):
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
        zone1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                    _("Deinterlace"))), wx.VERTICAL)
        zone2 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (
                                    _("Interlace"))), wx.VERTICAL)

        self.ckbx_deintW3fdif = wx.CheckBox(self, wx.ID_ANY,
                                            (_("Deinterlaces (Using the "
                                               "'w3fdif' filter)"))
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
                                           (_("Deinterlaces (Using the "
                                              "'yadif' filter)"))
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
                                          (_("Interlaces (Using the "
                                             "'interlace' filter)"))
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
        # ----- confirm buttons section
        btn_help = wx.Button(self, wx.ID_HELP, "")
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        self.btn_ok = wx.Button(self, wx.ID_OK, "")
        btn_reset = wx.Button(self, wx.ID_CLEAR, "")

        # set Properties
        self.SetTitle(_("Videomass: deinterlace/interlace"))
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
        self.rdbx_Yadif_mode.SetSelection(1)
        self.rdbx_Yadif_parity.SetSelection(2)
        self.rdbx_Yadif_deint.SetSelection(0)
        self.rdbx_inter_scan.SetSelection(0)
        self.rdbx_inter_lowpass.SetSelection(1)
        self.rdbx_w3fdif.Disable(), self.rdbx_w3fdif_d.Disable(),
        self.rdbx_Yadif_mode.Disable(),
        self.rdbx_Yadif_parity.Disable(), self.rdbx_Yadif_deint.Disable(),
        self.rdbx_inter_scan.Disable(), self.rdbx_inter_lowpass.Disable()

        # ------ set Layout
        self.sizer_base = wx.BoxSizer(wx.VERTICAL)
        self.sizer_base.Add(self.enable_opt, 0, wx.ALL |
                            wx.ALIGN_RIGHT, 10
                            )
        self.sizer_base.Add(zone1, 0, wx.ALL | wx.EXPAND, 10)
        deint_grid = wx.FlexGridSizer(2, 4, 0, 0)
        zone1.Add(deint_grid)
        deint_grid.Add(self.ckbx_deintW3fdif, 0, wx.ALL, 15)
        deint_grid.Add(self.rdbx_w3fdif, 0, wx.ALL, 15)
        deint_grid.Add(self.rdbx_w3fdif_d, 0, wx.ALL, 15)
        deint_grid.Add((20, 20), 0, wx.ALL, 15)
        deint_grid.Add(self.ckbx_deintYadif, 0, wx.ALL, 15)
        deint_grid.Add(self.rdbx_Yadif_mode, 0, wx.ALL, 15)
        deint_grid.Add(self.rdbx_Yadif_parity, 0, wx.ALL, 15)
        deint_grid.Add(self.rdbx_Yadif_deint, 0, wx.ALL, 15)
        self.sizer_base.Add(zone2, 0, wx.ALL | wx.EXPAND, 10)
        inter_grid = wx.FlexGridSizer(1, 3, 0, 0)
        zone2.Add(inter_grid)
        inter_grid.Add(self.ckbx_interlace, 0, wx.ALL, 15)
        inter_grid.Add(self.rdbx_inter_scan, 0, wx.ALL, 15)
        inter_grid.Add(self.rdbx_inter_lowpass, 0, wx.ALL, 15)

        # confirm btn section:
        self.gridBtn = wx.GridSizer(1, 2, 0, 0)
        gridhelp = wx.GridSizer(1, 1, 0, 0)

        gridhelp.Add(btn_help, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.gridBtn.Add(gridhelp)
        self.gridexit = wx.BoxSizer(wx.HORIZONTAL)

        self.gridexit.Add(btn_close, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.gridexit.Add(self.btn_ok, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.gridexit.Add(btn_reset, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.gridBtn.Add(self.gridexit, 0, wx.ALL |
                         wx.ALIGN_RIGHT | wx.RIGHT, 0
                         )
        self.sizer_base.Add(self.gridBtn, 0, wx.ALL | wx.EXPAND, 5)
        # final settings:
        self.SetSizer(self.sizer_base)
        self.sizer_base.Fit(self)
        self.Layout()

        self.ckbx_deintW3fdif.SetToolTip(_('Deinterlace the input video '
                                           'with `w3fdif` filter'))
        self.rdbx_w3fdif.SetToolTip(_('Set the interlacing filter '
                                      'coefficients.'))
        self.rdbx_w3fdif_d.SetToolTip(_('Specify which frames to '
                                        'deinterlace.'))
        toolt = _('Deinterlace the input video with `yadif` filter. '
                  'For FFmpeg is the best and fastest choice ')
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
        toolt = _('lowpas:\nEnable (default) or disable the vertical '
                  'lowpass filter to avoid twitter interlacing and reduce '
                  'moire patterns.\nDefault is no setting.')
        self.rdbx_inter_lowpass.SetToolTip(toolt)

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
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
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
                if indx[1] == '-1':
                    parity = 2
                self.rdbx_Yadif_mode.SetSelection(int(indx[0]))
                self.rdbx_Yadif_parity.SetSelection(parity)
                self.rdbx_Yadif_deint.SetSelection(int(indx[2]))

            elif self.cmd_opt["deinterlace"].startswith('w3fdif'):
                self.ckbx_deintW3fdif.SetValue(True)
                self.ckbx_deintYadif.Disable()
                self.ckbx_interlace.Disable()
                self.rdbx_w3fdif.Enable()
                self.rdbx_w3fdif_d.Enable()
                indx = self.cmd_opt["deinterlace"].split('=')[1].split(':')
                if indx[0] == 'complex':
                    filt = 1
                elif indx[0] == 'simple':
                    filt = 0
                self.rdbx_w3fdif.SetSelection(filt)
                if indx[1] == 'all':
                    deint = 0
                elif indx[1] == 'interlaced':
                    deint = 1
                self.rdbx_w3fdif_d.SetSelection(deint)

        elif 'interlace' in self.cmd_opt:
            self.ckbx_interlace.SetValue(True)
            self.ckbx_deintW3fdif.Disable(), self.ckbx_deintYadif.Disable(),
            self.rdbx_inter_scan.Enable(), self.rdbx_inter_lowpass.Enable(),

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
        """
        if self.ckbx_deintW3fdif.IsChecked():
            self.rdbx_w3fdif.Enable(), self.rdbx_w3fdif_d.Enable(),
            self.ckbx_deintYadif.Disable(), self.ckbx_interlace.Disable()
            self.cmd_opt["deinterlace"] = "w3fdif=complex:all"

        elif not self.ckbx_deintW3fdif.IsChecked():
            self.rdbx_w3fdif.Disable(), self.rdbx_w3fdif_d.Disable(),
            self.ckbx_deintYadif.Enable(), self.ckbx_interlace.Enable(),
            self.cmd_opt.clear()
    # ------------------------------------------------------------------#

    def on_W3fdif_filter(self, event):
        """
        """
        self.cmd_opt["deinterlace"] = "w3fdif=%s:%s" % (
                                self.rdbx_w3fdif.GetStringSelection(),
                                self.rdbx_w3fdif_d.GetStringSelection()
                                                    )
    # ------------------------------------------------------------------#

    def on_W3fdif_deint(self, event):
        """
        """
        self.cmd_opt["deinterlace"] = "w3fdif=%s:%s" % (
                                self.rdbx_w3fdif.GetStringSelection(),
                                self.rdbx_w3fdif_d.GetStringSelection()
                                                    )
    # ------------------------------------------------------------------#

    def on_DeintYadif(self, event):
        """
        """
        if self.ckbx_deintYadif.IsChecked():
            self.ckbx_deintW3fdif.Disable(), self.rdbx_Yadif_mode.Enable(),
            self.rdbx_Yadif_parity.Enable(), self.rdbx_Yadif_deint.Enable(),
            self.ckbx_interlace.Disable(),
            self.cmd_opt["deinterlace"] = "yadif=1:-1:0"

        elif not self.ckbx_deintYadif.IsChecked():
            self.ckbx_deintW3fdif.Enable(), self.rdbx_Yadif_mode.Disable(),
            self.rdbx_Yadif_parity.Disable(), self.rdbx_Yadif_deint.Disable(),
            self.ckbx_interlace.Enable(),
            self.cmd_opt.clear()
    # ------------------------------------------------------------------#

    def on_modeYadif(self, event):
        """
        """
        parity = self.rdbx_Yadif_parity.GetStringSelection().split(',')
        self.cmd_opt["deinterlace"] = "yadif=%s:%s:%s" % (
                                self.rdbx_Yadif_mode.GetStringSelection()[0],
                                parity[0],
                                self.rdbx_Yadif_deint.GetStringSelection()[0]
                                                    )
    # ------------------------------------------------------------------#

    def on_parityYadif(self, event):
        """
        """
        parity = self.rdbx_Yadif_parity.GetStringSelection().split(',')
        self.cmd_opt["deinterlace"] = "yadif=%s:%s:%s" % (
                                self.rdbx_Yadif_mode.GetStringSelection()[0],
                                parity[0],
                                self.rdbx_Yadif_deint.GetStringSelection()[0]
                                                    )
    # ------------------------------------------------------------------#

    def on_deintYadif(self, event):
        """
        """
        parity = self.rdbx_Yadif_parity.GetStringSelection().split(',')
        self.cmd_opt["deinterlace"] = "yadif=%s:%s:%s" % (
                                self.rdbx_Yadif_mode.GetStringSelection()[0],
                                parity[0],
                                self.rdbx_Yadif_deint.GetStringSelection()[0]
                                                    )
    # ------------------------------------------------------------------#

    def on_Interlace(self, event):
        """
        """
        if self.ckbx_interlace.IsChecked():
            self.ckbx_deintW3fdif.Disable(), self.ckbx_deintYadif.Disable(),
            self.rdbx_inter_scan.Enable(), self.rdbx_inter_lowpass.Enable(),
            self.cmd_opt["interlace"] = "interlace=scan=tff:lowpass=1"

        elif not self.ckbx_interlace.IsChecked():
            self.ckbx_deintW3fdif.Enable(), self.ckbx_deintYadif.Enable(),
            self.rdbx_inter_scan.Disable(), self.rdbx_inter_lowpass.Disable(),
            self.cmd_opt.clear()
    # ------------------------------------------------------------------#

    def on_intScan(self, event):
        """
        """
        self.cmd_opt["interlace"] = "interlace=%s:%s" % (
                                self.rdbx_inter_scan.GetStringSelection(),
                                self.rdbx_inter_lowpass.GetStringSelection(),
                                                     )
    # ------------------------------------------------------------------#

    def on_intLowpass(self, event):
        """
        """
        self.cmd_opt["interlace"] = "interlace=%s:%s" % (
                                self.rdbx_inter_scan.GetStringSelection(),
                                self.rdbx_inter_lowpass.GetStringSelection(),
                                                     )
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
        self.rdbx_Yadif_mode.SetSelection(1)
        self.rdbx_Yadif_parity.SetSelection(2)
        self.rdbx_Yadif_deint.SetSelection(0)
        self.rdbx_inter_scan.SetSelection(0)
        self.rdbx_inter_lowpass.SetSelection(1)
        self.rdbx_w3fdif.Disable(), self.rdbx_w3fdif_d.Disable(),
        self.rdbx_Yadif_mode.Disable(), self.rdbx_Yadif_parity.Disable(),
        self.rdbx_Yadif_deint.Disable(), self.rdbx_inter_scan.Disable(),
        self.rdbx_inter_lowpass.Disable()
    # ------------------------------------------------------------------#

    def on_help(self, event):
        """
        """
        page = ('https://jeanslack.github.io/Videomass/Pages/Main_Toolbar/'
                'VideoConv_Panel/Filters/Deint_Inter.html')
        webbrowser.open(page)
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
        return self.cmd_opt
#############################################################################


class Denoisers(wx.Dialog):
    """
    Show a dialog for set denoiser filter
    """
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
        self.btn_ok = wx.Button(self, wx.ID_OK, "")
        btn_reset = wx.Button(self, wx.ID_CLEAR, "")
        # ------ set Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(zone, 1, wx.ALL | wx.EXPAND, 10)
        grid_den = wx.FlexGridSizer(2, 2, 0, 0)
        zone.Add(grid_den)
        grid_den.Add(self.ckbx_nlmeans, 0,
                     wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL |
                     wx.ALIGN_CENTER_HORIZONTAL,
                     15)
        grid_den.Add(self.rdb_nlmeans, 0,
                     wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL |
                     wx.ALIGN_CENTER_HORIZONTAL,
                     15)
        grid_den.Add(self.ckbx_hqdn3d, 0,
                     wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL |
                     wx.ALIGN_CENTER_HORIZONTAL,
                     15)
        grid_den.Add(self.rdb_hqdn3d, 0,
                     wx.ALL |
                     wx.ALIGN_CENTER_VERTICAL |
                     wx.ALIGN_CENTER_HORIZONTAL,
                     15)
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
        sizer_base.Add(gridBtn, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        # set Properties
        self.SetTitle(_("Videomass: denoisers filters"))
        tool = _('nlmeans:\n(Denoise frames using Non-Local Means algorithm '
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
        """
        page = ('https://jeanslack.github.io/Videomass/Pages/Main_Toolbar/'
                'VideoConv_Panel/Filters/Denoisers.html')
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
