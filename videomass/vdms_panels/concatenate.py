# -*- coding: UTF-8 -*-
"""
Name: concatenate.py
Porpose: A simple concat demuxer UI
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.25.2024
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
import wx.lib.agw.hyperlink as hpl
from videomass.vdms_dialogs.widget_utils import NormalTransientPopup
from videomass.vdms_utils.utils import integer_to_time
from videomass.vdms_io.checkup import check_files
from videomass.vdms_dialogs.epilogue import Formula


def compare_media_param(data):
    """
    This function expects json data from FFprobe to checks
    that the indexed streams of each item in the list have
    the same codec, video size and audio sample rate in order
    to ensure correct file concatenation.
    Returns an error message if any error found,
    Returns None otherwise.
    """
    if len(data) == 1:
        return ('error',
                _('At least two files are required to perform concatenation.'))
    com = {}
    mediatype = []
    for streams in data:
        name = streams.get('format').get('filename')
        com[name] = {}
        for items in streams.get('streams'):
            mediatype.append(items.get('codec_type'))
            if items.get('codec_type') == 'video':
                com[name][items.get('index')] = [items.get('codec_name')]
                size = f"{items.get('width')}x{items.get('height')}"
                com[name][items.get('index')].append(size)
            if items.get('codec_type') == 'audio':
                com[name][items.get('index')] = [items.get('codec_name')]
                com[name][items.get('index')].append(items.get('sample_rate'))
    if not com:
        return ('error', _('Invalid data found'))

    totest = list(com.values())[0]
    if not all(val == totest for val in com.values()):
        return ('error',
                _('The files do not have the same "codec_types", '
                  'same "sample_rate" or same "width" or "height". '
                  'Unable to proceed.'))
    return None, mediatype[0]
# -------------------------------------------------------------------------


class Conc_Demuxer(wx.Panel):
    """
    A simple concat demuxer UI to set media files
    concatenation using concat demuxer,
    see <https://ffmpeg.org/ffmpeg-formats.html#concat>

    """
    LGREEN = '#52ee7d'
    BLACK = '#1f1f1f'
    MSG_1 = _("\n- The concatenation function is performed only with "
              "Audio files or only with Video files."
              "\n\n- The order of concatenation depends on the order in "
              "which the files were added."
              "\n\n- The output file name will have the same name as the "
              "first file added (also depends on the\n"
              "  settings made in the preferences dialog or the renaming "
              "functions used)."
              "\n\n- Video files must have exactly same streams, same "
              "codecs and same\n  width/height, but can be wrapped in "
              "different container formats."
              "\n\n- Audio files must have exactly the same formats, "
              "same codecs with equal sample rate.")

    # ----------------------------------------------------------------#

    def __init__(self, parent):
        """
        This is a panel impemented on MainFrame
        """
        get = wx.GetApp()  # get data from bootstrap
        self.appdata = get.appset
        self.cachedir = self.appdata['cachedir']
        self.parent = parent  # parent is the MainFrame
        self.args = ''
        self.duration = None
        self.ext = None
        self.mediatype = None

        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_THEME)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((20, 20))
        self.btn_help = wx.Button(self, wx.ID_ANY, _("Read me"), size=(-1, -1))
        self.btn_help.SetBackgroundColour(wx.Colour(Conc_Demuxer.LGREEN))
        self.btn_help.SetForegroundColour(wx.Colour(Conc_Demuxer.BLACK))
        sizer.Add(self.btn_help, 0, wx.ALL, 5)
        sizer.Add((20, 20))
        sizer_link2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer_link2)
        self.lbl_msg3 = wx.StaticText(self, wx.ID_ANY,
                                      label=_("Videomass Documentation:")
                                      )
        page = ("https://jeanslack.github.io/Videomass/User-guide/"
                "User_Interface_Overview_en.pdf")
        link2 = hpl.HyperLinkCtrl(self, -1, ("User Interface Overview"),
                                  URL=page)
        sizer_link2.Add(self.lbl_msg3, 0, wx.ALL | wx.EXPAND, 5)
        sizer_link2.Add(link2)
        sizer_link1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer_link1)
        self.lbl_msg2 = wx.StaticText(self, wx.ID_ANY,
                                      label=_("Official FFmpeg documentation:")
                                      )
        link1 = hpl.HyperLinkCtrl(self, -1, "Concat",
                                  URL="https://ffmpeg.org/ffmpeg-formats."
                                      "html#concat"
                                  )
        sizer_link1.Add(self.lbl_msg2, 0, wx.ALL | wx.EXPAND, 5)
        sizer_link1.Add(link1)
        self.SetSizer(sizer)

        if self.appdata['ostype'] == 'Darwin':
            self.lbl_msg2.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            self.lbl_msg3.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            self.lbl_msg2.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            self.lbl_msg3.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self.Bind(wx.EVT_BUTTON, self.on_help, self.btn_help)
    # ---------------------------------------------------------

    def on_help(self, event):
        """
        event on button help
        """
        win = NormalTransientPopup(self,
                                   wx.SIMPLE_BORDER,
                                   Conc_Demuxer.MSG_1,
                                   Conc_Demuxer.LGREEN,
                                   Conc_Demuxer.BLACK)

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = event.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Popup()
    # ---------------------------------------------------------

    def on_start(self):
        """
        Builds FFmpeg command arguments

        """
        fsource = self.parent.file_src
        ftext = os.path.join(self.cachedir, 'tmp', 'flist.txt')

        diff = compare_media_param(self.parent.data_files)
        if diff[0] == 'error':
            wx.MessageBox(diff[1], _('Videomass - Error!'),
                          wx.ICON_ERROR, self)
            return

        self.mediatype = diff[1]
        textstr = []
        self.ext = os.path.splitext(self.parent.file_src[0])[1].split('.')[1]
        self.duration = sum(self.parent.duration)
        for f in self.parent.file_src:
            escaped = f.replace(r"'", r"'\''")  # need escaping some chars
            textstr.append(f"file '{escaped}'")
        self.args = (f'"{ftext}" -map 0:v? -map_chapters 0 '
                     f'-map 0:s? -map 0:a? -map_metadata 0 -c copy')

        with open(ftext, 'w', encoding='utf-8') as txt:
            txt.write('\n'.join(textstr))

        checking = check_files((fsource[0],),
                               self.appdata['outputdir'],
                               self.appdata['outputdir_asinput'],
                               self.appdata['filesuffix'],
                               self.ext,
                               self.parent.outputnames
                               )
        if not checking:  # User changing idea or not such files exist
            return
        newfile = checking[1]

        self.build_args(self.parent.file_src, newfile[0])
    # -----------------------------------------------------------

    def build_args(self, filesrc, newfile):
        """
        Redirect to processing

        """
        logname = 'Concatenate Media File.log'

        kwargs = {'logname': logname, 'type': 'concat_demuxer',
                  'source': filesrc, 'destination': newfile, 'args': self.args,
                  'nmax': len(filesrc), 'duration': self.duration,
                  'start-time': '', 'end-time': '',
                  'preset name': 'Concatenate media files',
                  }
        keyval = self.update_dict(newfile, os.path.dirname(newfile))
        ending = Formula(self, (700, 170),
                         self.parent.movetotrash,
                         self.parent.emptylist,
                         **keyval,
                         )
        if ending.ShowModal() == wx.ID_OK:
            (self.parent.movetotrash,
             self.parent.emptylist) = ending.getvalue()
            self.parent.switch_to_processing(kwargs["type"],
                                             logname,
                                             datalist=kwargs)
    # -----------------------------------------------------------

    def update_dict(self, newfile, destdir):
        """
        Update information before send to epilogue

        """
        lenfile = len(self.parent.file_src)
        dur = integer_to_time(self.duration)
        dest = os.path.join(destdir, newfile)

        keys = (_("Items to concatenate\nFile destination\nOutput Format"
                  "\nOutput multimedia type\nDuration"
                  ))
        vals = (f"{lenfile}\n{dest}\n{self.ext}\n"
                f"{self.mediatype}\n{dur}")

        return {'key': keys, 'val': vals}
