# -*- coding: UTF-8 -*-
"""
Name: long_processing_task.py
Porpose: Console to show logging messages during processing
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: May.09.2021 *-pycodestyle- compatible*
########################################################
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
import os
from pubsub import pub
import wx
from videomass.vdms_io.make_filelog import write_log
from videomass.vdms_threads.ydl_downloader import YdlDownloader
from videomass.vdms_threads.one_pass import OnePass
from videomass.vdms_threads.two_pass import TwoPass
from videomass.vdms_threads.two_pass_ebu import Loudnorm
from videomass.vdms_threads.picture_exporting import PicturesFromVideo
from videomass.vdms_threads.video_stabilization import VidStab
from videomass.vdms_threads.concat_demuxer import ConcatDemuxer
from videomass.vdms_utils.utils import get_milliseconds


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
    # get videomass wx.App attribute
    get = wx.GetApp()
    appdata = get.appset

    # used msg on text
    MSG_done = _('[Videomass]: SUCCESS !\n')
    MSG_failed = _('[Videomass]: FAILED !\n')
    MSG_taskfailed = _('\n[Videomass]: Sorry, task failed !\n')
    MSG_interrupted = _('\n[Videomass]: Interrupted Process !\n')
    MSG_completed = _('\n[Videomass]: Successfully completed !\n')
    MSG_unfinished = _('\n[Videomass]: completed, but not everything '
                       'was successful.\n')

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
        self.parent = parent  # main frame
        self.thread_type = None  # the instantiated thread
        self.abort = False  # if True set to abort current process
        self.error = False  # if True, all the tasks was failed
        self.previus = None  # panel name from which it starts
        self.logname = None  # example: AV_conversions.log
        self.result = None  # result of the final process
        self.clr = LogOut.appdata['icontheme'][1]

        wx.Panel.__init__(self, parent=parent)

        infolbl = _("Process log:")
        lbl = wx.StaticText(self, label=infolbl)
        if LogOut.appdata['ostype'] != 'Darwin':
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

        pub.subscribe(self.youtubedl_from_import, "UPDATE_YDL_EVT")
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
        self.logname = varargs[8]  # example: Videomass_VideoConversion.log

        write_log(self.logname, LogOut.appdata['logdir'])  # initial file LOG

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
            self.thread_type = PicturesFromVideo(varargs, duration,
                                                 self.logname, time_seq
                                                 )
        elif varargs[0] == 'libvidstab':  # from Audio/Video Conv.
            self.thread_type = VidStab(varargs, duration,
                                       self.logname, time_seq
                                       )
        elif varargs[0] == 'concat_demuxer':  # from Concatenation Demuxer
            self.thread_type = ConcatDemuxer(varargs, duration,
                                             self.logname,
                                             )
        elif varargs[0] == 'youtube_dl downloading':  # as import youtube_dl
            self.ckbx_text.Hide()
            self.thread_type = YdlDownloader(varargs, self.logname)
    # ----------------------------------------------------------------------

    def youtubedl_from_import(self, output, duration, status):
        """
        Receiving output messages from youtube_dl library via
        pubsub "UPDATE_YDL_EVT" .
        """
        if status == 'ERROR':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['ERR0']))
            self.txtout.AppendText(f'{output}\n')
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['FAILED']))
            self.txtout.AppendText(LogOut.MSG_failed)
            self.result = 'failed'

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

                with open(os.path.join(LogOut.appdata['logdir'], self.logname),
                          "a", encoding='utf8') as logerr:
                    logerr.write(f"[YOUTUBE_DL]: {status} > {output}\n")
        elif status == 'DOWNLOAD':
            self.labperc.SetLabel(f"{duration[0]}")
            self.barprog.SetValue(duration[1])

        elif status == 'FINISHED':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT1']))
            self.txtout.AppendText(f'{duration}\n')

        if status in ['ERROR', 'WARNING']:
            with open(os.path.join(LogOut.appdata['logdir'], self.logname),
                      "a", encoding='utf8') as logerr:
                logerr.write(f"[YOUTUBE_DL]: {output}\n")
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
            self.txtout.AppendText(LogOut.MSG_failed)
            self.result = 'failed'
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
            self.labperc.SetLabel(f"Processing... {str(int(percentage))}%% | "
                                  f"{''.join(ffprog)}")
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

            with open(os.path.join(LogOut.appdata['logdir'], self.logname),
                      "a", encoding='utf8') as logerr:
                logerr.write(f"[FFMPEG]: {output}")
                # write a row error into file log
    # ----------------------------------------------------------------------

    def update_count(self, count, fsource, destination, duration, end):
        """
        Receive message from first 'for' loop in the thread process.
        This method can be used even for non-loop threads.

        """
        if end == 'ok':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['SUCCESS']))
            self.txtout.AppendText(LogOut.MSG_done)
            try:
                if self.labperc.GetLabel()[1] != '100%':
                    newlab = self.labperc.GetLabel().split()
                    newlab[1] = '100%'
                    self.labperc.SetLabel(" ".join(newlab))
            except IndexError:
                self.labperc.SetLabel('')

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

    # ----------------------------------------------------------------------
    def end_proc(self):
        """
        At the end of the process
        """
        if self.error is True:
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['ERR1']))
            self.txtout.AppendText(LogOut.MSG_taskfailed + '\n')

        elif self.abort is True:
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['ABORT']))
            self.txtout.AppendText(LogOut.MSG_interrupted + '\n')

        else:
            if not self.result:
                endmsg = LogOut.MSG_completed
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT3']))
            else:
                endmsg = LogOut.MSG_unfinished
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['WARN']))
            self.parent.statusbar_msg(_('...Finished'), None)
            self.txtout.AppendText(endmsg + '\n')
            self.barprog.SetValue(0)

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
        if not self.logname:  # there is not process
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
        self.ckbx_text.Show()
        self.button_stop.Enable(True)
        self.button_close.Enable(False)
        self.thread_type = None
        self.abort = False
        self.error = False
        self.logname = None
        self.result = None
        # self.txtout.Clear()
        # self.labperc.SetLabel('')
        self.parent.panelShown(self.previus)  # retrieve at previusly panel
        # event.Skip()
