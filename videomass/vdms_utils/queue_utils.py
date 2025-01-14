# -*- coding: UTF-8 -*-
"""
Name: queue_utils.py
Porpose: utils for queue managements
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
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
from videomass.vdms_dialogs.singlechoicedlg import SingleChoice


def write_json_file_queue(data, queuefile=None):
    """
    Write queue json file
    """
    if not queuefile:
        get = wx.GetApp()
        appdata = get.appset
        queuefile = os.path.join(appdata["confdir"], 'queue.backup')
    with open(queuefile, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)
# --------------------------------------------------------------------


def load_json_file_queue(newincoming=None):
    """
    Locates, loads and validates a QUEUE json file.
    Note, a Videomass queue file cannot contain multiple
    occurrences of the 'destination' key value
    """
    if not newincoming:
        wild = "Source (*.json)|*.json| All files (*.*)|*.*"
        with wx.FileDialog(None, _("Import queue file"),
                           defaultDir=os.path.expanduser('~'),
                           wildcard=wild,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fdlg:

            if fdlg.ShowModal() == wx.ID_CANCEL:
                return None
            newincoming = fdlg.GetPath()
    try:
        with open(newincoming, 'r', encoding='utf-8') as fln:
            newdata = json.load(fln)

    except json.decoder.JSONDecodeError as err:
        wx.MessageBox(f"ERROR: {str(err)}.\nInvalid file: «{newincoming}»",
                      _('Videomass - Error!'), wx.STAY_ON_TOP
                      | wx.ICON_ERROR
                      | wx.OK,
                      None
                      )
        return None

    keys = ('type', 'args', 'extension', 'logname', 'source', 'preset name',
            'destination', 'duration', 'start-time', 'end-time',)
    for ck in newdata:
        for key in keys:
            if key not in ck:
                msg = (_('ERROR: Keys mismatched for requested data.\n'
                         'Invalid file: «{0}»').format(newincoming))
                wx.MessageBox(msg, _('Videomass - Error!'), wx.STAY_ON_TOP
                              | wx.ICON_ERROR
                              | wx.OK,
                              None
                              )
                return None
    occurences = []
    msg = (_('ERROR: invalid data found loading queue file.\n'
             '«{0}»\n\nCannot contain multiple occurrences '
             'in `destination` keys value.').format(newincoming))
    for item in newdata:
        occurences.append(item['destination'])
    if any(occurences.count(x) > 1 for x in occurences):
        wx.MessageBox(msg, _('Videomass - Error!'),
                      wx.STAY_ON_TOP | wx.ICON_ERROR | wx.OK, None)
        return None
    return newdata
# --------------------------------------------------------------------


def extend_data_queue(parent, currentqueue: list, newqueue: list) -> list:
    """
    This function is responsible for extending the items of
    the `currentqueue` list while maintaining the same ID.
    The result varies based on the index of a specific
    selection given by the `selected` object.
    """
    indx_orig = []
    indx_new = []
    for indx1, olditem in enumerate(currentqueue):
        for indx2, newitem in enumerate(newqueue):
            if olditem['destination'] == newitem['destination']:
                indx_orig.append(indx1)
                indx_new.append(indx2)

    if indx_orig and indx_new:
        caption = _('Videomass - Add Items to Queue')
        message = (_('Multiple items with identical names and destination '
                     'paths cannot coexist.\nPlease choose one of the '
                     'following actions:'))
        choices = (
            _('Replace occurrences with items from the imported queue.'),
            _('Add only the currently missing items to the queue.'),
            _('Remove the current queue and replace it with the imported '
              'one.'))
        selected = None
        with SingleChoice(parent, caption, message, choices, setsel=2,
                          ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                selected = dlg.getvalue()

        if selected == 0:
            indx_orig.sort(reverse=True)  # IMPORTANT before iterate
            for idx in indx_orig:
                del currentqueue[idx]
            currentqueue.extend(newqueue)
        elif selected == 1:
            indx_new.sort(reverse=True)  # IMPORTANT before iterate
            for idx in indx_new:
                del newqueue[idx]
            currentqueue.extend(newqueue)
        elif selected == 2:
            currentqueue.clear()
            currentqueue.extend(newqueue)
        else:
            return None
    else:
        currentqueue.extend(newqueue)

    return currentqueue
