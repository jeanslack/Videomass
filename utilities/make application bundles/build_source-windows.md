## Installing required dependencies
-----------------

- Install Python>=3.7 .

- Use pip for install wxPython4 and PyPubSub:   

   `pip install wxPython`
   `pip install PyPubSub`
   
- Since I didn't succeed using py2exe with Python version 3.7.4 I tried pyinstaller and got good results. So go install pyinstaller.   

   `pip install pyinstaller`

- Download the [Videomass](https://github.com/jeanslack/Videomass) TAR or ZIP sources and extract the archive.

- To create a redistributable package compile with pyinstaller:

    - If you want start the Videomass.spec (file specification by pyinstaller) type:   
    `pyinstaller [OPTIONS] Videomass.spec`

- If you want start from installerpy.py script type: python3 [OPTIONS] installer.py

- Remember to copy the /bin/videomass and paste to current folder before to
  run any pyinstaller command.
  
  try: python makespec.main installerpy.py

NOTE: when you use installerpy.py script will generate a Videomass.spec which
      you can handle by edit the statements of the class instance to leading
      any aspect on next bundled application, e.g `excludes=['youtube_dl']`
      in Analysis to excludes that python package from bundle.

      see https://pyinstaller.readthedocs.io/en/stable/spec-files.html
