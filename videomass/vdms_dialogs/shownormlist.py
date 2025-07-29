# -*- coding: UTF-8 -*-
"""
Name: shownormlist.py
Porpose: Show audio volume data list (PEAK/RMS only)
Compatibility: Python3, wxPython4
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.09.2023
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
from pubsub import pub
from videomass.vdms_dialogs.widget_utils import NormalTransientPopup


class AudioVolNormal(wx.Dialog):
    """
    It shows the target volume offset and the volume
    result obtained from the audio normalization process,
    as well as some statistics given by the volumedetect
    command.
    """
    get = wx.GetApp()
    if get.appset['IS_DARK_THEME'] is True:
        RED = '#600E0D'
        YELLOW = '#66640A'
        BLUE = '#174573'
        FOREGRD = '#FFFFFF'
    elif get.appset['IS_DARK_THEME'] is False:
        RED = '#FF3348'
        YELLOW = '#E6D039'
        BLUE = '#3BBBE6'
        FOREGRD = '#050505'
    else:
        RED = 'ORANGE'
        YELLOW = 'YELLOW GREEN'
        BLUE = 'LIGHT STEEL BLUE'
        FOREGRD = 'BLACK'

    def __init__(self, title, data, OS):
        """
        data contains volume list per-track.
        """
        get = wx.GetApp()  # get data from bootstrap
        vidicon = get.iconset['videomass']
        self.red = AudioVolNormal.RED
        self.yellow = AudioVolNormal.YELLOW
        self.blue = AudioVolNormal.BLUE
        self.fgrd = AudioVolNormal.FOREGRD

        wx.Dialog.__init__(self, None,
                           style=wx.DEFAULT_DIALOG_STYLE
                           | wx.RESIZE_BORDER
                           | wx.DIALOG_NO_PARENT
                           )
        self.panel = wx.Panel(self,
                              wx.ID_ANY,
                              style=wx.TAB_TRAVERSAL
                              | wx.BORDER_THEME,
                              )
        normlist = wx.ListCtrl(self.panel,
                               wx.ID_ANY,
                               style=wx.LC_REPORT
                               | wx.SUNKEN_BORDER,
                               )
        normlist.SetMinSize((850, 250))
        normlist.InsertColumn(0, _('File name'), width=300)
        normlist.InsertColumn(1, _('Max volume dBFS'), width=150)
        normlist.InsertColumn(2, _('Mean volume dBFS'), width=150)
        normlist.InsertColumn(3, _('Offset dBFS'), width=100)
        normlist.InsertColumn(4, _('Result dBFS'), width=120)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(normlist, 1, wx.EXPAND | wx.ALL, 5)
        descript = wx.StaticText(self.panel,
                                 wx.ID_ANY,
                                 (_('Post-normalization references:')
                                  ))
        sizer.Add(descript, 0, wx.ALL, 10)
        grid_list = wx.FlexGridSizer(1, 6, 0, 0)
        sizer.Add(grid_list, 0, wx.ALL, 5)

        self.btn_red = wx.Button(self.panel, wx.ID_ANY, _("Read me"),
                                 size=(-1, -1))
        self.btn_red.SetBackgroundColour(wx.Colour(self.red))
        grid_list.Add(self.btn_red, 1, wx.ALL, 5)
        txtred = wx.StaticText(self.panel, wx.ID_ANY, (_("=  Clipped peaks")))
        grid_list.Add(txtred, 1, wx.ALL
                      | wx.ALIGN_CENTER_VERTICAL
                      | wx.ALIGN_CENTER_HORIZONTAL, 5,
                      )
        self.btn_blue = wx.Button(self.panel, wx.ID_ANY, _("Read me"),
                                  size=(-1, -1))
        self.btn_blue.SetBackgroundColour(wx.Colour(self.blue))
        grid_list.Add(self.btn_blue, 1, wx.ALL, 5)
        txtgrey = wx.StaticText(self.panel, wx.ID_ANY, (_("=  No changes")))
        grid_list.Add(txtgrey, 1, wx.ALL
                      | wx.ALIGN_CENTER_VERTICAL
                      | wx.ALIGN_CENTER_HORIZONTAL, 5,
                      )
        self.btn_yell = wx.Button(self.panel, wx.ID_ANY, _("Read me"),
                                  size=(-1, -1))
        self.btn_yell.SetBackgroundColour(wx.Colour(self.yellow))
        grid_list.Add(self.btn_yell, 1, wx.ALL, 5)
        txtyell = wx.StaticText(self.panel,
                                wx.ID_ANY, (_("=  Below max peak")))
        grid_list.Add(txtyell, 1, wx.ALL
                      | wx.ALIGN_CENTER_VERTICAL
                      | wx.ALIGN_CENTER_HORIZONTAL, 5,
                      )
        # bottm btns
        gridbtn = wx.GridSizer(1, 1, 0, 0)
        sizer.Add(gridbtn, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=0)
        self.button_close = wx.Button(self.panel, wx.ID_CLOSE, "")
        gridbtn.Add(self.button_close, 1, wx.ALL, 5)

        # ----------------------Properties----------------------#
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(vidicon, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetTitle(title)
        self.SetMinSize((850, 400))
        self.panel.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()

        if OS == 'Darwin':
            normlist.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL))
            descript.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
            txtred.SetFont(wx.Font(11, wx.SWISS, wx.ITALIC, wx.NORMAL))
            txtgrey.SetFont(wx.Font(11, wx.SWISS, wx.ITALIC, wx.NORMAL))
            txtyell.SetFont(wx.Font(11, wx.SWISS, wx.ITALIC, wx.NORMAL))
        else:
            self.btn_red.SetForegroundColour(wx.Colour(self.fgrd))
            self.btn_blue.SetForegroundColour(wx.Colour(self.fgrd))
            self.btn_yell.SetForegroundColour(wx.Colour(self.fgrd))
            normlist.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            descript.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
            txtred.SetFont(wx.Font(8, wx.SWISS, wx.ITALIC, wx.NORMAL))
            txtgrey.SetFont(wx.Font(8, wx.SWISS, wx.ITALIC, wx.NORMAL))
            txtyell.SetFont(wx.Font(8, wx.SWISS, wx.ITALIC, wx.NORMAL))

        # ----------------------Binding (EVT)------------------------#
        self.Bind(wx.EVT_BUTTON, self.on_red, self.btn_red)
        self.Bind(wx.EVT_BUTTON, self.on_blue, self.btn_blue)
        self.Bind(wx.EVT_BUTTON, self.on_yellow, self.btn_yell)
        self.Bind(wx.EVT_BUTTON, self.on_close, self.button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)  # controlla la chiusura (x)

        index = 0
        if title == _('RMS-based volume statistics'):
            for items in data:  # populate dmx listctrl:
                normlist.InsertItem(index, items[0])
                normlist.SetItem(index, 1, items[1])
                normlist.SetItem(index, 2, items[2])

                if float(items[3]) == 0.0:  # not changes
                    normlist.SetItemBackgroundColour(index, self.blue)
                    normlist.SetItem(index, 3, items[3])
                else:
                    normlist.SetItem(index, 3, items[3])

                if float(items[4]) > 0.0:  # is clipped red
                    normlist.SetItemBackgroundColour(index, self.red)
                    normlist.SetItem(index, 4, items[4])
                else:
                    normlist.SetItem(index, 4, items[4])

                if float(items[4]) < float(items[1]):  # target
                    normlist.SetItemBackgroundColour(index, self.yellow)
                    normlist.SetItem(index, 4, items[4])
                else:
                    normlist.SetItem(index, 4, items[4])
                index += 1

        if title == _('PEAK-based volume statistics'):
            for items in data:  # populate dmx listctrl:
                normlist.InsertItem(index, items[0])
                normlist.SetItem(index, 1, items[1])
                normlist.SetItem(index, 2, items[2])
                normlist.SetItem(index, 3, items[3])

                if float(items[4]) == float(items[1]):  # not changes
                    normlist.SetItemBackgroundColour(index, self.blue)
                    normlist.SetItem(index, 4, items[4])
                else:
                    normlist.SetItem(index, 4, items[4])
                if float(items[4]) < float(items[1]):  # target
                    normlist.SetItemBackgroundColour(index, self.yellow)

                    normlist.SetItem(index, 4, items[4])
                else:
                    normlist.SetItem(index, 4, items[4])
                index += 1
    # --------------------------------------------------------------#

    def on_red(self, event):
        """
        event on button red
        """
        msg = (_("...It means the resulting audio will be clipped,\n"
                 "because its volume is higher than the maximum 0 db\n"
                 "level. This results in data loss and the audio may\n"
                 "sound distorted."))

        win = NormalTransientPopup(self,
                                   wx.SIMPLE_BORDER,
                                   msg,
                                   (self.red),
                                   (self.fgrd),
                                   )

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = event.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Popup()
    # --------------------------------------------------------------#

    def on_blue(self, event):
        """
        event on button blue
        """
        msg = (_("...It means the resulting audio will not change,\n"
                 "because it's equal to the source."))

        win = NormalTransientPopup(self,
                                   wx.SIMPLE_BORDER,
                                   msg,
                                   (self.blue),
                                   (self.fgrd),
                                   )

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = event.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Popup()
    # --------------------------------------------------------------#

    def on_yellow(self, event):
        """
        event on button yellow
        """
        msg = (_("...It means an audio signal will be produced with\n"
                 "a lower volume than the source."))

        win = NormalTransientPopup(self,
                                   wx.SIMPLE_BORDER,
                                   msg,
                                   (self.yellow),
                                   (self.fgrd),
                                   )

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = event.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Popup()
    # --------------------------------------------------------------#

    def on_close(self, event):
        """
        Destroy this window
        """
        pub.sendMessage("DESTROY_ORPHANED_WINDOWS", msg='AudioVolNormal')
