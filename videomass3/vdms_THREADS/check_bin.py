# -*- coding: UTF-8 -*-

#########################################################
# Name: check_bin.py
# Porpose: Gets the output to display the features of FFmpeg
# Compatibility: Python3 (Unix, Windows)
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

#------------------------------------------------------#
#------------------------------------------------------#
def subp_win32(args):
    """
    Execute commands received by args parameter on Windows 
    OS only.
    This function uses 'Popen' to invoke the subprocess, since 
    on Windows it is necessary to use the STARTUPINFO class, 
    therefore the following constants are available only on 
    Windows.
    
    """
    cmd = [] 
    for opt in args:
        cmd.append(opt)
    cmd = ' '.join(cmd)
        
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        p = subprocess.Popen(cmd, 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.STDOUT,
                             universal_newlines=True, # mod text
                             startupinfo=startupinfo,
                             )
        out =  p.communicate()
    
    except OSError as oserr:# if ffmpeg do not exist
        return('Not found', oserr)
        
    if p.returncode: # if returncode == 1
        return('Not found', out[0])
    
    return ('None', out[0])
#-----------------------------------------------------------#

def subp(args):
    """
    Execute commands received by args parameter on Unix-like 
    OS only.
    This function uses 'run' to invoke the subprocess, since 
    these are not advanced use cases.
    
    """
    cmd = [] 
    for opt in args:
        cmd.append(opt)
        
    try:
        p = subprocess.run(cmd, 
                           capture_output=True, 
                           universal_newlines=True
                           # mod text, otherwise must be used p.stdout.decode()
                           # for decode bytestring (b'')
                           )
        
    except FileNotFoundError as err:# if ffmpeg do not exist
        return('Not found', err)

    if p.returncode:# if has error on args
        err = p.stderr
        return('Not found', err)
    
    return ('None', p.stdout)
#-----------------------------------------------------------#

def ff_conf(ffmpeg_link, OS):
    """
    Receive output of the passed command to parse 
    configuration messages of FFmpeg
    
    ...Returns lists of:
        - info = [version number etc, release and building]
        - others = [building flags]
        - enable = [enabled features]
        - disable = [disable features]
    
    ...If errors returns 'Not found'
    
    """
    # grab generic informations:
    if OS == 'Windows':
        vers = subp_win32([ffmpeg_link, '-loglevel', 'error', '-version'])
    else:
        vers = subp([ffmpeg_link, '-loglevel', 'error', '-version'])
        
    if 'Not found' in vers[0]:
        return(vers[0], vers[1])

    info = []
    for v in vers[1].split('\n'):
        if 'ffmpeg version' in v:
            info.append(v.strip())
            
        if 'built with' in v:
            info.append(v.strip())
            
    # grab buildconf:
    if OS == 'Windows':
        build = subp_win32([ffmpeg_link, '-loglevel', 'error', '-buildconf'])
    else:
        build = subp([ffmpeg_link, '-loglevel', 'error', '-buildconf'])
    
    if 'Not found' in build[0]:
        return(build[0], build[1])

    conf = []
    for c in build[1].split('\n'):
        conf.append(c.strip())

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
    
    return(info, others, enable, disable)
#-------------------------------------------------------------------#

def ff_formats(ffmpeg_link, OS):
    """
    Receive output of *ffmpeg -formats* command and return a 
    ditionary with the follow keys and values:
    
        * KEYS                  * VALUES 
        'Demuxing Supported' :  [list of (D)emuxing formats support]
        'Muxing Supported' :    [list of (M)uxing formats support]
        'Mux/Demux Supported' : [list of (D)emuxing(M)uxing formats support]
    
    """
    # grab buildconf:
    if OS == 'Windows':
        ret = subp_win32([ffmpeg_link, '-loglevel', 'error', '-formats'])
    else:
        ret = subp([ffmpeg_link, '-loglevel', 'error', '-formats'])
    
    if 'Not found' in ret[0]:
        return({ret[0]:ret[1], '':'', '':''})
    
    frmt = ret[1].split('\n')
    
    
    dic = {'Demuxing Supported':[], 
           'Muxing Supported':[], 
           'Mux/Demux Supported':[]}
    
    for f in frmt:
        if f.strip().startswith('D '):
            dic['Demuxing Supported'].append(f.replace('D', '', 1).strip())
        elif f.strip().startswith('E '):
            dic['Muxing Supported'].append(f.replace('E', '', 1).strip())
        elif f.strip().startswith('DE '):
            dic['Mux/Demux Supported'].append(f.replace('DE', '', 1).strip())
            
    return(dic)
#-------------------------------------------------------------------#

def ff_codecs(ffmpeg_link, type_opt, OS):
    """
    Receive output of *ffmpeg -encoders* or *ffmpeg -decoders*
    command and return a ditionary with the follow keys and values:
    
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
    # grab encoders or decoders output:
    if OS == 'Windows':
        ret = subp_win32([ffmpeg_link, '-loglevel', 'error', type_opt])
    else:
        ret = subp([ffmpeg_link, '-loglevel', 'error', type_opt])
    
    if 'Not found' in ret[0]:
        return({ret[0], ret[1]})
    
    codecs = ret[1].split('\n')
    
    dic = {'Video':[], 'Audio':[], 'Subtitle':[]}
    
    for f in codecs:
        if f.strip().startswith('V'):
            if not 'V..... = Video' in f:
                dic['Video'].append(f.strip())
                
        elif f.strip().startswith('A'):
            if not 'A..... = Audio' in f:
                dic['Audio'].append(f.strip())
                
        elif f.strip().startswith('S'):
            if not 'S..... = Subtitle' in f:
                dic['Subtitle'].append(f.strip())
            
    return(dic)
#-------------------------------------------------------------------#

def ff_topics(ffmpeg_link, topic, OS):
    """
    Get output of the options help command of FFmpeg. 
    Note that the 'topic' parameter is always a list.
    
    """
    # get output:
    arr = [ffmpeg_link, '-loglevel', 'error'] + topic 
    if OS == 'Windows':
        ret = subp_win32(arr)
    else:
        ret = subp(arr)
    
    if 'Not found' in ret[0]:
        return(ret[0], ret[1])
    
    return ('None', ret[1])
