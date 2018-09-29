[Home](index.md)
## Build a redistributable package   
-----------------

### Installing required dependencies on your OS   

-----------------
#### Windows
1. Download the latest release of the Python2.7 for your architecture from [python.org](https://www.python.org/downloads/) and
   install it.
   For your convenience, I strongly recommend that you install for all users and check all the options offered by the
   installer.     
  
2. Download the latest release of wxPython3.0 toolkit for python 2.7 compatible with your system architecture from [souceforge.net](https://sourceforge.net/projects/wxpython/files/wxPython/3.0.2.0/) and install it for all users and check all the options offered by the installer.   

3. Download the Videomass2 TAR or ZIP sources at the top of this page and extract the archive.   

4. Download the static version of FFmpeg binaries for your system architecture from <https://ffmpeg.zeranoe.com/builds/>, then extract the archive. Inside the *bin* folder you will find the FFmpeg's executables: ffmpeg.exe, ffprobe.exe and ffplay.exe (the extensions depends to your system settings or preferences). Now, you can copy and paste all the 'bin' folder to '\Videomass2\Win32Setup\FFMPEG_BIN', or you can set the path later on Videomass2.   

-----------------
#### MacOs
On MaOS, there is no need to install python since it should already be installed by default. For the rest, the most convenient way to get all dependencies is to use the [homebrew](https://brew.sh/) tool. However, homebrew uses the "Command Line Tools" installed on your machine. By default, OS X does not ship with this tool, and you need to manually install it. One way to install it is to install Xcode, and it will install these commands as well. But, Xcode is heavy (in filesize), and unless you are a developer, you won’t have any need for it. Well, you can do it by just installing the command line tools only:
```
xcode-select --install  
```
When this is finished, you can install homebrew!
```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
After installing 'homebrew' you can immediately proceed to install wxPython and FFmpeg.
```
$ brew install wxpython
```
There are different ways to get FFmpeg, we consider only two here.   

1. By homebrew (the simply and secure way)   

   Before installing FFmpeg you could take a look at this interesting explanation of its homebrew compilation options:   
   <https://gist.github.com/clayton/6196167>   

   Or search for the options you want to enable on homebrew:   
   <https://formulae.brew.sh/formula/ffmpeg>    

   Otherwise, get this command for enable all options:   
   ```
   brew install ffmpeg --with-chromaprint --with-fdk-aac --with-fontconfig --with-freetype --with-frei0r --with-game-music-emu --with-libass --with-libbluray --with-libbs2b --with-libcaca --with-libgsm --with-libmodplug --with-librsvg --with-libsoxr --with-libssh --with-libvidstab --with-libvorbis --with-libvpx --with-opencore-amr --with-openh264 --with-openjpeg --with-openssl --with-opus --with-rtmpdump --with-rubberband --with-sdl2 --with-snappy --with-speex --with-tesseract --with-theora --with-tools --with-two-lame --with-wavpack --with-webp --with-x265 --with-xz --with-zeromq --with-zimg
   ```
2. By download the precompiled static binary files:   

   Go at this page <https://ffmpeg.zeranoe.com/builds/macos64/static/>, download your prefered file, then extract the archive.
   Inside the 'bin' folder you find the ffmpeg, ffprobe and ffplay binaries already to use with the terminal app or by Videomass2.
   Now, you can copy and paste all the 'bin' folder to '/Videomass2/MAcOsxSetup/FFMPEG_BIN/', or you can set the path later on Videomass2.   
   
3. Download the Videomass2 TAR or ZIP sources at the top of this page and extract the archive.
   
-----------------
#### Gnu/Linux
As MacOS,  there is no need to install python since it should already be installed by default. 

1. Proceede with installing wxPython and FFmpeg if not already installed:

   ```
   ~$ sudo apt-get install python-wxgtk3.0 ffmpeg
   ```
2. Download the Videomass2 TAR or ZIP sources at the top of this page and extract the archive.

---------------------------
### Let's build the package
---------------------------

To create a redistributable package, we will use the setup.py script in the source folder, with which we will use the _py2exe_ tool with Windows and the _py2app_ tool with MacOS, plus other common packaging tools also useful for Gnu/Linux: _distutils_ and _setuptools_.

- **distutils** is still the standard tool for packaging in python. It is included in the standard library that can be easily
  imported.

- **setuptools** which is not included in the standard library, must be separately installed if not present in your system.  Update: setuptools is included from python 2.7   

-----------------
#### Windows
If you have successfully completed the points described above, now download and Install the py2exe utility for python 2.7 from:

<https://sourceforge.net/projects/py2exe/files/py2exe/0.6.9/>

if need update it and follow this how-to:

<https://www.blog.pythonlibrary.org/2010/07/31/a-py2exe-tutorial-build-a-binary-series/>

Then open a dos window and position you in the Videomass2 folder you just unzipped and type:

```
python setup.py py2exe
```
A folder named 'dist' will be created where there will be the magic executable of Videomass2.exe   

-----------------
#### MacOS
To build a Videomass.app I suggest you create a virtual environment, also to avoid some errors that I found when compiling the app without a virtual environment. An exhaustive guide to doing this is as follows:   
<https://docs.python-guide.org/dev/virtualenvs/>  

and this page:   
<https://wiki.wxpython.org/wxPythonVirtualenvOnMac>   

You might be interested read the follow web page also:   
<https://www.metachris.com/2015/11/create-standalone-mac-os-x-applications-with-python-and-py2app/>   

Note that inside Videomass2 sources already exists a setup.py with certain parameters for your MacOS, then make a virtual env inside Videomass2 sources, activate it and run setup.py:   
```
~$ python setup.py py2app
``` 
The Videomass2.app will be create at _dist_ folder

-----------------
#### Gnu/Linux
If you want make a .deb binary package installable in your debian system and compatible with others debian-based systems, you need install those following tools first:   
```
~# apt-get update && apt-get install python-all python-stdeb fakeroot
```
This installs all the need dependencies, including python-setuptools.

Then, go into Videomass2 unzipped folder with your user (not root) and type:
```
~$ python setup.py --command-packages=stdeb.command bdist_deb
```
This should create a _python-videomass2_version_all.deb_ in the new _deb_dist_ directory, installable with 
```
~# dpkg -i python-videomass2_version_all.deb
```

[Home](index.md)
