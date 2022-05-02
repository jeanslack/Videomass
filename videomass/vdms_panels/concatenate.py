# -*- coding: UTF-8 -*-
"""
Name: concatenate.py
Porpose: A simple concat demuxer UI
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.24.2022
Code checker:
    flake8: --ignore F821, W504
    pylint: --ignore E0602, E1101
########################################################

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
from videomass.vdms_io.checkup import check_files
from videomass.vdms_dialogs.epilogue import Formula


def compare_media_param(data):
    """
    Compare video codec types, audio codec types with sample_rate,
    dimensions (width and height).

    Returns True if differences are found between them,
    otherwise it returns False.

    """
    vcodec = []  # video codec
    acodec = []  # audio codec
    ahz = []  # audio sample rate
    size = []  # width x height (frame dimensions if video)

    for streams in data:
        for items in streams.get('streams'):
            if items.get('codec_type') == 'video':
                vcodec.append(items.get('codec_name'))
                size.append(f"{items.get('width')}x{items.get('height')}")
            if items.get('codec_type') == 'audio':
                acodec.append(items.get('codec_name'))
                ahz.append(items.get('sample_rate'))

    for compare in (vcodec, acodec, ahz, size):
        if len(compare) == 1:
            return True

        if all(items == compare[0] for items in compare) is False:
            return True

    return False
# -------------------------------------------------------------------------


class Conc_Demuxer(wx.Panel):
    """
    A simple concat demuxer UI to set media files
    concatenation using concat demuxer,
    see <https://ffmpeg.org/ffmpeg-formats.html#concat>

    """
    MSG_1 = _("NOTE:\n\n- The concatenation function is performed only with "
              "Audio files or only with Video files."
              "\n\n- The order of concatenation depends on the order in "
              "which the files were added."
              "\n\n- The output file name will have the same name as the "
              "first file added (also depends\n"
              "  on the settings made in the preferences dialog)."
              "\n\n- Video files must have exactly same streams, same "
              "codecs and same\n  width/height, but can be wrapped in "
              "different container formats."
              "\n\n- Audio files must have exactly the same formats, "
              "same codecs and same sample rate.")

    # ----------------------------------------------------------------#

    def __init__(self, parent):
        """
        This is a panel impemented on MainFrame
        """
        get = wx.GetApp()
        appdata = get.appset
        self.cachedir = appdata['cachedir']
        self.parent = parent  # parent is the MainFrame
        self.args = ''

        wx.Panel.__init__(self, parent=parent, style=wx.BORDER_THEME)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.lbl_msg1 = wx.StaticText(self, wx.ID_ANY,
                                      label=Conc_Demuxer.MSG_1
                                      )
        sizer.Add(self.lbl_msg1, 0, wx.ALL | wx.EXPAND, 5)
        sizer_link2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer_link2)
        self.lbl_msg3 = wx.StaticText(self, wx.ID_ANY,
                                      label=_("For more details, see the "
                                              "Videomass User Guide:")
                                      )
        if appdata['GETLANG'] in appdata['SUPP_LANGs']:
            lang = appdata['GETLANG'].split('_')[0]
            page = (f"https://jeanslack.github.io/Videomass/"
                    f"Pages/User-guide-languages/{lang}/1-User_"
                    f"Interface_Overview_{lang}.pdf")
        else:
            page = ("https://jeanslack.github.io/Videomass/"
                    "Pages/User-guide-languages/en/1-User_"
                    "Interface_Overview_en.pdf"
                    )
        link2 = hpl.HyperLinkCtrl(self, -1, ("1.4 Concatenate media files "
                                              "(demuxer)"), URL=page)
        sizer_link2.Add(self.lbl_msg3, 0, wx.ALL | wx.EXPAND, 5)
        sizer_link2.Add(link2)
        sizer_link1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer_link1)
        self.lbl_msg2 = wx.StaticText(self, wx.ID_ANY,
                                      label=_("For more information, "
                                              "visit the official FFmpeg "
                                              "documentation:")
                                      )
        link1 = hpl.HyperLinkCtrl(self, -1, "3.4 concat",
                                  URL="https://ffmpeg.org/ffmpeg-formats."
                                      "html#concat"
                                  )
        sizer_link1.Add(self.lbl_msg2, 0, wx.ALL | wx.EXPAND, 5)
        sizer_link1.Add(link1)
        line1 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        sizer.Add(line1, 0, wx.ALL | wx.EXPAND, 5)
        # sizer.Add((20, 20))
        boxctrl = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY), wx.VERTICAL)
        sizer.Add(boxctrl, 0, wx.ALL | wx.EXPAND, 5)
        sizFormat = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(sizFormat)

        siz_pict = wx.BoxSizer(wx.HORIZONTAL)
        boxctrl.Add(siz_pict)
        self.ckbx_pict = wx.CheckBox(self, wx.ID_ANY,
                                     _('From an image sequence '
                                       'to a video file')
                                     )
        siz_pict.Add(self.ckbx_pict, 0, wx.ALL | wx.EXPAND, 5)
        self.lbl_pict = wx.StaticText(self, wx.ID_ANY,
                                      label=_("Duration:")
                                      )
        siz_pict.Add(self.lbl_pict, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.lbl_pict.Disable()
        self.spin_pict = wx.SpinCtrl(self, wx.ID_ANY, "0", min=1,
                                     max=100, size=(-1, -1),
                                     style=wx.TE_PROCESS_ENTER
                                     )
        siz_pict.Add(self.spin_pict, 0, wx.ALL, 5)
        self.spin_pict.Disable()
        self.lbl_frmt = wx.StaticText(self, wx.ID_ANY,
                                      label=_("Output format:")
                                      )
        siz_pict.Add(self.lbl_frmt, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.lbl_frmt.Disable()

        self.cmb_pict = wx.ComboBox(self, wx.ID_ANY, choices=['mkv', 'mp4'],
                                    size=(160, -1), style=wx.CB_DROPDOWN |
                                    wx.CB_READONLY)
        siz_pict.Add(self.cmb_pict, 0, wx.ALL, 5)
        self.cmb_pict.SetSelection(0)
        self.cmb_pict.Disable()

        self.SetSizer(sizer)

        if appdata['ostype'] == 'Darwin':
            self.lbl_msg1.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.lbl_msg2.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            self.lbl_msg3.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            self.lbl_msg1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.lbl_msg2.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            self.lbl_msg3.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        tip = (_('Set the time interval between images in seconds '
                 '(from 1 to 100 sec.), default is 1 second'))
        self.spin_pict.SetToolTip(tip)

        self.Bind(wx.EVT_CHECKBOX, self.on_pictures, self.ckbx_pict)
    # ---------------------------------------------------------

    def on_pictures(self, event):
        """
        Enables controls to create a video file from a
        sequence of images using Concat Demuxer.
        """
        if self.ckbx_pict.IsChecked():
            self.lbl_pict.Enable()
            self.spin_pict.Enable()
            self.lbl_frmt.Enable()
            self.cmb_pict.Enable()
        else:
            self.lbl_pict.Disable()
            self.spin_pict.Disable()
            self.lbl_frmt.Disable()
            self.cmb_pict.Disable()
    # ---------------------------------------------------------

    def on_start(self):
        """
        Builds FFmpeg command arguments

        """
        fsource = self.parent.file_src
        basename = os.path.basename(fsource[0].rsplit('.')[0])
        ftext = os.path.join(self.cachedir, 'tmp', 'flist.txt')

        if len(fsource) < 2:
            wx.MessageBox(_('At least two files are required to perform '
                            'concatenation.'), _('ERROR'),
                          wx.ICON_ERROR, self
                          )
            return

        diff = compare_media_param(self.parent.data_files)

        if diff is True:
            wx.MessageBox(_('The files do not have the same "codec_types", '
                            'same "sample_rate" or same "width" or "height". '
                            'Unable to proceed.'),
                          _('ERROR'), wx.ICON_ERROR, self
                          )
            return

        textstr = []
        if not self.ckbx_pict.IsChecked():
            ext = os.path.splitext(self.parent.file_src[0])[1].split('.')[1]
            self.duration = sum(self.parent.duration)
            for f in self.parent.file_src:
                escaped = f.replace(r"'", r"'\'")  # need escaping some chars
                textstr.append(f"file '{escaped}'")
            self.args = (f'"{ftext}" -map 0:v? -map_chapters 0 '
                         f'-map 0:s? -map 0:a? -map_metadata 0 -c copy')
        else:
            ext = self.cmb_pict.GetValue()
            duration = self.spin_pict.GetValue() * len(self.parent.file_src)
            self.duration = duration * 1000
            for f in self.parent.file_src:
                escaped = f.replace(r"'", r"'\'")  # need escaping some chars
                textstr.append(f"file '{escaped}'\nduration "
                               f"{self.spin_pict.GetValue()}"
                               )
            textstr.append(f"file '{self.parent.file_src[-1]}'")
            self.args = (f'"{ftext}" -vsync vfr -pix_fmt yuv420p '
                         f'-profile:v baseline -map 0:v? -map_chapters 0 '
                         '-map 0:s? -map 0:a? -map_metadata 0'
                         )
        with open(ftext, 'w', encoding='utf8') as txt:
            txt.write('\n'.join(textstr))

        checking = check_files((fsource[0],),
                               self.parent.outpath_ffmpeg,
                               self.parent.same_destin,
                               self.parent.suffix,
                               ext
                               )
        if checking is None:  # User changing idea or not such files exist
            return

        destin = checking[1]
        newfile = f'{basename}{self.parent.suffix}.{ext}'

        self.concat_demuxer(self.parent.file_src, newfile,
                            destin[0], ext)
    # -----------------------------------------------------------

    def concat_demuxer(self, filesrc, newfile, destdir, outext):
        """
        Redirect to processing

        """
        logname = 'concatenate_demuxer.log'
        valupdate = self.update_dict(newfile, destdir, outext)
        ending = Formula(self, valupdate[0], valupdate[1], _('Starts'))
        if ending.ShowModal() == wx.ID_OK:

            self.parent.switch_to_processing('concat_demuxer',
                                             filesrc,
                                             outext,
                                             destdir,
                                             self.args,
                                             None,
                                             self.duration,  # modify
                                             None,
                                             logname,
                                             1,
                                             )
    # -----------------------------------------------------------

    def update_dict(self, newfile, destdir, ext):
        """
        Update information before send to epilogue

        """
        lenfile = len(self.parent.file_src)

        formula = (_("SUMMARY\n\nFile to concatenate\nOutput filename\
                      \nDestination\nOutput Format\nTime Period"))
        dictions = (f"\n\n{lenfile}\n{newfile}\n{destdir}\n{ext}\n"
                    f"Not applicable")
        return formula, dictions
