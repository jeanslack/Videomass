#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import subprocess

def ff_encoders(ffmpeg_link):
    try: # grab buildconf:
        p = subprocess.run([ffmpeg_link, 
                                '-loglevel', 
                                'error', 
                                '-encoders'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.STDOUT,)
        _f = p.stdout
    except FileNotFoundError as e:
        return('Not found', e)
            
    encoders = _f.split(b'\n')
    
    #demux_supp = []
    #mux_supp = []
    #demux_mux_supp = []
    
    diz = {'Video':[], 'Audio':[], 'Subtitle':[]}
    
    for f in encoders:
        if f.strip().startswith(b'V'):
            diz['Video'].append(f.strip().decode())
        elif f.strip().startswith(b'A'):
            diz['Audio'].append(f.strip().decode())
        elif f.strip().startswith(b'S'):
            diz['Subtitle'].append(f.strip().decode())
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

ff_encoders('ffmpeg')
