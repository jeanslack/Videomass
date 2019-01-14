# -*- coding: UTF-8 -*-

#########################################################
# Name: ffprobe_parser.py (for wxpython >= 2.8)
# Porpose: ffprobe parsing class for Ms Windows
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2014-2018/19 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3

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

# Rev (06) 24/08/2014
# Rev (07) 12/01/2015
# Rev (08) 20/04/2015
# Rev (09) 12 july 2018
#########################################################

import subprocess
import re

########################################################################
# message strings for all the following Classes.
# WARNING: For translation reasons, try to keep the position of these 
#          strings unaltered.
non_ascii_msg = _(u'Non-ASCII/UTF-8 character string not supported. '
                  u'Please, check the filename and correct it.')
not_exist_msg =  _(u'not found in your system')
#########################################################################

class FFProbe(object):
    """
    NOTICE: compatible with python2 and python3.
    
    FFProbe wraps the ffprobe command and pulls the data into an object form:
    
    metadata = FFProbe(filename, ffprobe_link, option)
    
    
    Arguments:
    ---------
    filename: path + filename
    ffprobe_link: the binary (ffprobe) or executable (ffprobe.exe)
    option: 'pretty' or 'no pretty'
    
    You can use the methods of this class for getting metadata in separated 
    list of each stream or format, example:
    
    print (metadata.video_stream())
    print (metadata.audio_stream())
    print (metadata.subtitle_stream())
    print (metadata.data_format())

    USE:
    ----
    First you should do a check for errors that might generate ffprobe 
    or lack of it. Then use control errors interface before referencing the 
    methods, example:

    if metadata.ERROR(): # control for errors
        print ("Some Error:  %s" % (metadata.error))
        return
    else:
        data_format = {}
        for line in metadata.data_format()[0]:
            if '=' in line:
                k, v = line.split('=')
                k = k.strip()
                v = v.strip()
                data_format[k] = v
        print (data_format)
    ------------------------------------------------

    This class was partially inspired to: 
    https://github.com/simonh10/ffprobe/blob/master/ffprobe/ffprobe.py
    """
    def __init__(self, mediafile, ffprobe_link, probeOpt):
        """
        The ffprobe command has stdout and stderr (unlike ffmpeg and ffplay)
        which allows me to initialize separate attributes also for errors
        
        NOTE for subprocess.STARTUPINFO() 
        < Windows: https://stackoverflow.com/questions/1813872/running-
        a-process-in-pythonw-with-popen-without-a-console?lq=1>
        """
        self.error = False
        self.mediastreams = []
        self.mediaformat = []
        self.video = []
        self.audio = []
        self._format = []
        self.subtitle = []
        datalines = []
        
        if probeOpt == 'pretty':
            cmnd = [ffprobe_link, '-show_format', '-show_streams', '-v', 
                    'error', '-pretty', mediafile]
        else:
            cmnd = [ffprobe_link, '-show_format', '-show_streams', '-v', 
                    'error', mediafile]
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE, 
                                 universal_newlines=True,
                                 startupinfo=startupinfo,
                                 )
            output, error =  p.communicate()

            if error:
                self.error = error

        except OSError:
            self.error = "'ffprobe.exe' %s" % not_exist_msg
            return
        
        except UnicodeEncodeError as err:
            e = (non_ascii_msg
                 )
            self.error = e
            return

        raw_list = output.split('\n') # create list with strings element

        for s in raw_list:
            if re.match('\[STREAM\]',s):
                datalines=[]

            elif re.match('\[\/STREAM\]',s):
                self.mediastreams.append(datalines)
                datalines=[]
            else:
                datalines.append(s)

        for f in raw_list:
            if re.match('\[FORMAT\]',f):
                datalines=[]

            elif re.match('\[\/FORMAT\]',f):
                self.mediaformat.append(datalines)
                datalines=[]
            else:
                datalines.append(f)

    def video_stream(self):
        """
        Return a metadata list for video stream. If there is not
        data video return a empty list
        """
        for datastream in self.mediastreams:
            if 'codec_type=video'in datastream:
                self.video.append(datastream)
        return self.video

    def audio_stream(self):
        """
        Return a metadata list for audio stream. If there is not
        data audio return a empty list
        """
        for datastream in self.mediastreams:
            if 'codec_type=audio'in datastream:
                self.audio.append(datastream)
        return self.audio

    def subtitle_stream(self):
        """
        Return a metadata list for subtitle stream. If there is not
        data subtitle return a empty list
        """
        for datastream in self.mediastreams:
            if 'codec_type=subtitle'in datastream:
                self.subtitle.append(datastream)
        return self.subtitle

    def data_format(self):
        """
        Return a metadata list for data format. If there is not
        data format return a empty list
        """
        for dataformat in self.mediaformat:
                self._format.append(dataformat)
        return self._format

    def get_audio_codec_name(self):
        """
        Return a list of possible audio codec name and tag language into
        a video with one or more audio streams. If not audio stream in video 
        return None. This method is useful for exemple to saving audio 
        content as audio track.
        """
        audio_list = self.audio_stream()
        info_list = []
        cn = ''#codec
        st = ''#subtitle
        i = ''# index
        
        if audio_list == []:
            #info_list.append('no audio stream')
            print ('No AUDIO stream metadata found')
            return
        else:    
            n = len(audio_list)
            for a in range(n):
                (key, value) = audio_list[a][0].strip().split('=')
                for b in audio_list[a]:
                    (key, value) = b.strip().split('=')
                    if "codec_name" in key:
                        cn = value
                    if "stream_tags" in key:
                        st = value
                        #stream_tag.append(value)
                    if "index" in key:
                        i = value
                        #stream_index.append(value)
                info_list.append("index: %s | codec: %s | language: %s" % (
                                    i,cn,st))
        return info_list

    def ERROR(self):
        """
        check if there are errors on stderr of ffprobe command or if there 
        is a IOError exception. For output errors you can use this method 
        as control interface before using all other methods of this class.
        """
        if self.error:
            return self.error 
