# -*- coding: UTF-8 -*-
"""
Name: subtitle_editor.py
Porpose: shows a dialog box to setting preferred subtitles
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: July.06.2023
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
import wx


class SubtitleEditor(wx.Dialog):
    """
    Shows a dialog box for setting preferred subtitles.
    See ``youtubedl_ui.py`` -> ``on_subtitles_editor`` method
    for how to use this class.

    """
    get = wx.GetApp()  # get data from bootstrap
    OS = get.appset['ostype']
    appdata = get.appset
    appicon = get.iconset['videomass']
    SUBS_LANG = {"en": _("English"),
                 "fr": _("French"),
                 "de": _("German"),
                 "el": _("Greek"),
                 "he": _("Hebrew"),
                 "it": _("Italian"),
                 "pl": _("Polish"),
                 "pt": _("Portuguese"),
                 "ru": _("Russian"),
                 "es": _("Spanish"),
                 "sv": _("Swedish"),
                 "tr": _("Turkish"),
                 "sq": _("Albanian"),
                 "zh": _("Chinese"),
                 }

    def __init__(self, parent, data):
        """
        NOTE Use 'parent, -1' param. to make parent, use 'None' otherwise

        """
        self.data = data

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)

        # ------ Add widget controls
        sizbase = wx.BoxSizer(wx.VERTICAL)
        labtstr1 = _('Language')
        lab = wx.StaticText(self, label=labtstr1)
        sizbase.Add(lab, 0, wx.LEFT, 5)
        lab.SetLabelMarkup(f"<b>{labtstr1}</b>")
        choicelang = (_("None"),
                      _("All available subtitles"),
                      _("Default language selection"),
                      _('By manual entry'),
                      )
        self.cmbx_langs = wx.ComboBox(self, wx.ID_ANY,
                                      choices=choicelang,
                                      size=(-1, -1),
                                      style=wx.CB_DROPDOWN
                                      | wx.CB_READONLY,
                                      )
        sizbase.Add(self.cmbx_langs, 0, wx.ALL | wx.EXPAND, 5)
        choice = list(SubtitleEditor.SUBS_LANG.values())
        self.listblang = wx.ListBox(self, wx.ID_ANY,
                                    choices=choice,
                                    style=0,
                                    name='ListBox',
                                    )
        sizbase.Add(self.listblang, 1, wx.ALL | wx.EXPAND, 5)
        sizbase.Add(10, 10)
        labtstr2 = _('Preferred languages')
        self.lab1 = wx.StaticText(self, label=labtstr2)
        sizbase.Add(self.lab1, 0, wx.LEFT, 5)
        self.lab1.SetLabelMarkup(f"<b>{labtstr2}</b>")

        self.addlangs = wx.TextCtrl(self,
                                    wx.ID_ANY,
                                    value=("Write here one or more language "
                                           "codes, example: ru, fr, ar"),
                                    size=(-1, -1),
                                    name="custom_subs",
                                    )
        sizbase.Add(self.addlangs, 0, wx.ALL | wx.EXPAND, 5)
        sizbase.Add(10, 10)
        labtstr3 = _('Options')
        self.lab3 = wx.StaticText(self, label=labtstr3)
        sizbase.Add(self.lab3, 0, wx.LEFT, 5)
        self.lab3.SetLabelMarkup(f"<b>{labtstr3}</b>")
        txt = _('Include automatically generated subtitle (YouTube only)')
        self.ckbx_autogen = wx.CheckBox(self, wx.ID_ANY, txt)
        sizbase.Add(self.ckbx_autogen, 0, wx.ALL, 5)
        txt = _('Embed subtitles into video file (mp4 only)')
        self.ckbx_embed = wx.CheckBox(self, wx.ID_ANY, txt)
        sizbase.Add(self.ckbx_embed, 0, wx.ALL, 5)
        txt = _('Download subtitles only (do not include audio and video)')
        self.ckbx_skip_dl = wx.CheckBox(self, wx.ID_ANY, txt)
        sizbase.Add(self.ckbx_skip_dl, 0, wx.ALL, 5)

        # ------ bottom layout buttons
        btnconf = wx.BoxSizer(wx.HORIZONTAL)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        btnconf.Add(btn_close, 0, wx.ALL, 5)
        self.btn_ok = wx.Button(self, wx.ID_OK, _("Apply"))
        btnconf.Add(self.btn_ok, 0, wx.ALL, 5)
        sizbase.Add(btnconf, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=0)

        # ------ Properties
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(SubtitleEditor.appicon,
                                      wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetTitle(_('Subtitles Editor'))
        self.SetMinSize((600, 400))
        tip = _('Languages code of the subtitles to download separated by '
                'commas, e.g. "en, ja, ar" for English, Japanese and Arabic '
                'respectively. You can use regex e.g. "en.*, ja, ar.*". '
                'You can prefix the language code with a "-" to exclude it '
                'from the requested languages, e.g. "all, -live_chat".')
        self.addlangs.SetToolTip(tip)
        self.SetSizer(sizbase)
        sizbase.Fit(self)
        self.Layout()

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_COMBOBOX, self.on_langs, self.cmbx_langs)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)

        if not self.data["writesubtitles"]:
            self.default_setting()
        else:
            self.ckbx_autogen.SetValue(self.data["writeautomaticsub"])
            self.ckbx_embed.SetValue(self.data["embedsubtitle"])
            self.ckbx_skip_dl.SetValue(self.data["skip_download"])
            deflang = ''.join(self.data["subtitleslangs"])

            if deflang == 'all':
                self.cmbx_langs.SetSelection(1)

            elif deflang in SubtitleEditor.SUBS_LANG:
                self.cmbx_langs.SetSelection(2)
                idx = list(SubtitleEditor.SUBS_LANG.keys()).index(deflang)
                self.listblang.SetSelection(idx)

            else:
                self.cmbx_langs.SetSelection(3)
                self.addlangs.SetValue(', '.join(self.data["subtitleslangs"]))

            self.on_langs(None)
    # ------------------------------------------------------------------#

    def default_setting(self):
        """
        Reset all settings to default (disable)
        """
        self.cmbx_langs.SetSelection(0)
        self.listblang.SetSelection(0)
        self.listblang.Disable()
        self.lab1.Disable()
        self.addlangs.Clear()
        self.listblang.Disable()
        self.lab3.Disable()
        self.ckbx_autogen.SetValue(False)
        self.ckbx_embed.SetValue(False)
        self.ckbx_skip_dl.SetValue(False)
        self.ckbx_autogen.Disable()
        self.ckbx_embed.Disable()
        self.ckbx_skip_dl.Disable()
    # ------------------------------------------------------------------#

    def getvalue(self):
        """
        This method return values via the interface getvalue()
        by the caller. See the caller for more info and usage.
        """
        if self.cmbx_langs.GetSelection() == 0:
            writesubtitles = False
            subtitleslangs = []
            writeautomaticsub = False
            embedsubtitle = False
            skip_download = False

        elif self.cmbx_langs.GetSelection() == 1:
            writesubtitles = True
            subtitleslangs = ['all',]
            writeautomaticsub = self.ckbx_autogen.GetValue()
            embedsubtitle = self.ckbx_embed.GetValue()
            skip_download = self.ckbx_skip_dl.GetValue()

        elif self.cmbx_langs.GetSelection() == 2:
            writesubtitles = True
            idx = self.listblang.GetSelection()
            lang = self.listblang.GetString(idx)
            langcode = [key for key, val in SubtitleEditor.SUBS_LANG.items()
                        if val == lang]
            subtitleslangs = langcode
            writeautomaticsub = self.ckbx_autogen.GetValue()
            embedsubtitle = self.ckbx_embed.GetValue()
            skip_download = self.ckbx_skip_dl.GetValue()

        elif self.cmbx_langs.GetSelection() == 3:
            writesubtitles = True
            txt = self.addlangs.GetValue()
            subtitleslangs = ''.join(txt.split()).split(',')
            writeautomaticsub = self.ckbx_autogen.GetValue()
            embedsubtitle = self.ckbx_embed.GetValue()
            skip_download = self.ckbx_skip_dl.GetValue()

        return {'writesubtitles': writesubtitles,
                'subtitleslangs': subtitleslangs,
                'writeautomaticsub': writeautomaticsub,
                'embedsubtitle': embedsubtitle,
                'skip_download': skip_download
                }
    # ----------------------Event handler (callback)----------------------#

    def on_langs(self, event):
        """
        ComboBox event
        """
        if self.cmbx_langs.GetSelection() == 0:
            self.default_setting()

        elif self.cmbx_langs.GetSelection() == 1:
            self.listblang.Disable()
            self.lab1.Disable()
            self.addlangs.Disable()
            self.lab3.Enable()
            self.ckbx_autogen.Enable()
            self.ckbx_embed.Enable()
            self.ckbx_skip_dl.Enable()

        elif self.cmbx_langs.GetSelection() == 2:
            self.listblang.Enable()
            self.lab1.Disable()
            self.addlangs.Disable()
            self.lab3.Enable()
            self.ckbx_autogen.Enable()
            self.ckbx_embed.Enable()
            self.ckbx_skip_dl.Enable()

        elif self.cmbx_langs.GetSelection() == 3:
            self.listblang.Disable()
            self.lab1.Enable()
            self.addlangs.Enable()
            self.lab3.Enable()
            self.ckbx_autogen.Enable()
            self.ckbx_embed.Enable()
            self.ckbx_skip_dl.Enable()
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
