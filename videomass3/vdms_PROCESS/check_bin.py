# -*- coding: UTF-8 -*-

#########################################################
# Name: check_bin.py
# Porpose: Test the binaries of ffmpeg, ffprobe and ffplay
# Compatibility: Python3, wxPython Phoenix on Unix like only
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

#-----------------------------------------------------------#

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
    try: # grab generic informations:
        p = subprocess.run([ffmpeg_link,
                              '-version'], 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT,) 
        vers = p.stdout
    except FileNotFoundError as e:
        return('Not found', e)

    info = []
    for v in vers.split(b'\n'):
        if b'ffmpeg version' in v:
            info.append(v.strip().decode())
        if b'built with' in v:
            info.append(v.strip().decode())
    
    try: # grab buildconf:
        p = subprocess.run([ffmpeg_link, 
                              '-loglevel', 
                              'error', 
                              '-buildconf'], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.STDOUT,)
        build = p.stdout
    except FileNotFoundError as e:
        return('Not found', e)
    
    conf = []
    for c in build.split(b'\n'):
        conf.append(c.strip().decode())

    enable = []
    disable = []
    others = []

    for en in conf:
        if en.startswith('--enable'):
            enable.append(en.split('--enable-')[1])
        elif en.startswith('--disable'):
            disable.append(en.split('--disable-')[1])
        else:
            others.append(en)
    if 'configuration:' in others:
        others.remove('configuration:')
    #if '' in others:
        #others.remove('')
    
    return(info, others, enable, disable)

#-------------------------------------------------------------------#

def ff_formats(ffmpeg_link):
    """
    bla bla bla
    """
    
    try: # grab buildconf:
        p = subprocess.run([ffmpeg_link, 
                                '-loglevel', 
                                'error', 
                                '-formats'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.STDOUT,)
        _f = p.stdout
    except FileNotFoundError as e:
        return('Not found', e)
            
    frmt = _f.split(b'\n')
    
    diz = {'Demuxing Supported':[], 
           'Muxing Supported':[], 
           'Mux/Demux Supported':[]}
    
    for f in frmt:
        if f.strip().startswith(b'D '):
            diz['Demuxing Supported'].append(f.replace(b'D', b'', 1).strip())
        elif f.strip().startswith(b'E '):
            diz['Muxing Supported'].append(f.replace(b'E', b'', 1).strip())
        elif f.strip().startswith(b'DE '):
            diz['Mux/Demux Supported'].append(f.replace(b'DE', b'', 1).strip())
            
    return(diz)
