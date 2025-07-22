# -*- coding: UTF-8 -*-
"""
Name: widget_utils.py
Porpose: Features a set of useful wx widgets to use dynamically
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2025 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Nov.27.2021
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

import wx
import wx.adv
from pubsub import pub


class NormalTransientPopup(wx.PopupTransientWindow):
    """
    Adds a bit of text and mouse movement to the wx.PopupWindow
    """
    def __init__(self, parent, style, message, backgrdcol, foregrdcol):
        wx.PopupTransientWindow.__init__(self, parent, style)
        panel = wx.Panel(self)
        panel.SetBackgroundColour(backgrdcol)
        st = wx.StaticText(panel, -1, message)
        st.SetForegroundColour(wx.Colour(foregrdcol))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(st, 0, wx.ALL, 5)
        panel.SetSizer(sizer)

        sizer.Fit(panel)
        sizer.Fit(self)
        self.Layout()


def notification_area(title, message, flag, timeout=5):
    """
    Show the user a message on system tray (Notification Area)

    Various options can be set after the message is created if desired.
    notify.SetFlags(wx.ICON_INFORMATION/wx.ICON_WARNING/wx.ICON_ERROR)
    notify.SetTitle("Wooot")
    notify.SetMessage("It's a message!")
    notify.SetParent(self)
    """
    notify = wx.adv.NotificationMessage(title=title,
                                        message=message,
                                        parent=None,
                                        flags=flag
                                        )
    notify.Show(timeout=timeout)  # 1 for short timeout, 100 for long timeout
    # notify.Close()       # Hides the notification.


class PopupDialog(wx.Dialog):
    """
    A pop-up dialog box for temporary messages that tell the
    user the process in progress (usually short/medium duration
    operations).
    New in version 5.0.12:
        If your thread has the `stop` method you can pass a running
        `thread` as default arg to interface with the auto-displayed
        Stop button (See `VolumeDetectThread` class as example model).

    Usage:
            loadDlg = PopupDialog(parent, caption, message, thread)
            loadDlg.ShowModal()
            loadDlg.Destroy()
    """
    def __init__(self, parent=None,
                 caption='Pop-Up Dialog',
                 msg="Wait, I'm completing a task...",
                 thread=None,
                 ):
        # Create a dialog
        wx.Dialog.__init__(self, parent, -1, caption, size=(350, 150),
                           style=wx.CAPTION)
        # Add sizers
        self.thread = thread
        boxv = wx.BoxSizer(wx.VERTICAL)
        boxh = wx.BoxSizer(wx.HORIZONTAL)

        if hasattr(wx, 'ActivityIndicator'):  # wxPython => 4.1
            # activity add indicator
            ai = wx.ActivityIndicator(self)
            ai.Start()
            boxh.Add(ai, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        # Add the message
        message = wx.StaticText(self, -1, msg, style=wx.ALIGN_CENTRE_VERTICAL)
        boxh.Add(message, 0, wx.EXPAND | wx.ALL, 10)
        boxv.Add(boxh, 0, wx.EXPAND)
        # Add an Info graphic
        bitmap = wx.Bitmap(48, 48)
        bitmap = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION,
                                          wx.ART_MESSAGE_BOX, (48, 48)
                                          )
        graphic = wx.StaticBitmap(self, -1, bitmap)
        boxh.Add(graphic, 0, wx.TOP | wx.ALL, 10)

        if self.thread:
            # show button stop
            gridbtn = wx.GridSizer(1, 1, 0, 0)
            boxv.Add(gridbtn, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=0)
            button_stop = wx.Button(self, wx.ID_ANY, _("Stop"))
            gridbtn.Add(button_stop, 1, wx.ALL, 5)
            self.Bind(wx.EVT_BUTTON, self.on_stop, button_stop)

        # Handle layout
        self.SetAutoLayout(True)
        self.SetSizer(boxv)
        self.Fit()
        self.Layout()

        pub.subscribe(self.getMessage, "RESULT_EVT")
    # ----------------------------------------------------------#

    def on_stop(self, event):
        """
        If thread is not None, you can call the thread stop
        method here.
        """
        self.thread.stop()

    def getMessage(self, status):
        """
        Process report terminated. This method is called using
        pub/sub protocol (see generic_download.py, generic_task.py,
        volumedetect.py, ytd_extractinfo.py, filter_stab.py),
        it riceive msg and status from current thread.
        NOTE:
        All'inizio usavo self.Destroy() per chiudere il dialogo modale
        (con modeless ritornava dati None), ma dava warning e critical
        e su OsX non chiudeva affatto. Con EndModal ho risolto tutti
        i problemi e funziona bene. Ma devi ricordarti di eseguire
        Destroy() dopo ShowModal() nel chiamante.
        vedi: https://github.com/wxWidgets/Phoenix/issues/672
        Penso sia fattibile anche implementare un'interfaccia GetValue
        su questo dialogo, ma si perderebbe un po' di portabilità.

        """
        # self.Destroy() # do not work
        # self.ai.Stop()
        self.EndModal(1)


class CountDownDlg(wx.Dialog):
    """
    This dialog notifies the user that something will happen
    when the countdown expires, e.g. exiting the application
    or shutting down the system.
    At the end of the countdown this dialogue will
    self-destroy and events will be allowed to continue unless
    the user clicks on the cancel button.

    Usage example:
        dlg = CountDownDlg(self,
                           timeout=10,
                           message='Something happens in {0} seconds',
                           caption='My awesome title'
                           )
        res = dlg.ShowModal() == wx.ID_OK
        dlg.Destroy()
        if res:
            ...other code here
    """
    get = wx.GetApp()  # get data from bootstrap
    APPICON = get.iconset['videomass']
    TIMER_INTERVAL = 1000  # milliseconds

    def __init__(self, parent, timeout, message, caption):
        """
        parent: -1 to make parent, use 'None' otherwise
        timeout: time second (int)
        message: a message including the format {0} (str)
        caption: title for caption (str)
        """
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)

        self.timeout = timeout
        self.message = message

        # ------ Add widget controls
        sizbase = wx.BoxSizer(wx.VERTICAL)
        sizbase.Add((0, 20), 0)
        self.msgtxt = wx.StaticText(self, wx.ID_ANY,
                                    self.message.format(self.timeout),
                                    style=wx.ALIGN_CENTRE_VERTICAL
                                    )
        sizbase.Add(self.msgtxt, 1, wx.ALL | wx.ALIGN_CENTRE, 5)
        # ------ bottom layout buttons
        sizbott = wx.BoxSizer(wx.HORIZONTAL)
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "")
        sizbott.Add(btn_cancel, 0)
        btn_ok = wx.Button(self, wx.ID_OK)
        sizbott.Add(btn_ok, 0, wx.LEFT, 5)
        sizbase.Add(sizbott, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=5)
        # ------ Properties
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(CountDownDlg.APPICON,
                                      wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetTitle(caption)
        self.SetMinSize((400, 150))
        self.SetSizer(sizbase)
        sizbase.Fit(self)
        self.Layout()
        self.Center()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(self.TIMER_INTERVAL)
    # ------------------------------------------------------------------#

    def autodestroy(self):
        """
        stop the timer and destroy this dialog.
        """
        self.timer.Stop()
        return self.Destroy()

    # ----------------------Event handler (callback)----------------------#

    def on_timer(self, event):
        """
        Set the timer countdown on message
        """
        self.timeout -= 1
        self.msgtxt.SetLabel(self.message.format(self.timeout))
        if self.timeout <= 0:
            self.EndModal(wx.ID_OK)
