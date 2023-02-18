# -*- coding: UTF-8 -*-
"""
Name: ffmpeg_help.py
Porpose: Show a window to search for FFmpeg help topics
Compatibility: Python3, wxPython4
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.16.2023
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
import re
import wx
from pubsub import pub
from videomass.vdms_io import io_tools


class FFmpegHelp(wx.Dialog):
    """
    Search and view all the FFmpeg help options.
    It has a real-time string search filter and is
    case-sensitive by default, but it is possible to
    ignore upper and lower case by activating the
    corresponding checkbox.

    """
    HELPTOPIC = (_('Contextual help based on the topic entered in the\n'
                   'additional text field. Below is a list of valid\n'
                   'topics as examples:'
                   ))
    TOPICEXAMPLES = ('\n\n\tencoder=libvpx-vp9\n\tencoder=libvorbis'
                     '\n\tencoder=libopus\n\tencoder=mpeg2video'
                     '\n\tencoder=libx264\n\tdecoder=dirac'
                     '\n\tdecoder=gif\n\tdecoder=libvpx-vp9'
                     '\n\tmuxer=matroska\n\tdemuxer=matroska\n\t...etc'
                     )
    ARGS_OPT = {"...": 'None',
                _("Help topic"): ['--help', ''],
                _("print basic options"): ['-h', ''],
                _("print more options"): ['-h', 'long'],
                _("print all options (very long)"): ['-h', 'full'],
                _("show available devices"): ['-devices'],
                _("show available bit stream filters"): ['-bsfs'],
                _("show available protocols"): ['-protocols'],
                _("show available filters"): ['-filters'],
                _("show available pixel formats"): ['-pix_fmts'],
                _("show available audio sample formats"): ['-sample_fmts'],
                _("show available color names"): ['-colors'],
                _("list sources of the input device"): ['-sources'],
                _("list sinks of the output device"): ['-sinks'],
                _("show available HW acceleration methods"): ['-hwaccels'],
                _("show license"): ['-L'],
                }
    CHOICES = tuple(ARGS_OPT.keys())

    def __init__(self, OS):
        """
        The list of topics in the combo box is part of the
        section given by the -h option on the FFmpeg command line.

        Mode:
            with 'None' not depend from parent:
            wx.Frame.__init__(self, None)

            With parent, -1:
            wx.Frame.__init__(self, parent, -1)
            if close videomass also close parent window

        """
        self.row = None  # output text from `io_tools.findtopic(topic)'
        get = wx.GetApp()  # get data from bootstrap
        colorscheme = get.appset['icontheme'][1]
        vidicon = get.iconset['videomass']

        wx.Dialog.__init__(self, None,
                           style=wx.DEFAULT_DIALOG_STYLE
                           | wx.RESIZE_BORDER
                           | wx.DIALOG_NO_PARENT
                           )
        # add panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        #self.panel = wx.Panel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL
                              #| wx.BORDER_THEME,
                              #)
        self.textlist = wx.TextCtrl(self, wx.ID_ANY,
                                    "",
                                    # size=(550,400),
                                    style=wx.TE_READONLY
                                    | wx.TE_MULTILINE
                                    | wx.TE_RICH2
                                    | wx.HSCROLL,
                                    )
        self.textlist.SetBackgroundColour(colorscheme['BACKGRD'])
        self.textlist.SetDefaultStyle(wx.TextAttr(colorscheme['TXT3']))
        if OS == 'Darwin':
            self.textlist.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
        else:
            self.textlist.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))

        self.textlist.AppendText(_("Choose a topic in the list"))
        sizer.Add(self.textlist, 1, wx.EXPAND | wx.ALL, 5)
        self.cmbx_choice = wx.ComboBox(self, wx.ID_ANY,
                                       choices=FFmpegHelp.CHOICES,
                                       style=wx.CB_DROPDOWN
                                       | wx.CB_READONLY,
                                       )
        self.cmbx_choice.SetSelection(0)
        self.cmbx_choice.SetToolTip(_("help topic list"))

        sizerselect = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizerselect, 0)
        sizerselect.Add(self.cmbx_choice, 0, wx.ALL, 5)
        self.text_topic = wx.TextCtrl(self, wx.ID_ANY,
                                      "", size=(160, -1),
                                      )
        sizerselect.Add(self.text_topic, 0, wx.ALL, 5)
        self.text_topic.Disable()
        self.text_topic.SetToolTip(_("Type the topic here"))
        self.btn_proc = wx.Button(self, wx.ID_ANY, _("Confirm Topic"))
        self.btn_proc.Disable()
        sizerselect.Add(self.btn_proc, 0, wx.ALL, 5)
        boxsearch = wx.BoxSizer(wx.HORIZONTAL)
        self.search = wx.SearchCtrl(self,
                                    wx.ID_ANY,
                                    size=(400, 30),
                                    style=wx.TE_PROCESS_ENTER,
                                    )
        self.search.SetToolTip(_("The search function allows you to find "
                                 "entries in the current topic"))
        boxsearch.Add(self.search, 0, wx.ALL, 0)
        self.case = wx.CheckBox(self, wx.ID_ANY, (_("Ignore case")))
        self.case.SetToolTip(_("Ignore case distinctions: characters with "
                               "different case will match."
                               ))
        boxsearch.Add(self.case, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(boxsearch, 0, wx.ALL, 5)
        # bottom layout
        grid = wx.GridSizer(1, 1, 0, 0)
        self.btn_close = wx.Button(self, wx.ID_CLOSE, "")
        grid.Add(self.btn_close, 1, wx.ALL, 5)
        sizer.Add(grid, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=0)
        self.SetTitle(_("FFmpeg help topics"))
        self.SetMinSize((750, 500))
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(vidicon, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        # set_properties:
        # self.panel.SetSizer(sizer)
        self.SetSizer(sizer)
        self.Fit()
        self.Layout()
        # --------------- EVT
        if not hasattr(wx, 'EVT_SEARCH'):
            self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN,
                      self.on_type_text, self.search)
        else:  # is wxPython >= 4.1
            self.Bind(wx.EVT_SEARCH, self.on_type_text, self.search)

        if not hasattr(wx, 'EVT_SEARCH_CANCEL'):
            self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.on_delete,
                      self.search)
        else:  # is wxPython >= 4.1
            self.Bind(wx.EVT_SEARCH_CANCEL, self.on_delete, self.search)

        self.Bind(wx.EVT_COMBOBOX, self.on_selected, self.cmbx_choice)
        self.Bind(wx.EVT_BUTTON, self.on_btn_proc, self.btn_proc)
        self.Bind(wx.EVT_TEXT, self.on_type_text, self.search)
        self.Bind(wx.EVT_TEXT, self.on_type_topic, self.text_topic)
        self.Bind(wx.EVT_CHECKBOX, self.on_ckbx, self.case)
        self.Bind(wx.EVT_BUTTON, self.on_close, self.btn_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)  # caption X
    # ---------------------------------------------------------#

    def on_type_topic(self, event):
        """
        Event on typing some text
        """
        text = self.text_topic.GetValue().strip()
        if not text:
            self.btn_proc.Disable()
            FFmpegHelp.ARGS_OPT[_("Help topic")] = ['--help', '']
        else:
            self.btn_proc.Enable()
    # --------------------------------------------------------------#

    def on_btn_proc(self, event):
        """
        Event when user press `btn_proc`.
        """
        self.search.Clear()
        newarg = self.text_topic.GetValue().split()
        topic = ['--help', ] + newarg
        FFmpegHelp.ARGS_OPT[_("Help topic")] = topic
        self.row = io_tools.findtopic(topic)
        if self.row:
            self.textlist.SetValue(self.row)
        else:
            self.textlist.SetValue(_("\n  ..Nothing available"))
    # --------------------------------------------------------------#

    def on_selected(self, event):
        """
        Event selecting topic in the `cmbx_choice`
        """
        topic = FFmpegHelp.ARGS_OPT[self.cmbx_choice.GetValue()]
        self.search.Clear()

        if topic[0] == "--help":  # from _(Help topic) only
            self.text_topic.Enable()
            if not self.text_topic.GetValue().strip():
                self.textlist.SetValue(FFmpegHelp.HELPTOPIC)
                self.textlist.AppendText(FFmpegHelp.TOPICEXAMPLES)
            else:
                self.on_btn_proc(self)
            return

        self.text_topic.Disable()
        self.btn_proc.Disable()

        if "None" in topic:
            self.row = None
            self.textlist.SetValue(_("First, choose a topic in the "
                                     "drop down list"))
        else:
            self.row = io_tools.findtopic(topic)
            if self.row:
                self.textlist.SetValue(self.row)
            else:
                self.textlist.SetValue(_("\n  ..Nothing available"))
    # --------------------------------------------------------------#

    def on_type_text(self, event, by_event=False):
        """
        Whenever text is entered it search the string typed
        on the search control and find on the current `self.row`
        output. The result is very similar to what grep does on
        the Unix like shell, i.e:
            `ffmpeg -*some option* | grep somestring`

        or if checkbox is True:

            `ffmpeg -*some option* | grep -i somestring`
        """
        if by_event:  # see `on_ckbx`
            is_string = self.search.GetValue()
        else:  # in all other cases
            is_string = event.GetString()

        if self.row and not is_string:
            self.textlist.SetValue(f'{self.row}')
            return

        if self.row and is_string:  # specified search (like grep does)
            find = []
            if self.case.GetValue():  # case insensitive: Hello/hello

                for lines in self.row.split('\n'):
                    if re.search(is_string, lines, re.IGNORECASE):
                        find.append(f"{lines}\n")
            else:  # is case sensitive
                for lines in self.row.split('\n'):  # case sensitive
                    if is_string in lines:
                        find.append(f"{lines}\n")
            if not find:
                self.textlist.SetValue(_('\n  ...Not found'))
            else:
                self.textlist.SetValue(' '.join(find))
        return
    # --------------------------------------------------------------#

    def on_ckbx(self, event):
        """
        This event updates the quick search with
        or without case sensitivity
        """
        self.on_type_text(self, True)
    # --------------------------------------------------------------#

    def on_delete(self, event):
        """
        It does nothing, but it seems needed.
        During deletion, the "on_type_text" call
        is generated automatically.
        """
        return
    # --------------------------------------------------------------#

    def on_close(self, event):
        """
        Destroy this window
        """
        pub.sendMessage("Destroying_window", msg='HelpTopic')
