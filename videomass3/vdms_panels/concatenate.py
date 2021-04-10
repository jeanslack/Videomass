# -*- coding: UTF-8 -*-
# Name: concatenate.py
# Porpose: join media files interface
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Apr.09.2021 *PEP8 compatible*
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
import os
from videomass3.vdms_dialogs.epilogue import Formula


class Conc_Demuxer(wx.Panel):
    """
    A simple panel to set media files concatenation

    """
    get = wx.GetApp()
    OS = get.OS

    MSG_1 = _("NOTE:\n\n- The order of concatenation depends on the order in "
              "which the files were added.\n\n- The output file name will have "
              "the same name as the first file added (also depends\n  on the "
              "settings made in the preferences dialog).")

    CONCVID = _("Make sure the files imported are all Video files and have "
                "exactly the same streams,\nsame codecs and same dimensions, "
                "but can be wrapped in different container formats.")
    CONCAUDIO = _("Make sure the files imported are all audio files and have "
                  "the same formats and codecs.")

    formats_vid = ('avi', 'flv', 'mp4', 'm4v', 'mkv', 'webm', 'ogv')
    formats_aud = ('wav', 'mp3', 'ac3', 'ogg', 'flac', 'm4a', 'aac', 'opus')
    # ----------------------------------------------------------------#

    def __init__(self, parent):
        """
        """
        self.parent = parent  # parent is the MainFrame
        self.command = ''

        wx.Panel.__init__(self, parent=parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((50, 50))
        self.lbl_msg1 = wx.StaticText(self, wx.ID_ANY,
                                      label=Conc_Demuxer.MSG_1
                                      )
        sizer.Add(self.lbl_msg1, 0, wx.ALL | wx.EXPAND, 5)
        tbchoice = [_('Audio files (tracks)'),
                    _('Video files'),
                    _('Only Audio streams from Videos'),]
        self.rdbOpt = wx.RadioBox(self, wx.ID_ANY,
                                  (_("Which files do you want to "
                                     "concatenate?")),
                                  choices=tbchoice,
                                  majorDimension=0,
                                  style=wx.RA_SPECIFY_COLS
                                  )
        self.rdbOpt.SetSelection(1)
        sizer.Add((20, 20))
        sizer.Add(self.rdbOpt, 0, wx.ALL, 5)
        sizer.Add((20, 20))
        self.lbl_info = wx.StaticText(self, wx.ID_ANY,
                                      label=Conc_Demuxer.CONCVID
                                      )
        sizer.Add(self.lbl_info, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add((20, 20))
        sizFormat = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizFormat)
        self.lbl_f = wx.StaticText(self, wx.ID_ANY, label=_('Output format:'))
        sizFormat.Add(self.lbl_f, 0, wx.LEFT | wx.CENTER, 5)
        self.cmb_format = wx.ComboBox(self, wx.ID_ANY,
                                      choices=Conc_Demuxer.formats_vid,
                                      size=(200, -1), style=wx.CB_DROPDOWN |
                                      wx.CB_READONLY
                                      )
        self.cmb_format.SetSelection(4)
        sizFormat.Add(self.cmb_format, 0, wx.ALL, 2)

        self.SetSizer(sizer)

        if Conc_Demuxer.OS == 'Darwin':
            self.lbl_info.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            self.lbl_msg1.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        else:
            self.lbl_info.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            self.lbl_msg1.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.lbl_msg1.SetForegroundColour((3, 152, 252, 255))

        # Binding
        self.Bind(wx.EVT_RADIOBOX, self.on_Radio, self.rdbOpt)
    # ---------------------------------------------------------

    def on_Radio(self, event):
        """
        Radio box event.

        """
        if self.rdbOpt.GetSelection() == 0:
            self.cmb_format.Clear()
            self.cmb_format.Append(Conc_Demuxer.formats_aud)
            self.cmb_format.SetSelection(1)
            self.lbl_info.SetLabel(Conc_Demuxer.CONCAUDIO)
            self.command = ''

        elif self.rdbOpt.GetSelection() == 1:
            self.cmb_format.Clear()
            self.cmb_format.Append(Conc_Demuxer.formats_vid)
            self.cmb_format.SetSelection(4)
            self.lbl_info.SetLabel(Conc_Demuxer.CONCVID)
            self.command = ''

        elif self.rdbOpt.GetSelection() == 2:
            self.cmb_format.Clear()
            self.cmb_format.Append(Conc_Demuxer.formats_aud)
            self.cmb_format.SetSelection(1)
            self.lbl_info.SetLabel(Conc_Demuxer.CONCVID)
            self.command = '-vn'
        # self.Layout()
    # ----------------------------------------------------------

    def on_start(self):
        """
        Parameters definition

        """
        logname = 'concatenate_demuxer.log'
        ext = self.cmb_format.GetValue()
        fsource = self.parent.file_src
        fname = os.path.splitext(os.path.basename(fsource[0]))[0]

        if len(fsource) < 2:
            wx.MessageBox(_('At least two files are required to perform '
                          'concatenation.'), _('ERROR'), wx.ICON_ERROR)
            return

        existing = False

        if self.parent.same_destin:
            newfile = '%s%s.%s' % (fname, self.parent.suffix, ext)
            dirname = os.path.dirname(fsource[0])
            for f in os.listdir(dirname):
                if f == '%s%s.%s' % (fname, self.parent.suffix, ext):
                    existing = True
                    break
        else:
            newfile = '%s.%s' % (fname, ext)
            dirname = self.parent.outpath_ffmpeg
            for f in os.listdir(dirname):
                if f == '%s.%s' % (fname, ext):
                    existing = True
                    break

        if existing:
            if wx.MessageBox(_('Already exist: \n\n%s\n\n'
                               'Do you want to overwrite? ')
                             % os.path.join(dirname, newfile),
                             _('Please Confirm'),
                             wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return

        self.concat_demuxer(self.parent.file_src, newfile,
                            dirname, ext, logname)
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
        dictions = ("\n\n%s\n%s\n%s\n%s\n%s" % (lenfile, newfile, destdir,
                                                ext, 'Not applicable',))
        return formula, dictions
