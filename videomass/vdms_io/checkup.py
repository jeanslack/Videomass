# -*- coding: UTF-8 -*-
"""
File Name: checkup.py
Porpose: input/output file check
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Aug.13.2025
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
import os
import wx
from videomass.vdms_dialogs.list_warning import ListWarning


def check_destination_dir(file_dest):
    """
    Check output destination directory only.
    return `None` if it meets the condition requirements,
    otherwise an error dialog will be shown and the function
    will return the boolean value `True`.

    """
    drn = os.path.abspath(file_dest)
    if os.path.exists(drn) and os.path.isdir(drn):
        return None

    wx.MessageBox(_('Output folder does not exist:\n\n"{}"\n').format(drn),
                  _('Videomass - Error!'), wx.ICON_ERROR)
    return True
# ------------------------------------------------------------------------#


def check_inout(file_sources, file_dest):
    """
    check for overwriting and file/dir existence.
    return tuple([file_sources], [file_dest]).
    return None otherwise.

    """
    # --------------- CHECK FOR OVERWRITING:
    files_ow = []  # already exist file LIST
    files_exist = []
    for files in file_dest:
        if os.path.exists(files):
            files_ow.append(f'"{files}"')

    if files_ow:
        msg = _('Files already exist, do you want to overwrite them?')
        with ListWarning(None,
                         dict.fromkeys(files_ow, _('Already exist')),
                         caption=_('Please confirm'),
                         header=msg,
                         buttons='CONFIRM',
                         ) as log:
            if log.ShowModal() != wx.ID_YES:
                return None

    # --------------- CHECK FOR MSSING FILES:
    for fln in file_sources:
        if not os.path.isfile(os.path.abspath(fln)):
            files_exist.append(f'"{fln}"')
    if files_exist:
        with ListWarning(None,
                         dict.fromkeys(files_exist, _('Not found')),
                         caption=_('Error list'),
                         header=_('File(s) not found'),
                         buttons='OK',
                         ) as log:
            log.ShowModal()
        return None
    # --------------- CHECK FOR EXISTING DIRECTORIES:
    for drn in file_dest:
        drn = os.path.abspath(os.path.dirname(drn))
        if not os.path.isdir(drn):
            wx.MessageBox(_('Output folder does not exist:\n\n"{}"\n').format(
                          drn), _('Videomass - Error!'), wx.ICON_ERROR
                          )
            return None

    return (file_sources, file_dest)
# ------------------------------------------------------------------------#


def check_files(*args, checkexists=True):
    """
    Build the full path filename for output files.
    return ([file_sources], [file_dest])
    None otherwise.

    """
    file_sources, dir_destin, same_destin = args[0], args[1], args[2]
    suffix, extout, outputnames = args[3], args[4], args[5]

    if not file_sources:
        return None

    file_dest = []  # output path names (not files)

    for path, fname in zip(file_sources, outputnames):
        dirname = os.path.dirname(path)

        if not extout:  # uses more extensions (copy formats)
            basename = os.path.basename(path)
            copyext = os.path.splitext(basename)[1]  # ext
            if same_destin:
                pathname = os.path.join(dirname, f'{fname}{suffix}{copyext}')
                file_dest.append(pathname)
            else:
                pathname = os.path.join(dir_destin, f'{fname}{copyext}')
                file_dest.append(pathname)

        else:  # uses one extension for all output
            if same_destin:
                pathname = os.path.join(dirname, f'{fname}{suffix}.{extout}')
                file_dest.append(pathname)
            else:
                pathname = os.path.join(dir_destin, f'{fname}.{extout}')
                file_dest.append(pathname)

    if checkexists:
        return check_inout(file_sources, file_dest)
    return (file_sources, file_dest)
