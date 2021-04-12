# -*- coding: UTF-8 -*-
# File Name: checkup.py
# Porpose: input/output file check
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Nov.08.2020 *PEP8 compatible*
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


def check_files(file_sources, dir_destin, same_destin, suffix, extout):
    """
    check for overwriting and the existence of
    files and directories.

    return following values:

    file_sources: a file list filtered by checking.
    outputdir: contains output paths as many as the file sources
    lenghmax: lengh list useful for count the loop index on the batch process.

    """
    if not file_sources:
        return (False, None, None, None, None)

    exclude = []  # already exist file names list, used by MessageBox
    outputdir = []  # output path names list
    # base_name = []  # represents the complete final basenames

    # --------------- CHECK OVERWRITING:
    for path in file_sources:
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        filename = os.path.splitext(basename)  # [name, ext]

        if not extout:  # uses more extensions (copy formats)
            if same_destin:
                pathname = '%s/%s%s%s' % (dirname, filename[0],
                                          suffix, filename[1])
                outputdir.append(dirname)
                # base_name.append(os.path.basename(pathname))
            else:
                pathname = '%s/%s' % (dir_destin, basename)
                outputdir.append(dir_destin)
                # base_name.append(basename)

            if os.path.exists(pathname):
                exclude.append(pathname)

        else:  # uses one extension for all output
            if same_destin:
                pathname = '%s/%s%s.%s' % (dirname, filename[0],
                                           suffix, extout)
                outputdir.append(dirname)
            else:
                pathname = '%s/%s.%s' % (dir_destin, filename[0], extout)
                outputdir.append(dir_destin)

            if os.path.exists(pathname):
                exclude.append(pathname)
    if exclude:
        if wx.MessageBox(_('Already exist: \n\n%s\n\n'
                           'Do you want to overwrite? ') %
                         ('\n'.join(exclude)),
                         _('Please Confirm'),
                         wx.ICON_QUESTION | wx.YES_NO, None) == wx.NO:

            return (False, None, None, None, None)

    # --------------- CHECK EXISTING FILES AND DIRECTORIES:
    for f in file_sources:
        if not os.path.isfile(os.path.abspath(f)):
            wx.MessageBox(_('File does not exist:\n\n"%s"\n') % (f),
                          "Videomass", wx.ICON_ERROR
                          )
            return (False, None, None, None, None)

    for d in outputdir:
        if not os.path.isdir(os.path.abspath(d)):
            wx.MessageBox(_('Output folder does not exist:\n\n"%s"\n') % (d),
                          'Videomass', wx.ICON_ERROR
                          )
            return (False, None, None, None, None)

    return (file_sources, outputdir, len(file_sources))
