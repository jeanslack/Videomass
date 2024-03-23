# -*- coding: UTF-8 -*-
"""
Name: ffmpeg.py
Porpose: FFmpeg long processing task
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Mar.22.2024
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
import subprocess
import platform
import wx
from pubsub import pub
from videomass.vdms_utils.utils import Popen
from videomass.vdms_io.make_filelog import logwrite
if not platform.system() == 'Windows':
    import shlex


def one_pass(*args, **kwa):
    """
    Command builder for first pass of two
    """
    nul = 'NUL' if platform.system() == 'Windows' else '/dev/null'
    pass1 = (f'"{kwa["ffmpeg_cmd"]}" '
             f'{kwa["ffmpeg_default_args"]} '
             f'{kwa.get("pre-input-1", "")} '
             f'{kwa["start-time"]} '
             f'-i "{kwa["fsrc"]}" '
             f'{kwa["end-time"]} '
             f'{kwa["args"][0]} '
             f'{nul}'
             )
    count1 = (f'File {args[0]}/{args[1]} - Pass One\n'
              f'Source: "{kwa["fsrc"]}"\nDestination: "{nul}"')
    stamp1 = f'{count1}\n\n[COMMAND]:\n{pass1}'

    if not platform.system() == 'Windows':
        pass1 = shlex.split(pass1)

    return {'pass1': pass1, 'count1': count1, 'stamp1': stamp1}
# ----------------------------------------------------------------------


def two_pass(*args, **kwa):
    """
    Command builder for second pass of two
    """
    pass2 = (f'"{kwa["ffmpeg_cmd"]}" '
             f'{kwa["ffmpeg_default_args"]} '
             f'{kwa.get("pre-input-2", "")} '
             f'{kwa["start-time"]} '
             f'-i "{kwa["fsrc"]}" '
             f'{kwa["end-time"]} '
             f'{kwa["args"][1]} '
             f'{kwa.get("volume", "")} '
             f'"{kwa["fdest"]}"'
             )
    count2 = (f'File {args[0]}/{args[1]} - Pass Two\n'
              f'Source: "{kwa["fsrc"]}"\nDestination: "{kwa["fdest"]}"')
    stamp2 = f'\n{count2}\n\n[COMMAND]:\n{pass2}'

    if not platform.system() == 'Windows':
        pass2 = shlex.split(pass2)

    return {'pass2': pass2, 'count2': count2, 'stamp2': stamp2}
# ----------------------------------------------------------------------


def one_pass_stabilizer(*args, **kwa):
    """
    Command builder for one pass video stabilizer
    """
    nul = 'NUL' if platform.system() == 'Windows' else '/dev/null'
    pass1 = (f'"{kwa["ffmpeg_cmd"]}" '
             f'{kwa["ffmpeg_default_args"]} '
             f'{kwa.get("pre-input-1", "")} '
             f'{kwa["start-time"]} '
             f'-i "{kwa["fsrc"]}" '
             f'{kwa["end-time"]} '
             f'{kwa["args"][0]} '
             f'{nul}'
             )
    count1 = (f'File {args[0]}/{args[1]} - Pass One\n'
              f'Detecting statistics for measurements...\n\nSource: '
              f'"{kwa["fsrc"]}"\nDestination: "{nul}"')
    stamp1 = f'{count1}\n\n[COMMAND]:\n{pass1}'

    if not platform.system() == 'Windows':
        pass1 = shlex.split(pass1)

    return {'pass1': pass1, 'count1': count1, 'stamp1': stamp1}
# ----------------------------------------------------------------------


def two_pass_stabilizer(*args, **kwa):
    """
    Command builder for two pass video stabilizer
    """
    pass2 = (f'"{kwa["ffmpeg_cmd"]}" '
             f'{kwa["ffmpeg_default_args"]} '
             f'{kwa.get("pre-input-2", "")} '
             f'{kwa["start-time"]} '
             f'-i "{kwa["fsrc"]}" '
             f'{kwa["end-time"]} '
             f'{kwa["args"][1]} '
             f'{kwa.get("volume", "")} '
             f'"{kwa["fdest"]}"'
             )
    count2 = (f'File {args[0]}/{args[1]} - Pass Two\n'
              f'Application of Audio/Video filters...\n\nSource: '
              f'"{kwa["fsrc"]}"\nDestination: "{kwa["fdest"]}"')
    stamp2 = f'\n{count2}\n\n[COMMAND]:\n{pass2}'

    if not platform.system() == 'Windows':
        pass2 = shlex.split(pass2)

    return {'pass2': pass2, 'count2': count2, 'stamp2': stamp2}
# ----------------------------------------------------------------------


def simple_one_pass(*args, **kwa):
    """
    Command builder for one pass ebu
    """
    pass1 = (f'"{kwa["ffmpeg_cmd"]}" '
             f'{kwa["ffmpeg_default_args"]} '
             f'{kwa.get("pre-input-1", "")} '
             f'{kwa["start-time"]} '
             f'-i "{kwa["fsrc"]}" '
             f'{kwa["end-time"]} '
             f'{kwa["args"][0]} '
             f'{kwa.get("volume", "")} '
             f'"{kwa["fdest"]}"'
             )
    count1 = (f'File {args[0]}/{args[1]}\nSource: '
              f'"{kwa["fsrc"]}"\nDestination: "{kwa["fdest"]}')
    stamp1 = f'{count1}\n\n[COMMAND]:\n{pass1}'

    if not platform.system() == 'Windows':
        pass1 = shlex.split(pass1)

    return {'pass1': pass1, 'count1': count1, 'stamp1': stamp1}
# ----------------------------------------------------------------------


def one_pass_ebu(*args, **kwa):
    """
    Command builder for one pass ebu
    """
    nul = 'NUL' if platform.system() == 'Windows' else '/dev/null'
    pass1 = (f'"{kwa["ffmpeg_cmd"]}" '
             f'{kwa["ffmpeg_default_args"]} '
             f'{kwa.get("pre-input-1", "")} '
             f'{kwa["start-time"]} '
             f'-i "{kwa["fsrc"]}" '
             f'{kwa["end-time"]} '
             f'{kwa["args"][0]} '
             f'{nul}'
             )
    count1 = (f'File {args[0]}/{args[1]} - Pass One\n'
              f'Detecting statistics for measurements...\n\nSource: '
              f'"{kwa["fsrc"]}"\nDestination: "{nul}"')
    stamp1 = f'{count1}\n\n[COMMAND]:\n{pass1}'

    if not platform.system() == 'Windows':
        pass1 = shlex.split(pass1)

    summary = {'Input Integrated:': None, 'Input True Peak:': None,
               'Input LRA:': None, 'Input Threshold:': None,
               'Output Integrated:': None, 'Output True Peak:': None,
               'Output LRA:': None, 'Output Threshold:': None,
               'Normalization Type:': None, 'Target Offset:': None
               }
    return {'pass1': pass1, 'count1': count1,
            'stamp1': stamp1, 'summary': summary}
# ----------------------------------------------------------------------


def two_pass_ebu(*args, **kwa):
    """
    Command builder for two pass ebu
    """
    pass2 = (f'"{kwa["ffmpeg_cmd"]}" '
             f'{kwa["ffmpeg_default_args"]} '
             f'{kwa.get("pre-input-2", "")} '
             f'{kwa["start-time"]} '
             f'-i "{kwa["fsrc"]}" '
             f'{kwa["end-time"]} '
             f'{kwa["args"][1]} '
             f'-filter:a:{kwa["audiomap"][1]} '
             f'{args[2]} '
             f'"{kwa["fdest"]}"'
             )
    count2 = (f'File {args[0]}/{args[1]} - Pass Two\n'
              f'Application of Audio/Video filters...\n\nSource: '
              f'"{kwa["fsrc"]}"\nDestination: "{kwa["fdest"]}"')
    stamp2 = f'\n{count2}\n\n[COMMAND]:\n{pass2}'

    if not platform.system() == 'Windows':
        pass2 = shlex.split(pass2)

    return {'pass2': pass2, 'count2': count2, 'stamp2': stamp2}
# ----------------------------------------------------------------------


class FFmpeg(Thread):
    """
    This class performs a long processing task in a separate thread.
    It is able to pipe up to two FFmpeg subprocesses to execute
    tasks in succession using command concatenation.

    NOTE capturing output in real-time (Windows, Unix):
    https://stackoverflow.com/questions/1388753/how-to-get-output-
    from-subprocess-popen-proc-stdout-readline-blocks-no-dat?rq=1

    """
    NOT_EXIST_MSG = _("Is 'ffmpeg' installed on your system?")

    def __init__(self, *args):
        """
        Called from `long_processing_task.topic_thread`.
        Also see `main_frame.switch_to_processing`.

        """
        self.stop_work_thread = False  # process terminate
        self.count = 0  # count for loop
        self.logfile = args[0]  # log filename
        self.kwargs = args[1]  # it is a list of dictionaries
        self.nargs = len(self.kwargs)  # how many items...

        Thread.__init__(self)
        self.start()

    def run(self):
        """
        Subprocess initialize thread.
        """
        filedone = []
        for kwa in self.kwargs:
            self.count += 1
            if kwa['type'] == 'onepass':
                model = simple_one_pass(self.count, self.nargs, **kwa)

            elif kwa['type'] == 'two pass EBU':
                model = one_pass_ebu(self.count, self.nargs, **kwa)

            elif kwa['type'] == 'libvidstab':
                model = one_pass_stabilizer(self.count, self.nargs, **kwa)

            elif kwa['type'] == 'twopass':
                model = one_pass(self.count, self.nargs, **kwa)

            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=model['count1'],
                         duration=kwa['duration'],
                         end='',
                         )
            logwrite(model['stamp1'], '', self.logfile)
            try:
                with Popen(model['pass1'],
                           stderr=subprocess.PIPE,
                           bufsize=1,
                           universal_newlines=True,
                           encoding='utf8',
                           ) as proc1:

                    for line in proc1.stderr:
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output=line,
                                     duration=kwa['duration'],
                                     status=0
                                     )
                        if self.stop_work_thread:  # break first 'for' loop
                            proc1.terminate()
                            break

                        if kwa["type"] == 'two pass EBU':
                            summary = model['summary']
                            for k in summary:
                                if line.startswith(k):
                                    summary[k] = line.split(':')[1].split()[0]

                    if proc1.wait():  # will add '..failed' to txtctrl
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output='',
                                     duration=kwa['duration'],
                                     status=proc1.wait(),
                                     )
                        logwrite('',
                                 f"Exit status: {proc1.wait()}",
                                 self.logfile,
                                 )  # append exit error number
                        break

            except (OSError, FileNotFoundError) as err:
                excepterr = f"{err}\n  {FFmpeg.NOT_EXIST_MSG}"
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count=excepterr,
                             duration=0,
                             end='error'
                             )
                break

            if self.stop_work_thread:  # break first 'for' loop
                proc1.terminate()
                break  # stop for loop

            if proc1.wait() == 0:  # will add '..terminated' to txtctrl
                if len(kwa["args"]) == 1:
                    filedone.append(kwa["fsrc"])
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count='',
                             duration=kwa['duration'],
                             end='Done'
                             )

            if not kwa["args"][1]:
                continue

            # --------------- second pass ----------------#
            if kwa["type"] == 'two pass EBU':
                filters = (f'{kwa["EBU"]}'
                           f':measured_I={summary["Input Integrated:"]}'
                           f':measured_LRA={summary["Input LRA:"]}'
                           f':measured_TP={summary["Input True Peak:"]}'
                           f':measured_thresh={summary["Input Threshold:"]}'
                           f':offset={summary["Target Offset:"]}'
                           f':linear=true:dual_mono=true'
                           )
                model = two_pass_ebu(self.count, self.nargs, filters, **kwa)
                time.sleep(.5)

            elif kwa['type'] == 'libvidstab':
                model = two_pass_stabilizer(self.count, self.nargs, **kwa)

            elif kwa['type'] == 'twopass':
                model = two_pass(self.count, self.nargs, **kwa)

            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=model['count2'],
                         duration=kwa['duration'],
                         end='',
                         )
            logwrite(model['stamp2'], '', self.logfile)

            with Popen(model['pass2'],
                       stderr=subprocess.PIPE,
                       bufsize=1,
                       universal_newlines=True,
                       encoding='utf8',
                       ) as proc2:

                for line2 in proc2.stderr:
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output=line2,
                                 duration=kwa['duration'],
                                 status=0,
                                 )
                    if self.stop_work_thread:  # break first 'for' loop
                        proc2.terminate()
                        break

                if proc2.wait():  # will add '..failed' to txtctrl
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output='',
                                 duration=kwa['duration'],
                                 status=proc2.wait(),
                                 )
                    logwrite('',
                             f"Exit status: {proc2.wait()}",
                             self.logfile,
                             )  # append exit error number

            if self.stop_work_thread:  # break first 'for' loop
                proc2.terminate()
                break  # stop for loop

            if proc2.wait() == 0:  # will add '..terminated' to txtctrl
                filedone.append(kwa["fsrc"])
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count='',
                             duration=kwa['duration'],
                             end='Done'
                             )
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT", filetotrash=filedone)
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
