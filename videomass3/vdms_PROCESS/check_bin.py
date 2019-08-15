# -*- coding: UTF-8 -*-
#########################################################
# Name: check_bin.py
# Porpose: Test the binaries of ffmpeg, ffprobe and ffplay
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Aug.15 2019
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

def ffmpeg_conf(ffmpeg_link, OS):
    """
    Execute FFmpeg without arguments to parse output 
    configuration  messages
    
    ...Returns lists of:
        - info = [version number etc, release and building]
        - others = [building flags]
        - enable = [enabled features]
        - disable = [disable features]
    
    ...If errors returns 'Not found'
    
    """
    if OS == 'Windows':# add Windows compatibility
        #TODO
        print('sono windows')
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        p = subprocess.Popen(ffmpeg_link,
                            stderr=subprocess.PIPE,
                            startupinfo=startupinfo,
                            )
        error =  p.communicate()
    else:
        try:
            p = subprocess.Popen([ffmpeg_link], stderr=subprocess.PIPE,) 
            err = p.communicate()
        except FileNotFoundError as err:
            return('Not found', err)

    info = []
    conf = []

    for vers in err[1].split(b'\n'):
        #if vers.startswith(b'ffmpeg version'):
        if b'ffmpeg version' in vers:
            info.append(vers.decode())
        if b'built with' in vers:
            info.append(vers.decode())
        if b'configuration' in vers:
            conf.append(vers.decode())

    enable = []
    disable = []
    others = []
    #print(conf[0].split())
    for e in conf[0].split():
        if e.startswith('--enable'):
            enable.append(e.split('--enable')[1])
        elif e.startswith('--disable'):
            disable.append(e.split('--disable')[1])
        else:
            others.append(e)
    if 'configuration:' in others:
        others.remove('configuration:')
            
    #print(enable)
    #print(disable)
    #print(others)
    
    return(info, others, enable, disable)
