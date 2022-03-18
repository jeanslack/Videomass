# -*- coding: UTF-8 -*-
"""
File Name: checkup.py
Porpose: input/output file check
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.18.2022
Code checker:
    flake8: --ignore F821
    pylint: --ignore E0602, E1101
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
import os
import wx


def check_inout(exclude,
                file_sources,
                outputdir
                ):
    """
    check for overwriting and file/dir existence.

    return following values:

    file_sources: a file list filtered by checking.
    outputdir: contains output paths as many as the file sources
    lenghmax: lengh list useful for count the loop index on the batch process.

    if already exists or file does not exist or output folder
    does not exist, return
        (False, None, None, None, None) .

    """
    if exclude:
        if wx.MessageBox(_('Already exist: \n\n{}\n\n'
                           'Do you want to overwrite? ').format(
                         '\n'.join(exclude)),
                         _('Please Confirm'),
                         wx.ICON_QUESTION | wx.YES_NO, None) == wx.NO:
            return None

    # --------------- CHECK EXISTING FILES AND DIRECTORIES:
    for fln in file_sources:
        if not os.path.isfile(os.path.abspath(fln)):
            wx.MessageBox(_('File does not exist:\n\n"{}"\n').format(fln),
                          "Videomass", wx.ICON_ERROR
                          )
            return None

    for drn in outputdir:
        if not os.path.isdir(os.path.abspath(drn)):
            wx.MessageBox(_('Output folder does not exist:\n\n"{}"\n').format(
                          drn), 'Videomass', wx.ICON_ERROR
                          )
            return None

    return (file_sources, outputdir, len(file_sources))


def check_files(file_sources,
                dir_destin,
                same_destin,
                suffix,
                extout
                ):
    """
    Creates the data structures relating to the files to
    be processed and to be excluded if they exist in the
    same path.

    if no file or one of the conditions returned by the
    check_inout function, return
        (False, None, None, None, None)

    return (file_sources, outputdir, len(file_sources)) otherwise

    """
    if not file_sources:
        return None

    exclude = []  # already exist file names list
    outputdir = []  # output path names list
    # base_name = []  # represents the complete final basenames

    # --------------- CHECK OVERWRITING:
    for path in file_sources:
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        filename = os.path.splitext(basename)  # [name, ext]

        if not extout:  # uses more extensions (copy formats)
            if same_destin:
                pathname = f'{dirname}/{filename[0]}{suffix}{filename[1]}'
                outputdir.append(dirname)
                # base_name.append(os.path.basename(pathname))
            else:
                pathname = f'{dir_destin}/{basename}'
                outputdir.append(dir_destin)
                # base_name.append(basename)

            if os.path.exists(pathname):
                exclude.append(pathname)

        else:  # uses one extension for all output
            if same_destin:
                pathname = f'{dirname}/{filename[0]}{suffix}.{extout}'
                outputdir.append(dirname)
            else:
                pathname = f'{dir_destin}/{filename[0]}.{extout}'
                outputdir.append(dir_destin)

            if os.path.exists(pathname):
                exclude.append(pathname)

    return check_inout(exclude, file_sources, outputdir)
