# -*- coding: UTF-8 -*-
"""
Name: ffprobe_parser.py
Porpose: cross-platform API for ffprobe
Compatibility: Python3, Python2
Platform: all platforms
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyright: (c) 2018/2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: May.11.2021
Code checker:
    flake8: --ignore F821, W504
    pylint: --ignore E0602, E1101
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
import subprocess
import platform
import re
if not platform.system() == 'Windows':
    import shlex


class FFProbe():
    """
    FFProbe wraps the ffprobe command and pulls the data into
    an object form. The `parse` argument defines the parser's behavior.

    If you specify `parser=True' (default) which give an auto-parsed output
    in a object list for each instance (see examples below). The `select`,
    `entries`, and `writer` arguments will be ignored;

    If you specify `parse=False` you  get a customized output characterized
    by the arguments you define. Note that in this case the output given by
    custom_output() instance will always be given in a string object.
    For instance, if you use `writer=json' you must use `eval' function
    to obtain a dict object.

    ---------------------
    USE with `parse=True` (default):
    ---------------------

    >>> from ffprobe_parser import FFProbe

    >>> data = FFProbe('ffprobe_url',
                       'filename_url',
                       parse=True,
                       pretty=True,
                       select=None,
                       entries=None,
                       show_format=True,
                       show_streams=True,
                       writer=None
                       )

        First handle possible exceptions, example:

            if data.error_check():
                print ("Some Error:  %s" % (data.error))

            else:
                video = data.video_stream()
                audio = data.audio_stream()
                subtitle = data.subtitle_stream()
                dataformat = data.data_format())

                formatdict = dict()
                for items in dataformat:
                    for line in items:
                        if '=' in line:
                            k, v = line.split('=')
                            formatdict[k.strip()] = v.strip()
                print(formatdict)

    ----------------------
    USE with `parse=False`:
    ----------------------

    >>> from ffprobe_parser import FFProbe

        Get simple output data:
        -----------------------

            `data = FFProbe(FFPROBE_URL,
                            filename_url,
                            parse=False,
                            writer='xml')
                            )`

            First handle possible exceptions, example:

                if data.error_check():
                    print("Some Error:  %s" % (data.error))

                else:
                    print(data.custom_output())

        To get a kind of output:
        ------------------------

             A example entry of a first audio streams section

            `data = FFProbe(FFPROBE_URL,
                            filename_url,
                            parse=False,
                            pretty=True,
                            select='a:0',
                            entries='stream=codec_type',
                            show_format=False,
                            show_streams=False,
                            writer='compact=nk=1:p=0'
                            )`

            First handle possible exceptions, example:

                if data.error_check():
                    print("Some Error:  %s" % (data.error))
                else:
                    print(data.custom_output().strip())

            The `entries` arg is the key to search some entry on sections

                entries='stream=codec_type,codec_name,bits_per_sample'
                entries='format=duration'

            The `select` arg is the key to select a specified section

                select='' # select all sections
                select='v' # select all video sections
                select='v:0' # select first video section

            The `writer` arg alias:

                writer='default=nw=1:nk=1'
                writer='default=noprint_wrappers=1:nokey=1'

                available writers name are:

                `default`, `compact`, `csv`, `flat`, `ini`, `json` and `xml`

                Options are list of key=value pairs, separated by ":"

                See `man ffprobe`

    ------------------------------------------------
    [i] This class was partially inspired to:
    ------------------------------------------------
        <https://github.com/simonh10/ffprobe/blob/master/ffprobe/ffprobe.py>

    """

    def __init__(self, FFPROBE_URL, filename, parse=True,
                 pretty=True, select=None, entries=None,
                 show_format=True, show_streams=True, writer=None):
        """
        -------------------
        Parameters meaning:
        -------------------
            FFPROBE_URL     command name by $PATH defined or a binary url
            filename_url    a pathname appropriately quoted
            parse           defines the output mode
            show_format     show format informations
            show_streams    show all streams information
            select          select which section to show (''= all sections)
            entries         get one or more entries
            pretty          get human values or machine values
            writer          define a format of printing output

        --------------------------------------------------
        [?] to know the meaning of the above options, see:
        --------------------------------------------------
            <http://trac.ffmpeg.org/wiki/FFprobeTips>
            <https://slhck.info/ffmpeg-encoding-course/#/46>

        -------------------------------------------------------------------
        The ffprobe command has stdout and stderr (unlike ffmpeg and ffplay)
        which allows me to initialize separate attributes also for errors
        """
        self.error = False
        self.mediastreams = []
        self.mediaformat = []
        self.video = []
        self.audio = []
        self._format = []
        self.subtitle = []
        self.writer = None
        self.datalines = []
        pretty = '-pretty' if pretty is True else 'no_pretty'
        show_format = '-show_format' if show_format is True else ''
        show_streams = '-show_streams' if show_streams is True else ''
        select = '-select_streams %s' % select if select else ''
        entries = '-show_entries %s' % entries if entries else ''
        writer = '-of %s' % writer if writer else '-of default'

        if parse:
            cmnd = ('"%s" -i "%s" -v error %s %s %s '
                    '-print_format default' % (FFPROBE_URL,
                                               filename,
                                               pretty,
                                               show_format,
                                               show_streams,)
                    )
        else:
            cmnd = '"%s" -i "%s" -v error %s %s %s %s %s %s' % (FFPROBE_URL,
                                                                filename,
                                                                pretty,
                                                                select,
                                                                entries,
                                                                show_format,
                                                                show_streams,
                                                                writer
                                                                )
        if not platform.system() == 'Windows':
            cmnd = shlex.split(cmnd)
            info = None
        else:
            # Hide subprocess window on MS Windows
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        try:
            with subprocess.Popen(cmnd,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  universal_newlines=True,
                                  startupinfo=info,
                                  ) as proc:
                output, error = proc.communicate()
                if proc.returncode:
                    self.error = error
                if parse:
                    self.parser(output)
                else:
                    self.writer = output

        except (OSError, FileNotFoundError) as err:
            self.error = err
            return
    # -------------------------------------------------------------#

    def parser(self, output):
        """
        Indexes the catalogs [STREAM\\] and [FORMAT\\] given by
        the default output of FFprobe
        """
        probing = output.split('\n')  # create list with strings element

        for streams in probing:
            if re.match('\\[STREAM\\]', streams):
                self.datalines = []

            elif re.match('\\[\\/STREAM\\]', streams):
                self.mediastreams.append(self.datalines)
                self.datalines = []
            else:
                self.datalines.append(streams)

        for fformat in probing:
            if re.match('\\[FORMAT\\]', fformat):
                self.datalines = []

            elif re.match('\\[\\/FORMAT\\]', fformat):
                self.mediaformat.append(self.datalines)
                self.datalines = []
            else:
                self.datalines.append(fformat)

    # --------------------------------------------------------------#

    def video_stream(self):
        """
        Return a metadata list for video stream. If there is not
        data video return a empty list
        """
        for datastream in self.mediastreams:
            if 'codec_type=video' in datastream:
                self.video.append(datastream)
        return self.video
    # --------------------------------------------------------------#

    def audio_stream(self):
        """
        Return a metadata list for audio stream. If there is not
        data audio return a empty list
        """
        for datastream in self.mediastreams:
            if 'codec_type=audio' in datastream:
                self.audio.append(datastream)
        return self.audio
    # --------------------------------------------------------------#

    def subtitle_stream(self):
        """
        Return a metadata list for subtitle stream. If there is not
        data subtitle return a empty list
        """
        for datastream in self.mediastreams:
            if 'codec_type=subtitle' in datastream:
                self.subtitle.append(datastream)
        return self.subtitle
    # --------------------------------------------------------------#

    def data_format(self):
        """
        Return a metadata list for data format. If there is not
        data format return a empty list
        """
        for dataformat in self.mediaformat:
            self._format.append(dataformat)
        return self._format
    # --------------------------------------------------------------#

    def custom_output(self):
        """
        Print output defined by writer argument. To use this feature
        you must specify parse=False, example:

        `data = FFProbe(filename_url,
                        FFPROBE_URL,
                        parse=False,
                        writer='json')`

        Then, to get output data call this method:

        output = data.custom_output()

        Valid writers are: `default`, `json`, `compact`, `csv`, `flat`,
        `ini` and `xml` .
        """
        return self.writer
    # ----------------------------------------------------------------#

    def error_check(self):
        """
        check for errors on stderr of the ffprobe command. It also
        handles the IOError exception. You can use this interface
        before using all other methods of this class.

        """
        return self.error if self.error else None
