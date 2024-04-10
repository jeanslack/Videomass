# -*- coding: UTF-8 -*-
"""
Name: ydl_preferences.py
Porpose: yt-dlp setup dialog
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Apr.08.2024
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
import webbrowser
import wx
from videomass.vdms_sys.settings_manager import ConfigManager


class Ytdlp_Options(wx.Dialog):
    """
    Represents settings and configuration
    storing of the program.
    """
    # -----------------------------------------------------------------

    def __init__(self, parent):
        """
        self.appdata: (dict) default settings already loaded.
        self.confmanager: instance to ConfigManager class
        self.settings: (dict) current user settings from file conf.

        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.confmanager = ConfigManager(self.appdata['fileconfpath'])
        self.settings = self.confmanager.read_options()

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)

        # ----------------------------set notebook
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(self, wx.ID_ANY, style=0)
        sizer_base.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)

        # -----tab 1
        tabOne = wx.Panel(notebook, wx.ID_ANY)
        sizerGen = wx.BoxSizer(wx.VERTICAL)
        sizerGen.Add((0, 40))
        labwa = wx.StaticText(tabOne, wx.ID_ANY, _("Workarounds"))
        sizerGen.Add(labwa, 0, wx.ALL, 5)
        self.ckbx_ssl = wx.CheckBox(tabOne, wx.ID_ANY,
                                    (_('Don’t check SSL certificate'))
                                    )
        self.ckbx_ssl.SetValue(self.appdata['ssl_certificate'])
        sizerGen.Add(self.ckbx_ssl, 0, wx.LEFT, 15)
        sizerGen.Add((0, 10))
        labfn = wx.StaticText(tabOne, wx.ID_ANY, _("Filename options"))
        sizerGen.Add(labfn, 0, wx.ALL, 5)
        self.ckbx_id = wx.CheckBox(tabOne, wx.ID_ANY,
                                   (_('Include the ID in file names')))
        self.ckbx_id.SetValue(self.appdata['include_ID_name'])

        sizerGen.Add(self.ckbx_id, 0, wx.LEFT, 15)

        self.ckbx_limitfn = wx.CheckBox(tabOne, wx.ID_ANY,
                                        (_('Restrict file names to ASCII '
                                           'characters'))
                                        )
        self.ckbx_limitfn.SetValue(self.appdata['restrict_fname'])
        sizerGen.Add(self.ckbx_limitfn, 0, wx.LEFT, 15)
        sizerGen.Add((0, 10))
        labpp = wx.StaticText(tabOne, wx.ID_ANY, _("Post-Process options"))
        sizerGen.Add(labpp, 0, wx.ALL, 5)
        self.ckbx_thumb = wx.CheckBox(tabOne, wx.ID_ANY,
                                      (_('Embed thumbnail in audio file'))
                                      )
        self.ckbx_thumb.SetValue(self.appdata['embed_thumbnails'])
        sizerGen.Add(self.ckbx_thumb, 0, wx.LEFT, 15)
        self.ckbx_meta = wx.CheckBox(tabOne, wx.ID_ANY,
                                     (_('Add metadata to file'))
                                     )
        self.ckbx_meta.SetValue(self.appdata['add_metadata'])
        sizerGen.Add(self.ckbx_meta, 0, wx.LEFT, 15)
        self.ckbx_ow = wx.CheckBox(tabOne, wx.ID_ANY,
                                   (_('Overwrite all files and metadata'))
                                   )
        self.ckbx_ow.SetValue(self.appdata['overwr_dl_files'])
        sizerGen.Add(self.ckbx_ow, 0, wx.LEFT, 15)
        tabOne.SetSizer(sizerGen)
        notebook.AddPage(tabOne, _("General"))

        # -----tab 2
        tabTwo = wx.Panel(notebook, wx.ID_ANY)
        sizerFiles = wx.BoxSizer(wx.VERTICAL)
        sizerFiles.Add((0, 40))
        msg = _("Where do you prefer to save your downloads?")
        labdown = wx.StaticText(tabTwo, wx.ID_ANY, msg)
        sizerFiles.Add(labdown, 0, wx.ALL | wx.EXPAND, 5)
        sizerFiles.Add((0, 20))
        sizeYDLdirdest = wx.BoxSizer(wx.HORIZONTAL)
        sizerFiles.Add(sizeYDLdirdest, 0, wx.EXPAND)
        self.txtctrl_YDLpath = wx.TextCtrl(tabTwo, wx.ID_ANY, "",
                                           style=wx.TE_READONLY
                                           )
        sizeYDLdirdest.Add(self.txtctrl_YDLpath, 1, wx.ALL | wx.CENTER, 5)
        self.txtctrl_YDLpath.AppendText(self.appdata['ydlp-outputdir'])
        self.btn_YDLpath = wx.Button(tabTwo, wx.ID_ANY, _('Change'))
        sizeYDLdirdest.Add(self.btn_YDLpath, 0, wx.RIGHT | wx.ALIGN_CENTER, 5)
        sizerFiles.Add((0, 10))
        descr = _("Auto-create subdirectories when downloading playlists")
        self.ckbx_playlist = wx.CheckBox(tabTwo, wx.ID_ANY, (descr))
        self.ckbx_playlist.SetValue(self.appdata['playlistsubfolder'])
        sizerFiles.Add(self.ckbx_playlist, 0, wx.ALL, 5)
        tabTwo.SetSizer(sizerFiles)
        notebook.AddPage(tabTwo, _("File Preferences"))

        # -----tab 3
        tabThree = wx.Panel(notebook, wx.ID_ANY)
        sizerextdown = wx.BoxSizer(wx.VERTICAL)
        sizerextdown.Add((0, 40))
        msg = _("Choosing an external downloader")
        labexdtitle = wx.StaticText(tabThree, wx.ID_ANY, msg)
        sizerextdown.Add(labexdtitle, 0, wx.ALL | wx.EXPAND, 5)
        msg = (_("In addition to the default native one, yt-dlp currently "
                 "supports the following external downloaders:\n"
                 "aria2c, avconv, axel, curl, ffmpeg, httpie, wget.\nPlease "
                 "note that download status information may not be available."
                 ))
        labdwmsg = wx.StaticText(tabThree, wx.ID_ANY, (msg))
        sizerextdown.Add(labdwmsg, 0, wx.ALL, 5)
        sizerextdown.Add((0, 20))
        msg = _("External downloader executable path")
        labextdw = wx.StaticText(tabThree, wx.ID_ANY, msg)
        sizerextdown.Add(labextdw, 0, wx.LEFT | wx.TOP | wx.BOTTOM, 5)
        exedw = str(self.appdata["external_downloader"])
        self.txtctrl_extdw = wx.TextCtrl(tabThree, wx.ID_ANY, exedw)
        sizerextdown.Add(self.txtctrl_extdw, 0, wx.EXPAND | wx.LEFT | wx.RIGHT
                         | wx.BOTTOM, 5)
        labextdwargs = wx.StaticText(tabThree, wx.ID_ANY,
                                     _("External downloader arguments"))
        sizerextdown.Add(labextdwargs, 0, wx.LEFT | wx.TOP | wx.BOTTOM, 5)
        val = self.appdata["external_downloader_args"]
        args = " ".join(val) if isinstance(val, list) else 'None'
        self.txtctrl_extdw_args = wx.TextCtrl(tabThree, wx.ID_ANY, args)
        sizerextdown.Add(self.txtctrl_extdw_args, 0, wx.EXPAND | wx.LEFT
                         | wx.RIGHT | wx.BOTTOM, 5)
        tabThree.SetSizer(sizerextdown)
        notebook.AddPage(tabThree, _("External Downloader"))

        # -----tab 4
        tabFour = wx.Panel(notebook, wx.ID_ANY)
        sizernet = wx.BoxSizer(wx.VERTICAL)
        sizernet.Add((0, 40))
        msg = _("Using a proxy")
        labproxtitle = wx.StaticText(tabFour, wx.ID_ANY, msg)
        sizernet.Add(labproxtitle, 0, wx.ALL | wx.EXPAND, 5)
        proex = 'socks5://user:pass@127.0.0.1:1080/'
        msg = (_('Use the specified HTTP/HTTPS/SOCKS proxy.\nTo enable SOCKS '
                 'proxy, specify a proper scheme, e.g.\n{}\nLeave the text '
                 'field blank for direct connection.').format(proex))
        labproxy = wx.StaticText(tabFour, wx.ID_ANY, (msg))
        sizernet.Add(labproxy, 0, wx.ALL, 5)
        sizernet.Add((0, 20))

        gridproxy = wx.FlexGridSizer(1, 2, 0, 0)
        proxylab = wx.StaticText(tabFour, wx.ID_ANY, _("Proxy"))
        gridproxy.Add(proxylab, 0, wx.ALL | wx.EXPAND, 5)
        self.txtctrl_proxy = wx.TextCtrl(tabFour, wx.ID_ANY, "",
                                         size=(300, -1))
        self.txtctrl_proxy.SetValue(self.appdata["proxy"])
        gridproxy.Add(self.txtctrl_proxy, 0, wx.ALL | wx.EXPAND, 5)
        sizernet.Add(gridproxy, 0, wx.ALL | wx.EXPAND, 5)
        tabFour.SetSizer(sizernet)
        notebook.AddPage(tabFour, _("Network"))
        # -----tab 5
        tabFive = wx.Panel(notebook, wx.ID_ANY)
        sizerauth = wx.BoxSizer(wx.VERTICAL)
        sizerauth.Add((0, 40))
        gridauth = wx.FlexGridSizer(3, 2, 0, 0)
        labuser = wx.StaticText(tabFive, wx.ID_ANY, _("Username"))
        gridauth.Add(labuser, 0, wx.ALL | wx.EXPAND, 5)
        self.txtctrl_username = wx.TextCtrl(tabFive, wx.ID_ANY, "",
                                            size=(300, -1))
        self.txtctrl_username.SetValue(self.appdata["username"])
        gridauth.Add(self.txtctrl_username, 0, wx.ALL | wx.EXPAND, 5)
        labpass = wx.StaticText(tabFive, wx.ID_ANY, _("Password"))
        gridauth.Add(labpass, 0, wx.ALL | wx.EXPAND, 5)
        self.txtctrl_pass = wx.TextCtrl(tabFive, wx.ID_ANY, "",
                                        style=wx.TE_PASSWORD, size=(300, -1))
        self.txtctrl_pass.SetValue(self.appdata["password"])
        gridauth.Add(self.txtctrl_pass, 0, wx.ALL | wx.EXPAND, 5)

        labvpass = wx.StaticText(tabFive, wx.ID_ANY, _("Video Password"))
        gridauth.Add(labvpass, 0, wx.ALL | wx.EXPAND, 5)
        self.txtctrl_vpass = wx.TextCtrl(tabFive, wx.ID_ANY, "",
                                         style=wx.TE_PASSWORD, size=(300, -1))
        self.txtctrl_vpass.SetValue(self.appdata["videopassword"])
        gridauth.Add(self.txtctrl_vpass, 0, wx.ALL | wx.EXPAND, 5)
        sizerauth.Add(gridauth, 0, wx.ALL | wx.EXPAND, 5)

        tabFive.SetSizer(sizerauth)
        notebook.AddPage(tabFive, _("Authentication"))

        # ----- confirm buttons section
        grdBtn = wx.GridSizer(1, 2, 0, 0)
        grdhelp = wx.GridSizer(1, 1, 0, 0)
        btn_help = wx.Button(self, wx.ID_HELP, "")
        grdhelp.Add(btn_help, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        grdBtn.Add(grdhelp)
        grdexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "")
        grdexit.Add(btn_cancel, 0, wx.ALIGN_CENTER_VERTICAL)
        btn_ok = wx.Button(self, wx.ID_OK, "")
        grdexit.Add(btn_ok, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        grdBtn.Add(grdexit, flag=wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, border=5)
        sizer_base.Add(grdBtn, 0, wx.EXPAND)

        # ----- Properties
        if self.appdata['ostype'] == 'Darwin':
            labdown.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labdwmsg.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labexdtitle.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labproxtitle.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labproxy.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            labdown.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labdwmsg.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labexdtitle.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labproxtitle.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labproxy.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self.SetTitle(_("YouTube Downloader Preferences"))

        # ------ set sizer
        self.SetMinSize((600, 550))
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_downloadfile, self.btn_YDLpath)
        self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)
        self.Bind(wx.EVT_TEXT, self.on_ext_downl, self.txtctrl_extdw)
        self.Bind(wx.EVT_TEXT, self.on_ext_downl_args, self.txtctrl_extdw_args)
        # --------------------------------------------#

    def on_downloadfile(self, event):
        """set up a custom user path for file downloads"""

        dlg = wx.DirDialog(self, _("Choose Destination"),
                           self.appdata['ydlp-outputdir'], wx.DD_DEFAULT_STYLE
                           )
        if dlg.ShowModal() == wx.ID_OK:
            self.txtctrl_YDLpath.Clear()
            getpath = self.appdata['getpath'](dlg.GetPath())
            self.txtctrl_YDLpath.AppendText(getpath)
            self.settings['ydlp-outputdir'] = getpath
            dlg.Destroy()
    # ---------------------------------------------------------------------#

    def on_ext_downl(self, event):
        """
        Event on entering executable path of external downloader
        """
        val = str(self.txtctrl_extdw.GetValue()).strip()
        downloader = None if val in ("", "None", "none") else val
        self.settings["external_downloader"] = downloader
    # -------------------------------------------------------------------#

    def on_ext_downl_args(self, event):
        """
        Event on entering arguments for external downloader
        """
        val = str(self.txtctrl_extdw_args.GetValue()).strip()
        args = None if val in ("", "None", "none") else val.split()
        self.settings["external_downloader_args"] = args
    # -------------------------------------------------------------------#

    def on_help(self, event):
        """
        Open default web browser via Python Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        if self.appdata['GETLANG'] in self.appdata['SUPP_LANGs']:
            lang = self.appdata['GETLANG'].split('_')[0]
            page = (f'https://jeanslack.github.io/Videomass/Pages/User-guide-'
                    f'languages/{lang}/2-Startup_and_Setup_{lang}.pdf')
        else:
            page = ('https://jeanslack.github.io/Videomass/Pages/User-guide-'
                    'languages/en/2-Startup_and_Setup_en.pdf')

        webbrowser.open(page)
    # --------------------------------------------------------------------#

    def on_cancel(self, event):
        """
        Close event
        """
        event.Skip()
    # --------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Writes the new changes to configuration file
        aka `settings.json` and updates `appdata` dict.
        """
        self.settings['add_metadata'] = self.ckbx_meta.GetValue()
        self.settings['embed_thumbnails'] = self.ckbx_thumb.GetValue()
        self.settings['playlistsubfolder'] = self.ckbx_playlist.GetValue()
        self.settings['ssl_certificate'] = self.ckbx_ssl.GetValue()
        self.settings['overwr_dl_files'] = self.ckbx_ow.GetValue()
        self.settings['include_ID_name'] = self.ckbx_id.GetValue()
        self.settings['restrict_fname'] = self.ckbx_limitfn.GetValue()
        self.settings['proxy'] = self.txtctrl_proxy.GetValue()
        self.settings['username'] = self.txtctrl_username.GetValue()
        self.settings['password'] = self.txtctrl_pass.GetValue()
        self.settings['videopassword'] = self.txtctrl_vpass.GetValue()

        self.confmanager.write_options(**self.settings)
        self.appdata.update(self.settings)
        event.Skip()
