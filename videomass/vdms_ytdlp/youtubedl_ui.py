# -*- coding: UTF-8 -*-
"""
Name: youtubedl_ui.py
Porpose: youtube-dl user interface
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Apr.29.2024
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
import sys
import itertools
import wx
from videomass.vdms_io.io_tools import youtubedl_getstatistics
from videomass.vdms_utils.utils import integer_to_time as totimesec
from videomass.vdms_utils.get_bmpfromsvg import get_bmp
from videomass.vdms_ytdlp.playlist_indexing import Indexing
from videomass.vdms_ytdlp.subtitles_editor import SubtitleEditor
from videomass.vdms_ytdlp.formatcode import FormatCode
from videomass.vdms_sys.settings_manager import ConfigManager


def from_api_to_cli(data, execpath):
    """
    Revert API arguments to command line options
    """
    if not data["format"]:
        dformat = ''
    else:
        dformat = f'--format "{data["format"]}"'
    opt = (f'"{execpath}" {dformat} --progress-template '
           f'"download-title:%(info.id)s-%(progress.eta)s" '
           f'--newline --compat-options "{data["compat_opts"]}" '
           f'--ignore-errors --ignore-config --no-color ')

    if data['extractaudio']:
        opt += '--extract-audio '
    if data['postprocessors']:
        for pp in data['postprocessors']:
            for key, val in pp.items():
                if 'preferredcodec' in key:
                    opt += f'--audio-format {val} '
                if 'EmbedThumbnail' in val:
                    opt += '--embed-thumbnail '
                if 'FFmpegEmbedSubtitle' in val:
                    opt += '--embed-subs '
    if data['addmetadata']:
        opt += '--embed-metadata '
    if data['external_downloader']:
        opt += f'--downloader "{data["external_downloader"]}" '
    if data['external_downloader_args']:
        dwargs = ' '.join(data["external_downloader_args"])
        opt += (f'--downloader-args "{data["external_downloader"]}:{dwargs}" ')
    if data['noplaylist'] is False:
        opt += '--yes-playlist '
        if data['playlist_items']:
            opt += f'--playlist-items "{data["playlist_items"]}" '
    else:
        opt += '--no-playlist '
    if data['writesubtitles']:
        opt += '--write-subs '
        if data['subtitleslangs'][0]:
            sublang = ','.join(data["subtitleslangs"])
            opt += f'--sub-langs "{sublang}" '
        if data['writeautomaticsub']:
            opt += '--write-auto-subs '
        if data['skip_download']:
            opt += '--skip-download '
    opt += '--restrict-filenames ' if data['restrictfilenames'] else ''
    opt += '--write-thumbnail ' if data['writethumbnail'] else ''
    opt += '--force-overwrites ' if data['overwrites'] else ''
    opt += '--no-check-certificates ' if data['nocheckcertificate'] else ''
    opt += f'--proxy "{data["proxy"]}" ' if data["proxy"] else ''
    if data['geo_verification_proxy']:
        opt += f'--geo-verification-proxy "{data["geo_verification_proxy"]}" '
    geo = (f'{data["geo_bypass"]} {data["geo_bypass_country"]} '
           f'{data["geo_bypass_ip_block"]}')
    if geo.strip():
        opt += f'--xff "{geo}" '
    if data['username']:
        opt += f'--username {data["username"]} '
        opt += f'--password {data["password"]} '
    if data['videopassword']:
        opt += f'--video-password {data["videopassword"]} '
    if data.get("cookiefile"):
        opt += f'--cookies "{data["cookiefile"]}" '
    if data.get("cookiesfrombrowser"):
        opt += f'--cookies-from-browser "{data["cookiesfrombrowser"][0]}" '
    opt += f'--ffmpeg-location "{data["ffmpeg_location"]}" '
    opt += f'--output "{data["outtmpl"]}" '

    return opt


class Downloader(wx.Panel):
    """
    This panel represents the main interface to yt-dlp
    """
    WHITE = '#fbf4f4'  # sb foreground
    VIOLET = '#D64E93'  # activated buttons

    MSG_1 = _('At least one "Format Code" must be checked for each '
              'URL selected in green.')
    # video resolution
    VRES = {('p1080'): ('best[height<=?1080]'),
            ('p720'): ('best[height<=?720]'),
            ('p480'): ('best[height<=?480]'),
            ('p360'): ('best[height<=?360]'),
            ('p240'): ('best[height<=?240]'),
            ('p144'): ('best[height>=?144]'),
            }
    # video qualities best or worst
    VQUAL = {('Best quality video'): ('bestvideo'),
             ('Worst quality video'): ('worstvideo'),
             }
    # precompiled video
    VPCOMP = {('Best precompiled video'): ('bestvideo+bestaudio/best'),
              ('Medium High precompiled video'): ('bestvideo*+bestaudio/best'),
              ('Medium Low precompiled video'): ('18'),
              ('Worst precompiled video'): ('worstvideo+worstaudio/worst'),
              }
    AFORMATS = {("Default"): ("best"),
                ("wav"): ("wav"),
                ("mp3"): ("mp3"),
                ("aac"): ("aac"),
                ("m4a"): ("m4a"),
                ("vorbis"): ("vorbis"),
                ("opus"): ("opus"),
                ("flac"): ("flac"),
                }
    # audio qualities best or worst
    AQUAL = {('Best quality audio'): ('bestaudio'),
             ('Worst quality audio'): ('worstaudio')}

    CHOICE = [_('Precompiled Videos'),
              _('Download videos by resolution'),
              _('Download split audio and video'),
              _('Download Audio only'),
              _('Download by format code')
              ]
    # -----------------------------------------------------------------#

    def __init__(self, parent):
        """
        The first item of the self.info is a complete list of all
        informations getting by extract_info method from youtube_dl
        module.
        """
        get = wx.GetApp()  # get data from bootstrap
        icons = get.iconset
        self.appdata = get.appset
        self.parent = parent
        self.red = self.appdata['colorscheme']['ERR1']  # code err + sb error
        confmanager = ConfigManager(self.appdata['fileconfpath'])
        sett = confmanager.read_options()

        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up
            bmplistindx = get_bmp(icons['playlist'], ((16, 16)))
            bmpsubtitles = get_bmp(icons['subtitles'], ((16, 16)))
        else:
            bmplistindx = wx.Bitmap(icons['playlist'], wx.BITMAP_TYPE_ANY)
            bmpsubtitles = wx.Bitmap(icons['subtitles'], wx.BITMAP_TYPE_ANY)

        self.opt = {("NO_PLAYLIST"): True,
                    ("V_QUALITY"): Downloader.VPCOMP['Best precompiled video'],
                    ("A_FORMAT"): "best",
                    ("A_QUALITY"): "bestaudio",
                    ("SUBS"): sett['subtitles_options'],
                    }
        self.plidx = {'': ''}
        self.info = []  # has data information for Statistics button
        self.format_dict = {}  # format codes order with URL matching
        self.quality = 'best'
        self.oldwx = None  # test result of hasattr EVT_LIST_ITEM_CHECKED

        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        # ------------- choice and comboboxes
        fgs1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(fgs1, 0, wx.ALL | wx.CENTRE, 5)
        self.choice = wx.Choice(self, wx.ID_ANY,
                                choices=Downloader.CHOICE,
                                size=(-1, -1),
                                )
        self.choice.SetSelection(0)
        fgs1.Add(self.choice, 0, wx.LEFT | wx.CENTRE, 5)

        self.ckbx_pl = wx.CheckBox(self, wx.ID_ANY,
                                   (_('Include playlists'))
                                   )
        fgs1.Add(self.ckbx_pl, 0, wx.LEFT | wx.CENTRE, 20)
        self.btn_plidx = wx.Button(self, wx.ID_ANY, "", size=(40, -1))
        self.btn_plidx.SetToolTip(_('Playlist Editor'))
        self.btn_plidx.SetBitmap(bmplistindx, wx.LEFT)
        fgs1.Add(self.btn_plidx, 0, wx.LEFT | wx.CENTRE, 2)
        self.btn_plidx.Disable()
        self.btn_subeditor = wx.Button(self, wx.ID_ANY, "",
                                       size=(40, -1))
        self.btn_subeditor.SetBitmap(bmpsubtitles, wx.LEFT)
        self.btn_subeditor.SetToolTip(_('Subtitles Editor'))
        fgs1.Add(self.btn_subeditor, 0, wx.LEFT | wx.CENTRE, 20)
        if sett['subtitles_options']['writesubtitles']:
            self.btn_subeditor.SetBackgroundColour(
                wx.Colour(Downloader.VIOLET))

        # ------------- quality pref
        box = wx.StaticBox(self, wx.ID_ANY, _('Quality settings'))
        boxoptions = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizer_base.Add(boxoptions, 0, wx.ALL | wx.EXPAND, 5)
        fgs2 = wx.BoxSizer(wx.HORIZONTAL)
        boxoptions.Add(fgs2, 0, wx.ALL | wx.EXPAND, 0)
        self.cmbx_vq = wx.ComboBox(self, wx.ID_ANY,
                                   choices=(),
                                   size=(-1, -1), style=wx.CB_DROPDOWN
                                   | wx.CB_READONLY
                                   )
        # grid_v.Add((20, 20), 0,)
        fgs2.Add(self.cmbx_vq, 0, wx.ALL | wx.CENTRE, 5)
        tip = (_('When not available, the chosen video resolution will '
                 'be replaced with the closest one'))
        self.cmbx_vq.SetToolTip(tip)

        txtvformat = wx.StaticText(self, wx.ID_ANY, _('Video format:'))
        fgs2.Add(txtvformat, 0, wx.LEFT | wx.CENTRE, 5)
        self.cmbx_vformat = wx.ComboBox(self, wx.ID_ANY,
                                        choices=['Default', 'webm', 'mp4'],
                                        size=(-1, -1), style=wx.CB_DROPDOWN
                                        | wx.CB_READONLY
                                        )
        self.cmbx_vformat.SetSelection(0)
        fgs2.Add(self.cmbx_vformat, 0, wx.ALL | wx.CENTRE, 5)
        fgs2.Add((20, 20), 0,)
        self.cmbx_aq = wx.ComboBox(self, wx.ID_ANY,
                                   choices=list(Downloader.AQUAL.keys()),
                                   size=(-1, -1),
                                   style=wx.CB_DROPDOWN
                                   | wx.CB_READONLY
                                   )
        self.cmbx_aq.SetSelection(0)
        self.cmbx_aq.Disable()
        # grid_v.Add((20, 20), 0,)
        fgs2.Add(self.cmbx_aq, 0, wx.ALL | wx.CENTRE, 5)

        txtaformat = wx.StaticText(self, wx.ID_ANY, _('Audio format:'))
        fgs2.Add(txtaformat, 0, wx.LEFT | wx.CENTRE, 5)
        self.cmbx_af = wx.ComboBox(self, wx.ID_ANY,
                                   choices=list(Downloader.AFORMATS.keys()),
                                   size=(-1, -1),
                                   style=wx.CB_DROPDOWN
                                   | wx.CB_READONLY
                                   )
        self.cmbx_af.Disable()
        self.cmbx_af.SetSelection(0)
        fgs2.Add(self.cmbx_af, 0, wx.ALL | wx.CENTRE, 5)

        # ------------- simple listctrl
        box = wx.StaticBox(self, wx.ID_ANY, '')
        boxpanel = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizer_base.Add(boxpanel, 1, wx.ALL | wx.EXPAND, 5)
        self.panel_cod = FormatCode(self, self.format_dict)
        self.panel_cod.enable_widgets(False)
        boxpanel.Add(self.panel_cod, 1, wx.EXPAND)
        self.SetSizer(sizer_base)
        self.Layout()

        # ----------------------Binder (EVT)----------------------#
        self.choice.Bind(wx.EVT_CHOICE, self.on_choicebox)
        self.cmbx_vq.Bind(wx.EVT_COMBOBOX, self.on_vquality)
        self.cmbx_vformat.Bind(wx.EVT_COMBOBOX, self.on_quality)
        self.cmbx_af.Bind(wx.EVT_COMBOBOX, self.on_aformat)
        self.cmbx_aq.Bind(wx.EVT_COMBOBOX, self.on_aquality)
        self.ckbx_pl.Bind(wx.EVT_CHECKBOX, self.on_playlist)
        self.btn_plidx.Bind(wx.EVT_BUTTON, self.on_playlist_idx)
        self.btn_subeditor.Bind(wx.EVT_BUTTON, self.on_subtitles_editor)

    # ----------------------------------------------------------------------
    def on_subtitles_editor(self, event):
        """
        Event by clicking on the subtitles button
        """
        with SubtitleEditor(self, self.opt["SUBS"]) as subeditor:
            if subeditor.ShowModal() == wx.ID_OK:
                data = subeditor.getvalue()
                self.opt["SUBS"] = data
        if not self.opt["SUBS"]["writesubtitles"]:
            self.btn_subeditor.SetBackgroundColour(wx.NullColour)
        else:
            self.btn_subeditor.SetBackgroundColour(
                wx.Colour(Downloader.VIOLET))
    # ----------------------------------------------------------------------

    def clear_data_list(self, changed):
        """
        Reset all required data if `changed` arg is True,
        delete data and set to Disable otherwise.
        """
        if not self.parent.data_url:
            del self.info[:]
            self.format_dict.clear()
            self.panel_cod.fcode.DeleteAllItems()
            self.on_choicebox(self, statusmsg=False)
        else:
            if changed:
                self.ckbx_pl.SetValue(False)
                self.on_playlist(self)
                self.panel_cod.fcode.DeleteAllItems()
                self.choice.SetSelection(0)
                self.on_choicebox(self, statusmsg=False)
                del self.info[:]
                self.format_dict.clear()
    # -----------------------------------------------------------------#

    def get_statistics(self, link):
        """
        Get media URLs informations by generator object
        `youtubedl_getstatistics`: This method `Return` a
        two elements list ['ERROR', (message error)]
        if `meta[1]` (error), [None, dictobject] otherwise.
        Check the first item of list to recognize the exit
        status, which is 'ERROR' or None.
        """
        kwa = self.default_statistics_options()
        data = youtubedl_getstatistics(link,
                                       kwa,
                                       parent=self.GetParent(),
                                       )
        for meta in data:
            if meta[1]:
                return ('ERROR', meta[1])

            if 'entries' in meta[0]:
                try:
                    meta[0]['entries'][0]  # don't parse all playlist
                except IndexError:
                    pass
            if 'duration' in meta[0]:

                ftime = (f"{totimesec(round(meta[0]['duration'] * 1000))} "
                         f"({meta[0]['duration']} sec.)")
            else:
                ftime = 'N/A'

            date = meta[0].get('upload_date')
            return (None, {'url': link,
                           'title': meta[0].get('title'),
                           'categories': meta[0].get('categories'),
                           'license': meta[0].get('license'),
                           'format': meta[0].get('format'),
                           'upload_date': date,
                           'uploader': meta[0].get('uploader'),
                           'view': meta[0].get('view_count'),
                           'like': meta[0].get('like_count'),
                           'dislike': meta[0].get('dislike_count'),
                           'avr_rat': meta[0].get('average_rating'),
                           'id': meta[0].get('id'),
                           'duration': ftime,
                           'description': meta[0].get('description'),
                           })
    # -----------------------------------------------------------------#

    def on_show_statistics(self):
        """
        show URL data information. This method is called by
        main frame when the 'Statistics' button is pressed.
        """
        if not self.info:
            for link in self.parent.data_url:
                ret = self.get_statistics(link)
                if ret[0] == 'ERROR':
                    wx.MessageBox(ret[1], _('Videomass - Error!'),
                                  wx.ICON_ERROR)
                    del self.info[:]
                    return None
                self.info.append(ret[1])

        return self.info
    # -----------------------------------------------------------------#

    def on_format_codes(self):
        """
        Check data given from `self.panel_cod.set_formatcode()` method
        which allow to enabling download by "Format Code".
        """
        if self.panel_cod.fcode.GetItemCount():  # not changed, already set
            return None
        kwa = self.default_statistics_options()

        def _error(msg, icon, cap):
            wx.MessageBox(msg, cap, icon, self)
            self.choice.SetSelection(0)
            self.on_choicebox(self, False)
            return True

        for url in self.parent.data_url:
            for unsupp in ('/playlists',
                           '/channels',
                           '/playlist',
                           '/channel',
                           '/videos',
                           ):
                if unsupp in url:
                    msg = _("Unable to get format codes on {0}, "
                            "unsupported URL:\n\n{1}"
                            ).format(unsupp.split('/')[1], url)
                    return _error(msg, wx.ICON_WARNING,
                                  _('Videomass - Warning!'))

        ret = self.panel_cod.set_formatcode(self.parent.data_url, kwa)
        if ret:
            return _error(ret, wx.ICON_ERROR, _('Videomass - Error!'))
        return None
    # -----------------------------------------------------------------#

    def on_choicebox(self, event, statusmsg=True):
        """
        Set widgets on switching choice box

        """
        if statusmsg:
            if not self.parent.sb.GetStatusText() == 'Ready':
                self.parent.statusbar_msg(_('Ready'), None)

        if self.choice.GetSelection() == 0:
            self.cmbx_af.Disable()
            self.cmbx_aq.Disable()
            self.cmbx_vq.Enable()
            self.cmbx_vformat.Disable()
            self.panel_cod.enable_widgets(False)
            self.cmbx_vq.Clear()
            self.cmbx_vq.Append(list(Downloader.VPCOMP.keys()))
            self.cmbx_vq.SetSelection(0)
            self.Layout()
            self.on_vquality(self)

        elif self.choice.GetSelection() == 1:
            self.cmbx_af.Disable()
            self.cmbx_aq.Disable()
            self.cmbx_vq.Enable()
            self.cmbx_vformat.Enable()
            self.panel_cod.enable_widgets(False)
            self.cmbx_vq.Clear()
            self.cmbx_vq.Append(list(Downloader.VRES.keys()))
            self.cmbx_vq.SetSelection(0)
            self.Layout()
            self.on_vquality(self)

        elif self.choice.GetSelection() == 2:
            self.cmbx_af.Disable()
            self.cmbx_aq.Enable()
            self.cmbx_vq.Enable()
            self.cmbx_vformat.Disable()
            self.panel_cod.enable_widgets(False)
            self.cmbx_vq.Clear()
            self.cmbx_vq.Append(list(Downloader.VQUAL.keys()))
            self.cmbx_vq.SetSelection(0)
            self.Layout()
            self.on_vquality(self)

        elif self.choice.GetSelection() == 3:
            self.cmbx_vq.Disable()
            self.cmbx_aq.Enable()
            self.cmbx_af.Enable()
            self.cmbx_vformat.Disable()
            self.panel_cod.enable_widgets(False)
            self.Layout()
            self.on_aformat(self)

        elif self.choice.GetSelection() == 4:
            self.cmbx_vq.Disable()
            self.cmbx_aq.Disable()
            self.cmbx_af.Disable()
            self.cmbx_vformat.Disable()
            self.panel_cod.enable_widgets()
            ret = self.on_format_codes()
            if ret:
                return
            self.Layout()
    # -----------------------------------------------------------------#

    def on_vquality(self, event):
        """
        Set video qualities during combobox event
        """
        if self.choice.GetSelection() == 0:
            self.opt["V_QUALITY"] = Downloader.VPCOMP[self.cmbx_vq.GetValue()]
        elif self.choice.GetSelection() == 1:
            self.opt["V_QUALITY"] = Downloader.VRES[self.cmbx_vq.GetValue()]
        elif self.choice.GetSelection() == 2:
            self.opt["V_QUALITY"] = Downloader.VQUAL[self.cmbx_vq.GetValue()]
        self.on_quality(self)
    # -----------------------------------------------------------------#

    def on_quality(self, event):
        """
        Set preferring video and audio format on combobox event
        """
        vformat = self.cmbx_vformat.GetValue()

        if self.choice.GetSelection() == 0:
            quality = self.opt["V_QUALITY"]
            self.parent.statusbar_msg(f'Quality: {quality}', None)

        elif self.choice.GetSelection() == 1:
            vf = '' if vformat == 'Default' else f'[ext={vformat}]'
            quality = self.opt["V_QUALITY"] + vf
            self.parent.statusbar_msg(f'Quality: {quality}', None)

        elif self.choice.GetSelection() == 2:
            quality = f'{self.opt["V_QUALITY"]},{self.opt["A_QUALITY"]}'
            self.parent.statusbar_msg(f'Quality: {quality}', None)

        elif self.choice.GetSelection() == 3:
            quality = f'{self.opt["A_QUALITY"]}/worst'
            msg = f'Quality: {quality} (format={self.cmbx_af.GetValue()})'
            self.parent.statusbar_msg(msg, None)

        self.quality = quality
    # -----------------------------------------------------------------#

    def on_aformat(self, event):
        """
        Set audio format extension to exporting on combobox event.
        This is related to "Download Audio only" choice.
        """
        self.opt["A_FORMAT"] = Downloader.AFORMATS.get(self.cmbx_af.GetValue())
        self.on_quality(None)
    # -----------------------------------------------------------------#

    def on_aquality(self, event):
        """
        Set audio qualities on combobox event.
        This is related to "Download spilt audio and video" and
        "Download Audio only" choices.
        """
        self.opt["A_QUALITY"] = Downloader.AQUAL.get(self.cmbx_aq.GetValue())
        self.on_quality(self)
    # -----------------------------------------------------------------#

    def on_playlist(self, event):
        """
        Enable or disable playlists downloading
        """
        if not self.parent.data_url:
            self.ckbx_pl.SetValue(False)
            self.parent.click_start(None)
            return

        if self.ckbx_pl.IsChecked():
            playlist = [url for url in self.parent.data_url
                        if '/playlist' in url]
            if not playlist:
                wx.MessageBox(_("URLs have no playlist references"),
                              "Videomass", wx.ICON_INFORMATION, self)
                self.ckbx_pl.SetValue(False)
                return
            self.opt["NO_PLAYLIST"] = False
            self.btn_plidx.Enable()

        else:
            self.opt["NO_PLAYLIST"] = True
            self.btn_plidx.SetBackgroundColour(wx.NullColour)
            self.btn_plidx.Disable()
            self.plidx = {'': ''}
    # -----------------------------------------------------------------#

    def on_playlist_idx(self, event):
        """
        Dialog for setting playlist indexing
        """
        with Indexing(self,
                      self.parent.data_url,
                      self.plidx) as idxdialog:
            if idxdialog.ShowModal() == wx.ID_OK:
                data = idxdialog.getvalue()
                if not data:
                    self.btn_plidx.SetBackgroundColour(wx.NullColour)
                    self.plidx = {'': ''}
                else:
                    self.btn_plidx.SetBackgroundColour(
                        wx.Colour(Downloader.VIOLET))
                    self.plidx = data
    # -----------------------------------------------------------------#

    def check_for_playlist(self):
        """
        Check for playlists and warn the user before continue.
        """
        urls = self.parent.data_url
        if [url for url in urls if 'playlist' in url]:
            if not self.ckbx_pl.IsChecked():
                if wx.MessageBox(_('The URLs contain playlists. '
                                   'Are you sure you want to continue?'),
                                 _('Please confirm'), wx.ICON_QUESTION
                                 | wx.CANCEL | wx.YES_NO, self) == wx.YES:
                    return False
                return True

        return False
    # -----------------------------------------------------------------#

    def check_for_channels(self):
        """
        Check for channels and warn the user before continue.
        """
        urls = self.parent.data_url
        if [url for url in urls if 'channel' in url]:
            if wx.MessageBox(_('The URLs contain channels. '
                               'Are you sure you want to continue?'),
                             _('Please confirm'), wx.ICON_QUESTION
                             | wx.CANCEL | wx.YES_NO, self) == wx.YES:
                return False
            return True

        return False
    # -----------------------------------------------------------------#

    def default_statistics_options(self):
        """

        Main mapping for Statistics options used by to
        get info and format code datas.
        return a type dict object.
        """
        kwa = {}
        if (self.appdata["use_cookie_file"]
                and self.appdata["cookiefile"].strip()):
            kwa["cookiefile"] = self.appdata["cookiefile"]
        if self.appdata["autogen_cookie_file"]:
            cfb = tuple(self.appdata["cookiesfrombrowser"])
            kwa["cookiesfrombrowser"] = cfb
        kwa['no_color'] = True
        kwa['nocheckcertificate'] = self.appdata["ssl_certificate"]
        kwa['ignoreerrors'] = True  # exit code 1 if any errors
        kwa['noplaylist'] = True
        kwa['no_color'] = True
        kwa['proxy'] = self.appdata["proxy"]
        kwa['username'] = self.appdata["username"]
        kwa['password'] = self.appdata["password"]
        kwa['videopassword'] = self.appdata["videopassword"]
        kwa["geo_verification_proxy"] = self.appdata["geo_verification_proxy"]
        kwa["geo_bypass"] = self.appdata["geo_bypass"]
        kwa["geo_bypass_country"] = self.appdata["geo_bypass_country"]
        kwa["geo_bypass_ip_block"] = self.appdata["geo_bypass_ip_block"]

        return kwa
    # -----------------------------------------------------------------#

    def default_download_options(self):
        """
        default_options
        Main mapping for download options.
        return a type dict object.
        """
        data = {}
        postprocessors = []
        if self.choice.GetSelection() == 3:
            postprocessors.append({'key': 'FFmpegExtractAudio',
                                   'preferredcodec': self.opt["A_FORMAT"],
                                   })
        if self.appdata['add_metadata']:
            postprocessors.append({'key': 'FFmpegMetadata'})
        if self.appdata["embed_thumbnails"]:
            postprocessors.append({'key': 'EmbedThumbnail'})
        if self.opt["SUBS"]["embedsubtitle"]:
            postprocessors.append({'key': 'FFmpegEmbedSubtitle'})
        if (self.appdata["use_cookie_file"]
                and self.appdata["cookiefile"].strip()):
            data["cookiefile"] = self.appdata["cookiefile"]
        if self.appdata["autogen_cookie_file"]:
            cfb = tuple(self.appdata["cookiesfrombrowser"])
            data["cookiesfrombrowser"] = cfb
        data['compat_opts'] = 'youtube-dl'
        data['external_downloader'] = (
            self.appdata["external_downloader"])
        data['external_downloader_args'] = (
            self.appdata["external_downloader_args"])
        # data['noplaylist'] = self.opt["NO_PLAYLIST"]
        data['writesubtitles'] = self.opt["SUBS"]["writesubtitles"]
        data['subtitleslangs'] = self.opt["SUBS"]["subtitleslangs"]
        data['writeautomaticsub'] = self.opt["SUBS"]["writeautomaticsub"]
        data['skip_download'] = self.opt["SUBS"]["skip_download"]
        data['addmetadata'] = self.appdata['add_metadata']
        data['restrictfilenames'] = self.appdata["restrict_fname"]
        data['ignoreerrors'] = True
        data['no_warnings'] = False
        data['writethumbnail'] = self.appdata["embed_thumbnails"]
        data['overwrites'] = self.appdata["overwr_dl_files"]
        data['no_color'] = True
        data['nocheckcertificate'] = self.appdata["ssl_certificate"]
        data['proxy'] = self.appdata["proxy"]
        data['username'] = self.appdata["username"]
        data['password'] = self.appdata["password"]
        data['videopassword'] = self.appdata["videopassword"]
        data["geo_verification_proxy"] = self.appdata["geo_verification_proxy"]
        data["geo_bypass"] = self.appdata["geo_bypass"]
        data["geo_bypass_country"] = self.appdata["geo_bypass_country"]
        data["geo_bypass_ip_block"] = self.appdata["geo_bypass_ip_block"]
        data['ffmpeg_location'] = f'{self.appdata["ffmpeg_cmd"]}'
        data['postprocessors'] = postprocessors

        return data
    # -----------------------------------------------------------------#

    def build_args(self, *args, **data):
        """
        Build the options list for yt_dlp,
        return a type list object.
        """
        datalist = []
        urlslist = self.parent.data_url

        if self.appdata['playlistsubfolder']:
            subdir = ('%(uploader)s/%(playlist_title)'
                      's/%(playlist_index)s - ')
        else:
            subdir = ''

        for url, code in itertools.zip_longest(urlslist,
                                               args[2],
                                               fillvalue='',
                                               ):
            if not self.opt["NO_PLAYLIST"]:
                if '/playlist' in url:
                    template = subdir + args[0]
                    playlistitems = self.plidx.get(url, None)
                    noplaylist = False
                else:
                    template = args[0]
                    playlistitems = None
                    noplaylist = True
            else:
                template = args[0]
                playlistitems = None
                noplaylist = True

            format_code = code if code else args[1]
            datalist.append(
                {'format': format_code,
                 'extractaudio': args[1],
                 'outtmpl': f"{self.appdata['ydlp-outputdir']}/{template}",
                 'noplaylist': noplaylist,
                 'playlist_items': playlistitems,
                 'postprocessors': data['postprocessors'],
                 **data
                 })
        return datalist
    # -----------------------------------------------------------------#

    def on_start(self):
        """
        Pass options list to processing.
        """
        if self.check_for_playlist() or self.check_for_channels():
            return

        data = self.default_download_options()

        if self.appdata["include_ID_name"]:
            _id = '%(title).100s-%(id)s'
        else:
            _id = '%(title).100s'

        formatquality = self.quality
        outtmpl = f'{_id}.%(ext)s'

        if self.choice.GetSelection() == 0:  # precompiled or quality
            code = []
            data['extractaudio'] = False

        elif self.choice.GetSelection() == 1:  # by video resolution
            code = []
            data['extractaudio'] = False

        elif self.choice.GetSelection() == 2:  # audio and video splitted
            code = []
            outtmpl = f'{_id}.f%(format_id)s.%(ext)s'
            data['extractaudio'] = False

        elif self.choice.GetSelection() == 3:  # audio only
            code = []
            data['extractaudio'] = True

        elif self.choice.GetSelection() == 4:  # format code
            code = self.panel_cod.getformatcode()
            formatquality = ''
            outtmpl = f'{_id}.f%(format_id)s.%(ext)s'
            data['extractaudio'] = False
            if not code:
                self.parent.statusbar_msg(Downloader.MSG_1,
                                          self.red,
                                          Downloader.WHITE
                                          )
                return

        self.to_processing(self.build_args(outtmpl,
                                           formatquality,
                                           code,
                                           **data
                                           ))
    # -----------------------------------------------------------------#

    def to_processing(self, datalist):
        """
        Call `main_ytdlp.switch_to_processing`
        """
        if self.appdata['ytdlp-useexec']:
            execlist = []
            execpath = self.appdata['ytdlp-executable-path']
            for args in datalist:
                execlist.append(from_api_to_cli(args, execpath))
            self.parent.switch_to_processing('YouTube Downloader', execlist)
        else:
            self.parent.switch_to_processing('YouTube Downloader', datalist)
