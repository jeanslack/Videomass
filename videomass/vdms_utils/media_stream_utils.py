# -*- coding: UTF-8 -*-
"""
Name: media_stream_utils.py
Purpose: It groups some function to work with ffprobe format/streams
Compatibility: Python >= 3.11, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.17.2026
Code checker: flake8, pylint, ruff .

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


def extract_video_stream(index):
    """
    Receives a list object derived from an index of `data_files`,

    Return the first valid video stream dictionary from ffprobe data,
    containing video dimension, filename and duration of video file,
    prioritizing real video streams over attached pictures (cover art).
    Returns None if no valid video stream is found.

    """
    streams = index.get("streams", [])
    frmat = index.get("format", {})

    if not isinstance(streams, list):
        return None

    video_stream = next(
        (
            s
            for s in streams
            if s.get("codec_type") == "video"
            and not s.get("disposition", {}).get("attached_pic", 0)
        ),
        None,
    )
    # Fallback: se non trova video reali, controlla se c'è almeno
    # uno stream video generico (es. immagine singola)
    # if not video_stream:
    #     print("NOT VIDEO STREAM")
    #     video_stream = next(
    #         (s for s in streams if s.get("codec_type") == "video"),
    #         None,
    #     )

    if video_stream and "width" in video_stream and "height" in video_stream:
        return {
            "width": int(video_stream["width"]),
            "height": int(video_stream["height"]),
            "filename": frmat.get("filename", ""),
            "duration": frmat.get("time", "00:00:00.000"),
        }

    return None


# ---------------------------------------------------------------------- #


def extract_audio_streams(index):
    """
    Return a list of valid audio stream dictionaries from ffprobe data.
    Returns an empty list if no audio streams are found.
    """
    if not isinstance(index, dict):
        return []

    streams = index.get("streams")
    if not isinstance(streams, list):
        return []

    return [
        s
        for s in streams
        if isinstance(s, dict) and s.get("codec_type") == "audio"
    ]
