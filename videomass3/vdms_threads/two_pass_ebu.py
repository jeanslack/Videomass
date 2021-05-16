# -*- coding: UTF-8 -*-
"""
Name: two_pass_EBU.py
Porpose: FFmpeg long processing task on 2 pass with EBU normalization
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: May.09.2021
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
import time
import itertools
import subprocess
import platform
import wx
from pubsub import pub
if not platform.system() == 'Windows':
    import shlex


def logwrite(cmd, sterr, logname, logdir):
    """
    writes ffmpeg commands and status error during threads below
    """
    if sterr:
        apnd = "...%s\n\n" % (sterr)
    else:
        apnd = "%s\n\n" % (cmd)

    with open(os.path.join(logdir, logname), "a", encoding='utf8') as log:
        log.write(apnd)


# ------------------------------ THREADS -------------------------------#
"""
NOTE MS Windows:

subprocess.STARTUPINFO()

https://stackoverflow.com/questions/1813872/running-
a-process-in-pythonw-with-popen-without-a-console?lq=1>

NOTE capturing output in real-time (Windows, Unix):

https://stackoverflow.com/questions/1388753/how-to-get-output-
from-subprocess-popen-proc-stdout-readline-blocks-no-dat?rq=1
"""


class Loudnorm(Thread):
    """
    Like `TwoPass_Thread` but execute -loudnorm parsing from first
    pass and has definitions to apply on second pass.

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    appdata = get.appset
    OS = appdata['ostype']
    SUFFIX = '' if appdata['filesuffix'] == 'none' else appdata['filesuffix']
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
            outputfile = os.path.join(folders, '%s%s.%s' % (filename,
                                                            Loudnorm.SUFFIX,
                                                            outext
                                                            ))

            # --------------- first pass
            pass1 = ('"{0}" -nostdin -loglevel info -stats '
                     '-hide_banner {1} -i "{2}" {3} {4} -y '
                     '{5}'.format(Loudnorm.appdata['ffmpeg_bin'],
                                  self.time_seq,
                                  files,
                                  self.passlist[0],
                                  Loudnorm.appdata['ffthreads'],
                                  self.nul,
                                  ))
            self.count += 1
            count = ('File %s/%s - Pass One\n '
                     'Loudnorm ebu: Getting statistics for '
                     'measurements...' % (self.count, self.countmax))
            cmd = ('%s\nSource: "%s"\nDestination: "%s"\n\n'
                   '[COMMAND]:\n%s' % (count, files, self.nul, pass1))

            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=count,
                         fsource='Source:  "%s"' % files,
                         destination='Destination: "%s"' % self.nul,
                         duration=duration,
                         end='',
                         )
            logwrite(cmd,
                     '',
                     self.logname,
                     Loudnorm.appdata['logdir']
                     )  # write n/n + command only

            if not Loudnorm.OS == 'Windows':
                pass1 = shlex.split(pass1)
                info = None
            else:   # Hide subprocess window on MS Windows
                info = subprocess.STARTUPINFO()
                info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            try:
                with subprocess.Popen(pass1,
                                      stderr=subprocess.PIPE,
                                      bufsize=1,
                                      universal_newlines=True,
                                      startupinfo=info,) as proc1:

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
                                     output=line,
                                     duration=duration,
                                     status=proc1.wait(),
                                     )
                        logwrite('',
                                 "Exit status: %s" % proc1.wait(),
                                 self.logname,
                                 Loudnorm.appdata['logdir'],
                                 )  # append exit error number
                        break

            except (OSError, FileNotFoundError) as err:
                excepterr = "%s\n  %s" % (err, Loudnorm.NOT_EXIST_MSG)
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
                             duration='',
                             end='ok'
                             )
            # --------------- second pass ----------------#
            filters = ('%s:measured_I=%s:measured_LRA=%s:measured_TP=%s:'
                       'measured_thresh=%s:offset=%s:linear=true:dual_mono='
                       'true' % (self.passlist[2],
                                 summary["Input Integrated:"],
                                 summary["Input LRA:"],
                                 summary["Input True Peak:"],
                                 summary["Input Threshold:"],
                                 summary["Target Offset:"]
                                 )
                       )
            time.sleep(.5)

            pass2 = ('"{0}" -nostdin -loglevel info -stats -hide_banner {1} '
                     '-i "{2}" {3} -filter:a:{9} {4} {5} -y "{6}/{7}{10}.{8}" '
                     ''.format(Loudnorm.appdata['ffmpeg_bin'],
                               self.time_seq,
                               files,
                               self.passlist[1],
                               filters,
                               Loudnorm.appdata['ffthreads'],
                               folders,
                               filename,
                               outext,
                               self.audio_outmap[1],
                               Loudnorm.SUFFIX,
                               ))

            count = ('File %s/%s - Pass Two\nLoudnorm ebu: '
                     'apply EBU R128... ' % (self.count, self.countmax))
            cmd = ('\n%s\nSource: "%s"\nDestination: "%s"\n\n'
                   '[COMMAND]:\n%s' % (count, files, outputfile, pass2))

            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=count,
                         fsource='Source:  "%s"' % files,
                         destination='Destination: "%s"' % outputfile,
                         duration=duration,
                         end='',
                         )
            logwrite(cmd, '', self.logname, Loudnorm.appdata['logdir'])

            if not Loudnorm.OS == 'Windows':
                pass2 = shlex.split(pass2)
                info = None
            else:  # Hide subprocess window on MS Windows
                info = subprocess.STARTUPINFO()
                info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            with subprocess.Popen(pass2,
                                  stderr=subprocess.PIPE,
                                  bufsize=1,
                                  universal_newlines=True,
                                  startupinfo=info,) as proc2:

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
                                 output=line,
                                 duration=duration,
                                 status=proc2.wait(),
                                 )
                    logwrite('',
                             "Exit status: %s" % proc2.wait(),
                             self.logname,
                             Loudnorm.appdata['logdir'],
                             )  # append exit error number

            if self.stop_work_thread:  # break first 'for' loop
                proc2.terminate()
                break  # fermo il ciclo for, altrimenti passa avanti

            if proc2.wait() == 0:  # will add '..terminated' to txtctrl
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count='',
                             fsource='',
                             destination='',
                             duration='',
                             end='ok'
                             )
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT")
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
