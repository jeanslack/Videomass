## Installing required dependencies
-----------------

- Download the latest release of the Python3 for your architecture from [python.org](https://www.python.org/downloads/) and install it. For your convenience, I recommend that you check all the options offered by the installer.

- Download the static version of FFmpeg binaries for your system architecture from <https://ffmpeg.zeranoe.com/builds/>, then extract the archive. Inside the *bin* folder
you will find the FFmpeg's executables: ffmpeg.exe, ffprobe.exe and ffplay.exe
(the extensions depends to your system settings or preferences).

You may be interested the following explanation:
<https://video.stackexchange.com/questions/20495/how-do-i-set-up-and-use-ffmpeg-in-windows>

## Build a Redistributable Package
-----------------
- Download the [Videomass](https://github.com/jeanslack/Videomass) TAR or ZIP sources and extract the archive.

- Install wxPython4, PyPubSub, pyinstaller with pip tool. Since I didn't succeed using py2exe with Python3.7.4 I tried pyinstaller and got good results.

- To create a redistributable package use pyinstaller
