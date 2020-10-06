#!/bin/bash
#
# Description: Build from scratch a `Videomass-*-x86_64.AppImage` starting
#              from a `python3.8.*-cp38-cp38-manylinux1_x86_64.AppImage`
#              via `appimagetool-x86_64.AppImage`
#              Note that this appimage work on GTK2 toolkit only.
#
# if you plan to install extra packages extract the AppImage, e.g. as:
#
#   ./Videomass*.AppImage --appimage-extract
#   export PATH="$(pwd)/squashfs-root/usr/bin:$PATH"
#
# Ideally run this inside the manylinux Docker container
# so that dependencies get bundled from that very container
#
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Update: Oct.03.2020

set -e  # stop if error

SELF="$(readlink -f -- $0)" # this file
HERE="${SELF%/*}"  # dirname
MACHINE_ARCH=$(arch)
PYTHON_APPIMAGE=python3.8.6-cp38-cp38-manylinux1_x86_64.AppImage
PYTHON_APPIMAGE_URL=https://github.com/niess/python-appimage/releases/download/python3.8/${PYTHON_APPIMAGE}
WX_PYTHON_WHEEL=wxPython-4.1.0-cp38-cp38-linux_x86_64.whl
WX_PYTHON_URL=https://extras.wxpython.org/wxPython4/extras/linux/gtk2/ubuntu-16.04/${WX_PYTHON_WHEEL}
BUILD_DIR=VIDEOMASS_APPIMAGE_GTK2
APP_DIR="AppDir"

# check for architecture
if [ "${MACHINE_ARCH}" != 'x86_64' ] ; then
    echo "ERROR: architecture not supported $MACHINE_ARCH, supports x86_64 only"
    exit 1
fi

# Make directory for building
if [ -d "$PWD/$BUILD_DIR" ]; then
    # switch to build dir
    pushd "$BUILD_DIR"
    if [ -d $APP_DIR ]; then
        echo "ERROR: another 'AppDir' dir exists!"
        exit 1
    fi
else
    mkdir -p -m 0775 "$PWD/$BUILD_DIR"
    # switch to build dir
    pushd "$BUILD_DIR"
fi

# Fetch a python relocatable installation
if [ ! -f ${PYTHON_APPIMAGE} ]; then
    wget -c ${PYTHON_APPIMAGE_URL}
fi

# Extract this AppImage
if [ ! -x ${PYTHON_APPIMAGE} ]; then
    chmod +x ${PYTHON_APPIMAGE}
fi
./${PYTHON_APPIMAGE} --appimage-extract

mv squashfs-root AppDir

# Download required shared library
if [ ! -d usr ] || [ ! -d lib ]; then
    wget -c http://security.ubuntu.com/ubuntu/pool/main/libp/libpng/libpng12-0_1.2.54-1ubuntu1.1_amd64.deb \
    http://security.ubuntu.com/ubuntu/pool/main/libj/libjpeg-turbo/libjpeg-turbo8_1.4.2-0ubuntu3.4_amd64.deb \
#     http://nl.archive.ubuntu.com/ubuntu/pool/universe/s/sndio/libsndio6.1_1.1.0-2_amd64.deb \
#     http://security.ubuntu.com/ubuntu/pool/universe/libs/libsdl2/libsdl2-2.0-0_2.0.4+dfsg1-2ubuntu2.16.04.2_amd64.deb

    # extract data from .deb files
    ar -x libpng12-0_1.2.54-1ubuntu1.1_amd64.deb data.tar.xz && tar -xf data.tar.xz
    ar -x libjpeg-turbo8_1.4.2-0ubuntu3.4_amd64.deb data.tar.xz && tar -xf data.tar.xz
#     ar -x libsndio6.1_1.1.0-2_amd64.deb data.tar.xz && tar -xf data.tar.xz
#     ar -x libsdl2-2.0-0_2.0.4+dfsg1-2ubuntu2.16.04.2_amd64.deb data.tar.xz && tar -xf data.tar.xz
fi

# copy shared libraries
cp -r lib/ $APP_DIR/
cp -r usr/ $APP_DIR/

# update pip
$APP_DIR/AppRun -m pip install -U pip

# installing wxPython4.1 binary wheel
if [ -f ${WX_PYTHON_WHEEL} ]; then
    $APP_DIR/AppRun -m pip install ${WX_PYTHON_WHEEL}
else
    $APP_DIR/AppRun -m pip install -U -f ${WX_PYTHON_URL} wxPython
fi

