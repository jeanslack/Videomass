[Home](index.md)

# Let's build the package
---------------------------

If you have already installed the dependencies listed on this page [dependencies](dependencies.md),
you can now proceed with the following package construction methods.

- To create a redistributable package, we will use the **setup.py** script in the source 
folder, with which we will use the _py2exe_ tool to make a standalone package for Windows, 
_py2app_ tool to make a standalone package for MacOS.


- To create a source and build distribution installable on any systems, we will use  _sdist_ 
and _bdist_wheel_ in conjunction with the setup.py.

In any case, make sure you have installed all the base necessary requirements:

- **distutils**, is still the standard tool for packaging in python. It is included in the standard library that can be easily
  imported.

- **setuptools**, which is not included in the standard library, must be separately installed if not present in your system. Update: setuptools is included from python 2.7

- Then, Download the Videomass2 TAR or ZIP sources at the top of this page and extract the archive.

-----------------
## Windows 
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
## MacOS
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

This will create a self contained applet in the ./dist/ directory   


**More details and resources:**   

-Usage for get help:   

`python setup.py py2app --help`   

-Usage for development and debug:   

`python setup.py py2app -A`   

and then debug with terminal:   

`./dist/Videomass2.app/Contents/MacOS/videomass2`   

-Usage for building a redistributable version standalone:   

`python setup.py py2app`   

-Resources:   

<https://www.metachris.com/2015/11/create-standalone-mac-os-x-applications-with-python-and-py2app/>   

<https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-dependencies>   

Set a virtualenv environment need for build the .app:   

<https://wiki.wxpython.org/wxPythonVirtualenvOnMac>   

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

-----------------
## Gnu/Linux Debian

If you want make a .deb binary package installable in your debian system, 
you need install those following tools first:

```
~# apt-get update && apt-get install python-all python-stdeb fakeroot
```

This will installs all the need dependencies, including python-setuptools. 
Then, go into Videomass2 unzipped folder with your user (not root)   

- To generate both source and binary packages type:

```
~$ python setup.py --command-packages=stdeb.command bdist_deb
```

The command above should create a _python-videomass2_version_all.deb_ in 
the new _deb_dist_ directory, installable with   

```
~# dpkg -i python-videomass2_version_all.deb
```

- To generate a source packages only:

```
~$ python setup.py --command-packages=stdeb.command sdist_dsc
```

#### Resources:

<https://pypi.python.org/pypi/stdeb>   
<http://shallowsky.com/blog/programming/python-debian-packages-w-stdeb.html>   


## Build distribution for Windows, MacOsX, Linux, Unix

First install the following tools:   

- **pip** or **python-pip**, The PyPA recommended tool for installing Python packages   

- **wheel** or **python-wheel**, The wheel project provides a "bdist_wheel" 
command for setuptools. The files wheel can be installed with "pip".   

```
python setup.py sdist bdist_wheel
```

In the dist folder you find a source distribution (videomass2-x.x.x.tar.gz) and
a build distribution (videomass2-x.x.x-py2-none-any.whl). You can install the 
build distribution with **pip** command:   

```
cd dist
pip install videomass2-x.x.x-py2-none-any.whl
```

[Home](index.md)
