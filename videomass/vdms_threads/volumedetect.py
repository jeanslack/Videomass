# -*- coding: UTF-8 -*-
"""
Name: volumedetect.py
Porpose: Get FFmpeg audio Peak level volume analyzes
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: July.26.2025
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
    ERROR = 'Please, see «volumedetected.log» file for error details.\n'
    STOP = '[Videomass]: STOP command received.'

    def __init__(self, timeseq, filelist, audiomap):
        """
        Replace /dev/null with NUL on Windows.

        self.status: None, if nothing error,
                     tuple(str(message), str(info/error/warn)) if errors.
        self.data: it is a tuple containing the list of audio volume
                   parameters and the self.status of the output error,
                   in the form:
                   ([[maxvol, medvol], [etc,etc]], None or "str errors")
        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.stop_work_thread = False  # process terminate
        self.filelist = filelist
        self.time_seq = timeseq
        self.audiomap = audiomap
        self.status = None
        self.data = None
        self.nul = 'NUL' if platform.system() == 'Windows' else '/dev/null'
        self.logf = os.path.join(self.appdata['logdir'], 'volumedetected.log')
        make_log_template('volumedetected.log',
                          self.appdata['logdir'], mode="w")  # initial LOG

        Thread.__init__(self)
        self.start()
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
            cmd = (f'"{self.appdata["ffmpeg_cmd"]}" '
                   f'{self.appdata["ffmpeg-default-args"]} '
                   f'{self.appdata["ffmpeg_loglev"]} '
                   f'{self.time_seq[0]} '
                   f'-i "{files}" '
                   f'{self.time_seq[1]} '
                   f'{self.audiomap} '
                   f'-af volumedetect -vn -sn -dn -f null '
                   f'{self.nul}'
                   )
            self.logwrite(cmd)

            if not platform.system() == 'Windows':
                cmd = shlex.split(cmd)
            try:
                with Popen(cmd,
                           stderr=subprocess.PIPE,
                           stdin=subprocess.PIPE,
                           bufsize=1,
                           universal_newlines=True,
                           encoding=self.appdata['encoding'],
                           ) as proc:
                    meanv, maxv = '', ''
                    for line in proc.stderr:
                        if 'max_volume:' in line:
                            maxv = line.split(':')[1].strip()
                        if 'mean_volume:' in line:
                            meanv = line.split(':')[1].strip()

                        if self.stop_work_thread:
                            proc.stdin.write('q')  # stop ffmpeg
                            output = proc.communicate()[1]
                            proc.wait()
                            self.status = 'INFO', VolumeDetectThread.STOP
                            break

                        if proc.wait():
                            output = proc.communicate()[1]
                            self.status = 'ERROR', VolumeDetectThread.ERROR
                            break

                    volume.append((maxv, meanv))

            except (OSError, FileNotFoundError) as err:
                self.status = 'ERROR', VolumeDetectThread.ERROR
                output = err

            if self.status:
                self.logerror(output)
                break

        self.data = (volume, self.status)

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
    # ----------------------------------------------------------------#

    def logwrite(self, cmd):
        """
        write ffmpeg command log
        """
        with open(self.logf, "a", encoding='utf-8') as log:
            line = '=' * 80
            log.write(f"\n{line}\n{cmd}\n")
    # ----------------------------------------------------------------#

    def logerror(self, output):
        """
        write ffmpeg volumedected errors
        """
        with open(self.logf, "a", encoding='utf-8') as logerr:
            logerr.write(f"\n[FFMPEG] volumedetect "
                         f"ERRORS:\n{output}\n")
    # ----------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
