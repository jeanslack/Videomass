#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import subprocess

p = subprocess.Popen(['ffmpeg'], stderr=subprocess.PIPE,) 
err = p.communicate()
#out = err[1].split(b'\n')
#print(err)
        

info = []
conf = []

for vers in err[1].split(b'\n'):
    #if vers.startswith(b'ffmpeg version'):
    if b'ffmpeg version' in vers:
        info.append(vers.decode())
    if b'built with' in vers:
        info.append(vers.decode())
    if b'configuration' in vers:
        conf.append(vers.decode())

enable = []
disable = []
others = []
#print(conf[0].split())
for e in conf[0].split():
    if e.startswith('--enable'):
        enable.append(e)
    elif e.startswith('--disable'):
        disable.append(e)
    else:
        others.append(e)
        
#print(enable)
#print(disable)
#print(others)

for x in enable:
    print(x.split('--enable')[1])
