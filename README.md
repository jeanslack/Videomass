# **Videomass** is a cross-platform graphical interface for FFmpeg and youtube-dl.
Videomass is not a converter; it provides a graphical interface for writing presets and profiles to be used with [FFmpeg](https://www.ffmpeg.org/) without limits on formats and codecs; it also provides a basic graphical interface for [youtube_dl](https://pypi.org/project/youtube_dl/) video downloader. From the beginning, the main goal was to give it a high flexibility and expandability in the management and control of the presets and profiles in order to facilitate their use with the potential of FFmpeg.

## General Features
- Multi-Platform, work on Linux, MacOs, Windows, FreeBsd.
- Batch processing.
- Advanced log management.
- Multi language (English and Italian Languages support for now).

## Features with FFmpeg
- Drag and drop to add multiple files simultaneously.
- Fully customizable presets and profiles.
- Possibility to create your new presets and profiles from scratch.
- Has useful presets to start with.
- Supports all formats and codecs available with FFmpeg.
- Displaying information from streams analyzer.
- Real-time video filters preview.
- Three audio normalization modes: Peak, RMS and EBU R128.
- Audio index from videos selectable to apply normalization.
- Setting duration portions for imported files, filters, export and tests.

## Features with youtube-dl
- Add multiple URLs simultaneously.
- Download multiple URLs from YouTube and more sites.
- Four download modes:
    - Default (choosing between 'best' or 'worst' qualities).
    - Download audio and video splitted.
    - Download Audio only (you can choose various formats).
    - Download videos and audio by 'format code' with audio merging.
- View video information without downloading it (using youtube_dl library only).
- Ability to playback individual URLs with different qualities via mpv player.
- Ability to download all playlist.
- Embed thumbnail in audio file (via atomicparsley).
- Add metadata to file.
- Write subtitles to video.


## Requirements
- [Python >=3.7](https://www.python.org/)
- [wxPython4](https://wxpython.org/) GUI framework.
- [PyPubSub](https://pypi.org/project/PyPubSub/) Python Publish-Subscribe Package.
- [pip](https://pypi.org/project/pip/) On Windows and MacOS it is included with Python3.7
- [ffmpeg](https://ffmpeg.org/) >= 4.1.4
- [ffprobe](https://ffmpeg.org/ffprobe.html) for multimedia streams analysis - should be included with FFmpeg.
- [ffplay](http://ffmpeg.org/ffplay.html) for files playback - should be included with FFmpeg.
- [youtube-dl](https://pypi.org/project/youtube_dl/) to download videos from the web

### Optionals
- [mpv](https://mpv.io/) for previewing URLs in different formats and qualities.
- [atomicparsley](http://atomicparsley.sourceforge.net/) if you want to embed thumbnail in audio file

## How to start Videomass
Videomass can be run without installing it, just unzip the source archive and executing the "launcher" script inside the directory:   

`python3 launcher`   

Videomass can also be run in interactive mode with the Python interpreter, always within the same unpacked directory:   

`>>> from videomass3 import Videomass3`   
`>>> Videomass3.main()`   

Keep in mind that on Linux a launcher should be even created in the application launcher of your desktop environment when installing Videomass with pip.

On other systems such as Mac-Os and MS-Windows you will still have to open a console to run Videomass and just write `videomass` command. But if the command still doesn't work, you can start Videomass in interactive mode with the Python interpreter, as seen above.

## Resources
* [Videomass on PyPi](https://pypi.org/project/videomass/)
* [GitHub Page](https://github.com/jeanslack/Videomass)
* [Support Page and Documentation](http://jeanslack.github.io/Videomass)
* [Wiki page](https://github.com/jeanslack/Videomass/wiki)
* [Downloads Source Code](https://github.com/jeanslack/Videomass/releases)
* [Installers for Windows and MacOsX](https://sourceforge.net/projects/videomass2/)


