# **Videomass** provides a graphical interface for audio and video conversions through FFmpeg.   

* [View progect on PyPi](https://pypi.org/project/videomass/)
* [GitHub Page](https://github.com/jeanslack/Videomass)
* [Support Page and Documentation](http://jeanslack.github.io/Videomass)
* [Wiki page](https://github.com/jeanslack/Videomass/wiki)
* [Downloads Source Code](https://github.com/jeanslack/Videomass/releases)
* [Installers for Windows and MacOsX](https://sourceforge.net/projects/videomass2/)

### Notice:

Since version 1.6.1, Videomass is compatible only with Python3 and therefore 
with wxPython4 (phoenix). For some reasons, such as the end of Python2 
support by 1 January 2020, the technical difficulties in the practical 
management of the code of both Python versions and the time investments 
for porting, Videomass will cease development for compatibility with Python2 .

## Features

- Drag n' Drop with multiple files at once
- Batch mode conversions (except for exporting images)
- Presets manager interface with fully customizable and expandable profiles 
- Independent video and audio conversions interface 
- Displaying streams information 
- Playback the files imported and last exported file
- Real-time filters preview (only with video conversion interface)
- Save jpg images from movies
- Audio peak level analysis with normalization process (only gain for now) 
- Save audio streams from movies with language selection
- Setting duration segments for imported files, filters, export and tests
- Log management
- Multi language (English and Italian Languages support for now)
- Work on many platforms where Python3 and wxPython4 are supported, 
  including Linux, Unix, MacOs and Windows.
- Compatible with Python 3 only
- ...And more

## Essential Dependencies

**Required:**   
- Python3     
- wxPython4 (phoenix)   

**Optionals:**   
- ffmpeg >= 3.2   
- ffprobe (for multimedia streams analysis)  
- ffplay (media player for media preview)   

