# -*- coding: UTF-8 -*-

#########################################################
# File Name: preset_manager_properties.py
# Porpose: module for managing the properties of the preset manager panel
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/19 Gianluca Pernigoto <jeanlucperni@gmail.com>
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

# Rev (09) 16 july 2018
# Rev (10) 3 Sept 2018
# Rev (11) 6 Sept 2018
#########################################################

import wx
import os
from xml.dom.minidom import parseString

DIRNAME = os.path.expanduser('~') # /home/user

#------------------------------------------------------------------#
def supported_formats(array3, file_sources):
    """
    Verifica del supporto al formato dei file importati secondo
    le specifiche in array[3] in presets manager

    """
    supported = array3.split()# diventa una lista
    exclude = []# se viene riempita la usano i dialoghi MessageBox

    #-------------- SUPPORTED CONTROL
    if supported:
        for sources in file_sources:#itero su ogni file input
            basename = os.path.basename(sources)#nome file (con ext)
            base_ext = os.path.splitext(basename)[1]#estensione con dot
            ext = base_ext.replace('.','')
            if  ext not in supported:
                exclude.append(sources)
        if exclude:
            for x in exclude:
                file_sources.remove(x)
            if not file_sources:
                wx.MessageBox(_(u"The selected profile is not suitable to "
                                u"convert the following file formats:\n\n%s\n\n") 
                              % ('\n'.join(exclude)), 
                              _(u"Videomass: Unsuitable format"), 
                              wx.ICON_WARNING | wx.OK, 
                              None
                              )
                return (False)
            
    return (file_sources)

########################################################################
# PARSINGS XML FILES AND FUNCTION FOR DELETING
########################################################################

def parser_xml(arg): # arg é il nome del file xml (vdms) 
    """
    This function it is called by presets_mng_panel.py for make a parsing 
    and read the presets memorized on vdms files.
    The vdms files are xml files with extension '.vdms' .
    The (arg) argument is a name of the vdms file to parse. 
    The xml.dom.minidom it is used to parsing vdms files and return a value 
    consisting of dictionaries containing other dictionaries in this form:
    {name: {filesupport:?, descript:?, command:?, extens:?}, else: {etc etc}}
    
    """
    with open('%s/.videomass/%s.vdms' %(DIRNAME, arg),'r') as fread:
        data = fread.read()

    parser = parseString(data) # fa il parsing del file xml ed esce: 
                            # <xml.dom.minidom.Document instance at 0x8141eec>
    dati = dict() 
    for presets in parser.getElementsByTagName("presets"):
        for preset in presets.getElementsByTagName("label"):
            name = preset.getAttribute("name")
            types = preset.getAttribute("type")
            parameters = None
            filesupport = None
            extension = None
            
            for presets in preset.getElementsByTagName("parameters"):
                for parameters in presets.childNodes:
                    params = parameters.data
                    
            for presets in preset.getElementsByTagName("filesupport"):
                for filesupport in presets.childNodes:
                    support = filesupport.data

            for presets in preset.getElementsByTagName("extension"):
                for extension in presets.childNodes:
                    ext = extension.data

            dati[name] = { "type": types, "parametri": params, 
                           "filesupport": support, "estensione": ext }
    #return dati[name]

    return dati
#------------------------------------------------------------------#

def delete_profiles(array, filename):
    """
    Funzione usata nel modulo presets_mng_panel.py per cancellare singole 
    voci (i profili) dei presets selezionati nella listcontrol.

    dati é il dizionario iterabile passato dal modulo parser_xml qui sopra

    array é solo una chiave del diz messa in lista e contiene cinque elementi: 
    name descr command  support ext 
    Array viene creata in presets_mng_panel.py nella 
    funzione def on_select()

    """
    
    dati = parser_xml(filename)
    #dirconf = os.path.expanduser('~/.videomass/%s.vdms' % (filename))
    dirconf = '%s/.videomass/%s.vdms' % (DIRNAME, filename)
    
    """
    Posso anche usare i dizionari al posto degli indici lista (sotto i cicli 
    for) ma ho deciso per gli indici lista, es: 
    
    #name_preset = array[0].encode("utf-8")
    #description = param["type"].encode("utf-8")
    #commands_ffmpeg = param["parametri"].encode("utf-8")  # not more used
    #file_support = param["filesupport"].encode("utf-8")   # not more used
    #file_extension = param["estensione"].encode("utf-8")  # not more used
    
    """
    
    param = dati[array[0]] # da il dizionario completo

    name_preset = array[0].encode("utf-8")
    description = array[1].encode("utf-8")

    """
    I can use 'with open(...)' or 'fxml = open(...)' but i prefer open,
    put in list and close the file:
    """
    #fxml = open('%s' % (dirconf),'r').readlines()
    with open('%s' % (dirconf),'r') as data:
        fxml = data.readlines()
    
    """
    Nella versione precedente, usavo il sistema con il metodo .index() ma 
    causava degli errori. Non trova title=fxml.index a volte (Vedi il 
    changelog) per errori di occorrenze.

    SOLUZIONE:
    title + 1 (oppure indx +1 -vedi sotto-) avanza sempre di uno rispetto a
    title, e sempre solo a quello. Questa soluzione dovrebbe impedire di 
    eliminare identiche occorrenze tipo <filesupport> </filesupport> nella 
    ricerca in fxml
    
    """
    title = '    <label name="%s" type="%s">\n' % (name_preset, description)
    
    for indx, row in enumerate(fxml): # mi da l'indx (come index)
                                            # ma anche la stringa in riga
        if title in row:
            
            for i in range(0,4): # ripete la stessa esecuzione per 4 volte
                del fxml[indx + 1]
            # il for sopra, mi serializza l'esecuzione di 'del' per 4 volte.
            # Fa la stessa cosa del codice fra i trattini qui sotto ma é più 
            # elegante:
            #----------------------------------------------#
            #del fxml [indx + 1] # label iniziale
            #del fxml [indx + 1] # command ffmpeg
            #del fxml [indx + 1] # file support
            #del fxml [indx + 1] # estensione
            #----------------------------------------------#

            if fxml [indx + 1] == "\n":
                del fxml [indx + 1] # lo spazio
                
            del fxml [indx] # per ultimo cancello il name e type
            
    # FIXME: c'é sempre una linea in più quando cancelli tutti i profili,
    #        questo non impedisce la corretta esecuzione ma influenza la
    #        formattazione del testo. L'occhio vuole la sua parte!

    with open('%s' % (dirconf),'w') as f:
        f.writelines(fxml)
