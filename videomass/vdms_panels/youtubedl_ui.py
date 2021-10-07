# -*- coding: UTF-8 -*-
"""
Name: youtubedl_ui.py
Porpose: youtube-dl user interface
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Oct.03.2021
Code checker: pycodestyle / flake8 --ignore=F821,W503
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
import sys
import wx
import wx.lib.scrolledpanel as scrolled
from videomass.vdms_io import io_tools
from videomass.vdms_utils.utils import format_bytes
from videomass.vdms_utils.utils import timehuman
from videomass.vdms_frames.ydl_mediainfo import YdlMediaInfo
from videomass.vdms_utils.get_bmpfromsvg import get_bmp
from videomass.vdms_dialogs.playlist_indexing import Indexing

if not hasattr(wx, 'EVT_LIST_ITEM_CHECKED'):
    import wx.lib.mixins.listctrl as listmix

    class TestListCtrl(wx.ListCtrl,
                       listmix.CheckListCtrlMixin,
                       listmix.ListCtrlAutoWidthMixin
                       ):
        """
        This is listctrl with a checkbox for each row in list.
        It work on both wxPython==4.1.? and wxPython<=4.1.? (e.g. 4.0.7).
        Since wxPython <= 4.0.7 has no attributes for fcode.EnableCheckBoxes
        and the 'wx' module does not have attributes 'EVT_LIST_ITEM_CHECKED',
        'EVT_LIST_ITEM_UNCHECKED' for binding, this class maintains backward
        compatibility.
        """
        def __init__(self,
                     parent,
                     ID,
                     pos=wx.DefaultPosition,
                     size=wx.DefaultSize,
                     style=0
                     ):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
            listmix.CheckListCtrlMixin.__init__(self)
            listmix.ListCtrlAutoWidthMixin.__init__(self)
            # self.setResizeColumn(3)

        def OnCheckItem(self, index, flag):
            """
            Send to parent (class Downloader) index and flag.
            index = int(num) of checked item.
            flag = boolean True or False of the checked or un-checked item
            """
            self.parent.onCheck(self)


class Downloader(wx.Panel):
    """
    This panel gives a graphic layout to some features of youtube-dl

    """
    get = wx.GetApp()  # get videomass wx.App attribute
    appdata = get.appset
    icons = get.iconset
    BACKGRD = get.appset['icontheme'][1]['BACKGRD']
    GREEN = get.appset['icontheme'][1]['TXT3']
    RED = get.appset['icontheme'][1]['ERR1']
    YELLOW = '#bd9f00'
    WHITE = '#fbf4f4'  # white for background status bar
    BLACK = '#060505'  # black for background status bar
    VIOLET = '#D64E93'

    MSG_1 = _('At least one "Format Code" must be checked for each '
              'URL selected in green.')
    MSG_2 = _('Function available only if you choose "Download by '
              'format code"')

    P1080 = 'bestvideo[height<=?1080]+bestaudio/best[height<=?1080]'
    P720 = 'bestvideo[height<=?720]+bestaudio/best[height<=?720]'
    P480 = 'bestvideo[height<=?480]+bestaudio/best[height<=?480]'
    P360 = 'bestvideo[height<=?360]+bestaudio/best[height<=?360]'
    P240 = 'bestvideo[height<=?240]+bestaudio/best[height<=?240]'
    P144 = 'worstvideo[height>=?144]+worstaudio/worst[height>=?144]'

    VQUALITY = {('Best quality video 1080p'): (P1080),
                ('720p'): (P720),
                ('480p'): (P480),
                ('360p'): (P360),
                ('240p'): (P240),
                ('Worst quality video 144p'): (P144),
                }
    AFORMATS = {("Default audio format"): ("best"),
                ("wav"): ("wav"),
                ("mp3"): ("mp3"),
                ("aac"): ("aac"),
                ("m4a"): ("m4a"),
                ("vorbis"): ("vorbis"),
                ("opus"): ("opus"),
                ("flac"): ("flac"),
                }
    AQUALITY = {('Best quality audio'): ('bestaudio'),
                ('Worst quality audio'): ('worstaudio')}

    CHOICE = [_('Default'),
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
        self.parent = parent

        if 'wx.svg' in sys.modules:  # available only in wx version 4.1 to up
            bmpplay = get_bmp(Downloader.icons['preview'], ((16, 16)))
            bmplistindx = get_bmp(Downloader.icons['listindx'], ((16, 16)))
        else:
            bmpplay = wx.Bitmap(Downloader.icons['preview'],
                                wx.BITMAP_TYPE_ANY)
            bmplistindx = wx.Bitmap(Downloader.icons['listindx'],
                                    wx.BITMAP_TYPE_ANY)

        self.opt = {("NO_PLAYLIST"): True,
                    ("THUMB"): False,
                    ("METADATA"): False,
                    ("V_QUALITY"): (Downloader.P1080),
                    ("A_FORMAT"): "best",
                    ("A_QUALITY"): "bestaudio",
                    ("SUBTITLES"): False,
                    }
        self.plidx = {'': ''}
        self.info = []  # has data information for Show More button
        self.format_dict = {}  # format codes order with URL matching
        self.oldwx = None  # test result of hasattr EVT_LIST_ITEM_CHECKED

        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)

        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_div = wx.BoxSizer(wx.HORIZONTAL)
        sizer_base.Add(sizer_div, 1, wx.EXPAND)
        boxoptions = wx.StaticBoxSizer(wx.StaticBox(
            self, wx.ID_ANY, _('Options')), wx.VERTICAL)
        sizer_div.Add(boxoptions, 0, wx.ALL | wx.EXPAND, 5)
        boxlistctrl = wx.StaticBoxSizer(wx.StaticBox(
            self, wx.ID_ANY, ('')), wx.VERTICAL)
        sizer_div.Add(boxlistctrl, 1, wx.ALL | wx.EXPAND, 5)

        # ------------- choice and comboboxes
        self.choice = wx.Choice(self, wx.ID_ANY,
                                choices=Downloader.CHOICE,
                                size=(-1, -1),
                                )
        self.choice.SetSelection(0)
        boxoptions.Add(self.choice, 0, wx.ALL | wx.EXPAND, 5)
        boxoptions.Add((5, 5))
        line0 = wx.StaticLine(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        boxoptions.Add(line0, 0, wx.ALL | wx.EXPAND, 5)
        boxoptions.Add((5, 5))
        panelscroll = scrolled.ScrolledPanel(self, -1, size=(260, 700),
                                             style=wx.TAB_TRAVERSAL
                                             | wx.BORDER_THEME,
                                             name="panelscr",
                                             )
        fgs1 = wx.BoxSizer(wx.VERTICAL)
        # fgs1.Add((5, 5))
        self.cmbx_vq = wx.ComboBox(panelscroll, wx.ID_ANY,
                                   choices=list(Downloader.VQUALITY.keys()),
                                   size=(-1, -1), style=wx.CB_DROPDOWN
                                   | wx.CB_READONLY
                                   )
        self.cmbx_vq.SetSelection(0)
        # grid_v.Add((20, 20), 0,)
        fgs1.Add(self.cmbx_vq, 0, wx.ALL | wx.EXPAND, 5)
        tip = (_('When not available, the chosen video resolution will '
                 'be replaced with the closest one'))
        self.cmbx_vq.SetToolTip(tip)

        self.cmbx_aq = wx.ComboBox(panelscroll, wx.ID_ANY,
                                   choices=list(Downloader.AQUALITY.keys()),
                                   size=(-1, -1),
                                   style=wx.CB_DROPDOWN
                                   | wx.CB_READONLY
                                   )
        self.cmbx_aq.SetSelection(0)
        self.cmbx_aq.Disable()
        # grid_v.Add((20, 20), 0,)
        fgs1.Add(self.cmbx_aq, 0, wx.ALL | wx.EXPAND, 5)
        self.cmbx_af = wx.ComboBox(panelscroll, wx.ID_ANY,
                                   choices=list(Downloader.AFORMATS.keys()),
                                   size=(-1, -1),
                                   style=wx.CB_DROPDOWN
                                   | wx.CB_READONLY
                                   )
        self.cmbx_af.Disable()
        self.cmbx_af.SetSelection(0)
        fgs1.Add(self.cmbx_af, 0, wx.ALL | wx.EXPAND, 5)
        # ------------- checkboxes
        line1 = wx.StaticLine(panelscroll, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=wx.DefaultSize, style=wx.LI_HORIZONTAL,
                              name=wx.StaticLineNameStr
                              )
        fgs1.Add(line1, 0, wx.ALL | wx.EXPAND, 10)

        self.btn_play = wx.Button(panelscroll, wx.ID_ANY, _("Preview"))
        self.btn_play.SetBitmap(bmpplay, wx.LEFT)
        self.btn_play.Disable()
        fgs1.Add(self.btn_play, 0, wx.ALL | wx.EXPAND, 5)

        self.ckbx_pl = wx.CheckBox(panelscroll, wx.ID_ANY,
                                   (_('Download all videos in playlist'))
                                   )
        fgs1.Add(self.ckbx_pl, 0, wx.ALL, 5)

        self.btn_plidx = wx.Button(panelscroll, wx.ID_ANY,
                                   (_('Playlist Editor'))
                                   )
        self.btn_plidx.SetBitmap(bmplistindx, wx.LEFT)
        fgs1.Add(self.btn_plidx, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_plidx.Disable()

        self.ckbx_thumb = wx.CheckBox(panelscroll, wx.ID_ANY,
                                      (_('Embed thumbnail in audio file'))
                                      )
        fgs1.Add(self.ckbx_thumb, 0, wx.ALL, 5)
        self.ckbx_meta = wx.CheckBox(panelscroll, wx.ID_ANY,
                                     (_('Add metadata to file'))
                                     )
        fgs1.Add(self.ckbx_meta, 0, wx.ALL, 5)
        self.ckbx_sb = wx.CheckBox(panelscroll, wx.ID_ANY,
                                   (_('Write subtitles to video'))
                                   )
        fgs1.Add(self.ckbx_sb, 0, wx.ALL, 5)

        self.ckbx_w = wx.CheckBox(panelscroll, wx.ID_ANY,
                                  (_('Prevent overwriting files'))
                                  )
        fgs1.Add(self.ckbx_w, 0, wx.ALL, 5)

        self.ckbx_id = wx.CheckBox(panelscroll, wx.ID_ANY,
                                   (_('Include the video ID\n'
                                      'in the file names'))
                                   )
        fgs1.Add(self.ckbx_id, 0, wx.ALL, 5)

        self.ckbx_restrict_fn = wx.CheckBox(panelscroll, wx.ID_ANY,
                                            (_('Restrict file names'))
                                            )
        fgs1.Add(self.ckbx_restrict_fn, 0, wx.ALL, 5)

        boxoptions.Add(panelscroll, 0, wx.ALL | wx.CENTRE, 0)

        panelscroll.SetSizer(fgs1)
        panelscroll.SetAutoLayout(1)
        panelscroll.SetupScrolling()

        # -------------listctrl
        if hasattr(wx, 'EVT_LIST_ITEM_CHECKED'):
            self.oldwx = False
            self.fcode = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT
                                     | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL
                                     )
        else:
            self.oldwx = True
            t_id = wx.NewIdRef()
            self.fcode = TestListCtrl(self, t_id, style=wx.LC_REPORT
                                      | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL
                                      )
        boxlistctrl.Add(self.fcode, 1, wx.ALL | wx.EXPAND, 5)
        # -------------textctrl
        labtstr = _('Help viewer')
        self.labtxt = wx.StaticText(self, label=labtstr)
        sizer_base.Add(self.labtxt, 0, wx.LEFT, 5)
        self.cod_text = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_MULTILINE
                                    | wx.TE_READONLY
                                    | wx.TE_RICH2,
                                    size=(-1, 100)
                                    )
        sizer_base.Add(self.cod_text, 0, wx.ALL | wx.EXPAND, 5)
        # -----------------------
        self.cod_text.Hide()
        self.labtxt.Hide()
        self.SetSizer(sizer_base)
        self.Layout()
        # ----------------------- Properties
        # WARNING do not append text on self.cod_text here,
        # see `on_Choice meth.`

        self.cod_text.SetBackgroundColour(Downloader.BACKGRD)

        if Downloader.appdata['ostype'] != 'Darwin':
            # self.labcode.SetLabelMarkup("<b>%s</b>" % labcstr)
            self.labtxt.SetLabelMarkup(f"<b>{labtstr}</b>")
        #  tooltips
        self.btn_play.SetToolTip(_('Play selected url'))

        # ----------------------Binder (EVT)----------------------#
        self.choice.Bind(wx.EVT_CHOICE, self.on_Choice)
        self.cmbx_vq.Bind(wx.EVT_COMBOBOX, self.on_Vq)
        self.cmbx_af.Bind(wx.EVT_COMBOBOX, self.on_Af)
        self.cmbx_aq.Bind(wx.EVT_COMBOBOX, self.on_Aq)
        self.Bind(wx.EVT_BUTTON, self.playSelurl, self.btn_play)
        self.ckbx_pl.Bind(wx.EVT_CHECKBOX, self.on_Playlist)
        self.btn_plidx.Bind(wx.EVT_BUTTON, self.on_Playlist_idx)
        self.ckbx_thumb.Bind(wx.EVT_CHECKBOX, self.on_Thumbnails)
        self.ckbx_meta.Bind(wx.EVT_CHECKBOX, self.on_Metadata)
        self.ckbx_sb.Bind(wx.EVT_CHECKBOX, self.on_Subtitles)
        self.fcode.Bind(wx.EVT_CONTEXT_MENU, self.onContext)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.fcode)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect, self.fcode)
        if self.oldwx is False:
            self.fcode.Bind(wx.EVT_LIST_ITEM_CHECKED, self.onCheck)
            self.fcode.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.onCheck)
    # -----------------------------------------------------------------#

    def on_select(self, event):
        """
        self.fcod selection event that enables btn_play
        """
        self.btn_play.Enable()
    # ----------------------------------------------------------------------

    def on_deselect(self, event):
        """
        self.fcod de-selection event that disables btn_play
        """
        self.btn_play.Disable()
    # ----------------------------------------------------------------------

    def onCheck(self, event):
        """
        get data from row in the enabled checkbox and set the values
        on corresponding key depending if check or uncheck e.g.:

            `key=url: values=[Audio: code, Video: code]`
        """
        if not self.choice.GetSelection() == 3:
            self.cod_text.Clear()
            num = self.fcode.GetItemCount()
            for idx in range(num):
                if self.fcode.IsChecked(idx):
                    self.cod_text.SetDefaultStyle(
                        wx.TextAttr(Downloader.YELLOW))
                    self.cod_text.AppendText(f'- {Downloader.MSG_2}\n')
            return

        if not self.parent.sb.GetStatusText() == 'Ready':
            self.parent.statusbar_msg('Ready', None)

        viddisp, auddisp = 'video', 'audio only'

        if self.oldwx is False:
            check = self.fcode.IsItemChecked
        else:
            check = self.fcode.IsChecked

        num = self.fcode.GetItemCount()
        for url in self.parent.data_url:
            self.format_dict[url] = []
            for i in range(num):
                if check(i):
                    if (self.fcode.GetItemText(i, 1)) == url:
                        if viddisp in self.fcode.GetItemText(i, 4):
                            dv = self.fcode.GetItemText(i, 0)
                            self.format_dict[url].append('Video: ' + dv)
                        elif auddisp in self.fcode.GetItemText(i, 4):
                            da = self.fcode.GetItemText(i, 0)
                            self.format_dict[url].append('Audio: ' + da)
                        else:
                            dv = self.fcode.GetItemText(i, 0)
                            self.format_dict[url].append('Video: ' + dv)

        self.cod_text.Clear()
        for k, v in self.format_dict.items():
            if not v:
                self.cod_text.SetDefaultStyle(wx.TextAttr(Downloader.RED))
                self.cod_text.AppendText(f'- {k} :\n')
            else:
                self.cod_text.SetDefaultStyle(wx.TextAttr(Downloader.GREEN))
                self.cod_text.AppendText(f'- {k} :  {v}\n')
        # print(self.format_dict)
    # ----------------------------------------------------------------------

    def onContext(self, event):
        """
        Create and show a Context Menu
        """
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID2"):
            self.popupID2 = wx.NewIdRef()
            self.Bind(wx.EVT_MENU, self.onPopup, id=self.popupID2)

        # build the menu
        menu = wx.Menu()
        menu.Append(self.popupID2, _("Play selected url"))
        # show the popup menu
        self.PopupMenu(menu)

        menu.Destroy()
    # ----------------------------------------------------------------------

    def onPopup(self, event):
        """
        Evaluate the label string of the menu item selected and starts
        the related process
        """
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)

        if menuItem.GetItemLabel() == _("Play selected url"):
            self.playSelurl(self)
    # ----------------------------------------------------------------------

    def playSelurl(self, event):
        """
        Playback urls
        """
        tstamp = f'-vf "{self.parent.cmdtimestamp}"' if \
                 self.parent.checktimestamp else ''

        if self.fcode.GetSelectedItemCount() == 0:
            self.parent.statusbar_msg(_('An item must be selected in the '
                                        'URLs checklist'), Downloader.YELLOW,
                                      Downloader.BLACK)
            return

        self.parent.statusbar_msg(_('Ready'), None)
        item = self.fcode.GetFocusedItem()
        url = self.fcode.GetItemText(item, 1)
        if '/watch' not in url:
            # prevent opening too many of ffplay windows
            wx.MessageBox(_("Cannot play playlists / channels or URLs "
                            "containing multiple videos listed."),
                          "Videomass", wx.ICON_INFORMATION, self)
            return

        if self.choice.GetSelection() == 0:  # play video only
            quality = self.fcode.GetItemText(item, 3).split('+')[0]
        elif self.choice.GetSelection() == 1:  # play audio only
            quality = self.fcode.GetItemText(item, 3).split(',')[1]
        elif self.choice.GetSelection() == 2:
            quality = 'bestaudio'
        elif self.choice.GetSelection() == 3:
            quality = self.fcode.GetItemText(item, 0)

        io_tools.url_play(url, quality, tstamp, self.parent.autoexit)
    # ----------------------------------------------------------------------

    def get_formatcode(self):
        """
        Get URLs data and format codes by generator object
        *youtubedl_getstatistics* (using youtube_dl library) and set the list
        control with new entries. Return `True` if `meta[1]` (error),
        otherwise return None as exit staus.
        """
        self.fcode.ClearAll()
        if self.oldwx is False:
            self.fcode.EnableCheckBoxes(enable=True)
        self.fcode.InsertColumn(0, (_('Format Code')), width=120)
        self.fcode.InsertColumn(1, (_('Url')), width=60)
        self.fcode.InsertColumn(2, (_('Title')), width=200)
        self.fcode.InsertColumn(3, (_('Extension')), width=80)
        self.fcode.InsertColumn(4, (_('Resolution')), width=160)
        self.fcode.InsertColumn(5, (_('Video Codec')), width=110)
        self.fcode.InsertColumn(6, (_('fps')), width=80)
        self.fcode.InsertColumn(7, (_('Audio Codec')), width=110)
        self.fcode.InsertColumn(8, (_('Size')), width=100)
        index = 0
        for link in self.parent.data_url:
            data = io_tools.youtubedl_getstatistics(link)
            for meta in data:
                if meta[1]:
                    # self.parent.statusbar_msg('Ready', None)
                    wx.MessageBox(meta[1], 'Videomass', wx.ICON_ERROR)
                    return True

            formats = iter(meta[0].get('formats', [meta[0]]))
            for n, f in enumerate(formats):
                if f.get('vcodec'):
                    vcodec, fps = f['vcodec'], f"{f.get('fps')}fps"
                else:
                    vcodec, fps = '', ''
                if f.get('acodec'):
                    acodec = f['acodec']
                else:
                    acodec = 'Video only'
                if f.get('filesize'):
                    size = format_bytes(float(f['filesize']))
                else:
                    size = 'N/A'
                self.fcode.InsertItem(index, f['format_id'])
                self.fcode.SetItem(index, 1, link)
                self.fcode.SetItem(index, 2, meta[0]['title'])
                self.fcode.SetItem(index, 3, f['ext'])
                self.fcode.SetItem(index, 4, f['format'].split('-')[1])
                self.fcode.SetItem(index, 5, vcodec)
                self.fcode.SetItem(index, 6, fps)
                self.fcode.SetItem(index, 7, acodec)
                self.fcode.SetItem(index, 8, size)
                if n == 0:
                    self.fcode.SetItemBackgroundColour(index, Downloader.GREEN)
                index += 1
        return None
    # ----------------------------------------------------------------------

    def get_statistics(self):
        """
        Get media URLs informations by generator object
        *youtubedl_getstatistics*  . Return `True` if `meta[1]` (error),
        otherwise return None as exit staus.
        """
        for link in self.parent.data_url:
            data = io_tools.youtubedl_getstatistics(link)
            for meta in data:
                if meta[1]:
                    # self.parent.statusbar_msg('Ready', None)
                    wx.MessageBox(meta[1], 'Videomass', wx.ICON_ERROR)
                    del self.info[:]
                    return True
                if 'entries' in meta[0]:
                    meta[0]['entries'][0]  # not parse all playlist
                if 'duration' in meta[0]:

                    ftime = (f"{timehuman(meta[0]['duration'])} "
                             f"({meta[0]['duration']} sec.)")
                else:
                    ftime = 'N/A'
                date = meta[0].get('upload_date')
                self.info.append({'url': link,
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
        return None
    # -----------------------------------------------------------------#

    def on_urls_list(self, quality):
        """
        Populate list control with new incoming as urls and
        related resolutions.

        """
        self.fcode.ClearAll()
        if self.oldwx is False:
            self.fcode.EnableCheckBoxes(enable=False)
        self.fcode.InsertColumn(0, ('#'), width=30)
        self.fcode.InsertColumn(1, (_('Url')), width=400)
        self.fcode.InsertColumn(2, (_('Title')), width=50)
        self.fcode.InsertColumn(3, (_('Quality')), width=250)

        if self.parent.data_url:
            index = 0
            for link in self.parent.data_url:
                self.fcode.InsertItem(index, str(index + 1))
                self.fcode.SetItem(index, 1, link)
                self.fcode.SetItem(index, 2, 'N/A')
                self.fcode.SetItem(index, 3, quality)
                index += 1
    # -----------------------------------------------------------------#

    def on_show_statistics(self):
        """
        show URL data information. This method is called by
        main frame when the 'Show More' button is pressed.

        """
        if not self.info:
            ret = self.get_statistics()
            if ret:
                return

        miniframe = YdlMediaInfo(self.info, Downloader.appdata['ostype'])
        miniframe.Show()
    # -----------------------------------------------------------------#

    def on_format_codes(self):
        """
        Evaluate which method to call to enable
        download from "Format Code"

        """
        ret = self.get_formatcode()
        if ret:
            return  # do not enable fcode

    # -----------------------------------------------------------------#

    def on_Choice(self, event, statusmsg=True):
        """
        - Enable or disable some widgets during switching choice box.
        - Set media quality parameter for on_urls_list method
        """

        if statusmsg is True:
            if not self.parent.sb.GetStatusText() == 'Ready':
                self.parent.statusbar_msg(_('Ready'), None)

        self.cod_text.Clear()
        self.btn_play.Disable()

        if self.choice.GetSelection() == 0:
            self.cmbx_af.Disable(), self.cmbx_aq.Disable()
            self.cmbx_vq.Enable(), self.cod_text.Hide()
            self.labtxt.Hide()
            self.Layout()
            self.on_urls_list(self.opt["V_QUALITY"])

        elif self.choice.GetSelection() == 1:
            self.cmbx_af.Disable(), self.cmbx_aq.Enable()
            self.cmbx_vq.Enable(), self.cod_text.Hide()
            self.labtxt.Hide()
            self.Layout()
            self.on_urls_list(f'{self.opt["V_QUALITY"].split("+", maxsplit=1)[0]},'
                              f'{self.opt["A_QUALITY"]}')
        elif self.choice.GetSelection() == 2:
            self.cmbx_vq.Disable(), self.cmbx_aq.Disable()
            self.cmbx_af.Enable(), self.cod_text.Hide()
            self.labtxt.Hide()
            self.Layout()
            self.on_urls_list('')

        elif self.choice.GetSelection() == 3:

            ceckurls = [url for url in self.parent.data_url if '/watch'
                        not in url]
            if ceckurls:
                wx.MessageBox(_("Unable to get format codes on playlists / "
                                "channels or URLs containing multiple "
                                "videos listed."),
                              "Videomass", wx.ICON_INFORMATION, self)
                # prevent KeyError: 'format_id'
                self.choice.SetSelection(0)
                return
            self.labtxt.Show(), self.cod_text.Show()
            self.Layout()
            self.cmbx_vq.Disable(), self.cmbx_aq.Disable()
            self.cmbx_af.Disable()
            self.on_format_codes()
    # -----------------------------------------------------------------#

    def on_Vq(self, event):
        """
        Set video qualities on 'best' or 'worst' during combobox event
        and self.choice selection == 0
        """
        self.opt["V_QUALITY"] = Downloader.VQUALITY[self.cmbx_vq.GetValue()]
        index = 0
        if self.choice.GetSelection() == 0:
            # set 'best' parameters on both audio and video.
            quality = self.opt["V_QUALITY"]
        elif self.choice.GetSelection() == 1:
            # set the "worst" and "best" parameters independently
            quality = (f'{self.opt["V_QUALITY"].split("+", maxsplit=1)[0]},'
                       f'{self.opt["A_QUALITY"]}')
        for link in self.parent.data_url:
            self.fcode.SetItem(index, 3, quality)
            index += 1
    # -----------------------------------------------------------------#

    def on_Af(self, event):
        """
        Set audio format to exporting during combobox event
        and self.choice selection == 2
        """
        self.opt["A_FORMAT"] = Downloader.AFORMATS.get(self.cmbx_af.GetValue())
        index = 0
        for link in self.parent.data_url:
            self.fcode.SetItem(index, 3, '')
            index += 1
    # -----------------------------------------------------------------#

    def on_Aq(self, event):
        """
        Set audio qualities on 'best' or 'worst' during combobox event
        and self.choice selection == 1
        """
        self.opt["A_QUALITY"] = Downloader.AQUALITY.get(
            self.cmbx_aq.GetValue())
        index = 0
        # set string to audio and video qualities independently for player

        quality = (f'{self.opt["V_QUALITY"].split("+", maxsplit=1)[0]},'
                   f'{self.opt["A_QUALITY"]}')
        for link in self.parent.data_url:
            self.fcode.SetItem(index, 3, quality)
            index += 1
    # -----------------------------------------------------------------#

    def on_Playlist(self, event):
        """
        Enable or disable the download of playlists
        """

        if self.ckbx_pl.IsChecked():
            playlist = [url for url in self.parent.data_url
                        if '/playlist?list' in url]
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

    def on_Playlist_idx(self, event):
        """
        Set up custom indexing when you download playlists
        """

        idxdialog = Indexing(self, self.parent.data_url, self.plidx)
        retcode = idxdialog.ShowModal()
        if retcode == wx.ID_OK:
            data = idxdialog.getvalue()
            if not data:
                self.btn_plidx.SetBackgroundColour(wx.NullColour)
                self.plidx = {'': ''}
            else:
                self.btn_plidx.SetBackgroundColour(
                    wx.Colour(Downloader.VIOLET))
                self.plidx = data
        else:
            idxdialog.Destroy()
            return
    # -----------------------------------------------------------------#

    def on_Thumbnails(self, event):
        """
        Enable or disable the tumbnails downloading
        """
        if self.ckbx_thumb.IsChecked():
            self.opt["THUMB"] = True
        else:
            self.opt["THUMB"] = False
    # -----------------------------------------------------------------#

    def on_Metadata(self, event):
        """
        Enable or disable writing metadata
        """
        if self.ckbx_meta.IsChecked():
            self.opt["METADATA"] = True
        else:
            self.opt["METADATA"] = False
    # -----------------------------------------------------------------#

    def on_Subtitles(self, event):
        """
        enable or disable writing subtitles
        """
        if self.ckbx_sb.IsChecked():
            self.opt["SUBTITLES"] = True
        else:
            self.opt["SUBTITLES"] = False
    # -----------------------------------------------------------------#

    def getformatcode(self, urls):
        """
        Called by on on_Start. Return format code list

        """
        format_code = []

        for url, key, val in zip(urls,
                                 self.format_dict.keys(),
                                 self.format_dict.values()
                                 ):
            if key == url:
                video, audio = '', ''
                if len(val) == 1:
                    if val[0].startswith('Audio: '):
                        audio = val[0].split('Audio: ')[1]
                    elif val[0].startswith('Video: '):
                        video = val[0].split('Video: ')[1]
                    else:
                        video = val[0].split('Video: ')[1]
                else:
                    index_1, index_2 = 0, 0
                    for i in val:
                        if i.startswith('Video: '):
                            index_1 += 1
                            if index_1 > 1:
                                video += f"/{i.split('Video: ')[1]}"
                            else:
                                video = i.split('Video: ')[1]

                        elif i.startswith('Audio: '):
                            index_2 += 1
                            if index_2 > 1:
                                audio += f"/{i.split('Audio: ')[1]}"
                            else:
                                audio = i.split('Audio: ')[1]
                        else:
                            index_1 += 1
                            if index_1 > 1:
                                video += f"/{i.split('Video: ')[1]}"
                            else:
                                video = i.split('Video: ')[1]

                if video and audio:
                    format_code.append(f'{video}+{audio}')
                elif video:
                    format_code.append(f'{video}')
                elif audio:
                    format_code.append(f'{audio}')

        if len(format_code) != len(urls):
            return None
        return format_code
    # -----------------------------------------------------------------#

    def on_start(self):
        """
        Builds command string to use with an embed youtube_dl as
        python library or using standard youtube-dl command line.
        """
        urls = self.parent.data_url

        if not self.ckbx_pl.IsChecked():
            if [url for url in urls if 'playlist' in url]:
                if wx.MessageBox(_('The URLs contain playlists. '
                                   'Are you sure you want to continue?'),
                                 _('Please confirm'),
                                 wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                    return
        if [url for url in urls if 'channel' in url]:
            if wx.MessageBox(_('The URLs contain channels. '
                               'Are you sure you want to continue?'),
                             _('Please confirm'),
                             wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return

        if self.ckbx_id.IsChecked():
            _id = '%(title).100s-%(id)s'
        else:
            _id = '%(title).100s'

        logname = 'youtubedl_lib.log'
        nooverwrites = self.ckbx_w.IsChecked() is True
        restrictfn = self.ckbx_restrict_fn.IsChecked() is True
        postprocessors = []

        if self.choice.GetSelection() == 2:
            postprocessors.append({'key': 'FFmpegExtractAudio',
                                   'preferredcodec': self.opt["A_FORMAT"],
                                   })
        if self.opt["METADATA"]:
            postprocessors.append({'key': 'FFmpegMetadata'})

        if self.opt["THUMB"]:
            postprocessors.append({'key': 'EmbedThumbnail',
                                    'already_have_thumbnail': False
                                    })
        if self.opt["SUBTITLES"]:
            postprocessors.append({'key': 'FFmpegEmbedSubtitle'})

        if self.choice.GetSelection() == 0:
            code = []
            data = {'format': self.opt["V_QUALITY"],
                    'noplaylist': self.opt["NO_PLAYLIST"],
                    'playlist_items': self.plidx,
                    'nooverwrites': nooverwrites,
                    'writethumbnail': self.opt["THUMB"],
                    'outtmpl': f'{_id}.%(ext)s',
                    'extractaudio': False,
                    'addmetadata': self.opt["METADATA"],
                    'writesubtitles': self.opt["SUBTITLES"],
                    'writeautomaticsub': self.opt["SUBTITLES"],
                    'allsubtitles': self.opt["SUBTITLES"],
                    'postprocessors': postprocessors,
                    'restrictfilenames': restrictfn,
                    }
        elif self.choice.GetSelection() == 1:  # audio files and video files
            code = []
            data = {'format': (f'{self.opt["V_QUALITY"].split("+", maxsplit=1)[0]},'
                               f'{self.opt["A_QUALITY"]}'),
                    'noplaylist': self.opt["NO_PLAYLIST"],
                    'playlist_items': self.plidx,
                    'nooverwrites': nooverwrites,
                    'writethumbnail': self.opt["THUMB"],
                    'outtmpl': f'{_id}.f%(format_id)s.%(ext)s',
                    'extractaudio': False,
                    'addmetadata': self.opt["METADATA"],
                    'writesubtitles': self.opt["SUBTITLES"],
                    'writeautomaticsub': self.opt["SUBTITLES"],
                    'allsubtitles': self.opt["SUBTITLES"],
                    'postprocessors': postprocessors,
                    'restrictfilenames': restrictfn,
                    }
        elif self.choice.GetSelection() == 2:  # audio only
            code = []
            data = {'format': 'best',
                    'noplaylist': self.opt["NO_PLAYLIST"],
                    'playlist_items': self.plidx,
                    'nooverwrites': nooverwrites,
                    'writethumbnail': self.opt["THUMB"],
                    'outtmpl': f'{_id}.%(ext)s',
                    'extractaudio': True,
                    'addmetadata': self.opt["METADATA"],
                    'writesubtitles': self.opt["SUBTITLES"],
                    'writeautomaticsub': self.opt["SUBTITLES"],
                    'allsubtitles': self.opt["SUBTITLES"],
                    'postprocessors': postprocessors,
                    'restrictfilenames': restrictfn,
                    }
        elif self.choice.GetSelection() == 3:  # format code
            code = self.getformatcode(urls)
            if not code:
                self.parent.statusbar_msg(Downloader.MSG_1,
                                          Downloader.RED,
                                          Downloader.WHITE
                                          )
                return
            data = {'format': '',
                    'noplaylist': self.opt["NO_PLAYLIST"],
                    'playlist_items': self.plidx,
                    'nooverwrites': nooverwrites,
                    'writethumbnail': self.opt["THUMB"],
                    'outtmpl': f'{_id}.f%(format_id)s.%(ext)s',
                    'extractaudio': False,
                    'addmetadata': self.opt["METADATA"],
                    'writesubtitles': self.opt["SUBTITLES"],
                    'writeautomaticsub': self.opt["SUBTITLES"],
                    'allsubtitles': self.opt["SUBTITLES"],
                    'postprocessors': postprocessors,
                    'restrictfilenames': restrictfn,
                    }
        self.parent.switch_to_processing('youtube_dl downloading',
                                            urls,
                                            '',
                                            self.parent.outpath_ydl,
                                            data,
                                            None,
                                            code,
                                            '',
                                            logname,
                                            len(urls),
                                            )
