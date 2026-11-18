# -*- coding: UTF-8 -*-
"""
Name: probe_worker.py
Purpose: Worker thread for ffprobe, specific to the ListCtrl
         component in Videomass.
Compatibility: Python >= 3.11
Platform: all platforms
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.18.2026
Code checker: flake8, pylint, ruff

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
   along with FFcuesplitter.  If not, see <http://www.gnu.org/licenses/>.
"""

import threading

import wx

from videomass.vdms_threads.ffprobe import ffprobe


class ProbeWorker(threading.Thread):
    """
    Background worker to run ffprobe on a batch of (path, newname) tuples.
    """

    def __init__(self, items, appdata, callback):
        super().__init__(daemon=True)
        self.items = items
        self.appdata = appdata
        self.callback = callback

    def run(self):
        results = []
        for path, newname in self.items:
            probe = ffprobe(
                path,
                cmd=self.appdata["ffprobe_cmd"],
                txtenc=self.appdata["encoding"],
                hide_banner=None,
                pretty=None,
            )
            results.append((path, newname, probe))

        wx.CallAfter(self.callback, results)
