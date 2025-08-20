# -*- coding: UTF-8 -*-
"""
Name: filter_crop.py
Porpose: A dialog to get video crop values based on FFmpeg syntax
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
import wx.lib.statbmp
import wx.lib.colourselect as csel
from pubsub import pub
from videomass.vdms_threads.generic_task import FFmpegGenericTask
from videomass.vdms_utils.utils import time_to_integer
from videomass.vdms_utils.utils import integer_to_time
from videomass.vdms_utils.utils import clockset
from videomass.vdms_io.make_filelog import make_log_template


def make_bitmap(width, height, fname):
    """
    Resize the image to the given size and convert it to a
    bitmap object.
    Returns a wx.Bitmap object
    """
    img = wx.Image(fname)
    img = img.Scale(int(width), int(height), wx.IMAGE_QUALITY_NORMAL)
    bmp = img.ConvertToBitmap()
    return bmp


class Actor(wx.lib.statbmp.GenStaticBitmap):
    """
    This class is useful for drawing a rubberband rectangle
    over a static bitmap using DC to select specific areas
    on an image. Implements the ability to draw with mouse
    movements or by dynamically passing the coordinates to the
    `onRedraw` method.

    Inspired by an explanation by Robin Dunn, where he discusses
    how to rotate images with DC:
    <https://discuss.wxpython.org/t/questions-about-rotation/34064>

    This `Actor` uses GenStaticBitmap in his show, which is a generic
    implementation of wx.StaticBitmap, to display larger images portably
    with advantages on all mouse events (such as detection of mouse
    motions, mouse clicks and so on).
    see <https://docs.wxpython.org/wx.lib.statbmp.html>
    """
    def __init__(self, parent, bitmap, idNum, imgFile, **kwargs):
        """
        Attributes defines the rectangle dimensions and coordinates,
        a parent and a bitmap. First make sure you scale the
        image to fit on parent, e.g. a panel.
        """
        self.rect = 0, 0, 0, 0  # x,y,w,h coords
        self.startpos = 0, 0  # start x,y axis on initial clicked
        self.bc = (255, 0, 0, 255)  # background color

        wx.lib.statbmp.GenStaticBitmap.__init__(self, parent, -1,
                                                bitmap, **kwargs)
        self.bitmap = bitmap

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOTION, self.on_move)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_leftdown)
        self.Bind(wx.EVT_LEFT_UP, self.on_leftup)

        self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
    # ------------------------------------------------------------------#

    def on_leftdown(self, event):
        """
        Left-click event. On mouse click stores the initial
        positions in pixels for the x/y axis points.
        """
        self.CaptureMouse()
        self.startpos = event.GetPosition()
    # ------------------------------------------------------------------#

    def on_move(self, event):
        """
        Dragging-mouse over the image, it sends the
        coordinates points for drawing the rectangle.
        """
        if event.Dragging() and event.LeftIsDown():
            rect = wx.Rect(self.startpos, event.GetPosition())
            pub.sendMessage("TO_REAL_SCALE", msg=rect)
            self.onRedraw(rect)
    # ------------------------------------------------------------------#

    def on_leftup(self, event):
        """
        Event on releasing the left mouse button.
        """
        if self.HasCapture():
            self.ReleaseMouse()
        self.startpos = 0, 0
    # ------------------------------------------------------------------#

    def OnPaint(self, event=None):
        """
        This event is always needed to repaint the area
        during window changes, i.e. startup, reopening,
        resizing, and hiding.
        """
        wx.PaintDC(self)  # draw window boundary
        self.Refresh()  # needed on wayland to make it work
        self.onRedraw(self.rect)
    # ------------------------------------------------------------------#

    def onRedraw(self, rect):
        """
        Updates the coordinates of the rectangle selection area
        redrawing the bitmap object. The brush color (for the box's
        interior) it has the same colour as pen color but 40%
        transparency.
        """
        self.rect = rect
        dc = wx.ClientDC(self)
        if 'wxMac' not in wx.PlatformInfo:
            self.SetDoubleBuffered(True)  # prevents flickers
            dc = wx.GCDC(dc)  # needed for brush transparency
        dc.Clear()
        dc.DrawBitmap(self.bitmap, 0, 0, True)
        dc.SetPen(wx.Pen(self.bc, 1, wx.PENSTYLE_SOLID))
        bcolor = wx.Colour(self.bc[0], self.bc[1], self.bc[2], 40)
        dc.SetBrush(wx.Brush(bcolor))
        dc.DrawRectangle(self.rect)
    # ------------------------------------------------------------------#

    def oncolor(self, event, color=None):
        """
        Button event to get color from colourselect dialog
        """
        if color:
            self.bc = color
        else:
            color = event.GetValue()
            self.bc = color
            self.onRedraw(self.rect)
    # ------------------------------------------------------------------#

    def setbitmap(self, bitmap):
        """
        Set a new bitmap object
        """
        self.bitmap = bitmap
        self.onRedraw(self.rect)


class Crop(wx.Dialog):
    """
    A dialog to get video crop values based on FFmpeg syntax.
    See ``av_conversions.py`` -> ``on_Set_crop`` method/event
    for how to use this class.
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
        Some attributes defined here:

            self.w_dc       width size for DC (aka monitor width)
            self.h_dc       height size for DC (aka monitor height)
            self.x_dc       horizontal axis for DC
            self.y_dc       vertical axis for DC
            self.height     unscaled height of the source video
            self.width      unscaled width of the source video
            toscale         scale factor
            self.h_scaled   height ratio
            self.w_scaled   width ratio
        """
        # pen/brush color, default RED color
        self.pencolor = (255, 0, 0, 255)
        # cropping values for monitor preview
        self.w_dc = 0
        self.h_dc = 0
        self.y_dc = 0
        self.x_dc = 0
        # current video size
        self.width = kwa['width']
        self.height = kwa['height']
        # scale preserving aspect ratio
        toscale = 220 if self.height >= self.width else 350
        self.h_scaled = round((self.height / self.width) * toscale)
        self.w_scaled = round((self.width / self.height) * self.h_scaled)
        self.filename = kwa['filename']  # selected filename on file list
        name = os.path.splitext(os.path.basename(self.filename))[0]
        self.frame = os.path.join(f'{Crop.TMPSRC}', f'{name}.png')  # image
        self.fileclock = os.path.join(Crop.TMPROOT, f'{name}.clock')
        tcheck = clockset(kwa['duration'], self.fileclock)
        self.clock = tcheck['duration']
        self.mills = tcheck['millis']
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        self.panelrect = wx.Panel(self, wx.ID_ANY,
                                  size=(self.w_scaled, self.h_scaled)
                                  )
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
        self.btn_color = csel.ColourSelect(self, -1, _("Crop color"),
                                           self.pencolor)
        sizersize.Add(self.btn_color, 0, wx.CENTER | wx.ALL, 5)
        msg = _("Search for a specific frame")
        sizer_load = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (msg)),
                                       wx.HORIZONTAL)
        sizerBase.Add(sizer_load, 0, wx.ALL | wx.CENTER, 5)
        self.sld_time = wx.Slider(self, wx.ID_ANY,
                                  time_to_integer(self.clock),
                                  0,
                                  1 if not self.mills else self.mills,
                                  size=(250, -1),
                                  style=wx.SL_HORIZONTAL,
                                  )
        sizer_load.Add(self.sld_time, 0, wx.ALL | wx.CENTER, 5)
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
        btn_reset.SetBitmap(args[2], wx.LEFT)
        boxaff.Add(btn_reset, 0, wx.LEFT, 5)
        gridbtns.Add(boxaff, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=5)
        sizerBase.Add(gridbtns, 0, wx.EXPAND)

        # instance to Actor widget
        if os.path.exists(self.frame):
            bmp = make_bitmap(self.w_scaled, self.h_scaled, self.frame)
            self.bob = Actor(self.panelrect, bmp, 1, "")
        else:  # make a temporary empty bitmap
            bmp = wx.Bitmap(self.w_scaled, self.h_scaled)
            self.bob = Actor(self.panelrect, bmp, 1, "")
            self.make_frame_from_file(None)

        # ----------------------Properties-----------------------#
        self.panelrect.SetBackgroundColour(wx.Colour(Crop.BACKGROUND))
        if Crop.OS == 'Darwin':
            label1.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            label1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self.SetTitle(_("Crop Tool"))
        self.btn_color.SetToolTip(_('Choose the color to draw '
                                    'the cropping area'))
        self.spin_w.SetToolTip(_('Crop to width'))
        self.spin_y.SetToolTip(_('Move vertically (set to -1 to center '
                                 'the vertical axis)'))
        self.spin_x.SetToolTip(_('Move horizontally (set to -1 to center '
                                 'the horizontal axis)'))
        self.spin_h.SetToolTip(_('Crop to height'))

        # ----- Set layout
        self.SetSizer(sizerBase)
        sizerBase.Fit(self)
        self.Layout()

        # ----------------------Binding (EVT)------------------------#
        self.Bind(wx.EVT_SPINCTRL, self.onWidth, self.spin_w)
        self.Bind(wx.EVT_SPINCTRL, self.onHeight, self.spin_h)
        self.Bind(wx.EVT_SPINCTRL, self.onX, self.spin_x)
        self.Bind(wx.EVT_SPINCTRL, self.onY, self.spin_y)
        self.Bind(wx.EVT_BUTTON, self.onCentre, self.btn_centre)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.on_Seek, self.sld_time)
        self.Bind(wx.EVT_BUTTON, self.make_frame_from_file, self.btn_load)

        self.Bind(wx.EVT_BUTTON, self.on_close, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.btn_color.Bind(csel.EVT_COLOURSELECT, self.bob.oncolor)

        pub.subscribe(self.to_real_scale_coords, "TO_REAL_SCALE")

        if not self.mills:
            self.sld_time.Disable()

        if args[0]:  # fcrop previusly values
            self.default(args[0], args[1])
    # ------------------------------------------------------------------#

    def default(self, fcrop, colorcrop):
        """
        Set controls to previous settings when reopening
        the Crop dialog
        """
        s = fcrop.split(':')
        s[0] = s[0][5:]  # removing `crop=` word on first item
        self.spin_w.SetValue(int(s[0][2:]))
        self.spin_h.SetValue(int(s[1][2:]))
        self.spin_x.SetValue(int(s[2][2:]))
        self.spin_y.SetValue(int(s[3][2:]))
        self.btn_color.SetValue(colorcrop)
        self.bob.oncolor(None, color=colorcrop)
        self.onDrawing()
    # ------------------------------------------------------------------#

    def on_Seek(self, event):
        """
        Slider event on seek time position.
        """
        seek = self.sld_time.GetValue()
        clock = integer_to_time(seek, False)  # to 24-hour
        self.txttime.SetLabel(clock)  # update StaticText
        if not self.btn_load.IsEnabled():
            self.btn_load.Enable()
    # ------------------------------------------------------------------#

    def make_frame_from_file(self, event):
        """
        This method is responsible for making available a
        new frame from a given time position of a video file,
        converting it into a bitmap object and displaying it
        by the `bob` actor. Note, milliseconds must not be
        greater than the max time nor less than the min time
        (see the `seek` callback above)
        """
        logfile = make_log_template('generic_task.log', Crop.LOGDIR, mode="w")
        if not self.mills:
            sseg = ''
        else:
            seek = self.sld_time.GetValue()
            self.clock = integer_to_time(seek, False)  # to 24-HH
            sseg = f'-ss {self.clock}'

        arg = (f'{sseg} -i "{self.filename}" -f image2 '
               f'-update 1 -frames:v 1 "{self.frame}"')
        thread = FFmpegGenericTask(arg, 'Crop', logfile)
        thread.join()  # wait end thread
        error = thread.status
        if error:
            wx.MessageBox(f'{error}', _('Videomass - Error!'), wx.ICON_ERROR)
            return
        if sseg:
            with open(self.fileclock, "w", encoding='utf-8') as atime:
                atime.write(self.clock)
        self.btn_load.Disable()
        bmp = make_bitmap(self.w_scaled, self.h_scaled, self.frame)
        self.bob.setbitmap(bmp)
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

        rect = (self.x_dc, self.y_dc, self.w_dc, self.h_dc)
        self.bob.onRedraw([round(r) for r in rect])
    # ------------------------------------------------------------------#

    def onWidth(self, event):
        """
        Width adjustment event, self.spin_w callback

        """
        self.onDrawing()
    # ------------------------------------------------------------------#

    def onHeight(self, event):
        """
        Height adjustment event, self.spin_h callback
        """
        self.onDrawing()
    # ------------------------------------------------------------------#

    def onX(self, event):
        """
        Event on Horizontal axis (X) adjustment, self.spin_x callback
        """
        self.onDrawing()
    # ------------------------------------------------------------------#

    def onY(self, event):
        """
        Event on Vertical axis (Y) adjustment, self.spin_y callback
        """
        self.onDrawing()
    # ------------------------------------------------------------------#

    def onCentre(self, event):
        """
        Sets coordinates X, Y to center.
        """
        x = (self.width / 2) - (self.spin_w.GetValue() / 2)
        self.spin_x.SetValue(round(x))
        y = (self.height / 2) - (self.spin_h.GetValue() / 2)
        self.spin_y.SetValue(round(y))
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

    def on_help(self, event):
        """
        Open default web browser via Python Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>

        """
        page = ('https://jeanslack.github.io/Videomass/User-guide/'
                'Video_filters_en.pdf#%5B%7B%22num%22%3A13%2C%22gen'
                '%22%3A0%7D%2C%7B%22name%22%3A%22XYZ%22%7D%2C56.7%2C785.'
                '189%2C0%5D')

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
            crop = val[:len(val) - 1]  # remove last ':' string
            color = self.btn_color.GetValue()
            return crop, color

        return None
