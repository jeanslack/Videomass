# -*- coding: UTF-8 -*-
"""
Name: ffprobe.py
Purpose: simple cross-platform wrap for ffprobe
Compatibility: Python >= 3.11
Platform: all platforms
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.05.2026
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

import json
import subprocess
import sys


def from_kwargs_to_args(kwargs):
    """
    Helper function to build command line
    arguments out of dict.
    """
    args = []
    for key in sorted(kwargs.keys()):
        val = kwargs[key]
        args.append(f"-{key}")
        if val is not None:
            args.append(f"{val}")
    return args


def ffprobe(filename, cmd="ffprobe", txtenc="utf-8", **kwargs):
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
    args = [cmd, "-show_format", "-show_streams", "-of", "json"]
    args.extend(from_kwargs_to_args(kwargs))
    args.append(filename)

    creationflags = (
        subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )

    try:
        with subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            text=True,
            encoding=txtenc,
            errors="replace",  # do not crash if non-UTF-8 chars
            creationflags=creationflags,
        ) as proc:
            output, error = proc.communicate()

            if proc.returncode != 0:
                return (None, f"ffprobe error: {error.strip()}")

        return json.loads(output), None

    except (OSError, FileNotFoundError) as excepterr:
        return (None, str(excepterr))

    except json.JSONDecodeError as jsonerr:
        return (None, f"Failed to parse ffprobe JSON output: {jsonerr!s}")
