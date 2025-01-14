# -*- coding: UTF-8 -*-
"""
Name: ffmpeg_help.py
Porpose: Show a window to search for FFmpeg help topics
Compatibility: Python3, wxPython4
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.14.2023
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
from videomass.vdms_dialogs.widget_utils import NormalTransientPopup
from videomass.vdms_io import io_tools


class FFmpegHelp(wx.Dialog):
    """
    Search and view all the FFmpeg help options.
    It has a real-time string search filter and is
    case-sensitive by default, but it is possible to
    ignore upper and lower case by activating the
    corresponding checkbox.

    """
    LGREEN = '#52ee7d'
    BLACK = '#1f1f1f'
    HELPTOPIC = (_('Contextual help based on the argument entered in the '
                   'additional text field.\nEach argument consists of the '
                   'type and a type-specific name.\n\n'
                   'For the list of encoders click the "Encoders" button.\n'
                   'For the list of decoders click on the "Decoders" button.\n'
                   'For the muxers and demuxers click on the "Muxers and '
                   'Demuxers" button.\nFor the filters, select "Show '
                   'available filters" in the drop down menu.\n'
                   'For the bsf, select "Show available bitstream '
                   'filters" in the drop down menu.\nFor the protocols, '
                   'select "Show available protocols" in the drop down '
                   'menu.\n\n'
                   'Some examples:'
                   ))
    EXAMPLES = ('\n\n\tencoder = libvpx-vp9'
                '\n\tdecoder = libaom-av1'
                '\n\tmuxer = matroska'
                '\n\tdemuxer = matroska'
                '\n\tfilter = scale'
                '\n\tbsf = av1_frame_merge'
                '\n\tprotocol = bluray'
                )
    ARGS_OPT = {_("Help topic"): ['--help', ''],
                _("List basic options"): ['-h', ''],
                _("List more options"): ['-h', 'long'],
                _("List all options (very long)"): ['-h', 'full'],
                _("Show available devices"): ['-devices'],
                _("Show available bit stream filters"): ['-bsfs'],
                _("Show available protocols"): ['-protocols'],
                _("Show available filters"): ['-filters'],
                _("Show available pixel formats"): ['-pix_fmts'],
                _("Show available audio sample formats"): ['-sample_fmts'],
                _("Show available color names"): ['-colors'],
                _("List sources of the input device"): ['-sources'],
                _("List sinks of the output device"): ['-sinks'],
                _("Show available HW acceleration methods"): ['-hwaccels'],
                _("Show license"): ['-L'],
                }
    MAIN_CHOICES = tuple(ARGS_OPT.keys())
    ARGS = ('encoder', 'decoder', 'muxer', 'demuxer',
            'filter', 'bsf', 'protocol')

    def __init__(self, parent, OS):
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
        self.parent = parent
        self.row = None  # output text from `io_tools.findtopic(topic)'
        get = wx.GetApp()  # get data from bootstrap
        colorscheme = get.appset['colorscheme']
        vidicon = get.iconset['videomass']

        wx.Dialog.__init__(self, None,
                           style=wx.DEFAULT_DIALOG_STYLE
                           | wx.RESIZE_BORDER
                           | wx.DIALOG_NO_PARENT
                           )
        sizer = wx.BoxSizer(wx.VERTICAL)
        boxshow = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(boxshow, 0, wx.ALL, 5)

        btn_readme = wx.Button(self, wx.ID_ANY, _("Read me"), size=(-1, -1))
        btn_readme.SetBackgroundColour(wx.Colour(FFmpegHelp.LGREEN))
        btn_readme.SetForegroundColour(wx.Colour(FFmpegHelp.BLACK))
        boxshow.Add(btn_readme, 0,)

        btn_conf = wx.Button(self, wx.ID_ANY,
                             label=_("Show configuration"),
                             name='configuration',
                             )
        btn_encoders = wx.Button(self, wx.ID_ANY,
                                 label=_("Encoders"),
                                 name='encoders',
                                 )
        btn_decoders = wx.Button(self, wx.ID_ANY,
                                 label=_("Decoders"),
                                 name='decoders',
                                 )
        btn_formats = wx.Button(self, wx.ID_ANY,
                                label=_("Muxers and Demuxers"),
                                name='formats',
                                )
        for button in (btn_conf, btn_encoders, btn_decoders, btn_formats):
            button.Bind(wx.EVT_BUTTON, self.on_show_extra)
            boxshow.Add(button, 0, wx.LEFT, 5)
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
        self.textlist.AppendText(FFmpegHelp.HELPTOPIC)
        self.textlist.AppendText(FFmpegHelp.EXAMPLES)
        self.textlist.SetInsertionPoint(0)
        sizer.Add(self.textlist, 1, wx.EXPAND | wx.ALL, 5)
        self.cmbx_main = wx.ComboBox(self, wx.ID_ANY,
                                     choices=FFmpegHelp.MAIN_CHOICES,
                                     style=wx.CB_DROPDOWN
                                     | wx.CB_READONLY,
                                     )
        self.cmbx_main.SetSelection(0)
        self.cmbx_main.SetToolTip(_("help topic list"))

        sizerselect = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizerselect, 0)
        sizerselect.Add(self.cmbx_main, 0, wx.ALL, 5)
        self.cmbx_arg = wx.ComboBox(self, wx.ID_ANY,
                                    choices=FFmpegHelp.ARGS,
                                    size=(140, -1),
                                    style=wx.CB_DROPDOWN
                                    | wx.CB_READONLY,
                                    )
        self.cmbx_arg.SetSelection(0)
        sizerselect.Add(self.cmbx_arg, 0, wx.ALL, 5)
        self.text_topic = wx.TextCtrl(self, wx.ID_ANY,
                                      "", size=(140, -1),
                                      style=wx.TE_PROCESS_ENTER
                                      )
        sizerselect.Add(self.text_topic, 0, wx.ALL, 5)
        self.text_topic.Enable()
        self.text_topic.SetToolTip(_("Type the argument here and confirm "
                                     "with the enter key on your keyboard"))
        boxsearch = wx.BoxSizer(wx.HORIZONTAL)
        self.search_str = wx.SearchCtrl(self,
                                        wx.ID_ANY,
                                        size=(400, 30),
                                        style=wx.TE_PROCESS_ENTER,
                                        )
        self.search_str.SetToolTip(_("The search function allows you to find "
                                     "entries in the current topic"))
        boxsearch.Add(self.search_str, 0, wx.ALL, 0)
        self.case = wx.CheckBox(self, wx.ID_ANY, (_("Ignore case")))
        self.case.SetToolTip(_("Ignore case distinctions: characters with "
                               "different case will match."
                               ))
        boxsearch.Add(self.case, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer.Add(boxsearch, 0, wx.ALL, 5)
        # bottom layout
        grid = wx.GridSizer(1, 1, 0, 0)
        btn_close = wx.Button(self, wx.ID_CLOSE, "")
        grid.Add(btn_close, 0)
        sizer.Add(grid, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=5)
        self.SetTitle(_("FFmpeg help topics"))
        self.SetMinSize((750, 550))
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(vidicon, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

        self.SetSizer(sizer)
        self.Fit()
        self.Layout()
        # --------------- EVT
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_readme)
        if not hasattr(wx, 'EVT_SEARCH'):
            self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN,
                      self.on_search_strings, self.search_str)
        else:  # is wxPython >= 4.1
            self.Bind(wx.EVT_SEARCH, self.on_search_strings, self.search_str)

        if not hasattr(wx, 'EVT_SEARCH_CANCEL'):
            self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.on_delete,
                      self.search_str)
        else:  # is wxPython >= 4.1
            self.Bind(wx.EVT_SEARCH_CANCEL, self.on_delete, self.search_str)
        self.Bind(wx.EVT_COMBOBOX, self.on_selected, self.cmbx_main)
        self.Bind(wx.EVT_TEXT, self.on_search_strings, self.search_str)
        self.Bind(wx.EVT_TEXT, self.on_type_topic, self.text_topic)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_type_enter_key, self.text_topic)
        self.Bind(wx.EVT_CHECKBOX, self.on_ckbx, self.case)
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)  # caption X
    # ---------------------------------------------------------#

    def append_text(self, text):
        """
        Set the value to the text control. Note that on
        MS-Windows I've had some problems with rendering
        text color using the SetValue() method, so it seems
        the only chance is to use the Clear() method first
        and then the AppendText() method here.
        """
        self.textlist.Clear()  # delete previous append:
        self.textlist.AppendText(text)
        self.textlist.SetInsertionPoint(0)  # scroll to top
    # --------------------------------------------------------------#

    def on_help(self, event):
        """
        event on button help
        """
        msg = (_("This is a multifunctional search tool useful for local "
                 "help searches\n"
                 "on multiple FFmpeg topics and options. The search control, "
                 "to\nfind occurences on text obtained from the chosen "
                 "argument,\nis very similar to what grep does on the "
                 "Unix shell, but here\nit's done in real time.\n\n"
                 "If you don't find support for a certain codec or other "
                 "feature,\nit's likely that your version of FFmpeg is "
                 "too old or not configured\nwith those features."))
        win = NormalTransientPopup(self,
                                   wx.SIMPLE_BORDER,
                                   msg,
                                   FFmpegHelp.LGREEN,
                                   FFmpegHelp.BLACK)

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = event.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Popup()
    # --------------------------------------------------------------#

    def on_show_extra(self, event):
        """
        It can display formats (muxers and demuxers) codecs
        and decoders windows by calling them from the parent
        (main_frame) instead of calling them from the menu bar
        """
        name = event.GetEventObject().GetName()
        if name == 'formats':
            self.parent.get_ffmpeg_formats(self)
        elif name == 'decoders':
            self.parent.get_ffmpeg_decoders(self)
        elif name == 'encoders':
            self.parent.get_ffmpeg_codecs(self)
        elif name == 'configuration':
            self.parent.get_ffmpeg_conf(self)
    # --------------------------------------------------------------#

    def on_type_topic(self, event):
        """
        Event on typing any text on text box
        """
        if not self.text_topic.GetValue().strip():
            FFmpegHelp.ARGS_OPT[_("Help topic")] = ['--help', '']
            self.append_text(FFmpegHelp.HELPTOPIC + FFmpegHelp.EXAMPLES)
    # --------------------------------------------------------------#

    def on_type_enter_key(self, event):
        """
        Event when user press enter key on self.text_topic box.
        """
        self.search_str.Clear()
        arg = self.cmbx_arg.GetStringSelection()
        argstr = self.text_topic.GetValue().strip()
        if not argstr:
            return
        topic = ['--help', ] + [f'{arg}={argstr}']
        FFmpegHelp.ARGS_OPT[_("Help topic")] = topic
        self.row = io_tools.findtopic(topic)
        if self.row:
            self.append_text(self.row)
        else:
            self.append_text(_("\n  ..Nothing available"))
    # --------------------------------------------------------------#

    def on_selected(self, event):
        """
        Event selecting topic in the `cmbx_main`
        """
        topic = FFmpegHelp.ARGS_OPT[self.cmbx_main.GetValue()]
        self.search_str.Clear()

        if topic[0] == "--help":  # from _(Help topic) only
            self.text_topic.Enable()
            self.cmbx_arg.Enable()
            if not self.text_topic.GetValue().strip():
                self.append_text(FFmpegHelp.HELPTOPIC + FFmpegHelp.EXAMPLES)
            else:
                self.on_type_enter_key(self)
            return

        self.text_topic.Disable()
        self.cmbx_arg.Disable()
        self.row = io_tools.findtopic(topic)
        if self.row:
            self.append_text(self.row)
        else:
            self.append_text(_("\n  ..Nothing available"))
    # --------------------------------------------------------------#

    def on_search_strings(self, event, by_event=False):
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
            is_string = self.search_str.GetValue()
        else:  # in all other cases
            is_string = event.GetString()

        # ---> only cmbx_choice selection 0
        if (self.cmbx_main.GetSelection()
                == 0 and not self.text_topic.GetValue().split()):
            if not is_string:
                self.on_type_topic(self)
                return
            self.append_text(_("\n  ..Nothing available"))
            return
        # --- end

        if self.row and not is_string:
            self.append_text(self.row)  # load all lines
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
                self.append_text(_("\n  ..Not found"))
            else:
                self.append_text(' '.join(find))
        return
    # --------------------------------------------------------------#

    def on_ckbx(self, event):
        """
        This event updates the quick search with
        or without case sensitivity
        """
        self.on_search_strings(self, True)
    # --------------------------------------------------------------#

    def on_delete(self, event):
        """
        This event occurs when user click the small icon along
        the search text field to clear previus text entered.
        It seems does nothing, but it needed.
        During deletion, the "on_search_strings" call
        is generated automatically.
        """
        return
    # --------------------------------------------------------------#

    def on_close(self, event):
        """
        Destroy this window
        """
        pub.sendMessage("DESTROY_ORPHANED_WINDOWS", msg='HelpTopic')
