-----------------
# Make bundle with pyinstaller

Before proceeding, install the dependencies required for your operating system:   
- [Gnu/Linux](#gnu-linux)
- [MacOs](#mac-os)
- [Windows](#ms-windows)

Packaging    
- [Make a Videomass bundle using pyinstaller](#building-the-bundle-with-pyinstaller)

-----------------
# Gnu-Linux

- Make sure you have at least Python version 3.6.9 or higher

- Make sure you have `pip`, if not install it with your package manager.

- Use `pip` to install PyPubSub
   - `python3 -m pip install --user PyPubSub`
   
   - `python3 -m pip install --user requests`

- Install wxPython (see [Installing-and-Dependencies](https://github.com/jeanslack/Videomass/wiki/Installing-and-Dependencies) )
for more details.

- Download the [Videomass](https://github.com/jeanslack/Videomass) using 
`git clone` command or download the ZIP archive by clicking on Code button 
of the [github]((https://github.com/jeanslack/Videomass)) page and choose 
`Download ZIP`, then extract the archive. 

-----------------
# Mac-Os

One of the tools to easily install everything that is missing on MacOS is
[homebrew](https://brew.sh/) tool. However, homebrew uses the "Command Line Tools"
installed on your machine. By default, OS X does not ship with this tool, and you
need to manually install it. One way to install it is to install Xcode, and it
will install these commands as well. But, Xcode is heavy (in filesize), and
unless you are a developer, you won’t have any need for it. Well, you can do it
by just installing the command line tools only:
```
xcode-select --install
```
Install homebrew!
```
$ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
### Python3 installation
```
$ brew install python3
```

### FFmpeg Installation

There are different ways to get FFmpeg, we consider only two here.

- By homebrew (the simply and secure way):
> Before installing FFmpeg you could take a look at this interesting explanation
of its homebrew compilation options: <https://gist.github.com/clayton/6196167>

search for the options you want to enable on homebrew:
<https://formulae.brew.sh/formula/ffmpeg>

Otherwise, get this command for enable all options:
```
brew install ffmpeg --with-chromaprint --with-fdk-aac --with-fontconfig --with-freetype --with-frei0r --with-game-music-emu --with-libass --with-libbluray --with-libbs2b --with-libcaca --with-libgsm --with-libmodplug --with-librsvg --with-libsoxr --with-libssh --with-libvidstab --with-libvorbis --with-libvpx --with-opencore-amr --with-openh264 --with-openjpeg --with-openssl --with-opus --with-rtmpdump --with-rubberband --with-sdl2 --with-snappy --with-speex --with-tesseract --with-theora --with-tools --with-two-lame --with-wavpack --with-webp --with-x265 --with-xz --with-zeromq --with-zimg
```
- By download the precompiled static binary files:

Go at this page <https://ffmpeg.zeranoe.com/builds/macos64/static/>, download
your prefered file, then extract the archive. Inside the 'bin' folder you find
the ffmpeg, ffprobe and ffplay binaries already to use with the terminal app or
by Videomass. Now, you can copy and paste all the `bin` folder to
`/Videomass3/MAcOsxSetup/FFMPEG_BIN/`, or you can set the path later on Videomass.

Also, If you want to get separately the ffmpeg, ffprobe and ffplay installers
statically compiled and ready to install, you can download them at the following site:

<http://www.evermeet.cx/ffmpeg/>
<http://www.evermeet.cx/ffprobe/>
<http://www.evermeet.cx/ffplay/>

Note, however, that they may have limitations for reasons related to distribution
(such as lack of AAC support)

### Create a virtual environment
To build a Videomass.app I suggest you create a virtual environment, Exhaustive
guides to doing this are as follows:   
- <https://docs.python-guide.org/dev/virtualenvs/>
- <https://wiki.wxpython.org/wxPythonVirtualenvOnMac>
- <https://www.metachris.com/2015/11/create-standalone-mac-os-x-applications-with-python-and-py2app/>

- Make sure you have pip, then install:
   - `python -m pip install --user wxPython`
   
   - `python -m pip install --user PyPubSub`
   
   - `python -m pip install --user requests`

- Download the [Videomass](https://github.com/jeanslack/Videomass) TAR or ZIP
sources and extract the archive.

-----------------
# MS-Windows

- Install Python>=3.7

- Make sure you have pip, then install:
   - `python -m pip install wxPython`

   - `python -m pip install PyPubSub`
   
   - `python -m pip install requests`

- Download the [Videomass](https://github.com/jeanslack/Videomass) TAR or ZIP
sources and extract the archive.

-----------------
# Building the bundle with pyinstaller 

- Make sure you have installed pyinstaller    
`$ python3 -m pip install --user pyinstaller`   

- Open root directory of the Videomass sources that you just extracted 
from the archive  e.g. `$ cd Videomass`

- Run `$ python3 develop/tools/pyinstaller_setup.py -h` script and choose the 
building option you want:   

    > <ins>**Note:**</ins>
    >
    > For debug on Windows, even enable `console=True` into videomass.spec, not for
    > production and distribution.
