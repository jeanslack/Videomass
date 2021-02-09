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
# Copyright: (c) 2020-2021 Gianluca Pernigotto <jeanlucperni@gmail.com>
# Create: Oct.10.2020
# Update: Feb.09.2021
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

PYTHON_APPIMAGE=python3.8.6-cp38-cp38-manylinux1_x86_64.AppImage
PYTHON_APPIMAGE_URL=https://github.com/niess/python-appimage/releases/download/python3.8/${PYTHON_APPIMAGE}
WX_PYTHON_WHEEL=wxPython-4.1.0-cp38-cp38-linux_x86_64.whl

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
if [ ! -d usr ]; then
    wget -c http://security.debian.org/debian-security/pool/updates/main/libj/libjpeg-turbo/libjpeg62-turbo_1.5.1-2+deb9u1_amd64.deb \
        http://ftp.de.debian.org/debian/pool/main/j/jbigkit/libjbig0_2.1-3.1+b2_amd64.deb \
            http://ftp.de.debian.org/debian/pool/main/s/sndio/libsndio6.1_1.1.0-3_amd64.deb \
                http://ftp.de.debian.org/debian/pool/main/libs/libsdl2/libsdl2-2.0-0_2.0.5+dfsg1-2_amd64.deb

    # extract data from .deb files
    ar -x libjpeg62-turbo_1.5.1-2+deb9u1_amd64.deb data.tar.xz && tar -xf data.tar.xz
    ar -x libjbig0_2.1-3.1+b2_amd64.deb data.tar.xz && tar -xf data.tar.xz
    ar -x libsndio6.1_1.1.0-3_amd64.deb data.tar.xz && tar -xf data.tar.xz
    ar -x libsdl2-2.0-0_2.0.5+dfsg1-2_amd64.deb data.tar.xz && tar -xf data.tar.xz
fi

# copy shared libraries
cp -r usr/ $APP_DIR/

# move some libraries to link when needed by starting appimage
mkdir $APP_DIR/x86_64-linux-gnu
mv $APP_DIR/usr/lib/x86_64-linux-gnu/libSDL2-2.0.so.0.4.1 \
    $APP_DIR/usr/lib/x86_64-linux-gnu/libSDL2-2.0.so.0 \
        $APP_DIR/usr/lib/x86_64-linux-gnu/libsndio.so.6.1 \
            $APP_DIR/x86_64-linux-gnu

# Update pip first
$APP_DIR/AppRun -m pip install -U pip

# installing wxPython4.1 binary wheel (GTK3 porting)
if [ -f "$OLD_CWD/$WX_PYTHON_WHEEL" ]; then
    $APP_DIR/AppRun -m pip install -U "$OLD_CWD/$WX_PYTHON_WHEEL"
else
    echo "ERROR: need '$WX_PYTHON_WHEEL' (GTK3 porting) builded on Debian 9 stretch x86_64"
    exit 1
fi

# install videomass and its dependencies
if [ -f $REPO_ROOT/dist/videomass-*.whl ]; then
    $APP_DIR/AppRun -m pip install $REPO_ROOT/dist/videomass-*.whl
else
    $APP_DIR/AppRun -m pip install videomass
fi

# metainfo setting
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
cp -f $REPO_ROOT/videomass3/art/io.github.jeanslack.videomass.desktop \
    $APP_DIR/usr/share/applications/io.github.jeanslack.videomass.desktop

# add pixmaps icon
cp -r $APP_DIR/opt/python*/share/pixmaps/ $APP_DIR/usr/share/

# download appimagetool and linuxdeploy
wget -c https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage \
    https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage

chmod +x appimagetool-x86_64.AppImage linuxdeploy-x86_64.AppImage

# for any updates, copy 'appimagetool*' and 'youtube_dl_update_appimage.sh' script
cp appimagetool-x86_64.AppImage \
    "$REPO_ROOT/develop/tools/youtube_dl_update_appimage.sh" \
        $APP_DIR/usr/bin

if [ ! -x $APP_DIR/usr/bin/youtube_dl_update_appimage.sh ]; then
chmod +x $APP_DIR/usr/bin/youtube_dl_update_appimage.sh
fi

# set architecture
export ARCH=x86_64

# retrieve the Videomass version from the package metadata
export VERSION=$(cat \
    $APP_DIR/opt/python*/lib/python3.8/site-packages/videomass-*.dist-info/METADATA \
        | grep "^Version:.*" | cut -d " " -f 2)

# Now, build AppImage using linuxdeploy
./linuxdeploy-x86_64.AppImage --appdir $APP_DIR \
    --icon-file $APP_DIR/opt/python*/share/icons/hicolor/256x256/apps/videomass.png \
        --desktop-file $APP_DIR/opt/python*/share/applications/io.github.jeanslack.videomass.desktop \
            --output appimage

# move built AppImage back into original CWD
mv Videomass*.AppImage "$OLD_CWD/"
