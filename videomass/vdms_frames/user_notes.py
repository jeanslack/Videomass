# -*- coding: UTF-8 -*-
"""
Name: user_notes.py
Porpose: Show a simple and useful notepad with search function
Compatibility: Python3, wxPython4
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.17.2021
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
import re
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


class Memos(wx.MiniFrame):
    """
    Show and edit user notes / reminders with a real-time
    string search filter. The search function is case sensitive
    by default.

    """
    def __init__(self):
        """
        Mode:
           with 'None' it does not depend on the parent:
            wx.Frame.__init__(self, None)

            With parent, -1:
            wx.Frame.__init__(self, parent, -1)
            if close videomass also close parent window

        """
        get = wx.GetApp()  # get data from bootstrap
        self.filename = os.path.join(get.appset['confdir'], 'user_memos.txt')
        curnotes = check_notes(self.filename)
        self.colorscheme = get.appset['icontheme'][1]

        wx.MiniFrame.__init__(self,
                              None,
                              style=wx.RESIZE_BORDER
                              | wx.CAPTION
                              | wx.CLOSE_BOX
                              | wx.SYSTEM_MENU
                              )
        # add panel
        self.panel = wx.Panel(self,
                              wx.ID_ANY,
                              style=wx.TAB_TRAVERSAL
                              | wx.BORDER_THEME)
        self.textbox = wx.TextCtrl(self.panel, wx.ID_ANY,
                                   "",
                                   # size=(550,400),
                                   style=wx.TE_MULTILINE
                                   | wx.TE_RICH2
                                   | wx.HSCROLL
                                   )
        self.textbox.SetBackgroundColour(self.colorscheme['BACKGRD'])
        self.textbox.SetDefaultStyle(wx.TextAttr(self.colorscheme['TXT3']))
        if get.appset['ostype'] == 'Darwin':
            self.textbox.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
        else:
            self.textbox.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))

        if curnotes is None:
            self.textbox.AppendText(_("Read and write memos with "
                                      "text search function."))
        else:
            self.textbox.AppendText(curnotes)

        self.search = wx.SearchCtrl(self.panel,
                                    wx.ID_ANY,
                                    size=(400, 30),
                                    style=wx.TE_PROCESS_ENTER,
                                    )
        self.search.SetToolTip(_("Find matching entries in the text box"))
        self.button_close = wx.Button(self.panel, wx.ID_CLOSE, "")
        self.button_save = wx.Button(self.panel, wx.ID_SAVE, "")
        self.button_save.Disable()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.textbox, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.search, 0, wx.ALL, 5)
        grid = wx.GridSizer(1, 2, 0, 0)
        sizer.Add(grid, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=0)
        grid.Add(self.button_save, 1, wx.ALL, 5)
        grid.Add(self.button_close, 1, wx.ALL, 5)

        self.SetTitle(_("User Memos"))
        self.SetMinSize((500, 500))
        # set_properties:
        self.panel.SetSizer(sizer)
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

        """
        findtext = event.GetString()  # the string to find
        text = self.textbox.GetValue()  # the current text within textctrl
        self.textbox.SetStyle(0, len(text),
                              wx.TextAttr(self.colorscheme['TXT3'],
                                          self.colorscheme['BACKGRD'])
                              )
        for num, line in enumerate(text.split('\n')):
            if findtext in line:
                tolong = self.textbox.XYToPosition(line.index(findtext), num)
                self.textbox.ShowPosition(tolong)
                break

        for match in re.finditer(findtext, text):
            self.textbox.SetStyle(match.start(), match.end(),
                                  wx.TextAttr("RED", "YELLOW"))
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
        if self.button_save.IsEnabled() is True:
            curnotes = check_notes(self.filename)
            if curnotes != self.textbox.GetValue():
                if wx.MessageBox(_("\nThe changes have not yet been applied.\n"
                                   "Do you want to save your changes now?"),
                                 _("Videomass - Save Changes"),
                                 wx.ICON_WARNING | wx.YES_NO | wx.CANCEL,
                                 self) == wx.YES:

                    ret = self.on_save(self)
                    if ret is False:
                        return
            self.Destroy()

        else:
            self.Destroy()
        # event.Skip()
