#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
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
#
import subprocess
import shlex
import os
import time
import sys
import timeit
import re




line = 'frame= 2916 fps=448 q=-1.0 Lsize=    3868kB time=00:01:59.99 bitrate= 264.0kbits/s speed=18.4x'
#from timeit import timeit
#import re
#reo = re.compile('time=(\d+):(\d+):(\d+)\.\d+', re.X)
def regex(line):
    reo = re.compile('time=(\d+):(\d+):(\d+)\.\d+')
    m = reo.search(line)
    if m:
        pos = m.group().split('time=')[1].split(':')
        hours, minutes, seconds = pos[0],pos[1],pos[2][:2]
        #print hours, minutes, seconds

def pyfind(line):
    if 'time=' in line:# ...sta processando
        #chunk = line.split(' ')
        #matching = [s for s in chunk if "time=" in s]
        #pos = matching[0].split('=')[1].split(':')
        #hours, minutes, seconds = pos[0],pos[1],pos[2].split('.')[0]
        #print hours, minutes, seconds

        i = line.index('time=')+5
        print i
        pos = line[i:i+8].split(':')
        hours, minutes, seconds = pos[0],pos[1],pos[2]
    #print hours, minutes, seconds


#regex(line)
pyfind(line)

#from timeit import timeit
#import re
#print (timeit("regex(line)", "from __main__ import regex; line='frame= 2916 fps=448 q=-1.0 Lsize=    3868kB time=00:01:59.99 bitrate= 264.0kbits/s speed=18.4x'"))
#print (timeit("pyfind(line)","from __main__ import pyfind; line='frame= 2916 fps=448 q=-1.0 Lsize=    3868kB time=00:01:59.99 bitrate= 264.0kbits/s speed=18.4x'"))


    #print e
##############################################################################
#DERRICK PETZOID
#def encode(filename, callback=None):
    ##cmd = ('ffmpeg -i "%s" -acodec libfaac -ab 128kb ' + \
          ##'-vcodec mpeg4 -b 1200kb -mbd 2 -flags +4mv ' + \
          ##'-trellis 2 -cmp 2 -subcmp 2 -s 320x180 "%s.mp4"')
    #for files in filename:
        #print '----------------------NOUVO PROCESSO CICLO FOR-------------------------'
        ##cmd = ('ffmpeg -i "%s"  -loglevel error -stats -vn -c:a pcm_s16le -threads 2 -y "%s.wav"')
        #cmd = ('ffmpeg -i "%s" -loglevel error -stats -vcodec libx264 -crf 23 -threads 2 -y "%s.mkv"')
        #pipe = subprocess.Popen(
            #shlex.split(cmd % (files, os.path.splitext(files)[0])),
            #stderr=subprocess.PIPE,
            #close_fds=True
        #)
        #fcntl.fcntl(
            #pipe.stderr.fileno(),
            #fcntl.F_SETFL,
            #fcntl.fcntl(pipe.stderr.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK,
        #)
        ## frame=   29 fps=  0 q=2.6 size=     114kB time=0.79 bitrate=1181.0kbits/s
        #reo = re.compile("""\S+\s+(?P<frame>d+)  # frame
                            #\s\S+\s+(?P<fps>\d+)           # fps
                            #\sq=(?P<q>\S+)                    # q
                            #\s\S+\s+(?P<size>\S+)          # size
                            #\stime=(?P<time>\S+)           # time
                            #\sbitrate=(?P<bitrate>[\d\.]+) # bitrate
                            #""", re.X)
        #while True:
            #readx = select.select([pipe.stderr.fileno()], [], [])[0]
            #if readx:
                #chunk = pipe.stderr.read()
                #sys.stdout.write(chunk)
                #sys.stdout.flush()
                #if chunk == '':
                    #break
                #m = reo.match(chunk)
                #if m and callback:
                    #callback(m.groupdict())
            #time.sleep(.1)

#encode('/media/Disco_Dati/Impiccalo Piu In Alto.ac3')
#lista = ['/media/Disco_Dati/PROVA/joemorello exercise 22.mov', '/media/Disco_Dati/PROVA/joemorelloaround.mov']
#encode(lista)
###############################################################################

#J.F. Sebastian's method 
def enc(filename, callback=None):
    #cmd = ('ffmpeg -i "%s" -acodec libfaac -ab 128kb ' + \
          #'-vcodec mpeg4 -b 1200kb -mbd 2 -flags +4mv ' + \
          #'-trellis 2 -cmp 2 -subcmp 2 -s 320x180 "%s.mp4"')
    for files in filename:
        print ('----------------------NOUVO PROCESSO CICLO FOR-------------------------')
        #cmd = ('ffmpeg -i "%s"  -loglevel error -stats -vn -c:a pcm_s16le -threads 2 -y "%s.wav"')
        cmd = shlex.split('ffmpeg -i "%s" -loglevel error -stats -vcodec libx264 -crf 23 -threads auto -y "%s.mkv"' % (files, os.path.splitext(files)[0]))
        #cmd = ('ffmpeg -i "%s" -loglevel error -stats -vcodec libx264 -crf 23 -threads 2 -y "%s.mkv"' % (files, os.path.splitext(files)[0]))

        #python3
        #with subprocess.Popen(cmd, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
            #for line in p.stderr:
                ##print(line, end='')
                #sys.stdout.write(line)
                #sys.stdout.flush()
        #p.communicate()

        
        #python2
        p = subprocess.Popen(cmd, stderr=subprocess.PIPE, 
                             bufsize=1, universal_newlines=True
                             )
        with p.stderr:
            for line in iter(p.stderr.readline, b''):
                print line,
        err = p.wait()
        if err:
           print 'ERROR'

