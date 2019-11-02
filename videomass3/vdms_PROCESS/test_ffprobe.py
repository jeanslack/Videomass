# -*- coding: UTF-8 -*-

#########################################################
# Name: import_stream_parsing.py
# Porpose: Stream parsing command output
# Compatibility: Python3, Python2
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: October 28 2019
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

from ffprobe_parser import FFProbe

filename_url = '/home/gianluca/out_EBU.avi'
ffprobe_url = '/usr/bin/ffprobe'

data = FFProbe(ffprobe_url, filename_url, parse=False, 
                    pretty=True, select=None, entries=None,
                    show_format=True, show_streams=True, writer='json=c=1')

if data.ERROR():
    print ("Some Error:  %s" % (data.error))
    #return
else:
    print (data.video_stream())
    print (data.audio_stream())
    print (data.subtitle_stream())
    print (data.data_format())
    print(data.custom_output())

#print(data)
    
    
