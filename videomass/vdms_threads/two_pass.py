# -*- coding: UTF-8 -*-
"""
Name: two_pass.py
Porpose: FFmpeg long processing task on 2 pass conversion
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Dec.02.2022
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
from threading import Thread
import time
import itertools
import subprocess
import platform
import wx
from pubsub import pub
from videomass.vdms_utils.utils import Popen
from videomass.vdms_io.make_filelog import logwrite
if not platform.system() == 'Windows':
    import shlex


class TwoPass(Thread):
    """
    This class represents a separate thread which need to read the
    stdout/stderr in real time mode. The subprocess module is instantiated
    twice for two different tasks: the process on the first video pass and
    the process on the second video pass for video only.

    NOTE capturing output in real-time (Windows, Unix):

    https://stackoverflow.com/questions/1388753/how-to-get-output-
    from-subprocess-popen-proc-stdout-readline-blocks-no-dat?rq=1

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    appdata = get.appset
    OS = appdata['ostype']
    NOT_EXIST_MSG = _("Is 'ffmpeg' installed on your system?")

    def __init__(self, logname, duration, timeseq, *args):
        """
        Called from `long_processing_task.topic_thread`.
        Also see `main_frame.switch_to_processing`.
        """
        self.stop_work_thread = False  # process terminate
        self.input_flist = args[1]  # list of infile (elements)
        self.passlist = args[5]  # comand list set for double-pass
        self.output_flist = args[3]  # output path
        self.duration = duration  # duration list
        self.time_seq = timeseq  # a time segment list
        self.volume = args[7]  # volume compensation data
        self.count = 0  # count first for loop
        self.countmax = len(args[1])  # length file list
        self.logname = logname  # title name of file log
        self.nul = 'NUL' if TwoPass.OS == 'Windows' else '/dev/null'

        Thread.__init__(self)
        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        Thread started.
        """
        filedone = []
        for (infile,
             outfile,
             volume,
             duration) in itertools.zip_longest(self.input_flist,
                                                self.output_flist,
                                                self.volume,
                                                self.duration,
                                                fillvalue='',
                                                ):
            # --------------- first pass
            pass1 = (f'"{TwoPass.appdata["ffmpeg_cmd"]}" '
                     f'{TwoPass.appdata["ffmpegloglev"]} '
                     f'{TwoPass.appdata["ffmpeg+params"]} {self.time_seq} '
                     f'-i "{infile}" {self.passlist[0]} '
                     f'{TwoPass.appdata["ffthreads"]} -y {self.nul}'
                     )
            self.count += 1
            count = f'File {self.count}/{self.countmax} - Pass One'
            cmd = (f'{count}\nSource: "{infile}"\nDestination: "{self.nul}"'
                   f'\n\n[COMMAND]:\n{pass1}'
                   )
            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=count,
                         fsource=f'Source:  "{infile}"',
                         destination=f'Destination:  "{self.nul}"',
                         duration=duration,
                         end='',
                         )
            logwrite(cmd, '', self.logname)  # write n/n + command only

            if not TwoPass.OS == 'Windows':
                pass1 = shlex.split(pass1)
            try:
                with Popen(pass1,
                           stderr=subprocess.PIPE,
                           bufsize=1,
                           universal_newlines=True,
                           encoding='utf8',
                           ) as proc1:

                    for line in proc1.stderr:
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output=line,
                                     duration=duration,
                                     status=0
                                     )
                        if self.stop_work_thread:  # break second 'for' loop
                            proc1.terminate()
                            break

                    if proc1.wait():  # will add '..failed' to txtctrl
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output='',
                                     duration=duration,
                                     status=proc1.wait(),
                                     )
                        logwrite('',
                                 f"Exit status: {proc1.wait()}",
                                 self.logname,
                                 )  # append exit error number

            except (OSError, FileNotFoundError) as err:
                excepterr = f"{err}\n  {TwoPass.NOT_EXIST_MSG}"
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count=excepterr,
                             fsource='',
                             destination='',
                             duration=0,
                             end='error',
                             )
                break

            if self.stop_work_thread:  # break first 'for' loop
                proc1.terminate()
                break  # fermo il ciclo for, altrimenti passa avanti

            if proc1.wait() == 0:  # will add '..terminated' to txtctrl
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count='',
                             fsource='',
                             destination='',
                             duration=duration,
                             end='Done'
                             )
            # --------------- second pass ----------------#
            pass2 = (f'"{TwoPass.appdata["ffmpeg_cmd"]}" '
                     f'{TwoPass.appdata["ffmpegloglev"]} '
                     f'{TwoPass.appdata["ffmpeg+params"]} {self.time_seq} '
                     f'-i "{infile}" {self.passlist[1]} '
                     f'{volume} {TwoPass.appdata["ffthreads"]} -y "{outfile}"'
                     )
            count = f'File {self.count}/{self.countmax} - Pass Two'
            cmd = (f'{count}\nSource: "{infile}"\nDestination: "{outfile}"'
                   f'\n\n[COMMAND]:\n{pass2}'
                   )

            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=count,
                         fsource=f'Source:  "{infile}"',
                         destination=f'Destination:  "{outfile}"',
                         duration=duration,
                         end='',
                         )
            logwrite(cmd, '', self.logname)

            if not TwoPass.OS == 'Windows':
                pass2 = shlex.split(pass2)

            with Popen(pass2,
                       stderr=subprocess.PIPE,
                       bufsize=1,
                       universal_newlines=True,
                       encoding='utf8',
                       ) as proc2:

                for line2 in proc2.stderr:
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output=line2,
                                 duration=duration,
                                 status=0,
                                 )
                    if self.stop_work_thread:
                        proc2.terminate()
                        break

                if proc2.wait():  # will add '..failed' to txtctrl
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output='',
                                 duration=duration,
                                 status=proc2.wait(),
                                 )
                    logwrite('',
                             f"Exit status: {proc2.wait()}",
                             self.logname,
                             )  # append exit error number

            if self.stop_work_thread:  # break first 'for' loop
                proc2.terminate()
                break  # fermo il ciclo for, altrimenti passa avanti

            if proc2.wait() == 0:  # will add '..terminated' to txtctrl
                filedone.append(infile)
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count='',
                             fsource='',
                             destination='',
                             duration=duration,
                             end='Done'
                             )
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT", msg=filedone)
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
