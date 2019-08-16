#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import subprocess

def ffmpeg_conf(ffmpeg_link):
    """
    Execute FFmpeg without arguments to parse output 
    configuration  messages
    
    ...Returns lists of:
        - info = [version number etc, release and building]
        - others = [building flags]
        - enable = [enabled features]
        - disable = [disable features]
    
    ...If errors returns 'Not found'
    
    """
    try: # grab generic informations:
        p = subprocess.check_output([ffmpeg_link, '-version'])
    except OSError as e:
        return('Not found', e)

    info = []

    print p.split('\n')

    return
    ##########################################
    for v in _vers:
        for a in v:

            print a
        #if 'ffmpeg version' in v:
            #info.append(v.strip().decode())
        #if 'built with' in v:
            #info.append(v.strip().decode())
    
    try: # grab buildconf:
        p = subprocess.Popen([ffmpeg_link, 
                              '-loglevel', 
                              'error', 
                              '-buildconf'], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.STDOUT,)
        build = p.communicate()
    except OSError as e:
        return('Not found', e)
    
    conf = []
    for c in build.split('\n'):
        conf.append(c.strip().decode())

    enable = []
    disable = []
    others = []

    for en in conf:
        if en.startswith('--enable'):
            enable.append(en.split('--enable-')[1])
        elif en.startswith('--disable'):
            disable.append(en.split('--disable-')[1])
        else:
            others.append(en)
    if 'configuration:' in others:
        others.remove('configuration:')
    #if '' in others:
        #others.remove('')
    
    return(info, others, enable, disable)

def funz(ffmpeg_link):
    try: # grab buildconf:
        p = subprocess.run([ffmpeg_link, 
                                '-loglevel', 
                                'error', 
                                '-formats'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.STDOUT,)
        _f = p.stdout
    except FileNotFoundError as e:
        return('Not found', e)
            
    frmt = _f.split(b'\n')
    
    demux_supp = []
    mux_supp = []
    demux_mux_supp = []
    
    diz = {'Demuxing Supported':[], 'Muxing Supported':[], 'Mux/Demux Supported':[]}
    
    
    #for f in frmt:
        #if f.strip().startswith(b'D '):
            #demux_supp.append(f)
        #elif f.strip().startswith(b'E '):
            #mux_supp.append(f)
        #elif f.strip().startswith(b'DE '):
            #demux_mux_supp.append(f)
    
    for f in frmt:
        if f.strip().startswith(b'D '):
            diz['Demuxing Supported'].append(f.replace(b'D', b'', 1).strip())
        elif f.strip().startswith(b'E '):
            diz['Muxing Supported'].append(f.replace(b'E', b'', 1).strip())
        elif f.strip().startswith(b'DE '):
            diz['Mux/Demux Supported'].append(f.replace(b'DE', b'', 1).strip())
    print(diz)

    #for b in demux_mux_supp:
        #print(b)
        
        
    #info = []
    #conf = []

    #for vers in err[1].split(b'\n'):
        ##if vers.startswith(b'ffmpeg version'):
        #if b'ffmpeg version' in vers:
            #info.append(vers.decode())
        #if b'built with' in vers:
            #info.append(vers.decode())
        #if b'configuration' in vers:
            #conf.append(vers.decode())

    #enable = []
    #disable = []
    #others = []
    ##print(conf[0].split())
    #for e in conf[0].split():
        #if e.startswith('--enable'):
            #enable.append(e)
        #elif e.startswith('--disable'):
            #disable.append(e)
        #else:
            #others.append(e)
            
    #print(enable)
    #print(disable)
    #print(others)

    #for x in enable:
        #print(x.split('--enable')[1])

#Formats('ffmpeg')
ffmpeg_conf('ffmpe')
