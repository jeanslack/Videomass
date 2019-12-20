[Back](../../../videomass_use.md)

## Presets Manager

![Image](../../../images/presets_manager.gif)

Presets Manager is an interface that allows a quick selection of profiles to start a conversion process. It is based 
on two types of lists: the list of presets, selectable by a drop down, and the list of selectable profiles.   
Each preset contains one or more profiles that can also be edited or deleted. A user can also create new presets and new profiles.   

A single click on a profile enables it.  
A double click on a profile starts the conversion.

**Note**: each preset is a simple text file with a JSON data structure with ".prst" extension. All presets are located in the Videomass configuration folder.

### The _Selecting Preset_ tab
In this tab there is a list of all presets that can be selected from a drop-down menu. When you create a new preset, it stored to /Videomass/presets folder and the drop-down menu be automatically updated with a new entry.

### The _Command Line FFmpeg_ tab
By selecting the 'Command Line FFmpeg' tab you will see the command of each selected profile. Here you can change the command on the fly by adding new parameters and the conversion process will execute exactly the command you wrote. Remember that a profile changed on the fly will not be stored on the profile. To save a new profile, you will need to use the 'New..' or 'Edit..' functions in the toolbar.

[Back](../../../videomass_use.md)