# Install videomass and its dependencies, PyPubSub, youtube_dl
if [ -f videomass-*.whl ]; then
    $APP_DIR/AppRun -m pip install videomass-*.whl
else
    $APP_DIR/AppRun -m pip install videomass
fi

# Change AppRun so that it launches videomass and export shared libraries dir
sed -i -e 's|/opt/python3.8/bin/python3.8|/usr/bin/videomass|g' $APP_DIR/AppRun
sed -i -e '/export TKPATH/a # required shared libraries to run Videomass' $APP_DIR/AppRun
sed -i -e '/# required shared libraries to run Videomass/a export LD_LIBRARY_PATH="${here}/usr/lib/x86_64-linux-gnu/":$LD_LIBRARY_PATH' $APP_DIR/AppRun
sed -i -e '/export LD_LIBRARY_PATH=/a export LD_LIBRARY_PATH="${here}/lib/x86_64-linux-gnu/":$LD_LIBRARY_PATH' $APP_DIR/AppRun

# set new metainfo
cat <<EOF > $APP_DIR/usr/share/metainfo/python*.appdata.xml
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
    <id>videomass</id>
    <metadata_license>MIT</metadata_license>
    <project_license>Python-2.0</project_license>
    <name>Videomass</name>
    <summary>A Python 3.8 runtime with videomass, youtube_dl, PyPubSub and wxPython GUI toolkit</summary>
    <description>
        <p>  A relocated Python 3.8 installation containing the videomass
             packages suite (videomass, youtube_dl, PyPubSub and wxPython)
             and running from an AppImage.
        </p>
    </description>
    <launchable type="desktop-id">videomass.desktop</launchable>
    <url type="homepage">http://jeanslack.github.io/Videomass</url>
    <provides>
        <binary>python3.8</binary>
    </provides>
</component>
EOF

# Edit the desktop file
mv $APP_DIR/usr/share/applications/python*.desktop \
    $APP_DIR/usr/share/applications/videomass.desktop

# set new .desktop
sed -i -e 's|^Name=.*|Name=Videomass|g' $APP_DIR/usr/share/applications/*.desktop
sed -i -e 's|^Exec=.*|Exec=videomass|g' $APP_DIR/usr/share/applications/*.desktop
sed -i -e 's|^Icon=.*|Icon=videomass|g' $APP_DIR/usr/share/applications/*.desktop
sed -i -e 's|^Comment=.*|Comment=Graphical user interface for FFmpeg and youtube-dl|g' \
    $APP_DIR/usr/share/applications/*.desktop
sed -i -e 's|^Terminal=.*|Terminal=false|g' $APP_DIR/usr/share/applications/*.desktop
sed -i -e 's|^Categories=.*|Categories=AudioVideo;|g' $APP_DIR/usr/share/applications/*.desktop

# del unused *.png and *.desktop
rm -Rf $APP_DIR/usr/share/icons/hicolor/256x256/apps/*.png
rm $APP_DIR/python.png $APP_DIR/*.desktop

# Add the new icon
cp $APP_DIR/opt/python*/share/icons/hicolor/256x256/apps/videomass.png \
    $APP_DIR/usr/share/icons/hicolor/256x256/apps/videomass.png
cp -r $APP_DIR/opt/python*/share/pixmaps/ $APP_DIR/usr/share/

# make simlink
ln -sr $APP_DIR/usr/share/icons/hicolor/256x256/apps/videomass.png \
    $APP_DIR/videomass.png
ln -sr $APP_DIR/usr/share/applications/videomass.desktop \
    $APP_DIR/videomass.desktop

# retrieve the Videomass version from the package metadata
export VERSION=$(cat \
    $APP_DIR/opt/python*/lib/python3.8/site-packages/videomass-*.dist-info/METADATA \
        | grep "^Version:.*" | cut -d " " -f 2)

# check appimagetool
if [ ! -f appimagetool-x86_64.AppImage ]; then
    wget -c https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
fi

if [ ! -x appimagetool-x86_64.AppImage ]; then
    chmod +x appimagetool-x86_64.AppImage
fi

# for any updates, copy 'appimagetool*' and 'youtube_dl_update_appimage.sh' script on bin/
cp appimagetool-x86_64.AppImage "$HERE/youtube_dl_update_appimage.sh" $APP_DIR/usr/bin

if [ ! -x $APP_DIR/usr/bin/youtube_dl_update_appimage.sh ]; then
    chmod +x $APP_DIR/usr/bin/youtube_dl_update_appimage.sh
fi

# Convert back into an AppImage with gpg signature
./appimagetool-x86_64.AppImage -s $APP_DIR/
