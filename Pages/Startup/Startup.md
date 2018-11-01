[Back](../../videomass2_use.md)

## Windows and MacOs Users

Windows and MacO users will be assisted by a wizard to determine the existence and location of FFmpeg.   
![Image](../../images/MacOs_wizard.png) ![Image](../../images/windows_wizard.png)   
Usually FFmpeg is included in the Videomass2 installation package and it will not be a big matter if FFmpeg is not 
installed on your system. Otherwise, if you use Videomass2 sources, things will be slightly more complicated and you 
will have to install FFmpeg on your system and manually set the binaries path on Videomass2. Also you must also install 
Python2.7 and wxPython3.0 and you would probably follow this [how to](../../execute_sources.md)...

## Linux Users
Linux users will see the program start normally. As often repeated, Videomass2 will not work without the FFmpeg backend, 
so FFmpeg is a dependency that can not be omitted and therefore also Python2.7 and wxPython3.0. For now Videomass2 will 
not automatically satisfy these dependencies and you will have to provide for yourself.
So first install these dependencies by following this [page](../../installation.md).

## All

During the first start-up, the application provides a drag n drop interface in which it is possible to load several files 
at a time. Once you have dragged at least one file, the **Presets Manager**, **Video Conversions** and **Audio Conversions** buttons on the main toolbar are enabled. You can choose a specific export path or export to the same source path. 
The **clear** button will delete the entire contents of the loaded list. A contextual menu is available that can be activated 
with a double click or with the right mouse button to reproduce or view metadata of each selected media.

[Back](../../videomass2_use.md)
