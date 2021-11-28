# -*- coding: UTF-8 -*-
"""
Name: shownormlist.py
Porpose: Show audio volume data list (PEAK/RMS only)
Compatibility: Python3, wxPython4
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.26.2021
Code checker:
    - flake8: --ignore F821, W504, F401
    - pylint: --ignore E0602, E1101, C0415, E0401, C0103
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
import wx
from videomass.vdms_dialogs.widget_utils import NormalTransientPopup


class NormalizationList(wx.MiniFrame):
    """
    Show FFmpeg volumedetect command data and report offset
    and gain results need for normalization process.

    """
    def __init__(self, title, data, OS):
        """
        detailslist is a list of items list.

        """
        wx.MiniFrame.__init__(self,
                              None,
                              style=wx.RESIZE_BORDER
                              | wx.CAPTION
                              | wx.CLOSE_BOX
                              | wx.SYSTEM_MENU)
        self.panel = wx.Panel(self,
                              wx.ID_ANY,
                              style=wx.TAB_TRAVERSAL
                              | wx.BORDER_THEME)
        normlist = wx.ListCtrl(self.panel,
                               wx.ID_ANY,
                               style=wx.LC_REPORT
                               | wx.SUNKEN_BORDER)
        # ----------------------Properties----------------------#
        self.SetTitle(_(title))
        self.SetMinSize((850, 400))
        normlist.SetMinSize((850, 250))
        normlist.InsertColumn(0, _('File name'), width=300)
        normlist.InsertColumn(1, _('Max volume dBFS'), width=150)
        normlist.InsertColumn(2, _('Mean volume dBFS'), width=150)
        normlist.InsertColumn(3, _('Offset dBFS'), width=100)
        normlist.InsertColumn(4, _('Result dBFS'), width=120)
        self.button_close = wx.Button(self.panel, wx.ID_CLOSE, "")
        descript = wx.StaticText(self.panel,
                                 wx.ID_ANY,
                                 (_('Post-normalization references:')
                                  ))
        self.btn_red = wx.Button(self.panel, wx.ID_ANY, ("?"), size=(30, -1))
        self.btn_red.SetBackgroundColour(wx.Colour(233, 80, 77))  # #e9504d
        self.btn_red.SetForegroundColour(wx.Colour(0, 0, 0))
        txtred = wx.StaticText(self.panel, wx.ID_ANY, (_("=  Clipped peaks")))

        self.btn_grey = wx.Button(self.panel, wx.ID_ANY, ("?"), size=(30, -1))
        self.btn_grey.SetBackgroundColour(wx.Colour(100, 100, 100))  # #646464
        self.btn_grey.SetForegroundColour(wx.Colour(0, 0, 0))
        txtgrey = wx.StaticText(self.panel, wx.ID_ANY, (_("=  No changes")))

        self.btn_yell = wx.Button(self.panel, wx.ID_ANY, ("?"), size=(30, -1))
        self.btn_yell.SetBackgroundColour(wx.Colour(198, 180, 38))  # #C6B426
        self.btn_yell.SetForegroundColour(wx.Colour(0, 0, 0))
        txtyell = wx.StaticText(self.panel,
                                wx.ID_ANY, (_("=  Below max peak")))

        sizer = wx.BoxSizer(wx.VERTICAL)

        gridbtn = wx.GridSizer(1, 1, 0, 0)
        sizer.Add(normlist, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(descript, 0, wx.ALL, 10)
        grid_list = wx.FlexGridSizer(1, 6, 0, 0)
        grid_list.Add(self.btn_red, 1, wx.ALL, 5)
        grid_list.Add(txtred, 1,
                      wx.ALL |
                      wx.ALIGN_CENTER_VERTICAL |
                      wx.ALIGN_CENTER_HORIZONTAL, 5
                      )
        grid_list.Add(self.btn_grey, 1, wx.ALL, 5)
        grid_list.Add(txtgrey, 1,
                      wx.ALL |
                      wx.ALIGN_CENTER_VERTICAL |
                      wx.ALIGN_CENTER_HORIZONTAL, 5
                      )
        grid_list.Add(self.btn_yell, 1, wx.ALL, 5)
        grid_list.Add(txtyell, 1,
                      wx.ALL |
                      wx.ALIGN_CENTER_VERTICAL |
                      wx.ALIGN_CENTER_HORIZONTAL, 5
                      )
        sizer.Add(grid_list, 0, wx.ALL, 5)

        sizer.Add(gridbtn, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=5)
        gridbtn.Add(self.button_close, 1, wx.ALL, 5)

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
            normlist.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
            descript.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
            txtred.SetFont(wx.Font(8, wx.SWISS, wx.ITALIC, wx.NORMAL))
            txtgrey.SetFont(wx.Font(8, wx.SWISS, wx.ITALIC, wx.NORMAL))
            txtyell.SetFont(wx.Font(8, wx.SWISS, wx.ITALIC, wx.NORMAL))

        # ----------------------Binding (EVT)------------------------#
        self.Bind(wx.EVT_BUTTON, self.on_red, self.btn_red)
        self.Bind(wx.EVT_BUTTON, self.on_grey, self.btn_grey)
        self.Bind(wx.EVT_BUTTON, self.on_yellow, self.btn_yell)
        self.Bind(wx.EVT_BUTTON, self.on_close, self.button_close)
        self.Bind(wx.EVT_CLOSE, self.on_close)  # controlla la chiusura (x)

        index = 0
        if title == _('RMS-based volume statistics'):
            for i in data:  # populate dmx listctrl:
                normlist.InsertItem(index, i[0])
                normlist.SetItem(index, 1, i[1])
                normlist.SetItem(index, 2, i[2])
                if float(i[3]) == 0.0:  # not changes
                    normlist.SetItemBackgroundColour(index, '#646464')  # grey
                    normlist.SetItem(index, 3, i[3])
                else:
                    normlist.SetItem(index, 3, i[3])
                if float(i[4]) > 0.0:  # is clipped red
                    normlist.SetItemBackgroundColour(index, '#e9504d')  # red
                    normlist.SetItem(index, 4, i[4])
                else:
                    normlist.SetItem(index, 4, i[4])

                if float(i[4]) < float(i[1]):  # target/res inf. to maxvol
                    normlist.SetItemBackgroundColour(index, '#C6B426')  # yel
                    normlist.SetItem(index, 4, i[4])
                else:
                    normlist.SetItem(index, 4, i[4])

        elif title == _('PEAK-based volume statistics'):
            for i in data:  # populate dmx listctrl:
                normlist.InsertItem(index, i[0])
                normlist.SetItem(index, 1, i[1])
                normlist.SetItem(index, 2, i[2])
                normlist.SetItem(index, 3, i[3])
                if float(i[4]) == float(i[1]):  # not changes
                    normlist.SetItemBackgroundColour(index, '#646464')  # grey
                    normlist.SetItem(index, 4, i[4])
                else:
                    normlist.SetItem(index, 4, i[4])
                if float(i[4]) < float(i[1]):  # target/res inf. to maxvol
                    normlist.SetItemBackgroundColour(index, '#C6B426')  # yel
                    normlist.SetItem(index, 4, i[4])
                else:
                    normlist.SetItem(index, 4, i[4])
    # --------------------------------------------------------------#

    def on_red(self, event):
        """
        event on button red
        """
        msg = (_("When it's red...\n\n"
                 "...It means the resulting audio will be clipped,\n"
                 "because its volume is higher than the maximum 0 db\n"
                 "level. This results in data loss and the audio may\n"
                 "sound distorted."))

        win = NormalTransientPopup(self,
                                   wx.SIMPLE_BORDER,
                                   msg,
                                   (233, 80, 77),
                                   (0, 0, 0))

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = event.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Popup()
    # --------------------------------------------------------------#

    def on_grey(self, event):
        """
        event on button grey
        """
        msg = (_("When it's grey...\n\n"
                 "...It means the resulting audio will not change,\n"
                 "because it's equal to the source."))

        win = NormalTransientPopup(self,
                                   wx.SIMPLE_BORDER,
                                   msg,
                                   (100, 100, 100),
                                   (250, 250, 250))

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
        msg = (_("When it's yellow...\n\n"
                 "...It means an audio signal will be produced with\n"
                 "a lower volume than the original."))

        win = NormalTransientPopup(self,
                                   wx.SIMPLE_BORDER,
                                   msg,
                                   (198, 180, 38),
                                   (0, 0, 0))

        # Show the popup right below or above the button
        # depending on available screen space...
        btn = event.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        win.Position(pos, (0, sz[1]))

        win.Popup()
    # --------------------------------------------------------------#

    def on_close(self, event):
        '''
        destroy dialog by button and the X
        '''
        self.Destroy()
