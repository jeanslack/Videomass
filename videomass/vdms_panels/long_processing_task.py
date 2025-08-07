# -*- coding: UTF-8 -*-
"""
Name: long_processing_task.py
Porpose: Console to show logging messages during processing
Compatibility: Python3, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Aug.07.2025
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
import time
import os
from shutil import move
from pubsub import pub
import wx
from videomass.vdms_dialogs.widget_utils import notification_area
from videomass.vdms_io.make_filelog import make_log_template
from videomass.vdms_threads.ffmpeg import FFmpeg
from videomass.vdms_threads.image_extractor import PicturesFromVideo
from videomass.vdms_threads.concat_demuxer import ConcatDemuxer
from videomass.vdms_threads.slideshow import SlideshowMaker
from videomass.vdms_utils.utils import (time_to_integer, integer_to_time)
from videomass.vdms_io import io_tools


def delete_file_source(flist, trashdir):
    """
    Move whole files list to Videomass Trash folder
    after encoding process.
    NOTE: Use `set()` function here because the source
    files to be moved to the trash may be the same more than twice.
    It is then important to also evaluate the existence of those files,
    see `for name ...` loop below.
    """
    filenotfounderror = None
    if not os.path.exists(trashdir):
        if not os.path.isdir(trashdir):
            try:
                os.mkdir(trashdir, mode=0o777)
            except FileNotFoundError as err:
                filenotfounderror = err

    if filenotfounderror is not None:
        wx.MessageBox(f"{filenotfounderror}", _('Videomass - Error!'),
                      wx.ICON_ERROR)
    else:
        date = time.strftime('%H%M%S-%a_%d_%B_%Y')
        for name in set(flist):
            if os.path.exists(name) and os.path.isfile(name):
                dest = os.path.join(trashdir,
                                    f'{date}_{os.path.basename(name)}')
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
    MSG_done = '[Videomass]: SUCCESS !'
    MSG_failed = '[Videomass]: FAILED !'
    MSG_stop = '[Videomass]: STOP command received.'
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
        get = wx.GetApp()  # get data from bootstrap
        self.appdata = get.appset
        self.parent = parent  # main frame
        self.thread_type = None  # the instantiated thread
        self.with_eta = True  # create estimated time of arrival (ETA)
        self.abort = False  # if True set to abort current process
        self.error = False  # if True, all the tasks was failed
        self.previous = None  # panel name from which it starts
        self.logfile = None  # log pathname, None otherwise
        self.result = []  # result of the final process
        self.count = 0  # keeps track of the counts (see `update_count`)
        self.clr = self.appdata['colorscheme']

        wx.Panel.__init__(self, parent=parent)

        infolbl = _("Encoding Status")
        lbl = wx.StaticText(self, label=infolbl)
        if self.appdata['ostype'] != 'Darwin':
            lbl.SetLabelMarkup(f"<b>{infolbl}</b>")
        self.btn_viewlog = wx.Button(self, wx.ID_ANY, _("Current Log"),
                                     size=(-1, -1))
        self.btn_viewlog.Disable()
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
        sizer.Add(self.btn_viewlog, 0, wx.ALL, 5)
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
        self.Bind(wx.EVT_BUTTON, self.view_log, self.btn_viewlog)

        pub.subscribe(self.update_display, "UPDATE_EVT")
        pub.subscribe(self.update_count, "COUNT_EVT")
        pub.subscribe(self.end_proc, "END_EVT")
    # ----------------------------------------------------------------------

    def view_log(self, event):
        """
        Opens the log file corresponding to the last executed process.
        """
        if self.logfile:
            fname = str(self.logfile)
            if os.path.exists(fname) and os.path.isfile(fname):
                io_tools.openpath(fname)
    # ----------------------------------------------------------------------

    def topic_thread(self, args, data, previous='View', mode='w'):
        """
        This method is resposible to create the Thread instance.

        """
        self.previous = previous  # stores the panel from which it starts

        if args[0] == 'View':
            return

        self.txtout.Clear()
        self.labprog.SetLabel('')
        self.labffmpeg.SetLabel('')
        self.btn_viewlog.Disable()

        self.logfile = make_log_template(args[1],
                                         self.appdata['logdir'],
                                         mode,  # w or a
                                         )
        if args[0] in ('One pass', 'Two pass', 'Two pass EBU',
                       'Two pass VIDSTAB', 'Queue Processing'):
            self.thread_type = FFmpeg(self.logfile, data)

        elif args[0] == 'video_to_sequence':
            self.with_eta = False
            self.thread_type = PicturesFromVideo(self.logfile, **data)

        elif args[0] == 'sequence_to_video':
            self.with_eta = False
            self.thread_type = SlideshowMaker(self.logfile, **data)

        elif args[0] == 'concat_demuxer':
            self.with_eta = False
            self.thread_type = ConcatDemuxer(self.logfile, **data)
    # ----------------------------------------------------------------------

    def append_messages(self, output):
        """
        Append all others lines on the textctrl and log file.
        Since not all ffmpeg messages are errors, sometimes
        it happens to see more output marked with yellow color.
        """
        with open(self.logfile, "a", encoding='utf-8') as logerr:
            logerr.write(f"[FFMPEG]: {output}")

        if [x for x in ('info', 'Info') if x in output]:
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['INFO']))
            self.txtout.AppendText(f'{output}')

        elif [x for x in ('Failed', 'failed', 'Error', 'error')
                if x in output]:
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['ERR0']))
            self.txtout.AppendText(f'{output}')

        elif [x for x in ('warning', 'Warning', 'warn') if x in output]:
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['WARN']))
            self.txtout.AppendText(f'{output}')

        else:
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT3']))
            self.txtout.AppendText(f'{output}')
    # ----------------------------------------------------------------------

    def update_display(self, output, duration, status):
        """
        Receive message from thread by pubsub UPDATE_EVT protocol.
        The received 'output' is parsed for calculate the bar
        progress value, percentage label and errors management.
        This method can be used even for non-loop threads.
        """
        if status != 0:  # error, exit status of the p.wait
            if output == 'STOP':
                msg, color = LogOut.MSG_stop, self.clr['ABORT']
            else:
                msg, color = LogOut.MSG_failed, self.clr['ERR1']
            self.txtout.SetDefaultStyle(wx.TextAttr(color))
            self.txtout.AppendText(f"\n\n{msg}")
            self.result.append('failed')
            return  # must be return here

        if 'time=' in output:  # ...in processing
            i = output.index('time=') + 5
            pos = output[i:].split()[0]
            msec = time_to_integer(pos)

            if msec > duration:
                self.barprog.SetValue(duration)
            elif msec == 0:
                self.barprog.SetValue(self.barprog.GetValue())
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
                    if speed in ('N/A', '0') or 'N/A' in speed:
                        eta = "   ETA: N/A"
                    else:  # is float
                        rem = (duration - msec) / float(speed)
                        remaining = integer_to_time(round(rem))
                        eta = f"   ETA: {remaining}"
                else:
                    eta = "   ETA: N/A"
            else:
                eta = ""
            self.labprog.SetLabel(f'Processing: {str(int(percentage))}% {eta}')
            self.labffmpeg.SetLabel(' | '.join(ffprog))

        else:
            self.append_messages(output)
    # ----------------------------------------------------------------------

    def update_count(self, count, duration, end):
        """
        Receive messages from file count, loop or non-loop thread.
        """
        if end == 'DONE':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['SUCCESS']))
            self.txtout.AppendText(f"\n{LogOut.MSG_done}")
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

        if end == 'ERROR':
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['ERR1']))
            self.txtout.AppendText(f'\nERROR: {count}\n')
            self.error = True
        else:
            self.barprog.SetRange(duration)  # set overall duration range
            self.barprog.SetValue(0)  # reset bar progress
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT0']))
            self.txtout.AppendText(f'\n{count}\n')
        self.count += 1
    # ----------------------------------------------------------------------

    def end_proc(self, filetotrash):
        """
        At the end of the process
        """
        if self.error:
            self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT0']))
            self.txtout.AppendText(f"{LogOut.MSG_fatalerror}")
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
                if os.path.basename(self.logfile) == 'Queue Processing.log':
                    pub.sendMessage("QUEUE PROCESS SUCCESSFULLY", msg='Done')

            else:
                if len(self.result) == self.count:
                    endmsg = LogOut.MSG_taskfailed
                else:
                    endmsg = LogOut.MSG_unfinished

                self.txtout.SetDefaultStyle(wx.TextAttr(self.clr['TXT0']))
                notification_area(endmsg, _("For more details please read the "
                                            "Current Log."), wx.ICON_ERROR)

            self.parent.statusbar_msg(_('...Finished'), None)
            self.txtout.AppendText(f"\n{endmsg}\n")
            self.barprog.SetValue(0)

            if filetotrash:  # move processed files to Videomass trash folder
                if self.parent.movetotrash:
                    trashdir = self.appdata['trashdir_loc']
                    delete_file_source(filetotrash, trashdir)  # filelist, dir

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
        self.thread_type = None
        self.abort = False
        self.error = False
        self.result.clear()
        self.count = 0
        self.with_eta = True  # restoring time remaining display
        self.btn_viewlog.Enable()
    # ----------------------------------------------------------------------
