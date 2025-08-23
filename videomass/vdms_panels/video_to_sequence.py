# -*- coding: UTF-8 -*-
"""
Name: video_to_sequence.py
Porpose: A simple images extractor UI
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Aug.23.2025
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
import sys
import wx
import wx.lib.agw.hyperlink as hpl
import wx.lib.agw.floatspin as FS
from videomass.vdms_dialogs.widget_utils import NormalTransientPopup
from videomass.vdms_utils.get_bmpfromsvg import get_bmp
from videomass.vdms_dialogs.filter_scale import Scale
from videomass.vdms_io.checkup import check_files
from videomass.vdms_dialogs.epilogue import Formula
from videomass.vdms_utils.utils import trailing_name_with_prog_digit
from videomass.vdms_utils.utils import update_timeseq_duration


class VideoToSequence(wx.Panel):
    """
    A simple UI for extracting frames from videos,
    with a special automation for output files and
    abilities of customization.
    """
    VIOLET = '#D64E93'
    LGREEN = '#52ee7d'
    BLACK = '#1f1f1f'
    MSG_1 = _("\n1. Import one or more video files, then select one."
              "\n\n2. To select a slice of time use the Timeline editor "
              "(CTRL+T) by adjusting the\n\"End\" and the \"Start\" duration "
              "values."
              "\n\n3. Select an output format (jpg, png, bmp)."
              "\n\n4. Start the conversion."
              "\n\n\nThe images produced will be saved in a folder "
              "named 'Movie_to_Pictures'\nwith a progressive digit, "
              "in the path you specify.")
    # ----------------------------------------------------------------#

    def __init__(self, parent):
        """
        This is a panel impemented on MainFrame
        """
        self.parent = parent  # parent is the MainFrame
        get = wx.GetApp()  # get data from bootstrap
        self.appdata = get.appset
        icons = get.iconset
        self.opt = {"Scale": "scale=w=320:h=-1", "Setdar": "", "Setsar": ""}

        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up
            bmpresize = get_bmp(icons['scale'], ((16, 16)))
            self.bmpreset = get_bmp(icons['clear'], ((16, 16)))
        else:
            bmpresize = wx.Bitmap(icons['scale'], wx.BITMAP_TYPE_ANY)
            self.bmpreset = wx.Bitmap(icons['clear'], wx.BITMAP_TYPE_ANY)

        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((20, 20))
        btn_help = wx.Button(self, wx.ID_ANY, _("Read me"), size=(-1, -1))
        btn_help.SetBackgroundColour(wx.Colour(VideoToSequence.LGREEN))
        btn_help.SetForegroundColour(wx.Colour(VideoToSequence.BLACK))
        sizer.Add(btn_help, 0, wx.ALL, 5)
        sizer.Add((20, 20))
        choices = [(_('Create thumbnails')),
                   (_('Create tiled mosaics')),
                   (_('Create animated GIF')),
                   ]
        self.rdbx_opt = wx.RadioBox(self, wx.ID_ANY, (_("Options")),
                                    choices=choices,
                                    majorDimension=1,
                                    style=wx.RA_SPECIFY_ROWS,
                                    )
        sizer.Add(self.rdbx_opt, 0, wx.ALL | wx.EXPAND, 5)
        self.rdbx_opt.SetSelection(0)
        boxctrl = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY), wx.VERTICAL)
        sizer.Add(boxctrl, 0, wx.ALL | wx.EXPAND, 5)
        siz_format = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(siz_format)
        siz_ctrl = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(siz_ctrl)
        self.lbl_rate = wx.StaticText(self, wx.ID_ANY, label="FPS:")
        siz_ctrl.Add(self.lbl_rate, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_rate = FS.FloatSpin(self, wx.ID_ANY,
                                      min_val=0.1, max_val=30.0,
                                      increment=0.1, value=0.2,
                                      agwStyle=FS.FS_LEFT, size=(120, -1)
                                      )
        self.spin_rate.SetFormat("%f")
        self.spin_rate.SetDigits(1)
        siz_ctrl.Add(self.spin_rate, 0, wx.ALL, 5)
        self.btn_resize = wx.Button(self, wx.ID_ANY, _("Resize"),
                                    size=(-1, -1)
                                    )
        self.btn_resize.SetBitmap(bmpresize, wx.LEFT)
        siz_ctrl.Add(self.btn_resize, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.lbl_frmt = wx.StaticText(self, wx.ID_ANY,
                                      label=_("Output format:")
                                      )
        siz_ctrl.Add(self.lbl_frmt, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_frmt = wx.ComboBox(self, wx.ID_ANY,
                                    choices=['jpeg', 'png', 'bmp', 'gif'],
                                    size=(160, -1), style=wx.CB_DROPDOWN
                                    | wx.CB_READONLY,
                                    )
        siz_ctrl.Add(self.cmb_frmt, 0, wx.ALL, 5)
        self.cmb_frmt.SetSelection(2)
        siz_tile = wx.FlexGridSizer(4, 4, 0, 0)
        boxctrl.Add(siz_tile, 0, wx.TOP | wx.BOTTOM, 10)
        self.lbl_rows = wx.StaticText(self, wx.ID_ANY, label=_("Rows:"))
        siz_tile.Add(self.lbl_rows, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.lbl_rows.Disable()
        self.spin_rows = wx.SpinCtrl(self, wx.ID_ANY, "4", min=2,
                                     max=32, size=(-1, -1),
                                     style=wx.TE_PROCESS_ENTER
                                     )
        siz_tile.Add(self.spin_rows, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_rows.Disable()
        self.lbl_cols = wx.StaticText(self, wx.ID_ANY,
                                      label=_("Columns:"))
        siz_tile.Add(self.lbl_cols, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.lbl_cols.Disable()
        self.spin_cols = wx.SpinCtrl(self, wx.ID_ANY, "4", min=2,
                                     max=32, size=(-1, -1),
                                     style=wx.TE_PROCESS_ENTER
                                     )
        siz_tile.Add(self.spin_cols, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_cols.Disable()
        self.lbl_pad = wx.StaticText(self, wx.ID_ANY, label="Padding:")
        siz_tile.Add(self.lbl_pad, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.lbl_pad.Disable()
        self.spin_pad = wx.SpinCtrl(self, wx.ID_ANY, "2", min=0,
                                    max=32, size=(-1, -1),
                                    style=wx.TE_PROCESS_ENTER
                                    )
        siz_tile.Add(self.spin_pad, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_pad.Disable()

        self.lbl_marg = wx.StaticText(self, wx.ID_ANY, label="Margin:")
        siz_tile.Add(self.lbl_marg, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.lbl_marg.Disable()
        self.spin_marg = wx.SpinCtrl(self, wx.ID_ANY, "2", min=0,
                                     max=32, size=(-1, -1),
                                     style=wx.TE_PROCESS_ENTER
                                     )
        siz_tile.Add(self.spin_marg, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_marg.Disable()
        siz_addparams = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(siz_addparams, 0, wx.EXPAND, 0)
        self.ckbx_edit = wx.CheckBox(self, wx.ID_ANY, _('Edit'))
        siz_addparams.Add(self.ckbx_edit, 0, wx.ALL | wx.EXPAND, 5)
        self.txt_args = wx.TextCtrl(self, wx.ID_ANY, size=(700, -1),)
        siz_addparams.Add(self.txt_args, 1, wx.ALL | wx.EXPAND, 5)
        self.txt_args.Disable()
        sizer.Add((20, 20))
        fgs1 = wx.BoxSizer(wx.VERTICAL)
        sizer_link1 = wx.BoxSizer(wx.HORIZONTAL)
        fgs1.Add(sizer_link1)
        lbl_msg1 = wx.StaticText(self, wx.ID_ANY,
                                 label=_("Official FFmpeg documentation:")
                                 )
        link1 = hpl.HyperLinkCtrl(self, -1, "image2",
                                  URL="https://ffmpeg.org/ffmpeg-"
                                      "formats.html#image2"
                                  )
        link2 = hpl.HyperLinkCtrl(self, -1, ("FFmpeg FAQ"),
                                  URL="https://ffmpeg.org/faq.html#How-do-I-"
                                      "encode-movie-to-single-pictures_003f"
                                  )
        link3 = hpl.HyperLinkCtrl(self, -1, ("FFmpeg Wiki"),
                                  URL="https://trac.ffmpeg.org/wiki/Create%"
                                      "20a%20thumbnail%20image%20every"
                                      "%20X%20seconds%20of%20the%20video"
                                  )
        sizer_link1.Add(lbl_msg1, 0, wx.ALL | wx.EXPAND, 5)
        sizer_link1.Add(link1)
        sizer_link1.Add((20, 20))
        sizer_link1.Add(link2)
        sizer_link1.Add((20, 20))
        sizer_link1.Add(link3)
        sizer_link2 = wx.BoxSizer(wx.HORIZONTAL)
        fgs1.Add(sizer_link2)
        lbl_msg2 = wx.StaticText(self, wx.ID_ANY,
                                 label=_("Other unofficial resources:")
                                 )
        link4 = hpl.HyperLinkCtrl(self, -1, ("Help Tile filter"),
                                  URL="http://underpop.online.fr/f/ffmpeg"
                                      "/help/tile.htm.gz"
                                  )
        link5 = hpl.HyperLinkCtrl(self, -1, ("High quality gif"),
                                  URL="http://blog.pkh.me/p/21-high-quality-"
                                      "gif-with-ffmpeg.html"
                                  )
        sizer_link2.Add(lbl_msg2, 0, wx.ALL | wx.EXPAND, 5)
        sizer_link2.Add(link4)
        sizer_link2.Add((20, 20))
        sizer_link2.Add(link5)
        sizer.Add(fgs1, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)

        if self.appdata['ostype'] == 'Darwin':
            lbl_msg1.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            lbl_msg2.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            lbl_msg1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            lbl_msg2.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        tip = (_('Set FPS control from 0.1 to 30.0 fps. The higher this '
                 'value, the more images will be extracted.'))
        self.spin_rate.SetToolTip(tip)
        tip = _('Spaces around the mosaic tiles. From 0 to 32 pixels')
        self.spin_pad.SetToolTip(tip)
        tip = _('Spaces around the mosaic borders. From 0 to 32 pixels')
        self.spin_marg.SetToolTip(tip)

        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_CHECKBOX, self.on_edit, self.ckbx_edit)
        self.Bind(wx.EVT_RADIOBOX, self.on_options, self.rdbx_opt)
        self.Bind(wx.EVT_BUTTON, self.on_resizing, self.btn_resize)
    # --------------------------------------------------------------#

    def on_help(self, event):
        """
        event on button help
        """
        win = NormalTransientPopup(self,
                                   wx.SIMPLE_BORDER,
                                   VideoToSequence.MSG_1,
                                   VideoToSequence.LGREEN,
                                   VideoToSequence.BLACK)

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = event.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Popup()
    # --------------------------------------------------------------#

    def on_edit(self, event):
        """
        edit in place with additional paramemeters
        """
        if self.ckbx_edit.IsChecked():
            self.spin_rate.Disable()
            self.cmb_frmt.Disable()
            self.lbl_rate.Disable()
            self.lbl_frmt.Disable()
            self.txt_args.Enable()
            self.btn_resize.Disable()
            self.lbl_rows.Disable()
            self.lbl_cols.Disable()
            self.lbl_pad.Disable()
            self.lbl_marg.Disable()
            self.spin_rows.Disable()
            self.spin_cols.Disable()
            self.spin_pad.Disable()
            self.spin_marg.Disable()
            arg = self.update_arguments(self.cmb_frmt.GetValue())
            self.txt_args.write(arg[1])
        else:
            if self.rdbx_opt.GetSelection() == 0:
                self.spin_rate.Enable()
                self.lbl_rate.Enable()
            if self.rdbx_opt.GetSelection() in (0, 1):
                self.cmb_frmt.Enable()
                self.lbl_frmt.Enable()
                self.btn_resize.Enable()
                if self.rdbx_opt.GetSelection() == 1:
                    self.lbl_rows.Enable()
                    self.lbl_cols.Enable()
                    self.lbl_pad.Enable()
                    self.lbl_marg.Enable()
                    self.spin_rows.Enable()
                    self.spin_cols.Enable()
                    self.spin_pad.Enable()
                    self.spin_marg.Enable()
            elif self.rdbx_opt.GetSelection() == 2:
                self.btn_resize.Enable()

            self.txt_args.Clear()
            self.txt_args.Disable()
    # ------------------------------------------------------------------#

    def on_options(self, event):
        """
        Available user options
        """
        if self.rdbx_opt.GetSelection() == 0:
            self.cmb_frmt.SetSelection(2)
            self.txt_args.Clear()
            self.lbl_rows.Disable()
            self.lbl_cols.Disable()
            self.lbl_pad.Disable()
            self.lbl_marg.Disable()
            self.spin_rows.Disable()
            self.spin_cols.Disable()
            self.spin_pad.Disable()
            self.spin_marg.Disable()
            self.on_edit(self)

        elif self.rdbx_opt.GetSelection() == 1:
            self.cmb_frmt.SetSelection(1)
            self.txt_args.Clear()
            self.lbl_rate.Disable()
            self.spin_rate.Disable()
            self.lbl_rows.Enable()
            self.lbl_cols.Enable()
            self.lbl_pad.Enable()
            self.lbl_marg.Enable()
            self.spin_rows.Enable()
            self.spin_cols.Enable()
            self.spin_pad.Enable()
            self.spin_marg.Enable()
            self.on_edit(self)

        elif self.rdbx_opt.GetSelection() == 2:
            self.cmb_frmt.SetSelection(3)
            self.cmb_frmt.Disable()
            self.lbl_frmt.Disable()
            self.txt_args.Clear()
            self.lbl_rate.Disable()
            self.spin_rate.Disable()
            self.lbl_rows.Disable()
            self.lbl_cols.Disable()
            self.lbl_pad.Disable()
            self.lbl_marg.Disable()
            self.spin_rows.Disable()
            self.spin_cols.Disable()
            self.spin_pad.Disable()
            self.spin_marg.Disable()
            self.on_edit(self)
    # ------------------------------------------------------------------#

    def file_selection(self):
        """
        Gets the selected file on files list and returns an object
        of type list [str('selected file name'), int(index)].
        Returns None if no files are selected.

        """
        if len(self.parent.file_src) == 1:
            return (self.parent.file_src[0], 0)

        if not self.parent.filedropselected:
            wx.MessageBox(_("Have to select an item in the file list first"),
                          'Videomass', wx.ICON_INFORMATION, self)
            return None

        clicked = self.parent.filedropselected
        return (clicked, self.parent.file_src.index(clicked))
    # ------------------------------------------------------------------#

    def get_video_stream(self):
        """
        Given a frame or a video file, it returns a tuple of data
        containing information on the streams required by some video
        filters.

        """
        fget = self.file_selection()
        if not fget:
            return None

        index = self.parent.data_files[fget[1]]

        if 'video' in index.get('streams')[0]['codec_type']:
            width = int(index['streams'][0]['width'])
            height = int(index['streams'][0]['height'])
            filename = index['format']['filename']
            duration = index['format'].get('time', '00:00:00.000')
            return dict(zip(['width', 'height', 'filename', 'duration'],
                            [width, height, filename, duration]))

        wx.MessageBox(_('The file is not a frame or a video file'),
                      _('Videomass - Warning!'), wx.ICON_WARNING)
        return None
    # ------------------------------------------------------------------#

    def on_resizing(self, event):
        """
        Enable or disable scale, setdar and setsar filters
        """
        kwa = self.get_video_stream()
        if not kwa:
            return
        with Scale(self,
                   self.opt["Scale"],
                   self.opt["Setdar"],
                   self.opt["Setsar"],
                   self.bmpreset,
                   **kwa,
                   ) as sizing:

            if sizing.ShowModal() == wx.ID_OK:
                data = sizing.getvalue()
                if not [x for x in data.values() if x]:
                    self.btn_resize.SetBackgroundColour(wx.NullColour)
                    self.opt["Setdar"] = ""
                    self.opt["Setsar"] = ""
                    self.opt["Scale"] = "scale=w=320:h=-1"
                else:
                    self.btn_resize.SetBackgroundColour(
                        wx.Colour(VideoToSequence.VIOLET))
                    self.opt["Scale"] = data['scale']
                    self.opt['Setdar'] = data['setdar']
                    self.opt['Setsar'] = data['setsar']
    # ------------------------------------------------------------------#

    def update_arguments(self, fmt):
        """
        Given a image format return the corresponding
        ffmpeg argument
        """
        if self.rdbx_opt.GetSelection() == 1:
            rows = self.spin_rows.GetValue()
            cols = self.spin_cols.GetValue()
            pad = self.spin_pad.GetValue()
            marg = self.spin_marg.GetValue()
            scale = self.opt["Scale"]
            if self.opt["Setdar"]:
                scale = f'{scale},{self.opt["Setdar"]}'
            if self.opt["Setsar"]:
                scale = f'{scale},{self.opt["Setsar"]}'
            cmd = ('-skip_frame nokey', f'-vf "{scale},tile={rows}x{cols}:'
                   f'padding={pad}:margin={marg}:color=White" -an '
                   f'-fps_mode vfr')

        elif self.rdbx_opt.GetSelection() == 2:
            setf = ''
            if self.opt["Setdar"]:
                setf = f',{self.opt["Setdar"]}'
            if self.opt["Setsar"]:
                setf = f'{setf},{self.opt["Setsar"]}'
            flt = (f'fps=10,{self.opt["Scale"]}:flags=lanczos,split=2 '
                   f'[a][b]; [a] palettegen [pal]; [b] '
                   f'[pal] paletteuse{setf}')
            cmd = ('', f'-vf "{flt}" -loop 0')

        elif self.rdbx_opt.GetSelection() == 0:
            scale = self.opt["Scale"]
            if self.opt["Setdar"]:
                scale = f'{scale},{self.opt["Setdar"]}'
            if self.opt["Setsar"]:
                scale = f'{scale},{self.opt["Setsar"]}'

            arg = {'jpeg': ('',
                            f'-fps_mode cfr -r {self.spin_rate.GetValue()} '
                            f'-vf "{scale}" -pix_fmt yuvj420p'
                            ),
                   'png': ('',
                           f'-fps_mode cfr -r {self.spin_rate.GetValue()} '
                           f'-vf "{scale}" -pix_fmt rgb24'
                           ),
                   'bmp': ('',
                           f'-fps_mode cfr -r {self.spin_rate.GetValue()} '
                           f'-vf "{scale}" -pix_fmt bgr24'
                           ),
                   'gif': ('',
                           f'-fps_mode cfr -r {self.spin_rate.GetValue()} '
                           f'-vf "{scale}"'
                           )
                   }
            cmd = arg[fmt]

        return cmd
    # ------------------------------------------------------------------#

    def on_start(self):
        """
        Check before Builds FFmpeg command arguments
        """
        fsource = self.parent.file_src
        if len(fsource) == 1:
            clicked = fsource[0]

        elif not self.parent.filedropselected:
            wx.MessageBox(_("Have to select an item in the file list first"),
                          'Videomass', wx.ICON_INFORMATION, self)
            return
        else:
            clicked = self.parent.filedropselected

        getclk = fsource.index(clicked)
        typemedia = self.parent.fileDnDTarget.flCtrl.GetItemText(getclk, 3)

        if 'video' not in typemedia or 'sequence' in typemedia:
            wx.MessageBox(_("Invalid file: '{}'").format(clicked),
                          _('Videomass - Error!'), wx.ICON_ERROR, self)
            return

        checking = check_files((clicked,),
                               self.appdata['outputdir'],
                               self.appdata['outputdir_asinput'],
                               self.appdata['filesuffix'],
                               self.cmb_frmt.GetValue(),
                               self.parent.outputnames
                               )
        if not checking:  # User changing idea or not such files exist
            return

        self.build_args(clicked, checking[1])
    # ------------------------------------------------------------------#

    def build_args(self, filename, outfile):
        """
        Save as files image the selected video input. The saved
        images are named as file name + a progressive number + .jpg
        and placed in a folder with the same file name + a progressive
        number in the chosen output path.

        """
        destdir = os.path.dirname(outfile[0])  # specified dest
        outputdir = trailing_name_with_prog_digit(destdir, 'Movie_to_Pictures')

        if self.cmb_frmt.GetValue() != 'gif':
            namesplit = os.path.splitext(outfile[0])
            fileout = f"{namesplit[0]}_%d{namesplit[1]}"
        else:
            fileout = f"{outfile[0]}"

        outfilename = os.path.join(outputdir, os.path.basename(fileout))

        if self.txt_args.IsEnabled():
            arg = self.update_arguments(self.cmb_frmt.GetValue())
            preargs = arg[0]
            command = " ".join(f'{self.txt_args.GetValue()} -y '
                               f'"{outfilename}"'.split())
        else:
            arg = self.update_arguments(self.cmb_frmt.GetValue())
            preargs = arg[0]
            command = " ".join(f'{arg[1]} {self.txt_args.GetValue()} -y '
                               f'"{outfilename}"'.split())

        dur, ss, et = update_timeseq_duration(self.parent.time_seq,
                                              self.parent.duration
                                              )
        kwargs = {'logname': 'From Movie to Pictures.log',
                  'type': 'video_to_sequence', 'duration': dur,
                  'start-time': ss, 'end-time': et, 'filename': filename,
                  'outputdir': outputdir, 'args': command,
                  'pre-input-1': preargs,
                  'preset name': 'From Movies to Pictures',
                  }
        keyval = self.update_dict(filename, outputdir)
        ending = Formula(self, (700, 280),
                         self.parent.movetotrash,
                         self.parent.emptylist,
                         **keyval,
                         )
        if ending.ShowModal() == wx.ID_OK:
            (self.parent.movetotrash,
             self.parent.emptylist) = ending.getvalue()
        else:
            return

        try:
            os.makedirs(outputdir, mode=0o777)
        except (OSError, FileExistsError) as err:
            wx.MessageBox(f"{err}", _('Videomass - Error!'),
                          wx.ICON_ERROR, self)
            return

        self.parent.switch_to_processing(kwargs["type"],
                                         kwargs["logname"],
                                         datalist=kwargs
                                         )
        return
    # ------------------------------------------------------------------#

    def update_dict(self, filename, outputdir):
        """
        Update information before send to epilogue

        """
        if not self.parent.time_seq:
            sst, endt = _('Same as source'), _('Same as source')
        else:
            endt = self.parent.time_seq.split()[3]
            sst = self.parent.time_seq.split()[1]

        if self.txt_args.IsEnabled():
            args = _('Enabled')
            rate = 'Disabled'
            resize, rows, cols, pad, marg = '', '', '', '', ''
        else:
            args = _('Disabled')
            resize = (f'{self.opt["Scale"]} '
                      f'{self.opt["Setdar"]} '
                      f'{self.opt["Setsar"]}')
            if self.rdbx_opt.GetSelection() == 0:
                rate = self.spin_rate.GetValue()
                rows, cols, pad, marg = '', '', '', ''
            elif self.rdbx_opt.GetSelection() == 1:
                rate = ''
                rows = self.spin_rows.GetValue()
                cols = self.spin_cols.GetValue()
                pad = self.spin_pad.GetValue()
                marg = self.spin_marg.GetValue()
            elif self.rdbx_opt.GetSelection() == 2:
                rate, rows, cols, pad, marg = '', '', '', '', ''

        keys = (_("Selected File\nOutput Format\n"
                  "Destination\nRate (fps)\nResizing\n"
                  "Mosaic rows\nMosaic columns\nMosaic padding\n"
                  "Mosaic margin\nCustom Arguments\n"
                  "Start of segment\nDuration"
                  ))
        vals = (f"{filename}\n{self.cmb_frmt.GetValue()}\n{outputdir}"
                f"\n{rate}\n{resize}\n{rows}\n{cols}\n{pad}\n{marg}"
                f"\n{args}\n{sst}\n{endt}"
                )
        return {'key': keys, 'val': vals}