#encode('/media/Disco_Dati/Impiccalo Piu In Alto.ac3')
#lista = ['/media/Disco_Dati/PROVA/joemorello exercise 22.mov', '/media/Disco_Dati/PROVA/joemorelloaround.mov']
#lista = ['/media/Disco_Dati/PROVA/joemorelloaround.mov']
#enc(lista)


#li = 'frame= 2034 fps=169 q=28.0 size=    2646kB time=00:01:25.44 bitrate= 253.7kbits/s speed=7.08x\n\nframe= 2097 fps=166 q=-1.0 Lsize=    2865kB time=00:01:26.87 bitrate= 270.1kbits/s speed=6.86x '
#print (li.splitlines('\n\n'))


###############################################################################

#cmnd = ['ffmpeg', '-i', files, 'opopo', '-af', 'volumedetect', 
        #'-vn', '-sn', '-dn', '-f', 'null', '/dev/null']

#cmnd = ['ffmpeg -i %s opo -af volumedetect -vn -sn -dn -f null /dev/null' % files]

#p = subprocess.Popen('bestia', stderr = subprocess.PIPE)
#error =  p.communicate()[1]
#raw_list = string.split(error_a) # splitta tutti gli spazi

#print error



#p = subprocess.Popen(cmnd, shell=True, stderr=subprocess.PIPE)
#error =  p.communicate()[1]

##p.wait()
#print p.returncode

#if p.returncode:
    #print error
    
#if error != '':
    #print 'si'

#p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#output, error =  p.communicate()

#print output
#print error

#p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
#output = p.stderr
#print output




#txt = None
#while txt != '':

    ##print 'thread status', STATUS_ERROR
    ##print 'thread change', CHANGE_STATUS
    #txt = output.read()
    #print txt
    #if txt == '':
        #print 'si'
#print '------------------post-----------------'


#FFmpegtxt = ''

#FFmpegtxt = """
#ffmpeg -i '/media/Disco_Dati/butta.wav' -loglevel info -af volume=4.7dB -c:v  -c:a libmp3lame -threads 2 -y '/media/Disco_Dati/joemorello exercise 22.mp4'    
#ffmpeg version 3.2.12-1~deb9u1 Copyright (c) 2000-2018 the FFmpeg developers
  #built with gcc 6.3.0 (Debian 6.3.0-18+deb9u1) 20170516
  #configuration: --prefix=/usr --extra-version='1~deb9u1' --toolchain=hardened --libdir=/usr/lib/x86_64-linux-gnu --incdir=/usr/include/x86_64-linux-gnu --enable-gpl --disable-stripping --enable-avresample --enable-avisynth --enable-gnutls --enable-ladspa --enable-libass --enable-libbluray --enable-libbs2b --enable-libcaca --enable-libcdio --enable-libebur128 --enable-libflite --enable-libfontconfig --enable-libfreetype --enable-libfribidi --enable-libgme --enable-libgsm --enable-libmp3lame --enable-libopenjpeg --enable-libopenmpt --enable-libopus --enable-libpulse --enable-librubberband --enable-libshine --enable-libsnappy --enable-libsoxr --enable-libspeex --enable-libssh --enable-libtheora --enable-libtwolame --enable-libvorbis --enable-libvpx --enable-libwavpack --enable-libwebp --enable-libx265 --enable-libxvid --enable-libzmq --enable-libzvbi --enable-omx --enable-openal --enable-opengl --enable-sdl2 --enable-libdc1394 --enable-libiec61883 --enable-chromaprint --enable-frei0r --enable-libopencv --enable-libx264 --enable-shared
  #libavutil      55. 34.101 / 55. 34.101
  #libavcodec     57. 64.101 / 57. 64.101
  #libavformat    57. 56.101 / 57. 56.101
  #libavdevice    57.  1.100 / 57.  1.100
  #libavfilter     6. 65.100 /  6. 65.100
  #libavresample   3.  1.  0 /  3.  1.  0
  #libswscale      4.  2.100 /  4.  2.100
  #libswresample   2.  3.100 /  2.  3.100
  #libpostproc    54.  1.100 / 54.  1.100
#Guessed Channel Layout for Input Stream #0.0 : stereo
#Input #0, wav, from '/media/Disco_Dati/butta.wav':
  #Metadata:
    #encoder         : Lavf57.56.101
  #Duration: 00:00:01.30, bitrate: 1411 kb/s
    #Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 44100 Hz, stereo, s16, 1411 kb/s
#[NULL @ 0x56501df0cb80] Unable to find a suitable output format for 'libmp3lame'
#libmp3lame: Invalid argument



#"""

#status_run = 0 # se superiore a zero da Interrupted process

##FFmpegtxt = ''.join(msg)#da lista a stringa
#lines = FFmpegtxt.split('\n')#splitto gli a capo e va in lista
#num = len(lines)#conto gli elementi in lista
#err_list = ('not found', 'Invalid data found when processing input',
            #'Error', 'Invalid', 'Option not found', 'Unknown',
            #'No such file or directory')
#try:
    #if status_run:
        #print ('\n ..Interrupted Process!\n')
        
    #elif not status_run:
        #for err in err_list:
            #if err in FFmpegtxt:
                #for item in lines:
                    #if err in item:
                        #error = item.strip()
                #print ('\n Failed!\n')
                #print (" %s\n" % (error))

    #else:
        #print ('\n *** Process successfully! ***\n')
        
#except IndexError:
    #e = '\n ..Unrecognized Error\n (See FFmpeg text above)\n'
    #print (e)
    
#else:# viene sempre eseguito anche se errore
    #print 'sys.stdout.flush()'

#finally:# viene sempre eeguito anche se errore

    #print 'self.button_stop.Enable(False)'
    #print 'self.button_close.Enable(True)'


