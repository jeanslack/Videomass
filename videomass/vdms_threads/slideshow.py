# -*- coding: UTF-8 -*-
"""
Name: slideshow.py
Porpose: FFmpeg long processing task
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.08.2024
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
import tempfile
from threading import Thread
import time
import subprocess
import platform
import wx
from pubsub import pub
from videomass.vdms_utils.utils import Popen
from videomass.vdms_io.make_filelog import logwrite
if not platform.system() == 'Windows':
    import shlex


def convert_images(*varargs, **kwargs):
    """
    Convert images to PNG format and assign
    progressive digits to them.
    """
    flist = varargs[0]
    tmpdir = varargs[1]
    logname = varargs[2]
    imagenames = varargs[3]

    count1 = (f'Preparing temporary files...\nSource: Imported file list\n'
              f'Destination: "{tmpdir}"\n')
    wx.CallAfter(pub.sendMessage,
                 "COUNT_EVT",
                 count=count1,
                 duration=len(flist),
                 end='CONTINUE',
                 )
    prognum = 0
    args = (f'"{kwargs["ffmpeg_cmd"]}" '
            f'{kwargs["ffmpeg-default-args"]} '
            f'{kwargs["ffmpeg_loglev"]} ')
    logwrite(f'Preparing temporary files...\n'
             f'\n[COMMAND:]\n{args}', '', logname)

    for files in flist:
        prognum += 1
        tmpf = os.path.join(tmpdir, f'{imagenames}{prognum}.bmp')
        cmd_1 = f'{args} -i "{files}" "{tmpf}"'

        if not platform.system() == 'Windows':
            cmd_1 = shlex.split(cmd_1)
        try:
            with Popen(cmd_1,
                       stderr=subprocess.PIPE,
                       bufsize=1,
                       universal_newlines=True,
                       encoding=kwargs['encoding'],
                       ) as proc1:
                error = proc1.communicate()[1]

            if proc1.returncode:  # ffmpeg error
                if error:
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output='FAILED',
                                 duration=0,
                                 status=proc1.wait(),
                                 )
                    logwrite('', (f"[VIDEOMASS]: Error Exit Status: "
                                  f"{proc1.wait()} {error}"), logname)
                    time.sleep(1)
                    return error

            else:  # ok
                wx.CallAfter(pub.sendMessage,
                             "UPDATE_EVT",
                             output=f' |{prognum}|  {files}  >  {tmpf}\n',
                             duration=0,
                             status=0,
                             )
        except (OSError, FileNotFoundError) as err:  # cmd not found
            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=err,
                         duration=0,
                         end='ERROR',
                         )
            return err

    time.sleep(.5)
    wx.CallAfter(pub.sendMessage,
                 "COUNT_EVT",
                 count='',
                 duration=0,
                 end='DONE'
                 )
    return None


def resizing_process(*varargs, **kwargs):
    """
    After the images have been converted to the required format,
    this process performs the resizing using ffmpeg filters.
    This is a necessary workaround for proper video playback.
    """
    flist = varargs[0]
    tmpdir = varargs[1]
    cmdargs = varargs[2]
    logname = varargs[3]

    count1 = (f'\n\nFile resizing...\nSource: Temporary directory\n'
              f'Destination: "{tmpdir}"')

    wx.CallAfter(pub.sendMessage,
                 "COUNT_EVT",
                 count=count1,
                 duration=len(flist),
                 end='CONTINUE',
                 )

    tmpf = os.path.join(tmpdir, 'TMP_%d.bmp')
    tmpfout = os.path.join(tmpdir, 'IMAGE_%d.bmp')
    cmd_1 = (f'"{kwargs["ffmpeg_cmd"]}" '
             f'{kwargs["ffmpeg-default-args"]} '
             f'{kwargs["ffmpeg_loglev"]} '
             f'-i "{tmpf}" {cmdargs} "{tmpfout}"'
             )
    logwrite(f'\nFile resizing...\n\n[COMMAND]:\n{cmd_1}', '', logname)

    if not platform.system() == 'Windows':
        cmd_1 = shlex.split(cmd_1)
    try:
        with Popen(cmd_1,
                   stderr=subprocess.PIPE,
                   bufsize=1,
                   universal_newlines=True,
                   encoding=kwargs['encoding'],
                   ) as proc1:
            error = proc1.communicate()[1]

        if proc1.returncode:  # ffmpeg error
            if error:
                wx.CallAfter(pub.sendMessage,
                             "UPDATE_EVT",
                             output='FAILED',
                             duration=0,
                             status=proc1.wait(),
                             )
                logwrite('', (f"[VIDEOMASS]: Error Exit Status: "
                              f"{proc1.wait()} {error}"), logname)
                time.sleep(1)
                return error

        else:  # ok
            wx.CallAfter(pub.sendMessage,
                         "UPDATE_EVT",
                         output='',
                         duration=0,
                         status=0,
                         )
            logwrite('', error, logname)
            time.sleep(1)

    except (OSError, FileNotFoundError) as err:  # cmd not found
        wx.CallAfter(pub.sendMessage,
                     "COUNT_EVT",
                     count=err,
                     duration=0,
                     end='ERROR',
                     )
        return err

    time.sleep(.5)
    wx.CallAfter(pub.sendMessage,
                 "COUNT_EVT",
                 count='',
                 duration=0,
                 end='DONE'
                 )
    return None


class SlideshowMaker(Thread):
    """
    Represents the ffmpeg subprocess to produce a video in
    mkv format from a sequence of images already converted
    and resized in a temporary context.
    """

    def __init__(self, *args, **kwargs):
        """
        Called from `long_processing_task.topic_thread`.
        Also see `main_frame.switch_to_processing`.
        """
        Thread.__init__(self)

        get = wx.GetApp()  # get videomass wx.App attribute
        self.appdata = get.appset
        self.stop_work_thread = False  # process terminate
        self.duration = kwargs['duration']
        self.count = 0  # count first for loop
        self.countmax = kwargs['nmax']
        self.logfile = args[0]  # log filename
        self.destination = kwargs['destination']
        self.kwa = kwargs

        self.start()

    def run(self):
        """
        Subprocess initialize thread.
        """
        imgtmpnames = 'TMP_' if self.kwa["resize"] else 'IMAGE_'
        filedone = []
        with tempfile.TemporaryDirectory() as tempdir:  # make tmp dir
            tmpproc1 = convert_images(self.kwa['source'],
                                      tempdir,
                                      self.logfile,
                                      imgtmpnames,
                                      **self.appdata,
                                      )
            if tmpproc1 is not None or self.stop_work_thread:
                wx.CallAfter(pub.sendMessage,
                             "UPDATE_EVT",
                             output='ERROR',
                             duration=self.kwa['duration'],
                             status=1,
                             )
                self.end_process(None)
                return

            if imgtmpnames == 'TMP_':
                tmpproc2 = resizing_process(self.kwa['source'],
                                            tempdir,
                                            self.kwa["resize"],
                                            self.logfile,
                                            **self.appdata,
                                            )

                if tmpproc2 is not None or self.stop_work_thread:
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output='ERROR',
                                 duration=self.kwa['duration'],
                                 status=1,
                                 )
                    self.end_process(None)
                    return

            # ------------------------------- make video
            tmpgroup = os.path.join(tempdir, 'IMAGE_%d.bmp')
            cmd_2 = (f'"{self.appdata["ffmpeg_cmd"]}" '
                     f'{self.appdata["ffmpeg-default-args"]} '
                     f'{self.appdata["ffmpeg_loglev"]} '
                     f'{self.kwa["pre-input-1"]} '
                     f'-i "{tmpgroup}" '
                     f'{self.kwa["args"]} '
                     f'"{self.destination}"'
                     )
            count = (f'\n\nVideo production...\nSource: "{tempdir}"\n'
                     f'Destination: "{self.destination}"\n')
            log = f'{count}\n\n[COMMAND]:\n{cmd_2}'

            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=count,
                         duration=self.duration,
                         end='CONTINUE',
                         )

            logwrite(log, '', self.logfile)
            time.sleep(1)

            if not self.appdata['ostype'] == 'Windows':
                cmd_2 = shlex.split(cmd_2)

            try:
                with Popen(cmd_2,
                           stderr=subprocess.PIPE,
                           stdin=subprocess.PIPE,
                           bufsize=1,
                           universal_newlines=True,
                           encoding=self.appdata['encoding'],
                           ) as proc2:
                    for line in proc2.stderr:
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output=line,
                                     duration=self.duration,
                                     status=0,
                                     )
                        if self.stop_work_thread:
                            proc2.stdin.write('q')  # stop ffmpeg
                            out = proc2.communicate()[1]
                            proc2.wait()
                            wx.CallAfter(pub.sendMessage,
                                         "UPDATE_EVT",
                                         output='STOP',
                                         duration=self.kwa['duration'],
                                         status=1,
                                         )
                            logwrite('', out, self.logfile)
                            time.sleep(1)
                            self.end_process(None)
                            return

                    if proc2.wait():  # error
                        out = proc2.communicate()[1]
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output='FAILED',
                                     duration=self.kwa['duration'],
                                     status=proc2.wait(),
                                     )
                        logwrite('', (f"[VIDEOMASS]: Error Exit Status: "
                                      f"{proc2.wait()} {out}"), self.logfile)
                        time.sleep(1)

                    else:  # status ok
                        filedone = self.kwa['source']
                        wx.CallAfter(pub.sendMessage,
                                     "COUNT_EVT",
                                     count='',
                                     duration=self.duration,
                                     end='DONE'
                                     )
            except (OSError, FileNotFoundError) as err:
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count=err,
                             duration=0,
                             end='ERROR',
                             )
                logwrite('', err, self.logfile)
        self.end_process(filedone)

    def end_process(self, filedone):
        """
        The process is finished
        """
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT", filetotrash=filedone)

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
