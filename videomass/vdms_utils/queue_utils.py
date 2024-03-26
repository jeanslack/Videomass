# -*- coding: UTF-8 -*-
"""
Name: queue_utils.py
Porpose: utils for queue managements
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.23.2024
Code checker: flake8, pylint .

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
import json
import wx


def write_json_file_queue(data, queuefile=None):
    """
    Write queue json file
    """
    if not queuefile:
        get = wx.GetApp()
        appdata = get.appset
        queuefile = os.path.join(appdata["confdir"], 'queue.backup')
    with open(queuefile, 'w', encoding='utf8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)
# --------------------------------------------------------------------


def load_json_file_queue(newincoming=None):
    """
    Locates, loads and validates a QUEUE json file
    """
    if not newincoming:
        wildcard = "Source (*.json)|*.json| All files (*.*)|*.*"
        with wx.FileDialog(None, _("Import queue"),
                           "", "", wildcard, wx.FD_OPEN
                           | wx.FD_FILE_MUST_EXIST) as filedlg:

            if filedlg.ShowModal() == wx.ID_CANCEL:
                return None
            newincoming = filedlg.GetPath()
    try:
        with open(newincoming, 'r', encoding='utf8') as fln:
            newdata = json.load(fln)

    except json.decoder.JSONDecodeError as err:
        msg = _('You are attempting to load a json file written with '
                'invalid JSON encoding.')
        wx.MessageBox(f'\nERROR: {err}\n\nFILE: "{newincoming}"\n\n{msg}',
                      ("Videomass"), wx.STAY_ON_TOP
                      | wx.ICON_ERROR
                      | wx.OK,
                      None
                      )
        return None

    keys = ('type', 'args', 'fext', 'logname', 'fsrc',
            'fdest', 'duration', 'start-time', 'end-time')
    msg = (_(f'Error: invalid data found loading '
             f'queue file:\n\n"{newincoming}"'))
    for ck in newdata:
        for key in keys:
            if key not in ck:
                wx.MessageBox(msg, ("Videomass"), wx.STAY_ON_TOP
                              | wx.ICON_ERROR
                              | wx.OK,
                              None
                              )
                return None

    return newdata
