-----------------
# Make AppImage for deployment

**IMPORTANT:** do not use the `pyinstaller-appimage.py` which is **deprecated**   

Use the `make_videomass_appimage.sh` script to automate embedding
Videomass on AppImage bundle.

## About downloading extra file

The following extra files will be downloaded from the following links:   

- Python3.8
    - https://github.com/niess/python-appimage/releases/download/python3.8/python3.8.5-cp38-cp38-manylinux1_x86_64.AppImage
- wxPython
    - https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-16.04/wxPython-4.1.0-cp38-cp38-linux_x86_64.whl
- shared libraries
    - http://security.ubuntu.com/ubuntu/pool/main/libp/libpng/libpng12-0_1.2.54-1ubuntu1.1_amd64.deb   
    - http://security.ubuntu.com/ubuntu/pool/main/libj/libjpeg-turbo/libjpeg-turbo8_1.4.2-0ubuntu3.4_amd64.deb   
    - http://nl.archive.ubuntu.com/ubuntu/pool/universe/s/sndio/libsndio6.1_1.1.0-2_amd64.deb   
    - http://security.ubuntu.com/ubuntu/pool/universe/libs/libsdl2/libsdl2-2.0-0_2.0.4+dfsg1-2ubuntu2.16.04.2_amd64.deb   

    
    
