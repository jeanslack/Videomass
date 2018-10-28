[Back](../../../videomass2_use.md)

## Presets Manager

![Image](../../../images/presets_manager.png)

Presets Manager is an interface for managing and using profiles. It is based on two types of lists: the list of presets, 
selectable by a drop down, and the list of profiles that always remains on display. Each preset can contain one or more 
profiles; each profile can be executed as a conversion process; it can be edited or deleted. A user can also create new 
profiles and organize them on certain presets.

### Menu Bar
When you are on the 'Presets Manager' interface, the following functions are enabled in the menubar on _File_:

Export (save) the preset you are on - _Save the current preset as separated file_

that you can import (restore) at any time - _Restore a previously saved preset_

you can also reset the current preset, ie return to the default state, or reset all presets at once. This will erase 
all your customizations to return to the original state.

### Tool Bar (secondary)
* To create a [new profile](https://jeanslack.github.io/Videomass2/Pages/Main_Toolbar/PresetsManager_Panel/Profiles_management.html), press the _New.._ button in the toolbar.
* To delete a profile, press the _Delete.._ button in the toolbar.
* To [edit a profile](https://jeanslack.github.io/Videomass2/Pages/Main_Toolbar/PresetsManager_Panel/Profiles_management.html). press the _Edit.._ button in the toolbar.

### Selecting Preset (tab)
The list of presets, selectable by a drop down. On the _User Profiles_ presets there are the saved profiles that you 
have saved from Video Conversions and Audio Conversions interfaces.

### Command Line FFmpeg (tab)
By selecting the 'Command Line FFmpeg' tab you will see the command of each selected profile. To change a command on the 
fly, you must first enable the write function on the [Setup dialog](https://github.com/jeanslack/Videomass2/blob/gh-pages/Pages/Startup/Setup.md). Remember that a profile changed on the fly will only be applied in the conversion process but will 
not be stored on the profile. To save a profile, you will need to use the 'New ..' function in the tool bar.

[Back](../../../videomass2_use.md)
