# -*- coding: UTF-8 -*-
"""
Name: slideshow.py
Porpose: FFmpeg long processing task
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Apr.28.2022
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


def convert_images(*varargs):
    """
    Convert images to PNG format and assign
    progressive digits to them.
    """
    get = wx.GetApp()  # get videomass wx.App attribute
    appdata = get.appset
    opsystem = appdata['ostype']
    not_exist_msg = _("Is 'ffmpeg' installed on your system?")
    flist = varargs[0]
    tmpdir = varargs[1]
    logname = varargs[2]
    imagenames = varargs[3]

    wx.CallAfter(pub.sendMessage,
                 "COUNT_EVT",
                 count='Preparing temporary files...',
                 fsource='Source: Imported file list',
                 destination=f'Destination: "{tmpdir}"',
                 duration=len(flist),
                 end='',
                 )
    prognum = 0
    args = (f'"{appdata["ffmpeg_cmd"]}" '
            f'{appdata["ffmpegloglev"]} '
            f'{appdata["ffmpeg+params"]} ')
    logwrite(f'Preparing temporary files...\n'
             f'\n[COMMAND:]\n{args}', '', logname)

    for files in flist:
        prognum += 1
        tmpf = os.path.join(tmpdir, f'{imagenames}{prognum}.bmp')
        cmd_1 = (f'{args} -i "{files}" "{tmpf}"')

        if not opsystem == 'Windows':
            cmd_1 = shlex.split(cmd_1)
        try:
            with Popen(cmd_1,
                       stderr=subprocess.PIPE,
                       bufsize=1,
                       universal_newlines=True
                       ) as proc1:
                error = proc1.communicate()

            if proc1.returncode:  # ffmpeg error
                if error[1]:
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output='',
                                 duration=0,
                                 status=proc1.wait(),
                                 )
                    logwrite('',
                             f"Exit status: {proc1.wait()}\n{error[1]}",
                             logname,
                             )  # append exit error number
                    return error[1]

            else:  # ok
                wx.CallAfter(pub.sendMessage,
                             "UPDATE_EVT",
                             output=f' |{prognum}|  {files}  >  {tmpf}\n',
                             duration=0,
                             status=0,
                             )
        except (OSError, FileNotFoundError) as err:  # cmd not found
            excepterr = f"{err}\n  {not_exist_msg}"
            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=excepterr,
                         fsource='',
                         destination='',
                         duration=0,
                         end='error',
                         )
            return err

    time.sleep(.5)
    wx.CallAfter(pub.sendMessage,
                 "COUNT_EVT",
                 count='',
                 fsource='',
                 destination='',
                 duration=0,
                 end='ok'
                 )
    return None


def resizing_process(*varargs):
    """
    After the images have been converted to the required format,
    this process performs the resizing using ffmpeg filters.
    This is a necessary workaround for proper video playback.
    """
    get = wx.GetApp()  # get videomass wx.App attribute
    appdata = get.appset
    opsystem = appdata['ostype']
    not_exist_msg = _("Is 'ffmpeg' installed on your system?")
    flist = varargs[0]
    tmpdir = varargs[1]
    cmdargs = varargs[2]
    logname = varargs[3]

    wx.CallAfter(pub.sendMessage,
                 "COUNT_EVT",
                 count='File resizing...',
                 fsource='Source: Temporary directory',
                 destination=f'Destination: "{tmpdir}"',
                 duration=len(flist),
                 end='',
                 )

    tmpf = os.path.join(tmpdir, 'TMP_%d.bmp')
    tmpfout = os.path.join(tmpdir, 'IMAGE_%d.bmp')
    cmd_1 = (f'"{appdata["ffmpeg_cmd"]}" '
             f'{appdata["ffmpegloglev"]} '
             f'{appdata["ffmpeg+params"]} '
             f'-i "{tmpf}" {cmdargs} "{tmpfout}"'
             )
    logwrite(f'\nFile resizing...\n\n[COMMAND]:\n{cmd_1}', '', logname)

    if not opsystem == 'Windows':
        cmd_1 = shlex.split(cmd_1)
    try:
        with Popen(cmd_1,
                   stderr=subprocess.PIPE,
                   bufsize=1,
                   universal_newlines=True
                   ) as proc1:
            error = proc1.communicate()

        if proc1.returncode:  # ffmpeg error
            if error[1]:
                wx.CallAfter(pub.sendMessage,
                             "UPDATE_EVT",
                             output='',
                             duration=0,
                             status=proc1.wait(),
                             )
                logwrite('',
                         f"Exit status: {proc1.wait()}\n{error[1]}",
                         logname,
                         )  # append exit error number
                return error[1]

        else:  # ok
            wx.CallAfter(pub.sendMessage,
                         "UPDATE_EVT",
                         output='',
                         duration=0,
                         status=0,
                         )
    except (OSError, FileNotFoundError) as err:  # cmd not found
        excepterr = f"{err}\n  {not_exist_msg}"
        wx.CallAfter(pub.sendMessage,
                     "COUNT_EVT",
                     count=excepterr,
                     fsource='',
                     destination='',
                     duration=0,
                     end='error',
                     )
        return err

    time.sleep(.5)
    wx.CallAfter(pub.sendMessage,
                 "COUNT_EVT",
                 count='',
                 fsource='',
                 destination='',
                 duration=0,
                 end='ok'
                 )
    return None


class SlideshowMaker(Thread):
    """
    Represents the ffmpeg subprocess to produce a video in
    mkv format from a sequence of images already converted
    and resized in a temporary context.
    """
    get = wx.GetApp()  # get videomass wx.App attribute
    appdata = get.appset
    OS = appdata['ostype']
    SUFFIX = appdata['filesuffix']
    NOT_EXIST_MSG = _("Is 'ffmpeg' installed on your system?")

    def __init__(self, varargs, duration, logname):
        """
        Initialize the attributes given by varargs
        """
        Thread.__init__(self)

        self.filelist = varargs[1]  # input file list (items)
        # self.destdir = varargs[2]  # destination dir
        self.filedest = varargs[3]  # filename destination
        self.args_0 = varargs[4][0]  # args for temporary process
        self.preinput_1 = varargs[5]  # pre-input args for processing
        self.args_1 = varargs[4][1]  # args for processing
        self.duration = duration  # duration
        self.countmax = varargs[9]  # length file list
        self.count = 0  # count first for loop
        self.logname = logname  # log name
        self.stop_work_thread = False  # process terminate

        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        """
        imgtmpnames = 'TMP_' if self.args_0 else 'IMAGE_'
        filedone = []
        with tempfile.TemporaryDirectory() as tempdir:  # make tmp dir
            tmpproc1 = convert_images(self.filelist,
                                      tempdir,
                                      self.logname,
                                      imgtmpnames,
                                      )
            if tmpproc1 is not None:
                self.end_process(filedone)
                return

            if self.stop_work_thread:  # break second 'for' loop
                self.end_process(filedone)
                return

            if imgtmpnames == 'TMP_':
                tmpproc2 = resizing_process(self.filelist,
                                            tempdir,
                                            self.args_0,
                                            self.logname,
                                            )
                if tmpproc2 is not None:
                    self.end_process(filedone)
                    return

                if self.stop_work_thread:  # break second 'for' loop
                    self.end_process(filedone)
                    return

            # ------------------------------- make video
            tmpgroup = os.path.join(tempdir, 'IMAGE_%d.bmp')
            cmd_2 = (f'"{SlideshowMaker.appdata["ffmpeg_cmd"]}" '
                     f'{SlideshowMaker.appdata["ffmpegloglev"]} '
                     f'{SlideshowMaker.appdata["ffmpeg+params"]} '
                     f'{self.preinput_1} -i "{tmpgroup}" {self.args_1} '
                     f'"{self.filedest}"'
                     )
            count = '\nVideo production...'
            log = (f'{count}\nSource: "{tempdir}"\n'
                   f'Destination: "{self.filedest}"\n\n[COMMAND]:\n{cmd_2}')

            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=count,
                         fsource=f'Source:  "{tempdir}"',
                         destination=f'Destination:  "{self.filedest}"',
                         duration=self.duration,
                         end='',
                         )

            logwrite(log, '', self.logname)
            time.sleep(1)

            if not SlideshowMaker.OS == 'Windows':
                cmd_2 = shlex.split(cmd_2)

            try:
                with Popen(cmd_2,
                           stderr=subprocess.PIPE,
                           bufsize=1,
                           universal_newlines=True,
                           ) as proc2:
                    for line in proc2.stderr:
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output=line,
                                     duration=self.duration,
                                     status=0,
                                     )
                        if self.stop_work_thread:  # break second 'for' loop
                            proc2.terminate()
                            break

                    if proc2.wait():  # error
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output='',
                                     duration=self.duration,
                                     status=proc2.wait(),
                                     )
                        logwrite('',
                                 f"Exit status: {proc2.wait()}",
                                 self.logname,
                                 )  # append exit error number
                        time.sleep(1)

                    else:  # status ok
                        filedone = self.filelist
                        wx.CallAfter(pub.sendMessage,
                                     "COUNT_EVT",
                                     count='',
                                     fsource='',
                                     destination='',
                                     duration=self.duration,
                                     end='ok'
                                     )
            except (OSError, FileNotFoundError) as err:
                excepterr = f"{err}\n  {SlideshowMaker.NOT_EXIST_MSG}"
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count=excepterr,
                             fsource='',
                             destination='',
                             duration=0,
                             end='error',
                             )
        self.end_process(filedone)

    def end_process(self, filedone):
        """
        The process is finished
        """
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT", msg=filedone)

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
