
Compile with pyinstaller:

- If you want start the Videomass.spec (file specification by pyinstaller)
  type: pyinstaller [OPTIONS] Videomass.spec

- If you want start from installerpy.py type: python3 [OPTIONS] installer.py

- Remember to copy the /bin/videomass and paste to current folder before to
  run any pyinstaller command.

NOTE: when you use installerpy.py script will generate a Videomass.spec which
      you can handle by edit the statements of the class instance to leading
      any aspect on next bundled application, e.g `excludes=['youtube_dl']`
      in Analysis to excludes that python package from bundle.

      see https://pyinstaller.readthedocs.io/en/stable/spec-files.html

