# -*- coding: UTF-8 -*-
"""
Name: sequence_to_video.py
Porpose: A slideshow maker based on FFmpeg
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: May.22.2024
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
from videomass.vdms_dialogs.widget_utils import NormalTransientPopup
from videomass.vdms_utils.get_bmpfromsvg import get_bmp
from videomass.vdms_dialogs.epilogue import Formula
from videomass.vdms_dialogs.filter_scale import Scale
from videomass.vdms_threads.ffprobe import ffprobe
from videomass.vdms_utils.utils import trailing_name_with_prog_digit
from videomass.vdms_utils.utils import time_to_integer
from videomass.vdms_utils.utils import integer_to_time


def check_images_size(flist):
    """
    Check for images size, if not equal return True,
    None otherwise.
    """
    sizes = []
    for index in flist:
        if 'video' in index.get('streams')[0]['codec_type']:
            width = index['streams'][0]['width']
            height = index['streams'][0]['height']
            sizes.append(f'{width}x{height}')

    if len(set(sizes)) > 1:
        wx.MessageBox(_('Images need to be resized, '
                        'please use Resize function.'),
                      'Videomass', wx.ICON_INFORMATION)
        return True

    return None
# -------------------------------------------------------------------------


class SequenceToVideo(wx.Panel):
    """
    This is an new implementation class to create
    Slideshow and static videos with the ability to
    add an audio track, resizing, and more.

    """
    VIOLET = '#D64E93'
    LGREEN = '#52ee7d'
    BLACK = '#1f1f1f'
    MSG_1 = _("\n1. Import one or more image files such as JPG, PNG and BMP "
              "formats (even in mixed mode),\nthen select one as your "
              "starting point."
              "\n\n2. Use the Resize tool if your images have different width "
              "and height dimensions.\nYou only need to do this once for the "
              "selected file to automatically resize the other images.\n"
              "Otherwise, it's optional."
              "\n\n3. Set a time interval between images, or for a single "
              "image if you\n«Enable a single still image» option."
              "\n\n4. Run the conversion."
              "\n\n\nThe produced video will have the name of the selected "
              "file in the 'File List' panel, which\nwill be saved in a "
              "folder named 'Still_Images' with a progressive digit, "
              "in the path you specify.")
    # ---------------------------------------------------------------------

    def __init__(self, parent):
        """
        Simple GUI panel with few controls to create slideshows
        based on ffmpeg syntax.
        """
        self.parent = parent  # parent is the MainFrame
        get = wx.GetApp()  # get data from bootstrap
        self.appdata = get.appset
        icons = get.iconset
        self.ffprobe_cmd = self.appdata['ffprobe_cmd']
        self.opt = {"Scale": "", "Setdar": "", "Setsar": "",
                    "RESIZE": "", "ADuration": 0, "AudioMerging": "",
                    "Map": "-map 0:v?", "Shortest": ["", "Disabled"],
                    "Interval": "", "Clock": "00:00:00:000",
                    "Preinput": "1/0", "Fps": ["fps=10,", "10"],
                    }

        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up
            bmpresize = get_bmp(icons['scale'], ((16, 16)))
            bmpatrack = get_bmp(icons['atrack'], ((16, 16)))
            self.bmpreset = get_bmp(icons['clear'], ((16, 16)))
        else:
            bmpresize = wx.Bitmap(icons['scale'], wx.BITMAP_TYPE_ANY)
            bmpatrack = wx.Bitmap(icons['atrack'], wx.BITMAP_TYPE_ANY)
            self.bmpreset = wx.Bitmap(icons['clear'], wx.BITMAP_TYPE_ANY)

        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((20, 20))
        btn_help = wx.Button(self, wx.ID_ANY, _("Read me"), size=(-1, -1))
        btn_help.SetBackgroundColour(wx.Colour(SequenceToVideo.LGREEN))
        btn_help.SetForegroundColour(wx.Colour(SequenceToVideo.BLACK))
        sizer.Add(btn_help, 0, wx.ALL, 5)
        sizer.Add((20, 20))
        # sizer.Add((5, 5))
        boxctrl = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY), wx.VERTICAL)
        sizer.Add(boxctrl, 0, wx.ALL | wx.EXPAND, 5)
        siz_format = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(siz_format)
        self.ckbx_static_img = wx.CheckBox(self, wx.ID_ANY,
                                           _('Enable a single still image'))
        boxctrl.Add(self.ckbx_static_img, 0, wx.ALL | wx.EXPAND, 5)
        boxctrl.Add((15, 15), 0)
        siz_sec = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(siz_sec)
        msg = _('Time interval between images (in seconds):')
        lbl_sec = wx.StaticText(self, wx.ID_ANY, label=msg)
        siz_sec.Add(lbl_sec, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.spin_sec = wx.SpinCtrl(self, wx.ID_ANY, "1", min=1,
                                    max=1000, size=(-1, -1),
                                    style=wx.TE_PROCESS_ENTER
                                    )
        siz_sec.Add(self.spin_sec, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        boxctrl.Add((15, 15), 0)
        siz_pict = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(siz_pict)
        lbl_fps = wx.StaticText(self, wx.ID_ANY, label="FPS:")
        siz_pict.Add(lbl_fps, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_fps = wx.ComboBox(self, wx.ID_ANY,
                                   choices=[("None"),
                                            ("ntsc"),
                                            ("pal"),
                                            ("film"),
                                            ("23.976"),
                                            ("24"),
                                            ("25"),
                                            ("29.97"),
                                            ("30"),
                                            ("5"),
                                            ("10"),
                                            ("15"),
                                            ("60")
                                            ],
                                   size=(160, -1),
                                   style=wx.CB_DROPDOWN | wx.CB_READONLY
                                   )
        siz_pict.Add(self.cmb_fps, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.cmb_fps.SetSelection(10)
        self.btn_resize = wx.Button(self, wx.ID_ANY, _("Resize"),
                                    size=(-1, -1)
                                    )
        self.btn_resize.SetBitmap(bmpresize, wx.LEFT)
        siz_pict.Add(self.btn_resize, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.ckbx_far = wx.CheckBox(self, wx.ID_ANY,
                                    _('Force original aspect ratio using\n'
                                      'padding rather than stretching'))
        siz_pict.Add(self.ckbx_far, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.ckbx_far.Disable()

        boxctrl.Add((15, 15), 0)
        siz_audio = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(siz_audio)
        self.ckbx_audio = wx.CheckBox(self, wx.ID_ANY, _('Include audio file'))
        siz_audio.Add(self.ckbx_audio, 0, wx.ALL | wx.CENTRE, 5)
        self.ckbx_shortest = wx.CheckBox(self, wx.ID_ANY,
                                         _('Play the video until '
                                           'audio track finishes'
                                           ))
        siz_audio.Add(self.ckbx_shortest, 0, wx.ALL | wx.CENTRE, 5)
        self.ckbx_shortest.Disable()
        siz_afile = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(siz_afile)
        self.btn_openaudio = wx.Button(self, wx.ID_ANY, _("Open audio file"),
                                       size=(-1, -1)
                                       )
        self.btn_openaudio.SetBitmap(bmpatrack, wx.LEFT)
        siz_afile.Add(self.btn_openaudio, 0, wx.ALL
                      | wx.ALIGN_CENTER_VERTICAL, 5)
        self.btn_openaudio.Disable()

        self.txt_apath = wx.TextCtrl(self, wx.ID_ANY, size=(500, -1),
                                     style=wx.TE_READONLY
                                     )
        siz_afile.Add(self.txt_apath, 0, wx.ALL, 5)
        self.txt_apath.Disable()

        boxctrl.Add((15, 15), 0)
        siz_addparams = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(siz_addparams, 0, wx.EXPAND, 0)

        self.ckbx_edit = wx.CheckBox(self, wx.ID_ANY,
                                     _('Additional arguments'))
        siz_addparams.Add(self.ckbx_edit, 0, wx.ALL | wx.CENTRE, 5)
        self.txt_addparams = wx.TextCtrl(self, wx.ID_ANY,
                                         value=('-c:v libx264 -crf 23 '
                                                '-tune:v stillimage'),
                                         size=(-1, -1),)
        siz_addparams.Add(self.txt_addparams, 1, wx.ALL | wx.EXPAND, 5)
        self.txt_addparams.Disable()
        sizer.Add((20, 20))
        fgs1 = wx.BoxSizer(wx.VERTICAL)
        sizer_link1 = wx.BoxSizer(wx.HORIZONTAL)
        fgs1.Add(sizer_link1)
        lbl_link = wx.StaticText(self, wx.ID_ANY,
                                 label=_("Official FFmpeg documentation:")
                                 )
        link1 = hpl.HyperLinkCtrl(self, -1, ("FFmpeg Slideshow Wiki"),
                                  URL="https://trac.ffmpeg.org/wiki/Slideshow"
                                  )
        sizer_link1.Add(lbl_link, 0, wx.ALL | wx.EXPAND, 5)
        sizer_link1.Add(link1)
        sizer.Add(fgs1, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)

        if self.appdata['ostype'] == 'Darwin':
            lbl_link.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            lbl_link.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_CHECKBOX, self.on_enable_audio, self.ckbx_audio)
        self.Bind(wx.EVT_BUTTON, self.on_addaudio_track, self.btn_openaudio)
        self.Bind(wx.EVT_CHECKBOX, self.on_shortest, self.ckbx_shortest)
        self.Bind(wx.EVT_CHECKBOX, self.on_addparams, self.ckbx_edit)
        self.Bind(wx.EVT_CHECKBOX, self.on_force_aspect_ratio, self.ckbx_far)
        self.Bind(wx.EVT_COMBOBOX, self.on_fps, self.cmb_fps)
        self.Bind(wx.EVT_BUTTON, self.on_resizing, self.btn_resize)
    # ---------------------------------------------------------

    def on_help(self, event):
        """
        event on button help
        """
        win = NormalTransientPopup(self,
                                   wx.SIMPLE_BORDER,
                                   SequenceToVideo.MSG_1,
                                   SequenceToVideo.LGREEN,
                                   SequenceToVideo.BLACK)

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = event.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Popup()
    # ------------------------------------------------------------------#

    def reset_all_values(self):
        """
        Reset all control and dictionary values
        NOTE this method is not used for now
        """
        self.opt["Scale"], self.opt["Setdar"] = "", ""
        self.opt["Setsar"], self.opt["RESIZE"] = "", ""
        self.opt["Preinput"] = "1/0"
        self.opt["Shortest"] = ["", "Disabled"]
        self.opt["Interval"] = ""
        self.opt["Clock"] = "00:00:00.000"
        self.ckbx_static_img.SetValue(False)
        self.btn_resize.SetBackgroundColour(wx.NullColour)
        self.ckbx_audio.SetValue(False)
        self.on_enable_audio(self)
        self.ckbx_shortest.SetValue(False)
    # ---------------------------------------------------------

    def on_addparams(self, event):
        """
        Enable additional args to command line
        """
        if self.ckbx_edit.IsChecked():
            self.txt_addparams.Enable()
        else:
            self.txt_addparams.Disable()
    # ---------------------------------------------------------

    def on_force_aspect_ratio(self, event):
        """
        Adds extra params to scale filter to preserving
        images aspect ratio.

        """
        if self.ckbx_far.IsChecked():
            width = self.opt["Scale"].split(':', maxsplit=1)[0][8:]
            height = self.opt["Scale"].split(':', maxsplit=1)[1][2:]
            params = (f':force_original_aspect_ratio=decrease:eval=frame,'
                      f'pad={width}:{height}:-1:-1:eval=frame')
            scale = ''.join(self.opt["Scale"] + params)
            if self.opt["Setdar"]:
                scale = f'{scale},{self.opt["Setdar"]}'
            if self.opt["Setsar"]:
                scale = f'{scale},{self.opt["Setsar"]}'
            self.opt["RESIZE"] = f'-vf "{scale}"'
        else:
            scale = self.opt["Scale"]
            if self.opt["Setdar"]:
                scale = f'{scale},{self.opt["Setdar"]}'
            if self.opt["Setsar"]:
                scale = f'{scale},{self.opt["Setsar"]}'
            self.opt["RESIZE"] = f'-vf "{scale}"'
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
                    self.opt["Scale"] = ""
                    self.opt["RESIZE"] = ''
                    self.ckbx_far.SetValue(False)
                    self.ckbx_far.Disable()
                else:
                    self.btn_resize.SetBackgroundColour(
                        wx.Colour(SequenceToVideo.VIOLET))
                    self.opt["Scale"] = data['scale']
                    self.opt['Setdar'] = data['setdar']
                    self.opt['Setsar'] = data['setsar']

                    flt = ''.join([f'{x},' for x in data.values() if x])[:-1]
                    if flt:
                        self.opt["RESIZE"] = f'-vf "{flt}"'
                        if '=-1' in data['scale'] or '=-2' in data['scale']:
                            self.ckbx_far.SetValue(False)
                            self.ckbx_far.Disable()
                        else:
                            self.ckbx_far.Enable()
                        if self.ckbx_far.IsChecked():
                            self.on_force_aspect_ratio(self)
    # ---------------------------------------------------------

    def on_fps(self, event):
        """
        Set frame per seconds using ComboBox
        """
        val = self.cmb_fps.GetValue()
        if val == 'None':
            self.opt["Fps"] = ['', 'None']
        else:
            self.opt["Fps"] = [f'fps={val},', val]
    # ---------------------------------------------------------

    def on_shortest(self, event):
        """
        Enable or disable shortest when audio file is loaded.
        Always disabled otherwise.
        """
        if self.ckbx_shortest.IsChecked():
            self.opt["Shortest"] = ["", "Disabled"]
        else:
            self.opt["Shortest"] = ["-shortest", "Enabled"]
    # ---------------------------------------------------------

    def on_enable_audio(self, event):
        """
        Enables controls to create a video file from a
        sequence of images using Concat Demuxer.
        """
        if self.ckbx_audio.IsChecked():
            self.btn_openaudio.Enable()
            self.txt_apath.Enable()
            self.ckbx_shortest.Enable()
            self.opt["Shortest"] = ["-shortest", "Enabled"]
        else:
            self.btn_openaudio.Disable()
            self.txt_apath.Disable()
            self.txt_apath.Clear()
            self.ckbx_shortest.Disable()
            self.ckbx_shortest.SetValue(False)
            self.btn_openaudio.SetBackgroundColour(wx.NullColour)
            self.btn_openaudio.SetLabel(_("Open audio file"))
            self.opt["AudioMerging"] = ''
            self.opt["Map"] = '-map 0:v?'
            self.opt["ADuration"] = 0
            self.opt["Shortest"] = ["", "Disabled"]
    # ---------------------------------------------------------

    def on_addaudio_track(self, event):
        """
        Add audio track to video.
        """
        fmt = ('*.wav;*.aiff;*.flac;*.oga;*.ogg;*.opus;*.tta;*.m4a;'
               '*.aac;*.ac3;*.mp3;')
        wild = f"Audio source ({fmt})|{fmt}| All files (*.*)|*.*"

        with wx.FileDialog(self, _("Open Audio File"),
                           wildcard=wild,
                           style=wx.FD_OPEN
                           | wx.FD_FILE_MUST_EXIST) as fdlg:

            if fdlg.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fdlg.GetPath()

        probe = ffprobe(pathname, self.ffprobe_cmd, hide_banner=None)

        if probe[1]:  # some error
            msg = _("Invalid file: '{}'\n\n{}").format(pathname, probe[1])
            wx.MessageBox(msg, _('Videomass - Error!'), wx.ICON_ERROR, self)
            return

        if probe[0]['streams'][0]['codec_type'] != 'audio':
            msg = _("Invalid file: '{}'\n\n"
                    "It doesn't appear to be an audio file.").format(pathname)
            wx.MessageBox(msg, _('Videomass - Error!'), wx.ICON_ERROR, self)
            return

        self.btn_openaudio.SetBackgroundColour(
            wx.Colour(SequenceToVideo.VIOLET))
        ext = os.path.splitext(pathname)[1].replace('.', '').upper()
        self.btn_openaudio.SetLabel(ext)
        self.txt_apath.write(pathname)
        self.opt["AudioMerging"] = f'-i "{pathname}"'
        self.opt["Map"] = '-map 0:v:0 -map 1:a:0'
        mills = float(probe[0]['format']['duration']) * 1000
        self.opt["ADuration"] = round(mills)
    # ---------------------------------------------------------

    def build_command_slideshow(self, timeline):
        """
        Set ffmpeg arguments for a slideshow.
        """
        loop = ''
        if (self.ckbx_audio.IsChecked()
                and self.txt_apath.GetValue().strip()
                and not self.opt["Shortest"][0]):
            self.opt["Clock"] = integer_to_time(self.opt["ADuration"])
            sec = time_to_integer(timeline, sec=True, rnd=True)
            duration = self.opt["ADuration"]
            loop = f'-loop 1 -t {self.opt["Clock"]}'
        else:
            sec = time_to_integer(timeline, sec=True, rnd=True)
            duration = sec * len(self.parent.file_src) * 1000
            self.opt["Clock"] = integer_to_time(duration)

        framerate = '-framerate 1/1' if not sec else f'-framerate 1/{sec}'
        self.opt["Preinput"] = f'{loop} {framerate}'
        self.opt["Interval"] = sec

        if self.txt_addparams.IsEnabled():
            addparam = self.txt_addparams.GetValue()
        else:
            addparam = ''

        cmd_2 = (f'{self.opt["AudioMerging"]} {addparam} -vf '
                 f'"{self.opt["Fps"][0]}format=yuv420p" {self.opt["Map"]} '
                 f'{self.opt["Shortest"][0]}')

        return cmd_2, duration
    # ---------------------------------------------------------

    def build_command_loop_image(self, timeline):
        """
        Set ffmpeg arguments for a static video,
        the checkbox `create a static video from image` is checked.

        """
        if (self.ckbx_audio.IsChecked()
                and self.txt_apath.GetValue().strip()
                and not self.opt["Shortest"][0]):
            self.opt["Clock"] = integer_to_time(self.opt["ADuration"])
            duration = self.opt["ADuration"]
            sec = round(self.opt["ADuration"] / 1000)
        else:
            sec = time_to_integer(timeline, sec=True, rnd=True)
            duration = sec * 1000
            self.opt["Clock"] = integer_to_time(duration)

        self.opt["Preinput"] = f'-loop 1 -t {self.opt["Clock"]}'
        self.opt["Interval"] = sec

        if self.txt_addparams.IsEnabled():
            addparam = self.txt_addparams.GetValue()
        else:
            addparam = ''

        cmd_2 = (f'{self.opt["AudioMerging"]} {addparam} -vf '
                 f'"{self.opt["Fps"][0]}format=yuv420p" {self.opt["Map"]} '
                 f'{self.opt["Shortest"][0]}')

        return cmd_2, duration
    # ---------------------------------------------------------

    def check_to_slide(self, fsource):
        """
        Check compatibility between loaded images and files exist.
        """
        itemcount = self.parent.fileDnDTarget.flCtrl.GetItemCount()
        for itc in range(itemcount):
            typemedia = self.parent.fileDnDTarget.flCtrl.GetItemText(itc, 3)
            if 'video' not in typemedia or 'sequence' not in typemedia:
                wx.MessageBox(_("Invalid file: '{}'").format(fsource[itc]),
                              _('Videomass - Error!'), wx.ICON_ERROR, self)
                return True

        unsupp = [f for f in fsource if os.path.splitext(f)[1]
                  not in ('.jpeg', '.jpg', '.png', '.bmp',
                          '.JPEG', '.JPG', '.PNG', '.BMP')
                  ]
        if unsupp:
            ext = os.path.splitext(unsupp[0])[1]
            wx.MessageBox(_("Unsupported format '{}'").format(ext),
                          _('Videomass - Error!'), wx.ICON_ERROR, self)
            return True

        for fsrc in fsource:
            if not os.path.isfile(os.path.abspath(fsrc)):
                wx.MessageBox(_('File does not exist:\n\n"{}"\n').format(fsrc),
                              _('ERROR'), wx.ICON_ERROR, self)
                return True
        return None
    # ---------------------------------------------------------

    def check_to_loop(self, typemedia, clicked):
        """
        Check the compatibility of the selected image and file exist.
        """
        if 'video' not in typemedia or 'sequence' not in typemedia:
            wx.MessageBox(_("Invalid file: '{}'").format(clicked),
                          _('Videomass - Error!'), wx.ICON_ERROR, self)
            return True

        supp = ('.jpeg', '.jpg', '.png', '.bmp',
                '.JPEG', '.JPG', '.PNG', '.BMP')
        ext = os.path.splitext(clicked)[1]
        if ext not in supp:
            wx.MessageBox(_("Unsupported format '{}'").format(ext),
                          _('Videomass - Error!'), wx.ICON_ERROR, self)
            return True

        if not os.path.isfile(os.path.abspath(clicked)):
            wx.MessageBox(_('File does not exist:'
                            '\n\n"{}"\n').format(clicked),
                          _('Videomass - Error!'), wx.ICON_ERROR, self)
            return True
        return None
    # ---------------------------------------------------------

    def get_args_line(self):
        """
        get arguments line for 'loop' or 'slide' modes
        """
        timeline = integer_to_time(self.spin_sec.GetValue() * 1000)

        if self.ckbx_static_img.IsChecked():
            args = self.build_command_loop_image(timeline)
        else:
            args = self.build_command_slideshow(timeline)

        return args
    # ---------------------------------------------------------

    def on_start(self):
        """
        Redirect to `switch_to_processing`
        """
        fget = self.file_selection()
        if not fget:
            return

        fsource = self.parent.file_src

        if self.appdata['outputdir_asinput']:
            destdir = os.path.dirname(fget[0])
        else:
            destdir = self.appdata['outputdir']

        name = self.parent.fileDnDTarget.flCtrl.GetItemText(fget[1], 5)
        outputdir = trailing_name_with_prog_digit(destdir, 'Still_Images')

        if outputdir[0] == 'ERROR':
            wx.MessageBox(f"{outputdir[1]}", _('Videomass - Error!'),
                          wx.ICON_ERROR, self)
            return

        destdir = os.path.join(outputdir, f"{name}.mkv")

        if self.ckbx_static_img.IsChecked():
            countmax = 1
            files = (fget[0],)
            prop = self.parent.fileDnDTarget.flCtrl.GetItemText(fget[1], 3)
            if self.check_to_loop(prop, fget[0]):
                return
        else:
            files = fsource
            countmax = len(files)
            if self.check_to_slide(files):
                return
            if not self.opt["RESIZE"] and countmax != 1:
                if check_images_size(self.parent.data_files):
                    return

        args = self.get_args_line()  # get args for command line
        kwargs = {'logname': 'Still Image Maker.log',
                  'type': 'sequence_to_video', 'source': files,
                  'destination': destdir, 'outputdir': outputdir,
                  'args': args[0], 'nmax': countmax, 'duration': args[1],
                  'pre-input-1': self.opt["Preinput"],
                  'resize': self.opt["RESIZE"],
                  'start-time': '', 'end-time': '',
                  'preset name': 'Still Image Maker',
                  }
        keyval = self.update_dict(f"{name}.mkv", outputdir, countmax, 'mkv')
        ending = Formula(self, (700, 320),
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
    # -----------------------------------------------------------

    def update_dict(self, newfile, destdir, count, ext):
        """
        Update information before send to epilogue

        """
        time = self.opt["Clock"]
        resize = _('Enabled') if self.opt["RESIZE"] else _('Disabled')
        short = self.opt["Shortest"][1]
        preinput = self.opt["Preinput"]
        duration = self.opt["Interval"]
        if self.ckbx_edit.IsChecked():
            addargs = self.txt_addparams.GetValue()
        else:
            addargs = ''

        keys = (_("Items to concatenate\nOutput filename"
                  "\nDestination\nOutput Format"
                  "\nAdditional arguments"
                  "\nAudio file\nShortest\nResize\nPre-input"
                  "\nFrame per Second (FPS)\nStill image duration"
                  "\nOverall video duration"
                  ))
        vals = (f'{count}\n{newfile}\n{destdir}\n{ext}\n{addargs}'
                f'\n{self.txt_apath.GetValue()}\n{short}'
                f'\n{resize}\n{preinput}\n{self.opt["Fps"][1]}'
                f'\n{duration} Seconds\n{time}'
                )
        return {'key': keys, 'val': vals}
