# -*- coding: UTF-8 -*-
# Name: check_bin.py
# Porpose: Gets the output to display the features of FFmpeg
# Compatibility: Python3 (Unix, Windows)
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.06.2020 *PEP8 compatible*
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


def subp(args, OS):
    """
    Execute commands which *do not* need to read the stdout/stderr in
    real time.

    Parameters:
        [*args* command list object]
        *OS* result of the platform.system()

    """
    cmd = []
    for opt in args:
        cmd.append(opt)

    if OS == 'Windows':
        cmd = ' '.join(cmd)
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    else:
        info = None
    try:
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             universal_newlines=True,  # mod text
                             startupinfo=info,
                             )
        out = p.communicate()

    except (OSError, FileNotFoundError) as oserr:  # if ffmpeg do not exist
        return('Not found', oserr)

    if p.returncode:  # if returncode == 1
        return('Not found', out[0])

    return ('None', out[0])
# -----------------------------------------------------------#


def ff_conf(FFMPEG_LINK, OS):
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

    # ------- grab generic informations:
    version = subp([FFMPEG_LINK, '-loglevel', 'error', '-version'], OS)

    if 'Not found' in version[0]:
        return(version[0], version[1])

    enable, disable, others, conf, info = [], [], [], [], []

    for vers in version[1].split('\n'):
        if 'ffmpeg version' in vers:
            info.append(vers.strip())

        if 'built with' in vers:
            info.append(vers.strip())

    # ------- grab buildconf:
    build = subp([FFMPEG_LINK, '-loglevel', 'error', '-buildconf'], OS)

    if 'Not found' in build[0]:
        return(build[0], build[1])

    for bld in build[1].split('\n'):
        conf.append(bld.strip())

    for enc in conf:
        if enc.startswith('--enable'):
            enable.append(enc.split('--enable-')[1])

        elif enc.startswith('--disable'):
            disable.append(enc.split('--disable-')[1])

        else:
            others.append(enc)

    if 'configuration:' in others:
        others.remove('configuration:')

    return(info, others, enable, disable)
# -------------------------------------------------------------------#


def ff_formats(FFMPEG_LINK, OS):
    """
    Receive output of *ffmpeg -formats* command and return a
    ditionary with the follow keys and values:

        * KEYS                  * VALUES
        'Demuxing Supported' :  [list of (D)emuxing formats support]
        'Muxing Supported' :    [list of (M)uxing formats support]
        'Mux/Demux Supported' : [list of (D)emuxing(M)uxing formats support]
    """

    # ------- grab buildconf:
    ret = subp([FFMPEG_LINK, '-loglevel', 'error', '-formats'], OS)

    if 'Not found' in ret[0]:
        return({ret[0]: ret[1], '': '', '': ''})

    frmt = ret[1].split('\n')

    dic = {'Demuxing Supported': [],
           'Muxing Supported': [],
           'Mux/Demux Supported': [],
           }
    for f in frmt:
        if f.strip().startswith('D '):
            dic['Demuxing Supported'].append(f.replace('D', '', 1).strip())
        elif f.strip().startswith('E '):
            dic['Muxing Supported'].append(f.replace('E', '', 1).strip())
        elif f.strip().startswith('DE '):
            dic['Mux/Demux Supported'].append(f.replace('DE', '', 1).strip())

    return(dic)
# -------------------------------------------------------------------#


def ff_codecs(FFMPEG_LINK, type_opt, OS):
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

    # ------- grab encoders or decoders output:
    ret = subp([FFMPEG_LINK, '-loglevel', 'error', type_opt], OS)

    if 'Not found' in ret[0]:
        return({ret[0], ret[1]})

    codecs = ret[1].split('\n')

    dic = {'Video': [], 'Audio': [], 'Subtitle': []}

    for f in codecs:
        if f.strip().startswith('V'):
            if 'V..... = Video' not in f:
                dic['Video'].append(f.strip())

        elif f.strip().startswith('A'):
            if 'A..... = Audio' not in f:
                dic['Audio'].append(f.strip())

        elif f.strip().startswith('S'):
            if 'S..... = Subtitle' not in f:
                dic['Subtitle'].append(f.strip())

    return(dic)
# -------------------------------------------------------------------#


def ff_topics(FFMPEG_LINK, topic, OS):
    """
    Get output of the options help command of FFmpeg.
    Note that the 'topic' parameter is always a list.
    """

    # ------ get output:
    arr = [FFMPEG_LINK, '-loglevel', 'error'] + topic
    ret = subp(arr, OS)

    if 'Not found' in ret[0]:
        return(ret[0], ret[1])

    return ('None', ret[1])
