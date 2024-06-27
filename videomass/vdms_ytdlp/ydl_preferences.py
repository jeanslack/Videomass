# -*- coding: UTF-8 -*-
"""
Name: ydl_preferences.py
Porpose: YouTube Downloader setup dialog
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Apr.13.2024
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
import os
import webbrowser
import wx
import wx.lib.agw.hyperlink as hpl
from videomass.vdms_sys.settings_manager import ConfigManager


class Ytdlp_Options(wx.Dialog):
    """
    Represents settings and configuration
    storing of the YouTube Downloader.
    """
    # -----------------------------------------------------------------

    def __init__(self, parent):
        """
        self.appdata: (dict) default settings already loaded.
        self.confmanager: instance to ConfigManager class
        self.sett: (dict) current user settings from file conf.

        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.confmanager = ConfigManager(self.appdata['fileconfpath'])
        self.sett = self.confmanager.read_options()

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE
                           | wx.RESIZE_BORDER
                           )
        # ----------------------------set notebook
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        notebook = wx.Notebook(self, wx.ID_ANY, style=0)
        sizer_base.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)

        # -----tab 1
        tabOne = wx.Panel(notebook, wx.ID_ANY)
        sizerGen = wx.BoxSizer(wx.VERTICAL)
        sizerGen.Add((0, 10))
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
        sizerFiles.Add((0, 10))
        msg = _("Where do you prefer to save your downloads?")
        labdown = wx.StaticText(tabTwo, wx.ID_ANY, msg)
        sizerFiles.Add(labdown, 0, wx.ALL | wx.EXPAND, 5)
        sizerFiles.Add((0, 10))
        sizeYDLdirdest = wx.BoxSizer(wx.HORIZONTAL)
        sizerFiles.Add(sizeYDLdirdest, 0, wx.EXPAND)
        self.txtctrl_YDLpath = wx.TextCtrl(tabTwo, wx.ID_ANY, "",
                                           style=wx.TE_READONLY
                                           )
        sizeYDLdirdest.Add(self.txtctrl_YDLpath, 1, wx.LEFT | wx.CENTER, 5)
        self.txtctrl_YDLpath.AppendText(self.appdata['ydlp-outputdir'])
        self.btn_YDLpath = wx.Button(tabTwo, wx.ID_ANY, _('Change'))
        sizeYDLdirdest.Add(self.btn_YDLpath, 0, wx.RIGHT | wx.LEFT
                           | wx.ALIGN_CENTER, 5)
        descr = _("Auto-create subdirectories when downloading playlists")
        self.ckbx_playlist = wx.CheckBox(tabTwo, wx.ID_ANY, (descr))
        self.ckbx_playlist.SetValue(self.appdata['playlistsubfolder'])
        sizerFiles.Add(self.ckbx_playlist, 0, wx.ALL, 5)
        tabTwo.SetSizer(sizerFiles)
        notebook.AddPage(tabTwo, _("File Preferences"))

        # -----tab 3
        tabThree = wx.Panel(notebook, wx.ID_ANY)
        sizerextdown = wx.BoxSizer(wx.VERTICAL)
        sizerextdown.Add((0, 10))
        msg = _("Choosing an external downloader")
        labexdtitle = wx.StaticText(tabThree, wx.ID_ANY, msg)
        sizerextdown.Add(labexdtitle, 0, wx.ALL | wx.EXPAND, 5)
        msg = (_("In addition to the default `native` one, yt-dlp can use the "
                 "following external downloaders:\n"
                 "`aria2c`, `avconv`, `axel`, `curl`, `ffmpeg`, `httpie`, "
                 "`wget`.\nPlease note that using an external downloader the "
                 "download status information may not be available."
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
        notebook.AddPage(tabThree, _("Download Options"))

        # -----tab 4
        tabFour = wx.Panel(notebook, wx.ID_ANY)
        sizernet = wx.BoxSizer(wx.VERTICAL)
        sizernet.Add((0, 10))
        msg = _("Using a proxy server")
        labproxtitle = wx.StaticText(tabFour, wx.ID_ANY, msg)
        sizernet.Add(labproxtitle, 0, wx.ALL | wx.EXPAND, 5)
        proex = 'socks5://user:pass@127.0.0.1:1080/'
        msg = (_('Use the specified HTTP/HTTPS/SOCKS proxy. To enable SOCKS '
                 'proxy, specify a proper\nscheme, e.g.\t{}\nLeave the text '
                 'field blank for direct connection.').format(proex))
        labproxy = wx.StaticText(tabFour, wx.ID_ANY, (msg))
        sizernet.Add(labproxy, 0, wx.ALL, 5)
        sizernet.Add((0, 20))

        gridproxy = wx.FlexGridSizer(1, 2, 0, 0)
        proxylab = wx.StaticText(tabFour, wx.ID_ANY, _("Proxy"))
        gridproxy.Add(proxylab, 0, wx.ALL | wx.EXPAND, 5)
        self.txtctrl_proxy = wx.TextCtrl(tabFour, wx.ID_ANY, "",
                                         size=(450, -1))
        self.txtctrl_proxy.SetValue(self.appdata["proxy"])
        gridproxy.Add(self.txtctrl_proxy, 0, wx.ALL | wx.EXPAND, 5)
        sizernet.Add(gridproxy, 0, wx.ALL | wx.EXPAND, 5)
        tabFour.SetSizer(sizernet)
        notebook.AddPage(tabFour, _("Network"))
        # -----tab 5
        tabFive = wx.Panel(notebook, wx.ID_ANY)
        sizergeo = wx.BoxSizer(wx.VERTICAL)
        sizergeo.Add((0, 10))
        msg = _("Geo-restriction options")
        labgeoproxtitle = wx.StaticText(tabFive, wx.ID_ANY, msg)
        sizergeo.Add(labgeoproxtitle, 0, wx.ALL | wx.EXPAND, 5)
        msg = (_('Use the following options to try bypassing '
                 'geographic restriction.'))
        labgeogeneral = wx.StaticText(tabFive, wx.ID_ANY, (msg))
        sizergeo.Add(labgeogeneral, 0, wx.ALL, 5)
        sizergeo.Add((0, 20))
        gridgeo = wx.FlexGridSizer(4, 2, 0, 0)
        labgeoproxy = wx.StaticText(tabFive, wx.ID_ANY,
                                    _("Geo verification proxy"))
        gridgeo.Add(labgeoproxy, 0, wx.ALL | wx.EXPAND, 5)
        self.txtctrl_geoproxy = wx.TextCtrl(tabFive, wx.ID_ANY, "",
                                            size=(450, -1))
        tip = _('URL of the proxy to use for IP address verification '
                'on geo-restricted sites.')
        self.txtctrl_geoproxy.SetToolTip(tip)
        self.txtctrl_geoproxy.SetValue(self.appdata["geo_verification_proxy"])
        gridgeo.Add(self.txtctrl_geoproxy, 0, wx.ALL | wx.EXPAND, 5)
        labgeobypass = wx.StaticText(tabFive, wx.ID_ANY, _("Geo bypass"))
        gridgeo.Add(labgeobypass, 0, wx.ALL | wx.EXPAND, 5)
        self.txtctrl_geobypass = wx.TextCtrl(tabFive, wx.ID_ANY, "",
                                             size=(450, -1))
        tip = (_('Bypass geographic restriction via faking X-Forwarded-For '
                 'HTTP header. One of "default" (only when known to be '
                 'useful), or "never"'))
        self.txtctrl_geobypass.SetToolTip(tip)
        self.txtctrl_geobypass.SetValue(self.appdata["geo_bypass"])
        gridgeo.Add(self.txtctrl_geobypass, 0, wx.ALL | wx.EXPAND, 5)
        labgeocountry = wx.StaticText(tabFive, wx.ID_ANY,
                                      _("Geo bypass country"))
        gridgeo.Add(labgeocountry, 0, wx.ALL | wx.EXPAND, 5)
        self.txtctrl_geocountry = wx.TextCtrl(tabFive, wx.ID_ANY, "",
                                              size=(450, -1))
        tip = (_('Two-letter ISO 3166-2 country code that will be used for '
                 'explicit geographic restriction bypassing via faking '
                 'X-Forwarded-For HTTP header.'))
        self.txtctrl_geocountry.SetToolTip(tip)
        self.txtctrl_geocountry.SetValue(self.appdata["geo_bypass_country"])
        gridgeo.Add(self.txtctrl_geocountry, 0, wx.ALL | wx.EXPAND, 5)

        labgeoipblock = wx.StaticText(tabFive, wx.ID_ANY,
                                      _("Geo bypass ip block"))
        gridgeo.Add(labgeoipblock, 0, wx.ALL | wx.EXPAND, 5)
        self.txtctrl_geoipblock = wx.TextCtrl(tabFive, wx.ID_ANY, "",
                                              size=(450, -1))
        tip = (_('IP range in CIDR notation that will be used similarly to '
                 'geo_bypass_country'))
        self.txtctrl_geoipblock.SetToolTip(tip)
        self.txtctrl_geoipblock.SetValue(self.appdata["geo_bypass_ip_block"])
        gridgeo.Add(self.txtctrl_geoipblock, 0, wx.ALL | wx.EXPAND, 5)
        sizergeo.Add(gridgeo, 0, wx.ALL | wx.EXPAND, 5)
        tabFive.SetSizer(sizergeo)
        notebook.AddPage(tabFive, _("Geo-Restriction"))
        # -----tab 6
        tabSix = wx.Panel(notebook, wx.ID_ANY)
        sizerauth = wx.BoxSizer(wx.VERTICAL)
        sizerauth.Add((0, 10))
        msg = _("Authentication with login credentials")
        labauthtitle = wx.StaticText(tabSix, wx.ID_ANY, msg)
        sizerauth.Add(labauthtitle, 0, wx.ALL | wx.EXPAND, 5)
        msg = (_('If you need to login with your credentials please note '
                 'that login with password is not\nsupported for some '
                 'websites (e.g. YouTube, CloudFlare). In this case you can '
                 'include a\ncookie file for authentication (see cookies '
                 'tab).'))
        labauthgen = wx.StaticText(tabSix, wx.ID_ANY, (msg))
        sizerauth.Add(labauthgen, 0, wx.ALL, 5)
        sizerauth.Add((0, 20))
        gridauth = wx.FlexGridSizer(3, 2, 0, 0)
        labuser = wx.StaticText(tabSix, wx.ID_ANY, _("Username"))
        gridauth.Add(labuser, 0, wx.ALL | wx.EXPAND, 5)
        self.txtctrl_username = wx.TextCtrl(tabSix, wx.ID_ANY, "",
                                            size=(300, -1))
        tip = _('Username for authentication purposes')
        self.txtctrl_username.SetToolTip(tip)
        self.txtctrl_username.SetValue(self.appdata["username"])
        gridauth.Add(self.txtctrl_username, 0, wx.ALL | wx.EXPAND, 5)
        labpass = wx.StaticText(tabSix, wx.ID_ANY, _("Password"))
        gridauth.Add(labpass, 0, wx.ALL | wx.EXPAND, 5)
        self.txtctrl_pass = wx.TextCtrl(tabSix, wx.ID_ANY, "",
                                        style=wx.TE_PASSWORD, size=(300, -1))
        tip = _('Password for authentication purposes')
        self.txtctrl_pass.SetToolTip(tip)
        self.txtctrl_pass.SetValue(self.appdata.get("password", ''))
        gridauth.Add(self.txtctrl_pass, 0, wx.ALL | wx.EXPAND, 5)

        labvpass = wx.StaticText(tabSix, wx.ID_ANY, _("Video Password"))
        gridauth.Add(labvpass, 0, wx.ALL | wx.EXPAND, 5)
        self.txtctrl_vpass = wx.TextCtrl(tabSix, wx.ID_ANY, "",
                                         style=wx.TE_PASSWORD, size=(300, -1))
        tip = _('Password for accessing a video')
        self.txtctrl_vpass.SetToolTip(tip)
        self.txtctrl_vpass.SetValue(self.appdata.get("videopassword", ''))
        gridauth.Add(self.txtctrl_vpass, 0, wx.ALL | wx.EXPAND, 5)
        sizerauth.Add(gridauth, 0, wx.ALL | wx.EXPAND, 5)
        tabSix.SetSizer(sizerauth)
        notebook.AddPage(tabSix, _("Authentication"))

        # -----tab 7
        tabSev = wx.Panel(notebook, wx.ID_ANY)
        sizercook = wx.BoxSizer(wx.VERTICAL)
        sizercook.Add((0, 10))
        msg = _("Using cookies to gain access to websites")
        labcooktitle = wx.StaticText(tabSev, wx.ID_ANY, msg)
        sizercook.Add(labcooktitle, 0, wx.ALL | wx.EXPAND, 5)
        msg = (_("Here you can pass your `Netscape HTTP Cookie File` in order "
                 "to access websites that require authentication.\nIf you "
                 "don't know how to obtain this type of file, you can let "
                 "the application try to extract it from "
                 "your browser\nautomatically. The currently supported "
                 "browsers are: brave, chrome, chromium, edge, firefox, "
                 "opera, safari, vivaldi.\n\nFor more information please "
                 "consult the documentation at the following link:"))
        labcookgen = wx.StaticText(tabSev, wx.ID_ANY, (msg))
        sizercook.Add(labcookgen, 0, wx.ALL, 5)
        url1 = ("https://github.com/yt-dlp/yt-dlp/wiki/"
                "FAQ#how-do-i-pass-cookies-to-yt-dlp")
        link1 = hpl.HyperLinkCtrl(tabSev, -1, url1, URL=url1)
        sizercook.Add(link1, 0, wx.LEFT | wx.EXPAND, 15)
        sizercook.Add((0, 20))
        sizercookie = wx.BoxSizer(wx.HORIZONTAL)

        msg = _('Allow cookies for authentication')
        self.ckbx_usecook = wx.CheckBox(tabSev, wx.ID_ANY, msg)
        self.ckbx_usecook.SetValue(self.appdata['use_cookie_file'])
        sizercook.Add(self.ckbx_usecook, 0, wx.LEFT, 5)
        labcookie = wx.StaticText(tabSev, wx.ID_ANY, _("Cookie file"))
        sizercookie.Add(labcookie, 0, wx.LEFT | wx.TOP | wx.EXPAND, 5)
        self.txtctrl_cook = wx.TextCtrl(tabSev, wx.ID_ANY, "",
                                        style=wx.TE_READONLY
                                        )
        self.txtctrl_cook.SetValue(self.appdata["cookiefile"])
        tip = _('File name from where cookies should be read and dumped to')
        self.txtctrl_cook.SetToolTip(tip)
        sizercookie.Add(self.txtctrl_cook, 1, wx.ALL | wx.EXPAND, 5)
        self.btn_cookie = wx.Button(tabSev, wx.ID_ANY, _('Browse'))
        sizercookie.Add(self.btn_cookie, 0, wx.RIGHT | wx.ALIGN_CENTER, 5)
        sizercook.Add(sizercookie, 0, wx.ALL | wx.EXPAND, 5)
        msg = _('Extract cookies automatically from your browser')
        self.ckbx_autocook = wx.CheckBox(tabSev, wx.ID_ANY, msg)
        self.ckbx_autocook.SetValue(self.appdata['autogen_cookie_file'])
        sizercook.Add(self.ckbx_autocook, 0, wx.ALL, 5)
        sizerautocook = wx.BoxSizer(wx.HORIZONTAL)
        self.labautocook = wx.StaticText(tabSev, wx.ID_ANY,
                                         _("Web Browser"))
        sizerautocook.Add(self.labautocook, 0, wx.LEFT | wx.TOP | wx.CENTER, 5)
        suppwebbrowser = ('brave', 'chrome', 'chromium', 'edge',
                          'firefox', 'opera', 'safari', 'vivaldi')
        self.cmbx_browser = wx.ComboBox(tabSev, wx.ID_ANY,
                                        choices=suppwebbrowser,
                                        size=(-1, -1),
                                        style=wx.CB_DROPDOWN | wx.CB_READONLY
                                        )
        self.cmbx_browser.SetValue(self.appdata['webbrowser'])
        sizerautocook.Add(self.cmbx_browser, 0, wx.LEFT | wx.TOP
                          | wx.CENTRE, 5)
        if not self.appdata['autogen_cookie_file']:
            self.labautocook.Disable(), self.cmbx_browser.Disable()
        if not self.sett['use_cookie_file']:
            self.btn_cookie.Disable(), self.ckbx_autocook.Disable()
            self.txtctrl_cook.Disable()
        sizercook.Add(sizerautocook, 0, wx.LEFT | wx.EXPAND, 5)
        tabSev.SetSizer(sizercook)
        notebook.AddPage(tabSev, _("Cookies"))
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
            labgeoproxtitle.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL,
                                            wx.BOLD))
            labgeogeneral.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labauthtitle.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labauthgen.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labcooktitle.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labcookgen.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            labdown.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labdwmsg.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labexdtitle.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labproxtitle.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labproxy.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labgeoproxtitle.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL,
                                            wx.BOLD))
            labgeogeneral.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labauthtitle.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labauthgen.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
            labcooktitle.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            labcookgen.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self.SetTitle(_("YouTube Downloader Options"))

        # ------ set sizer
        self.SetMinSize((700, 550))
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
        self.Bind(wx.EVT_BUTTON, self.on_cookie_file, self.btn_cookie)
        self.Bind(wx.EVT_CHECKBOX, self.on_autogen_cookie, self.ckbx_autocook)
        self.Bind(wx.EVT_COMBOBOX, self.on_autogen_cookie, self.cmbx_browser)
        self.Bind(wx.EVT_CHECKBOX, self.on_enable_cookie, self.ckbx_usecook)
        # --------------------------------------------#

    def on_enable_cookie(self, event):
        """
        Event triggered on enabling cookies CheckBox.
        """
        if self.ckbx_usecook.GetValue():
            self.ckbx_autocook.Enable()
            self.btn_cookie.Enable()
            self.txtctrl_cook.Enable()
            self.sett['use_cookie_file'] = True
        else:
            ckf = self.txtctrl_cook.GetValue()
            if os.path.exists(ckf) and os.path.isfile(ckf):
                if wx.MessageBox(_("Do you want to remove the current "
                                   "cookie file from your system?"),
                                 _('Please confirm'), wx.ICON_QUESTION
                                 | wx.CANCEL | wx.YES_NO, self) == wx.YES:
                    os.remove(ckf)
            self.ckbx_autocook.SetValue(False)
            self.on_autogen_cookie(None)
            self.ckbx_autocook.Disable()
            self.btn_cookie.Disable()
            self.txtctrl_cook.SetValue("")
            self.txtctrl_cook.Disable()
            self.sett['use_cookie_file'] = False
    # ---------------------------------------------------------------------#

    def on_autogen_cookie(self, event):
        """
        Event on checking Generate a cookie file from web
        browser CheckBox.
        """
        if self.ckbx_autocook.GetValue():
            self.labautocook.Enable(), self.cmbx_browser.Enable()
            self.sett['autogen_cookie_file'] = True
            self.sett['webbrowser'] = self.cmbx_browser.GetStringSelection()
            path = os.path.join(self.appdata["confdir"], 'cookies.txt')
            self.sett["cookiefile"] = path
            self.txtctrl_cook.SetValue(path)
            self.sett["cookiesfrombrowser"] = (self.sett['webbrowser'],
                                               None, None, None)

        else:
            self.labautocook.Disable(), self.cmbx_browser.Disable()
            self.sett['autogen_cookie_file'] = False
            self.sett["cookiefile"] = ""
            self.txtctrl_cook.SetValue("")
            self.sett["cookiesfrombrowser"] = (None, None, None, None)
    # ---------------------------------------------------------------------#

    def on_web_browser(self, event):
        """
        Event on choice a web browser item from ComboBox
        """
        self.sett['webbrowser'] = self.cmbx_browser.GetStringSelection()
        self.sett["cookiesfrombrowser"] = (self.sett['webbrowser'],
                                           None, None, None)
    # ---------------------------------------------------------------------#

    def on_cookie_file(self, event):
        """
        Event triggered clicking on Button to
        select a new cookies.txt file.
        """
        fmt = '*cookies.txt'
        wild = f"Netscape HTTP Cookie File ({fmt})|{fmt}"
        with wx.FileDialog(self, _("Locate your cookie file"),
                           defaultDir=os.path.expanduser('~'),
                           wildcard=wild,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fdlg:
            if fdlg.ShowModal() == wx.ID_CANCEL:
                return
            filename = fdlg.GetPath()
            self.txtctrl_cook.SetValue(filename)
    # ---------------------------------------------------------------------#

    def on_downloadfile(self, event):
        """
        Event clicking on Button to setting up a custom
        path where save downloads.
        """
        dlg = wx.DirDialog(self, _("Choose Destination"),
                           self.appdata['ydlp-outputdir'], wx.DD_DEFAULT_STYLE
                           )
        if dlg.ShowModal() == wx.ID_OK:
            self.txtctrl_YDLpath.Clear()
            getpath = self.appdata['getpath'](dlg.GetPath())
            self.txtctrl_YDLpath.AppendText(getpath)
            self.sett['ydlp-outputdir'] = getpath
            dlg.Destroy()
    # ---------------------------------------------------------------------#

    def on_ext_downl(self, event):
        """
        Event on entering executable path of external downloader
        """
        val = str(self.txtctrl_extdw.GetValue()).strip()
        downloader = None if val in ("", "None", "none") else val
        self.sett["external_downloader"] = downloader
    # -------------------------------------------------------------------#

    def on_ext_downl_args(self, event):
        """
        Event on entering arguments for external downloader
        """
        val = str(self.txtctrl_extdw_args.GetValue()).strip()
        args = None if val in ("", "None", "none") else val.split()
        self.sett["external_downloader_args"] = args
    # -------------------------------------------------------------------#

    def on_help(self, event):
        """
        Open default web browser via Python Web-browser controller.
        see <https://docs.python.org/3.8/library/webbrowser.html>
        """
        page = ('https://jeanslack.github.io/Videomass/User-guide/'
                'YouTube_Downloader_Options_en.pdf')
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
        if not self.sett['trashdir_loc'].strip():
            self.sett['trashdir_loc'] = self.appdata['trashdir_default']
        self.sett['username'] = self.txtctrl_username.GetValue()
        self.sett['add_metadata'] = self.ckbx_meta.GetValue()
        self.sett['embed_thumbnails'] = self.ckbx_thumb.GetValue()
        self.sett['playlistsubfolder'] = self.ckbx_playlist.GetValue()
        self.sett['ssl_certificate'] = self.ckbx_ssl.GetValue()
        self.sett['overwr_dl_files'] = self.ckbx_ow.GetValue()
        self.sett['include_ID_name'] = self.ckbx_id.GetValue()
        self.sett['restrict_fname'] = self.ckbx_limitfn.GetValue()
        self.sett['proxy'] = self.txtctrl_proxy.GetValue()
        self.sett['geo_verification_proxy'] = self.txtctrl_geoproxy.GetValue()
        self.sett['geo_bypass'] = self.txtctrl_geobypass.GetValue()
        self.sett['geo_bypass_country'] = self.txtctrl_geocountry.GetValue()
        self.sett['geo_bypass_ip_block'] = self.txtctrl_geoipblock.GetValue()
        self.sett['cookiefile'] = self.txtctrl_cook.GetValue()
        self.confmanager.write_options(**self.sett)
        self.appdata.update(self.sett)
        # do not store this data in the configuration file
        self.appdata['password'] = self.txtctrl_pass.GetValue()
        self.appdata['videopassword'] = self.txtctrl_vpass.GetValue()
        event.Skip()
