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

import subprocess
import wx

# get videomass wx.App attribute
get = wx.GetApp()
ffmpeg_url = get.ffmpeg_url
OS = get.OS

def parsing_import(path):
    """
    """
    status = None
    data = dict()
    if OS == 'Windows':
        null = 'NUL'
        cmd = ('%s -nostdin -hide_banner  -y -i "%s" '
              '-c copy -t 0 -map 0 -f null %s')
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True,
                                 startupinfo=startupinfo,
                                 )
            output =  p.communicate()
            
        except OSError as e:# if ffmpeg do not exist
                status = e
                return(data, status)
            
        else:
            
            if p.returncode: # if error occurred
                status = output[0]
                return(data, status)
            
            else:
                out = output[0].split('\n')
    else:
        import shlex
        null = '/dev/null'
        cmd = shlex.split('%s -nostdin -hide_banner  -y -i "%s" '
                          '-c copy -t 0 -map 0 -f null %s' %(ffmpeg_url, 
                                                             path, 
                                                             null)
                          )
        try:
            p = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True
                                 )
            output =  p.communicate()
            
        except OSError as e:# if ffmpeg do not exist
                status = e
                return(data, status)
            
        else:
            
            if p.returncode: # if error occurred
                status = output[0]
                return(data, status)
            
            else:
                lis = output[0].split('\n')
                
    index = 0
    for items in lis:
        if items.strip().startswith('Input '):
            data['Input'] = path
            
        if items.strip().startswith('Stream #0:%d' % index):
            data['index %d' % index] = items.strip().split()
            index +=1
            
        if items.strip().startswith('Duration:'):
            data['Time'] = items.strip().split(',')[0].split()[1]

    return(data, status)
        
    
    
