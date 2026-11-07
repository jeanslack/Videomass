# -*- coding: UTF-8 -*-
"""
Name: generic_downloads.py
Purpose: generic network download operation
Compatibility: Python >= 3.11, wxPython4 Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Oct.30.2026
Code checker: flake8, pylint, ruff

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

import shutil
import urllib.error
import urllib.request
from threading import Thread

import requests
import wx
from pubsub import pub


class FileDownloading(Thread):
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
        self.start()  # start the thread (va in self.run())

    # ----------------------------------------------------------------#

    def run(self):
        """
        Check for new version release
        """
        headers = {"User-Agent": "Mozilla/5.0"}
        page = urllib.request.Request(self.url, headers=headers)
        try:
            # Removed the disabling of SSL certificate validation
            # for security reasons (SAST compliance)
            with (
                urllib.request.urlopen(page) as response,
                open(self.filename, "wb") as out_file,
            ):
                shutil.copyfileobj(response, out_file)

            self.status = self.url, None

        except urllib.error.HTTPError as error:
            self.status = None, error

        except urllib.error.URLError as error:
            self.status = None, error

        self.data = self.status

        wx.CallAfter(pub.sendMessage, "RESULT_EVT", status="")


# ---------------------------------------------------------------------#


def download_bigfile(url, filename):
    """
    Network download operation via `requests`. It is used to
    download big files and save them on filesystem.

    Example to get tarball_url name from github:
    `get_github_releases(url, keyname)` see function on IO module.
    url = 'https://api.github.com/repos/jeanslack/Vidtuber/releases/latest'
    filename = '/home/gianluca/Modelli/porzione.tar.gz'

    """
    # ------------------------------------------

    # Se l'URL punta alle API GitHub, estrae dinamicamente link tarball reale
    if "api.github.com" in url:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        url = response.json()["tarball_url"]

    # Removed encoding='utf-8' not compatible with binary mode 'wb'
    with requests.get(url, stream=True, timeout=10) as dwnl:
        dwnl.raise_for_status()
        with open(filename, "wb") as fname:
            for chunk in dwnl.iter_content(chunk_size=8192):
                fname.writelines(chunk)

    return filename
