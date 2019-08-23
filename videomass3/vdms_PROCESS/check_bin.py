# -*- coding: UTF-8 -*-

#########################################################
# Name: check_bin.py
# Porpose: Test the binaries of ffmpeg, ffprobe and ffplay
# Compatibility: Python3, wxPython4
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Aug.23 2019
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

def ff_conf(ffmpeg_link, OS):
    """
    Execute FFmpeg -version command to parse output 
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
    Parse output of *ffmpeg -formats* command (see p = subprocess below)
    and return a ditionary with the follow keys and values:
    
        * KEYS                  * VALUES 
        'Demuxing Supported' :  [list of (D)emuxing formats support]
        'Muxing Supported' :    [list of (M)uxing formats support]
        'Mux/Demux Supported' : [list of (D)emuxing(M)uxing formats support]
    
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
        return({'Not found':e, '':'', '':''})
        #return('Not found', e,)
            
    frmt = _f.split(b'\n')
    
    dic = {'Demuxing Supported':[], 
           'Muxing Supported':[], 
           'Mux/Demux Supported':[]}
    
    for f in frmt:
        if f.strip().startswith(b'D '):
            dic['Demuxing Supported'].append(f.replace(
                                      b'D', b'', 1).strip().decode())
        elif f.strip().startswith(b'E '):
            dic['Muxing Supported'].append(f.replace(
                                    b'E', b'', 1).strip().decode())
        elif f.strip().startswith(b'DE '):
            dic['Mux/Demux Supported'].append(f.replace(
                                       b'DE', b'', 1).strip().decode())
            
    return(dic)

#-------------------------------------------------------------------#

def ff_codecs(ffmpeg_link, type_opt):
    """
    Parse output of *ffmpeg -encoders* or *ffmpeg -decoders* commands 
    (see p = subprocess below) and return a ditionary with the follow 
    keys and values:
    
        * KEYS                  * VALUES 
        'Video' :    [list of V.....   name    descrition]
        'Audio' :    [list of A.....   name    descrition]
        'Subtitle' : [list of S.....   name    descrition]
    
    Accept two arguments: the call to FFmpeg and the type of 
    option used to obtain data on the encoding and decoding 
    capabilities of FFmpeg. The options to pass as arguments 
    are the following:
    
    -encoders
    -decoders
    
    """
    try: # grab buildconf:
        p = subprocess.run([ffmpeg_link, 
                                '-loglevel', 
                                'error', 
                                '%s' % type_opt], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.STDOUT,)
        _f = p.stdout
    except FileNotFoundError as e:
        return('Not found', e)
            
    codecs = _f.split(b'\n')
    
    dic = {'Video':[], 'Audio':[], 'Subtitle':[]}
    
    for f in codecs:
        if f.strip().startswith(b'V'):
            if not b'V..... = Video' in f:
                dic['Video'].append(f.strip().decode())
        elif f.strip().startswith(b'A'):
            if not b'A..... = Audio' in f:
                dic['Audio'].append(f.strip().decode())
        elif f.strip().startswith(b'S'):
            if not b'S..... = Subtitle' in f:
                dic['Subtitle'].append(f.strip().decode())
            
    return(dic)

#-------------------------------------------------------------------#

def ff_topics(ffmpeg_link, topic):
    """
    Get output of topic command of FFmpeg
    
    """
    try:
        p = subprocess.run([ffmpeg_link, topic],
                            capture_output=True,)
        
    except FileNotFoundError as e:
        return('Not found', e)
    
    #row = (p.stdout.split(b'\n'))
    row = "%s" % p.stdout.decode()
    return ('None', row)
    

