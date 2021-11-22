# -*- coding: UTF-8 -*-
"""
Name: user_notes.py
Porpose: Show a simple and useful notepad with search function
Compatibility: Python3, wxPython4
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.18.2021
Code checker:
    - flake8: --ignore F821, W504, F401
    - pylint: --ignore E0602, E1101, C0415, E0401, C0103

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


def check_notes(fname):
    """
    Accepts the path string of a text file, reads it,
    and returns its contents if the text file exists
    and is not empty. Returns `None` otherwise.
    """
    nts = None
    if os.path.exists(fname) and os.path.isfile(fname):
        with open(fname, "r", encoding='utf8') as text:
            nts = text.read()
        if nts.strip() == "":
            return None
    return nts


class Memos(wx.Dialog):
    """
    Show and edit user notes / reminders with a real-time
    string search filter. The search function is case sensitive
    by default.

    """
    def __init__(self):
        """
        Modal mode

        """
        get = wx.GetApp()  # get data from bootstrap
        self.filename = os.path.join(get.appset['confdir'], 'user_memos.txt')
        curnotes = check_notes(self.filename)
        self.colorscheme = get.appset['icontheme'][1]

        wx.Dialog.__init__(self, None,
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
                           )
        self.textbox = wx.TextCtrl(self, wx.ID_ANY,
                                   "",
                                   # size=(550,400),
                                   style=wx.TE_MULTILINE
                                   | wx.TE_RICH
                                   | wx.HSCROLL
                                   )
        self.textbox.SetBackgroundColour(self.colorscheme['BACKGRD'])
        self.textbox.SetDefaultStyle(wx.TextAttr(self.colorscheme['TXT3']))

        if curnotes is None:
            self.textbox.AppendText(_("Read and write memos with "
                                      "text search function."))
        else:
            self.textbox.AppendText(curnotes)

        self.search = wx.SearchCtrl(self,
                                    wx.ID_ANY,
                                    size=(400, 30),
                                    style=wx.TE_PROCESS_ENTER,
                                    )
        self.search.SetToolTip(_("Find matching entries in the text box"))

        self.labcount = wx.StaticText(self, wx.ID_ANY, "")

        self.button_close = wx.Button(self, wx.ID_CLOSE, "")
        self.button_save = wx.Button(self, wx.ID_SAVE, "")
        self.button_save.Disable()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.textbox, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.search, 0, wx.ALL, 5)
        sizer.Add(self.labcount, 0, wx.ALL | wx.EXPAND, 5)
        grid = wx.GridSizer(1, 2, 0, 0)
        sizer.Add(grid, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=0)
        grid.Add(self.button_save, 1, wx.ALL, 5)
        grid.Add(self.button_close, 1, wx.ALL, 5)

        self.SetTitle(_("User Memos"))
        self.SetMinSize((500, 500))
        # set_properties:
        self.SetSizer(sizer)
        self.Fit()
        self.Layout()

        # EVT
        if not hasattr(wx, 'EVT_SEARCH'):
            self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN,
                      self.on_search_text, self.search)
        else:  # is wxPython >= 4.1
            self.Bind(wx.EVT_SEARCH, self.on_search_text, self.search)

        if not hasattr(wx, 'EVT_SEARCH_CANCEL'):
            self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.on_delete,
                      self.search)
        else:  # is wxPython >= 4.1
            self.Bind(wx.EVT_SEARCH_CANCEL, self.on_delete, self.search)

        self.Bind(wx.EVT_TEXT, self.on_textbox, self.textbox)
        self.Bind(wx.EVT_TEXT, self.on_search_text, self.search)
        self.Bind(wx.EVT_BUTTON, self.on_save, self.button_save)
        self.Bind(wx.EVT_BUTTON, self.on_close, self.button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)  # controlla la chiusura (x)

    # ---------------------------------------------------------#

    def on_textbox(self, event):
        """
        This method catches any event made in the wx.TxtCtrl.

        """
        if wx.version().startswith('4.0.7 '):
            self.textbox.SetStyle(0, len(self.textbox.GetValue()),
                                  wx.TextAttr(self.colorscheme['TXT3'],
                                              self.colorscheme['BACKGRD']))
        if self.button_save.IsEnabled() is False:
            self.button_save.Enable()
    # ---------------------------------------------------------#

    def on_save(self, event):
        """
        Save changes to text file.
        Writing the file is left to the `SaveFile` method of `wx.TxtCtrl`.
        Make sure it has utf8 encoding enabled, otherwise use the Python
        context manager as follows:

        with open(self.filename, "w", encoding='utf8') as text:
            text.write(self.textbox.GetValue())

        """
        if self.textbox.SaveFile(filename=self.filename) is True:
            wx.MessageBox(_("Successfully saved!"),
                          'Videomass', wx.ICON_INFORMATION, self)
            self.button_save.Disable()
            status = True
        else:
            wx.MessageBox(_("Unexpected error: Unable to save changes."),
                          'Videomass', wx.ICON_ERROR, self)
            status = False

        return status
    # --------------------------------------------------------------#

    def on_search_text(self, event):
        """
        Finds all text occurrences matching with entered
        search string. Each matching string is highlighted
        in yellow and the text should scroll to the first
        occurrence position.

        NOTE: `re.finditer` works but does not find some chars
              like 'this?' or 'like=' and give re.error with special
              chars like '?', '=' .
        count = 0
        for match in re.finditer(findtext, text):
            if match:
                count += 1
                self.textbox.SetStyle(match.start(), match.end(),
                                    wx.TextAttr("RED", "YELLOW"))

        """
        findtext = event.GetString()  # the string to find
        lengh = len(findtext)
        text = self.textbox.GetValue()  # the current text within textctrl
        self.textbox.SetStyle(0, len(text),
                              wx.TextAttr(self.colorscheme['TXT3'],
                                          self.colorscheme['BACKGRD']))

        if findtext == "":
            self.labcount.SetLabel("")
            return

        for num, line in enumerate(text.split('\n')):
            if findtext in line:
                # get long value from XYToPosition method
                tolong = self.textbox.XYToPosition(line.index(findtext), num)
                # use long value to set position with ShowPosition method
                self.textbox.ShowPosition(tolong)
                break  # find first occurrence and stop

        count = 0
        for num, match in enumerate(text):
            if text.find(findtext, num) == num:
                count += 1
                self.textbox.SetStyle(num, num + lengh,
                                      wx.TextAttr("RED", "YELLOW"))

        if count == 1:
            msg = _('Found {0} match in your search').format(str(count))
        elif count == 0:
            msg = _('No occurrences found: {0}').format(str(count))
        else:
            msg = _('Found {0} occurrences that '
                    'match your search').format(str(count))

        self.labcount.SetLabel(msg)
        # self.Layout()
    # --------------------------------------------------------------#

    def on_delete(self, event):
        """
        It does nothing, but it seems needed.
        During deletion, the "on_search_text" call is
        generated automatically
        """
        return
    # --------------------------------------------------------------#

    def on_close(self, event):
        """
        destroy dialog by Close button or by the X button on
        the title bar. If there are any changes in the text box,
        a dialog box appears with a question.

        """
        msg = _("\nThe changes have not yet been applied.\n"
                "Do you want to save your changes now?")

        if self.button_save.IsEnabled() is True:
            curnotes = check_notes(self.filename)
            if curnotes != self.textbox.GetValue():
                resp = wx.MessageBox(msg, _("Videomass - Save Changes"),
                                     wx.ICON_WARNING | wx.YES_NO | wx.CANCEL,
                                     self)
                if resp == wx.YES:
                    ret = self.on_save(self)
                    if ret is False:
                        return

                elif resp == wx.CANCEL:
                    return

            self.Destroy()

        else:
            self.Destroy()
        # event.Skip()
