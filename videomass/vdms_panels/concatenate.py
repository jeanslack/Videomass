# -*- coding: UTF-8 -*-
"""
Name: concatenate.py
Porpose: A simple concat demuxer UI
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Sep.29.2021
Code checker:
    - pycodestyle
    - flake8: --ignore F821
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
    A simple concat demuxer UI to set media files concatenation using
    concat demuxer, see <https://ffmpeg.org/ffmpeg-formats.html#concat>

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
        self.Command attribute is an empty string when radiobox is
        set to 0 - 1 Selections, otherwise a '-vn' parameter is
        added.
        .
        """
        get = wx.GetApp()
        appdata = get.appset
        self.parent = parent  # parent is the MainFrame
        self.command = ''

        wx.Panel.__init__(self, parent=parent, style=wx.BORDER_THEME)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((50, 50))
        line0 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        sizer.Add(line0, 0, wx.ALL | wx.EXPAND, 5)
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
        link2 = hpl.HyperLinkCtrl(self, -1, _("1.4 Concatenate media files "
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
        sizFormat = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizFormat)

        self.SetSizer(sizer)

        if appdata['ostype'] == 'Darwin':
            self.lbl_msg1.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.lbl_msg2.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            self.lbl_msg3.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            self.lbl_msg1.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.lbl_msg2.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            self.lbl_msg3.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
    # ---------------------------------------------------------

    def on_start(self):
        """
        Parameters definition

        """
        logname = 'concatenate_demuxer.log'
        fsource = self.parent.file_src
        fname = os.path.splitext(os.path.basename(fsource[0]))[0]

        if len(fsource) < 2:
            wx.MessageBox(_('At least two files are required to perform '
                            'concatenation.'), _('ERROR'),
                          wx.ICON_ERROR, self
                          )
            return

        ext = os.path.splitext(self.parent.file_src[0])[1].split('.')[1]
        diff = compare_media_param(self.parent.data_files)

        if diff is True:
            wx.MessageBox(_('The files do not have the same "codec_types", '
                            'same "sample_rate" or same "width" or "height". '
                            'Unable to proceed.'),
                          _('ERROR'), wx.ICON_ERROR, self
                          )
            return

        checking = check_files((fsource[0],),
                               self.parent.outpath_ffmpeg,
                               self.parent.same_destin,
                               self.parent.suffix,
                               ext
                               )
        if not checking[0]:  # User changing idea or not such files exist
            return

        f_src, destin, countmax = checking
        newfile = f'{fname}{self.parent.suffix}.{ext}'

        self.concat_demuxer(self.parent.file_src, newfile,
                            destin[0], ext, logname)
    # -----------------------------------------------------------

    def concat_demuxer(self, filesrc, newfile, destdir, outext, logname):
        """
        Parameters redirection

        """
        valupdate = self.update_dict(newfile, destdir, outext)
        ending = Formula(self, valupdate[0], valupdate[1], _('Starts'))
        if ending.ShowModal() == wx.ID_OK:

            self.parent.switch_to_processing('concat_demuxer',
                                             filesrc,
                                             outext,
                                             destdir,
                                             self.command,
                                             None,
                                             '',
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
