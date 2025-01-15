# -*- coding: UTF-8 -*-
"""
Name: ffprobe.py
Porpose: simple cross-platform wrap for ffprobe
Compatibility: Python3
Platform: all platforms
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.17.2022
Code checker: flake8, pylint

This file is part of FFcuesplitter.

   FFcuesplitter is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   FFcuesplitter is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with FFcuesplitter.  If not, see <http://www.gnu.org/licenses/>.
"""
import subprocess
import shlex
import platform
import json
from videomass.vdms_utils.utils import Popen


def from_kwargs_to_args(kwargs):
    """
    Helper function to build command line
    arguments out of dict.
    """
    args = []
    for key in sorted(kwargs.keys()):
        val = kwargs[key]
        args.append(f'-{key}')
        if val is not None:
            args.append(f'{val}')
    return args


def ffprobe(filename, cmd='ffprobe', txtenc='utf-8', **kwargs):
    """
    Run ffprobe subprocess on the specified file.
    This function always returns a tuple of two items (data, error),
    where `data` is the data representation given from the subprocess
    output, and `error` is the current status error.

    Raises:
        `OSError` or `FileNotFoundError` occurs if the ffprobe
        binary/executable does not exists.
    Returns:
        If the above exceptions raises, or if ffprobe returns a
        non-zero exit code, Returns (None, str(error)).
        Returns a JSON representation (dict(data), None) of the
        subprocess output otherwise.
    Usage:
        >>> from videomass.vdms_threads.ffprobe import ffprobe
        >>> probe = ffprobe(filename,
                            cmd='/path/to/ffprobe',
                            loglevel='error',
                            hide_banner=None,
                            **kwargs,
                            )
        >>> if probe[1]:
                raise Exception(probe[1])
        >>> else:
        >>>     probe[0]
    """
    args = (f'"{cmd}" -show_format -show_streams -of json '
            f'{" ".join(from_kwargs_to_args(kwargs))} '
            f'"{filename}"'
            )
    args = shlex.split(args) if platform.system() != 'Windows' else args
    try:
        with Popen(args,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   bufsize=1,
                   universal_newlines=True,
                   encoding=txtenc,
                   ) as proc:
            output, error = proc.communicate()

            if proc.returncode != 0:
                return (None, f'ffprobe: {error}')

    except (OSError, FileNotFoundError, UnicodeDecodeError) as excepterr:
        return (None, excepterr)

    return json.loads(output), None
