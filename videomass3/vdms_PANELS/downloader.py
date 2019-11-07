# -*- coding: UTF-8 -*-

#########################################################
# Name: presets_mng_panel.py
# Porpose: ffmpeg's presets manager panel
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Dec 28 2018, Aug.28 2019
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

# set widget colours in some case with html rappresentetion:
azure = '#15a6a6'# rgb form (wx.Colour(217,255,255))
yellow = '#a29500'
red = '#ea312d'
orange = '#f28924'
greenolive = '#8aab3c'
green = '#268826'

class Downloader(wx.Panel):
    """
    
    """

    def __init__(self, parent, OS):
        """
        """

        self.OS = OS
        self.parent = parent
        #self.file_destin = ''

        wx.Panel.__init__(self, parent, -1) 
        """constructor"""

        self.panel_1 = wx.Panel(self, wx.ID_ANY)

        #self.list_ctrl = wx.ListCtrl(self.panel_1, wx.ID_ANY, 
                                    #style=wx.LC_REPORT| 
                                          #wx.SUNKEN_BORDER
                                    #)
        nb1 = wx.Notebook(self.panel_1, wx.ID_ANY, style=0)
        nb1_p1 = wx.Panel(nb1, wx.ID_ANY)
        lab_prfl = wx.StaticText(nb1_p1, wx.ID_ANY, _("Select a preset from "
                                                      "the drop down:"))
        self.cmbx_prst = wx.ComboBox(nb1_p1,wx.ID_ANY, 
                                     choices=[],
                                     size=(200,-1),
                                     style=wx.CB_DROPDOWN | 
                                     wx.CB_READONLY
                                     )
        self.btn = wx.Button(nb1_p1, wx.ID_ANY, 'LA cerveza', size=(-1,-1))
        nb1_p2 = wx.Panel(nb1, wx.ID_ANY)
        
        labcmd_1 = wx.StaticBox(nb1_p2, wx.ID_ANY, _("First pass parameters:"))
        self.txt_1_cmd = wx.TextCtrl(nb1_p2, wx.ID_ANY,"", style=wx.TE_MULTILINE| 
                                                          wx.TE_PROCESS_ENTER
                                                          )
        labcmd_2 = wx.StaticBox(nb1_p2, wx.ID_ANY, _("Second pass parameters:"))
        self.txt_2_cmd = wx.TextCtrl(nb1_p2, wx.ID_ANY,"", style=wx.TE_MULTILINE| 
                                                          wx.TE_PROCESS_ENTER
                                                          )
        #----------------------Set Properties----------------------#
        self.cmbx_prst.SetSelection(0)
        
        #self.list_ctrl.SetBackgroundColour(azure)
        self.txt_1_cmd.SetMinSize((430, 60))
        self.txt_1_cmd.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.txt_1_cmd.SetToolTip(_('First pass parameters of the '
                                    'selected profile'))
        self.txt_2_cmd.SetMinSize((430, 60))
        self.txt_2_cmd.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.txt_2_cmd.SetToolTip(_('Second pass parameters of the '
                                    'selected profile'))

        #----------------------Build Layout----------------------#
        #siz1 = wx.BoxSizer(wx.VERTICAL)
        siz1 = wx.FlexGridSizer(1, 1, 0, 0)
        grid_siz7 = wx.GridSizer(3, 1, 0, 0)
        grd_s1 = wx.FlexGridSizer(2, 1, 0, 0)
        grd_s2 = wx.FlexGridSizer(3, 1, 0, 0)
        grd_s4 = wx.GridSizer(1, 3, 0, 0)
        grid_siz5 = wx.FlexGridSizer(2, 2, 0, 0)
        grid_siz6 = wx.FlexGridSizer(1, 7, 0, 0)
        grd_s3 = wx.GridSizer(1, 2, 0, 0)
        #grd_s1.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 15)
        
        labcmd_1.Lower()
        sizlab1 = wx.StaticBoxSizer(labcmd_1, wx.VERTICAL)
        sizlab1.Add(self.txt_1_cmd, 0, wx.ALL | wx.EXPAND 
                                            | wx.ALIGN_CENTER_HORIZONTAL 
                                            | wx.ALIGN_CENTER_VERTICAL, 15
                                            )
        grd_s3.Add(sizlab1,  0, wx.ALL | wx.EXPAND 
                                            | wx.ALIGN_CENTER_HORIZONTAL 
                                            | wx.ALIGN_CENTER_VERTICAL, 15
                                            )
        
        labcmd_2.Lower()
        sizlab2 = wx.StaticBoxSizer(labcmd_2, wx.VERTICAL)
        sizlab2.Add(self.txt_2_cmd, 0, wx.ALL | wx.EXPAND 
                                            | wx.ALIGN_CENTER_HORIZONTAL 
                                            | wx.ALIGN_CENTER_VERTICAL, 15
                                            )
        grd_s3.Add(sizlab2, 0, wx.ALL | wx.EXPAND 
                                            | wx.ALIGN_CENTER_HORIZONTAL 
                                            | wx.ALIGN_CENTER_VERTICAL, 15
                                            )
        grid_siz7.Add(lab_prfl, 0, wx.ALIGN_CENTER_HORIZONTAL | 
                                   wx.ALIGN_CENTER_VERTICAL, 0
                                   )
        grid_siz7.Add(self.cmbx_prst, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_siz7.Add(self.btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        nb1_p1.SetSizer(grid_siz7)
        nb1_p2.SetSizer(grd_s3)
        nb1.AddPage(nb1_p1, (_("Selecting presets")))
        nb1.AddPage(nb1_p2, (_("Command line FFmpeg")))
        grd_s2.Add(nb1, 1, wx.EXPAND, 0)
        grd_s2.Add(grd_s4, 1, wx.EXPAND, 0)
        grd_s1.Add(grd_s2, 1, wx.ALL | wx.EXPAND, 15)
        self.panel_1.SetSizer(grd_s1)
        siz1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(siz1)
        siz1.AddGrowableRow(0)
        siz1.AddGrowableCol(0)
        grd_s1.AddGrowableRow(0)
        grd_s1.AddGrowableCol(0)
        grd_s2.AddGrowableRow(0)
        grd_s2.AddGrowableCol(0)
        self.Layout()
        
        #----------------------Binder (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_start, self.btn)
    
    def on_start(self, event):
        opt = ''
        logname = 'DOWNLOADER'
        urls = self.parent.data

        self.parent.switch_Process('downloader',
                                        urls,
                                        '',
                                        self.parent.file_destin,
                                        opt,
                                        None,
                                        '',
                                        '',
                                        logname, 
                                        len(urls),
                                        )
        
        
