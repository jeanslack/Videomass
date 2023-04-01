# -*- coding: UTF-8 -*-
"""
Name: long_processing_task.py
Porpose: Console to show logging messages during processing
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Jan.21.2023
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
from __future__ import unicode_literals
import time
import os
from shutil import move
from pubsub import pub
import wx
from videomass.vdms_dialogs.widget_utils import notification_area
from videomass.vdms_io.make_filelog import make_log_template
from videomass.vdms_threads.one_pass import OnePass
from videomass.vdms_threads.two_pass import TwoPass
from videomass.vdms_threads.two_pass_ebu import Loudnorm
from videomass.vdms_threads.picture_exporting import PicturesFromVideo
from videomass.vdms_threads.video_stabilization import VidStab
from videomass.vdms_threads.concat_demuxer import ConcatDemuxer
from videomass.vdms_threads.slideshow import SlideshowMaker
from videomass.vdms_utils.utils import (get_milliseconds, milliseconds2clock)


def delete_file_source(flist, trashdir):
    """
    Move whole files list to Videomass Trash folder
    after encoding process.
    """
    filenotfounderror = None
    if not os.path.exists(trashdir):
        if not os.path.isdir(trashdir):
            try:
                os.mkdir(trashdir, mode=0o777)
            except FileNotFoundError as err:
                filenotfounderror = err

    if filenotfounderror is not None:
        wx.MessageBox(f"{filenotfounderror}", 'Videomass', wx.ICON_ERROR)
    else:
        date = time.strftime('%H%M%S-%a_%d_%B_%Y')
        for name in flist:
            dest = os.path.join(trashdir, f'{date}_{os.path.basename(name)}')
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
    1)
        for x, y in pairwise(iterable):
            x, y
    2)
        dict(pairwise(iterable))

    Return: a zip object pairs from list iterable object.

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
    YELLOW = '#bd9f00'
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
        self.with_eta = True  # create estimated time of arrival (ETA)
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
                                  style=wx.TE_MULTILINE
                                  | wx.TE_READONLY
                                  | wx.TE_RICH2
                                  )
        self.barprog = wx.Gauge(self, wx.ID_ANY, range=0)
        self.labprog = wx.StaticText(self, label="")
        self.labffmpeg = wx.StaticText(self, label="")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((0, 10))
        sizer.Add(lbl, 0, wx.ALL, 5)
        sizer.Add(self.txtout, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.barprog, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.labprog, 0, wx.ALL, 5)
        sizer.Add(self.labffmpeg, 0, wx.ALL, 5)
        line = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                             size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                             name=wx.StaticLineNameStr,
                             )
        sizer.Add(line, 0, wx.ALL | wx.EXPAND, 5)
        # set_properties:
        self.txtout.SetBackgroundColour(self.clr['BACKGRD'])
        self.SetSizerAndFit(sizer)
        # ------------------------------------------

        pub.subscribe(self.update_display, "UPDATE_EVT")
        pub.subscribe(self.update_count, "COUNT_EVT")
        pub.subscribe(self.end_proc, "END_EVT")
    # ----------------------------------------------------------------------

    def topic_thread(self, panel, durs, tseq, *args):
        """
        This method is resposible to create the Thread instance.
        *args: type tuple data object
        durs: list of file durations or partial if tseq is setted
        """
        self.previus = panel  # stores the panel from which it starts

        if args[0] == 'Viewing last log':
            return

        self.txtout.Clear()
        self.labprog.SetLabel('')
        self.labffmpeg.SetLabel('')

        self.logname = make_log_template(args[8], self.appdata['logdir'])

        if args[0] == 'onepass':
            self.thread_type = OnePass(self.logname, durs, tseq, *args)

        elif args[0] == 'twopass':
            self.thread_type = TwoPass(self.logname, durs, tseq, *args)

        elif args[0] == 'two pass EBU':
            self.thread_type = Loudnorm(self.logname, durs, tseq, *args)

        elif args[0] == 'video_to_sequence':
            self.with_eta = False
            self.thread_type = PicturesFromVideo(self.logname, durs,
                                                 tseq, *args
                                                 )
        elif args[0] == 'sequence_to_video':
            self.thread_type = SlideshowMaker(self.logname, durs, *args)

        elif args[0] == 'libvidstab':
            self.thread_type = VidStab(self.logname, durs, tseq, *args)

        elif args[0] == 'concat_demuxer':
            self.with_eta = False
            self.thread_type = ConcatDemuxer(self.logname, durs, *args)
    # ----------------------------------------------------------------------

    def update_display(self, output, duration, status):
        """
        Receive message from thread by pubsub UPDATE_EVT protol.
        The received 'output' is parsed for calculate the bar
        progress value, percentage label and errors management.
        This method can be used even for non-loop threads.

        NOTE: During conversion the ffmpeg errors do not stop all
              others tasks, if an error occurred it will be marked
              with 'failed' but the other tasks will continue;
              if it has finished without errors it will be marked with
              'done' on `update_count` method. Since not all ffmpeg
              messages are errors, sometimes it happens to see more
              output marked with yellow color.
        """
        if not status == 0:  # error, exit status of the p.wait
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['ERR1']))
            self.txtout.AppendText(f"{LogOut.MSG_failed}\n")
            self.result.append('failed')
            return  # must be return here

        if 'time=' in output:  # ...in processing
            i = output.index('time=') + 5
            pos = output[i:].split()[0]
            msec = get_milliseconds(pos)

            if msec > duration:
                self.barprog.SetValue(duration)
            else:
                self.barprog.SetValue(msec)

            percentage = round((msec / duration) * 100 if
                               duration != 0 else 100)
            out = [a for a in "=".join(output.split()).split('=') if a]
            ffprog = []
            for key, val in pairwise(out):
                ffprog.append(f"{key}: {val}")

            if self.with_eta:
                if 'speed=' in output:
                    speed = output.split('speed=')[-1].strip().split('x')[0]
                    if speed in ('N/A', '0'):
                        eta = "   ETA: N/A"
                    else:  # is float
                        rem = (duration - msec) / float(speed)
                        remaining = milliseconds2clock(round(rem))
                        eta = f"   ETA: {remaining}"
                else:
                    eta = "   ETA: N/A"
            else:
                eta = ""
            self.labprog.SetLabel(f'Processing: {str(int(percentage))}% {eta}')
            self.labffmpeg.SetLabel(' | '.join(ffprog))

            del output, duration

        else:  # append all others lines on the textctrl and log file
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
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT3']))
                self.txtout.AppendText(f'{output}')

            with open(self.logname, "a", encoding='utf8') as logerr:
                logerr.write(f"[FFMPEG]: {output}")
    # ----------------------------------------------------------------------

    def update_count(self, count, fsource, destination, duration, end):
        """
        Receive messages from file count, loop or non-loop thread.
        """
        if end == 'Done':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['SUCCESS']))
            self.txtout.AppendText(f"{LogOut.MSG_done}\n")
            # set end values for percentage and ETA
            if self.with_eta:
                newlab = self.labprog.GetLabel().split()
                if 'Processing:' in newlab:
                    newlab[1] = '100%   '
                if 'ETA:' in newlab:
                    newlab[3] = '00:00:00.000'
                self.labprog.SetLabel(" ".join(newlab))
            else:
                self.labprog.SetLabel('Processing: 100%')
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
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT1']))
            self.txtout.AppendText(f'{fsource}\n')
            if destination:
                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT1']))
                self.txtout.AppendText(f'{destination}\n')

        self.count += 1
    # ----------------------------------------------------------------------

    def end_proc(self, msg):
        """
        At the end of the process
        """
        if self.error:
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT0']))
            self.txtout.AppendText(f"\n{LogOut.MSG_fatalerror}\n")
            notification_area(_("Fatal Error !"), LogOut.MSG_fatalerror,
                              wx.ICON_ERROR)
        elif self.abort:
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
                if self.parent.movetotrash:
                    trashdir = self.appdata['user_trashdir']
                    delete_file_source(msg, trashdir)  # filelist, dir

        self.txtout.AppendText('\n')
        self.reset_all()
        pub.sendMessage("PROCESS TERMINATED", msg='Terminated')
    # ----------------------------------------------------------------------

    def on_stop(self):
        """
        The user change idea and was stop process
        """
        self.thread_type.stop()
        self.parent.statusbar_msg(_("Please wait... interruption in progress"),
                                  LogOut.YELLOW, LogOut.BLACK)
        self.thread_type.join()
        self.parent.statusbar_msg(_("...Interrupted"), None)
        self.abort = True
        # event.Skip()
    # ----------------------------------------------------------------------

    def reset_all(self):
        """
        Reset to default at any process terminated
        """
        self.logname = None
        self.thread_type = None
        self.abort = False
        self.error = False
        self.result.clear()
        self.count = 0
        self.with_eta = True  # restoring time remaining display
    # ----------------------------------------------------------------------
