# -*- coding: UTF-8 -*-
# Name: generic_downloads.py
# Porpose: generic network download operation
# Compatibility: Python3, wxPython4 Phoenix
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: Oct.03.2020 *PEP8 compatible*
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
import shutil
import ssl
import urllib.request
import wx
from pubsub import pub
from threading import Thread


class File_Downloading(Thread):
    """
    'FileDownloading' is a generic network download operation
    via `urllib.request`. It is used to download small files
    and save them on filesystem.

    """
    def __init__(self, url, filename):
        """
        Attributes defined here:
        self.url: file on network
        self.filename: file to download (dirname + filename.ext)
        self.data: returned output of the self.status
        self.status: tuple object with exit status of the process

        """
        self.url = url
        self.filename = filename
        self.data = None
        self.status = None

        Thread.__init__(self)
        """initialize"""

        self.start()  # start the thread (va in self.run())
    # ----------------------------------------------------------------#

    def run(self):
        """
        Check for new version release
        """
        # HACK fix soon the ssl certificate
        context = ssl._create_unverified_context()
        headers = {'User-Agent': 'Mozilla/5.0'}
        page = urllib.request.Request(self.url, headers=headers)
        try:
            with urllib.request.urlopen(page, context=context) as \
                 response, open(self.filename, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

            self.status = self.url, None

        except urllib.error.HTTPError as error:
            self.status = None, error

        except urllib.error.URLError as error:
            self.status = None, error

        self.data = self.status

        wx.CallAfter(pub.sendMessage,
                     "RESULT_EVT",
                     status=''
                     )
# ---------------------------------------------------------------------#


def download_bigfile(url, filename):
    """
    network download operation via `requests`. It is used to
    download big files and save them on filesystem.

    """
    import requests

    # ------------------------------------------
    # this section is an example to get tarball_url name from github.
    # Use `get_github_releases(url, keyname)` function on IO module
    url = 'https://api.github.com/repos/jeanslack/Videomass/releases/latest'
    filename = '/home/gianluca/Modelli/porzione.tar.gz'
    response = requests.get(url)
    tarball = response.json()["tarball_url"]
    # -------------------------------------------

    with requests.get(tarball, stream=True) as dw:
        dw.raise_for_status()
        with open(filename, 'wb', encoding='utf8') as f:
            for chunk in dw.iter_content(chunk_size=8192):
                f.write(chunk)

    return filename
