# -*- coding: UTF-8 -*-
"""
Name: long_processing_task.py
Porpose: Console to show logging messages during processing
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2022 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.14.2022
Code checker:
    - flake8: --ignore F821, W504, F401
    - pylint: --ignore E0602, E1101, C0415, E0401, C0103

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
from __future__ import unicode_literals
import time
import os
from shutil import move
from pubsub import pub
import wx
from videomass.vdms_dialogs.widget_utils import notification_area
from videomass.vdms_io.make_filelog import make_log_template
from videomass.vdms_threads.ydl_downloader import YdlDownloader
from videomass.vdms_threads.one_pass import OnePass
from videomass.vdms_threads.two_pass import TwoPass
from videomass.vdms_threads.two_pass_ebu import Loudnorm
from videomass.vdms_threads.picture_exporting import PicturesFromVideo
from videomass.vdms_threads.video_stabilization import VidStab
from videomass.vdms_threads.concat_demuxer import ConcatDemuxer
from videomass.vdms_utils.utils import (get_milliseconds,
                                        milliseconds2timeformat,
                                        )


def delete_file_source(flist, path):
    """
    Move whole files list to Videomass Trash folder
    after encoding process.
    """
    date = time.strftime('%H%M%S-%a_%d_%B_%Y')
    for name in flist:
        dest = os.path.join(path, f'{date}_{os.path.basename(name)}')
        move(name, dest)


def pairwise(iterable):
    """
    Return a zip object from iterable.
    This function is used by the update_display method.
    ----
    USE:

    after splitting ffmpeg's progress strings such as:
    output = "frame= 1178 fps=155 q=29.0 size=    2072kB time=00:00:39.02
              bitrate= 435.0kbits/s speed=5.15x  "
    in a list as:
    iterable = ['frame', '1178', 'fps', '155', 'q', '29.0', 'size', '2072kB',
                'time', '00:00:39.02', 'bitrate', '435.0kbits/s', speed',
                '5.15x']
    for x, y in pairwise(iterable):
        print(x,y)

    <https://stackoverflow.com/questions/5389507/iterating-over-every-
    two-elements-in-a-list>

    """
    itobj = iter(iterable)  # list_iterator object
    return zip(itobj, itobj)  # zip object pairs from list iterable object
# ----------------------------------------------------------------------#


class LogOut(wx.Panel):
    """
    displays a text control for the output logging, a progress bar
    and a progressive percentage text label. This panel is used
    in combination with separated threads for long processing tasks.
    It also implements stop and close buttons to stop the current
    process and close the panel at the end.

    """
    # used msg on text
    MSG_done = _('[Videomass]: SUCCESS !')
    MSG_failed = _('[Videomass]: FAILED !')
    MSG_taskfailed = _('Sorry, all task failed !')
    MSG_fatalerror = _("The process was stopped due to a fatal error.")
    MSG_interrupted = _('Interrupted Process !')
    MSG_completed = _('Successfully completed !')
    MSG_unfinished = _('Not everything was successful.')

    WHITE = '#fbf4f4'  # white for background status bar
    BLACK = '#060505'  # black for background status bar
    # ------------------------------------------------------------------#

    def __init__(self, parent):
        """
        In the 'previous' attribute is stored an ID string used to
        recover the previous panel from which the process is started.
        The 'logname' attribute is the name_of_panel.log file in which
        log messages will be written

        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.parent = parent  # main frame
        self.thread_type = None  # the instantiated thread
        self.time_remaining = True  # create time remaining progress
        self.abort = False  # if True set to abort current process
        self.error = False  # if True, all the tasks was failed
        self.previus = None  # panel name from which it starts
        self.logname = None  # log pathname, None otherwise
        self.result = []  # result of the final process
        self.count = 0  # keeps track of the counts (see `update_count`)
        self.clr = self.appdata['icontheme'][1]

        wx.Panel.__init__(self, parent=parent)

        infolbl = _("Process log:")
        lbl = wx.StaticText(self, label=infolbl)
        if self.appdata['ostype'] != 'Darwin':
            lbl.SetLabelMarkup(f"<b>{infolbl}</b>")
        self.txtout = wx.TextCtrl(self, wx.ID_ANY, "",
                                  style=wx.TE_MULTILINE |
                                  wx.TE_READONLY |
                                  wx.TE_RICH2
                                  )
        self.ckbx_text = wx.CheckBox(self, wx.ID_ANY, (_("Suppress excess "
                                                         "output")))
        self.barprog = wx.Gauge(self, wx.ID_ANY, range=0)
        self.labperc = wx.StaticText(self, label="")
        self.button_stop = wx.Button(self, wx.ID_STOP, _("Abort"))
        self.button_close = wx.Button(self, wx.ID_CLOSE, "")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((0, 10))
        sizer.Add(lbl, 0, wx.ALL, 5)
        sizer.Add(self.txtout, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.ckbx_text, 0, wx.ALL, 5)
        sizer.Add(self.barprog, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.labperc, 0, wx.ALL, 5)
        # grid = wx.GridSizer(1, 2, 0, 0)
        grid = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(grid, 0, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=0)
        grid.Add(self.button_stop, 0, wx.EXPAND | wx.ALL, 5)
        grid.Add(self.button_close, 0, wx.EXPAND | wx.ALL, 5)
        # set_properties:
        self.txtout.SetBackgroundColour(self.clr['BACKGRD'])
        self.ckbx_text.SetToolTip(_('If activated, hides some '
                                    'output messages.'))
        self.button_stop.SetToolTip(_("Stops current process"))
        self.SetSizerAndFit(sizer)
        # bind
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.button_stop)
        self.Bind(wx.EVT_BUTTON, self.on_close, self.button_close)

        # ------------------------------------------
        self.button_stop.Enable(True)
        self.button_close.Enable(False)

        pub.subscribe(self.downloader_activity, "UPDATE_YDL_EVT")
        pub.subscribe(self.update_display, "UPDATE_EVT")
        pub.subscribe(self.update_count, "COUNT_EVT")
        pub.subscribe(self.end_proc, "END_EVT")
    # ----------------------------------------------------------------------

    def topic_thread(self, panel, varargs, duration, time_seq):
        """
        Thread redirection
        varargs: type tuple data object
        duration: total duration or partial if set time_seq
        """
        self.previus = panel  # stores the panel from which it starts

        if varargs[0] == 'Viewing last log':
            self.button_stop.Enable(False)
            self.button_close.Enable(True)
            return

        self.txtout.Clear()
        self.labperc.SetLabel('')

        self.logname = make_log_template(varargs[8], self.appdata['logdir'])

        if varargs[0] == 'onepass':  # from Audio/Video Conv.
            self.thread_type = OnePass(varargs, duration,
                                       self.logname, time_seq,
                                       )
        elif varargs[0] == 'twopass':  # from Video Conv.
            self.thread_type = TwoPass(varargs, duration,
                                       self.logname, time_seq
                                       )
        elif varargs[0] == 'two pass EBU':  # from Audio/Video Conv.
            self.thread_type = Loudnorm(varargs, duration,
                                        self.logname, time_seq
                                        )
        elif varargs[0] == 'savepictures':
            self.time_remaining = False
            self.thread_type = PicturesFromVideo(varargs, duration,
                                                 self.logname, time_seq
                                                 )
        elif varargs[0] == 'libvidstab':  # from Audio/Video Conv.
            self.thread_type = VidStab(varargs, duration,
                                       self.logname, time_seq
                                       )
        elif varargs[0] == 'concat_demuxer':  # from Concatenation Demuxer
            self.time_remaining = False
            self.thread_type = ConcatDemuxer(varargs, duration,
                                             self.logname,
                                             )
        elif varargs[0] == 'youtube_dl downloading':  # as import youtube_dl
            self.time_remaining = False
            self.ckbx_text.Hide()
            self.barprog.Hide()
            self.thread_type = YdlDownloader(varargs, self.logname)
    # ----------------------------------------------------------------------

    def downloader_activity(self, output, duration, status):
        """
        Receiving output messages from youtube_dl library via
        pubsub "UPDATE_YDL_EVT" .
        """
        if status == 'ERROR':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['ERR0']))
            self.txtout.AppendText(f'{output}\n')
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['FAILED']))
            self.txtout.AppendText(f"{LogOut.MSG_failed}\n")
            self.result.append('failed')

        elif status == 'WARNING':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['WARN']))
            self.txtout.AppendText(f'{output}\n')

        elif status == 'DEBUG':
            if '[download] Destination' in output:
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['DEBUG']))
                self.txtout.AppendText(f'{output}\n')

            elif '[info]' in output:
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['INFO']))
                self.txtout.AppendText(f'{output}\n')

            elif '[download]' not in output:
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT1']))
                self.txtout.AppendText(f'{output}\n')
                with open(self.logname, "a", encoding='utf8') as logerr:
                    logerr.write(f"[{self.appdata['downloader'].upper()}]: "
                                 f"{status} > {output}\n")

        elif status == 'DOWNLOAD':
            perc = duration['_percent_str']
            tbytes = duration['_total_bytes_str']
            speed = duration['_speed_str']
            eta = duration['_eta_str']
            self.labperc.SetLabel(f'Downloading... {perc} of '
                                  f'{tbytes} at {speed} ETA {eta}')

        elif status == 'FINISHED':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT1']))
            self.txtout.AppendText(f'{duration}\n')

        if status in ['ERROR', 'WARNING']:
            with open(self.logname, "a", encoding='utf8') as logerr:
                logerr.write(f"[{self.appdata['downloader'].upper()}]: "
                             f"{output}\n")
    # ---------------------------------------------------------------------#

    def update_display(self, output, duration, status):
        """
        Receive message from thread of the second loops process
        by wxCallafter and pubsub UPDATE_EVT.
        The received 'output' is parsed for calculate the bar
        progress value, percentage label and errors management.
        This method can be used even for non-loop threads.

        NOTE: During conversion the ffmpeg errors do not stop all
              others tasks, if an error occurred it will be marked
              with 'failed' but continue; if it has finished without
              errors it will be marked with 'done' on update_count
              method. Since not all ffmpeg messages are errors, sometimes
              it happens to see more output marked with yellow color.

        This strategy consists first of capturing all the output and
        marking it in yellow, then in capturing the error if present,
        but exiting immediately after the function.

        """
        # if self.ckbx_text.IsChecked(): #ffmpeg output messages in real time:
        #    self.txtout.AppendText(output)

        if not status == 0:  # error, exit status of the p.wait
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['ERR1']))
            self.txtout.AppendText(f"{LogOut.MSG_failed}\n")
            self.result.append('failed')
            return  # must be return here

        if 'time=' in output:  # ...in processing
            i = output.index('time=') + 5
            pos = output[i:].split()[0]
            ms = get_milliseconds(pos)

            if ms > duration:
                self.barprog.SetValue(duration)
            else:
                self.barprog.SetValue(ms)

            percentage = round((ms / duration) * 100 if duration != 0 else 100)
            out = [a for a in "=".join(output.split()).split('=') if a]
            ffprog = []
            for x, y in pairwise(out):
                ffprog.append(f"{x}: {y} | ")

            if self.time_remaining is True:
                if 'speed=' in output:
                    try:
                        s = output.split()[-1].strip()
                        speed = s.split('=')[1].split('x')[0]
                        res = (duration - ms) / float(speed)
                        remaining = milliseconds2timeformat(round(res))
                        eta = f"ETA: {remaining} |"
                    except IndexError:
                        eta = f"ETA: N/A |"
                else:
                    eta = ""
            else:
                eta = ""
            self.labperc.SetLabel(f"Processing... {str(int(percentage))}% | "
                                  f"{''.join(ffprog)} {eta}"
                                  )
            del output, duration

        else:  # append all others lines on the textctrl and log file
            if not self.ckbx_text.IsChecked():  # not print the output
                if [x for x in ('info', 'Info') if x in output]:
                    self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['INFO']))
                    self.txtout.AppendText(f'{output}')

                elif [x for x in ('Failed', 'failed', 'Error', 'error')
                      if x in output]:
                    self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['ERR0']))
                    self.txtout.AppendText(f'{output}')

                elif [x for x in ('warning', 'Warning') if x in output]:
                    self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['WARN']))
                    self.txtout.AppendText(f'{output}')

                else:
                    self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT1']))
                    self.txtout.AppendText(f'{output}')

            with open(self.logname, "a", encoding='utf8') as logerr:
                logerr.write(f"[FFMPEG]: {output}")
    # ----------------------------------------------------------------------

    def update_count(self, count, fsource, destination, duration, end):
        """
        Receive message from first 'for' loop in the thread process.
        This method can be used even for non-loop threads.

        """
        if end == 'ok':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['SUCCESS']))
            self.txtout.AppendText(f"{LogOut.MSG_done}\n")
            # set final values for percentage, time and ETA
            if self.time_remaining is True:
                newlab = self.labperc.GetLabel().split('|')
                for idx, ele in enumerate(self.labperc.GetLabel().split('|')):
                    if 'Processing...' in ele:
                        newlab[idx] = 'Processing... 100%'
                    if ' time:' in ele:
                        timefrm = milliseconds2timeformat(duration)
                        newlab[idx] = (f' time: {str(timefrm)}')
                    if ' ETA:' in ele:
                        newlab[idx] = ' ETA: 00:00:00.000'
                self.labperc.SetLabel("|".join(newlab))
            return

        # if STATUS_ERROR == 1:
        if end == 'error':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['WARN']))
            self.txtout.AppendText(f'\n{count}\n')
            self.error = True
        else:
            self.barprog.SetRange(duration)  # set overall duration range
            self.barprog.SetValue(0)  # reset bar progress
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT0']))
            self.txtout.AppendText(f'\n{count}\n')
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['DEBUG']))
            self.txtout.AppendText(f'{fsource}\n')
            if destination:
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['DEBUG']))
                self.txtout.AppendText(f'{destination}\n')

        self.count += 1
    # ----------------------------------------------------------------------

    def end_proc(self, msg):
        """
        At the end of the process
        """
        if self.error is True:
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT0']))
            self.txtout.AppendText(f"\n{LogOut.MSG_fatalerror}\n")
            notification_area(_("Fatal Error !"), LogOut.MSG_fatalerror,
                              wx.ICON_ERROR)

        elif self.abort is True:
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['ABORT']))
            self.txtout.AppendText(f"\n{LogOut.MSG_interrupted}\n")

        else:
            if not self.result:
                endmsg = LogOut.MSG_completed
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT0']))
                notification_area(endmsg, _("Get your files at the "
                                            "destination you specified"),
                                  wx.ICON_INFORMATION,
                                  )
            else:
                if len(self.result) == self.count:
                    endmsg = LogOut.MSG_taskfailed
                    self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT0']))
                    notification_area(endmsg, _("Check the current output "
                                                "or read the related log "
                                                "file for more information."),
                                      wx.ICON_ERROR,)
                else:
                    endmsg = LogOut.MSG_unfinished
                    self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT0']))
                    notification_area(endmsg, _("Check the current output "
                                                "or read the related log "
                                                "file for more information."),
                                      wx.ICON_WARNING, timeout=10)

            self.parent.statusbar_msg(_('...Finished'), None)
            self.txtout.AppendText(f"\n{endmsg}\n")
            self.barprog.SetValue(0)

            if msg:  # move processed files to Videomass trash folder
                if self.appdata["move_file_to_trash"] is True:
                    if not os.path.exists(self.appdata["trashfolder"]):
                        if not os.path.isdir(self.appdata["trashfolder"]):
                            os.mkdir(self.appdata["trashfolder"], mode=0o777)
                    delete_file_source(msg, self.appdata["trashfolder"])

        self.txtout.AppendText('\n')
        self.button_stop.Enable(False)
        self.button_close.Enable(True)
        self.thread_type = None
    # ----------------------------------------------------------------------

    def on_stop(self, event):
        """
        The user change idea and was stop process
        """
        self.thread_type.stop()
        self.parent.statusbar_msg(_("wait... I'm aborting"), 'GOLDENROD',
                                  LogOut.WHITE)
        self.thread_type.join()
        self.parent.statusbar_msg(_("...Interrupted"), None)
        self.abort = True

        event.Skip()
    # ----------------------------------------------------------------------

    def on_close(self, event):
        """
        close dialog and retrieve at previusly panel

        """
        if not self.logname:  # only read mod is shown
            self.ckbx_text.Show()
            self.button_stop.Enable(True)
            self.button_close.Enable(False)
            self.parent.panelShown(self.previus)  # retrieve at previusly panel

        if self.thread_type is not None:
            if wx.MessageBox(_('There are still processes running.. if you '
                               'want to stop them, use the "Abort" button.\n\n'
                               'Do you want to kill application?'),
                             _('Please confirm'),
                             wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return
            self.parent.on_Kill()

        # reset all before close
        self.logname = None
        self.ckbx_text.Show()
        self.button_stop.Enable(True)
        self.button_close.Enable(False)
        self.thread_type = None
        self.abort = False
        self.error = False
        self.result.clear()
        self.count = 0
        if not self.barprog.IsShown():
            self.barprog.Show()  # restoring progress bar if hidden
        self.time_remaining = True  # restoring time remaining display
        # self.txtout.Clear()
        # self.labperc.SetLabel('')
        self.parent.panelShown(self.previus)  # retrieve at previusly panel
        # event.Skip()
