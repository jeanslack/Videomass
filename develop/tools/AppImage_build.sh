#!/bin/bash
#
# Description: Build a `Videomass-*-x86_64.AppImage` starting
#              from a `PYTHON_APPIMAGE` and `WX_PYTHON_WHEEL` .
#              Note that this appimage work on GTK3 toolkit only.
#
# if you plan to install extra packages, extract the AppImage, e.g. as:
#
#   ./Videomass*.AppImage --appimage-extract
#   export PATH="$(pwd)/squashfs-root/usr/bin:$PATH"
#
# Ideally run this inside the manylinux Docker container
# so that dependencies get bundled from that very container
#
# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyleft - 2024 Gianluca Pernigotto <jeanlucperni@gmail.com>
# Create: Oct.02.2020
# Update: Nov.25.2022
###################################################################

set -x  # Print commands and their arguments as they are executed.
set -e  # Exit immediately if a command exits with a non-zero status.

# building in temporary directory to keep system clean
# use RAM disk if possible (as in: not building on CI system like Travis, and RAM disk is available)
if [ "$CI" == "" ] && [ -d /dev/shm ]; then
    if mount | grep '/dev/shm' | grep -q 'noexec'; then
        TEMP_BASE=/tmp
    else
        TEMP_BASE=/dev/shm
    fi
else
    TEMP_BASE=/tmp
fi

# Set the latest release of python-appimage,
# make sure the version matches correctly, if not fix it.
PYTHON_APPIMAGE=python3.9.17-cp39-cp39-manylinux1_x86_64.AppImage
PYTHON_APPIMAGE_URL=https://github.com/niess/python-appimage/releases/download/python3.9/${PYTHON_APPIMAGE}

# Set the wxPython release, make sure the version matches correctly,
# if not fix it.
WX_PYTHON_WHEEL=wxPython-4.1.1-cp39-cp39-linux_x86_64.whl
WX_PYTHON_URL=https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-18.04

# Set a temporary dir
BUILD_DIR=$(mktemp -d -p "$TEMP_BASE" videomass-AppImage-build-XXXXXX)
APP_DIR="$BUILD_DIR/AppDir"

# make sure to clean up build dir, even if errors occur
cleanup () {
    if [ -d "$BUILD_DIR" ]; then
        rm -rf "$BUILD_DIR"
    fi
    }
trap cleanup EXIT

# Store repo root as variable
REPO_ROOT=$(dirname $(dirname $(dirname $(realpath $0))))  # repo root (src)
OLD_CWD=$(readlink -f .)  # path from which you start the script

# switch to build dir
pushd "$BUILD_DIR"

# Fetch a python relocatable installation
wget -c ${PYTHON_APPIMAGE_URL}
chmod +x ${PYTHON_APPIMAGE}
./${PYTHON_APPIMAGE} --appimage-extract

mv squashfs-root AppDir

# Download required shared library
if [ ! -d usr ] || [ ! -d lib ]; then
    wget -c http://security.ubuntu.com/ubuntu/pool/main/libp/libpng/libpng12-0_1.2.54-1ubuntu1.1_amd64.deb \
        http://security.ubuntu.com/ubuntu/pool/main/libj/libjpeg-turbo/libjpeg-turbo8_1.4.2-0ubuntu3.4_amd64.deb \
            http://nl.archive.ubuntu.com/ubuntu/pool/universe/s/sndio/libsndio6.1_1.1.0-2_amd64.deb \
                http://security.ubuntu.com/ubuntu/pool/universe/libs/libsdl2/libsdl2-2.0-0_2.0.8+dfsg1-1ubuntu1.18.04.4_amd64.deb

    # extract data from .deb files
    ar -x libpng12-0_1.2.54-1ubuntu1.1_amd64.deb data.tar.xz && tar -xf data.tar.xz
    ar -x libjpeg-turbo8_1.4.2-0ubuntu3.4_amd64.deb data.tar.xz && tar -xf data.tar.xz
    ar -x libsndio6.1_1.1.0-2_amd64.deb data.tar.xz && tar -xf data.tar.xz
    ar -x libsdl2-2.0-0_2.0.8+dfsg1-1ubuntu1.18.04.4_amd64.deb data.tar.xz && tar -xf data.tar.xz
fi

# copy shared libraries
cp -r lib/ $APP_DIR/
cp -r usr/ $APP_DIR/

# move some libraries to link when needed by starting appimage
mkdir $APP_DIR/x86_64-linux-gnu
mv $APP_DIR/usr/lib/x86_64-linux-gnu/libSDL2-2.0.so.0.8.0 \
    $APP_DIR/usr/lib/x86_64-linux-gnu/libSDL2-2.0.so.0 \
        $APP_DIR/usr/lib/x86_64-linux-gnu/libsndio.so.6.1 \
            $APP_DIR/x86_64-linux-gnu

# Update pip first
$APP_DIR/AppRun -m pip install -U pip

# installing wxPython binary wheel (GTK3 porting)
if [ -f "$OLD_CWD/$WX_PYTHON_WHEEL" ]; then
    $APP_DIR/AppRun -m pip install -U "$OLD_CWD/$WX_PYTHON_WHEEL"
else
    $APP_DIR/AppRun -m pip install -U -f ${WX_PYTHON_URL} wxPython
fi

# install videomass and its dependencies
if [ -f $REPO_ROOT/dist/videomass-*.whl ]; then
    $APP_DIR/AppRun -m pip install $REPO_ROOT/dist/videomass-*.whl

else
    $APP_DIR/AppRun -m pip install videomass
fi

# remove old appdata on metainfo dir
rm $APP_DIR/usr/share/metainfo/python*.appdata.xml

# copy new appdata file for Videomass
cp -f $REPO_ROOT/io.github.jeanslack.videomass.appdata.xml \
    $APP_DIR/usr/share/metainfo/io.github.jeanslack.videomass.appdata.xml

# copy new AppRun for Videomass
cp -f $REPO_ROOT/develop/tools/AppRun $APP_DIR/AppRun

# remove unused .png and .desktop files
rm $APP_DIR/python.png \
    $APP_DIR/python*.desktop \
     $APP_DIR/usr/share/applications/python*.desktop \
        $APP_DIR/usr/share/icons/hicolor/256x256/apps/python.png

# copy new .desktop file
cp -f $REPO_ROOT/videomass/art/io.github.jeanslack.videomass.desktop \
    $APP_DIR/usr/share/applications/io.github.jeanslack.videomass.desktop

# add pixmaps icon
cp -r $APP_DIR/opt/python*/share/pixmaps/ $APP_DIR/usr/share/

# download linuxdeploy for building now
wget -c https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage

chmod +x linuxdeploy-x86_64.AppImage

# set architecture
export ARCH=x86_64

# retrieve the Videomass version from the package metadata
export VERSION=$(cat \
    $APP_DIR/opt/python*/lib/python3.9/site-packages/videomass-*.dist-info/METADATA \
        | grep "^Version:.*" | cut -d " " -f 2)

# Now, build AppImage using linuxdeploy
./linuxdeploy-x86_64.AppImage --appdir $APP_DIR \
    --icon-file $APP_DIR/opt/python*/share/icons/hicolor/256x256/apps/videomass.png \
        --desktop-file $APP_DIR/opt/python*/share/applications/io.github.jeanslack.videomass.desktop \
            --output appimage

# move built AppImage back into original CWD
mv Videomass*.AppImage "$OLD_CWD/"
