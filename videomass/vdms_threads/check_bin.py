# -*- coding: UTF-8 -*-
"""
Name: check_bin.py
Porpose: Gets the output to display the features of FFmpeg
Compatibility: Python3 (Unix, Windows)
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: May.15.2021
Code checker: flake8, pylint

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

import subprocess
from videomass.vdms_utils.utils import Popen


def subp(args, ostype):
    """
    Execute commands which *do not* need to read the stdout/stderr in
    real time.

    Parameters:
        [*args* command list object]
        *ostype* result of the platform.system()

    """
    cmd = []
    for opt in args:
        cmd.append(opt)

    if ostype == 'Windows':
        cmd = ' '.join(cmd)
    try:
        with Popen(cmd,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.STDOUT,
                   universal_newlines=True,  # mod text
                   encoding='utf-8',
                   ) as proc:
            out = proc.communicate()

            if proc.returncode:  # if returncode == 1
                return ('Not found', out[0])

    except (OSError, FileNotFoundError) as oserr:  # no executable found
        return ('Not found', oserr)

    return ('None', out[0])
# -----------------------------------------------------------#


def ff_conf(ffmpeg_url, ostype):
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
    version = subp([ffmpeg_url, '-loglevel', 'error', '-version'], ostype)

    if 'Not found' in version[0]:
        return (version[0], version[1])

    enable, disable, others, conf, info = [], [], [], [], []

    for vers in version[1].split('\n'):
        if 'ffmpeg version' in vers:
            info.append(vers.strip())

        if 'built with' in vers:
            info.append(vers.strip())

    # ------- grab buildconf:
    build = subp([ffmpeg_url, '-loglevel', 'error', '-buildconf'], ostype)

    if 'Not found' in build[0]:
        return (build[0], build[1])

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

    return (info, others, enable, disable)
# -------------------------------------------------------------------#


def ff_formats(ffmpeg_url, ostype):
    """
    Receive output of *ffmpeg -formats* command and return a
    ditionary with the follow keys and values:

        * KEYS                  * VALUES
        'Demuxing Supported' :  [list of (D)emuxing formats support]
        'Muxing Supported' :    [list of (M)uxing formats support]
        'Mux/Demux Supported' : [list of (D)emuxing(M)uxing formats support]
    """

    # ------- grab buildconf:
    ret = subp([ffmpeg_url, '-loglevel', 'error', '-formats'], ostype)

    if 'Not found' in ret[0]:
        return {ret[0]: ret[1]}

    frmt = ret[1].split('\n')

    dic = {'Demuxing Supported': [],
           'Muxing Supported': [],
           'Mux/Demux Supported': [],
           }
    for its in frmt:
        if its.strip().startswith('D '):
            dic['Demuxing Supported'].append(its.replace('D', '', 1).strip())
        elif its.strip().startswith('E '):
            dic['Muxing Supported'].append(its.replace('E', '', 1).strip())
        elif its.strip().startswith('DE '):
            dic['Mux/Demux Supported'].append(its.replace('DE', '', 1).strip())

    return dic
# -------------------------------------------------------------------#


def ff_codecs(ffmpeg_url, type_opt, ostype):
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
    ret = subp([ffmpeg_url, '-loglevel', 'error', type_opt], ostype)

    if 'Not found' in ret[0]:
        return ({ret[0], ret[1]})

    codecs = ret[1].split('\n')

    dic = {'Video': [], 'Audio': [], 'Subtitle': []}

    for sup in codecs:
        if sup.strip().startswith('V'):
            if 'V..... = Video' not in sup:
                dic['Video'].append(sup.strip())

        elif sup.strip().startswith('A'):
            if 'A..... = Audio' not in sup:
                dic['Audio'].append(sup.strip())

        elif sup.strip().startswith('S'):
            if 'S..... = Subtitle' not in sup:
                dic['Subtitle'].append(sup.strip())

    return dic
# -------------------------------------------------------------------#


def ff_topics(ffmpeg_url, topic, ostype):
    """
    Get output of the options help command of FFmpeg.
    Note that the 'topic' parameter is always a list.
    """

    # ------ get output:
    arr = [ffmpeg_url, '-loglevel', 'error'] + list(topic)
    ret = subp(arr, ostype)

    if 'Not found' in ret[0]:
        return (ret[0], ret[1])

    return ('None', ret[1])
