[Back](../../../videomass2_use.md)

## Presets Manager

![Image](../../../images/presets_manager.png)

Presets Manager is an interface for managing and using profiles. It is based on two types of lists: the list of presets, 
selectable by a drop down, and the list of profiles that always remains on display. Each preset can contain one or more 
profiles; each profile can be executed as a conversion process; it can be edited or deleted. A user can also create new 
profiles and organize them on certain presets.   

Each preset is an xml file with a .vdms extension containing the entries of each profile stored on a specific preset. 
All presets are located in the Videomass2 configuration directory.

### Menu Bar
When you are on the 'Presets Manager' interface, the following functions are enabled in the menubar - _File_:

- _Save the current preset as separated file_ (export the selected preset)

- _Restore a previously saved preset_ (import and replace a preset)

- _reset the current preset_  (ie return to the default state)   

- _reset all presets_ (reset all presets at once. This will erase all your customizations 
  to return to the original state.)

- _Reload Presets List_ (This feature can be useful when you import new presets previously exported)

### The "New", "Delete" and "Edit" buttons
![Image](../../../images/presets_manager_buttons.png)   
These buttons are shown on the toolbar when the **Presets Manager** interface is active.
* To create a [new profile](https://jeanslack.github.io/Videomass2/Pages/Main_Toolbar/PresetsManager_Panel/Profiles_management.html), press the _New.._ button in the toolbar.
* To delete a profile, press the _Delete.._ button in the toolbar.
* To [edit a profile](https://jeanslack.github.io/Videomass2/Pages/Main_Toolbar/PresetsManager_Panel/Profiles_management.html). press the _Edit.._ button in the toolbar.

### Selecting Preset (tab)
In this tab there is a list of all presets that can be selected from a drop-down menu.
**NOTE:** "_User Profiles_" is a particular menu item where the profiles that you saved from the Video Conversions and Audio Conversions interfaces are stored.

### Command Line FFmpeg (tab)
By selecting the 'Command Line FFmpeg' tab you will see the command of each selected profile. To change a command on the 
fly, you must first enable the write function on the [Setup dialog](https://github.com/jeanslack/Videomass2/blob/gh-pages/Pages/Startup/Setup.md). Remember that a profile changed on the fly will only be applied in the conversion process but will 
not be stored on the profile. To save a new profile, you will need to use the 'New..' function in the toolbar.

[Back](../../../videomass2_use.md)
