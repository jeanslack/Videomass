# -*- coding: UTF-8 -*-
"""
Name: timeline.py
Purpose: Time trimming settings
Compatibility: Python >= 3.11, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.01.2026
Code checker: flake8, pylint, ruff

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
import wx.adv
from pubsub import pub

from videomass.vdms_dialogs.widget_utils import NormalTransientPopup
from videomass.vdms_io.io_tools import show_msg_notify
from videomass.vdms_io.make_filelog import make_log_template
from videomass.vdms_threads.ffplay_file import FilePlayWithprogress
from videomass.vdms_threads.generic_task import FFmpegGenericTask
from videomass.vdms_utils.get_bmpfromsvg import get_bmp
from videomass.vdms_utils.utils import integer_to_time, time_to_integer


class Time_Selector(wx.Dialog):
    """
    fine-tune segments duration
    """

    def __init__(self, parent, clockstr, mode):
        """
        When this dialog is called, the values already set
        in the timeline panel are reproduced exactly here.
        """
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        caption = "No caption"
        if mode == "start":
            caption = _("Start point adjustment")
        elif mode == "duration":
            caption = _("End point adjustment")
        boxs = wx.StaticBox(self, wx.ID_ANY, "HH:MM:SS.ms")
        staticbox1 = wx.StaticBoxSizer(boxs, wx.VERTICAL)
        boxsiz1 = wx.BoxSizer(wx.HORIZONTAL)
        staticbox1.Add(boxsiz1, 0, wx.ALL | wx.ALIGN_CENTER, 0)
        sizer_base.Add(staticbox1, 0, wx.ALL | wx.EXPAND, 5)

        self.box_hour = wx.SpinCtrl(
            boxs,
            wx.ID_ANY,
            value=f"{clockstr[0:2]}",
            min=0,
            max=23,
            style=wx.SP_ARROW_KEYS,
        )

        boxsiz1.Add(self.box_hour, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        lab1 = wx.StaticText(boxs, wx.ID_ANY, (":"))
        lab1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        boxsiz1.Add(lab1, 0, wx.ALIGN_CENTER, 5)

        self.box_min = wx.SpinCtrl(
            boxs,
            wx.ID_ANY,
            value=f"{clockstr[3:5]}",
            min=0,
            max=59,
            style=wx.SP_ARROW_KEYS,
        )

        boxsiz1.Add(self.box_min, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        lab2 = wx.StaticText(boxs, wx.ID_ANY, (":"))
        lab2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        boxsiz1.Add(lab2, 0, wx.ALIGN_CENTER, 5)

        self.box_sec = wx.SpinCtrl(
            boxs,
            wx.ID_ANY,
            value=f"{clockstr[6:8]}",
            min=0,
            max=59,
            style=wx.SP_ARROW_KEYS,
        )

        boxsiz1.Add(self.box_sec, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        lab3 = wx.StaticText(boxs, wx.ID_ANY, ("."))
        lab3.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        boxsiz1.Add(lab3, 0, wx.ALIGN_CENTER, 5)

        self.box_mills = wx.SpinCtrl(
            boxs,
            wx.ID_ANY,
            value=f"{clockstr[9:12]}",
            min=000,
            max=999,
            style=wx.SP_ARROW_KEYS,
        )
        boxsiz1.Add(self.box_mills, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        # confirm buttons:
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        gridexit.Add(btn_close, 0, wx.ALL, 5)
        btn_ok = wx.Button(self, wx.ID_OK, "")
        gridexit.Add(btn_ok, 0, wx.ALL, 5)
        sizer_base.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # ----------------------Properties ----------------------#

        self.SetTitle(caption)
        self.box_hour.SetToolTip(_("Hours"))
        self.box_min.SetToolTip(_("Minutes"))
        self.box_sec.SetToolTip(_("Seconds"))
        self.box_mills.SetToolTip(_("Milliseconds"))

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)

    # ----------------------Event handler (callback)----------------------#

    def on_close(self, event):
        """
        Close this dialog without saving anything
        """
        event.Skip()  # need if destroy from parent

    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Confirm event
        """
        event.Skip()

    # ------------------------------------------------------------------#

    def getvalue(self):
        """
        This method return values via the getvalue() interface
        from the caller.
        """
        val = (
            f"{str(self.box_hour.GetValue()).zfill(2)}:"
            f"{str(self.box_min.GetValue()).zfill(2)}:"
            f"{str(self.box_sec.GetValue()).zfill(2)}."
            f"{str(self.box_mills.GetValue()).zfill(3)}"
        )
        return val, time_to_integer(val)


