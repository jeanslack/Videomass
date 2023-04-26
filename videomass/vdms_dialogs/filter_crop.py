# -*- coding: UTF-8 -*-
"""
Name: filter_crop.py
Porpose: Show dialog to get video crop values based on FFmpeg syntax
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: April.09.2023
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
import wx.lib.statbmp
from pubsub import pub
from videomass.vdms_threads.generic_task import FFmpegGenericTask
from videomass.vdms_utils.utils import get_milliseconds
from videomass.vdms_utils.utils import milliseconds2clocksec
from videomass.vdms_utils.utils import clockset
from videomass.vdms_io.make_filelog import make_log_template


def make_bitmap(width, height, image):
    """
    Resize the image to the given size and convert it to a
    bitmap object.

    Returns a wx.Bitmap object

    """
    bitmap = wx.Bitmap(image)
    img = bitmap.ConvertToImage()
    img = img.Scale(int(width), int(height), wx.IMAGE_QUALITY_NORMAL)
    bmp = img.ConvertToBitmap()

    return bmp


class Actor(wx.lib.statbmp.GenStaticBitmap):
    """
    From an explanation by Robin Dunn, where he discusses
    how to rotate images with DC:
    <https://discuss.wxpython.org/t/questions-about-rotation/34064>

    Actor uses the GenStaticBitmap which is a generic implementation
    of wx.StaticBitmap, for display larger images portably.

    This class is useful for drawing a selection rectangle on the image
    given a position specified by the X and Y coordinates and the size
    by the W (width) and H (height) lines.

    """
    def __init__(self, parent, bitmap, idNum, imgFile, **kwargs):
        """
        Attributes defines the rectangle dimensions and coordinates,
        a parent and a current_bmp. First make sure you scale the
        image to fit on parent, e.g. a panel.
        """
        self.h = 0  # rectangle height
        self.w = 0  # rectangle width
        self.x = 0  # rectangle x axis
        self.y = 0  # rectangle y axis
        self.startpos = 0, 0  # start x,y axis clicked
        self.endpos = 0, 0  # end x,y axis on releasing

        wx.lib.statbmp.GenStaticBitmap.__init__(self, parent, -1,
                                                bitmap, **kwargs)
        self.current_bmp = bitmap

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOTION, self.on_move)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_leftdown)
        self.Bind(wx.EVT_LEFT_UP, self.on_leftup)
    # ------------------------------------------------------------------#

    def on_move(self, event):
        """
        Dragging-mouse over the cropping area, it sends
        the coordinates for drawing the rectangle.
        """
        self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
        if event.Dragging() and event.LeftIsDown():
            pos = event.GetPosition()
            x, y = pos[0], pos[1]
            # draw rectangle opposite to mouse direction:
            w, h = self.startpos[0] - x, self.startpos[1] - y
            self.onRedraw(x, y, w, h)
    # ------------------------------------------------------------------#

    def on_leftdown(self, event):
        """
        Left-click event. On mouse click stores the initial
        positions in pixels for the x/y axis points.
        """
        self.startpos = event.GetPosition()
    # ------------------------------------------------------------------#

    def on_leftup(self, event):
        """
        Event on releasing the left mouse button.
        Note: seeking x, y minimum values as dc x
        even to top left and y to bottom left.
        (end position click released)
        """
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        self.endpos = event.GetPosition()
        x = min(self.startpos[0], self.endpos[0])
        y = min(self.startpos[1], self.endpos[1])
        w, h = abs(self.w), abs(self.h)
        self.startpos, self.endpos = (0, 0), (0, 0)
        self.onRedraw(x, y, w, h)
        pub.sendMessage("TO_REAL_SCALE", msg=[x, y, w, h])
    # ------------------------------------------------------------------#

    def OnPaint(self, event=None):
        """
        When instantiating the Actor class, this event is
        executed last. This method is needed to set initial
        image on panel and/or to set crop area previously
        drawn on reopen this dialog.
        """
        dc = wx.PaintDC(self)  # draw window boundary
        dc.DrawBitmap(self.current_bmp, 0, 0, True)
        dc.SetPen(wx.Pen('red', 2, wx.PENSTYLE_SOLID))
        dc.SetBrush(wx.Brush('green', wx.BRUSHSTYLE_TRANSPARENT))
        dc.DrawRectangle(round(self.x + 1),
                         round(self.y + 1),
                         round(self.w + 1),
                         round(self.h + 1),
                         )
    # ------------------------------------------------------------------#

    def onRedraw(self, x, y, w, h):
        """
        Update Drawing: A transparent background rectangle in a
        bitmap object.
        NOTE dc.SetBrush(wx.Brush(wx.Colour(30, 30, 30, 128))) would set
        a useful transparent gradation color but it doesn't work on windows
        and gtk2.
        """
        self.h, self.w, self.x, self.y = h, w, x, y
        dc = wx.ClientDC(self)
        dc.Clear()  # needed if image has trasparences
        dc.DrawBitmap(self.current_bmp, 0, 0, True)
        dc.SetPen(wx.Pen('red', 2, wx.PENSTYLE_SOLID))
        dc.SetBrush(wx.Brush('green', wx.BRUSHSTYLE_TRANSPARENT))
        dc.DrawRectangle(round(self.x + 1),
                         round(self.y + 1),
                         round(self.w + 1),
                         round(self.h + 1),
                         )


class Crop(wx.Dialog):
    """
    A dialog tool to get video crop values based on FFmpeg syntax.
    See ``av_conversions.py`` -> ``on_Set_crop`` method for
    how to use this class.
    """
    get = wx.GetApp()
    OS = get.appset['ostype']
    LOGDIR = get.appset['logdir']
    TMPROOT = os.path.join(get.appset['cachedir'], 'tmp', 'Crop')
    TMPSRC = os.path.join(TMPROOT, 'tmpsrc')
    os.makedirs(TMPSRC, mode=0o777, exist_ok=True)
    BACKGROUND = '#1b0413'

    def __init__(self, parent, *args, **kwa):
        """
        Attributes defined here:

            self.w_dc       width size for DC (aka monitor width)
            self.h_dc       height size for DC (aka monitor height)
            self.x_dc       horizontal axis for DC
            self.y_dc       vertical axis for DC
            self.height     unscaled height of the source video
            self.width      unscaled width of the source video
            toscale         scale factor
            self.h_scaled   height ratio
            self.w_scaled   width ratio

        The images (also the panel and the DC) are resized to keep
        the scale factor.
        """
        # cropping values for monitor preview
        self.w_dc = 0
        self.h_dc = 0
        self.y_dc = 0
        self.x_dc = 0
        # current video size
        self.width = kwa['width']
        self.height = kwa['height']
        # resizing values preserving aspect ratio for monitor
        toscale = 220 if self.height >= self.width else 350
        self.h_scaled = round((self.height / self.width) * toscale)
        self.w_scaled = round((self.width / self.height) * self.h_scaled)
        self.filename = kwa['filename']  # selected filename on queued list
        name = os.path.splitext(os.path.basename(self.filename))[0]
        self.frame = os.path.join(f'{Crop.TMPSRC}', f'{name}.png')  # image
        self.fileclock = os.path.join(Crop.TMPROOT, f'{name}.clock')
        tcheck = clockset(kwa['duration'], self.fileclock)
        self.clock = tcheck['duration']
        self.mills = tcheck['millis']
        if os.path.exists(self.frame):
            self.image = self.frame
        else:  # make empty
            self.image = wx.Bitmap(self.w_scaled, self.h_scaled)
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        self.panelrect = wx.Panel(self, wx.ID_ANY,
                                  size=(self.w_scaled, self.h_scaled)
                                  )
        bmp = make_bitmap(self.w_scaled, self.h_scaled, self.image)
        self.bob = Actor(self.panelrect, bmp, 1, "")
        sizerBase.Add(self.panelrect, 0, wx.ALL | wx.CENTER, 5)
        sizersize = wx.BoxSizer(wx.VERTICAL)
        sizerBase.Add(sizersize, 0, wx.ALL | wx.CENTER, 5)
        msg = _("Source size: {0} x {1} pixels").format(self.width,
                                                        self.height)
        label1 = wx.StaticText(self, wx.ID_ANY,
                               label=msg,
                               style=wx.ST_NO_AUTORESIZE
                               | wx.ALIGN_CENTRE_HORIZONTAL,
                               )
        sizersize.Add(label1, 0, wx.CENTER | wx.EXPAND)
        msg = _("Search for a specific frame")
        sizer_load = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (msg)),
                                       wx.HORIZONTAL)
        sizerBase.Add(sizer_load, 0, wx.ALL | wx.CENTER, 5)
        self.slider = wx.Slider(self, wx.ID_ANY,
                                get_milliseconds(self.clock),
                                0,
                                self.mills,
                                size=(250, -1),
                                style=wx.SL_HORIZONTAL,
                                )
        sizer_load.Add(self.slider, 0, wx.ALL | wx.CENTER, 5)
        self.txttime = wx.StaticText(self, wx.ID_ANY, self.clock)
        sizer_load.Add(self.txttime, 0, wx.ALL | wx.CENTER, 10)
        self.btn_load = wx.Button(self, wx.ID_ANY, _("Load"))
        self.btn_load.Disable()
        sizer_load.Add(self.btn_load, 0, wx.ALL | wx.CENTER, 5)
        boxs = wx.StaticBox(self, wx.ID_ANY, (_("Cropping area selection ")))
        sizerLabel = wx.StaticBoxSizer(boxs, wx.VERTICAL)
        sizerBase.Add(sizerLabel, 0, wx.ALL | wx.EXPAND, 5)
        boxctrl = wx.BoxSizer(wx.VERTICAL)
        sizerLabel.Add(boxctrl, 0, wx.CENTRE)
        label_height = wx.StaticText(self, wx.ID_ANY, (_("Height")))
        boxctrl.Add(label_height, 0, wx.ALL | wx.CENTRE, 0)
        self.spin_h = wx.SpinCtrl(self, wx.ID_ANY, "0", min=0,
                                  max=self.height, size=(-1, -1),
                                  style=wx.TE_PROCESS_ENTER
                                  | wx.SP_ARROW_KEYS,
                                  )
        boxctrl.Add(self.spin_h, 0, wx.CENTRE)
        grid_sizerBase = wx.FlexGridSizer(1, 5, 0, 0)
        boxctrl.Add(grid_sizerBase, 0, wx.CENTRE, 0)
        label_X = wx.StaticText(self, wx.ID_ANY, ("X"))
        grid_sizerBase.Add(label_X, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)

        self.spin_x = wx.SpinCtrl(self, wx.ID_ANY, "0", min=-1,
                                  max=self.width, size=(-1, -1),
                                  style=wx.TE_PROCESS_ENTER
                                  | wx.SP_ARROW_KEYS
                                  )
        grid_sizerBase.Add(self.spin_x, 0, wx.ALL | wx.CENTRE, 5)

        self.btn_centre = wx.Button(self, wx.ID_ANY, _("Center"))
        grid_sizerBase.Add(self.btn_centre, 0, wx.ALL
                           | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_w = wx.SpinCtrl(self, wx.ID_ANY, "0", min=0,
                                  max=self.width,
                                  size=(-1, -1),
                                  style=wx.TE_PROCESS_ENTER
                                  | wx.SP_ARROW_KEYS,
                                  )
        grid_sizerBase.Add(self.spin_w, 0, wx.ALL | wx.CENTRE, 5)

        label_width = wx.StaticText(self, wx.ID_ANY, (_("Width")))
        grid_sizerBase.Add(label_width, 0, wx.RIGHT
                           | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_y = wx.SpinCtrl(self, wx.ID_ANY, "0", min=-1,
                                  max=self.height, size=(-1, -1),
                                  style=wx.TE_PROCESS_ENTER
                                  | wx.SP_ARROW_KEYS
                                  )
        boxctrl.Add(self.spin_y, 0, wx.CENTRE)
        label_Y = wx.StaticText(self, wx.ID_ANY, ("Y"))
        boxctrl.Add(label_Y, 0, wx.BOTTOM | wx.CENTRE, 5)
        # bottom layout for buttons
        gridBtn = wx.GridSizer(1, 2, 0, 0)
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_reset = wx.Button(self, wx.ID_ANY, _("Reset"))
        btn_reset.SetBitmap(args[1], wx.LEFT)
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
        self.panelrect.SetBackgroundColour(wx.Colour(Crop.BACKGROUND))
        if Crop.OS == 'Darwin':
            label1.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            label1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self.SetTitle(_("Crop Filter"))
        self.spin_w.SetToolTip(_('Crop to width'))
        self.spin_y.SetToolTip(_('Move vertically - set to -1 to center '
                                 'the vertical axis'))
        self.spin_x.SetToolTip(_('Move horizontally - set to -1 to center '
                                 'the horizontal axis'))
        self.spin_h.SetToolTip(_('Crop to height'))

        # ----------------------Binding (EVT)------------------------#
        self.Bind(wx.EVT_SPINCTRL, self.onWidth, self.spin_w)
        self.Bind(wx.EVT_SPINCTRL, self.onHeight, self.spin_h)
        self.Bind(wx.EVT_SPINCTRL, self.onX, self.spin_x)
        self.Bind(wx.EVT_SPINCTRL, self.onY, self.spin_y)
        self.Bind(wx.EVT_BUTTON, self.onCentre, self.btn_centre)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.on_Seek, self.slider)
        self.Bind(wx.EVT_BUTTON, self.image_loader, self.btn_load)

        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)
        # self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        pub.subscribe(self.to_real_scale_coords, "TO_REAL_SCALE")

        if not self.mills:
            self.slider.Disable()
        self.image_loader(self)

        if args[0]:  # fcrop previusly values
            self.default(args[0])
    # ------------------------------------------------------------------#

    def default(self, fcrop):
        """
        Set controls to previous settings
        """
        s = fcrop.split(':')
        s[0] = s[0][5:]  # removing `crop=` word on first item
        self.spin_w.SetValue(int(s[0][2:]))
        self.spin_h.SetValue(int(s[1][2:]))
        self.spin_x.SetValue(int(s[2][2:]))
        self.spin_y.SetValue(int(s[3][2:]))

        self.onWidth(self)  # set min/max horizontal axis
        self.onHeight(self)  # set min/max vertical axis
    # ------------------------------------------------------------------#

    def on_Seek(self, event):
        """
        gets value from time slider, converts it to clock format
        e.g (00:00:00), and sets the label with the converted value.
        """
        seek = self.slider.GetValue()
        clock = milliseconds2clocksec(seek, rounds=True)  # to 24-hour
        self.txttime.SetLabel(clock)  # update StaticText
        if not self.btn_load.IsEnabled():
            self.btn_load.Enable()
    # ------------------------------------------------------------------#

    def image_loader(self, event):
        """
        Load in a wx.dc (device context) image frame
        at a given time clock point. Note, milliseconds
        must not be greater than the max time nor less
        than the min time (see seek).
        """
        logfile = make_log_template('generic_task.log',
                                    Crop.LOGDIR,
                                    mode="w",
                                    )
        if not self.mills:
            sseg = ''
        else:
            seek = self.slider.GetValue()
            self.clock = milliseconds2clocksec(seek, rounds=True)  # to 24-HH
            sseg = f'-ss {self.clock}'

        arg = (f'{sseg} -i "{self.filename}" -f image2 '
               f'-update 1 -frames:v 1 -y "{self.frame}"')
        thread = FFmpegGenericTask(arg, 'Crop', logfile)
        thread.join()  # wait end thread
        error = thread.status
        if error:
            wx.MessageBox(f'{error}', 'ERROR', wx.ICON_ERROR)
            return
        if sseg:
            with open(self.fileclock, "w", encoding='utf8') as atime:
                atime.write(self.clock)
        self.btn_load.Disable()
        self.image = self.frame  # update with new frame
        bmp = make_bitmap(self.w_scaled, self.h_scaled, self.image)
        self.bob.current_bmp = bmp
        self.onDrawing()
    # ------------------------------------------------------------------#

    def to_real_scale_coords(self, msg):
        """
        Update controls values to real scale coordinates.
        This method is called using pub/sub protocol
        subscribing "UPDATE_DISPLAY_SCALE".
        """
        x_scale = self.width / self.w_scaled
        y_scale = self.height / self.h_scaled
        self.spin_x.SetValue(round(msg[0] * x_scale))
        self.spin_y.SetValue(round(msg[1] * y_scale))
        self.spin_w.SetValue(round(msg[2] * x_scale))
        self.spin_h.SetValue(round(msg[3] * y_scale))
    # ------------------------------------------------------------------#

    def onDrawing(self):
        """
        Converting coordinate values to scale factor to update
        the rectangle's position and size.
        """
        x_scale = self.w_scaled / self.width
        y_scale = self.h_scaled / self.height

        self.w_dc = self.spin_w.GetValue() * x_scale
        self.h_dc = self.spin_h.GetValue() * y_scale

        if self.spin_y.GetValue() == -1:
            self.y_dc = (self.h_scaled / 2) - (self.h_dc / 2)
        else:
            self.y_dc = self.spin_y.GetValue() * y_scale

        if self.spin_x.GetValue() == -1:
            self.x_dc = (self.w_scaled / 2) - (self.w_dc / 2)
        else:
            self.x_dc = self.spin_x.GetValue() * x_scale

        self.bob.onRedraw(self.x_dc,
                          self.y_dc,
                          self.w_dc,
                          self.h_dc,
                          )
    # ------------------------------------------------------------------#

    def onWidth(self, event):
        """
        Sets the limit to the minimum and maximum values for the
        horizontal X axis in relation to the values set for the
        width of the crop.
        If the maximum allowed value is set to the width of the crop,
        the X axis will be set to `min, max = 0, 0` i.e. disabled.

        The maximum allowed value for the width of the crop is
        established in the `self.width` attribute

        """
        if self.spin_w.GetValue() == self.width:
            self.spin_x.SetMax(0)
            self.spin_x.SetMin(0)
        else:
            self.spin_x.SetMax(self.width - self.spin_w.GetValue())
            self.spin_x.SetMin(-1)

        self.onDrawing()
    # ------------------------------------------------------------------#

    def onHeight(self, event):
        """
        Sets the limit to the minimum and maximum values for the
        vertical Y axis in relation to the values set for the
        height of the crop.
        If the maximum allowed value is set to the height of the crop,
        the Y axis will be set to `min, max = 0, 0` i.e. disabled.

        The maximum allowed value for the height of the crop is
        established in the `self.height` attribute

        """
        if self.spin_h.GetValue() == self.height:
            self.spin_y.SetMax(0), self.spin_y.SetMin(0)
        else:
            self.spin_y.SetMax(self.height - self.spin_h.GetValue())
            self.spin_y.SetMin(-1)

        self.onDrawing()
    # ------------------------------------------------------------------#

    def onX(self, event):
        """
        self.spin_x callback
        """
        self.onDrawing()
    # ------------------------------------------------------------------#

    def onY(self, event):
        """
        self.spin_y callback
        """
        self.onDrawing()
    # ------------------------------------------------------------------#

    def onCentre(self, event):
        """
        Sets coordinates X, Y to center if not `GetMax == 0` .
        `GetMax == 0` means that the maximum size of the crop
        has been setted and the X or Y axes cannot be setted anymore.

        """
        if self.spin_y.GetMax():
            y = (self.height / 2) - (self.spin_h.GetValue() / 2)
            self.spin_y.SetValue(round(y))
        if self.spin_x.GetMax():
            x = (self.width / 2) - (self.spin_w.GetValue() / 2)
            self.spin_x.SetValue(round(x))
        if self.spin_y.GetMax() or self.spin_x.GetMax():
            self.onDrawing()
    # ------------------------------------------------------------------#

    def on_reset(self, event):
        """
        Reset all control values
        """
        self.spin_y.SetMin(-1)
        self.spin_y.SetMax(self.height)
        self.spin_x.SetMin(-1)
        self.spin_x.SetMax(self.width)
        self.spin_w.SetValue(0)
        self.spin_x.SetValue(0)
        self.spin_h.SetValue(0)
        self.spin_y.SetValue(0)
        self.onDrawing()
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
        Note: -1 for X and Y coordinates means center, which are
        no longer supported by the FFmpeg syntax.
        """
        width = self.spin_w.GetValue()
        height = self.spin_h.GetValue()
        x_axis = self.spin_x.GetValue()
        y_axis = self.spin_y.GetValue()

        if width and height:
            if x_axis == -1:
                pos = round((self.width / 2) - (width / 2))
                horiz_pos = f'x={pos}:'
            else:
                horiz_pos = f'x={x_axis}:'

            if y_axis == -1:
                pos = round((self.height / 2) - (height / 2))
                vert_pos = f'y={pos}:'
            else:
                vert_pos = f'y={y_axis}:'

            val = f'w={width}:h={height}:{horiz_pos}{vert_pos}'
            return val[:len(val) - 1]  # remove last ':' string

        return None
