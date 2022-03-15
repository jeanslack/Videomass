# -*- coding: UTF-8 -*-
"""
Name: volumedetect.py
Porpose: Audio Peak level volume analyzes
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.11.2022
Code checker:
    flake8: --ignore F821, W504
    pylint: --ignore E0602, E1101

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
import os
from threading import Thread
import subprocess
import platform
import wx
from pubsub import pub
from videomass.vdms_utils.utils import Popen
from videomass.vdms_io.make_filelog import make_log_template
if not platform.system() == 'Windows':
    import shlex


class VolumeDetectThread(Thread):
    """
    This class represents a separate subprocess thread to get
    audio volume peak level when required for audio normalization
    process.

    NOTE: all error handling (including verification of the
    existence of files) is entrusted to ffmpeg, except for the
    lack of ffmpeg of course.

    """

    def __init__(self, timeseq, filelist, audiomap, logdir, ffmpeg_url):
        """
        Replace /dev/null with NUL on Windows.

        self.status: None, if nothing error,
                     'str error' if errors.
        self.data: it is a tuple containing the list of audio volume
                   parameters and the self.status of the output error,
                   in the form:
                   ([[maxvol, medvol], [etc,etc]], None or "str errors")
        """
        self.filelist = filelist
        empty = "-ss 00:00:00.000 -t 00:00:00.000"
        self.time_seq = '' if timeseq == empty else timeseq
        self.audiomap = audiomap
        self.ffmpeg_url = ffmpeg_url
        self.status = None
        self.data = None
        self.nul = 'NUL' if platform.system() == 'Windows' else '/dev/null'
        self.logf = os.path.join(logdir, 'volumedected.log')
        make_log_template('volumedected.log', logdir)
        # set initial file LOG

        Thread.__init__(self)
        self.start()  # start the thread (va in self.run())
    # ----------------------------------------------------------------#

    def run(self):
        """
        Audio volume data is getted by the thread's caller using
        the thread.data method (see io_tools).
        NOTE: wx.callafter(pub...) do not send data to pop-up
              dialog, but a empty string that is useful to get
              the end of the process to close of the pop-up

        """
        volume = []

        for files in self.filelist:
            cmd = (f'"{self.ffmpeg_url}" {self.time_seq} -i "{files}" '
                   f'-hide_banner {self.audiomap} -af volumedetect '
                   f'-vn -sn -dn -f null {self.nul}'
                   )
            self.logwrite(cmd)

            if not platform.system() == 'Windows':
                cmd = shlex.split(cmd)
            try:
                with Popen(cmd,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           universal_newlines=True,
                           ) as proc:

                    output = proc.communicate()

                    if proc.returncode:  # if error occurred
                        self.status = output[0]
                        break

                    raw_list = output[0].split()  # splitta tutti gli spazi
                    if 'mean_volume:' in raw_list:
                        mean_volume = raw_list.index("mean_volume:")
                        # mean_volume is indx integear
                        medvol = f"{raw_list[mean_volume + 1]} dB"
                        max_volume = raw_list.index("max_volume:")
                        # max_volume is indx integear
                        maxvol = f"{raw_list[max_volume + 1]} dB"
                        volume.append([maxvol, medvol])

            except (OSError, FileNotFoundError) as err:  # ffmpeg do not exist
                self.status = err
                break

        self.data = (volume, self.status)

        if self.status:
            self.logerror()

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
    # ----------------------------------------------------------------#

    def logwrite(self, cmd):
        """
        write ffmpeg command log
        """
        with open(self.logf, "a", encoding='utf8') as log:
            log.write(f"{cmd}\n")
    # ----------------------------------------------------------------#

    def logerror(self):
        """
        write ffmpeg volumedected errors
        """
        with open(self.logf, "a", encoding='utf8') as logerr:
            logerr.write(f"\n[FFMPEG] volumedetect "
                         f"ERRORS:\n{self.status}\n")
