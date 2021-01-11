# -*- coding: UTF-8 -*-
# Name: long_processing_task.py
# Porpose: Console to show logging messages during processing
# Compatibility: Python3, wxPython4 Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: May.26.2020 *PEP8 compatible*
#########################################################
# This file is part of Videomass.

#    Videomass is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass.  If not, see <http://www.gnu.org/licenses/>.

#########################################################
from __future__ import unicode_literals
import wx
import wx.richtext as rt
import os
from pubsub import pub
from videomass3.vdms_io.make_filelog import write_log
from videomass3.vdms_threads.ydl_pylibdownloader import Ydl_DL_Pylib
from videomass3.vdms_threads.ydl_executable import Ydl_DL_Exec
from videomass3.vdms_threads.one_pass import OnePass
from videomass3.vdms_threads.two_pass import TwoPass
from videomass3.vdms_threads.two_pass_EBU import Loudnorm
from videomass3.vdms_threads.picture_exporting import PicturesFromVideo
from videomass3.vdms_utils.utils import time_human

# Used colour in HTML
BLACK = '#242424'
DARK_BROWN = '#262222'  # for background color on TextCtrl
WHITE = '#FFFFFF'  # file title or URL in progress
GREY = '#959595'  # all other text messages
CYAN = '#31BAA7'  # for info text messages
YELLOW = '#C8B72F'  # for warning text messages
ORANGE = '#FF4A1B'  # for error text messages
ORANGE_DEEP = '#E92D15'
RED = '#EA312D'
RED_DEEP = '#D21814'  # if failed
VIOLET = '#A41EA4'  # if the user stops the processes
GREEN = '#1EA41E'  # when it is successful
AZURE = '#3298FB'

# used msg on text
MSG_done = _('[Videomass]: DONE !\n')
MSG_failed = _('[Videomass]: FAILED !\n')
MSG_taskfailed = _('\n[Videomass]: Sorry, task failed !\n')
MSG_interrupted = _('\n[Videomass]: Interrupted Process !\n')
MSG_completed = _('\n[Videomass]: Successfully completed !\n')
MSG_unfinished = _('\n[Videomass]: completed, but not everything '
                   'was successful.\n')

