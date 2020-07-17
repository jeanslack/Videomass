# -*- coding: UTF-8 -*-
# Name: textdrop.py
# Porpose: Allows you to add URLs to download media
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
import os


class TextDnD(wx.Panel):
    """
    Accept one or more urls separated by a white space or newline.

    """
    get = wx.GetApp()
    OUTSAVE = get.USERfilesave  # files destination folder
    OS = get.OS
    # ----------------------------------------------------------------#

    def __init__(self, parent):
        """
        """
        self.parent = parent  # parent is the MainFrame
        dirname = os.path.expanduser('~')  # /home/user/
        self.file_dest = dirname if not TextDnD.OUTSAVE else TextDnD.OUTSAVE

        wx.Panel.__init__(self, parent=parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        infomsg = _("Add one or more URLs below")
        lbl_info = wx.StaticText(self, label=infomsg)
        sizer.Add(lbl_info, 0, wx.ALL, 5)
        self.textCtrl = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_MULTILINE |
                                    wx.TE_DONTWRAP
                                    )
        sizer.Add(self.textCtrl, 1, wx.EXPAND | wx.ALL, 5)
        optionsmsg = _("Options")
        lbl_listdel = wx.StaticText(self, label=optionsmsg)
        sizer.Add(lbl_listdel, 0, wx.ALL, 5)
        btn_clear = wx.Button(self, wx.ID_CLEAR, "")
        sizer.Add(btn_clear, 0, wx.ALL | wx.EXPAND, 10)
        outdirmsg = _("Output Directory")
        lbl_dir = wx.StaticText(self, label=outdirmsg)
        sizer.Add(lbl_dir, 0, wx.ALL, 5)
        sizer_ctrl = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer_ctrl, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_save = wx.Button(self, wx.ID_OPEN, "...", size=(-1, -1))
        sizer_ctrl.Add(self.btn_save, 0, wx.ALL |
                       wx.ALIGN_CENTER_HORIZONTAL |
                       wx.ALIGN_CENTER_VERTICAL, 5
                       )
        self.text_path_save = wx.TextCtrl(self, wx.ID_ANY, "",
                                          style=wx.TE_PROCESS_ENTER |
                                          wx.TE_READONLY
                                          )
        sizer_ctrl.Add(self.text_path_save, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)

        # properties
        if TextDnD.OS != 'Darwin':
            lbl_info.SetLabelMarkup("<b>%s</b>" % infomsg)
            lbl_listdel.SetLabelMarkup("<b>%s</b>" % optionsmsg)
            lbl_dir.SetLabelMarkup("<b>%s</b>" % outdirmsg)
        self.text_path_save.SetValue(self.file_dest)

        # Tooltip
        btn_clear.SetToolTip(_('Delete all text from the list'))
        tip = (_('Choose another output directory for files saving'))
        self.btn_save.SetToolTip(tip)

        # Binding
        self.Bind(wx.EVT_BUTTON, self.deleteAll, btn_clear)
        self.Bind(wx.EVT_TEXT, self.on_emptyText, self.textCtrl)
    # ---------------------------------------------------------

    def on_emptyText(self, event):
        """
        Text event, if empty set parent.data_url
        """
        if not self.textCtrl.GetValue().strip():
            self.parent.data_url = None
    # ----------------------------------------------------------

    def topic_Redirect(self):
        """
        Redirects data to specific panel
        """
        if not self.textCtrl.GetValue():
            return
        else:
            data = (self.textCtrl.GetValue().split())
            return data
    # -----------------------------------------------------------

    def deleteAll(self, event):
        """
        Delete and clear all text lines of the TxtCtrl

        """
        self.textCtrl.Clear()
    # -----------------------------------------------------------

    def on_file_save(self, path):
        """
        Set a specific directory for files saving

        """
        self.text_path_save.SetValue("")
        self.text_path_save.AppendText(path)
        self.file_dest = '%s' % (path)
    # ------------------------------------------------------------

    def statusbar_msg(self, mess, color):
        """
        Set a status bar message of the parent method.
        """
        self.parent.statusbar_msg('%s' % mess, color)
