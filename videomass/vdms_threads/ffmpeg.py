# -*- coding: UTF-8 -*-
"""
Name: ffmpeg.py
Porpose: FFmpeg long processing task
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Aug.13.2025
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


def get_raw_cmdline_args(**kwa):
    """
    Return a list of raw command lines.
    """
    if kwa['type'] == 'One pass':
        model = simple_one_pass(1, 1, **kwa)

    elif kwa['type'] == 'Two pass EBU':
        model = one_pass_ebu(1, 1, **kwa)

    elif kwa['type'] == 'Two pass VIDSTAB':
        model = one_pass_stab(1, 1, **kwa)

    elif kwa['type'] == 'Two pass':
        model = one_pass(1, 1, **kwa)
    else:
        return None

    spl1 = model['stamp1'].split('\n')
    idx1 = spl1.index('[COMMAND]:') + 1
    cmd1 = spl1[idx1]

    if not kwa["args"][1]:
        return (cmd1,)

    if kwa["type"] == 'Two pass EBU':
        filters = (f'{kwa["EBU"]}'
                   f':measured_I=<?>'
                   f':measured_LRA=<?>'
                   f':measured_TP=<?>'
                   f':measured_thresh=<?>'
                   f':offset=<?>'
                   f':linear=true:dual_mono=true'
                   )
        model = two_pass_ebu(1, 1, filters, **kwa)

    elif kwa['type'] == 'Two pass VIDSTAB':
        model = two_pass_stab(1, 1, **kwa)

    elif kwa['type'] == 'Two pass':
        model = two_pass(1, 1, **kwa)

    spl2 = model['stamp2'].split('\n')
    idx2 = spl2.index('[COMMAND]:') + 1
    cmd2 = spl2[idx2]

    return cmd1, cmd2
# ----------------------------------------------------------------------


def ffmpeg_cmd_args():
    """
    Get ffmpeg command and default args
    """
    get = wx.GetApp()
    appdata = get.appset
    defargs = f'-y -stats -hide_banner {appdata["ffmpeg_loglev"]}'
    return {"ffmpeg_cmd": appdata["ffmpeg_cmd"],
            "ffmpeg-default-args": defargs}
# ----------------------------------------------------------------------


def one_pass(*args, **kwa):
    """
    Command builder for first pass of two
    """
    cmd = ffmpeg_cmd_args()
    nul = 'NUL' if platform.system() == 'Windows' else '/dev/null'
    pass1 = (f'"{cmd["ffmpeg_cmd"]}" '
             f'{cmd["ffmpeg-default-args"]} '
             f'{kwa.get("pre-input-1", "")} '
             f'{kwa["start-time"]} '
             f'-i "{kwa["source"]}" '
             f'{kwa["end-time"]} '
             f'{kwa["args"][0]} '
             f'{nul}'
             )
    count1 = (f'File {args[0]}/{args[1]} - Pass One\n'
              f'Source: "{kwa["source"]}"\nDestination: "{nul}"')
    stamp1 = f'{count1}\n\n[COMMAND]:\n{pass1}'

    if not platform.system() == 'Windows':
        pass1 = shlex.split(pass1)

    return {'pass1': pass1, 'count1': count1, 'stamp1': stamp1}
# ----------------------------------------------------------------------


def two_pass(*args, **kwa):
    """
    Command builder for second pass of two
    """
    cmd = ffmpeg_cmd_args()
    pass2 = (f'"{cmd["ffmpeg_cmd"]}" '
             f'{cmd["ffmpeg-default-args"]} '
             f'{kwa.get("pre-input-2", "")} '
             f'{kwa["start-time"]} '
             f'-i "{kwa["source"]}" '
             f'{kwa["end-time"]} '
             f'{kwa["args"][1]} '
             f'{kwa.get("volume", "")} '
             f'"{kwa["destination"]}"'
             )
    count2 = (f'File {args[0]}/{args[1]} - Pass Two\n'
              f'Source: "{kwa["source"]}"\nDestination: '
              f'"{kwa["destination"]}"'
              )
    stamp2 = f'\n{count2}\n\n[COMMAND]:\n{pass2}'

    if not platform.system() == 'Windows':
        pass2 = shlex.split(pass2)

    return {'pass2': pass2, 'count2': count2, 'stamp2': stamp2}
# ----------------------------------------------------------------------


def one_pass_stab(*args, **kwa):
    """
    Command builder for one pass video stabilizer
    """
    cmd = ffmpeg_cmd_args()
    nul = 'NUL' if platform.system() == 'Windows' else '/dev/null'
    pass1 = (f'"{cmd["ffmpeg_cmd"]}" '
             f'{cmd["ffmpeg-default-args"]} '
             f'{kwa.get("pre-input-1", "")} '
             f'{kwa["start-time"]} '
             f'-i "{kwa["source"]}" '
             f'{kwa["end-time"]} '
             f'{kwa["args"][0]} '
             f'{nul}'
             )
    count1 = (f'File {args[0]}/{args[1]} - Pass One\n'
              f'Detecting statistics for measurements...\n\nSource: '
              f'"{kwa["source"]}"\nDestination: "{nul}"')
    stamp1 = f'{count1}\n\n[COMMAND]:\n{pass1}'

    if not platform.system() == 'Windows':
        pass1 = shlex.split(pass1)

    return {'pass1': pass1, 'count1': count1, 'stamp1': stamp1}
# ----------------------------------------------------------------------


def two_pass_stab(*args, **kwa):
    """
    Command builder for two pass video stabilizer
    """
    cmd = ffmpeg_cmd_args()
    pass2 = (f'"{cmd["ffmpeg_cmd"]}" '
             f'{cmd["ffmpeg-default-args"]} '
             f'{kwa.get("pre-input-2", "")} '
             f'{kwa["start-time"]} '
             f'-i "{kwa["source"]}" '
             f'{kwa["end-time"]} '
             f'{kwa["args"][1]} '
             f'{kwa.get("volume", "")} '
             f'"{kwa["destination"]}"'
             )
    count2 = (f'File {args[0]}/{args[1]} - Pass Two\n'
              f'Application of Audio/Video filters...\n\nSource: '
              f'"{kwa["source"]}"\nDestination: "{kwa["destination"]}"')
    stamp2 = f'\n{count2}\n\n[COMMAND]:\n{pass2}'

    if not platform.system() == 'Windows':
        pass2 = shlex.split(pass2)

    return {'pass2': pass2, 'count2': count2, 'stamp2': stamp2}
# ----------------------------------------------------------------------


def simple_one_pass(*args, **kwa):
    """
    Command builder for one pass ebu
    """
    cmd = ffmpeg_cmd_args()
    pass1 = (f'"{cmd["ffmpeg_cmd"]}" '
             f'{cmd["ffmpeg-default-args"]} '
             f'{kwa.get("pre-input-1", "")} '
             f'{kwa["start-time"]} '
             f'-i "{kwa["source"]}" '
             f'{kwa["end-time"]} '
             f'{kwa["args"][0]} '
             f'{kwa.get("volume", "")} '
             f'"{kwa["destination"]}"'
             )
    count1 = (f'File {args[0]}/{args[1]}\nSource: '
              f'"{kwa["source"]}"\nDestination: "{kwa["destination"]}"')
    stamp1 = f'{count1}\n\n[COMMAND]:\n{pass1}'

    if not platform.system() == 'Windows':
        pass1 = shlex.split(pass1)

    return {'pass1': pass1, 'count1': count1, 'stamp1': stamp1}
# ----------------------------------------------------------------------


def one_pass_ebu(*args, **kwa):
    """
    Command builder for one pass ebu
    """
    cmd = ffmpeg_cmd_args()
    nul = 'NUL' if platform.system() == 'Windows' else '/dev/null'
    pass1 = (f'"{cmd["ffmpeg_cmd"]}" '
             f'{cmd["ffmpeg-default-args"]} '
             f'{kwa.get("pre-input-1", "")} '
             f'{kwa["start-time"]} '
             f'-i "{kwa["source"]}" '
             f'{kwa["end-time"]} '
             f'{kwa["args"][0]} '
             f'{nul}'
             )
    count1 = (f'File {args[0]}/{args[1]} - Pass One\n'
              f'Detecting statistics for measurements...\n\nSource: '
              f'"{kwa["source"]}"\nDestination: "{nul}"')
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
    cmd = ffmpeg_cmd_args()
    pass2 = (f'"{cmd["ffmpeg_cmd"]}" '
             f'{cmd["ffmpeg-default-args"]} '
             f'{kwa.get("pre-input-2", "")} '
             f'{kwa["start-time"]} '
             f'-i "{kwa["source"]}" '
             f'{kwa["end-time"]} '
             f'{kwa["args"][1]} '
             f'-filter:a:{kwa["audiomap"][1]} '
             f'{args[2]} '
             f'"{kwa["destination"]}"'
             )
    count2 = (f'File {args[0]}/{args[1]} - Pass Two\n'
              f'Application of Audio/Video filters...\n\nSource: '
              f'"{kwa["source"]}"\nDestination: "{kwa["destination"]}"')
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
    def __init__(self, *args):
        """
        Called from `long_processing_task.topic_thread`.
        Also see `main_frame.switch_to_processing`.

        """
        get = wx.GetApp()  # get data from bootstrap
        self.appdata = get.appset
        self.stop_work_thread = False  # set stop ffmpeg
        self.count = 0  # count for loop
        self.logfile = args[0]  # log filename
        self.kwargs = args[1]  # it is a list of dictionaries
        self.nargs = len(self.kwargs)  # how many items...

        Thread.__init__(self)
        self.start()

    def run(self):
        """
        Run the separated thread.
        """
        filedone = []
        for kwa in self.kwargs:
            self.count += 1
            if kwa['type'] == 'One pass':
                model = simple_one_pass(self.count, self.nargs, **kwa)

            elif kwa['type'] == 'Two pass EBU':
                model = one_pass_ebu(self.count, self.nargs, **kwa)

            elif kwa['type'] == 'Two pass VIDSTAB':
                model = one_pass_stab(self.count, self.nargs, **kwa)

            elif kwa['type'] == 'Two pass':
                model = one_pass(self.count, self.nargs, **kwa)
            else:
                return

            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=model['count1'],
                         duration=kwa['duration'],
                         end='CONTINUE',
                         )
            logwrite(model['stamp1'], '', self.logfile)
            try:
                with Popen(model['pass1'],
                           stderr=subprocess.PIPE,
                           stdin=subprocess.PIPE,
                           bufsize=1,
                           universal_newlines=True,
                           encoding=self.appdata['encoding'],
                           ) as proc1:

                    for line in proc1.stderr:
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output=line,
                                     duration=kwa['duration'],
                                     status=0
                                     )
                        if self.stop_work_thread:
                            proc1.stdin.write('q')  # stop ffmpeg
                            out = proc1.communicate()[1]
                            proc1.wait()
                            wx.CallAfter(pub.sendMessage,
                                         "UPDATE_EVT",
                                         output='STOP',
                                         duration=kwa['duration'],
                                         status=1,
                                         )
                            logwrite('', out, self.logfile)
                            time.sleep(.5)
                            wx.CallAfter(pub.sendMessage, "END_EVT",
                                         filetotrash=None)
                            return

                        if kwa["type"] == 'Two pass EBU':
                            summary = model['summary']
                            for k in summary:
                                if line.startswith(k):
                                    summary[k] = line.split(':')[1].split()[0]

                    if proc1.wait():  # ..Failed
                        out = proc1.communicate()[1]
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output='FAILED',
                                     duration=kwa['duration'],
                                     status=proc1.wait(),
                                     )
                        logwrite('', (f"[VIDEOMASS]: Error Exit Status: "
                                      f"{proc1.wait()} {out}"), self.logfile)
                        time.sleep(1)
                        continue

            except (OSError, FileNotFoundError) as err:
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count=err,
                             duration=0,
                             end='ERROR'
                             )
                logwrite('', err, self.logfile)
                break

            if proc1.wait() == 0:  # ..Finished
                if not kwa["args"][1]:
                    filedone.append(kwa["source"])
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count='',
                             duration=kwa['duration'],
                             end='DONE'
                             )

            if not kwa["args"][1]:
                continue

            # --------------- second pass ----------------#
            if kwa["type"] == 'Two pass EBU':
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

            elif kwa['type'] == 'Two pass VIDSTAB':
                model = two_pass_stab(self.count, self.nargs, **kwa)

            elif kwa['type'] == 'Two pass':
                model = two_pass(self.count, self.nargs, **kwa)

            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=model['count2'],
                         duration=kwa['duration'],
                         end='CONTINUE',
                         )
            logwrite(model['stamp2'], '', self.logfile)

            with Popen(model['pass2'],
                       stderr=subprocess.PIPE,
                       stdin=subprocess.PIPE,
                       bufsize=1,
                       universal_newlines=True,
                       encoding=self.appdata['encoding'],
                       ) as proc2:

                for line2 in proc2.stderr:
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output=line2,
                                 duration=kwa['duration'],
                                 status=0,
                                 )
                    if self.stop_work_thread:
                        proc2.stdin.write('q')  # stop ffmpeg
                        out = proc2.communicate()[1]
                        proc2.wait()
                        wx.CallAfter(pub.sendMessage,
                                     "UPDATE_EVT",
                                     output='STOP',
                                     duration=kwa['duration'],
                                     status=1,
                                     )
                        logwrite('', out, self.logfile)
                        time.sleep(.5)
                        wx.CallAfter(pub.sendMessage, "END_EVT",
                                     filetotrash=None)
                        return

                if proc2.wait():  # ..Failed
                    out = proc2.communicate()[1]
                    wx.CallAfter(pub.sendMessage,
                                 "UPDATE_EVT",
                                 output='FAILED',
                                 duration=kwa['duration'],
                                 status=proc2.wait(),
                                 )
                    logwrite('', (f"[VIDEOMASS]: Error Exit Status: "
                                  f"{proc2.wait()} {out}"), self.logfile)
                    time.sleep(1)
                    continue

            if proc2.wait() == 0:  # ..Finished
                filedone.append(kwa["source"])
                wx.CallAfter(pub.sendMessage,
                             "COUNT_EVT",
                             count='',
                             duration=kwa['duration'],
                             end='DONE'
                             )
        time.sleep(.5)
        wx.CallAfter(pub.sendMessage, "END_EVT", filetotrash=filedone)
    # --------------------------------------------------------------------#

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
