# -*- coding: UTF-8 -*-

#########################################################
# Name: os_interaction.py
# Porpose: module with standard tools for OS
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2015-2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
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

# Rev (01) 17/01/2015
#########################################################

"""
The module contains some useful function for copying, moving, deleting 
and renaming files and folders.

"""
import shutil
import os
import glob


def copy_restore(src, dest):
    """
    function for restore file. File name is owner choice and can be an preset
    or not. If file exist overwrite it.
    """
    shutil.copyfile(src, '%s' % (dest))

#------------------------------------------------------------------#
def copy_backup(src, dest):
    """
    function for backup file. File name is owner choice
    """
    shutil.copyfile('%s' % (src), dest)

#------------------------------------------------------------------#
def makedir_move(ext, name_dir):
    """
    this function is for make directory and move-in file (ext, name_dir: 
    extension, directory name)
    """
    try: # if exist dir not exit OSError, go...
        os.mkdir("%s" % (name_dir))
    except: OSError
    move_on(ext, name_dir)

#------------------------------------------------------------------#
def rename_move_indir(src, ext, name_dir):
    """
    this function includes "makedir_move(ext, name_dir)" function but cycling 
    files renames groups
    """
    for path in os.listdir(os.getcwd()):
        nuovoNome = path.replace("%s" % (src), "%s" % (ext))
        os.rename(path, nuovoNome)
    try:
        os.mkdir("%s" % (name_dir))
    except: OSError
    
    move_on(ext, name_dir)

#------------------------------------------------------------------#
def rename_file(src, ext):
    """
    Cycling for file rename groups only
    """
    for path in os.listdir(os.getcwd()):
        nuovoNome = path.replace("%s" % (src), "%s" % (ext))
        os.rename(path,nuovoNome)

#------------------------------------------------------------------#
def move_on(ext, name_dir):
    """
    Cycling on name extension file and move-on in other directory
    """
    files = glob.glob("*%s" % (ext))
    for sposta in files:
        #shutil.move(sposta, '%s' % (name_dir))
        print '%s   %s' % (sposta,name_dir)
        
#------------------------------------------------------------------#
def copy_on(ext, name_dir, path_confdir):
    """
    Cycling on path and file extension name for copy files in other directory
    ARGUMENTS:
    ext: files extension with no dot
    name_dir: path name with no basename
    """
    files = glob.glob("%s/*.%s" % (name_dir, ext))
    
    for copia in files:
        shutil.copy(copia, '%s' % (path_confdir))

#------------------------------------------------------------------#
def delete(ext):
    """
    function for file group delete with same extension
    """
    files = glob.glob("*%s" % (ext))
    for rimuovi in files:
        os.remove(rimuovi)

#------------------------------------------------------------------#
def delete_noempty_dir(path):
    """
    Delete a entire directory no empty
    """
    shutil.rmtree(path)

#------------------------------------------------------------------#
#def exist_file(inputfile):
    #"""
    #Control if exist an file name
    
    #"""
    #os.chdir(PWD)
    #file_exist =  os.path.isfile(os.path.join(PWD,'%s' % inputfile))
    #if file_exist is False:
        #call('clear', shell = True) 
        #print ("Nella directory: '%s'\nNessun file da processare che abbia "
            #"questo nome:\033[0;1m %s\033[0m" % (PWD, inputfile)
            #)
        #sys.exit("...Error\n")
