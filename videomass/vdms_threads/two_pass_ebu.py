# -*- coding: UTF-8 -*-
"""
Name: two_pass_EBU.py
Porpose: FFmpeg long processing task with EBU normalization
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.10.2022
Code checker: flake8: --ignore F821, W504

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


class Loudnorm(Thread):
    """
    Like `TwoPass_Thread` but execute -loudnorm parsing from first
    pass and has definitions to apply on second pass.

    NOTE capturing output in real-time (Windows, Unix):

    https://stackoverflow.com/questions/1388753/how-to-get-output-
    from-subprocess-popen-proc-stdout-readline-blocks-no-dat?rq=1

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    appdata = get.appset
    OS = appdata['ostype']
    SUFFIX = appdata['filesuffix']
    NOT_EXIST_MSG = _("Is 'ffmpeg' installed on your system?")

    def __init__(self, var, duration, logname, timeseq):
        """
        """
        self.stop_work_thread = False  # process terminate
        self.filelist = var[1]  # list of files (elements)
        self.ext = var[2]
        self.passlist = var[5]  # comand list
        self.audio_outmap = var[6]  # map output list
        self.outputdir = var[3]  # output path
        self.duration = duration  # duration list
        self.time_seq = timeseq  # a time segment
        self.count = 0  # count first for loop
        self.countmax = len(var[1])  # length file list
        self.logname = logname  # title name of file log
        self.nul = 'NUL' if Loudnorm.OS == 'Windows' else '/dev/null'

        Thread.__init__(self)
        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        Subprocess initialize thread.
        """
        filedone = []
        summary = {'Input Integrated:': None, 'Input True Peak:': None,
                   'Input LRA:': None, 'Input Threshold:': None,
                   'Output Integrated:': None, 'Output True Peak:': None,
                   'Output LRA:': None, 'Output Threshold:': None,
                   'Normalization Type:': None, 'Target Offset:': None
                   }
        for (files,
             folders,
             duration) in itertools.zip_longest(self.filelist,
                                                self.outputdir,
                                                self.duration,
                                                fillvalue='',
                                                ):
            basename = os.path.basename(files)  # name.ext
            filename = os.path.splitext(basename)[0]  # name
            source_ext = os.path.splitext(basename)[1].split('.')[1]  # ext
            outext = source_ext if not self.ext else self.ext
            outputfile = os.path.join(folders,
                                      f'{filename}{Loudnorm.SUFFIX}.{outext}')

            # --------------- first pass
            pass1 = (f'"{Loudnorm.appdata["ffmpeg_cmd"]}" -nostdin -loglevel '
                     f'info -stats -hide_banner {self.time_seq} -i "{files}" '
                     f'{self.passlist[0]} {Loudnorm.appdata["ffthreads"]} -y '
                     f'{self.nul}'
                     )
            self.count += 1
            count = (f'File {self.count}/{self.countmax} - Pass One\n '
                     f'Loudnorm ebu: Getting statistics for measurements...')
            cmd = (f'{count}\nSource: "{files}"\nDestination: "{self.nul}"\n\n'
                   f'[COMMAND]:\n{pass1}')

            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=count,
                         fsource=f'Source:  "{files}"',
                         destination=f'Destination: "{self.nul}"',
                         duration=duration,
                         end='',
                         )
            logwrite(cmd, '', self.logname)  # write n/n + command only

            if not Loudnorm.OS == 'Windows':
                pass1 = shlex.split(pass1)
            try:
                with Popen(pass1,
                           stderr=subprocess.PIPE,
                           bufsize=1,
                           universal_newlines=True,
                           ) as proc1:

                    for line in proc1.stderr:
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output=line,
                                     duration=duration,
                                     status=0
                                     )
                        if self.stop_work_thread:  # break first 'for' loop
                            proc1.terminate()
                            break

                        for k in summary:
                            if line.startswith(k):
                                summary[k] = line.split(':')[1].split()[0]

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
                        break

            except (OSError, FileNotFoundError) as err:
                excepterr = f"{err}\n  {Loudnorm.NOT_EXIST_MSG}"
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count=excepterr,
                             fsource='',
                             destination='',
                             duration=0,
                             end='error'
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
                             end='ok'
                             )
            # --------------- second pass ----------------#
            filters = (f'{self.passlist[2]}'
                       f':measured_I={summary["Input Integrated:"]}'
                       f':measured_LRA={summary["Input LRA:"]}'
                       f':measured_TP={summary["Input True Peak:"]}'
                       f':measured_thresh={summary["Input Threshold:"]}'
                       f':offset={summary["Target Offset:"]}'
                       f':linear=true:dual_mono=true'
                       )
            time.sleep(.5)

            pass2 = (f'"{Loudnorm.appdata["ffmpeg_cmd"]}" -nostdin -loglevel '
                     f'info -stats -hide_banner {self.time_seq} -i '
                     f'"{files}" {self.passlist[1]} '
                     f'-filter:a:{self.audio_outmap[1]} {filters} '
                     f'{Loudnorm.appdata["ffthreads"]} -y '
                     f'"{folders}/{filename}{Loudnorm.SUFFIX}.{outext}"'
                     )
            count = (f'File {self.count}/{self.countmax} - Pass Two\n'
                     f'Loudnorm ebu: apply EBU R128...'
                     )
            cmd = (f'\n{count}\nSource: "{files}"\n'
                   f'Destination: "{outputfile}"\n\n'
                   f'[COMMAND]:\n{pass2}'
                   )

            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=count,
                         fsource=f'Source:  "{files}"',
                         destination=f'Destination: "{outputfile}"',
                         duration=duration,
                         end='',
                         )
            logwrite(cmd, '', self.logname)

            if not Loudnorm.OS == 'Windows':
                pass2 = shlex.split(pass2)
            with Popen(pass2,
                       stderr=subprocess.PIPE,
                       bufsize=1,
                       universal_newlines=True,
                       ) as proc2:

                for line2 in proc2.stderr:
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output=line2,
                                 duration=duration,
                                 status=0,
                                 )
                    if self.stop_work_thread:  # break first 'for' loop
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
                filedone.append(files)
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count='',
                             fsource='',
                             destination='',
                             duration=duration,
                             end='ok'
                             )
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT", msg=filedone)
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