class Float_TL(wx.MiniFrame):
    """
    A graphical representation of the Float_TL object,
    a floating bar (ruler) for trimming and slicing time
    segments from media duration.

    """

    get = wx.GetApp()
    ICONS = get.iconset
    # COLORSCHEME = get.appset['colorscheme']
    OS = get.appset["ostype"]
    LOGDIR = get.appset["logdir"]
    TMPROOT = os.path.join(get.appset["cachedir"], "tmp", "Waveforms")
    TMPSRC = os.path.join(TMPROOT, "tmpsrc")
    os.makedirs(TMPSRC, mode=0o777, exist_ok=True)

    # Code Colours
    YELLOW = "#bd9f00"  # for warnings
    BLACK = "#060505"  # black for background status bar
    ORANGE = "#f28924"  # for errors and warnings
    LGREEN = "#52EE7D"
    RULER_BKGRD = "#646D6F"  # GREY ruler background
    DELIMITER_COLOR = "#00F5D4"  # Mint Green for margin selection handles
    SELECTION = (0, 245, 212, 40)  # semi-transparent Mint Green, inner area
    DURATION_RESET = "#E6FFFC"  # Cyan-white for the initial time text
    DURATION_START = "#FF7A00"  # Neon orange for the time text (Start/End)
    TEXT_PEN_COLOR = "#E6FFFC"  # Cyan-white for the ruler markings
    # --- INVALID SELECTION HIGHLIGHTED
    SELECTION_INVALID = (255, 38, 38, 110)  # Semi-transparent red error
    TEXT_INVALID = "#FFD700"  # Golden yellow for text containing errors
    # --- BTN readme
    READMEGREEN = "#80C058"  # readme btn background
    READMEBLACK = "#1f1f1f"  # readme btn foreground

    # ruler and panel specifications constants
    RW = 900  # ruler width
    RM = 0  # ruler margin
    PW = 906  # panel width
    PH = 80  # panel height

    def __init__(self, parent):
        """
        self.pix: scale pixels to milliseconds
        self.milliseconds: int(milliseconds)
        self.duration: see parent attr.
        self.bar_w: END point value in pixel
        self.bar_x: START point value in pixel

        """
        icons = Float_TL.ICONS
        bmp_reset = get_bmp(icons["clear"], ((16, 16)))
        bmp_tstart = get_bmp(icons["start_time"], ((16, 16)))
        bmp_tend = get_bmp(icons["end_time"], ((16, 16)))
        bmp_wave = get_bmp(icons["waveform"], ((16, 16)))
        self.bmp_play = get_bmp(icons["playback"], ((16, 16)))
        self.bmp_stop = get_bmp(icons["playstop"], ((16, 16)))

        self.parent = parent
        self.duration = self.parent.duration
        self.overalltime = "00:00:00.000"
        self.milliseconds = 86399999  # 23:59:59:999
        self.clock_start = "00:00:00.000"  # seek position
        self.clock_end = "00:00:00.000"
        self.mills_end = 0  # end point in milliseconds
        self.mills_start = 0  # stat point in milliseconds
        self.pix = Float_TL.RW / self.milliseconds  # scale factor
        self.bar_w = 0  # End point value in pixel
        self.bar_x = 0  # Start point value in pixel
        self.pointpx = [0, 0]  # mouse points (see on_move(), on_leftdown())
        self.sourcedur = _("No source duration:")
        self.filename = None  # selected filename on file list
        self.frame = None  # waveform image located on cache dir
        self.invalidselection = False  # booleaan reference
        self.playpoint = None  # `x` point pixel representation or None
        self.playback = None  # playback thread

        wx.MiniFrame.__init__(
            self,
            parent,
            -1,
            style=wx.CAPTION
            | wx.CLOSE_BOX
            | wx.SYSTEM_MENU
            | wx.FRAME_FLOAT_ON_PARENT
            | wx.RESIZE_BORDER,
        )
        self.panelbase = wx.Panel(
            self, wx.ID_ANY, style=wx.TAB_TRAVERSAL | wx.BORDER_THEME
        )
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        self.panelruler = wx.Panel(
            self.panelbase,
            wx.ID_ANY,
            size=(Float_TL.PW, Float_TL.PH),
            style=wx.BORDER_SUNKEN,
        )
        sizer_base.Add(self.panelruler, 0, wx.ALL | wx.CENTRE, 2)
        sizer_btns = wx.BoxSizer(wx.HORIZONTAL)
        sizer_btns = wx.FlexGridSizer(0, 7, 0, 0)
        sizer_base.Add(sizer_btns, 0, wx.ALL | wx.CENTRE, 8)
        self.btn_play = wx.Button(self.panelbase, wx.ID_ANY, "", size=(40, -1))
        self.btn_play.SetBitmap(self.bmp_play, wx.LEFT)
        sizer_btns.Add(self.btn_play, 0, wx.RIGHT | wx.CENTRE, 20)
        self.counterplay = wx.StaticText(
            self.panelbase, wx.ID_ANY, ("00:00:00.000")
        )
        self.counterplay.SetFont(
            wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, "")
        )
        sizer_btns.Add(
            self.counterplay,
            0,
            wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL | wx.ALIGN_CENTRE_HORIZONTAL,
            20,
        )
        self.btn_tstart = wx.Button(
            self.panelbase, wx.ID_ANY, "", size=(40, -1)
        )
        self.btn_tstart.SetBitmap(bmp_tstart, wx.LEFT)
        sizer_btns.Add(self.btn_tstart, 0, wx.CENTRE, 5)
        self.btn_reset = wx.Button(
            self.panelbase, wx.ID_ANY, "", size=(40, -1)
        )
        self.btn_reset.SetBitmap(bmp_reset, wx.LEFT)
        sizer_btns.Add(self.btn_reset, 0, wx.LEFT | wx.CENTRE, 5)
        self.btn_tend = wx.Button(self.panelbase, wx.ID_ANY, "", size=(40, -1))
        self.btn_tend.SetBitmap(bmp_tend, wx.LEFT)
        sizer_btns.Add(self.btn_tend, 0, wx.LEFT | wx.CENTRE, 5)
        self.btn_wave = wx.ToggleButton(
            self.panelbase, wx.ID_ANY, _("Wave"), size=(-1, -1)
        )
        self.btn_wave.SetBitmap(bmp_wave, wx.LEFT)
        sizer_btns.Add(self.btn_wave, 0, wx.LEFT | wx.CENTRE, 20)
        btn_quicktip = wx.Button(
            self.panelbase, wx.ID_ANY, _("?"), size=(40, -1)
        )
        font = btn_quicktip.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        btn_quicktip.SetFont(font)
        btn_quicktip.SetBackgroundColour(wx.Colour(Float_TL.READMEGREEN))
        btn_quicktip.SetForegroundColour(wx.Colour(Float_TL.READMEBLACK))
        sizer_btns.Add(btn_quicktip, 0, wx.LEFT | wx.CENTRE, 20)

        # ----------------------Properties ----------------------#
        self.panelruler.SetBackgroundColour(wx.Colour(Float_TL.RULER_BKGRD))
        self.panelruler.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        if Float_TL.OS == "Windows":
            self.panelruler.SetDoubleBuffered(
                True
            )  # Reduces the flickering only on windows
        self.textcolor = wx.Colour(Float_TL.TEXT_PEN_COLOR)
        self.selcolor = wx.Colour(Float_TL.SELECTION)

        self.SetTitle("Timeline Editor")
        icon = wx.Icon()
        icon.CopyFromBitmap(
            wx.Bitmap(Float_TL.ICONS["videomass"], wx.BITMAP_TYPE_ANY)
        )
        self.SetIcon(icon)

        self.sb = self.CreateStatusBar(1)
        msg = _("{0} {1}  |  Segment Duration: {2}").format(
            self.sourcedur, self.overalltime, "00:00:00.000"
        )
        self.statusbar_msg(msg, None)

        # ----------------------Layout----------------------#
        self.panelbase.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        self.SetMinSize((920, 190))
        self.Move(tuple(Float_TL.get.appset["timeline_window_pos"]))

        if Float_TL.OS == "Linux":
            self.font_med = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        elif Float_TL.OS == "Windows":
            self.font_med = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        elif Float_TL.OS == "Darwin":
            self.font_med = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        else:
            self.font_med = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        # ---------------------- disable all controls by default
        # self.panelbase.Disable()

        # ---------------------- Tooltips
        tip = _("End adjustment")
        self.btn_tend.SetToolTip(tip)
        tip = _("Start adjustment")
        self.btn_tstart.SetToolTip(tip)
        tip = _(
            "Toggles the display of the audio waveform in the background ruler"
        )
        self.btn_wave.SetToolTip(tip)
        tip = _("Reset segment on timeline")
        self.btn_reset.SetToolTip(tip)
        tip = _("Timeline Editor Usage")
        btn_quicktip.SetToolTip(tip)
        tip = _("Play/Stop segment")
        self.btn_play.SetToolTip(tip)

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_load_waveform, self.btn_wave)
        self.Bind(
            wx.EVT_BUTTON,
            lambda event: self.on_set_pos(event, mode="duration"),
            self.btn_tend,
        )
        self.Bind(
            wx.EVT_BUTTON,
            lambda event: self.on_set_pos(event, mode="start"),
            self.btn_tstart,
        )
        self.Bind(wx.EVT_BUTTON, self.on_trim_time_reset, self.btn_reset)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_quicktip)
        self.Bind(wx.EVT_BUTTON, self.on_play_segment, self.btn_play)
        self.panelruler.Bind(wx.EVT_PAINT, self.OnPaint)
        self.panelruler.Bind(wx.EVT_LEFT_DOWN, self.on_leftdown)
        self.panelruler.Bind(wx.EVT_LEFT_UP, self.on_leftup)
        self.panelruler.Bind(wx.EVT_LEFT_DCLICK, self.on_set_pos)
        self.panelruler.Bind(wx.EVT_MOTION, self.on_move)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.set_ui_ctrl(state=False)
        self.panelruler.Refresh()

        pub.subscribe(self.set_values, "RESET_ON_CHANGED_LIST")
        pub.subscribe(self.update_counter_thread, "UPDATE_PLAY_COUNTER")
        pub.subscribe(self.end_playback_thread, "END_PLAY")

    def set_ui_ctrl(self, state=True):
        """
        Enable or disable the graphical user interface controls.
        Accetta True per attivare o False per disattivare i widget.
        """
        # 2. Lista dei widget da aggiornare in blocco
        widgets = [
            self.btn_play,
            self.btn_wave,
            self.btn_tstart,
            self.btn_reset,
            self.btn_tend,
            self.panelruler,
        ]
        if self.playback is not None and self.playback.is_alive():
            del widgets[0]  # del btn_play

        for widget in widgets:
            widget.Enable(state)

    # ------------------------------------------------------------------#

    def file_selection(self):
        """
        Defines the selected file as filename. Returns an object
        of type list (str('selected file name'), int(index)).
        Returns None type if no file is selected.
        """
        if not self.parent.filedropselected:
            wx.MessageBox(
                _("Have to select an item in the file list first"),
                "Videomass",
                wx.ICON_INFORMATION,
                self,
            )
            return None
        self.filename = self.parent.filedropselected
        return (self.filename, self.parent.file_src.index(self.filename))

    # ------------------------------------------------------------------#

    def make_frame_from_file(self):
        """
        This method is responsible for making available
        an audio waveform frame from a selected file.
        Return None type if error, str(frame) as pathname otherwise.
        """
        logfile = make_log_template(
            "generic_task.log", Float_TL.LOGDIR, mode="w"
        )
        name = os.path.splitext(os.path.basename(self.filename))[0]
        self.frame = os.path.join(f"{Float_TL.TMPSRC}", f"{name}.png")  # image

        args = (
            f'-i "{self.filename}" -filter_complex "aformat=channel_layouts'
            f"=mono,compand,showwavespic=s={Float_TL.RW + 10}x{Float_TL.PH}:"
            f'colors=0x0A192F@0.70:split_channels=1:draw=full:filter=peak" '
            f'-update 1 -frames:v 1 "{self.frame}"'
        )
        thread = FFmpegGenericTask(args, "Timeline Waveform", logfile)
        thread.join()  # wait end thread
        error = thread.status
        if error:
            self.frame = None
            show_msg_notify(
                self.GetParent(), logname=os.path.basename(logfile)
            )
        return self.frame

    # ------------------------------------------------------------------#

    def get_audio_stream(self, fileselected):
        """
        Given a selected media file (object of type `file_selection()`),
        it evaluates whether it contains any audio streams.
        If no audio streams Returns None, True otherwise.
        """
        selected = self.parent.data_files[fileselected[1]].get("streams")
        isaudio = [a for a in selected if "audio" in a.get("codec_type")]

        if isaudio:
            return True
        return None

    # ------------------------------------------------------------------#

    def stop_playback(self):
        """
        Extension of the btn_play event when the user clicks
        the button to stop playback.
        """
        self.playback.stop("FilePlayWithprogress")
        self.playback = None
        self.end_playback_thread()

    # ----------------------Event handler (callbacks)----------------------#

    def on_play_segment(self, event):
        """
        Button play event. Plays a segment of a selected file.
        IMPORTANT: To make this effective, set ffplay's loglevel
        args to info: `-loglevel info.
        """
        if not self.file_selection():
            return

        if self.sourcedur == _("No source duration:"):
            wx.MessageBox(
                _("Invalid file format for playback."),
                _("Videomass - Warning!"),
                wx.ICON_WARNING,
                self,
            )
            return

        if self.parent.time_seq == "":
            wx.MessageBox(
                _("No segment selected in the timeline yet."),
                _("Videomass - Warning!"),
                wx.ICON_WARNING,
                self,
            )
            return

        if self.invalidselection:
            wx.MessageBox(
                _(
                    "Invalid segment selection!\n«End» cursor must be "
                    "moved to the right side of the «Start» cursor."
                ),
                _("Videomass - Error!"),
                wx.ICON_ERROR,
                self,
            )
            return

        if self.playback is not None and self.playback.is_alive():
            self.stop_playback()
            return

        self.btn_play.SetBitmap(self.bmp_stop)

        filesel = self.file_selection()[0]

        if self.parent.checktimestamp:
            scalef, tstamp = "scale=w=360:h=-1,", f"{self.parent.cmdtimestamp}"
        else:
            scalef, tstamp = "scale=w=360:h=-1", ""

        args = (
            f'"{Float_TL.get.appset["ffplay_cmd"]}" '
            f"{Float_TL.get.appset['ffplay-default-args']} "
            f"-loglevel info "  # this is mandatory here
            f'-autoexit -i "{filesel}" '
            f"{self.parent.time_seq} "
            f'-vf "{scalef}{tstamp}"'
        )
        try:
            with open(filesel, encoding="utf-8"):
                self.playback = FilePlayWithprogress(self.GetParent(), args)
                self.playback.start()
        except OSError:
            wx.MessageBox(
                _("Invalid or unsupported file:  %s") % (filesel),
                "Videomass",
                wx.ICON_EXCLAMATION,
                self,
            )
            return

        self.set_ui_ctrl(False)
        self.playpoint = round(self.bar_x)

    # ----------------------------------------------------------------------

    def update_counter_thread(self, output, status):
        """
        Updates the counter, sets self.playpoint taking into account the
        slice/segment offset, and requests thread-safe redraw.

        This method uses pub/sub protocol subscribing "UPDATE_PLAY_COUNTER"
        message. It is called by `FilePlay` class thread to update
        the output lines of the ffplay stderr (see `on_play_segment` def).

        """
        if status:
            """
            Set the timeline to be disabled while playing the file
            """
            return

        if output:
            # Cleans up whitespace at the beginning and end of the line
            clean_line = output.strip()
            if not clean_line:
                return

            # Check the diagnostic line from ffplay's actual counter
            if not any(
                x in clean_line for x in ("A-V:", "M-A:", "aq=", "vq=")
            ):
                return

            # exclude lines unrelated to the number of seconds
            line_parts = clean_line.split()
            if not line_parts or len(line_parts) == 0:
                return

            try:
                if line_parts[0] == "nan":
                    return
                # Extracts the current milliseconds from the ffplay output
                timemils = float(line_parts[0]) * 1000
                # Update the visual text counter
                res = integer_to_time(round(timemils))
                wx.CallAfter(self.counterplay.SetLabel, res)

                # Checks whether playback is still in the "previous keyframe"
                # phase before the actual slice start.
                if timemils < self.mills_start:
                    # Force the cursor to the start position of the segment
                    pixpos = round(self.bar_x)

                # Check whether the end of the set slice has been exceeded
                elif timemils > self.mills_end:
                    # Force the cursor to the end position of the segment
                    pixpos = round(self.bar_w)
                else:
                    # when the video is at the very beginning
                    if timemils == 0:
                        pixpos = 0
                    else:
                        scaletopix = round(
                            self.pix / (Float_TL.RW / timemils) * Float_TL.RW
                        )
                        pixpos = scaletopix

                def safe_ui_update(px):
                    """
                    Safe graphical update on the main thread.
                    Update the variable read by OnPaint and redraw.
                    """
                    self.playpoint = px
                    self.panelruler.Refresh()

                wx.CallAfter(safe_ui_update, pixpos)

            except (ValueError, IndexError, ZeroDivisionError):
                wx.CallAfter(self.counterplay.SetLabel, "N/A")

    # ----------------------------------------------------------------------

    def end_playback_thread(self):
        """
        This method uses pub/sub protocol subscribing "END_PLAY" message.
        It is called by `FilePlay` class thread to indicate the end of the
        thread.
        """

        def reset_gui():
            # Enables cmponents of the timeline
            self.set_ui_ctrl(True)
            self.btn_play.SetBitmap(self.bmp_play)
            # Move the cursor back to the beginning of the segment (bar_x)
            self.playpoint = round(self.bar_x)
            self.panelruler.Refresh()

        # Dispatch execution to the main GUI thread to avoid freezing
        # on Windows
        wx.CallAfter(reset_gui)

    # ----------------------------------------------------------------------

    def on_load_waveform(self, event):
        """
        Event on toggle waveform button
        """
        if self.btn_wave.GetValue() is True:
            if not self.file_selection():
                self.btn_wave.SetValue(False)
                return

            if not self.get_audio_stream(self.file_selection()):
                wx.MessageBox(
                    _(
                        "Unable to create waveform.\nThe selected "
                        "source file does not contain any audio "
                        'streams:\n"{}"'
                    ).format(self.file_selection()[0]),
                    _("Videomass - Warning!"),
                    wx.ICON_WARNING,
                    self,
                )
                self.btn_wave.SetValue(False)
                return

            if not self.make_frame_from_file():
                self.btn_wave.SetValue(False)
                return
        else:
            self.frame = None

        self.onRedraw()

    # ----------------------------------------------------------------------

    def on_help(self, event):
        """
        Event clicking on button Quick Tip.
        """
        msg = _(
            "The timeline editor allows you to trim slices of time on "
            "selected files.\nThe time format used to report durations "
            "is expressed in hours, minutes,\nseconds and milliseconds "
            "(HH:MM:SS.ms).\n\nThe «Start»/«End» duration values always "
            "refer to the initial position of\na overall duration. "
            "The overall duration of a file and the duration of a\n"
            "selected segment (including warnings) are displayed on the "
            "timeline\nstatus bar.\n\nPlease note that actions such as "
            "importing new files, selecting, deselecting,\ndeleting, and "
            "sorting items will reset the timeline to its default "
            "values.\n\nIf no source file, the duration values will be "
            "set to the default value\n(00:00:00.000) and all timeline "
            "controls will be disabled.\nThis behavior also applies when "
            "deselecting files."
        )

        win = NormalTransientPopup(self, wx.SIMPLE_BORDER, msg)

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = event.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Popup()

    # --------------------------------------------------------------#

    def on_trim_time_reset(self, event):
        """
        Reset all timeline values to default.
        """
        self.pix = Float_TL.RW / self.milliseconds
        self.bar_w = 0
        self.bar_x = 0
        self.mills_end = 0
        self.clock_end = "00:00:00.000"
        self.mills_start = 0
        self.clock_start = "00:00:00.000"
        msg = _("{0} {1}  |  Segment Duration: {2}").format(
            self.sourcedur, self.overalltime, "00:00:00.000"
        )
        self.playpoint = None
        self.counterplay.SetLabel("00:00:00.000")
        self.statusbar_msg(msg, None)
        self.parent.time_seq = ""

        self.onRedraw()

    # ------------------------------------------------------------------#

    def set_values(self, msg):
        """
        Any change to the file list in the drag panel reset
        timeline data. This method is called using pub/sub protocol
        subscribing "RESET_ON_CHANGED_LIST" by adding, selecting or
        removing imported files (see`filedrop.py`).
        """
        if self.playback is not None and self.playback.is_alive():
            self.playback.stop("FilePlayWithprogress")
            self.playback = None
            self.btn_play.SetBitmap(self.bmp_play)

        self.sourcedur = _("No source duration:")
        if msg is None:
            self.milliseconds = 86399999
            self.overalltime = "00:00:00.000"
            self.set_ui_ctrl(False)

        else:
            if self.duration[msg] < 100:
                self.milliseconds = 86399999
                self.set_ui_ctrl(False)
                self.overalltime = "00:00:00.000"
            else:
                self.milliseconds = self.duration[msg]
                self.sourcedur = _("Source duration:")
                self.set_ui_ctrl(True)
                self.overalltime = integer_to_time(self.milliseconds)

        self.btn_wave.SetValue(False)
        self.frame = None
        self.on_trim_time_reset(None)

    # ------------------------------------------------------------------#

    def set_time_seq(self, isset=True):
        """
        Set parent time_seq attr.
        """
        if isset:
            dur = integer_to_time(self.mills_end - self.mills_start)
            self.parent.time_seq = f"-ss {self.clock_start} -t {dur}"
            msg = _("{0} {1}  |  Segment Duration: {2}").format(
                self.sourcedur, self.overalltime, dur
            )
            self.statusbar_msg(f"{msg}", None)
        else:
            self.parent.time_seq = ""
            msg = _("{0} {1}  |  Segment Duration: {2}").format(
                self.sourcedur, self.overalltime, "00:00:00.000"
            )
            self.statusbar_msg(f"{msg}", None)

    # ------------------------------------------------------------------#

    def set_coordinates(self):
        """
        Set data for x axis rectangle selection and
        call onRedraw.
        """
        if self.pointpx[1] > 30:
            self.bar_w = self.pointpx[0]
            self.mills_end = round(self.bar_w / self.pix)
            self.clock_end = integer_to_time(self.mills_end)
            self.onRedraw()

        elif self.pointpx[1] < 30:
            self.bar_x = self.pointpx[0]
            self.mills_start = round(self.bar_x / self.pix)
            self.clock_start = integer_to_time(self.mills_start)
            self.onRedraw()

    # ------------------------------------------------------------------#

    def on_leftdown(self, event):
        """
        Event on clicking the left mouse button
        """
        self.panelruler.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.pointpx = event.GetPosition()
        if self.pointpx[0] >= Float_TL.RW:
            return
        if self.pointpx[0] <= 0:
            return
        self.set_coordinates()

    # ------------------------------------------------------------------#

    def on_leftup(self, event):
        """
        Event on releasing the left mouse button

        """
        self.panelruler.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

        if self.bar_w == 0 and self.bar_x == 0:
            self.set_time_seq(isset=False)
            return

        if (
            self.bar_w <= self.bar_x
            or self.mills_end > self.milliseconds
            or self.mills_start < 0
        ):
            msg = _("WARNING: Invalid segment selection, out of range.")
            self.statusbar_msg(f"{msg}", Float_TL.ORANGE, Float_TL.BLACK)
            return

        self.set_time_seq(isset=True)

    # ------------------------------------------------------------------#

    def on_set_pos(self, event, mode=None):
        """
        Event on mouse double click right button.
        Note that pixpos variable is the KEY
        """
        if mode == "duration":
            clock, mode = self.clock_end, "duration"
        elif mode == "start":
            clock, mode = self.clock_start, "start"
        elif self.pointpx[1] > 30:
            clock, mode = self.clock_end, "duration"
        elif self.pointpx[1] < 30:
            clock, mode = self.clock_start, "start"
        else:
            return

        with Time_Selector(self, clock, mode) as selector:
            if selector.ShowModal() == wx.ID_OK:
                data = selector.getvalue()
                # pixpos: convert to new `x` point pixel
                pixpos = self.pix / (Float_TL.RW / data[1]) * Float_TL.RW
                self.pointpx[0] = round(pixpos)  # set x point
                if mode == "start":
                    self.bar_x = pixpos
                    self.mills_start = data[1]
                    self.clock_start = data[0]
                elif mode == "duration":
                    self.bar_w = pixpos
                    self.mills_end = data[1]
                    self.clock_end = data[0]

                self.onRedraw()
                self.on_leftup(None)

    # ------------------------------------------------------------------#

    def on_move(self, event):
        """
        Mouse event when moving it on the panel bar
        """
        if event.Dragging() and event.LeftIsDown():
            self.pointpx = event.GetPosition()
            if self.pointpx[1] > 30:
                if self.mills_end == self.milliseconds:
                    return
            elif self.pointpx[1] < 30 and self.mills_start == 0:
                return
            dur = integer_to_time(self.mills_end - self.mills_start)
            msg = _("{0} {1}  |  Segment Duration: {2}").format(
                self.sourcedur, self.overalltime, dur
            )
            self.statusbar_msg(f"{msg}", None)
            self.set_coordinates()

    # ------------------------------------------------------------------#
    def OnPaint(self, event):
        """
        A centralized, cross-platform graphics manager protected by
        double buffering. It unifies the `onRedraw` logic, the waveform
        display (background), and the real-time red cursor.
        """
        # Initialize the multi-platforms graphics context
        dc = wx.PaintDC(self.panelruler)
        if Float_TL.OS != "Darwin":
            dc = wx.GCDC(dc)

        # Manual background handling to avoid artifacts with BG_STYLE_PAINT
        bg_color = self.panelruler.GetBackgroundColour()
        dc.SetBackground(wx.Brush(bg_color))
        dc.Clear()

        # Waveform background, must be placed strictly BEFORE the indicators
        if self.frame:
            # try:
            bmp = wx.Image(self.frame, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            dc.DrawBitmap(bmp, 0, 0, True)
            # except Exception as err:
            # Prevents crashes if removed from the cache
            # pass

        # determination of the selection status and colors
        show_help_msg = False
        if self.bar_w == 0 and self.bar_x == 0:
            self.invalidselection = False
            selcolor = wx.Colour(*Float_TL.SELECTION)
            textcolor = wx.Colour(Float_TL.DURATION_RESET)
            show_help_msg = True  # Enable to draw msg afterwards
        elif (
            self.bar_x >= self.bar_w
            or self.pointpx[0] > Float_TL.RW
            or self.pointpx[0] < 0
        ):
            self.invalidselection = True
            selcolor = wx.Colour(*Float_TL.SELECTION_INVALID)
            textcolor = wx.Colour(Float_TL.TEXT_INVALID)
        else:
            self.invalidselection = False
            selcolor = wx.Colour(*Float_TL.SELECTION)
            textcolor = wx.Colour(Float_TL.DURATION_START)

        # design of indicators and notches
        self.text_time_indicator(dc, textcolor, selcolor)
        self.ruler_notches(dc)

        # help text
        if show_help_msg:
            msg = _(
                "Start by dragging the handles in the left corners or\n"
                "click the Start/End adjustment buttons for fine tuning."
            )
            dc.SetFont(self.font_med)
            dc.SetTextForeground(wx.Colour(Float_TL.DURATION_START))
            dc.DrawText(msg, 310, 20)

        # real-time red cursor drawing
        if hasattr(self, "playpoint") and self.playpoint is not None:
            dc.SetBrush(wx.Brush(wx.RED, wx.BRUSHSTYLE_SOLID))
            dc.SetPen(wx.Pen(wx.RED))
            dc.DrawRectangle(round(self.playpoint), 0, 3, Float_TL.PH)

    # ------------------------------------------------------------------#

    def onRedraw(self, dc=None):
        """
        Legacy method retained for compatibility with mouse handlers.
        Requires safe redrawing of the panel.
        """

        self.panelruler.Refresh()

    # ------------------------------------------------------------------#

    def text_time_indicator(self, dc, textcolor, selcolor):
        """
        Make text indicator & drag handles next to the boundaries
        e.g start/duration delimiters.
        """
        dc.SetPen(wx.Pen(Float_TL.DELIMITER_COLOR, 1, wx.PENSTYLE_SOLID))
        bar_w, bar_x = round(self.bar_w), round(self.bar_x)
        dc.SetBrush(wx.Brush(selcolor, wx.BRUSHSTYLE_SOLID))
        dc.DrawRectangle(bar_x, -2, bar_w - bar_x, 85)

        dc.SetFont(self.font_med)
        txt_s = _("Start")
        txt_d = _("End")
        dc.SetPen(wx.Pen(Float_TL.DELIMITER_COLOR, 2, wx.PENSTYLE_SOLID))
        dc.SetBrush(wx.Brush(Float_TL.DELIMITER_COLOR))

        # Make start txt
        txt1 = f"{txt_s}  {self.clock_start}"
        dc.SetTextForeground(textcolor)
        w = dc.GetTextExtent(txt1)[0]

        if w > bar_x:
            dc.DrawText(txt1, bar_x + 3, 20)
            dc.DrawRectangle(bar_x, 1, 7, 9)
        else:
            dc.DrawText(txt1, bar_x - w - 2, 20)
            dc.DrawRectangle(bar_x - 5, 1, 7, 9)

        # Make duration txt
        txt2 = f"{txt_d}  {self.clock_end}"
        w = dc.GetTextExtent(txt2)[0]
        if w < Float_TL.RW - bar_w:
            dc.DrawText(txt2, bar_w + 1, 42)
            dc.DrawRectangle(bar_w - 1, 68, 7, 10)
        else:
            dc.DrawText(txt2, bar_w - w - 5, 42)
            dc.DrawRectangle(bar_w - 6, 68, 7, 10)

    # ------------------------------------------------------------------#

    def ruler_notches(self, dc):
        """
        Make ruler delimiters sign
        """
        dc.SetPen(wx.Pen(Float_TL.TEXT_PEN_COLOR))
        dc.SetTextForeground(Float_TL.TEXT_PEN_COLOR)

        for i in range(Float_TL.RW):
            if not i % 600 or not i % 300 or not i % 150:
                dc.DrawLine(i + Float_TL.RM, 0, i + Float_TL.RM, 10)
            elif not i % 25:
                dc.DrawLine(i + Float_TL.RM, 0, i + Float_TL.RM, 5)

        dc.DrawLine(i, 0, i, 10)

    # ------------------------------------------------------------------#

    def move_play_cursor(self, playpoint):
        """
        Updates the cursor position and requests a graphical update.
        """
        self.playpoint = playpoint

        # Requires a partial redraw of only the ruler panel, maximizing FPS
        self.panelruler.Refresh()

        # NOTE Su alcune versioni di Linux/GTK, potrebbe essere
        # necessario forzare l'elaborazione immediata dell'evento
        # di refresh se la riproduzione va a scatti:
        # self.panelruler.Update()

    # ------------------------------------------------------------------#

    def statusbar_msg(self, msg, bcolor, fcolor=None):
        """
        Set the status-bar message and color.
        See main_frame docstrings for details.
        """
        if Float_TL.OS == "Linux":
            if not bcolor:
                self.sb.SetBackgroundColour(wx.NullColour)
                self.sb.SetForegroundColour(wx.NullColour)
            else:
                self.sb.SetBackgroundColour(bcolor)
                self.sb.SetForegroundColour(fcolor)

        if Float_TL.OS == "Windows":
            self.sb.SetDoubleBuffered(True)  # prevents flickers
        self.sb.SetStatusText(msg)
        self.sb.Refresh()

    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        Hide this frame
        """
        self.parent.menuBar.Check(self.parent.viewtimeline.GetId(), False)
        self.Hide()
