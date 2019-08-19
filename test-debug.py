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

ff_encoders('ffmpeg')
