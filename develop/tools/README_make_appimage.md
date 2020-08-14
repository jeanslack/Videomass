-----------------
# Make AppImage for deployment

**IMPORTANT:** do not use the `pyinstaller-appimage.py` which is **deprecated**   

Use the `make_videomass_appimage.sh` script to automate embedding
Videomass on AppImage bundle.

## About included shared libraries

These shared libraries are needed to run wxPython on some other Linux 
distributions starting with Ubuntu 16.04 xenial x86_64. They come from the 
Ubuntu 16.04 xenial archive on the following web pages:   

    https://packages.ubuntu.com/xenial/libs/libjpeg-turbo8   
    https://packages.ubuntu.com/xenial/libpng12-0   
    https://packages.ubuntu.com/xenial/libs/libsdl2-2.0-0   
    https://packages.ubuntu.com/xenial/libs/libsndio6.1   
