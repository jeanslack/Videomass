# -*- coding: UTF-8 -*-
# Name: ffprobe_parser.py
# Porpose: cross-platform parsing class for ffprobe
# Compatibility: Python3, Python2
# Platform: all platforms
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.06.2020 *PEP8 compatible*
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
import subprocess
import platform
import re


class FFProbe(object):
    """
    FFProbe wraps the ffprobe command and pulls the data into
    an object form:

    `data = FFProbe(FFPROBE_URL, filename_url, parse=True,
                    pretty=True, select=None, entries=None,
                    show_format=True, show_streams=True, writer=None)`

   The `parse` argument defines the parser's behavior; `parse=True` get
   an automatically parsed output with four list-type sections while the
   `select`, `entries`,` writer` arguments will be ignored; `parse=False`
   you get a customized output characterized by the arguments you define.

    ---------------------
    USE with `parse=True`:
    ---------------------

        After referencing the above class, use a convenient way to handle
        possible exceptions, example:

            if data.ERROR():
                print ("Some Error:  %s" % (data.error))
                return
            else:
                print (data.video_stream())
                print (data.audio_stream())
                print (data.subtitle_stream())
                print (data.data_format())

            format_dict = dict()
            for line in data.data_format():
                for items in line:
                    if '=' in items:
                        k, v = items.split('=')
                        k, v = k.strip(), v.strip()
                        data_format[k] = v
            print (data_format)

    ----------------------
    USE with `parse=False`:
    ----------------------

        Get simple output data:
        -----------------------

            `data = FFProbe(FFPROBE_URL,
                            filename_url,
                            parse=False,
                            writer='xml')
                            )`

            After referencing the above class, use a convenient way to handle
            possible exceptions, example:

                if data.ERROR():
                    print ("Some Error:  %s" % (data.error))
                    return

            then, get your custom output:

                print(data.custom_output())

        To get a kind of output:
        ------------------------

             A example entry of a first audio streams section

            `data = FFProbe(FFPROBE_URL,
                            filename_url,
                            parse=False,
                            pretty=True,
                            select='a:0',
                            entries='stream=code_type',
                            show_format=False,
                            show_streams=False,
                            writer='compact=nk=1:p=0'
                            )`

            After referencing the above class, use a convenient way to handle
            possible exceptions, example:

                if data.ERROR():
                    print ("Some Error:  %s" % (data.error))
                    return

            then, get your custom output:

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
            cmnd = ('%s -i "%s" -v error %s %s %s '
                    '-print_format default' % (FFPROBE_URL,
                                               filename,
                                               pretty,
                                               show_format,
                                               show_streams,)
                    )
        else:
            cmnd = '%s -i "%s" -v error %s %s %s %s %s %s' % (FFPROBE_URL,
                                                              filename,
                                                              pretty,
                                                              select,
                                                              entries,
                                                              show_format,
                                                              show_streams,
                                                              writer
                                                              )
        if not platform.system() == 'Windows':
            import shlex
            cmnd = shlex.split(cmnd)
            info = None
        else:
            # Hide subprocess window on MS Windows
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        try:
            p = subprocess.Popen(cmnd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True,
                                 startupinfo=info,
                                 )
            output, error = p.communicate()

        except (OSError, FileNotFoundError) as e:
            self.error = e
            return

        if p.returncode:
            self.error = error
        if parse:
            self.parser(output)
        else:
            self.writer = output
    # -------------------------------------------------------------#

    def parser(self, output):
        """
        Indexes the catalogs [STREAM\\] and [FORMAT\\] given by
        the default output of FFprobe
        """
        probing = output.split('\n')  # create list with strings element

        for s in probing:
            if re.match('\\[STREAM\\]', s):
                self.datalines = []

            elif re.match('\\[\\/STREAM\\]', s):
                self.mediastreams.append(self.datalines)
                self.datalines = []
            else:
                self.datalines.append(s)

        for f in probing:
            if re.match('\\[FORMAT\\]', f):
                self.datalines = []

            elif re.match('\\[\\/FORMAT\\]', f):
                self.mediaformat.append(self.datalines)
                self.datalines = []
            else:
                self.datalines.append(f)

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

    def get_audio_codec_name(self):
        """
        Return title and list of possible audio codec name and
        tag language into a video with one or more audio streams.
        If not audio stream in video return None.
        This method is useful for exemple to saving audio content as
        audio track.
        """
        astream = self.audio_stream()  # get audio stream
        audio_lang = []
        acod = ''  # audio codec
        lang = 'unknown'  # language
        indx = ''  # index
        srate = ''  # smple_rate
        bits = ''  # bit_per_sample (raw only)
        chan = ''  # channel_layout
        bitr = ''  # bit_rate (codec compressed only)

        if astream == []:
            # audio_lang.append('no audio stream')
            return None, None
        else:
            n = len(astream)
            for a in range(n):
                (key, value) = astream[a][0].strip().split('=')
                for b in astream[a]:
                    (key, value) = b.strip().split('=')
                    if "codec_name" in key:
                        acod = value
                    if "stream_tags" in key:
                        lang = value
                    if "TAG:language" in key:
                        lang = value
                    if "index" in key:
                        indx = value
                    if key == "sample_rate":
                        srate = value
                    if key == "bits_per_sample":
                        bits = value
                    if key == "channel_layout":
                        chan = value
                    if key == "bit_rate":
                        bitr = value

                audio_lang.append("index: %s | codec: %s | language: %s "
                                  "| sampe rate: %s | bit: %s | channels: %s "
                                  "| bit rate: %s" % (indx, acod, lang,
                                                      srate, bits, chan,
                                                      bitr)
                                  )
        video_list = self.data_format()  # get video format for video title

        for t in video_list[0]:
            if 'filename=' in t:
                vtitle = t.split('=')[1]
                break
            else:
                vtitle = 'Title unknown'

        return audio_lang, vtitle
    # ----------------------------------------------------------------#

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

    def ERROR(self):
        """
        check for errors on stderr of the ffprobe command. It also
        handles the IOError exception. You can use this interface
        before using all other methods of this class.
        """
        if self.error:
            return self.error
