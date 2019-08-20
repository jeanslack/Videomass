#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from pubsub import pub

def update(msg):
    print('sono su update')
    print(msg)

def ff():
    
    print('sono su ff')
    pub.subscribe(update, "UPDATE_EVT")
    

def mai():
    print('sono su mai')
    msg = 'ciao baby'
    pub.sendMessage("UPDATE_EVT", msg=msg)
    
ff()