# get videomass wx.App attribute
get = wx.GetApp()
OS = get.OS
LOGDIR = get.LOGdir


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
                'time', '00:00:39.02', 'bitrate', '435.0kbits/s', s'peed',
                '5.15x']
    for x, y in pairwise(iterable):
        print(x,y)

    <https://stackoverflow.com/questions/5389507/iterating-over-every-
    two-elements-in-a-list>

    """
    a = iter(iterable)  # list_iterator object
    return zip(a, a)  # zip object pairs from list iterable object
# ----------------------------------------------------------------------#


class Logging_Console(wx.Panel):
    """
    This is an alternative Rich textctrl style implementation.
    Displays a text control for the output logging, a progress bar
    and a progressive percentage text label. This panel is used
    in combination with separated threads for long processing tasks.
    It also implements stop and close buttons to stop the current
    process and close the panel at the end.

    """
    def __init__(self, parent):
        """
        In the 'previous' attribute is stored an ID string used to
        recover the previous panel from which the process is started.
        The 'logname' attribute is the name_of_panel.log file in which
        log messages will be written

        """
        self.parent = parent  # main frame
        self.PARENT_THREAD = None  # the instantiated thread
        self.ABORT = False  # if True set to abort current process
        self.ERROR = False  # if True, all the tasks was failed
        self.previus = None  # panel name from which it starts
        self.logname = None  # example: Videomass_VideoConversion.log
        self.result = None  # result of the final process

        wx.Panel.__init__(self, parent=parent)
        """ Constructor """

        lbl = wx.StaticText(self, label=_("Log viewing console:"))
        self.OutText = rt.RichTextCtrl(self,
                                       style=wx.VSCROLL |
                                       wx.HSCROLL |
                                       wx.TE_MULTILINE |
                                       wx.TE_READONLY
                                       )
        self.ckbx_text = wx.CheckBox(self, wx.ID_ANY, (_("Suppress excess "
                                                         "output")))
        self.barProg = wx.Gauge(self, wx.ID_ANY, range=0)
        self.labPerc = wx.StaticText(self, label="")
        self.button_stop = wx.Button(self, wx.ID_STOP, _("Abort"))
        self.button_close = wx.Button(self, wx.ID_CLOSE, "")
        sizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridSizer(1, 2, 5, 5)
        sizer.Add(lbl, 0, wx.ALL, 5)
        sizer.Add(self.OutText, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.ckbx_text, 0, wx.ALL, 5)
        sizer.Add(self.barProg, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.labPerc, 0, wx.ALL, 5)
        sizer.Add(grid, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=5)
        grid.Add(self.button_stop, 0, wx.ALL, 5)
        grid.Add(self.button_close, 1, wx.ALL, 5)
        # set_properties:
        self.OutText.SetBackgroundColour(DARK_BROWN)
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

        pub.subscribe(self.youtubedl_from_import, "UPDATE_YDL_FROM_IMPORT_EVT")
        pub.subscribe(self.youtubedl_exec, "UPDATE_YDL_EXECUTABLE_EVT")
        pub.subscribe(self.update_display, "UPDATE_EVT")
        pub.subscribe(self.update_count, "COUNT_EVT")
        pub.subscribe(self.end_proc, "END_EVT")
    # ----------------------------------------------------------------------

    def topic_thread(self, panel, varargs, duration):
        """
        Thread redirection
        varargs: type tuple data object
        duration: total duration or partial if set timeseq
        """
        self.previus = panel  # stores the panel from which it starts

        if varargs[0] == 'console view only':
            self.button_stop.Enable(False)
            self.button_close.Enable(True)
            return

        self.OutText.Clear(), self.labPerc.SetLabel('')
        self.logname = varargs[8]  # example: Videomass_VideoConversion.log
        time_seq = self.parent.time_seq  # a time segment

        write_log(self.logname, LOGDIR)  # set initial file LOG

        if varargs[0] == 'onepass':  # from Audio/Video Conv.
            self.PARENT_THREAD = OnePass(varargs, duration,
                                         self.logname, time_seq,
                                         )
        elif varargs[0] == 'twopass':  # from Video Conv.
            self.PARENT_THREAD = TwoPass(varargs, duration,
                                         self.logname, time_seq
                                         )
        elif varargs[0] == 'two pass EBU':  # from Audio/Video Conv.
            self.PARENT_THREAD = Loudnorm(varargs, duration,
                                          self.logname, time_seq
                                          )
        elif varargs[0] == 'savepictures':
            self.PARENT_THREAD = PicturesFromVideo(varargs, duration,
                                                   self.logname, time_seq
                                                   )
        elif varargs[0] == 'youtube_dl python package':  # as import youtube_dl
            self.ckbx_text.Hide()
            self.PARENT_THREAD = Ydl_DL_Pylib(varargs, self.logname)

        elif varargs[0] == 'youtube-dl executable':  # as youtube-dl exec.
            self.ckbx_text.Hide()
            self.PARENT_THREAD = Ydl_DL_Exec(varargs, self.logname)
    # ----------------------------------------------------------------------

    def youtubedl_from_import(self, output, duration, status):
        """
        Receiving output messages from youtube_dl library via
        pubsub "UPDATE_YDL_FROM_IMPORT_EVT" .
        """
        if status == 'ERROR':
            self.OutText.BeginTextColour((RED))
            self.OutText.WriteText('%s\n' % output)
            self.OutText.BeginBold()
            self.OutText.WriteText(MSG_failed)
            self.OutText.EndBold(), self.OutText.EndTextColour()
            self.result = 'failed'

        elif status == 'WARNING':
            self.OutText.BeginTextColour((YELLOW))
            self.OutText.WriteText('%s\n' % output)
            self.OutText.EndTextColour()

        elif status == 'DEBUG':
            if '[download] Destination' in output:
                self.OutText.BeginTextColour((AZURE))
                self.OutText.WriteText('%s\n' % output)
                self.OutText.EndTextColour()

            elif '[info]' in output:
                self.OutText.BeginTextColour((CYAN))
                self.OutText.WriteText('%s\n' % output)
                self.OutText.EndTextColour()

            elif '[download]' not in output:
                self.OutText.BeginTextColour((GREY))
                self.OutText.WriteText('%s\n' % output)
                self.OutText.EndTextColour()

                with open(os.path.join(LOGDIR, self.logname), "a") as logerr:
                    logerr.write("[YOUTUBE_DL]: %s > %s\n" % (status, output))
        elif status == 'DOWNLOAD':
            self.labPerc.SetLabel("%s" % duration[0])
            self.barProg.SetValue(duration[1])

        elif status == 'FINISHED':
            self.OutText.BeginTextColour((GREY))
            self.OutText.WriteText('%s\n' % duration)
            self.OutText.EndTextColour()

        if status in ['ERROR', 'WARNING']:
            with open(os.path.join(LOGDIR, self.logname), "a") as logerr:
                logerr.write("[YOUTUBE_DL]: %s\n" % (output))
    # ---------------------------------------------------------------------#

    def youtubedl_exec(self, output, duration, status):
        """
        Receiving output messages from youtube-dl command line execution
        via pubsub "UPDATE_YDL_EXECUTABLE_EVT" .

        """
        if not status == 0:  # error, exit status of the p.wait
            if output:
                if 'ERROR:' in output:
                    self.OutText.BeginTextColour((RED))
                    self.OutText.WriteText('%s\n' % output)
            self.OutText.BeginBold()
            self.OutText.WriteText(MSG_failed)
            self.OutText.EndBold(), self.OutText.EndTextColour()
            self.result = 'failed'
            return

        if '[download]' in output:  # ...in processing
            if 'Destination' not in output:
                try:
                    i = float(output.split()[1].split('%')[0])
                except ValueError:
                    self.OutText.BeginTextColour((YELLOW))
                    self.OutText.WriteText(' %s' % output)
                    self.OutText.EndTextColour()
                else:
                    self.barProg.SetValue(i)
                    self.labPerc.SetLabel("%s" % output)
                    del output, duration

        else:  # append all others lines on the textctrl and log file
            if not self.ckbx_text.IsChecked():  # not print the output
                if '[info]' in output:
                    self.OutText.BeginTextColour((CYAN))
                    self.OutText.WriteText(' %s' % output)
                    self.OutText.EndTextColour()
                elif 'WARNING:' in output:
                    self.OutText.BeginTextColour((YELLOW))
                    self.OutText.WriteText(' %s' % output)
                    self.OutText.EndTextColour()
                elif 'ERROR:' not in output:
                    self.OutText.BeginTextColour((GREY))
                    self.OutText.WriteText(' %s' % output)
                    self.OutText.EndTextColour()

            with open(os.path.join(LOGDIR, self.logname), "a") as logerr:
                logerr.write("[YOUTUBE-DL]: %s" % (output))
                # write a row error into file log

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
        #    self.OutText.WriteText(output)

        if not status == 0:  # error, exit status of the p.wait
            self.OutText.BeginBold()
            self.OutText.BeginTextColour((RED))
            self.OutText.WriteText(MSG_failed)
            self.OutText.EndBold(), self.OutText.EndTextColour()
            self.result = 'failed'
            return  # must be return here

        if 'time=' in output:  # ...in processing
            i = output.index('time=')+5
            pos = output[i:i+8].split(':')
            hours, minutes, seconds = pos[0], pos[1], pos[2]
            timesum = (int(hours) * 3600 + int(minutes)) * 60 + int(seconds)
            self.barProg.SetValue(timesum)
            percentage = timesum / duration * 100
            out = [a for a in "=".join(output.split()).split('=') if a]
            ffprog = []
            for x, y in pairwise(out):
                ffprog.append("%s: %s | " % (x, y))

            remaining = time_human(duration-timesum)
            self.labPerc.SetLabel("Processing... %s%% | %sTime Remaining: %s" %
                                  (str(int(percentage)), "".join(ffprog),
                                   remaining)
                                  )
            del output, duration

        else:  # append all others lines on the textctrl and log file
            if not self.ckbx_text.IsChecked():  # not print the output
                if [x for x in ('info', 'Info') if x in output]:
                    self.OutText.BeginTextColour((CYAN))
                    self.OutText.WriteText('%s' % output)
                    self.OutText.EndTextColour()

                elif [x for x in ('Failed', 'failed', 'Error', 'error')
                      if x in output]:
                    self.OutText.BeginTextColour((RED))
                    self.OutText.WriteText('%s' % output)
                    self.OutText.EndTextColour()

                elif [x for x in ('warning', 'Warning') if x in output]:
                    self.OutText.BeginTextColour((YELLOW))
                    self.OutText.WriteText('%s' % output)
                    self.OutText.EndTextColour()

                else:
                    self.OutText.BeginTextColour((GREY))
                    self.OutText.WriteText('%s' % output)
                    self.OutText.EndTextColour()

            with open(os.path.join(LOGDIR, self.logname), "a") as logerr:
                logerr.write("[FFMPEG]: %s" % (output))
                # write a row error into file log
    # ----------------------------------------------------------------------

    def update_count(self, count, duration, fname, end):
        """
        Receive message from first 'for' loop in the thread process.
        This method can be used even for non-loop threads.

        """
        if end == 'ok':
            self.OutText.SetInsertionPointEnd()
            self.OutText.BeginBold()
            self.OutText.BeginTextColour((GREEN))
            self.OutText.WriteText(MSG_done)
            self.OutText.EndBold(), self.OutText.EndTextColour()
            self.OutText.SetInsertionPointEnd()
            lab = "%s" % self.labPerc.GetLabel()
            if lab.split('|')[0] == 'Processing... 99% ':
                relab = lab.replace('Processing... 99%', 'Processing... 100%')
                self.labPerc.SetLabel(relab)
            return
        # if STATUS_ERROR == 1:
        if end == 'error':
            self.OutText.BeginTextColour((YELLOW))
            self.OutText.WriteText('\n%s\n' % (count))
            self.ERROR = True
        else:
            self.barProg.SetRange(duration)  # set la durata complessiva
            self.barProg.SetValue(0)  # resetto la prog bar
            self.OutText.BeginTextColour((WHITE))
            self.OutText.WriteText('\n%s : "%s"\n' % (count, fname))
        self.OutText.EndTextColour()
    # ----------------------------------------------------------------------

    def end_proc(self):
        """
        At the end of the process
        """
        self.OutText.BeginBold()
        self.OutText.BeginUnderline()

        if self.ERROR is True:
            self.OutText.BeginTextColour((RED))
            self.OutText.WriteText(MSG_taskfailed)

        elif self.ABORT is True:
            self.OutText.BeginTextColour((VIOLET))
            self.OutText.WriteText(MSG_interrupted)

        else:
            if not self.result:
                endmsg = MSG_completed
                self.OutText.BeginTextColour((WHITE))
            else:
                endmsg = MSG_unfinished
                self.OutText.BeginTextColour((YELLOW))
            self.parent.statusbar_msg(_('...Finished'), None)
            self.OutText.WriteText(endmsg)
            self.barProg.SetValue(0)

        self.OutText.EndBold()
        self.OutText.EndUnderline()
        self.OutText.EndTextColour()
        self.button_stop.Enable(False)
        self.button_close.Enable(True)
        self.PARENT_THREAD = None
    # ----------------------------------------------------------------------

    def on_stop(self, event):
        """
        The user change idea and was stop process
        """
        self.PARENT_THREAD.stop()
        self.parent.statusbar_msg(_("wait... I'm aborting"), 'GOLDENROD')
        self.PARENT_THREAD.join()
        self.parent.statusbar_msg(_("...Interrupted"), None)
        self.ABORT = True

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

        if self.PARENT_THREAD is not None:
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
        self.PARENT_THREAD = None
        self.ABORT = False
        self.ERROR = False
        self.logname = None
        self.result = None
        # self.OutText.Clear()
        # self.labPerc.SetLabel('')
        self.parent.panelShown(self.previus)  # retrieve at previusly panel
        # event.Skip()
