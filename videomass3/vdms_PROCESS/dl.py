#!/usr/bin/env python3




#['python', '/home/gianluca/.config/youtube-dlg/youtube-dl', '--newline', '-i', '-o', 
 #'/home/gianluca/Immagini/%(title)s.%(ext)s', '-f', 'webm', '--ignore-config', '--hls-prefer-native', 
 #'https://www.youtube.com/watch?v=i_SSmsF_RGw&list=PL_Ybd3jiyiLeRBvbMdeZmWcZ4Yw0VqcxH&index=3']




#from __future__ import unicode_literals
#import youtube_dl

#ydl_opts = {}
#with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    #ydl.download(['https://www.youtube.com/watch?v=COK6FN474gs'])


from __future__ import unicode_literals
#import subprocess
#import shlex
import youtube_dl


def sizeof_fmt(num, suffix='B'):
    print(num)
    num = int(num)
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

#-------------------------------------------------------------------------
#### DOWNLOAD CON HOOK E LOGGER
#-------------------------------------------------------------------------
def riceiver(output, duration, status):
    
    if status == 'ERROR':
        print('msg errore:: ', output)
        #pass
    elif status == 'WARNING':
        print('messaggi warning:: ', output)
        #pass
        
    elif status == 'DEBUG':
        print('messaggi in console:: ', output)
        #pass
        
    elif status == 'DOWNLOAD':
        print(status + ':: ', duration)
        #pass
        
    elif status == 'FINISHED':
        print('FINEEEE ', duration)
        #pass

class MyLogger(object):
    
    def debug(self, msg):
        riceiver(msg, None, 'DEBUG',)
        #pass
        
    def warning(self, msg):
        riceiver(msg, None, 'WARNING')


    def error(self, msg):
        riceiver(msg, None, 'ERROR')

def my_hook(d):
    #print('stampa',d)
    
    if d['status'] == 'downloading':
        duration = ('{}: {} of {} at {} ETA {}'.format(d['status'], 
                                                       d['_percent_str'], 
                                                       d['_total_bytes_str'], 
                                                       d['_speed_str'],
                                                       d['_eta_str'], 
                                                       ))
        
        riceiver(None, duration, 'DOWNLOAD')
        
    if d['status'] == 'finished':
        riceiver(None, 'Done downloading, now converting ...', 'FINISHED')

def downloader(urls):  
    for url in urls:
        
        ydl_opts = {
                    #'format': '140',
                    'format': 'best',
                    'outtmpl': '/home/gianluca/Video/%(title)s.%(ext)s',
                    'restrictfilenames' : True,
                    'ignoreerrors' : True,
                    'no_warnings' : True,
                    'writethumbnail': False,
                    'noplaylist': True,
                    #'postprocessors': [{
                                        #'key': ''FFmpegExtractAudio'',
                                        #'preferredcodec': 'mp3',
                                        #'preferredquality': '192',
                                        #}],
                    'logger': MyLogger(),
                    'progress_hooks': [my_hook],
                    }
                    
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            #ydl.download(['https://www.youtube.com/watc'])

downloader(['https://www.youtube.com/watc', 'https://www.youtube.com/watch?v=BaW_jenozKc'])
    
#-------------------------------------------------------------------------    
#### EXTRACT INFO
#-------------------------------------------------------------------------
#link = 'https://www.youtube.com/watch?v=BaW_jenozKc'
#link = 'https://www.youtube.com/watch?v=9bZkp7q19f0'
#link = 'https://www.youtube.com/watc'
#link = 'https://www.youtube.com/watch?v=EeyyGmd5dvM&list=PL_Ybd3jiyiLeRBvbMdeZmWcZ4Yw0VqcxH' 
##ydl_opts = {'listformats': True }
#ydl_opts = {'ignoreerrors' : True, 'noplaylist': True,}# 'logger': MyLogger(),}
#with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    #meta = ydl.extract_info( link, download=False)

    #if meta:
        #formats = meta.get('formats', [meta])
    #else:
        #print('\nERROR\n')
        
#for f in formats:
    #if f['vcodec'] == 'none':
        #vcodec = ''
        #fps = ''
    #else:
        #vcodec = f['vcodec']
        #fps = '%sfps' % f['fps']
        
                  
    #if f['acodec'] == 'none':
        #acodec = 'Video only'
    #else:
        #acodec = f['acodec']
        
    #if f['filesize']:
        #size = sizeof_fmt(f['filesize'])
    #else:
        #size = ''
                  
    #print('| %s| %s | %s | %s | %s | %s | %s | ' %(f['format_id'], f['ext'], f['format'].split('-')[1], vcodec,
          #acodec, size, fps))

#-------------------------------------------------------------------------
#### CON SUBPROCESS
#-------------------------------------------------------------------------
#try:
    #cmd = ('youtube-dl -o "/home/gianluca/Video/%(title)s.%(ext)s" --ignore-config '
           #'--restrict-filenames --prefer-free-formats '
           #'"https://www.youtube.com/watch?v=BaW_jenozKc"')
    ##cmd = ('youtube-dl --newline -o "/home/gianluca/Video/%(title)s.%(ext)s" --ignore-config '
           ##'--restrict-filenames --prefer-free-formats '
           ##'')

    #with subprocess.Popen(shlex.split(cmd),
                          #stdout=subprocess.PIPE,
                          #stderr=subprocess.STDOUT,
                          ##stderr=subprocess.PIPE, 
                          ##stdout=subprocess.PIPE, 
                          #bufsize=1, 
                          #universal_newlines=True) as p:
        #for line in p.stdout:
            ##sys.stdout.write(line)
            ##sys.stdout.flush()
            ##print('PROVA ', line, end='')
            #if '[download]' in line:
                #if not 'Destination' in line:
            
                    #print(line.split()[1])
            
        #if p.wait(): # error
            #print('status error: ', p.wait(), 'errore: ', line)
        #else:
            #print('ok')
            
#except OSError as err:
    #print('questo è un errore: ', err)
