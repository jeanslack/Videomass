# -*- coding: UTF-8 -*-
# Name: get_bmpfromSvg.py
# Porpose: return bmp image from a scalable vector graphic (svg format)
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: January.05.2021 *PEP8 compatible*
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
try:
    from wx.svg import SVGimage
except ModuleNotFoundError:
    pass


def get_bmp(imgfile, size):
    """
    Given a file  and a size, converts to bmp
    """

    img = SVGimage.CreateFromFile(imgfile)
    bmp = img.ConvertToScaledBitmap(size)

    return bmp
