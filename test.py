#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import subprocess


def fun():
    
    args = ['ffmpeg','-xxxxx']
    try:
        p = subprocess.check_output(args, stderr=subprocess.STDOUT,)
        #p = subprocess.check_output(args)
    except OSError as oserr: # ffmpeg do not exist
        return('Not found', "'%s' %s" %(args[0], oserr))
    except subprocess.CalledProcessError as e: # args command error
        print('\n')
        print(e.cmd)
        print(e.returncode)
        print(e.output)

stampa = fun()
print(stampa)
