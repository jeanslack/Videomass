# Installing required dependencies on Mac-Os 
-----------------

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
 
-1 By homebrew (the simply and secure way):   
> Before installing FFmpeg you could take a look at this interesting explanation 
of its homebrew compilation options: <https://gist.github.com/clayton/6196167>   

Or search for the options you want to enable on homebrew:   
<https://formulae.brew.sh/formula/ffmpeg>    

Otherwise, get this command for enable all options:   
```
brew install ffmpeg --with-chromaprint --with-fdk-aac --with-fontconfig --with-freetype --with-frei0r --with-game-music-emu --with-libass --with-libbluray --with-libbs2b --with-libcaca --with-libgsm --with-libmodplug --with-librsvg --with-libsoxr --with-libssh --with-libvidstab --with-libvorbis --with-libvpx --with-opencore-amr --with-openh264 --with-openjpeg --with-openssl --with-opus --with-rtmpdump --with-rubberband --with-sdl2 --with-snappy --with-speex --with-tesseract --with-theora --with-tools --with-two-lame --with-wavpack --with-webp --with-x265 --with-xz --with-zeromq --with-zimg
```
-2 By download the precompiled static binary files:   

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

### Build a Redistributable Package    
To build a Videomass.app I suggest you create a virtual environment, Exhaustive 
guides to doing this are as follows:   
<https://docs.python-guide.org/dev/virtualenvs/>   
<https://wiki.wxpython.org/wxPythonVirtualenvOnMac>   
<https://www.metachris.com/2015/11/create-standalone-mac-os-x-applications-with-python-and-py2app/>   

- Make sure you have pip, then install:   

   `python -m pip install wxPython PyPubSub`   

   `python -m pip install pyinstaller`

- Download the [Videomass](https://github.com/jeanslack/Videomass) TAR or ZIP 
sources and extract the archive.   

# Installing required dependencies on MS Windows 10
-----------------

### Installing required dependencies
- Install Python>=3.7   

- Make sure you have pip, then install:   

   `python -m pip install wxPython PyPubSub`   

   `python -m pip install pyinstaller`

- Download the [Videomass](https://github.com/jeanslack/Videomass) TAR or ZIP 
sources and extract the archive.   


# Building the bundle with pyinstaller
-----------------

### Before to run any command

- Copy `pyinstaller_setup.py` file on `dev/make application bundles` and paste it 
into base/root directory of videomass source. When you use `pyinstaller_setup.py` 
script will also generate a new videomass.spec file (or it overwrite the existing 
one) which you can handle by edit the statements of the class instance to leading 
any aspect on next bundled application.   
> see https://pyinstaller.readthedocs.io/en/stable/spec-files.html.   

### Create a redistributable package with pyinstaller:

- You can start whit installerpy.py script like this:
    `python3 pyinstaller_setup.py`   

- If you want to start with videomass.spec (when created), then type:   
    `pyinstaller [OPTIONS] videomass.spec`   

> <ins>**Note:**</ins>
>
> Do not enter the "[OPTIONS]" field on pyinstaller commands if you want start 
with no options. This is just an example to show the optional flag too.   
For debug, even enable `console=True` into videomass.spec
