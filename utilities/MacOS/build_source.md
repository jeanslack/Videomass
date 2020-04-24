## Installing required dependencies   
-----------------
One of the tools to easily install everything that is missing on MacOS is [homebrew](https://brew.sh/) tool. However, homebrew uses the "Command Line Tools" installed on your machine. By default, OS X does not ship with this tool, and you need to manually install it. One way to install it is to install Xcode, and it will install these commands as well. But, Xcode is heavy (in filesize), and unless you are a developer, you won’t have any need for it. Well, you can do it by just installing the command line tools only:
```
xcode-select --install  
```
When this is finished, you can install homebrew!
```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
### Python3 installation
```
$ brew install python3
```

### FFmpeg Installation

There are different ways to get FFmpeg, we consider only two here.   
 
- By homebrew (the simply and secure way):   

Before installing FFmpeg you could take a look at this interesting explanation of its homebrew compilation options:   
<https://gist.github.com/clayton/6196167>   

Or search for the options you want to enable on homebrew:   
<https://formulae.brew.sh/formula/ffmpeg>    

Otherwise, get this command for enable all options:   
```
brew install ffmpeg --with-chromaprint --with-fdk-aac --with-fontconfig --with-freetype --with-frei0r --with-game-music-emu --with-libass --with-libbluray --with-libbs2b --with-libcaca --with-libgsm --with-libmodplug --with-librsvg --with-libsoxr --with-libssh --with-libvidstab --with-libvorbis --with-libvpx --with-opencore-amr --with-openh264 --with-openjpeg --with-openssl --with-opus --with-rtmpdump --with-rubberband --with-sdl2 --with-snappy --with-speex --with-tesseract --with-theora --with-tools --with-two-lame --with-wavpack --with-webp --with-x265 --with-xz --with-zeromq --with-zimg
```
- By download the precompiled static binary files:   

Go at this page <https://ffmpeg.zeranoe.com/builds/macos64/static/>, download your prefered file, then extract the archive.
Inside the 'bin' folder you find the ffmpeg, ffprobe and ffplay binaries already to use with the terminal app or by Videomass.
Now, you can copy and paste all the 'bin' folder to '/Videomass3/MAcOsxSetup/FFMPEG_BIN/', or you can set the path later on Videomass.   

Also, If you want to get separately the ffmpeg, ffprobe and ffplay installers statically compiled and ready to install, you can download them at the following site:

<http://www.evermeet.cx/ffmpeg/>   
<http://www.evermeet.cx/ffprobe/>   
<http://www.evermeet.cx/ffplay/>

Note, however, that they may have limitations for reasons related to distribution (such as lack of AAC support)

## Build a Redistributable Package    
-----------------
To build a Videomass.app I suggest you create a virtual environment, also to avoid some errors that I found when compiling the app without a virtual environment. Exhaustive guides to doing this are as follows:   
<https://docs.python-guide.org/dev/virtualenvs/>     
<https://wiki.wxpython.org/wxPythonVirtualenvOnMac>      
<https://www.metachris.com/2015/11/create-standalone-mac-os-x-applications-with-python-and-py2app/>   

Note that inside Videomass sources already exists a setup.py with certain parameters for your MacOS, then make a virtual env inside Videomass sources, activate it and install **setuptools** and **py2app** with pip tool, then run setup.py   
```
~$ python3 setup.py py2app --packages=wx
``` 
This will create a self contained applet in the ./dist/ directory   

**More details and resources:** (outdated)   

<https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-dependencies> 

-Usage for get help:   

`python3 setup.py py2app --help`   

-Usage for development and debug:   

`python3 setup.py py2app -A`   

and then debug with terminal:   

`./dist/Videomass.app/Contents/MacOS/videomass`   

-Usage for building a redistributable version standalone:   

`python setup.py py2app`          

On Mac OSX, I installed wxpPthon with Homebrew using:   

`brew install wxpython`   
    
...and I change into virtualenv site-packages directory:   

`cd /venv/lib/python2.7/site-packages`   

then link the wx.pth   
    
```
ln -s /usr/local/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/wx.pth wx.pth
```
```     
ln -s /usr/local/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/wx-3.0-osx_cocoa wx-3.0-osx_cocoa
```
