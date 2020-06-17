# Make Videomass standalone exe
-----------------

### Installing required dependencies
- Install Python>=3.7   

- Then use pip for install wxPython4 and PyPubSub:   

   `python -m pip install wxPython PyPubSub`   

- Since I didn't succeed using py2exe with Python version 3.7.4 I tried 
pyinstaller and got good results. So go install pyinstaller.

   `python -m pip install pyinstaller`

- Download the [Videomass](https://github.com/jeanslack/Videomass) TAR or ZIP 
sources and extract the archive.   

### Before to run any command
- Copy the bin/videomass file and paste it into base directory of videomass.

- Copy utilities/make application bundles/installerpy.py file and paste it into 
base directory of videomass. When you use installerpy.py script will also 
generate a new videomass.spec file (or it overwrite the existing one) which you 
can handle by edit the statements of the class instance to leading any aspect 
on next bundled application, e.g `excludes=['youtube_dl']` in Analysis in order 
to excludes that python package from bundle.   

- see https://pyinstaller.readthedocs.io/en/stable/spec-files.html.   

### Create a redistributable package with pyinstaller:

- You can start whit installerpy.py script like this:
    `python3 [OPTIONS] installerpy.py`   

- If you want to start with videomass.spec (when created), then type:   
    `pyinstaller [OPTIONS] videomass.spec`   

> <ins>**Note:**</ins>
>
> Do not enter the "[OPTIONS]" field on pyinstaller and python3 commands if you 
want start with no options. This is just an example to show the optional flag too.   
For debug, even enable console=True into videomass.spec
